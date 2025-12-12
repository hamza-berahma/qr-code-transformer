FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Set working directory to web for simpler commands
WORKDIR /app/web

# Run the application
# Use sh to expand PORT environment variable
CMD sh -c "python -m uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}"

