#!/usr/bin/env python3
"""
Fabric Docker Setup Validation Tests
Tests API keys, model availability, service health, and startup sequence
"""

import os
import sys
import json
import time
import subprocess
import requests
from typing import Dict, List, Tuple, Optional
from pathlib import Path

# Color codes for output
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color


class FabricTestSuite:
    """Test suite for Fabric configuration and services"""
    
    def __init__(self, env_path: str = "../.env"):
        self.env_path = Path(__file__).parent / env_path
        self.config = {}
        self.test_results = []
        
    def print_header(self, text: str):
        """Print test section header"""
        print(f"\n{BLUE}{'='*60}{NC}")
        print(f"{BLUE}{text:^60}{NC}")
        print(f"{BLUE}{'='*60}{NC}\n")
    
    def print_test(self, name: str, passed: bool, message: str = ""):
        """Print test result"""
        status = f"{GREEN}✓ PASS{NC}" if passed else f"{RED}✗ FAIL{NC}"
        print(f"{status} - {name}")
        if message:
            indent = "       "
            print(f"{indent}{message}")
        self.test_results.append((name, passed, message))
    
    def load_env_file(self) -> bool:
        """Load and parse .env file"""
        try:
            if not self.env_path.exists():
                self.print_test("Load .env file", False, f"File not found: {self.env_path}")
                return False
            
            with open(self.env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        self.config[key.strip()] = value.strip()
            
            self.print_test("Load .env file", True, f"Loaded {len(self.config)} variables")
            return True
        except Exception as e:
            self.print_test("Load .env file", False, str(e))
            return False
    
    def test_api_keys(self) -> bool:
        """Test that required API keys are present and valid format"""
        self.print_header("API Key Validation")
        
        all_passed = True
        
        # Define expected keys and their prefixes
        key_specs = {
            'ANTHROPIC_API_KEY': 'sk-ant-',
            'OPENAI_API_KEY': 'sk-',
            'GEMINI_API_KEY': 'AIza',
            'GROQ_API_KEY': 'gsk_',
        }
        
        for key_name, prefix in key_specs.items():
            if key_name in self.config:
                value = self.config[key_name]
                if value.startswith(prefix):
                    # Check length (basic validation)
                    min_length = 40 if 'OPENAI' in key_name else 30
                    if len(value) >= min_length:
                        self.print_test(f"{key_name} format", True, 
                                      f"Valid key (length: {len(value)})")
                    else:
                        self.print_test(f"{key_name} format", False, 
                                      f"Key too short: {len(value)} chars")
                        all_passed = False
                else:
                    self.print_test(f"{key_name} format", False, 
                                  f"Invalid prefix (expected: {prefix})")
                    all_passed = False
            else:
                self.print_test(f"{key_name} presence", False, "Key not found in .env")
                all_passed = False
        
        # Check optional keys
        optional_keys = ['YOUTUBE_API_KEY', 'JINA_AI_API_KEY', 'OLLAMA_API_URL']
        for key_name in optional_keys:
            if key_name in self.config:
                self.print_test(f"{key_name} (optional)", True, "Present")
        
        return all_passed
    
    def test_default_config(self) -> bool:
        """Test default vendor and model configuration"""
        self.print_header("Default Configuration")
        
        all_passed = True
        
        # Check default vendor
        if 'DEFAULT_VENDOR' in self.config:
            vendor = self.config['DEFAULT_VENDOR']
            valid_vendors = ['OpenAI', 'Anthropic', 'Groq', 'Gemini', 'Ollama']
            if vendor in valid_vendors:
                self.print_test("DEFAULT_VENDOR", True, f"Set to: {vendor}")
            else:
                self.print_test("DEFAULT_VENDOR", False, 
                              f"Unknown vendor: {vendor}")
                all_passed = False
        else:
            self.print_test("DEFAULT_VENDOR", False, "Not configured")
            all_passed = False
        
        # Check default model
        if 'DEFAULT_MODEL' in self.config:
            model = self.config['DEFAULT_MODEL']
            self.print_test("DEFAULT_MODEL", True, f"Set to: {model}")
        else:
            self.print_test("DEFAULT_MODEL", False, "Not configured")
            all_passed = False
        
        # Check API base URLs
        url_keys = {
            'ANTHROPIC_API_BASE_URL': 'https://api.anthropic.com',
            'OPENAI_API_BASE_URL': 'https://api.openai.com',
            'GROQ_API_BASE_URL': 'https://api.groq.com',
        }
        
        for key, expected_base in url_keys.items():
            if key in self.config:
                url = self.config[key]
                if expected_base in url:
                    self.print_test(f"{key}", True, url)
                else:
                    self.print_test(f"{key}", False, f"Unexpected URL: {url}")
                    all_passed = False
        
        return all_passed
    
    def test_docker_availability(self) -> bool:
        """Test if Docker is running"""
        self.print_header("Docker Availability")
        
        try:
            result = subprocess.run(
                ['docker', 'info'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                self.print_test("Docker daemon", True, "Docker is running")
                return True
            else:
                self.print_test("Docker daemon", False, "Docker not responding")
                return False
        except subprocess.TimeoutExpired:
            self.print_test("Docker daemon", False, "Docker command timeout")
            return False
        except FileNotFoundError:
            self.print_test("Docker daemon", False, "Docker command not found")
            return False
        except Exception as e:
            self.print_test("Docker daemon", False, str(e))
            return False
    
    def test_dockerfile_syntax(self) -> bool:
        """Test that Dockerfiles exist and have valid syntax"""
        self.print_header("Dockerfile Validation")
        
        dockerfiles = [
            ('Dockerfile.api', '../Dockerfile.api'),
            ('Dockerfile.svelte', '../Dockerfile.svelte'),
            ('Dockerfile (streamlit)', '../../fabric-streamlit/Dockerfile'),
        ]
        
        all_passed = True
        
        for name, path in dockerfiles:
            dockerfile_path = Path(__file__).parent / path
            if dockerfile_path.exists():
                # Check basic Dockerfile structure
                with open(dockerfile_path, 'r') as f:
                    content = f.read()
                    has_from = 'FROM ' in content
                    has_cmd_or_entrypoint = ('CMD ' in content or 'ENTRYPOINT ' in content)
                    
                    if has_from and has_cmd_or_entrypoint:
                        self.print_test(f"{name} syntax", True, str(dockerfile_path))
                    else:
                        missing = []
                        if not has_from:
                            missing.append("FROM")
                        if not has_cmd_or_entrypoint:
                            missing.append("CMD/ENTRYPOINT")
                        self.print_test(f"{name} syntax", False, 
                                      f"Missing: {', '.join(missing)}")
                        all_passed = False
            else:
                self.print_test(f"{name} existence", False, 
                              f"File not found: {dockerfile_path}")
                all_passed = False
        
        return all_passed
    
    def test_docker_compose_syntax(self) -> bool:
        """Test docker-compose.yml syntax"""
        self.print_header("Docker Compose Validation")
        
        compose_path = Path(__file__).parent / '../docker-compose.yml'
        
        if not compose_path.exists():
            self.print_test("docker-compose.yml", False, "File not found")
            return False
        
        try:
            # Test docker-compose config validation
            result = subprocess.run(
                ['docker-compose', '-f', str(compose_path), 'config'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                self.print_test("docker-compose.yml syntax", True, "Valid YAML")
                
                # Parse output to check services
                if 'fabric-api' in result.stdout:
                    self.print_test("Service: fabric-api", True, "Defined")
                if 'fabric-web-svelte' in result.stdout:
                    self.print_test("Service: fabric-web-svelte", True, "Defined")
                if 'fabric-web-streamlit' in result.stdout:
                    self.print_test("Service: fabric-web-streamlit", True, "Defined")
                
                return True
            else:
                self.print_test("docker-compose.yml syntax", False, 
                              result.stderr[:200])
                return False
        except Exception as e:
            self.print_test("docker-compose.yml syntax", False, str(e))
            return False
    
    def test_service_health_endpoints(self, base_urls: Dict[str, str]) -> bool:
        """Test service health endpoints (if services are running)"""
        self.print_header("Service Health Checks")
        
        all_passed = True
        
        health_endpoints = {
            'fabric-api': (base_urls.get('api', 'http://localhost:8080'), '/health'),
            'fabric-web-svelte': (base_urls.get('svelte', 'http://localhost:5173'), '/'),
            'fabric-web-streamlit': (base_urls.get('streamlit', 'http://localhost:8501'), '/_stcore/health'),
        }
        
        for service, (base_url, endpoint) in health_endpoints.items():
            try:
                url = f"{base_url}{endpoint}"
                response = requests.get(url, timeout=5)
                
                if response.status_code == 200:
                    self.print_test(f"{service} health", True, 
                                  f"Status: {response.status_code}")
                else:
                    self.print_test(f"{service} health", False, 
                                  f"Status: {response.status_code}")
                    all_passed = False
            except requests.exceptions.ConnectionError:
                self.print_test(f"{service} health", False, 
                              "Service not running (expected if not started)")
            except requests.exceptions.Timeout:
                self.print_test(f"{service} health", False, "Timeout")
                all_passed = False
            except Exception as e:
                self.print_test(f"{service} health", False, str(e))
                all_passed = False
        
        return all_passed
    
    def test_volume_configuration(self) -> bool:
        """Test Docker volume configuration"""
        self.print_header("Docker Volume Configuration")
        
        try:
            result = subprocess.run(
                ['docker', 'volume', 'ls', '--format', '{{.Name}}'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                volumes = result.stdout.strip().split('\n')
                expected_volumes = [
                    'fabric-web_fabric-config',
                    'fabric-web_fabric-patterns',
                    'fabric-web_fabric-logs',
                ]
                
                for vol in expected_volumes:
                    if vol in volumes:
                        self.print_test(f"Volume: {vol}", True, "Exists")
                    else:
                        self.print_test(f"Volume: {vol}", False, 
                                      "Not found (will be created on first start)")
                
                return True
            else:
                self.print_test("Volume listing", False, "Could not list volumes")
                return False
        except Exception as e:
            self.print_test("Volume listing", False, str(e))
            return False
    
    def test_network_configuration(self) -> bool:
        """Test Docker network configuration"""
        self.print_header("Docker Network Configuration")
        
        try:
            result = subprocess.run(
                ['docker', 'network', 'ls', '--format', '{{.Name}}'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                networks = result.stdout.strip().split('\n')
                expected_network = 'fabric-web_fabric-net'
                
                if expected_network in networks:
                    self.print_test(f"Network: {expected_network}", True, "Exists")
                    return True
                else:
                    self.print_test(f"Network: {expected_network}", False, 
                                  "Not found (will be created on first start)")
                    return True  # Not critical for initial tests
            else:
                self.print_test("Network listing", False, "Could not list networks")
                return False
        except Exception as e:
            self.print_test("Network listing", False, str(e))
            return False
    
    def print_summary(self):
        """Print test summary"""
        self.print_header("Test Summary")
        
        passed = sum(1 for _, result, _ in self.test_results if result)
        failed = sum(1 for _, result, _ in self.test_results if not result)
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"{GREEN}Passed: {passed}{NC}")
        print(f"{RED}Failed: {failed}{NC}")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        
        if failed > 0:
            print(f"\n{YELLOW}Failed Tests:{NC}")
            for name, result, message in self.test_results:
                if not result:
                    print(f"  - {name}: {message}")
        
        return failed == 0


def run_all_tests():
    """Run all tests"""
    suite = FabricTestSuite()
    
    print(f"{BLUE}{'='*60}{NC}")
    print(f"{BLUE}{'Fabric Docker Setup Validation':^60}{NC}")
    print(f"{BLUE}{'='*60}{NC}")
    
    # Phase 1: Configuration tests (no Docker required)
    if not suite.load_env_file():
        print(f"\n{RED}Cannot proceed without .env file{NC}")
        return False
    
    suite.test_api_keys()
    suite.test_default_config()
    suite.test_dockerfile_syntax()
    
    # Phase 2: Docker tests (require Docker running)
    docker_available = suite.test_docker_availability()
    
    if docker_available:
        suite.test_docker_compose_syntax()
        suite.test_volume_configuration()
        suite.test_network_configuration()
        
        # Phase 3: Service tests (require services running)
        base_urls = {
            'api': 'http://localhost:8080',
            'svelte': 'http://localhost:5173',
            'streamlit': 'http://localhost:8501',
        }
        suite.test_service_health_endpoints(base_urls)
    else:
        print(f"\n{YELLOW}Skipping Docker-dependent tests (Docker not running){NC}")
    
    # Print summary
    all_passed = suite.print_summary()
    
    return all_passed


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
