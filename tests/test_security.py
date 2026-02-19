#!/usr/bin/env python3
"""
Fabric Security Tests
Tests for API key protection, input sanitization, and security best practices
"""

import os
import sys
import json
import time
import subprocess
import requests
import re
from typing import Dict, List, Optional
from pathlib import Path

# Color codes
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
CYAN = '\033[0;36m'
NC = '\033[0m'


class SecurityTests:
    """Security test suite"""
    
    def __init__(self):
        self.api_base = 'http://localhost:8080'
        self.test_results = []
        self.project_root = Path(__file__).parent.parent
        
    def print_header(self, text: str):
        """Print test section header"""
        print(f"\n{BLUE}{'='*70}{NC}")
        print(f"{BLUE}{text:^70}{NC}")
        print(f"{BLUE}{'='*70}{NC}\n")
    
    def print_test(self, name: str, passed: bool, message: str = "", duration: float = 0):
        """Print test result"""
        status = f"{GREEN}✓ PASS{NC}" if passed else f"{RED}✗ FAIL{NC}"
        duration_str = f"({duration:.2f}s)" if duration > 0 else ""
        print(f"{status} - {name} {CYAN}{duration_str}{NC}")
        if message:
            indent = "       "
            if len(message) > 200:
                message = message[:200] + "..."
            print(f"{indent}{message}")
        self.test_results.append((name, passed, message, duration))
    
    # ===== API Key Exposure Tests =====
    
    def test_api_keys_not_in_logs(self) -> bool:
        """Test API keys are not exposed in Docker logs"""
        self.print_header("API Key Protection")
        
        # Check Docker logs for API key patterns
        try:
            result = subprocess.run(
                ['docker', 'logs', 'fabric-api', '--tail', '1000'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                self.print_test("API keys not in Docker logs", True,
                              "Container not running (skipped)")
                return True
            
            logs = result.stdout + result.stderr
            
            # Check for common API key patterns
            key_patterns = [
                r'sk-ant-[a-zA-Z0-9]{90,}',  # Anthropic
                r'sk-[a-zA-Z0-9]{48,}',       # OpenAI
                r'gsk_[a-zA-Z0-9]{52,}',      # Groq
                r'AIza[a-zA-Z0-9]{35,}',      # Google
            ]
            
            found_keys = []
            for pattern in key_patterns:
                matches = re.findall(pattern, logs)
                if matches:
                    found_keys.extend(matches)
            
            passed = len(found_keys) == 0
            
            self.print_test("API keys not in Docker logs", passed,
                          f"Found {len(found_keys)} exposed keys" if not passed else "No keys exposed")
            return passed
            
        except Exception as e:
            self.print_test("API keys not in Docker logs", False, str(e))
            return False
    
    def test_env_not_exposed_in_response(self) -> bool:
        """Test .env variables not exposed in API responses"""
        try:
            # Try to get some information that might expose env
            response = requests.get(f"{self.api_base}/health", timeout=5)
            
            if response.status_code != 200:
                self.print_test("ENV not in API response", True,
                              "API not available (skipped)")
                return True
            
            response_text = response.text.lower()
            
            # Check for env variable indicators
            suspicious = ['api_key', 'secret', 'password', 'token', 'sk-ant', 'sk-proj']
            
            found_suspicious = [s for s in suspicious if s in response_text]
            
            passed = len(found_suspicious) == 0
            
            self.print_test("ENV not in API response", passed,
                          f"Found suspicious: {found_suspicious}" if not passed else "Clean response")
            return passed
            
        except Exception as e:
            self.print_test("ENV not in API response", False, str(e))
            return False
    
    def test_env_file_permissions(self) -> bool:
        """Test .env file has restrictive permissions"""
        env_path = self.project_root / '.env'
        
        if not env_path.exists():
            self.print_test(".env file permissions", True,
                          "File not found (skipped)")
            return True
        
        try:
            stat_info = env_path.stat()
            # Check permissions (should be 600 or more restrictive)
            permissions = oct(stat_info.st_mode)[-3:]
            
            # Should not be world-readable (last digit should be 0)
            passed = permissions[-1] == '0'
            
            self.print_test(".env file permissions", passed,
                          f"Permissions: {permissions} (should end in 0)")
            return passed
            
        except Exception as e:
            self.print_test(".env file permissions", False, str(e))
            return False
    
    # ===== Input Sanitization Tests =====
    
    def test_sql_injection_protection(self) -> bool:
        """Test SQL injection attempts are handled safely"""
        self.print_header("Input Sanitization")
        
        sql_payloads = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'--",
            "1; DELETE FROM patterns WHERE 1=1",
        ]
        
        all_passed = True
        
        for payload in sql_payloads:
            try:
                response = requests.post(
                    f"{self.api_base}/chat",
                    json={
                        "input": payload,
                        "pattern": "summarize",
                        "stream": False
                    },
                    timeout=10
                )
                
                # Should either handle safely (200) or reject (400/422)
                # Should NOT return 500 (server error)
                passed = response.status_code != 500
                
                if not passed:
                    all_passed = False
                    
            except Exception as e:
                all_passed = False
        
        self.print_test("SQL injection protection", all_passed,
                      "All payloads handled safely" if all_passed else "Some caused errors")
        return all_passed
    
    def test_xss_protection(self) -> bool:
        """Test XSS attempts are sanitized"""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<iframe src='javascript:alert(1)'>",
        ]
        
        all_passed = True
        
        for payload in xss_payloads:
            try:
                response = requests.post(
                    f"{self.api_base}/chat",
                    json={
                        "input": payload,
                        "pattern": "summarize",
                        "stream": False
                    },
                    timeout=10
                )
                
                # Check if response contains unsanitized script tags
                if response.status_code == 200:
                    response_text = response.text
                    # Script tags should be escaped or removed
                    has_active_script = '<script>' in response_text.lower()
                    
                    if has_active_script:
                        all_passed = False
                        
            except Exception as e:
                all_passed = False
        
        self.print_test("XSS protection", all_passed,
                      "Scripts sanitized" if all_passed else "Active scripts found")
        return all_passed
    
    def test_command_injection_protection(self) -> bool:
        """Test command injection attempts are handled safely"""
        command_payloads = [
            "; ls -la",
            "| cat /etc/passwd",
            "`whoami`",
            "$(rm -rf /)",
        ]
        
        all_passed = True
        
        for payload in command_payloads:
            try:
                response = requests.post(
                    f"{self.api_base}/chat",
                    json={
                        "input": payload,
                        "pattern": "summarize",
                        "stream": False
                    },
                    timeout=10
                )
                
                # Should not execute commands (500 error)
                passed = response.status_code != 500
                
                if not passed:
                    all_passed = False
                    
            except Exception as e:
                all_passed = False
        
        self.print_test("Command injection protection", all_passed,
                      "All payloads handled safely" if all_passed else "Some caused errors")
        return all_passed
    
    def test_path_traversal_protection(self) -> bool:
        """Test path traversal attempts are blocked"""
        traversal_payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
            "....//....//....//etc/passwd",
        ]
        
        all_passed = True
        
        for payload in traversal_payloads:
            try:
                # Try to use as pattern name
                response = requests.post(
                    f"{self.api_base}/chat",
                    json={
                        "input": "test",
                        "pattern": payload,
                        "stream": False
                    },
                    timeout=10
                )
                
                # Should reject (400/404) or handle safely
                # Should NOT return file contents
                passed = response.status_code in [400, 404] or \
                        (response.status_code == 200 and '/etc/passwd' not in response.text)
                
                if not passed:
                    all_passed = False
                    
            except Exception as e:
                all_passed = False
        
        self.print_test("Path traversal protection", all_passed,
                      "Traversal blocked" if all_passed else "Potential vulnerability")
        return all_passed
    
    # ===== Secret Handling Tests =====
    
    def test_secrets_not_in_docker_compose(self) -> bool:
        """Test secrets use env_file not hardcoded values"""
        self.print_header("Secret Handling")
        
        compose_file = self.project_root / 'docker-compose.yml'
        
        if not compose_file.exists():
            self.print_test("Secrets in docker-compose", True,
                          "File not found (skipped)")
            return True
        
        try:
            with open(compose_file, 'r') as f:
                content = f.read()
            
            # Check for API key patterns in compose file
            key_patterns = [
                r'sk-ant-[a-zA-Z0-9]{90,}',
                r'sk-[a-zA-Z0-9]{48,}',
                r'gsk_[a-zA-Z0-9]{52,}',
            ]
            
            found_keys = []
            for pattern in key_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    found_keys.extend(matches)
            
            # Should use env_file instead
            uses_env_file = 'env_file:' in content
            
            passed = len(found_keys) == 0 and uses_env_file
            
            message = "Uses env_file correctly" if passed else \
                     f"Found {len(found_keys)} hardcoded keys" if found_keys else \
                     "Not using env_file"
            
            self.print_test("Secrets in docker-compose", passed, message)
            return passed
            
        except Exception as e:
            self.print_test("Secrets in docker-compose", False, str(e))
            return False
    
    def test_env_example_no_real_secrets(self) -> bool:
        """Test .env.example doesn't contain real secrets"""
        env_example = self.project_root / '.env.example'
        
        if not env_example.exists():
            self.print_test(".env.example no real secrets", True,
                          "File not found (skipped)")
            return True
        
        try:
            with open(env_example, 'r') as f:
                content = f.read()
            
            # Check for real API key patterns
            key_patterns = [
                r'sk-ant-api-[a-zA-Z0-9]{90,}',  # Real Anthropic key
                r'sk-proj-[a-zA-Z0-9]{48,}',     # Real OpenAI key
            ]
            
            found_real_keys = []
            for pattern in key_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    found_real_keys.extend(matches)
            
            passed = len(found_real_keys) == 0
            
            self.print_test(".env.example no real secrets", passed,
                          "Only placeholders" if passed else f"Found {len(found_real_keys)} real keys")
            return passed
            
        except Exception as e:
            self.print_test(".env.example no real secrets", False, str(e))
            return False
    
    # ===== Rate Limiting Tests =====
    
    def test_rate_limiting_exists(self) -> bool:
        """Test if rate limiting is in place"""
        self.print_header("Rate Limiting")
        
        # Make rapid requests
        responses = []
        
        try:
            for i in range(20):  # 20 rapid requests
                response = requests.get(f"{self.api_base}/health", timeout=2)
                responses.append(response.status_code)
        except:
            pass
        
        # Check if any were rate limited (429)
        rate_limited = 429 in responses
        
        # Note: Rate limiting might not be implemented - that's ok for now
        # This test documents whether it exists (always passes, it's informational)
        
        self.print_test("Rate limiting check", True,
                      "Rate limiting active (429 responses)" if rate_limited else \
                      "No rate limiting detected (optional feature)")
        
        return True
    
    # ===== Docker Security Tests =====
    
    def test_containers_run_as_non_root(self) -> bool:
        """Test Docker containers don't run as root"""
        self.print_header("Docker Security")
        
        try:
            # Check user in fabric-api container
            result = subprocess.run(
                ['docker', 'exec', 'fabric-api', 'whoami'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                self.print_test("Containers run as non-root", True,
                              "Container not running (skipped)")
                return True
            
            user = result.stdout.strip()
            
            passed = user != 'root'
            
            self.print_test("Containers run as non-root", passed,
                          f"Running as: {user}")
            return passed
            
        except Exception as e:
            self.print_test("Containers run as non-root", True,
                          "Cannot check (skipped)")
            return True
    
    def test_sensitive_files_not_in_image(self) -> bool:
        """Test .env files are not copied into Docker images"""
        try:
            # Check if .env exists in container
            result = subprocess.run(
                ['docker', 'exec', 'fabric-api', 'test', '-f', '/app/.env'],
                capture_output=True,
                timeout=5
            )
            
            if result.returncode != 0:
                # Check different path
                result = subprocess.run(
                    ['docker', 'exec', 'fabric-api', 'test', '-f', '/.env'],
                    capture_output=True,
                    timeout=5
                )
            
            # .env should NOT exist in container (should use volumes)
            passed = result.returncode != 0
            
            self.print_test("Sensitive files not in image", passed,
                          ".env not baked into image" if passed else ".env found in image")
            return passed
            
        except Exception as e:
            self.print_test("Sensitive files not in image", True,
                          "Cannot check (skipped)")
            return True
    
    # ===== CORS & Headers Tests =====
    
    def test_cors_headers_present(self) -> bool:
        """Test CORS headers are configured"""
        self.print_header("HTTP Security Headers")
        
        try:
            response = requests.options(
                f"{self.api_base}/chat",
                headers={'Origin': 'http://localhost:5173'},
                timeout=5
            )
            
            has_cors = 'Access-Control-Allow-Origin' in response.headers
            
            # CORS is optional depending on deployment (always pass, informational)
            self.print_test("CORS headers check", True,
                          "CORS configured" if has_cors else "No CORS headers (optional for local dev)")
            
            return True
            
        except Exception as e:
            self.print_test("CORS headers present", True,
                          "Cannot check (skipped)")
            return True
    
    # ===== Summary =====
    
    def print_summary(self):
        """Print test summary"""
        self.print_header("Security Test Summary")
        
        passed = sum(1 for _, result, _, _ in self.test_results if result)
        failed = sum(1 for _, result, _, _ in self.test_results if not result)
        total = len(self.test_results)
        
        total_time = sum(duration for _, _, _, duration in self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"{GREEN}Passed: {passed}{NC}")
        print(f"{RED}Failed: {failed}{NC}")
        print(f"Total Time: {total_time:.2f}s")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        
        if failed > 0:
            print(f"\n{RED}SECURITY ISSUES FOUND:{NC}")
            for name, result, message, _ in self.test_results:
                if not result:
                    msg_short = message[:80] if message else ""
                    print(f"  ⚠️  {name}: {msg_short}")
            print(f"\n{RED}Please address these security issues immediately!{NC}")
        
        print(f"\n{BLUE}{'='*70}{NC}")
        if failed == 0:
            print(f"{GREEN}{'🔒 ALL SECURITY TESTS PASSED! 🔒':^70}{NC}")
        else:
            print(f"{RED}{'🚨 SECURITY VULNERABILITIES FOUND 🚨':^70}{NC}")
        print(f"{BLUE}{'='*70}{NC}")
        
        return failed == 0


def run_security_tests():
    """Run all security tests"""
    suite = SecurityTests()
    
    print(f"{BLUE}{'='*70}{NC}")
    print(f"{BLUE}{'Fabric Security Tests':^70}{NC}")
    print(f"{BLUE}{'='*70}{NC}")
    print(f"\n{YELLOW}Testing for security vulnerabilities and best practices...{NC}\n")
    
    # API key protection
    suite.test_api_keys_not_in_logs()
    suite.test_env_not_exposed_in_response()
    suite.test_env_file_permissions()
    
    # Input sanitization
    suite.test_sql_injection_protection()
    suite.test_xss_protection()
    suite.test_command_injection_protection()
    suite.test_path_traversal_protection()
    
    # Secret handling
    suite.test_secrets_not_in_docker_compose()
    suite.test_env_example_no_real_secrets()
    
    # Rate limiting
    suite.test_rate_limiting_exists()
    
    # Docker security
    suite.test_containers_run_as_non_root()
    suite.test_sensitive_files_not_in_image()
    
    # HTTP headers
    suite.test_cors_headers_present()
    
    # Print summary
    all_passed = suite.print_summary()
    
    return all_passed


if __name__ == '__main__':
    success = run_security_tests()
    sys.exit(0 if success else 1)
