# Fabric Docker Setup Test Suite

Comprehensive validation tests for Fabric Docker configuration, API keys, and service health.

## Quick Start

```bash
cd ~/workspace/fabric-web/tests
./run_tests.sh
```

## What Gets Tested

### Phase 1: Configuration Tests (No Docker Required)

#### ✅ API Key Validation
- **ANTHROPIC_API_KEY** - Format: `sk-ant-*`, min length 30
- **OPENAI_API_KEY** - Format: `sk-*`, min length 40  
- **GEMINI_API_KEY** - Format: `AIza*`, min length 30
- **GROQ_API_KEY** - Format: `gsk_*`, min length 30
- **YOUTUBE_API_KEY** (optional)
- **JINA_AI_API_KEY** (optional)
- **OLLAMA_API_URL** (optional)

#### ✅ Default Configuration
- DEFAULT_VENDOR (must be: OpenAI, Anthropic, Groq, Gemini, or Ollama)
- DEFAULT_MODEL (any valid model name)
- API base URLs for all providers

#### ✅ Dockerfile Validation
- `Dockerfile.api` - Syntax and structure
- `Dockerfile.svelte` - Syntax and structure
- `Dockerfile` (Streamlit) - Syntax and structure

### Phase 2: Docker Tests (Requires Docker Running)

#### ✅ Docker Daemon
- Checks if Docker Desktop is running
- Validates Docker API connectivity

#### ✅ Docker Compose
- Validates `docker-compose.yml` syntax
- Checks service definitions:
  - fabric-api
  - fabric-web-svelte
  - fabric-web-streamlit

#### ✅ Docker Volumes
- fabric-docker_fabric-config
- fabric-docker_fabric-patterns
- fabric-docker_fabric-logs

#### ✅ Docker Network
- fabric-docker_fabric-net

### Phase 3: Service Health Tests (Requires Services Running)

#### ✅ Service Health Endpoints
- **fabric-api**: http://localhost:8080/health
- **fabric-web-svelte**: http://localhost:5173/
- **fabric-web-streamlit**: http://localhost:8502/_stcore/health

## Test Output Example

```
============================================================
              Fabric Docker Setup Validation
============================================================

============================================================
                    API Key Validation
============================================================

✓ PASS - ANTHROPIC_API_KEY format
       Valid key (length: 108)
✓ PASS - OPENAI_API_KEY format
       Valid key (length: 132)
✓ PASS - GEMINI_API_KEY format
       Valid key (length: 39)
✓ PASS - GROQ_API_KEY format
       Valid key (length: 56)

============================================================
                      Test Summary
============================================================

Total Tests: 28
Passed: 21
Failed: 7
Success Rate: 75.0%
```

## Running Specific Tests

### Test Only Configuration (No Docker)
```python
from test_fabric_setup import FabricTestSuite

suite = FabricTestSuite()
suite.load_env_file()
suite.test_api_keys()
suite.test_default_config()
```

### Test Docker Setup
```python
suite = FabricTestSuite()
suite.test_docker_availability()
suite.test_dockerfile_syntax()
suite.test_docker_compose_syntax()
```

### Test Running Services
```python
suite = FabricTestSuite()
base_urls = {
    'api': 'http://localhost:8080',
    'svelte': 'http://localhost:5173',
    'streamlit': 'http://localhost:8502',
}
suite.test_service_health_endpoints(base_urls)
```

## Expected Results

### Before Docker Build
- ✅ All configuration tests should pass
- ✅ Dockerfile validation should pass
- ❌ Volume/network tests will show "not found" (normal)
- ❌ Service health checks will fail (services not running)

### After Docker Build
- ✅ All configuration tests should pass
- ✅ All Docker tests should pass
- ❌ Service health checks will fail (services not started)

### After Services Started
- ✅ All tests should pass (100%)

## Continuous Integration

Add to your CI/CD pipeline:

```yaml
# .github/workflows/test.yml
name: Fabric Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: |
          cd tests
          ./run_tests.sh
```

## Troubleshooting

### "Cannot proceed without .env file"
**Solution:** Copy `.env.example` to `.env` and add API keys
```bash
cp .env.example .env
nano .env
```

### "Docker daemon not responding"
**Solution:** Start Docker Desktop
```bash
open -a Docker
# Wait 30-60 seconds
```

### "Service not running" (health checks)
**Solution:** Start services
```bash
cd ~/workspace/fabric-web
docker-compose up -d
```

### "Invalid API key format"
**Solution:** Check API key prefixes:
- Anthropic: `sk-ant-api03-...`
- OpenAI: `sk-proj-...` or `sk-...`
- Gemini: `AIza...`
- Groq: `gsk_...`

## Test Files

```
tests/
├── README.md              # This file
├── test_fabric_setup.py   # Configuration & Docker tests (428 lines)
├── test_smoke.py          # End-to-end smoke tests (465 lines)
├── run_tests.sh           # Config/Docker test runner
├── run_all_tests.sh       # Complete test runner (all phases)
└── requirements.txt       # Python dependencies
```

## Smoke Tests

**Purpose:** Validate end-to-end functionality by running actual prompts through services.

**Requires:** Services must be running (`docker-compose up -d`)

### What Smoke Tests Cover

1. **API Endpoints**
   - Health check
   - List patterns (256 expected)
   - List models (all configured vendors)
   - Response time (<1s average)

2. **Pattern Execution**
   - Simple pattern ("summarize")
   - Pattern with context ("explain_code")
   - Actual AI model invocation
   - Response validation

3. **UI Loading**
   - Svelte UI HTML/JS loads
   - Streamlit UI health check
   - Page rendering validation

4. **Configuration**
   - Multiple vendors configured
   - Default model set

### Run Smoke Tests

```bash
# After services are running
cd ~/workspace/fabric-web/tests
python3 test_smoke.py
```

### Run Complete Test Suite

```bash
cd ~/workspace/fabric-web/tests
./run_all_tests.sh
```

This runs:
1. Configuration & Docker tests
2. Smoke tests (if services running)

## Exit Codes

- **0** - All tests passed
- **1** - Some tests failed

## Dependencies

- Python 3.7+
- `requests` library (auto-installed)
- Docker Desktop (for Docker tests)
- Running services (for health checks)

## Future Tests

Planned additions:
- [ ] API endpoint integration tests
- [ ] Pattern execution tests
- [ ] Model availability tests
- [ ] Performance benchmarks
- [ ] Load testing for services
- [ ] Pattern library verification

## Contributing

To add new tests, extend the `FabricTestSuite` class in `test_fabric_setup.py`:

```python
def test_new_feature(self) -> bool:
    """Test description"""
    self.print_header("New Feature Test")
    
    # Your test logic here
    success = True
    
    self.print_test("Feature name", success, "Details")
    return success
```

Then add to `run_all_tests()` function.
