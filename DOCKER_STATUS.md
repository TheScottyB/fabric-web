# Fabric Docker Status

## Current State Model

This project is configured for production-like reliability in Docker:

- `fabric-api` healthy on `:8080`
- `fabric-web-svelte` healthy on `:5173`
- `fabric-web-streamlit` healthy on `:8501`

Svelte runtime is compiled adapter-node output (`node build`) rather than Vite dev mode.

## Verification Commands

```bash
cd /Users/scottybe/workspace/fabric-docker

docker compose config -q
docker compose build fabric-api fabric-web-svelte fabric-web-streamlit
docker compose up -d
docker compose ps

curl -fsS http://localhost:8080/models/names >/dev/null
curl -fsS http://localhost:5173 >/dev/null
curl -fsS http://localhost:8501/_stcore/health >/dev/null
```

## Reliability Gates

The repo CI workflow (`.github/workflows/ci.yml`) enforces:

1. `quality-gates`: install, env validation, check, build, test
2. `docker-smoke`: compose config + API/Svelte image builds

## Known Limitations (Current)

- `/chat` behavior remains upstream-dependent; no API contract changes were made in this hardening release.
- Warning cleanup is scoped to touched files; repo-wide warning debt may still exist.

## Rollback

If runtime startup regresses after deployment hardening:

1. Revert Docker/Svelte runtime commits.
2. Rebuild images.
3. Redeploy with `docker compose up -d --build`.
