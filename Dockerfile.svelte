# Fabric Svelte Web UI Dockerfile
# Multi-stage build for optimized production image

# Build stage
FROM node:20-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production=false

# Copy source code
COPY . .

# Create required directories and files
RUN mkdir -p static/data && \
    echo '{}' > static/data/pattern_descriptions.json

# Build for production
RUN npm run build

# Production stage
FROM node:20-alpine

# Install serve for static hosting
RUN npm install -g serve

# Create app user
RUN addgroup -g 1000 fabric && \
    adduser -D -u 1000 -G fabric fabric

# Set working directory
WORKDIR /app

# Copy built assets from builder
COPY --from=builder --chown=fabric:fabric /app/build ./build
COPY --from=builder --chown=fabric:fabric /app/package.json ./

# Switch to fabric user
USER fabric

# Expose port
EXPOSE 5173

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:5173 || exit 1

# Serve the built app
CMD ["serve", "-s", "build", "-l", "5173"]
