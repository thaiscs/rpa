FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir nicegui==3.9.0 httpx
# pip freeze > requirements.txt
EXPOSE 3000
CMD ["python", "main.py", "--reload"]