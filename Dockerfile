# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.9-slim

# Allow statements and log messages to immediately appear in the logs
ENV PYTHONUNBUFFERED=1

# Copy local code to the container image.
WORKDIR /app

# Install production dependencies.
# Explicitly use PyPI for the download index
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --index-url https://pypi.org/simple

# Copy the rest of the application
COPY . .

# Run the web service on container startup.
# Gunicorn binds to the port specified by the PORT environment variable (default 8080 on Cloud Run)
CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 0 app:app
