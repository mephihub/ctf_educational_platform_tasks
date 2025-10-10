FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and templates
COPY app.py .
COPY init_db.py .
COPY templates/ ./templates/

# Create directory for SQLite database
RUN mkdir -p /app/data

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Initialize database and run the application
CMD ["sh", "-c", "python init_db.py && python app.py"]
