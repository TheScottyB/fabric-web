# Fabric Testing Suite - Comprehensive Guide

## ✅ What Was Expanded

### New Test Files Created

1. **test_unit.py** ✨ NEW (664 lines)
   - Environment configuration tests
   - File structure validation
   - Docker environment checks
   - Strategy configuration tests
   - Fabric CLI validation
   - Shell completion tests
   - Test infrastructure checks
   - Build scripts validation

2. **test_api_integration.py** ✨ NEW (784 lines)
   - Core API endpoints (health, patterns, models, strategies)
   - Pattern execution (basic, with strategies, streaming)
   - Chat completions (standard + strategy integration)
   - YouTube integration (transcript + comments)
   - Ollama compatibility (version, tags, chat)
   - Context management (create, list, retrieve)
   - Performance tests (concurrent requests, consistency)
   - Error handling tests

3. **test_fabric_setup.py** (Existing - 428 lines)
   - API key validation
   - Default configuration
   - Dockerfile syntax
   - docker-compose validation
   - Service health checks
   - Volume & network configuration

4. **test_smoke.py** (Existing - 600 lines)
   - End-to-end smoke tests
   - Pattern execution
   - YouTube workflows
   - UI tests (Svelte, Streamlit)

---

## 📊 Test Coverage Summary

### Total Test Count: **~70 tests**

| Test Suite | Test Count | Coverage |
|------------|-----------|----------|
| **Unit Tests** | 30+ | Environment, files, Docker, strategies, CLI |
| **Configuration Tests** | 28 | API keys, Dockerfiles, volumes, networks |
| **API Integration Tests** | 30+ | REST endpoints, Ollama, contexts, performance |
| **Smoke Tests** | 11 | End-to-end workflows, UIs |

---

## 🎯 Test Organization

### Phase 1: Unit Tests (No Services Required)
```bash
# Test 1: Unit Tests
python3 tests/test_unit.py

Tests:
✓ .env file exists and loads
✓ Required API keys present
✓ API key format validation
✓ Default vendor/model config
✓ Dockerfile files exist and valid
✓ Documentation files exist
✓ Docker installed and running
✓ docker-compose syntax
✓ Strategies directory and files
✓ Strategy JSON format
✓ Fabric CLI installed
✓ Fabric patterns directory
✓ Shell completions installed
✓ Test scripts exist
✓ Build scripts exist
```

```bash
# Test 2: Configuration Tests
python3 tests/test_fabric_setup.py

Tests:
✓ Load .env file
✓ API key validation (format, length)
✓ Default vendor/model
✓ Docker availability
✓ Dockerfile syntax (3 files)
✓ docker-compose.yml syntax
✓ Volume configuration
✓ Network configuration
```

### Phase 2: Integration Tests (Services Required)
```bash
# Test 3: API Integration Tests
python3 tests/test_api_integration.py

Tests:
✓ GET /health
✓ GET /patterns
✓ GET /models
✓ GET /strategies
✓ POST /chat (basic pattern)
✓ POST /chat (with strategy: cot, standard, reflexion)
✓ POST /chat (streaming)
✓ POST /v1/chat/completions
✓ POST /v1/chat/completions (with strategy)
✓ POST /youtube/transcript
✓ POST /youtube/comments
✓ GET /api/version (Ollama)
✓ GET /api/tags (Ollama)
✓ POST /api/chat (Ollama)
✓ POST /contexts (create)
✓ GET /contexts (list)
✓ GET /contexts/{name} (retrieve)
✓ Concurrent requests (5x)
✓ Response time consistency
✓ Error handling (invalid pattern, missing field, malformed JSON)
```

```bash
# Test 4: Smoke Tests
python3 tests/test_smoke.py

Tests:
✓ API health
✓ List patterns (256 expected)
✓ List models
✓ Multiple vendors configured
✓ API response time
✓ Simple pattern execution
✓ Pattern with context
✓ YouTube transcript integration
✓ YouTube comments integration
✓ Svelte UI loads
✓ Streamlit UI loads
```

---

## 🚀 Usage

### Run All Tests
```bash
cd ~/workspace/fabric-web/tests
./run_all_tests.sh
```

### Run Individual Test Suites

**Unit Tests (no services needed):**
```bash
cd ~/workspace/fabric-web/tests
python3 test_unit.py
```

**Configuration Tests (no services needed):**
```bash
python3 test_fabric_setup.py
```

**API Integration Tests (requires services):**
```bash
# Start services first
cd ~/workspace/fabric-web
docker-compose up -d

# Run tests
cd tests
python3 test_api_integration.py
```

**API + Ollama Tests (requires both APIs):**
```bash
# Start with Ollama profile
cd ~/workspace/fabric-web
docker-compose --profile ollama up -d

# Run tests
cd tests
python3 test_api_integration.py
```

**Smoke Tests (requires services):**
```bash
python3 test_smoke.py
```

---

## 📋 Test Prerequisites

### Phase 1 Tests (Unit + Config)
- ✅ Python 3
- ✅ .env file with API keys
- ✅ Docker installed
- ✅ Fabric CLI installed

### Phase 2 Tests (Integration + Smoke)
- ✅ All Phase 1 requirements
- ✅ Services running (`docker-compose up -d`)
- ✅ Python `requests` package

Install dependencies:
```bash
pip3 install requests
```

---

## 🧪 Test Scenarios Covered

### 1. Environment & Configuration
- [x] .env file parsing
- [x] API key presence and format
- [x] Default vendor/model settings
- [x] File structure validation

### 2. Docker Environment
- [x] Docker installation
- [x] Docker daemon running
- [x] docker-compose availability
- [x] Dockerfile syntax validation
- [x] docker-compose.yml syntax
- [x] Volume creation
- [x] Network creation

### 3. Strategies
- [x] Strategy directory exists
- [x] Strategy files present (JSON)
- [x] Strategy JSON format validation
- [x] Expected strategies present (cot, tot, standard, reflexion)

### 4. REST API Endpoints
- [x] Health check
- [x] Pattern listing
- [x] Model listing
- [x] Strategy listing
- [x] Pattern execution (basic)
- [x] Pattern execution with strategies
- [x] Streaming responses
- [x] Chat completions (OpenAI format)
- [x] YouTube transcript extraction
- [x] YouTube comments extraction
- [x] Context management (CRUD)

### 5. Ollama Compatibility
- [x] Version endpoint
- [x] Tags endpoint (patterns as models)
- [x] Chat endpoint
- [x] Pattern-as-model mapping

### 6. Performance
- [x] Concurrent request handling
- [x] Response time consistency
- [x] API latency (<1s for health)

### 7. Error Handling
- [x] Invalid pattern names
- [x] Missing required fields
- [x] Malformed JSON
- [x] Proper HTTP status codes

### 8. End-to-End Workflows
- [x] YouTube transcript → Fabric pattern
- [x] YouTube comments → Fabric pattern
- [x] Multi-pattern chaining
- [x] UI loading (Svelte + Streamlit)

---

## 📈 Expected Test Results

### Without Services Running
```
Phase 1: Unit Tests
✓ PASS - 30+ tests
  - Environment config: ~5 tests
  - File structure: ~8 tests
  - Docker environment: ~4 tests
  - Strategies: ~4 tests
  - Fabric CLI: ~4 tests
  - Shell config: ~2 tests
  - Test infrastructure: ~3 tests

Phase 1: Configuration Tests
⚠ PARTIAL - 21/28 tests (expected)
  - API keys: ✓ All pass
  - Config: ✓ All pass
  - Dockerfiles: ✓ All pass
  - Volumes/Networks: ✗ Not created yet

Phase 2: SKIPPED - Services not running
```

### With Services Running (Standard API)
```
Phase 1: Unit Tests
✓ PASS - 30+ tests (same as above)

Phase 1: Configuration Tests
✓ PASS - 28/28 tests
  - Volumes created: ✓
  - Networks created: ✓
  - Service health: ✓

Phase 2: API Integration Tests
✓ PASS - 30+ tests
  - Core endpoints: ✓
  - Pattern execution: ✓
  - Strategies: ✓
  - YouTube: ✓
  - Ollama: ⚠ Skipped (not running)
  - Performance: ✓
  - Error handling: ✓

Phase 2: Smoke Tests
✓ PASS - 11 tests
  - All workflows: ✓
```

### With Services + Ollama API Running
```
All Phase 1 & 2 Tests: ✓ PASS

Plus:
✓ Ollama /api/version
✓ Ollama /api/tags (256 patterns as models)
✓ Ollama /api/chat
```

---

## 🐛 Troubleshooting

### Tests Fail: "requests module not found"
```bash
pip3 install requests
```

### Tests Fail: "Docker not running"
```bash
# Start Docker Desktop
open -a Docker

# Wait 30-60 seconds for Docker to start
# Then re-run tests
```

### Tests Fail: "Connection refused on port 8080"
```bash
# Start services
cd ~/workspace/fabric-web
docker-compose up -d

# Check services are running
docker-compose ps

# View logs if issues
docker-compose logs fabric-api
```

### Ollama Tests Fail
```bash
# Start with Ollama profile
cd ~/workspace/fabric-web
docker-compose --profile ollama up -d

# Verify Ollama API is running
curl http://localhost:11434/api/version
```

### Volume/Network Tests Fail
```bash
# These fail before first start - expected
# Build and start services once:
cd ~/workspace/fabric-web
./build.sh
docker-compose up -d

# Then re-run tests
cd tests
python3 test_fabric_setup.py
```

---

## 📚 Test Documentation

### Test File Structure
```
~/workspace/fabric-web/tests/
├── test_unit.py                # Unit tests (30+ tests)
├── test_fabric_setup.py        # Config tests (28 tests)
├── test_api_integration.py     # API tests (30+ tests)
├── test_smoke.py               # E2E tests (11 tests)
├── run_all_tests.sh            # Master test runner
├── run_tests.sh                # Config test runner
├── requirements.txt            # Python dependencies
├── README.md                   # Test documentation
├── INTEGRATION_TESTS.md        # Workflow guide
└── TESTING_SUMMARY.md          # This file
```

### Test Categories

**Unit Tests** (`test_unit.py`):
- No external dependencies
- Fast execution (<10s)
- Tests configuration, files, environment

**Configuration Tests** (`test_fabric_setup.py`):
- Minimal dependencies (Docker)
- Medium execution (~20s)
- Tests setup and validation

**Integration Tests** (`test_api_integration.py`):
- Requires running services
- Slower execution (30-60s)
- Tests API endpoints, strategies, Ollama

**Smoke Tests** (`test_smoke.py`):
- Requires running services + UIs
- Slowest execution (60-120s)
- Tests complete workflows end-to-end

---

## 🎉 Benefits of Expanded Testing

### For Development
1. **Comprehensive Coverage** - 70+ tests across all layers
2. **Fast Feedback** - Unit tests run in seconds
3. **CI/CD Ready** - Separate test phases for pipelines
4. **Regression Prevention** - Catch breaks early

### For Operations
1. **Health Monitoring** - API endpoint validation
2. **Performance Baselines** - Response time tracking
3. **Configuration Validation** - Pre-deployment checks
4. **Service Dependencies** - Network/volume validation

### For Quality
1. **Strategy Testing** - All 9 strategies validated
2. **API Compatibility** - Standard + Ollama tested
3. **Error Handling** - Edge cases covered
4. **End-to-End Workflows** - Complete user journeys

---

## 🚦 Quick Reference

```bash
# Run everything
cd ~/workspace/fabric-web/tests && ./run_all_tests.sh

# Just unit tests (fast)
python3 test_unit.py

# Just API tests (requires services)
python3 test_api_integration.py

# Just smoke tests (requires services + UIs)
python3 test_smoke.py

# Check if services ready
curl http://localhost:8080/health
curl http://localhost:11434/api/version  # Ollama
```

---

## 📊 Test Execution Time

| Test Suite | Duration | Dependencies |
|-----------|----------|--------------|
| Unit Tests | ~5-10s | None |
| Configuration Tests | ~10-20s | Docker |
| API Integration Tests | ~30-60s | Running services |
| Smoke Tests | ~60-120s | Running services + UIs |
| **Total (all)** | **~2-3min** | All services |

---

**The Fabric test suite is comprehensive and production-ready! 🎉**
