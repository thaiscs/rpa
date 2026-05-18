import subprocess
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from worker import process_job, run_rpa


class TestRunRpa:
    def _mock_tmp_files(self, mock_tmp, cert_name="/tmp/cert_abc", key_name="/tmp/key_abc"):
        cert_file = MagicMock()
        cert_file.name = cert_name
        key_file = MagicMock()
        key_file.name = key_name
        mock_tmp.side_effect = [cert_file, key_file]
        return cert_file, key_file

    def test_writes_cert_and_key_to_temp_files(self):
        with patch("worker.tempfile.NamedTemporaryFile") as mock_tmp, \
             patch("worker.subprocess.run"), \
             patch("worker.os.remove"):
            cert_file, key_file = self._mock_tmp_files(mock_tmp)
            run_rpa({}, b"CERT", b"KEY")
            cert_file.write.assert_called_once_with(b"CERT")
            key_file.write.assert_called_once_with(b"KEY")

    def test_calls_subprocess_with_cert_and_key_paths(self):
        with patch("worker.tempfile.NamedTemporaryFile") as mock_tmp, \
             patch("worker.subprocess.run") as mock_run, \
             patch("worker.os.remove"):
            self._mock_tmp_files(mock_tmp, "/tmp/cert_abc", "/tmp/key_abc")
            run_rpa({"task": "ecac"}, b"cert", b"key")
            cmd = mock_run.call_args[0][0]
            assert cmd == ["python3", "automation/bot.py", "/tmp/cert_abc", "/tmp/key_abc"]

    def test_subprocess_called_with_check_and_capture(self):
        with patch("worker.tempfile.NamedTemporaryFile") as mock_tmp, \
             patch("worker.subprocess.run") as mock_run, \
             patch("worker.os.remove"):
            self._mock_tmp_files(mock_tmp)
            run_rpa({}, b"c", b"k")
            _, kwargs = mock_run.call_args
            assert kwargs["check"] is True
            assert kwargs["capture_output"] is True

    def test_deletes_both_temp_files_on_success(self):
        with patch("worker.tempfile.NamedTemporaryFile") as mock_tmp, \
             patch("worker.subprocess.run"), \
             patch("worker.os.remove") as mock_remove:
            self._mock_tmp_files(mock_tmp)
            run_rpa({}, b"c", b"k")
            assert mock_remove.call_count == 2
            mock_remove.assert_any_call("/tmp/cert_abc")
            mock_remove.assert_any_call("/tmp/key_abc")

    def test_deletes_temp_files_even_when_subprocess_raises(self):
        with patch("worker.tempfile.NamedTemporaryFile") as mock_tmp, \
             patch("worker.subprocess.run") as mock_run, \
             patch("worker.os.remove") as mock_remove:
            self._mock_tmp_files(mock_tmp)
            mock_run.side_effect = subprocess.CalledProcessError(1, "python3")
            with pytest.raises(subprocess.CalledProcessError):
                run_rpa({}, b"c", b"k")
            assert mock_remove.call_count == 2

    def test_closes_temp_files_before_running_subprocess(self):
        with patch("worker.tempfile.NamedTemporaryFile") as mock_tmp, \
             patch("worker.subprocess.run"), \
             patch("worker.os.remove"):
            cert_file, key_file = self._mock_tmp_files(mock_tmp)
            run_rpa({}, b"c", b"k")
            cert_file.close.assert_called_once()
            key_file.close.assert_called_once()


class TestProcessJob:
    def _make_db_session_ctx(self):
        """Return a mock AsyncSessionLocal() context manager that yields a mock session."""
        mock_session = AsyncMock()
        mock_ctx = AsyncMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_session)
        mock_ctx.__aexit__ = AsyncMock(return_value=False)
        mock_session_local = MagicMock(return_value=mock_ctx)
        return mock_session_local, mock_session

    async def test_empty_job_raises_runtime_error(self):
        with pytest.raises(RuntimeError, match="Job missing client_id"):
            await process_job({})

    async def test_none_client_id_raises_runtime_error(self):
        with pytest.raises(RuntimeError, match="Job missing client_id"):
            await process_job({"client_id": None})

    async def test_fetches_cert_with_db_session_and_calls_run_rpa(self):
        job = {"client_id": "abc123", "task": "ecac"}
        mock_session_local, mock_session = self._make_db_session_ctx()

        with patch("worker.AsyncSessionLocal", mock_session_local), \
             patch("worker.fetch_client_cert", new_callable=AsyncMock, return_value=(b"cert", b"key")) as mock_fetch, \
             patch("worker.asyncio.get_event_loop") as mock_get_loop:
            mock_loop = AsyncMock()
            mock_loop.run_in_executor = AsyncMock(return_value=None)
            mock_get_loop.return_value = mock_loop

            await process_job(job)

        mock_fetch.assert_called_once_with(mock_session, "abc123")
        mock_loop.run_in_executor.assert_called_once()
        executor_args = mock_loop.run_in_executor.call_args[0]
        assert executor_args[1] is run_rpa
        assert executor_args[2] == job
        assert executor_args[3] == b"cert"
        assert executor_args[4] == b"key"

    async def test_fetch_cert_error_propagates(self):
        mock_session_local, _ = self._make_db_session_ctx()

        with patch("worker.AsyncSessionLocal", mock_session_local), \
             patch("worker.fetch_client_cert", new_callable=AsyncMock, side_effect=RuntimeError("No cert")), \
             pytest.raises(RuntimeError, match="No cert"):
            await process_job({"client_id": "abc123"})

    async def test_run_rpa_error_propagates(self):
        mock_session_local, _ = self._make_db_session_ctx()

        with patch("worker.AsyncSessionLocal", mock_session_local), \
             patch("worker.fetch_client_cert", new_callable=AsyncMock, return_value=(b"c", b"k")), \
             patch("worker.asyncio.get_event_loop") as mock_get_loop:
            mock_loop = AsyncMock()
            mock_loop.run_in_executor = AsyncMock(
                side_effect=subprocess.CalledProcessError(1, "python3")
            )
            mock_get_loop.return_value = mock_loop

            with pytest.raises(subprocess.CalledProcessError):
                await process_job({"client_id": "abc123"})
