# Indian Market Web Dashboard - Docker Image

FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create required directories
RUN mkdir -p data/cache data/credentials configs logs

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DASHBOARD_HOST=0.0.0.0
ENV DASHBOARD_PORT=8080

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/', timeout=5)"

# Run the application
CMD ["python", "indian_dashboard.py", "--host", "0.0.0.0", "--port", "8080"]
