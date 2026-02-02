# Use official Python runtime as base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Create data directory for persistence
RUN mkdir -p /app/data

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot code
COPY bot.py .

# Run the bot
CMD ["python", "-u", "bot.py"]
