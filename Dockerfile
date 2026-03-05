FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

CMD ["sh", "-c", "echo '=== Container start ===' && python seed.py && echo '=== Seed OK ===' && exec python main.py"]
