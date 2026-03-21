FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
# build-essential is often needed for some python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose ports
# 8000 for Token Server
# Agent doesn't strictly "listen" on a port in the traditional HTTP sense for incoming requests 
# (it connects OUT to LiveKit), but we might expose health checks.
EXPOSE 8000

# Script to run both services or choose one based on env var
# For production, you might want to run them as separate containers or use supervisord.
# For simplicity here, we'll default to running the token server, 
# but provide a way to override key commands.

# Make the startup script executable
RUN chmod +x start_prod.sh

# Run the production startup script
CMD ["./start_prod.sh"]
