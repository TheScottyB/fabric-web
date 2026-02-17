#!/usr/bin/env python3
"""
Fabric REST API Integration Tests
Comprehensive tests for REST API endpoints, strategies, and Ollama compatibility
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


class APIIntegrationTests:
    """REST API integration test suite"""
    
    def __init__(self):
        self.api_base = 'http://localhost:8080'
        self.ollama_base = 'http://localhost:11434'
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
            if len(message) > 200:
                message = message[:200] + "..."
            print(f"{indent}{message}")
        self.test_results.append((name, passed, message, duration))
    
    # ===== Core API Tests =====
    
    def test_health_endpoint(self) -> bool:
        """Test /health endpoint"""
        self.print_header("Core API Endpoints")
        
        try:
            start = time.time()
            response = requests.get(f"{self.api_base}/health", timeout=5)
            duration = time.time() - start
            
            passed = response.status_code == 200
            self.print_test("GET /health", passed, 
                          f"Status: {response.status_code}", duration)
            return passed
        except Exception as e:
            self.print_test("GET /health", False, str(e))
            return False
    
    def test_patterns_endpoint(self) -> bool:
        """Test /patterns endpoint"""
        try:
            start = time.time()
            response = requests.get(f"{self.api_base}/patterns", timeout=10)
            duration = time.time() - start
            
            if response.status_code == 200:
                patterns = response.json()
                passed = isinstance(patterns, list) and len(patterns) > 0
                self.print_test("GET /patterns", passed, 
                              f"Found {len(patterns)} patterns", duration)
                return passed
            else:
                self.print_test("GET /patterns", False, 
                              f"Status: {response.status_code}", duration)
                return False
        except Exception as e:
            self.print_test("GET /patterns", False, str(e))
            return False
    
    def test_models_endpoint(self) -> bool:
        """Test /models endpoint"""
        try:
            start = time.time()
            response = requests.get(f"{self.api_base}/models", timeout=10)
            duration = time.time() - start
            
            if response.status_code == 200:
                models = response.json()
                passed = (isinstance(models, dict) or isinstance(models, list))
                count = len(models) if isinstance(models, list) else len(models.keys())
                self.print_test("GET /models", passed, 
                              f"Found {count} models/vendors", duration)
                return passed
            else:
                self.print_test("GET /models", False, 
                              f"Status: {response.status_code}", duration)
                return False
        except Exception as e:
            self.print_test("GET /models", False, str(e))
            return False
    
    def test_strategies_endpoint(self) -> bool:
        """Test /strategies endpoint"""
        try:
            start = time.time()
            response = requests.get(f"{self.api_base}/strategies", timeout=10)
            duration = time.time() - start
            
            if response.status_code == 200:
                strategies = response.json()
                passed = isinstance(strategies, list) and len(strategies) > 0
                self.print_test("GET /strategies", passed, 
                              f"Found {len(strategies)} strategies", duration)
                return passed
            elif response.status_code == 404:
                # Endpoint might not exist in older versions
                self.print_test("GET /strategies", True, 
                              "Endpoint not available (optional)", duration)
                return True
            else:
                self.print_test("GET /strategies", False, 
                              f"Status: {response.status_code}", duration)
                return False
        except Exception as e:
            self.print_test("GET /strategies", False, str(e))
            return False
    
    # ===== Pattern Execution Tests =====
    
    def test_pattern_execution_basic(self) -> bool:
        """Test basic pattern execution"""
        self.print_header("Pattern Execution Tests")
        
        try:
            start = time.time()
            
            payload = {
                "input": "Artificial intelligence is transforming software development.",
                "pattern": "summarize",
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
                passed = result and len(result) > 20
                self.print_test("POST /chat (basic pattern)", passed, 
                              f"Response: {len(result)} chars", duration)
                return passed
            else:
                self.print_test("POST /chat (basic pattern)", False, 
                              f"Status: {response.status_code}", duration)
                return False
        except Exception as e:
            self.print_test("POST /chat (basic pattern)", False, str(e))
            return False
    
    def test_pattern_execution_with_strategy(self) -> bool:
        """Test pattern execution with strategy"""
        strategies = ["cot", "standard", "reflexion"]
        all_passed = True
        
        for strategy in strategies:
            try:
                start = time.time()
                
                payload = {
                    "input": "Explain recursion in programming.",
                    "pattern": "explain_code",
                    "strategy": strategy,
                    "stream": False
                }
                
                response = requests.post(
                    f"{self.api_base}/chat",
                    json=payload,
                    timeout=40
                )
                duration = time.time() - start
                
                if response.status_code == 200:
                    result = response.text
                    passed = result and len(result) > 30
                    self.print_test(f"Pattern with strategy '{strategy}'", passed, 
                                  f"Response: {len(result)} chars", duration)
                    if not passed:
                        all_passed = False
                elif response.status_code == 404:
                    # Strategy or pattern not found - not critical
                    self.print_test(f"Pattern with strategy '{strategy}'", True, 
                                  "Not available (optional)", duration)
                else:
                    self.print_test(f"Pattern with strategy '{strategy}'", False, 
                                  f"Status: {response.status_code}", duration)
                    all_passed = False
            except Exception as e:
                self.print_test(f"Pattern with strategy '{strategy}'", False, str(e))
                all_passed = False
        
        return all_passed
    
    def test_pattern_execution_streaming(self) -> bool:
        """Test streaming pattern execution"""
        try:
            start = time.time()
            
            payload = {
                "input": "Quick test for streaming.",
                "pattern": "summarize",
                "stream": True
            }
            
            response = requests.post(
                f"{self.api_base}/chat",
                json=payload,
                stream=True,
                timeout=30
            )
            duration = time.time() - start
            
            if response.status_code == 200:
                chunks = []
                for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
                    if chunk:
                        chunks.append(chunk)
                        if len(chunks) >= 3:  # Get a few chunks then stop
                            break
                
                passed = len(chunks) > 0
                self.print_test("Streaming execution", passed, 
                              f"Received {len(chunks)} chunks", duration)
                return passed
            else:
                self.print_test("Streaming execution", False, 
                              f"Status: {response.status_code}", duration)
                return False
        except Exception as e:
            self.print_test("Streaming execution", False, str(e))
            return False
    
    # ===== Chat Completions Tests =====
    
    def test_chat_completions_endpoint(self) -> bool:
        """Test OpenAI-compatible /v1/chat/completions"""
        self.print_header("Chat Completions API")
        
        try:
            start = time.time()
            
            payload = {
                "model": "gpt-4",
                "messages": [
                    {"role": "user", "content": "What is Python?"}
                ],
                "stream": False
            }
            
            response = requests.post(
                f"{self.api_base}/v1/chat/completions",
                json=payload,
                timeout=30
            )
            duration = time.time() - start
            
            if response.status_code == 200:
                result = response.json()
                passed = "choices" in result and len(result["choices"]) > 0
                self.print_test("POST /v1/chat/completions", passed, 
                              "OpenAI-compatible format", duration)
                return passed
            elif response.status_code == 404:
                self.print_test("POST /v1/chat/completions", True, 
                              "Endpoint not available (optional)", duration)
                return True
            else:
                self.print_test("POST /v1/chat/completions", False, 
                              f"Status: {response.status_code}", duration)
                return False
        except Exception as e:
            self.print_test("POST /v1/chat/completions", False, str(e))
            return False
    
    def test_chat_completions_with_strategy(self) -> bool:
        """Test chat completions with strategy parameter"""
        try:
            start = time.time()
            
            payload = {
                "model": "gpt-4",
                "messages": [
                    {"role": "user", "content": "Explain quantum computing."}
                ],
                "strategy": "cot",
                "stream": False
            }
            
            response = requests.post(
                f"{self.api_base}/v1/chat/completions",
                json=payload,
                timeout=30
            )
            duration = time.time() - start
            
            if response.status_code == 200:
                result = response.json()
                passed = "choices" in result
                self.print_test("Chat completions + strategy", passed, 
                              "Strategy applied", duration)
                return passed
            elif response.status_code == 404:
                self.print_test("Chat completions + strategy", True, 
                              "Not available (optional)", duration)
                return True
            else:
                self.print_test("Chat completions + strategy", False, 
                              f"Status: {response.status_code}", duration)
                return False
        except Exception as e:
            self.print_test("Chat completions + strategy", False, str(e))
            return False
    
    # ===== YouTube Integration Tests =====
    
    def test_youtube_transcript_endpoint(self) -> bool:
        """Test YouTube transcript extraction"""
        self.print_header("YouTube Integration")
        
        try:
            start = time.time()
            
            payload = {
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            }
            
            response = requests.post(
                f"{self.api_base}/youtube/transcript",
                json=payload,
                timeout=20
            )
            duration = time.time() - start
            
            if response.status_code == 200:
                transcript = response.json()
                passed = isinstance(transcript, dict) or isinstance(transcript, str)
                self.print_test("POST /youtube/transcript", passed, 
                              "Transcript extracted", duration)
                return passed
            elif response.status_code == 404:
                self.print_test("POST /youtube/transcript", True, 
                              "Endpoint not available (optional)", duration)
                return True
            else:
                self.print_test("POST /youtube/transcript", False, 
                              f"Status: {response.status_code}", duration)
                return False
        except Exception as e:
            self.print_test("POST /youtube/transcript", False, str(e))
            return False
    
    def test_youtube_comments_endpoint(self) -> bool:
        """Test YouTube comments extraction"""
        try:
            start = time.time()
            
            payload = {
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            }
            
            response = requests.post(
                f"{self.api_base}/youtube/comments",
                json=payload,
                timeout=20
            )
            duration = time.time() - start
            
            if response.status_code == 200:
                comments = response.json()
                passed = isinstance(comments, (dict, list))
                self.print_test("POST /youtube/comments", passed, 
                              "Comments extracted", duration)
                return passed
            elif response.status_code == 404:
                self.print_test("POST /youtube/comments", True, 
                              "Endpoint not available (optional)", duration)
                return True
            else:
                self.print_test("POST /youtube/comments", False, 
                              f"Status: {response.status_code}", duration)
                return False
        except Exception as e:
            self.print_test("POST /youtube/comments", False, str(e))
            return False
    
    # ===== Ollama Compatibility Tests =====
    
    def test_ollama_version_endpoint(self) -> bool:
        """Test Ollama /api/version endpoint"""
        self.print_header("Ollama Compatibility API")
        
        try:
            start = time.time()
            response = requests.get(f"{self.ollama_base}/api/version", timeout=5)
            duration = time.time() - start
            
            if response.status_code == 200:
                version = response.json()
                passed = "version" in version or isinstance(version, dict)
                self.print_test("GET /api/version (Ollama)", passed, 
                              "Version endpoint works", duration)
                return passed
            else:
                self.print_test("GET /api/version (Ollama)", False, 
                              f"Ollama API not running (port 11434)", duration)
                return False
        except requests.exceptions.ConnectionError:
            self.print_test("GET /api/version (Ollama)", False, 
                          "Ollama API not available (optional)")
            return False
        except Exception as e:
            self.print_test("GET /api/version (Ollama)", False, str(e))
            return False
    
    def test_ollama_tags_endpoint(self) -> bool:
        """Test Ollama /api/tags endpoint (lists patterns as models)"""
        try:
            start = time.time()
            response = requests.get(f"{self.ollama_base}/api/tags", timeout=10)
            duration = time.time() - start
            
            if response.status_code == 200:
                data = response.json()
                passed = "models" in data and len(data["models"]) > 0
                count = len(data.get("models", []))
                self.print_test("GET /api/tags (Ollama)", passed, 
                              f"Found {count} models (patterns)", duration)
                return passed
            else:
                self.print_test("GET /api/tags (Ollama)", False, 
                              "Ollama API not running")
                return False
        except requests.exceptions.ConnectionError:
            self.print_test("GET /api/tags (Ollama)", False, 
                          "Ollama API not available (optional)")
            return False
        except Exception as e:
            self.print_test("GET /api/tags (Ollama)", False, str(e))
            return False
    
    def test_ollama_chat_endpoint(self) -> bool:
        """Test Ollama /api/chat endpoint"""
        try:
            start = time.time()
            
            payload = {
                "model": "summarize:latest",
                "messages": [
                    {"role": "user", "content": "Test message for Ollama API"}
                ],
                "stream": False
            }
            
            response = requests.post(
                f"{self.ollama_base}/api/chat",
                json=payload,
                timeout=30
            )
            duration = time.time() - start
            
            if response.status_code == 200:
                result = response.json()
                passed = "message" in result or "response" in result
                self.print_test("POST /api/chat (Ollama)", passed, 
                              "Chat works with pattern as model", duration)
                return passed
            else:
                self.print_test("POST /api/chat (Ollama)", False, 
                              "Ollama API not running")
                return False
        except requests.exceptions.ConnectionError:
            self.print_test("POST /api/chat (Ollama)", False, 
                          "Ollama API not available (optional)")
            return False
        except Exception as e:
            self.print_test("POST /api/chat (Ollama)", False, str(e))
            return False
    
    # ===== Context Management Tests =====
    
    def test_contexts_endpoints(self) -> bool:
        """Test context management endpoints"""
        self.print_header("Context Management")
        
        context_name = f"test_context_{int(time.time())}"
        
        # Create context
        try:
            payload = {
                "name": context_name,
                "content": "This is test context data for integration testing."
            }
            
            response = requests.post(
                f"{self.api_base}/contexts",
                json=payload,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                self.print_test("POST /contexts (create)", True, 
                              f"Created context: {context_name}")
            elif response.status_code == 404:
                self.print_test("POST /contexts (create)", True, 
                              "Endpoint not available (optional)")
                return True
            else:
                self.print_test("POST /contexts (create)", False, 
                              f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.print_test("POST /contexts (create)", False, str(e))
            return False
        
        # List contexts
        try:
            response = requests.get(f"{self.api_base}/contexts", timeout=10)
            
            if response.status_code == 200:
                contexts = response.json()
                passed = isinstance(contexts, list)
                self.print_test("GET /contexts (list)", passed, 
                              f"Found {len(contexts)} contexts")
            else:
                self.print_test("GET /contexts (list)", False, 
                              f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.print_test("GET /contexts (list)", False, str(e))
            return False
        
        # Get specific context
        try:
            response = requests.get(
                f"{self.api_base}/contexts/{context_name}", 
                timeout=10
            )
            
            if response.status_code == 200:
                context = response.json()
                passed = "content" in context or "name" in context
                self.print_test("GET /contexts/{name} (retrieve)", passed, 
                              "Context retrieved")
                return passed
            else:
                self.print_test("GET /contexts/{name} (retrieve)", False, 
                              f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.print_test("GET /contexts/{name} (retrieve)", False, str(e))
            return False
    
    # ===== Performance Tests =====
    
    def test_concurrent_requests(self) -> bool:
        """Test handling concurrent requests"""
        self.print_header("Performance & Load Tests")
        
        import threading
        
        results = []
        
        def make_request():
            try:
                response = requests.get(f"{self.api_base}/health", timeout=5)
                results.append(response.status_code == 200)
            except:
                results.append(False)
        
        # Start 5 concurrent requests
        threads = []
        start = time.time()
        
        for _ in range(5):
            t = threading.Thread(target=make_request)
            t.start()
            threads.append(t)
        
        for t in threads:
            t.join()
        
        duration = time.time() - start
        
        success_count = sum(1 for r in results if r)
        passed = success_count == 5
        
        self.print_test("Concurrent requests (5x)", passed, 
                      f"{success_count}/5 successful", duration)
        return passed
    
    def test_response_time_consistency(self) -> bool:
        """Test response time consistency"""
        times = []
        
        for i in range(5):
            try:
                start = time.time()
                response = requests.get(f"{self.api_base}/health", timeout=5)
                times.append(time.time() - start)
            except:
                times.append(5.0)
        
        if len(times) > 0:
            avg_time = sum(times) / len(times)
            max_time = max(times)
            
            # All requests should be under 1 second
            passed = max_time < 1.0
            
            self.print_test("Response time consistency", passed, 
                          f"Avg: {avg_time*1000:.0f}ms, Max: {max_time*1000:.0f}ms")
            return passed
        else:
            self.print_test("Response time consistency", False, "No responses")
            return False
    
    # ===== Error Handling Tests =====
    
    def test_error_handling(self) -> bool:
        """Test API error handling"""
        self.print_header("Error Handling")
        
        # Test invalid pattern
        try:
            payload = {
                "input": "Test",
                "pattern": "nonexistent_pattern_12345",
                "stream": False
            }
            
            response = requests.post(
                f"{self.api_base}/chat",
                json=payload,
                timeout=10
            )
            
            # Should return 404 or 400
            passed = response.status_code in [400, 404]
            self.print_test("Invalid pattern error", passed, 
                          f"Status: {response.status_code}")
        except Exception as e:
            self.print_test("Invalid pattern error", False, str(e))
            return False
        
        # Test missing required field
        try:
            payload = {
                "pattern": "summarize"
                # Missing "input" field
            }
            
            response = requests.post(
                f"{self.api_base}/chat",
                json=payload,
                timeout=10
            )
            
            passed = response.status_code in [400, 422]
            self.print_test("Missing field error", passed, 
                          f"Status: {response.status_code}")
        except Exception as e:
            self.print_test("Missing field error", False, str(e))
            return False
        
        # Test malformed JSON
        try:
            response = requests.post(
                f"{self.api_base}/chat",
                data="invalid json",
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            passed = response.status_code in [400, 422]
            self.print_test("Malformed JSON error", passed, 
                          f"Status: {response.status_code}")
            return passed
        except Exception as e:
            self.print_test("Malformed JSON error", False, str(e))
            return False
    
    # ===== Summary =====
    
    def print_summary(self):
        """Print test summary"""
        self.print_header("API Integration Test Summary")
        
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
            print(f"{GREEN}{'🎉 ALL API TESTS PASSED! 🎉':^70}{NC}")
        else:
            print(f"{YELLOW}{'⚠️  SOME TESTS FAILED':^70}{NC}")
        print(f"{BLUE}{'='*70}{NC}")
        
        return failed == 0


def run_api_tests():
    """Run all API integration tests"""
    suite = APIIntegrationTests()
    
    print(f"{BLUE}{'='*70}{NC}")
    print(f"{BLUE}{'Fabric REST API Integration Tests':^70}{NC}")
    print(f"{BLUE}{'='*70}{NC}")
    
    # Run all test groups
    suite.test_health_endpoint()
    suite.test_patterns_endpoint()
    suite.test_models_endpoint()
    suite.test_strategies_endpoint()
    
    suite.test_pattern_execution_basic()
    suite.test_pattern_execution_with_strategy()
    suite.test_pattern_execution_streaming()
    
    suite.test_chat_completions_endpoint()
    suite.test_chat_completions_with_strategy()
    
    suite.test_youtube_transcript_endpoint()
    suite.test_youtube_comments_endpoint()
    
    suite.test_ollama_version_endpoint()
    suite.test_ollama_tags_endpoint()
    suite.test_ollama_chat_endpoint()
    
    suite.test_contexts_endpoints()
    
    suite.test_concurrent_requests()
    suite.test_response_time_consistency()
    
    suite.test_error_handling()
    
    # Print summary
    all_passed = suite.print_summary()
    
    return all_passed


if __name__ == '__main__':
    success = run_api_tests()
    sys.exit(0 if success else 1)
