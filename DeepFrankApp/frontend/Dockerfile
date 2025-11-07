# Development Dockerfile for DeepFrank Frontend
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Install dependencies first (for better caching)
COPY package.json package-lock.json* ./
RUN npm install

# Copy application code
COPY . .

# Expose Next.js port
EXPOSE 3000

# Set environment variables for development
ENV NODE_ENV=development
ENV NEXT_TELEMETRY_DISABLED=1

# Run the development server
# The dev script already includes --hostname 0.0.0.0 for Docker compatibility
CMD ["npm", "run", "dev"]

