# Standard python 3.11 slim image
FROM python:3.11-slim

WORKDIR /app

# Upgrade pip and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the app code
COPY app/ ./app/

# Expose port 8080 (Cloud Run default)
EXPOSE 8080

# Command: use sh -c so $PORT env variable is expanded by Cloud Run properly
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port $PORT"]
