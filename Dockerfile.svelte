# Fabric Svelte Web UI Dockerfile
# Multi-stage production image using SvelteKit adapter-node runtime

FROM node:20-alpine AS builder
WORKDIR /app

COPY package*.json ./
RUN npm install --force

COPY . .
RUN mkdir -p static/data && echo '{"patterns":[]}' > static/data/pattern_descriptions.json
RUN npm run build

FROM node:20-alpine AS runtime
WORKDIR /app

RUN adduser -D -u 1001 fabric

COPY package*.json ./
RUN npm install --omit=dev --force && npm cache clean --force

COPY --from=builder /app/build ./build
COPY --from=builder /app/static ./static

RUN chown -R fabric:fabric /app
USER fabric

ENV NODE_ENV=production
ENV PORT=5173
ENV HOST=0.0.0.0

EXPOSE 5173

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://127.0.0.1:5173/ || exit 1

CMD ["node", "build"]
