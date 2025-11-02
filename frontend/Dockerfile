# Use Node 23 slim image as base
FROM node:23-slim

# Set working directory
WORKDIR /app

# Install dependencies for node-gyp and healthchecks
RUN apt-get update && apt-get install -y \
    python3 \
    make \
    g++ \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm i

# Copy project files
COPY . .

# Build the Next.js application
RUN npm run build

# Expose port
EXPOSE 3000

# Set environment to production
ENV NODE_ENV=production

# Start the application
CMD ["npm", "start"]

