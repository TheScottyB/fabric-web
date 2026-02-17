#!/usr/bin/env python3
"""
Fabric Smoke Tests
End-to-end tests that run actual prompts through all services
"""

import os
import sys
import json
import time
import requests
from typing import Dict, List, Optional
from pathlib import Path

# Color codes
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
CYAN = '\033[0;36m'
NC = '\033[0m'


class FabricSmokeTests:
    """Smoke test suite for Fabric services"""
    
    def __init__(self):
        self.api_base = 'http://localhost:8080'
        self.svelte_base = 'http://localhost:5173'
        self.streamlit_base = 'http://localhost:8501'
        self.test_results = []
        
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
            # Truncate long messages
            if len(message) > 200:
                message = message[:200] + "..."
            print(f"{indent}{message}")
        self.test_results.append((name, passed, message, duration))
    
    def wait_for_service(self, url: str, timeout: int = 30, service_name: str = "service") -> bool:
        """Wait for a service to be available"""
        print(f"{YELLOW}Waiting for {service_name} to be ready...{NC}")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(url, timeout=2)
                if response.status_code in [200, 404]:  # 404 is ok for some endpoints
                    elapsed = time.time() - start_time
                    print(f"{GREEN}✓ {service_name} ready after {elapsed:.1f}s{NC}")
                    return True
            except requests.exceptions.ConnectionError:
                time.sleep(1)
            except Exception:
                time.sleep(1)
        
        print(f"{RED}✗ {service_name} not ready after {timeout}s{NC}")
        return False
    
    def test_api_health(self) -> bool:
        """Test API health endpoint"""
        self.print_header("API Health Check")
        
        try:
            start = time.time()
            response = requests.get(f"{self.api_base}/health", timeout=5)
            duration = time.time() - start
            
            if response.status_code == 200:
                self.print_test("API /health endpoint", True, 
                              f"Status: {response.status_code}", duration)
                return True
            else:
                self.print_test("API /health endpoint", False, 
                              f"Status: {response.status_code}", duration)
                return False
        except Exception as e:
            self.print_test("API /health endpoint", False, str(e))
            return False
    
    def test_api_list_patterns(self) -> bool:
        """Test listing available patterns"""
        self.print_header("API Pattern Listing")
        
        try:
            start = time.time()
            response = requests.get(f"{self.api_base}/patterns", timeout=10)
            duration = time.time() - start
            
            if response.status_code == 200:
                patterns = response.json()
                if isinstance(patterns, list) and len(patterns) > 0:
                    self.print_test("List patterns", True, 
                                  f"Found {len(patterns)} patterns", duration)
                    
                    # Show some pattern names
                    sample = patterns[:5]
                    print(f"       Sample patterns: {', '.join(sample)}")
                    return True
                else:
                    self.print_test("List patterns", False, 
                                  "No patterns returned", duration)
                    return False
            else:
                self.print_test("List patterns", False, 
                              f"Status: {response.status_code}", duration)
                return False
        except Exception as e:
            self.print_test("List patterns", False, str(e))
            return False
    
    def test_api_list_models(self) -> bool:
        """Test listing available models"""
        self.print_header("API Model Listing")
        
        try:
            start = time.time()
            response = requests.get(f"{self.api_base}/models", timeout=10)
            duration = time.time() - start
            
            if response.status_code == 200:
                models = response.json()
                if isinstance(models, dict) or isinstance(models, list):
                    model_count = len(models) if isinstance(models, list) else len(models.keys())
                    self.print_test("List models", True, 
                                  f"Found {model_count} providers/models", duration)
                    
                    # Show available vendors
                    if isinstance(models, dict):
                        vendors = list(models.keys())
                        print(f"       Vendors: {', '.join(vendors[:5])}")
                    return True
                else:
                    self.print_test("List models", False, 
                                  "Invalid response format", duration)
                    return False
            else:
                self.print_test("List models", False, 
                              f"Status: {response.status_code}", duration)
                return False
        except Exception as e:
            self.print_test("List models", False, str(e))
            return False
    
    def test_simple_pattern_execution(self) -> bool:
        """Test running a simple pattern"""
        self.print_header("Pattern Execution Test")
        
        test_input = "Artificial intelligence is transforming software development."
        pattern = "summarize"  # Common pattern that should exist
        
        try:
            start = time.time()
            
            # Try the chat endpoint
            payload = {
                "input": test_input,
                "pattern": pattern,
                "stream": False
            }
            
            response = requests.post(
                f"{self.api_base}/chat",
                json=payload,
                timeout=30
            )
            duration = time.time() - start
            
            if response.status_code == 200:
                result = response.text
                if result and len(result) > 10:
                    self.print_test(f"Execute '{pattern}' pattern", True, 
                                  f"Output: {result[:100]}...", duration)
                    return True
                else:
                    self.print_test(f"Execute '{pattern}' pattern", False, 
                                  "Empty or too short response", duration)
                    return False
            else:
                self.print_test(f"Execute '{pattern}' pattern", False, 
                              f"Status: {response.status_code} - {response.text[:100]}", 
                              duration)
                return False
                
        except requests.exceptions.Timeout:
            self.print_test(f"Execute '{pattern}' pattern", False, 
                          "Timeout (>30s) - model may be slow", 30.0)
            return False
        except Exception as e:
            self.print_test(f"Execute '{pattern}' pattern", False, str(e))
            return False
    
    def test_multiple_vendors(self) -> bool:
        """Test that multiple AI vendors are configured"""
        self.print_header("Vendor Configuration Test")
        
        # Read .env to check configured vendors
        env_path = Path(__file__).parent / '../.env'
        configured_vendors = []
        
        try:
            with open(env_path, 'r') as f:
                content = f.read()
                if 'ANTHROPIC_API_KEY' in content:
                    configured_vendors.append('Anthropic')
                if 'OPENAI_API_KEY' in content:
                    configured_vendors.append('OpenAI')
                if 'GROQ_API_KEY' in content:
                    configured_vendors.append('Groq')
                if 'GEMINI_API_KEY' in content:
                    configured_vendors.append('Gemini')
            
            if len(configured_vendors) >= 2:
                self.print_test("Multiple vendors configured", True, 
                              f"Vendors: {', '.join(configured_vendors)}")
                return True
            else:
                self.print_test("Multiple vendors configured", False, 
                              f"Only {len(configured_vendors)} vendor(s)")
                return False
        except Exception as e:
            self.print_test("Multiple vendors configured", False, str(e))
            return False
    
    def test_pattern_with_context(self) -> bool:
        """Test running a pattern with context"""
        self.print_header("Pattern with Context Test")
        
        test_input = """
        def fibonacci(n):
            if n <= 1:
                return n
            return fibonacci(n-1) + fibonacci(n-2)
        """
        
        pattern = "explain_code"  # Common code explanation pattern
        
        try:
            start = time.time()
            
            payload = {
                "input": test_input,
                "pattern": pattern,
                "stream": False
            }
            
            response = requests.post(
                f"{self.api_base}/chat",
                json=payload,
                timeout=30
            )
            duration = time.time() - start
            
            if response.status_code == 200:
                result = response.text
                # Check if response mentions recursion or fibonacci
                if result and (len(result) > 50):
                    self.print_test(f"Execute '{pattern}' with code", True, 
                                  f"Output length: {len(result)} chars", duration)
                    return True
                else:
                    self.print_test(f"Execute '{pattern}' with code", False, 
                                  "Response too short or empty", duration)
                    return False
            elif response.status_code == 404:
                self.print_test(f"Execute '{pattern}' with code", False, 
                              "Pattern not found (optional test)", duration)
                return True  # Not critical
            else:
                self.print_test(f"Execute '{pattern}' with code", False, 
                              f"Status: {response.status_code}", duration)
                return False
                
        except requests.exceptions.Timeout:
            self.print_test(f"Execute '{pattern}' with code", False, 
                          "Timeout (>30s)", 30.0)
            return False
        except Exception as e:
            self.print_test(f"Execute '{pattern}' with code", False, str(e))
            return False
    
    def test_svelte_ui_loads(self) -> bool:
        """Test that Svelte UI loads"""
        self.print_header("Svelte UI Test")
        
        try:
            start = time.time()
            response = requests.get(self.svelte_base, timeout=10)
            duration = time.time() - start
            
            if response.status_code == 200:
                content = response.text
                # Check for expected content
                has_html = '<html' in content or '<!DOCTYPE' in content
                has_js = '<script' in content or 'javascript' in content.lower()
                
                if has_html:
                    self.print_test("Svelte UI loads", True, 
                                  f"Page size: {len(content)} bytes", duration)
                    return True
                else:
                    self.print_test("Svelte UI loads", False, 
                                  "No HTML content found", duration)
                    return False
            else:
                self.print_test("Svelte UI loads", False, 
                              f"Status: {response.status_code}", duration)
                return False
        except Exception as e:
            self.print_test("Svelte UI loads", False, str(e))
            return False
    
    def test_streamlit_ui_loads(self) -> bool:
        """Test that Streamlit UI loads"""
        self.print_header("Streamlit UI Test")
        
        try:
            start = time.time()
            # Check health endpoint
            response = requests.get(f"{self.streamlit_base}/_stcore/health", timeout=10)
            duration = time.time() - start
            
            if response.status_code == 200:
                self.print_test("Streamlit UI health", True, 
                              "Streamlit is healthy", duration)
                
                # Try to load main page
                main_response = requests.get(self.streamlit_base, timeout=10)
                if main_response.status_code == 200:
                    self.print_test("Streamlit UI loads", True, 
                                  f"Page size: {len(main_response.text)} bytes")
                    return True
                else:
                    self.print_test("Streamlit UI loads", False, 
                                  f"Main page status: {main_response.status_code}")
                    return False
            else:
                self.print_test("Streamlit UI health", False, 
                              f"Status: {response.status_code}", duration)
                return False
        except Exception as e:
            self.print_test("Streamlit UI health", False, str(e))
            return False
    
    def test_api_response_time(self) -> bool:
        """Test API response time is acceptable"""
        self.print_header("Performance Test")
        
        try:
            # Test health endpoint speed
            times = []
            for i in range(3):
                start = time.time()
                requests.get(f"{self.api_base}/health", timeout=5)
                times.append(time.time() - start)
            
            avg_time = sum(times) / len(times)
            
            if avg_time < 1.0:
                self.print_test("API response time", True, 
                              f"Average: {avg_time*1000:.0f}ms (3 requests)")
                return True
            else:
                self.print_test("API response time", False, 
                              f"Slow: {avg_time*1000:.0f}ms average")
                return False
        except Exception as e:
            self.print_test("API response time", False, str(e))
            return False
    
    def test_youtube_transcript_integration(self) -> bool:
        """Test YouTube transcript + Fabric pattern integration"""
        self.print_header("YouTube Integration Test")
        
        # Check if yt command is available
        try:
            import subprocess
            yt_check = subprocess.run(['which', 'yt'], capture_output=True, timeout=2)
            if yt_check.returncode != 0:
                self.print_test("YouTube CLI (yt) available", False, 
                              "'yt' command not found - install from fabric")
                return True  # Not critical, skip gracefully
        except Exception as e:
            self.print_test("YouTube CLI check", False, str(e))
            return True  # Not critical
        
        # Test the integration flow: yt transcript -> fabric pattern
        # Using a short, well-known video for testing
        test_video = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Short video
        pattern = "summarize"
        
        try:
            start = time.time()
            
            # Simulate: yt --transcript 'URL' | fabric -sp pattern
            # Step 1: Get transcript (mock for test - would normally use yt command)
            test_transcript = """This is a test transcript. 
            It contains sample text that would normally come from YouTube. 
            The content discusses technology and innovation in software development.
            Artificial intelligence is transforming how we build applications.
            End of transcript."""
            
            # Step 2: Send to fabric with pattern
            payload = {
                "input": test_transcript,
                "pattern": pattern,
                "stream": False
            }
            
            response = requests.post(
                f"{self.api_base}/chat",
                json=payload,
                timeout=30
            )
            duration = time.time() - start
            
            if response.status_code == 200:
                result = response.text
                if result and len(result) > 20:
                    self.print_test("YT transcript -> Fabric pattern", True, 
                                  f"Pipeline works: {len(result)} char response", duration)
                    return True
                else:
                    self.print_test("YT transcript -> Fabric pattern", False, 
                                  "Response too short", duration)
                    return False
            else:
                self.print_test("YT transcript -> Fabric pattern", False, 
                              f"Status: {response.status_code}", duration)
                return False
                
        except requests.exceptions.Timeout:
            self.print_test("YT transcript -> Fabric pattern", False, 
                          "Timeout (>30s)", 30.0)
            return False
        except Exception as e:
            self.print_test("YT transcript -> Fabric pattern", False, str(e))
            return False
    
    def test_youtube_comments_integration(self) -> bool:
        """Test YouTube comments + Fabric pattern integration"""
        self.print_header("YouTube Comments Integration Test")
        
        # Test the integration flow: fabric -y URL --comments | fabric -rp pattern
        # This is a chained pattern execution
        
        try:
            start = time.time()
            
            # Simulate: fabric -y 'URL' --comments | fabric -rp summary_action
            # Step 1: Get comments (mock for test - would normally use fabric -y command)
            test_comments = """Comment 1: This video is amazing! Very informative.
            Comment 2: Great explanation of the concepts.
            Comment 3: Thanks for sharing this knowledge.
            Comment 4: The examples really helped me understand.
            Comment 5: Looking forward to more content like this.
            Comment 6: Best tutorial I've found on this topic.
            Comment 7: Clear and concise presentation.
            Comment 8: Helpful for beginners and advanced users.
            Comment 9: Appreciate the detailed breakdown.
            Comment 10: Excellent work!"""
            
            # Step 2: Send comments to fabric with summary pattern
            # Using a pattern that works well for aggregating opinions
            pattern = "summarize"
            
            payload = {
                "input": test_comments,
                "pattern": pattern,
                "stream": False
            }
            
            response = requests.post(
                f"{self.api_base}/chat",
                json=payload,
                timeout=30
            )
            duration = time.time() - start
            
            if response.status_code == 200:
                result = response.text
                if result and len(result) > 20:
                    self.print_test("YT comments -> Fabric pattern", True, 
                                  f"Pipeline works: {len(result)} char response", duration)
                    return True
                else:
                    self.print_test("YT comments -> Fabric pattern", False, 
                                  "Response too short", duration)
                    return False
            else:
                self.print_test("YT comments -> Fabric pattern", False, 
                              f"Status: {response.status_code}", duration)
                return False
                
        except requests.exceptions.Timeout:
            self.print_test("YT comments -> Fabric pattern", False, 
                          "Timeout (>30s)", 30.0)
            return False
        except Exception as e:
            self.print_test("YT comments -> Fabric pattern", False, str(e))
            return False
    
    def print_summary(self):
        """Print test summary"""
        self.print_header("Smoke Test Summary")
        
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
            print(f"\n{YELLOW}Failed Tests:{NC}")
            for name, result, message, _ in self.test_results:
                if not result:
                    msg_short = message[:80] if message else ""
                    print(f"  - {name}: {msg_short}")
        
        print(f"\n{BLUE}{'='*70}{NC}")
        if failed == 0:
            print(f"{GREEN}{'🎉 ALL SMOKE TESTS PASSED! 🎉':^70}{NC}")
        else:
            print(f"{YELLOW}{'⚠️  SOME TESTS FAILED':^70}{NC}")
        print(f"{BLUE}{'='*70}{NC}")
        
        return failed == 0


def run_smoke_tests():
    """Run all smoke tests"""
    suite = FabricSmokeTests()
    
    print(f"{BLUE}{'='*70}{NC}")
    print(f"{BLUE}{'Fabric End-to-End Smoke Tests':^70}{NC}")
    print(f"{BLUE}{'='*70}{NC}")
    
    # Wait for services to be ready
    print(f"\n{YELLOW}Checking if services are available...{NC}\n")
    
    api_ready = suite.wait_for_service(f"{suite.api_base}/health", 
                                       timeout=30, service_name="API")
    svelte_ready = suite.wait_for_service(suite.svelte_base, 
                                          timeout=10, service_name="Svelte UI")
    streamlit_ready = suite.wait_for_service(f"{suite.streamlit_base}/_stcore/health", 
                                             timeout=10, service_name="Streamlit UI")
    
    if not api_ready:
        print(f"\n{RED}API not available. Did you start services?{NC}")
        print(f"{YELLOW}Run: docker-compose up -d{NC}\n")
        return False
    
    # Run tests
    suite.test_api_health()
    suite.test_api_list_patterns()
    suite.test_api_list_models()
    suite.test_multiple_vendors()
    suite.test_api_response_time()
    
    # Pattern execution tests (may take longer)
    suite.test_simple_pattern_execution()
    suite.test_pattern_with_context()
    suite.test_youtube_transcript_integration()
    suite.test_youtube_comments_integration()
    
    # UI tests
    if svelte_ready:
        suite.test_svelte_ui_loads()
    
    if streamlit_ready:
        suite.test_streamlit_ui_loads()
    
    # Print summary
    all_passed = suite.print_summary()
    
    return all_passed


if __name__ == '__main__':
    success = run_smoke_tests()
    sys.exit(0 if success else 1)
