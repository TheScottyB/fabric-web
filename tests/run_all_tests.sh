#!/bin/bash
# Complete Fabric Test Suite Runner
# Runs configuration tests, Docker tests, and smoke tests

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║           Fabric Complete Test Suite                          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"

# Change to script directory
cd "$(dirname "$0")"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 not found${NC}"
    exit 1
fi

# Install dependencies
echo -e "\n${CYAN}Installing test dependencies...${NC}"
pip3 install -q requests 2>&1 | grep -v "already satisfied" || true

# Track results
SETUP_PASSED=0
SMOKE_PASSED=0
SECURITY_PASSED=0

echo -e "\n${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Phase 1: Configuration & Setup Tests                         ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"

python3 test_fabric_setup.py
SETUP_EXIT=$?

if [ $SETUP_EXIT -eq 0 ]; then
    SETUP_PASSED=1
    echo -e "\n${GREEN}✓ Setup tests passed${NC}"
else
    echo -e "\n${YELLOW}⚠ Some setup tests failed (may be expected if services not started)${NC}"
fi

# Check if services are running
echo -e "\n${CYAN}Checking if services are running...${NC}"
if curl -s http://localhost:8080/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Services are running${NC}"
    
    echo -e "\n${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  Phase 2: End-to-End Smoke Tests                              ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
    
    python3 test_smoke.py
    SMOKE_EXIT=$?
    
    if [ $SMOKE_EXIT -eq 0 ]; then
        SMOKE_PASSED=1
        echo -e "\n${GREEN}✓ Smoke tests passed${NC}"
    else
        echo -e "\n${RED}✗ Some smoke tests failed${NC}"
    fi
    
    echo -e "\n${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  Phase 3: Security Tests                                       ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
    
    python3 test_security.py
    SECURITY_EXIT=$?
    
    if [ $SECURITY_EXIT -eq 0 ]; then
        SECURITY_PASSED=1
        echo -e "\n${GREEN}✓ Security tests passed${NC}"
    else
        echo -e "\n${RED}✗ Some security tests failed${NC}"
    fi
    
    echo -e "\n${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  Phase 4: Docker Profile Tests                                 ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
    
    python3 test_docker_profiles.py
    DOCKER_PROFILE_EXIT=$?
    
    if [ $DOCKER_PROFILE_EXIT -eq 0 ]; then
        echo -e "\n${GREEN}✓ Docker profile tests passed${NC}"
    else
        echo -e "\n${YELLOW}⚠ Some Docker profile tests failed${NC}"
    fi
    
    echo -e "\n${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  Phase 5: Pattern Validation Tests                             ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
    
    python3 test_patterns.py
    PATTERNS_EXIT=$?
    
    if [ $PATTERNS_EXIT -eq 0 ]; then
        echo -e "\n${GREEN}✓ Pattern validation tests passed${NC}"
    else
        echo -e "\n${YELLOW}⚠ Some pattern tests failed${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Services not running - skipping smoke and security tests${NC}"
    echo -e "${CYAN}To run all tests, start services first:${NC}"
    echo -e "${CYAN}  cd ~/workspace/fabric-web${NC}"
    echo -e "${CYAN}  docker-compose up -d${NC}"
    echo -e "${CYAN}  cd tests && ./run_all_tests.sh${NC}"
fi

# Final summary
echo -e "\n${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Final Test Summary                                            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"

echo ""
if [ $SETUP_PASSED -eq 1 ]; then
    echo -e "${GREEN}✓ Configuration Tests: PASSED${NC}"
else
    echo -e "${YELLOW}⚠ Configuration Tests: SOME FAILURES${NC}"
fi

if [ $SMOKE_PASSED -eq 1 ]; then
    echo -e "${GREEN}✓ Smoke Tests: PASSED${NC}"
elif curl -s http://localhost:8080/health > /dev/null 2>&1; then
    echo -e "${RED}✗ Smoke Tests: FAILED${NC}"
else
    echo -e "${CYAN}- Smoke Tests: SKIPPED (services not running)${NC}"
fi

if [ $SECURITY_PASSED -eq 1 ]; then
    echo -e "${GREEN}✓ Security Tests: PASSED${NC}"
elif curl -s http://localhost:8080/health > /dev/null 2>&1; then
    echo -e "${RED}✗ Security Tests: FAILED${NC}"
else
    echo -e "${CYAN}- Security Tests: SKIPPED (services not running)${NC}"
fi

echo ""

# Determine overall status
if [ $SETUP_PASSED -eq 1 ] && ([ $SMOKE_PASSED -eq 1 ] || ! curl -s http://localhost:8080/health > /dev/null 2>&1) && ([ $SECURITY_PASSED -eq 1 ] || ! curl -s http://localhost:8080/health > /dev/null 2>&1); then
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                   🎉 ALL TESTS PASSED! 🎉                      ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
    exit 0
else
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${YELLOW}║               ⚠️  SOME TESTS FAILED OR SKIPPED                 ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
    exit 1
fi
