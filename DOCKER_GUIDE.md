# Fabric Docker Guide

Canonical runbook for running Fabric API + Svelte + Streamlit in Docker.

## Workspace

```bash
cd /Users/scottybe/workspace/fabric-docker
```

## Prerequisites

- Docker Desktop running
- `.env` present (`cp .env.example .env`)
- At least one model provider configured in `.env` or `OLLAMA_API_BASE`

## Build and Start

```bash
# Validate compose

docker compose config -q

# Build images

docker compose build fabric-api fabric-web-svelte fabric-web-streamlit

# Start stack

docker compose up -d

# Service state

docker compose ps
```

## Services

- API: [http://localhost:8080](http://localhost:8080)
- Svelte UI: [http://localhost:5173](http://localhost:5173)
- Streamlit UI: [http://localhost:8501](http://localhost:8501)

## Health Checks

```bash
curl -fsS http://localhost:8080/models/names >/dev/null
curl -fsS http://localhost:5173 >/dev/null
curl -fsS http://localhost:8501/_stcore/health >/dev/null
```

## Runtime Model

- `fabric-web-svelte` runs compiled SvelteKit Node output (`node build`)
- No Vite dev server in container runtime

## Logs and Debugging

```bash
docker compose logs -f
docker compose logs -f fabric-api
docker compose logs -f fabric-web-svelte
docker compose logs -f fabric-web-streamlit
```

## Smoke Test Checklist

```bash
npm ci --force
npm run env:validate
npm run check
npm run build
npm run test
docker compose config -q
docker compose build fabric-api fabric-web-svelte
docker compose up -d
```

## Shutdown

```bash
docker compose down
```

## Full Cleanup

```bash
docker compose down -v --rmi local
```
