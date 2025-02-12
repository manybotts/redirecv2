# Use an official Python runtime as a parent image.
FROM python:3.9-slim

# Set the working directory.
WORKDIR /app

# Copy the requirements file and install dependencies.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code.
COPY . .

# Expose port 5000 (informational; actual port is set at runtime via PORT env var)
EXPOSE 5000

# Use the PORT environment variable (default to 5000 if not set)
CMD ["sh", "-c", "gunicorn redirector:app --bind 0.0.0.0:${PORT:-5000}"]
