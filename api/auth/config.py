import os

def load_secret():
    file_path = os.getenv("AUTH_SECRET_FILE")
    if file_path and os.path.exists(file_path):
        with open(file_path, "r") as f:
            return f.read().strip()
    return os.getenv("AUTH_SECRET")

SECRET = load_secret()