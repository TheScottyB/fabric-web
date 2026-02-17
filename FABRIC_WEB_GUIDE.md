# Fabric Web Interfaces Guide

## Architecture Overview

Fabric provides **three separate web interfaces** that all connect to the same backend API:

```
┌─────────────────────────────────────────────────────────┐
│                    Fabric Ecosystem                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │   Fabric REST API (Port 8080)                   │   │
│  │   Backend: fabric --serve                       │   │
│  └─────────────────────────────────────────────────┘   │
│                         │                               │
│          ┌──────────────┼──────────────┐               │
│          │              │              │                │
│  ┌───────▼─────┐ ┌──────▼──────┐ ┌───▼───────────┐   │
│  │   Svelte    │ │  Streamlit  │ │  Direct CLI   │   │
│  │   Web App   │ │  Python UI  │ │  Access       │   │
│  │             │ │             │ │               │   │
│  │ Port: 5173  │ │ Port: 8501  │ │ (Terminal)    │   │
│  │             │ │             │ │               │   │
│  │ Modern UI   │ │ Data Viz    │ │ Scripts       │   │
│  │ Pattern Mgmt│ │ Charts      │ │ Automation    │   │
│  │ Obsidian    │ │ Analysis    │ │               │   │
│  └─────────────┘ └─────────────┘ └───────────────┘   │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Three Web Interfaces

### 1. Svelte Web App (Modern UI) - Port 5173
**Location:** `~/workspace/fabric-web/`
**Best for:** General use, pattern management, Obsidian integration

**Features:**
- 🎨 Modern Skeleton UI framework
- 📝 Pattern execution with real-time previews
- 📚 Obsidian vault integration for notes
- 🔍 Search and filter patterns
- 📊 Markdown rendering with syntax highlighting
- 🎯 PDF processing capabilities

**Start:**
```bash
cd ~/workspace/fabric-web
npm run dev
# Visit: http://localhost:5173
```

### 2. Streamlit Python UI - Port 8501
**Location:** `/tmp/fabric-web-temp/scripts/python_ui/`
**Best for:** Data analysis, visualization, complex pattern chains

**Features:**
- 📈 Charts with Matplotlib/Seaborn
- 🔗 Pattern chaining workflows
- 📊 Data visualization and analysis
- 💾 Export results to CSV/Markdown
- 🖼️ Output management and starring
- 📋 Cross-platform clipboard support

**Start:**
```bash
cd /tmp/fabric-web-temp/scripts/python_ui
pip install -r requirements.txt
streamlit run streamlit.py
# Visit: http://localhost:8501
```

### 3. Fabric REST API - Port 8080
**Backend service required by both UIs**

**Start:**
```bash
fabric --serve --address :8080
```

## Port Assignments (No Conflicts)

| Service | Port | Purpose |
|---------|------|---------|
| Fabric API | 8080 | Backend REST API |
| Svelte UI | 5173 | Modern web interface |
| Streamlit UI | 8501 | Python data visualization UI |

## Docker Compose Setup

All three services can be managed together with Docker:

```bash
cd ~/workspace/fabric-web
docker-compose up -d
```

**Access:**
- Svelte UI: http://localhost:5173
- Streamlit UI: http://localhost:8501
- API: http://localhost:8080

**Control:**
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# Restart specific service
docker-compose restart fabric-web-svelte
```

## Manual Setup (No Docker)

### Terminal 1: Start API
```bash
fabric --serve --address :8080
```

### Terminal 2: Start Svelte UI
```bash
cd ~/workspace/fabric-web
npm run dev
```

### Terminal 3: Start Streamlit UI (Optional)
```bash
cd /tmp/fabric-web-temp/scripts/python_ui
streamlit run streamlit.py
```

## When to Use Each Interface

### Use Svelte UI when:
- ✅ You want a modern, responsive interface
- ✅ Managing and browsing patterns
- ✅ Integrating with Obsidian notes
- ✅ Processing PDFs
- ✅ General daily use

### Use Streamlit UI when:
- ✅ Analyzing pattern outputs with charts
- ✅ Running complex pattern chains
- ✅ Need data visualization
- ✅ Exporting results to CSV
- ✅ Python-centric workflows

### Use CLI when:
- ✅ Scripting and automation
- ✅ CI/CD pipelines
- ✅ Terminal-based workflows
- ✅ Quick one-off pattern runs

## Configuration

Both UIs share the same Fabric configuration:
- **Patterns:** `~/.config/fabric/patterns/`
- **Config:** `~/.config/fabric/.env`
- **Logs:** `~/.config/fabric/logs/`

## Troubleshooting

### Port Already in Use
```bash
# Check what's using a port
lsof -i :8080
lsof -i :5173
lsof -i :8501

# Kill process if needed
kill -9 <PID>
```

### API Connection Issues
Both UIs connect to `http://localhost:8080` by default. Ensure:
1. Fabric API is running: `fabric --serve`
2. No firewall blocking localhost
3. Check logs: `~/.config/fabric/logs/`

### Svelte UI Build Errors
```bash
cd ~/workspace/fabric-web
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Streamlit Dependencies
```bash
pip install streamlit pandas matplotlib seaborn numpy python-dotenv pyperclip
```

## Current Status

✅ Fabric v1.4.410 installed
✅ Patterns updated (256 total)
✅ Svelte UI ready at `~/workspace/fabric-web/`
✅ Streamlit UI available in repo
✅ Docker Compose configuration created
✅ No port conflicts

## Next Steps

1. Choose your preferred interface(s)
2. Start services (Docker or manual)
3. Configure AI providers: `fabric --setup`
4. Start using patterns!
