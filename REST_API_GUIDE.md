# Fabric REST API Guide

## Overview

Fabric includes a built-in REST API server that exposes all core functionality over HTTP. This guide covers both **Standard API** and **Ollama Compatibility** modes.

---

## 🚀 Quick Start

### Standard REST API (Port 8080)
```bash
# Start standard API only
docker-compose up -d fabric-api

# Test the API
curl http://localhost:8080/health
```

### Ollama-Compatible API (Port 11434)
```bash
# Start Ollama-compatible API
docker-compose --profile ollama up -d fabric-api-ollama

# Test Ollama endpoints
curl http://localhost:11434/api/version
curl http://localhost:11434/api/tags
```

### Start Both APIs
```bash
# Run standard + Ollama simultaneously
docker-compose --profile ollama up -d

# Standard API: http://localhost:8080
# Ollama API:    http://localhost:11434
```

---

## 📡 Standard REST API Endpoints

### Health & Status
```bash
GET /health
curl http://localhost:8080/health
```

### Patterns
```bash
# List all patterns
GET /patterns
curl http://localhost:8080/patterns

# Get specific pattern
GET /patterns/{name}
curl http://localhost:8080/patterns/summarize

# Execute pattern
POST /patterns/{name}/execute
curl -X POST http://localhost:8080/patterns/summarize/execute \
  -H "Content-Type: application/json" \
  -d '{"input": "Your text here"}'
```

### Models
```bash
# List all available models
GET /models
curl http://localhost:8080/models

# List models by vendor
GET /models?vendor=openai
curl "http://localhost:8080/models?vendor=openai"
```

### Chat Completions
```bash
# Standard chat completion
POST /v1/chat/completions
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4",
    "messages": [{"role": "user", "content": "Hello"}]
  }'

# Streaming response
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4",
    "messages": [{"role": "user", "content": "Hello"}],
    "stream": true
  }'
```

### YouTube Integration
```bash
# Extract transcript
POST /youtube/transcript
curl -X POST http://localhost:8080/youtube/transcript \
  -H "Content-Type: application/json" \
  -d '{"url": "https://youtube.com/watch?v=VIDEO_ID"}'

# Extract comments
POST /youtube/comments
curl -X POST http://localhost:8080/youtube/comments \
  -H "Content-Type: application/json" \
  -d '{"url": "https://youtube.com/watch?v=VIDEO_ID"}'
```

### Context Management
```bash
# Create context
POST /contexts
curl -X POST http://localhost:8080/contexts \
  -H "Content-Type: application/json" \
  -d '{"name": "my-context", "content": "Context data"}'

# List contexts
GET /contexts
curl http://localhost:8080/contexts

# Get context
GET /contexts/{name}
curl http://localhost:8080/contexts/my-context
```

### Strategies
```bash
# List available strategies
GET /strategies
curl http://localhost:8080/strategies

# Execute pattern with strategy
POST /patterns/{name}/execute?strategy={strategy}
curl -X POST "http://localhost:8080/patterns/analyze_code/execute?strategy=cot" \
  -H "Content-Type: application/json" \
  -d '{"input": "Your code here"}'
```

---

## 🦙 Ollama Compatibility Mode

Fabric can serve as a **drop-in replacement** for Ollama, allowing you to use any Fabric-supported AI provider through the Ollama API interface.

### Key Features
- ✅ Patterns appear as models (e.g., `summarize:latest`)
- ✅ Standard Ollama port (11434)
- ✅ Compatible with Ollama clients/tools
- ✅ Access to all Fabric AI providers

### Ollama-Compatible Endpoints

#### List Models (Patterns)
```bash
GET /api/tags
curl http://localhost:11434/api/tags

# Response:
{
  "models": [
    {"name": "summarize:latest", "modified_at": "2024-01-01T00:00:00Z"},
    {"name": "explain_code:latest", "modified_at": "2024-01-01T00:00:00Z"},
    ...
  ]
}
```

#### Chat Completions
```bash
POST /api/chat
curl -X POST http://localhost:11434/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "model": "summarize:latest",
    "messages": [
      {"role": "user", "content": "Your text to summarize"}
    ]
  }'

# Streaming response
curl -X POST http://localhost:11434/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "model": "summarize:latest",
    "messages": [{"role": "user", "content": "Text"}],
    "stream": true
  }'
```

#### Version Info
```bash
GET /api/version
curl http://localhost:11434/api/version
```

### Using Fabric as Ollama Replacement

**Configure any Ollama-compatible client:**
```bash
# Set Ollama API URL
export OLLAMA_HOST=http://localhost:11434

# Now use Ollama CLI/SDK normally
ollama list  # Lists Fabric patterns as models
ollama run summarize:latest "Text to summarize"
```

**Example with Python Ollama SDK:**
```python
import ollama

# Point to Fabric API
client = ollama.Client(host='http://localhost:11434')

# Use any pattern as a model
response = client.chat(
    model='summarize:latest',
    messages=[{'role': 'user', 'content': 'Your text here'}]
)
```

---

## 🔧 Configuration

### Environment Variables
```bash
# .env file
DEFAULT_VENDOR=groq
DEFAULT_MODEL=llama-3.3-70b-versatile
ANTHROPIC_API_KEY=your_key
OPENAI_API_KEY=your_key
GROQ_API_KEY=your_key
YOUTUBE_API_KEY=your_key
```

### Docker Compose Profiles

**Standard API only (default):**
```bash
docker-compose up -d
# Starts: fabric-api, fabric-web-svelte, fabric-web-streamlit
```

**With Ollama compatibility:**
```bash
docker-compose --profile ollama up -d
# Starts: everything + fabric-api-ollama
```

**Ollama only:**
```bash
docker-compose up -d fabric-api-ollama --profile ollama
# Starts: fabric-api-ollama only
```

---

## 🧪 Testing

### Test Standard API
```bash
# Health check
curl http://localhost:8080/health

# List patterns
curl http://localhost:8080/patterns | jq '.patterns | length'

# Execute pattern
echo "This is a test" | curl -X POST http://localhost:8080/patterns/summarize/execute \
  -H "Content-Type: application/json" \
  -d @-
```

### Test Ollama API
```bash
# Version
curl http://localhost:11434/api/version

# List models
curl http://localhost:11434/api/tags | jq '.models[0:5]'

# Chat (non-streaming)
curl -X POST http://localhost:11434/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "model": "summarize:latest",
    "messages": [{"role": "user", "content": "Hello world"}],
    "stream": false
  }' | jq
```

### Automated Tests
```bash
cd tests
python3 test_smoke.py  # Includes API endpoint tests
```

---

## 🔐 Authentication (Optional)

To add authentication, set environment variables:

```bash
# In .env
API_KEY=your_secret_key
API_AUTH_ENABLED=true
```

Then include the key in requests:
```bash
curl -H "Authorization: Bearer your_secret_key" \
  http://localhost:8080/patterns
```

---

## 📊 Monitoring

### Check Container Logs
```bash
# Standard API
docker logs -f fabric-api

# Ollama API
docker logs -f fabric-api-ollama
```

### Health Checks
```bash
# Standard API
docker exec fabric-api curl -f http://localhost:8080/health

# Ollama API
docker exec fabric-api-ollama curl -f http://localhost:11434/api/version
```

### Performance Metrics
```bash
# Request latency
time curl http://localhost:8080/patterns

# Pattern execution time
time curl -X POST http://localhost:8080/patterns/summarize/execute \
  -H "Content-Type: application/json" \
  -d '{"input": "Test"}'
```

---

## 🎯 Use Cases

### 1. Standard REST API
- Custom web applications
- Mobile apps
- Microservices integration
- Webhook consumers

### 2. Ollama Compatibility Mode
- Existing Ollama clients
- LangChain/LlamaIndex integration
- Open WebUI
- Continue.dev VSCode extension
- Any tool expecting Ollama API

### 3. Hybrid Setup
Run both APIs simultaneously:
- Port 8080: Full Fabric REST API
- Port 11434: Ollama-compatible interface
- Same patterns, same AI providers, different interfaces

---

## 🐛 Troubleshooting

### API Not Responding
```bash
# Check if container is running
docker ps | grep fabric-api

# Check logs
docker logs fabric-api

# Restart
docker-compose restart fabric-api
```

### Port Conflicts
```bash
# Check what's using the port
lsof -i :8080
lsof -i :11434

# Change ports in docker-compose.yml
ports:
  - "8081:8080"  # Map to different host port
```

### Pattern Not Found
```bash
# Update patterns
docker exec fabric-api fabric --updatepatterns

# Verify patterns exist
docker exec fabric-api ls /home/fabric/.config/fabric/patterns
```

### API Key Issues
```bash
# Check environment variables
docker exec fabric-api env | grep API_KEY

# Verify .env file
cat .env
```

---

## 📚 Additional Resources

- [Fabric GitHub Repo](https://github.com/danielmiessler/Fabric)
- [REST API Documentation](https://github.com/danielmiessler/Fabric/blob/main/API.md)
- [Ollama API Docs](https://github.com/ollama/ollama/blob/main/docs/api.md)
- [Docker Guide](./DOCKER_GUIDE.md)
- [Integration Tests](./tests/INTEGRATION_TESTS.md)

---

## 🚦 Next Steps

1. **Start the API:**
   ```bash
   docker-compose up -d fabric-api
   ```

2. **Test basic functionality:**
   ```bash
   curl http://localhost:8080/health
   curl http://localhost:8080/patterns
   ```

3. **Try pattern execution:**
   ```bash
   echo "Sample text" | fabric -sp summarize
   ```

4. **Enable Ollama mode (optional):**
   ```bash
   docker-compose --profile ollama up -d
   curl http://localhost:11434/api/tags
   ```

5. **Run smoke tests:**
   ```bash
   cd tests && python3 test_smoke.py
   ```

---

**The Fabric REST API is now ready for integration! 🎉**
