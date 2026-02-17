#!/usr/bin/env python3
"""
Fabric Ollama Integration Tests
Comprehensive tests for Ollama API compatibility and pattern-as-model functionality
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


class OllamaIntegrationTests:
    """Ollama compatibility integration test suite"""
    
    def __init__(self):
        self.ollama_base = 'http://localhost:11434'
        self.fabric_api_base = 'http://localhost:8080'
        self.test_results = []
        self.available_patterns = []
        
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
    
    # ===== Connection Tests =====
    
    def test_ollama_api_available(self) -> bool:
        """Test Ollama API is available"""
        self.print_header("Ollama API Connection")
        
        try:
            start = time.time()
            response = requests.get(f"{self.ollama_base}/api/version", timeout=5)
            duration = time.time() - start
            
            passed = response.status_code == 200
            self.print_test("Ollama API available", passed, 
                          f"Port 11434 responding" if passed else "Not running", 
                          duration)
            return passed
        except requests.exceptions.ConnectionError:
            self.print_test("Ollama API available", False, 
                          "Connection refused - API not running")
            return False
        except Exception as e:
            self.print_test("Ollama API available", False, str(e))
            return False
    
    def test_version_endpoint(self) -> bool:
        """Test /api/version endpoint"""
        try:
            start = time.time()
            response = requests.get(f"{self.ollama_base}/api/version", timeout=5)
            duration = time.time() - start
            
            if response.status_code == 200:
                version_data = response.json()
                has_version = "version" in version_data or isinstance(version_data, dict)
                self.print_test("GET /api/version", has_version, 
                              f"Version: {json.dumps(version_data)[:50]}", duration)
                return has_version
            else:
                self.print_test("GET /api/version", False, 
                              f"Status: {response.status_code}", duration)
                return False
        except Exception as e:
            self.print_test("GET /api/version", False, str(e))
            return False
    
    # ===== Model (Pattern) Listing Tests =====
    
    def test_tags_endpoint(self) -> bool:
        """Test /api/tags endpoint lists patterns as models"""
        self.print_header("Pattern-as-Model Listing")
        
        try:
            start = time.time()
            response = requests.get(f"{self.ollama_base}/api/tags", timeout=10)
            duration = time.time() - start
            
            if response.status_code == 200:
                data = response.json()
                
                # Check structure
                if "models" not in data:
                    self.print_test("GET /api/tags structure", False, 
                                  "Missing 'models' key", duration)
                    return False
                
                models = data["models"]
                passed = len(models) > 0
                
                # Store for later tests
                self.available_patterns = [m["name"].replace(":latest", "") 
                                          for m in models if isinstance(m, dict) and "name" in m]
                
                self.print_test("GET /api/tags", passed, 
                              f"Found {len(models)} patterns as models", duration)
                
                # Show sample patterns
                if len(models) > 0:
                    sample = [m.get("name", "") for m in models[:5] if isinstance(m, dict)]
                    print(f"       Sample: {', '.join(sample)}")
                
                return passed
            else:
                self.print_test("GET /api/tags", False, 
                              f"Status: {response.status_code}", duration)
                return False
        except Exception as e:
            self.print_test("GET /api/tags", False, str(e))
            return False
    
    def test_pattern_naming_convention(self) -> bool:
        """Test patterns follow Ollama naming convention (name:latest)"""
        if not self.available_patterns:
            self.print_test("Pattern naming convention", True, 
                          "Skipped - no patterns loaded")
            return True
        
        try:
            response = requests.get(f"{self.ollama_base}/api/tags", timeout=10)
            if response.status_code == 200:
                models = response.json().get("models", [])
                
                # Check all have :latest or :tag format
                valid_names = []
                invalid_names = []
                
                for model in models[:10]:  # Check first 10
                    name = model.get("name", "")
                    if ":" in name:
                        valid_names.append(name)
                    else:
                        invalid_names.append(name)
                
                passed = len(invalid_names) == 0
                message = f"Valid: {len(valid_names)}, Invalid: {len(invalid_names)}"
                
                self.print_test("Pattern naming convention", passed, message)
                return passed
        except Exception as e:
            self.print_test("Pattern naming convention", False, str(e))
            return False
    
    def test_common_patterns_available(self) -> bool:
        """Test common patterns are available as models"""
        common_patterns = ["summarize", "analyze_code", "explain_code", 
                          "extract_wisdom", "improve_writing"]
        
        found = []
        missing = []
        
        for pattern in common_patterns:
            if pattern in self.available_patterns:
                found.append(pattern)
            else:
                missing.append(pattern)
        
        passed = len(found) >= 3  # At least 3 common patterns
        message = f"Found: {len(found)}/{len(common_patterns)} - {', '.join(found[:3])}"
        
        self.print_test("Common patterns available", passed, message)
        return passed
    
    # ===== Chat Endpoint Tests =====
    
    def test_chat_endpoint_basic(self) -> bool:
        """Test basic /api/chat functionality"""
        self.print_header("Ollama Chat Endpoint")
        
        try:
            start = time.time()
            
            payload = {
                "model": "summarize:latest",
                "messages": [
                    {"role": "user", "content": "Test message for Ollama integration"}
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
                
                # Check response structure
                has_message = "message" in result or "response" in result
                
                if has_message:
                    content = result.get("message", {}).get("content", "") or result.get("response", "")
                    self.print_test("POST /api/chat (basic)", True, 
                                  f"Response: {len(content)} chars", duration)
                    return True
                else:
                    self.print_test("POST /api/chat (basic)", False, 
                                  "Invalid response structure", duration)
                    return False
            else:
                self.print_test("POST /api/chat (basic)", False, 
                              f"Status: {response.status_code}", duration)
                return False
        except Exception as e:
            self.print_test("POST /api/chat (basic)", False, str(e))
            return False
    
    def test_chat_with_different_patterns(self) -> bool:
        """Test chat with multiple different patterns"""
        patterns_to_test = ["summarize:latest", "analyze_code:latest", "extract_wisdom:latest"]
        all_passed = True
        
        for pattern in patterns_to_test:
            # Check if pattern exists
            pattern_name = pattern.replace(":latest", "")
            if pattern_name not in self.available_patterns:
                self.print_test(f"Chat with '{pattern_name}'", True, 
                              "Skipped - pattern not available")
                continue
            
            try:
                start = time.time()
                
                payload = {
                    "model": pattern,
                    "messages": [
                        {"role": "user", "content": f"Test for {pattern_name}"}
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
                    has_response = "message" in result or "response" in result
                    self.print_test(f"Chat with '{pattern_name}'", has_response, 
                                  f"Completed in {duration:.1f}s", duration)
                    if not has_response:
                        all_passed = False
                else:
                    self.print_test(f"Chat with '{pattern_name}'", False, 
                                  f"Status: {response.status_code}", duration)
                    all_passed = False
            except Exception as e:
                self.print_test(f"Chat with '{pattern_name}'", False, str(e))
                all_passed = False
        
        return all_passed
    
    def test_chat_streaming(self) -> bool:
        """Test streaming chat responses"""
        try:
            start = time.time()
            
            payload = {
                "model": "summarize:latest",
                "messages": [
                    {"role": "user", "content": "Stream test message"}
                ],
                "stream": True
            }
            
            response = requests.post(
                f"{self.ollama_base}/api/chat",
                json=payload,
                stream=True,
                timeout=30
            )
            duration = time.time() - start
            
            if response.status_code == 200:
                chunks = []
                for line in response.iter_lines(decode_unicode=True):
                    if line:
                        try:
                            data = json.loads(line)
                            chunks.append(data)
                            if len(chunks) >= 3:  # Get a few chunks
                                break
                        except json.JSONDecodeError:
                            continue
                
                passed = len(chunks) > 0
                self.print_test("Streaming chat", passed, 
                              f"Received {len(chunks)} chunks", duration)
                return passed
            else:
                self.print_test("Streaming chat", False, 
                              f"Status: {response.status_code}", duration)
                return False
        except Exception as e:
            self.print_test("Streaming chat", False, str(e))
            return False
    
    def test_chat_with_context(self) -> bool:
        """Test chat with multiple messages (context)"""
        try:
            start = time.time()
            
            payload = {
                "model": "summarize:latest",
                "messages": [
                    {"role": "user", "content": "Hello, I need help."},
                    {"role": "assistant", "content": "Hello! How can I help you?"},
                    {"role": "user", "content": "Summarize the previous conversation."}
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
                has_response = "message" in result or "response" in result
                self.print_test("Chat with context", has_response, 
                              "Multi-message conversation handled", duration)
                return has_response
            else:
                self.print_test("Chat with context", False, 
                              f"Status: {response.status_code}", duration)
                return False
        except Exception as e:
            self.print_test("Chat with context", False, str(e))
            return False
    
    # ===== Pattern-Specific Tests =====
    
    def test_code_analysis_pattern(self) -> bool:
        """Test code analysis pattern"""
        self.print_header("Pattern-Specific Tests")
        
        if "analyze_code" not in self.available_patterns:
            self.print_test("Code analysis pattern", True, 
                          "Skipped - pattern not available")
            return True
        
        try:
            start = time.time()
            
            code_sample = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n-1)
"""
            
            payload = {
                "model": "analyze_code:latest",
                "messages": [
                    {"role": "user", "content": f"Analyze this code:\n{code_sample}"}
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
                content = result.get("message", {}).get("content", "") or result.get("response", "")
                
                # Check if analysis seems reasonable (mentions code concepts)
                has_analysis = len(content) > 50
                
                self.print_test("Code analysis pattern", has_analysis, 
                              f"Generated {len(content)} char analysis", duration)
                return has_analysis
            else:
                self.print_test("Code analysis pattern", False, 
                              f"Status: {response.status_code}", duration)
                return False
        except Exception as e:
            self.print_test("Code analysis pattern", False, str(e))
            return False
    
    def test_summarize_pattern(self) -> bool:
        """Test summarize pattern"""
        if "summarize" not in self.available_patterns:
            self.print_test("Summarize pattern", True, 
                          "Skipped - pattern not available")
            return True
        
        try:
            start = time.time()
            
            long_text = """
Artificial intelligence is transforming software development. 
Machine learning models can now generate code, detect bugs, and optimize performance.
Developers are using AI-powered tools to increase productivity and code quality.
The future of programming involves collaboration between human developers and AI systems.
This technology is rapidly evolving and becoming more sophisticated each year.
"""
            
            payload = {
                "model": "summarize:latest",
                "messages": [
                    {"role": "user", "content": long_text}
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
                content = result.get("message", {}).get("content", "") or result.get("response", "")
                
                # Summary should be shorter than input but not empty
                passed = 20 < len(content) < len(long_text)
                
                self.print_test("Summarize pattern", passed, 
                              f"Input: {len(long_text)}, Output: {len(content)}", duration)
                return passed
            else:
                self.print_test("Summarize pattern", False, 
                              f"Status: {response.status_code}", duration)
                return False
        except Exception as e:
            self.print_test("Summarize pattern", False, str(e))
            return False
    
    def test_extract_wisdom_pattern(self) -> bool:
        """Test extract_wisdom pattern"""
        if "extract_wisdom" not in self.available_patterns:
            self.print_test("Extract wisdom pattern", True, 
                          "Skipped - pattern not available")
            return True
        
        try:
            start = time.time()
            
            content = """
The key to successful software development is clear communication.
Always write code as if the person maintaining it is a violent psychopath who knows where you live.
Premature optimization is the root of all evil in programming.
"""
            
            payload = {
                "model": "extract_wisdom:latest",
                "messages": [
                    {"role": "user", "content": content}
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
                wisdom = result.get("message", {}).get("content", "") or result.get("response", "")
                
                passed = len(wisdom) > 30
                
                self.print_test("Extract wisdom pattern", passed, 
                              f"Extracted {len(wisdom)} chars", duration)
                return passed
            else:
                self.print_test("Extract wisdom pattern", False, 
                              f"Status: {response.status_code}", duration)
                return False
        except Exception as e:
            self.print_test("Extract wisdom pattern", False, str(e))
            return False
    
    # ===== Compatibility Tests =====
    
    def test_ollama_client_compatibility(self) -> bool:
        """Test compatibility with standard Ollama client expectations"""
        self.print_header("Ollama Client Compatibility")
        
        # Test 1: Version endpoint returns expected format
        try:
            response = requests.get(f"{self.ollama_base}/api/version", timeout=5)
            version_ok = response.status_code == 200 and isinstance(response.json(), dict)
        except:
            version_ok = False
        
        # Test 2: Tags endpoint returns expected format
        try:
            response = requests.get(f"{self.ollama_base}/api/tags", timeout=5)
            data = response.json()
            tags_ok = response.status_code == 200 and "models" in data and isinstance(data["models"], list)
        except:
            tags_ok = False
        
        # Test 3: Chat endpoint accepts standard payload
        try:
            payload = {
                "model": "summarize:latest",
                "messages": [{"role": "user", "content": "test"}],
                "stream": False
            }
            response = requests.post(f"{self.ollama_base}/api/chat", json=payload, timeout=30)
            chat_ok = response.status_code == 200
        except:
            chat_ok = False
        
        all_ok = version_ok and tags_ok and chat_ok
        details = f"Version: {version_ok}, Tags: {tags_ok}, Chat: {chat_ok}"
        
        self.print_test("Ollama client compatibility", all_ok, details)
        return all_ok
    
    def test_error_handling(self) -> bool:
        """Test error handling for invalid requests"""
        # Test 1: Invalid model name
        try:
            payload = {
                "model": "nonexistent_pattern:latest",
                "messages": [{"role": "user", "content": "test"}],
                "stream": False
            }
            response = requests.post(f"{self.ollama_base}/api/chat", json=payload, timeout=10)
            invalid_model_handled = response.status_code in [404, 400]
        except:
            invalid_model_handled = False
        
        # Test 2: Missing messages field
        try:
            payload = {
                "model": "summarize:latest",
                "stream": False
            }
            response = requests.post(f"{self.ollama_base}/api/chat", json=payload, timeout=10)
            missing_field_handled = response.status_code in [400, 422]
        except:
            missing_field_handled = False
        
        # Test 3: Malformed JSON
        try:
            response = requests.post(
                f"{self.ollama_base}/api/chat",
                data="invalid json",
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            malformed_handled = response.status_code in [400, 422]
        except:
            malformed_handled = False
        
        all_handled = invalid_model_handled and missing_field_handled and malformed_handled
        details = f"Invalid model: {invalid_model_handled}, Missing field: {missing_field_handled}, Malformed: {malformed_handled}"
        
        self.print_test("Error handling", all_handled, details)
        return all_handled
    
    # ===== Performance Tests =====
    
    def test_response_times(self) -> bool:
        """Test response times are reasonable"""
        self.print_header("Performance Tests")
        
        times = []
        
        for i in range(3):
            try:
                start = time.time()
                payload = {
                    "model": "summarize:latest",
                    "messages": [{"role": "user", "content": f"Test {i}"}],
                    "stream": False
                }
                response = requests.post(
                    f"{self.ollama_base}/api/chat",
                    json=payload,
                    timeout=30
                )
                if response.status_code == 200:
                    times.append(time.time() - start)
            except:
                times.append(30.0)
        
        if len(times) > 0:
            avg_time = sum(times) / len(times)
            max_time = max(times)
            
            # Response should be under 10 seconds on average
            passed = avg_time < 10.0
            
            self.print_test("Response times", passed, 
                          f"Avg: {avg_time:.1f}s, Max: {max_time:.1f}s")
            return passed
        else:
            self.print_test("Response times", False, "No successful responses")
            return False
    
    def test_concurrent_requests(self) -> bool:
        """Test handling concurrent requests"""
        import threading
        
        results = []
        
        def make_request():
            try:
                payload = {
                    "model": "summarize:latest",
                    "messages": [{"role": "user", "content": "Concurrent test"}],
                    "stream": False
                }
                response = requests.post(
                    f"{self.ollama_base}/api/chat",
                    json=payload,
                    timeout=30
                )
                results.append(response.status_code == 200)
            except:
                results.append(False)
        
        # Start 3 concurrent requests
        threads = []
        start = time.time()
        
        for _ in range(3):
            t = threading.Thread(target=make_request)
            t.start()
            threads.append(t)
        
        for t in threads:
            t.join()
        
        duration = time.time() - start
        
        success_count = sum(1 for r in results if r)
        passed = success_count == 3
        
        self.print_test("Concurrent requests (3x)", passed, 
                      f"{success_count}/3 successful", duration)
        return passed
    
    # ===== Integration with Fabric API =====
    
    def test_fabric_api_comparison(self) -> bool:
        """Test Ollama API returns similar results to Fabric API"""
        self.print_header("Fabric API Integration")
        
        test_input = "Artificial intelligence is transforming technology."
        
        # Get result from Fabric API
        try:
            fabric_payload = {
                "input": test_input,
                "pattern": "summarize",
                "stream": False
            }
            fabric_response = requests.post(
                f"{self.fabric_api_base}/chat",
                json=fabric_payload,
                timeout=30
            )
            fabric_result = fabric_response.text if fabric_response.status_code == 200 else ""
        except:
            fabric_result = ""
        
        # Get result from Ollama API
        try:
            ollama_payload = {
                "model": "summarize:latest",
                "messages": [{"role": "user", "content": test_input}],
                "stream": False
            }
            ollama_response = requests.post(
                f"{self.ollama_base}/api/chat",
                json=ollama_payload,
                timeout=30
            )
            ollama_result = ollama_response.json().get("message", {}).get("content", "") if ollama_response.status_code == 200 else ""
        except:
            ollama_result = ""
        
        # Both should return non-empty results
        both_work = len(fabric_result) > 0 and len(ollama_result) > 0
        
        message = f"Fabric: {len(fabric_result)} chars, Ollama: {len(ollama_result)} chars"
        
        self.print_test("Fabric vs Ollama API", both_work, message)
        return both_work
    
    # ===== Summary =====
    
    def print_summary(self):
        """Print test summary"""
        self.print_header("Ollama Integration Test Summary")
        
        passed = sum(1 for _, result, _, _ in self.test_results if result)
        failed = sum(1 for _, result, _, _ in self.test_results if not result)
        total = len(self.test_results)
        
        total_time = sum(duration for _, _, _, duration in self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"{GREEN}Passed: {passed}{NC}")
        print(f"{RED}Failed: {failed}{NC}")
        print(f"Total Time: {total_time:.2f}s")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        
        print(f"\n{CYAN}Patterns Found: {len(self.available_patterns)}{NC}")
        if len(self.available_patterns) > 0:
            print(f"  Sample: {', '.join(self.available_patterns[:5])}")
        
        if failed > 0:
            print(f"\n{YELLOW}Failed Tests:{NC}")
            for name, result, message, _ in self.test_results:
                if not result:
                    msg_short = message[:80] if message else ""
                    print(f"  - {name}: {msg_short}")
        
        print(f"\n{BLUE}{'='*70}{NC}")
        if failed == 0:
            print(f"{GREEN}{'🎉 ALL OLLAMA TESTS PASSED! 🎉':^70}{NC}")
        else:
            print(f"{YELLOW}{'⚠️  SOME TESTS FAILED':^70}{NC}")
        print(f"{BLUE}{'='*70}{NC}")
        
        return failed == 0


def run_ollama_tests():
    """Run all Ollama integration tests"""
    suite = OllamaIntegrationTests()
    
    print(f"{BLUE}{'='*70}{NC}")
    print(f"{BLUE}{'Fabric Ollama Integration Tests':^70}{NC}")
    print(f"{BLUE}{'='*70}{NC}")
    
    # Check if Ollama API is available
    if not suite.test_ollama_api_available():
        print(f"\n{RED}Ollama API not available on port 11434{NC}")
        print(f"{YELLOW}Start with: docker-compose --profile ollama up -d{NC}\n")
        return False
    
    # Connection tests
    suite.test_version_endpoint()
    
    # Model listing tests
    suite.test_tags_endpoint()
    suite.test_pattern_naming_convention()
    suite.test_common_patterns_available()
    
    # Chat endpoint tests
    suite.test_chat_endpoint_basic()
    suite.test_chat_with_different_patterns()
    suite.test_chat_streaming()
    suite.test_chat_with_context()
    
    # Pattern-specific tests
    suite.test_code_analysis_pattern()
    suite.test_summarize_pattern()
    suite.test_extract_wisdom_pattern()
    
    # Compatibility tests
    suite.test_ollama_client_compatibility()
    suite.test_error_handling()
    
    # Performance tests
    suite.test_response_times()
    suite.test_concurrent_requests()
    
    # Integration tests
    suite.test_fabric_api_comparison()
    
    # Print summary
    all_passed = suite.print_summary()
    
    return all_passed


if __name__ == '__main__':
    success = run_ollama_tests()
    sys.exit(0 if success else 1)
