#!/usr/bin/env bash
# docker-up.sh — Pull secrets from Infisical, then start Docker Compose.
#
# Usage:
#   ./scripts/docker-up.sh              # dev environment (default)
#   ./scripts/docker-up.sh prod         # production environment
#   ./scripts/docker-up.sh dev --build  # dev + rebuild images
#
# Requires: infisical CLI authenticated (infisical login)

set -euo pipefail

ENV="${1:-dev}"
shift 2>/dev/null || true
EXTRA_ARGS="$*"

echo "▸ Pulling secrets from Infisical (env: ${ENV})..."
infisical export --env="${ENV}" --format=dotenv > .env

echo "▸ Validating environment..."
node scripts/validate-env.mjs

echo "▸ Starting Docker Compose..."
# shellcheck disable=SC2086
docker compose up -d ${EXTRA_ARGS}

echo "✓ Stack is up. Secrets loaded from Infisical [${ENV}]."
