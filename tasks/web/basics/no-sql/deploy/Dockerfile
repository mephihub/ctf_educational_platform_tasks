FROM node:18-alpine

# Install netcat for connectivity checks
RUN apk add --no-cache netcat-openbsd

# Set working directory
WORKDIR /app

# Copy package files
COPY package.json yarn.lock ./

# Install dependencies
RUN yarn install --frozen-lockfile

# Copy application code
COPY . .

# Create directory for MongoDB data
RUN mkdir -p /app/data

# Expose port
EXPOSE 3000

# Set environment variables
ENV NODE_ENV=production

# Create startup script that seeds database and starts app
RUN echo '#!/bin/sh' > /app/start.sh && \
    echo 'echo "Waiting for MongoDB to be ready..."' >> /app/start.sh && \
    echo 'until nc -z mongodb 27017; do' >> /app/start.sh && \
    echo '  echo "MongoDB is unavailable - sleeping"' >> /app/start.sh && \
    echo '  sleep 2' >> /app/start.sh && \
    echo 'done' >> /app/start.sh && \
    echo 'echo "MongoDB is up - seeding database..."' >> /app/start.sh && \
    echo 'npm run seed' >> /app/start.sh && \
    echo 'echo "Starting application..."' >> /app/start.sh && \
    echo 'npm start' >> /app/start.sh && \
    chmod +x /app/start.sh

# Run the startup script
CMD ["/app/start.sh"]