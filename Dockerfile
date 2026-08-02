FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD gunicorn scraper:app -b 0.0.0.0:${PORT:-8080}# Use the official Playwright Python image (includes all browser dependencies)
FROM mcr.microsoft.com/playwright/python:v1.44.0-jammy

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Run the scraper via gunicorn on the specified port
CMD gunicorn scraper:app -b 0.0.0.0:${PORT:-8080}
