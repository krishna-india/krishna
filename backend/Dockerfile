FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
COPY backend /app
COPY utils.py streaming.py assets /app/
EXPOSE 8000
CMD ["uvicorn", "main:app", "--workers", "4", "--host", "0.0.0.0", "--port", "8000"]
