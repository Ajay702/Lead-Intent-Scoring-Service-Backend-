# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

# Install deps
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

ENV FLASK_APP=app

# Create instance folder for SQLite
RUN mkdir -p instance

# Use PORT environment variable for cloud deployment
EXPOSE $PORT
CMD gunicorn -w 1 -b 0.0.0.0:$PORT "app:create_app()"
