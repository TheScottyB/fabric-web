# Fabric Docker Guide

Complete guide for running all three Fabric interfaces in Docker.

## Quick Start

```bash
# 1. Start Docker Desktop (if not running)
open -a Docker

# 2. Build all images
cd ~/workspace/fabric-web
./build.sh

# 3. Configure API keys
cp .env.example .env
# Edit .env with your API keys

# 4. Start all services
docker-compose up -d

# 5. Access interfaces
# Svelte UI:    http://localhost:5173
# Streamlit UI: http://localhost:8501
# API:          http://localhost:8080
```

## Prerequisites

- Docker Desktop for Mac installed and running
- At least one AI provider API key (OpenAI, Anthropic, Google, etc.)

## Project Structure

```
~/workspace/fabric-web/
├── Dockerfile.api          # Fabric REST API container
├── Dockerfile.svelte       # Svelte UI container
├── docker-compose.yml      # Orchestration configuration
├── .env                    # Your API keys (create from .env.example)
├── .env.example            # Template for environment variables
├── build.sh                # Build all Docker images
├── start-fabric.sh         # Interactive startup script
├── package.json            # Svelte dependencies
└── src/                    # Svelte source code

~/workspace/fabric-streamlit/
├── Dockerfile              # Streamlit UI container
├── streamlit.py            # Streamlit application
└── requirements.txt        # Python dependencies
```

## Step-by-Step Setup

### 1. Start Docker

```bash
# Check if Docker is running
docker info

# If not running, start Docker Desktop
open -a Docker

# Wait for Docker to be ready
until docker info >/dev/null 2>&1; do echo "Waiting for Docker..."; sleep 2; done
```

### 2. Build Docker Images

```bash
cd ~/workspace/fabric-web
./build.sh
```

This will:
- Validate all Dockerfiles exist
- Create `.env` from `.env.example` if needed
- Build three Docker images:
  - `fabric-api:latest` (Go-based REST API)
  - `fabric-web-svelte:latest` (Node.js Svelte UI)
  - `fabric-web-streamlit:latest` (Python Streamlit UI)

### 3. Configure Environment

```bash
# Copy template
cp .env.example .env

# Edit with your API keys
nano .env  # or use your preferred editor
```

**Required:** At minimum, add ONE AI provider API key:
```bash
# Example for OpenAI
OPENAI_API_KEY=sk-your-actual-api-key-here

# Or for Anthropic
ANTHROPIC_API_KEY=sk-ant-your-actual-api-key-here

# Or for Google
GOOGLE_API_KEY=your-google-api-key-here
```

### 4. Start Services

**Option A: Using docker-compose directly**
```bash
cd ~/workspace/fabric-web
docker-compose up -d
```

**Option B: Using the interactive script**
```bash
cd ~/workspace/fabric-web
./start-fabric.sh
# Choose option 1 or 2
```

### 5. Verify Services

```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs -f

# Check health
docker-compose ps | grep healthy
```

## Service Architecture

```
┌─────────────────────────────────────────┐
│           Docker Network                │
│              fabric-net                 │
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────────────────────────────┐   │
│  │   fabric-api (Port 8080)        │   │
│  │   • Go 1.25                     │   │
│  │   • Fabric CLI                  │   │
│  │   • REST API Server             │   │
│  │   • Health check enabled        │   │
│  └─────────────┬───────────────────┘   │
│                │                        │
│     ┌──────────┴──────────┐            │
│     │                     │             │
│  ┌──▼─────────┐  ┌───────▼──────────┐ │
│  │  svelte    │  │   streamlit      │ │
│  │  (5173)    │  │    (8501)        │ │
│  │  Node 20   │  │   Python 3.11    │ │
│  │  Skeleton  │  │   Data viz       │ │
│  │  UI        │  │   Charts         │ │
│  └────────────┘  └──────────────────┘ │
│                                         │
└─────────────────────────────────────────┘
         │              │             │
         ▼              ▼             ▼
    Host Ports: 5173    8501        8080
```

## Docker Volumes

Persistent data is stored in named volumes:

| Volume | Purpose | Data |
|--------|---------|------|
| `fabric-config` | API configuration | `.env` settings, API keys |
| `fabric-patterns` | Pattern library | 256 AI prompts/patterns |
| `fabric-logs` | Application logs | Service logs, debugging |

## Common Commands

### Start/Stop

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart a specific service
docker-compose restart fabric-api
```

### Logs and Debugging

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f fabric-api
docker-compose logs -f fabric-web-svelte
docker-compose logs -f fabric-web-streamlit

# Check last 100 lines
docker-compose logs --tail=100
```

### Rebuild

```bash
# Rebuild all images
./build.sh

# Or rebuild specific service
docker-compose build fabric-api
docker-compose build fabric-web-svelte
docker-compose build fabric-web-streamlit

# Rebuild and restart
docker-compose up -d --build
```

### Volume Management

```bash
# List volumes
docker volume ls | grep fabric

# Inspect a volume
docker volume inspect fabric-patterns

# Backup patterns
docker run --rm -v fabric-patterns:/data -v $(pwd):/backup \
  alpine tar czf /backup/patterns-backup.tar.gz /data

# Restore patterns
docker run --rm -v fabric-patterns:/data -v $(pwd):/backup \
  alpine tar xzf /backup/patterns-backup.tar.gz -C /

# Remove all volumes (WARNING: deletes all data)
docker-compose down -v
```

### Cleanup

```bash
# Remove containers
docker-compose down

# Remove containers and volumes
docker-compose down -v

# Remove images
docker rmi fabric-api:latest fabric-web-svelte:latest fabric-web-streamlit:latest

# Complete cleanup
docker-compose down -v --rmi all
```

## Troubleshooting

### Docker Not Running

```bash
# Check Docker status
docker info

# Start Docker Desktop
open -a Docker

# Wait for Docker
until docker info >/dev/null 2>&1; do sleep 2; done
```

### Build Failures

```bash
# Check Dockerfile syntax
docker build -t test -f Dockerfile.api .

# Clear build cache
docker builder prune -a

# Rebuild from scratch
docker-compose build --no-cache
```

### Container Won't Start

```bash
# Check logs
docker-compose logs fabric-api

# Check if port is already in use
lsof -i :8080
lsof -i :5173
lsof -i :8501

# Kill conflicting processes
pkill -f "fabric --serve"
pkill -f "npm run dev"
pkill -f "streamlit run"
```

### API Connection Issues

```bash
# Test API from host
curl http://localhost:8080/health

# Test API from within network
docker-compose exec fabric-web-svelte curl http://fabric-api:8080/health

# Check network
docker network inspect fabric_fabric-net
```

### Volume Permission Issues

```bash
# All containers run as user 'fabric' (UID 1000)
# If you see permission errors, check volume permissions

# Fix permissions
docker-compose down
docker volume rm fabric-config fabric-patterns fabric-logs
docker-compose up -d
```

### Missing Patterns

```bash
# Check if patterns volume has data
docker run --rm -v fabric-patterns:/data alpine ls -la /data

# Manually update patterns
docker-compose exec fabric-api fabric --updatepatterns
```

## Health Checks

All services have health checks:

```bash
# Check health status
docker-compose ps

# Manually test health endpoints
curl http://localhost:8080/health              # API
wget -q -O- http://localhost:5173 >/dev/null   # Svelte
curl http://localhost:8501/_stcore/health      # Streamlit
```

## Performance Tips

1. **Multi-stage builds**: Already implemented for optimal image sizes
2. **Layer caching**: Build images once, reuse unless code changes
3. **Resource limits**: Add to docker-compose.yml if needed:
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '1'
         memory: 1G
   ```

## Security Best Practices

1. **Never commit `.env`** - Already in `.gitignore`
2. **Use read-only volumes** where possible - Streamlit uses `:ro` flags
3. **Non-root users** - All containers run as user `fabric` (UID 1000)
4. **Network isolation** - Services communicate via internal network
5. **Health checks** - Monitors service status automatically

## Next Steps

1. Configure your AI provider API keys in `.env`
2. Start services with `docker-compose up -d`
3. Access Svelte UI at http://localhost:5173
4. Try running patterns from the web interface
5. Check Streamlit UI at http://localhost:8501 for data viz

## Support

- Docker logs: `docker-compose logs -f`
- Fabric patterns: 256 available after first start
- Health status: `docker-compose ps`
- Full documentation: `FABRIC_WEB_GUIDE.md`
