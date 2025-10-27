FROM python:3.11-slim

# Install system dependencies including SQLite3
RUN apt-get update && apt-get install -y \
    sqlite3 \
    libsqlite3-dev \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (Railway will set this)
EXPOSE 5000

# Run with gunicorn for production
CMD ["python", "app_clean.py"]