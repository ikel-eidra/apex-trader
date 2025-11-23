FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Copy pre-built dashboard
COPY dashboard/dist ./dashboard/dist

# Create data directory
RUN mkdir -p data

# Expose API port
EXPOSE 10000

# Run the bot
CMD ["python", "main.py"]
