FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    socat \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install pycryptodome

# Set working directory
WORKDIR /app

# Copy the task files
COPY task.py /app/
COPY flag.py /app/

# Make the task executable
RUN chmod +x /app/task.py

# Expose port 1337
EXPOSE 1337

# Run socat to listen on port 1337 and execute the task
CMD ["socat", "TCP-LISTEN:1337,fork,reuseaddr", "EXEC:python3 /app/task.py"]
