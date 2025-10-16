FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY main.py .

# 2 workers, threaded, 5s hard timeout, 5s graceful timeout
CMD ["gunicorn", "-w", "2", "-k", "gthread", "--threads", "4",
     "--timeout", "5", "--graceful-timeout", "5",
     "--bind", "0.0.0.0:8080", "main:app"]
