# Use Python 3.12 slim image as base
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set work directory
WORKDIR /app

# Install system dependencies including OpenSSL
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    openssl \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy project files
COPY . .

# Create logs directory
RUN mkdir -p logs && \
    mkdir -p staticfiles && \
    mkdir -p media

# Expose port
EXPOSE 8000

# Run migrations and start server
# Note: Using sh -c allows environment variable expansion
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]

