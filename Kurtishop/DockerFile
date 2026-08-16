FROM python:3.11-slim

# Prevent Python from creating .pyc files 
# and ensure logs are immediately displayed
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Application directory
WORKDIR /app

# Install dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       libpq-dev \
       gcc \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Install Python dependencies
# This allows Docker to cache this year
# When application code changes but requirements do not
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Create directory for collected static files
RUN mkdir -p /app/staticfiles

# Django/Gunicorn listen on port 8000
EXPOSE 8000

# Production WSGI server
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]