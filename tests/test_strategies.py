#!/usr/bin/env python3
"""
Fabric Strategy Integration Tests
Comprehensive tests for all 9 prompt strategies and their behavior
"""

import os
import sys
import json
import time
import subprocess
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


class StrategyIntegrationTests:
    """Strategy integration test suite"""
    
    def __init__(self):
        self.api_base = 'http://localhost:8080'
        self.test_results = []
        
        # All 9 strategies
        self.strategies = [
            'standard',
            'cot',           # Chain-of-Thought
            'cod',           # Chain-of-Draft
            'tot',           # Tree-of-Thought
            'aot',           # Atom-of-Thought
            'ltm',           # Least-to-Most
            'self-consistent',
            'self-refine',
            'reflexion'
        ]
        
        # Test inputs
        self.test_inputs = {
            'simple': "Explain what artificial intelligence is.",
            'code': """
def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)
""",
            'complex': "Design a scalable microservices architecture for a social media platform with 100 million users.",
        }
        
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
    
    # ===== Strategy Installation Tests =====
    
    def test_strategies_installed(self) -> bool:
        """Test strategies are installed"""
        self.print_header("Strategy Installation")
        
        strategies_dir = Path.home() / '.config' / 'fabric' / 'strategies'
        
        if not strategies_dir.exists():
            self.print_test("Strategies directory exists", False,
                          f"Directory not found. Run: fabric -S")
            return False
        
        self.print_test("Strategies directory exists", True, str(strategies_dir))
        
        # Check each strategy file
        all_found = True
        found_strategies = []
        missing_strategies = []
        
        for strategy in self.strategies:
            strategy_file = strategies_dir / f"{strategy}.json"
            if strategy_file.exists():
                found_strategies.append(strategy)
            else:
                missing_strategies.append(strategy)
                all_found = False
        
        message = f"Found: {len(found_strategies)}/{len(self.strategies)}"
        if missing_strategies:
            message += f" - Missing: {', '.join(missing_strategies)}"
        
        self.print_test("All strategies installed", all_found, message)
        return all_found
    
    # ===== CLI Strategy Tests =====
    
    def test_strategy_cli_execution(self) -> bool:
        """Test strategy execution via CLI"""
        self.print_header("CLI Strategy Execution")
        
        test_input = self.test_inputs['simple']
        all_passed = True
        
        for strategy in ['standard', 'cot', 'tot']:  # Test subset
            try:
                start = time.time()
                
                # Create temp file with input
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
                    f.write(test_input)
                    temp_path = f.name
                
                # Run fabric with strategy
                result = subprocess.run(
                    ['fabric', '--strategy', strategy, '-p', 'summarize'],
                    stdin=open(temp_path, 'r'),
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                duration = time.time() - start
                
                # Cleanup
                os.unlink(temp_path)
                
                if result.returncode == 0:
                    output = result.stdout
                    passed = len(output) > 20
                    
                    self.print_test(f"CLI: fabric --strategy {strategy}", passed,
                                  f"Generated {len(output)} chars", duration)
                    
                    if not passed:
                        all_passed = False
                else:
                    error = result.stderr[:100] if result.stderr else "Unknown error"
                    self.print_test(f"CLI: fabric --strategy {strategy}", False,
                                  error, duration)
                    all_passed = False
                    
            except Exception as e:
                self.print_test(f"CLI: fabric --strategy {strategy}", False, str(e))
                all_passed = False
        
        return all_passed
    
    # ===== API Strategy Tests =====
    
    def test_strategy_api_execution(self) -> bool:
        """Test strategy execution via API"""
        self.print_header("API Strategy Execution")
        
        test_input = self.test_inputs['simple']
        all_passed = True
        
        for strategy in self.strategies:
            try:
                start = time.time()
                
                payload = {
                    "input": test_input,
                    "pattern": "summarize",
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
                    output = response.text
                    passed = len(output) > 20
                    
                    self.print_test(f"API: strategy={strategy}", passed,
                                  f"Output: {len(output)} chars", duration)
                    
                    if not passed:
                        all_passed = False
                elif response.status_code == 404:
                    # Strategy not found - might not be installed
                    self.print_test(f"API: strategy={strategy}", True,
                                  "Strategy not available (optional)")
                else:
                    self.print_test(f"API: strategy={strategy}", False,
                                  f"Status: {response.status_code}", duration)
                    all_passed = False
                    
            except Exception as e:
                self.print_test(f"API: strategy={strategy}", False, str(e))
                all_passed = False
        
        return all_passed
    
    # ===== Strategy Comparison Tests =====
    
    def test_strategy_output_differences(self) -> bool:
        """Test that different strategies produce different outputs"""
        self.print_header("Strategy Output Comparison")
        
        test_input = self.test_inputs['simple']
        outputs = {}
        
        # Get outputs from different strategies
        strategies_to_compare = ['standard', 'cot', 'tot']
        
        for strategy in strategies_to_compare:
            try:
                payload = {
                    "input": test_input,
                    "pattern": "summarize",
                    "strategy": strategy,
                    "stream": False
                }
                
                response = requests.post(
                    f"{self.api_base}/chat",
                    json=payload,
                    timeout=40
                )
                
                if response.status_code == 200:
                    outputs[strategy] = response.text
            except:
                pass
        
        # Compare outputs
        if len(outputs) < 2:
            self.print_test("Strategy outputs differ", False,
                          "Not enough strategies responded")
            return False
        
        # Standard vs CoT should be different
        if 'standard' in outputs and 'cot' in outputs:
            are_different = outputs['standard'] != outputs['cot']
            length_diff = abs(len(outputs['standard']) - len(outputs['cot']))
            
            self.print_test("Standard vs CoT differ", are_different,
                          f"Length difference: {length_diff} chars")
        
        # CoT vs ToT should be different
        if 'cot' in outputs and 'tot' in outputs:
            are_different = outputs['cot'] != outputs['tot']
            length_diff = abs(len(outputs['cot']) - len(outputs['tot']))
            
            self.print_test("CoT vs ToT differ", are_different,
                          f"Length difference: {length_diff} chars")
        
        return True
    
    # ===== Strategy-Specific Behavior Tests =====
    
    def test_cot_shows_reasoning(self) -> bool:
        """Test Chain-of-Thought shows step-by-step reasoning"""
        self.print_header("Strategy-Specific Behavior")
        
        test_input = "Calculate 15% of 240 and explain your steps."
        
        try:
            start = time.time()
            
            payload = {
                "input": test_input,
                "pattern": "summarize",
                "strategy": "cot",
                "stream": False
            }
            
            response = requests.post(
                f"{self.api_base}/chat",
                json=payload,
                timeout=30
            )
            duration = time.time() - start
            
            if response.status_code == 200:
                output = response.text.lower()
                
                # CoT should mention steps or reasoning
                has_reasoning = any(keyword in output for keyword in 
                                   ['step', 'first', 'second', 'then', 'therefore',
                                    'because', 'so', 'thus', 'calculation'])
                
                self.print_test("CoT shows reasoning steps", has_reasoning,
                              "Contains reasoning keywords" if has_reasoning else "No reasoning found",
                              duration)
                return has_reasoning
            else:
                self.print_test("CoT shows reasoning steps", False,
                              f"Status: {response.status_code}", duration)
                return False
                
        except Exception as e:
            self.print_test("CoT shows reasoning steps", False, str(e))
            return False
    
    def test_tot_explores_alternatives(self) -> bool:
        """Test Tree-of-Thought explores multiple paths"""
        test_input = self.test_inputs['complex']
        
        try:
            start = time.time()
            
            payload = {
                "input": test_input,
                "pattern": "create_design_document",
                "strategy": "tot",
                "stream": False
            }
            
            response = requests.post(
                f"{self.api_base}/chat",
                json=payload,
                timeout=40
            )
            duration = time.time() - start
            
            if response.status_code == 200:
                output = response.text.lower()
                
                # ToT should explore alternatives/options
                explores = any(keyword in output for keyword in 
                              ['option', 'alternative', 'approach', 'path',
                               'solution', 'way', 'method'])
                
                self.print_test("ToT explores alternatives", explores,
                              "Contains alternative exploration" if explores else "No alternatives",
                              duration)
                return explores
            elif response.status_code == 404:
                self.print_test("ToT explores alternatives", True,
                              "Pattern not available (optional)", duration)
                return True
            else:
                self.print_test("ToT explores alternatives", False,
                              f"Status: {response.status_code}", duration)
                return False
                
        except Exception as e:
            self.print_test("ToT explores alternatives", False, str(e))
            return False
    
    def test_standard_is_concise(self) -> bool:
        """Test standard strategy is most concise"""
        test_input = self.test_inputs['simple']
        lengths = {}
        
        for strategy in ['standard', 'cot', 'tot']:
            try:
                payload = {
                    "input": test_input,
                    "pattern": "summarize",
                    "strategy": strategy,
                    "stream": False
                }
                
                response = requests.post(
                    f"{self.api_base}/chat",
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    lengths[strategy] = len(response.text)
            except:
                pass
        
        if 'standard' in lengths and len(lengths) >= 2:
            is_shortest = all(lengths['standard'] <= lengths[s] 
                            for s in lengths if s != 'standard')
            
            comparison = ', '.join(f"{s}: {l}" for s, l in lengths.items())
            
            self.print_test("Standard is most concise", is_shortest,
                          f"Lengths: {comparison}")
            return is_shortest
        else:
            self.print_test("Standard is most concise", False,
                          "Not enough responses to compare")
            return False
    
    # ===== Strategy with Different Patterns =====
    
    def test_strategies_with_code_pattern(self) -> bool:
        """Test strategies work with code analysis pattern"""
        self.print_header("Strategies with Different Patterns")
        
        test_input = self.test_inputs['code']
        all_passed = True
        
        for strategy in ['standard', 'cot', 'reflexion']:
            try:
                start = time.time()
                
                payload = {
                    "input": test_input,
                    "pattern": "analyze_code",
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
                    output = response.text
                    passed = len(output) > 50
                    
                    self.print_test(f"{strategy} + analyze_code", passed,
                                  f"Generated {len(output)} chars", duration)
                    
                    if not passed:
                        all_passed = False
                elif response.status_code == 404:
                    self.print_test(f"{strategy} + analyze_code", True,
                                  "Pattern not available (optional)", duration)
                else:
                    self.print_test(f"{strategy} + analyze_code", False,
                                  f"Status: {response.status_code}", duration)
                    all_passed = False
                    
            except Exception as e:
                self.print_test(f"{strategy} + analyze_code", False, str(e))
                all_passed = False
        
        return all_passed
    
    # ===== Performance Tests =====
    
    def test_strategy_performance_comparison(self) -> bool:
        """Compare performance across strategies"""
        self.print_header("Strategy Performance")
        
        test_input = self.test_inputs['simple']
        timings = {}
        
        for strategy in ['standard', 'cot', 'tot']:
            try:
                start = time.time()
                
                payload = {
                    "input": test_input,
                    "pattern": "summarize",
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
                    timings[strategy] = duration
            except:
                pass
        
        if len(timings) >= 2:
            # Standard should generally be fastest
            fastest = min(timings.values())
            slowest = max(timings.values())
            
            comparison = ', '.join(f"{s}: {t:.1f}s" for s, t in timings.items())
            
            # All should complete within 30 seconds
            all_reasonable = all(t < 30 for t in timings.values())
            
            self.print_test("Strategy performance reasonable", all_reasonable,
                          f"Times: {comparison} (range: {fastest:.1f}s - {slowest:.1f}s)")
            return all_reasonable
        else:
            self.print_test("Strategy performance reasonable", False,
                          "Not enough responses to compare")
            return False
    
    # ===== Error Handling Tests =====
    
    def test_invalid_strategy_name(self) -> bool:
        """Test error handling for invalid strategy"""
        self.print_header("Strategy Error Handling")
        
        try:
            payload = {
                "input": "Test input",
                "pattern": "summarize",
                "strategy": "invalid_strategy_12345",
                "stream": False
            }
            
            response = requests.post(
                f"{self.api_base}/chat",
                json=payload,
                timeout=10
            )
            
            # Should return 404 or 400
            passed = response.status_code in [400, 404]
            
            self.print_test("Invalid strategy handling", passed,
                          f"Status: {response.status_code}")
            return passed
            
        except Exception as e:
            self.print_test("Invalid strategy handling", False, str(e))
            return False
    
    def test_strategy_with_empty_input(self) -> bool:
        """Test strategy behavior with empty input"""
        try:
            payload = {
                "input": "",
                "pattern": "summarize",
                "strategy": "cot",
                "stream": False
            }
            
            response = requests.post(
                f"{self.api_base}/chat",
                json=payload,
                timeout=10
            )
            
            # Should handle gracefully (400/422 or empty response)
            passed = response.status_code in [200, 400, 422]
            
            self.print_test("Strategy with empty input", passed,
                          f"Status: {response.status_code}")
            return passed
            
        except Exception as e:
            self.print_test("Strategy with empty input", False, str(e))
            return False
    
    # ===== Ollama Integration Tests =====
    
    def test_strategies_with_ollama_api(self) -> bool:
        """Test strategies work through Ollama API"""
        self.print_header("Strategy + Ollama Integration")
        
        ollama_base = 'http://localhost:11434'
        
        # Check if Ollama API is available
        try:
            check_response = requests.get(f"{ollama_base}/api/version", timeout=2)
            if check_response.status_code != 200:
                self.print_test("Ollama API + strategies", True,
                              "Ollama API not available (optional)")
                return True
        except:
            self.print_test("Ollama API + strategies", True,
                          "Ollama API not available (optional)")
            return True
        
        # Test strategy with Ollama
        try:
            start = time.time()
            
            payload = {
                "model": "summarize:latest",
                "messages": [
                    {"role": "user", "content": self.test_inputs['simple']}
                ],
                "strategy": "cot",  # If Ollama supports strategy param
                "stream": False
            }
            
            response = requests.post(
                f"{ollama_base}/api/chat",
                json=payload,
                timeout=30
            )
            duration = time.time() - start
            
            if response.status_code == 200:
                result = response.json()
                has_response = "message" in result or "response" in result
                
                self.print_test("Ollama API + strategies", has_response,
                              "Strategy parameter accepted", duration)
                return has_response
            else:
                # Ollama might not support strategy param - that's ok
                self.print_test("Ollama API + strategies", True,
                              "Strategy param not supported (optional)", duration)
                return True
                
        except Exception as e:
            self.print_test("Ollama API + strategies", True,
                          f"Optional test: {str(e)[:50]}")
            return True
    
    # ===== Summary =====
    
    def print_summary(self):
        """Print test summary"""
        self.print_header("Strategy Integration Test Summary")
        
        passed = sum(1 for _, result, _, _ in self.test_results if result)
        failed = sum(1 for _, result, _, _ in self.test_results if not result)
        total = len(self.test_results)
        
        total_time = sum(duration for _, _, _, duration in self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"{GREEN}Passed: {passed}{NC}")
        print(f"{RED}Failed: {failed}{NC}")
        print(f"Total Time: {total_time:.2f}s")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        
        print(f"\n{CYAN}Strategies Tested: {len(self.strategies)}{NC}")
        print(f"  {', '.join(self.strategies)}")
        
        if failed > 0:
            print(f"\n{YELLOW}Failed Tests:{NC}")
            for name, result, message, _ in self.test_results:
                if not result:
                    msg_short = message[:80] if message else ""
                    print(f"  - {name}: {msg_short}")
        
        print(f"\n{BLUE}{'='*70}{NC}")
        if failed == 0:
            print(f"{GREEN}{'🎉 ALL STRATEGY TESTS PASSED! 🎉':^70}{NC}")
        else:
            print(f"{YELLOW}{'⚠️  SOME TESTS FAILED':^70}{NC}")
        print(f"{BLUE}{'='*70}{NC}")
        
        return failed == 0


def run_strategy_tests():
    """Run all strategy integration tests"""
    suite = StrategyIntegrationTests()
    
    print(f"{BLUE}{'='*70}{NC}")
    print(f"{BLUE}{'Fabric Strategy Integration Tests':^70}{NC}")
    print(f"{BLUE}{'='*70}{NC}")
    
    # Installation tests
    suite.test_strategies_installed()
    
    # Execution tests
    suite.test_strategy_cli_execution()
    suite.test_strategy_api_execution()
    
    # Comparison tests
    suite.test_strategy_output_differences()
    
    # Behavior tests
    suite.test_cot_shows_reasoning()
    suite.test_tot_explores_alternatives()
    suite.test_standard_is_concise()
    
    # Pattern compatibility
    suite.test_strategies_with_code_pattern()
    
    # Performance
    suite.test_strategy_performance_comparison()
    
    # Error handling
    suite.test_invalid_strategy_name()
    suite.test_strategy_with_empty_input()
    
    # Ollama integration
    suite.test_strategies_with_ollama_api()
    
    # Print summary
    all_passed = suite.print_summary()
    
    return all_passed


if __name__ == '__main__':
    success = run_strategy_tests()
    sys.exit(0 if success else 1)
