# Standard python 3.11 slim image
FROM python:3.11-slim

WORKDIR /app

# Upgrade pip and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the app code and runner
COPY app/ ./app/
COPY run.py .

# Expose port 8080 (Cloud Run default)
EXPOSE 8080

# Command to run the Fastapi application perfectly synchronously
CMD ["python", "run.py"]
