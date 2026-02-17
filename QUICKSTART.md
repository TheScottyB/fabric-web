# Fabric Quick Start

## 🚀 One-Command Start

```bash
cd ~/workspace/fabric-web
./start-fabric.sh
```

Choose your startup mode and the script handles everything!

## 📦 What's Installed

```
~/workspace/
├── fabric-web/           # Svelte UI (Port 5173)
│   ├── docker-compose.yml
│   ├── start-fabric.sh
│   ├── FABRIC_WEB_GUIDE.md
│   └── QUICKSTART.md
│
└── fabric-streamlit/     # Streamlit UI (Port 8501)
    ├── streamlit.py
    └── requirements.txt
```

## 🌐 Three Web Interfaces

| Interface | Port | Best For | Location |
|-----------|------|----------|----------|
| **Svelte UI** | 5173 | Daily use, pattern management | `~/workspace/fabric-web` |
| **Streamlit** | 8501 | Data analysis, charts | `~/workspace/fabric-streamlit` |
| **API** | 8080 | Backend (required by both) | `fabric --serve` |

## 🐳 Docker (Recommended)

### First Time Setup
```bash
# 1. Start Docker Desktop
open -a Docker

# 2. Build images
cd ~/workspace/fabric-web
./build.sh

# 3. Configure API keys
nano .env  # Add your API keys

# 4. Start services
docker-compose up -d
```

### Daily Use
```bash
cd ~/workspace/fabric-web
docker-compose up -d       # Start all services
docker-compose logs -f     # View logs
docker-compose down        # Stop all services
```

**Access:**
- Svelte: http://localhost:5173
- Streamlit: http://localhost:8501
- API: http://localhost:8080

**See:** `DOCKER_GUIDE.md` for complete Docker documentation

## 💻 Manual Start

### Option 1: Svelte Only
```bash
# Terminal 1
fabric --serve --address :8080

# Terminal 2
cd ~/workspace/fabric-web
npm run dev
```

### Option 2: Streamlit Only
```bash
# Terminal 1
fabric --serve --address :8080

# Terminal 2
cd ~/workspace/fabric-streamlit
streamlit run streamlit.py
```

### Option 3: Both UIs
```bash
# Terminal 1
fabric --serve --address :8080

# Terminal 2
cd ~/workspace/fabric-web && npm run dev

# Terminal 3
cd ~/workspace/fabric-streamlit && streamlit run streamlit.py
```

## ⚙️ Configuration

All services share the same config:
- `~/.config/fabric/.env` - API keys and settings
- `~/.config/fabric/patterns/` - Pattern library (256 patterns)
- `fabric --setup` - Configure providers

## 🛑 Stop Services

```bash
# Quick stop (kills all Fabric processes)
pkill -f "fabric --serve"
pkill -f "vite dev"
pkill -f "streamlit run"

# Or use the script
cd ~/workspace/fabric-web
./start-fabric.sh  # Choose option 5
```

## ✅ Status Check

Currently running:
- ✅ Fabric v1.4.410
- ✅ Patterns updated (256 total)
- ✅ Svelte UI installed and working
- ✅ Streamlit UI installed
- ✅ Docker Compose configured
- ✅ No port conflicts

## 📚 Documentation

### Core Guides
- **QUICKSTART.md** (this file) - Get started fast
- **DOCKER_GUIDE.md** - Complete Docker reference
- **REST_API_GUIDE.md** - REST API & Ollama compatibility
- **STRATEGIES_GUIDE.md** - AI reasoning strategies
- **tests/INTEGRATION_TESTS.md** - Testing & workflows

### Quick Links
```bash
# REST API (Standard)
curl http://localhost:8080/patterns

# REST API (Ollama-compatible on port 11434)
docker-compose --profile ollama up -d
curl http://localhost:11434/api/tags

# Strategies (AI reasoning)
fabric -S  # Install strategies
fabric --strategy cot -p analyze_code < input.txt

# Shell completions
fabric --<TAB>  # Auto-complete!
```
