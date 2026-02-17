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

# Create app user (use node user that already exists)
RUN adduser -D -u 1001 fabric

# Set working directory
WORKDIR /app

# Copy built assets from builder
# SvelteKit with adapter-auto outputs to .svelte-kit/output
COPY --from=builder --chown=fabric:fabric /app/.svelte-kit ./.svelte-kit
COPY --from=builder --chown=fabric:fabric /app/package.json ./
COPY --from=builder --chown=fabric:fabric /app/node_modules ./node_modules

# Switch to fabric user
USER fabric

# Set environment variables
ENV PORT=5173
ENV HOST=0.0.0.0

# Expose port
EXPOSE 5173

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:5173 || exit 1

# Run the SvelteKit app (adapter-auto will use adapter-node in Docker)
CMD ["node", ".svelte-kit/output/server/index.js"]
