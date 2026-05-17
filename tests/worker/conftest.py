import sys
from pathlib import Path

# The worker service runs from the worker/ directory, so worker.py is importable
# as `import worker` from there. Add it to sys.path so tests can do the same.
_worker_dir = str(Path(__file__).parent.parent.parent / "worker")
if _worker_dir not in sys.path:
    sys.path.insert(0, _worker_dir)
