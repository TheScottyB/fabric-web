#!/usr/bin/env python3
"""
Pattern Validation Tests for Fabric
Tests pattern file existence, structure, and integrity.
"""

import os
import sys
import subprocess
import json
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


class PatternValidationTests:
    """Test suite for pattern validation"""
    
    def __init__(self):
        self.api_base = 'http://localhost:8080'
        self.test_results = []
        self.patterns_dir = Path.home() / '.config' / 'fabric' / 'patterns'
        
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
            print(f"       {message}")
        self.test_results.append((name, passed, message))
    
    def test_patterns_api_available(self) -> bool:
        """Test that patterns API endpoint is available"""
        self.print_header("Pattern API Availability")
        
        try:
            response = requests.get(f"{self.api_base}/patterns", timeout=10)
            
            if response.status_code == 200:
                patterns = response.json()
                self.print_test("Patterns API endpoint", True, f"Status: {response.status_code}")
                self.print_test("Pattern count from API", True, f"Found {len(patterns)} patterns")
                return True
            else:
                self.print_test("Patterns API endpoint", False, f"Status: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            self.print_test("Patterns API endpoint", False, "API not running")
            return False
        except Exception as e:
            self.print_test("Patterns API endpoint", False, str(e))
            return False
    
    def test_pattern_directory_exists(self) -> bool:
        """Test that the patterns directory exists"""
        self.print_header("Pattern Directory")
        
        if self.patterns_dir.exists():
            self.print_test("Patterns directory exists", True, str(self.patterns_dir))
            return True
        else:
            # Try alternative locations
            alt_paths = [
                Path('/home/fabric/.config/fabric/patterns'),  # Docker container
                Path.home() / '.fabric' / 'patterns',
            ]
            
            for alt in alt_paths:
                if alt.exists():
                    self.patterns_dir = alt
                    self.print_test("Patterns directory exists", True, f"Found at: {alt}")
                    return True
            
            self.print_test("Patterns directory exists", False, f"Not found at {self.patterns_dir}")
            return False
    
    def test_minimum_pattern_count(self) -> bool:
        """Test that minimum number of patterns exist"""
        self.print_header("Pattern Count Validation")
        
        min_expected = 200  # Expect at least 200 patterns
        
        if not self.patterns_dir.exists():
            self.print_test("Pattern count check", False, "Patterns directory not found")
            return False
        
        try:
            patterns = [d for d in self.patterns_dir.iterdir() if d.is_dir()]
            count = len(patterns)
            
            if count >= min_expected:
                self.print_test("Minimum pattern count", True, f"Found {count} patterns (>= {min_expected})")
                return True
            else:
                self.print_test("Minimum pattern count", False, f"Found {count} patterns (expected >= {min_expected})")
                return False
        except Exception as e:
            self.print_test("Pattern count check", False, str(e))
            return False
    
    def test_core_patterns_exist(self) -> bool:
        """Test that core/essential patterns exist"""
        self.print_header("Core Patterns Existence")
        
        core_patterns = [
            'summarize',
            'extract_wisdom',
            'analyze_claims',
            'explain_code',
            'improve_prompt',
            'create_summary',
            'rate_value',
            'extract_main_idea',
        ]
        
        all_passed = True
        
        # Check via API first
        try:
            response = requests.get(f"{self.api_base}/patterns", timeout=10)
            if response.status_code == 200:
                api_patterns = response.json()
                
                for pattern in core_patterns:
                    if pattern in api_patterns:
                        self.print_test(f"Core pattern: {pattern}", True, "Available via API")
                    else:
                        self.print_test(f"Core pattern: {pattern}", False, "Not found in API")
                        all_passed = False
                
                return all_passed
        except:
            pass
        
        # Fallback to filesystem check
        if not self.patterns_dir.exists():
            for pattern in core_patterns:
                self.print_test(f"Core pattern: {pattern}", False, "Cannot verify (no patterns dir)")
            return False
        
        for pattern in core_patterns:
            pattern_path = self.patterns_dir / pattern
            if pattern_path.exists():
                self.print_test(f"Core pattern: {pattern}", True, "Found on filesystem")
            else:
                self.print_test(f"Core pattern: {pattern}", False, "Not found")
                all_passed = False
        
        return all_passed
    
    def test_pattern_structure(self) -> bool:
        """Test that patterns have the correct file structure"""
        self.print_header("Pattern File Structure")
        
        if not self.patterns_dir.exists():
            self.print_test("Pattern structure check", False, "Patterns directory not found")
            return False
        
        all_passed = True
        sample_patterns = list(self.patterns_dir.iterdir())[:10]  # Check first 10
        
        for pattern_dir in sample_patterns:
            if not pattern_dir.is_dir():
                continue
            
            pattern_name = pattern_dir.name
            system_file = pattern_dir / 'system.md'
            
            if system_file.exists():
                # Check file is not empty
                content = system_file.read_text()
                if len(content) > 10:
                    self.print_test(f"Pattern structure: {pattern_name}", True, "Has system.md with content")
                else:
                    self.print_test(f"Pattern structure: {pattern_name}", False, "system.md is too short")
                    all_passed = False
            else:
                self.print_test(f"Pattern structure: {pattern_name}", False, "Missing system.md")
                all_passed = False
        
        return all_passed
    
    def test_pattern_content_format(self) -> bool:
        """Test that pattern content follows expected format"""
        self.print_header("Pattern Content Format")
        
        if not self.patterns_dir.exists():
            self.print_test("Pattern content check", False, "Patterns directory not found")
            return False
        
        all_passed = True
        checked = 0
        
        for pattern_dir in self.patterns_dir.iterdir():
            if not pattern_dir.is_dir() or checked >= 5:
                continue
            
            system_file = pattern_dir / 'system.md'
            if not system_file.exists():
                continue
            
            content = system_file.read_text()
            pattern_name = pattern_dir.name
            
            # Check for common pattern elements
            has_instructions = any(word in content.lower() for word in ['you are', 'your task', 'instructions', 'output'])
            has_structure = len(content.split('\n')) > 3
            
            if has_instructions and has_structure:
                self.print_test(f"Content format: {pattern_name}", True, "Has instructions and structure")
            else:
                issues = []
                if not has_instructions:
                    issues.append("missing instructions")
                if not has_structure:
                    issues.append("too short/unstructured")
                self.print_test(f"Content format: {pattern_name}", False, ", ".join(issues))
                all_passed = False
            
            checked += 1
        
        return all_passed
    
    def test_pattern_api_execution(self) -> bool:
        """Test that a pattern can be executed via API"""
        self.print_header("Pattern Execution Test")
        
        test_input = "This is a test input for validating pattern execution."
        test_pattern = "summarize"
        
        try:
            # Check if API is available
            health_response = requests.get(f"{self.api_base}/health", timeout=5)
            if health_response.status_code != 200:
                self.print_test("API health check", False, "API not healthy")
                return False
            
            self.print_test("API health check", True)
            
            # Try to execute a pattern
            payload = {
                "input": test_input,
                "pattern": test_pattern,
                "stream": False
            }
            
            response = requests.post(
                f"{self.api_base}/chat",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.text
                if len(result) > 0:
                    self.print_test(f"Execute pattern: {test_pattern}", True, f"Got response ({len(result)} chars)")
                    return True
                else:
                    self.print_test(f"Execute pattern: {test_pattern}", False, "Empty response")
                    return False
            else:
                self.print_test(f"Execute pattern: {test_pattern}", False, f"Status: {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            self.print_test("Pattern execution", False, "API not running")
            return False
        except requests.exceptions.Timeout:
            self.print_test("Pattern execution", False, "Timeout (API may be slow)")
            return False
        except Exception as e:
            self.print_test("Pattern execution", False, str(e))
            return False
    
    def test_pattern_names_valid(self) -> bool:
        """Test that pattern names follow naming conventions"""
        self.print_header("Pattern Naming Conventions")
        
        if not self.patterns_dir.exists():
            self.print_test("Pattern naming check", False, "Patterns directory not found")
            return False
        
        all_passed = True
        invalid_patterns = []
        
        for pattern_dir in self.patterns_dir.iterdir():
            if not pattern_dir.is_dir():
                continue
            
            name = pattern_dir.name
            
            # Check naming rules
            is_valid = (
                name.islower() or name.replace('_', '').islower() or name.replace('-', '').islower()
            ) and not name.startswith('.')
            
            if not is_valid:
                invalid_patterns.append(name)
        
        if len(invalid_patterns) == 0:
            self.print_test("Pattern naming conventions", True, "All patterns follow conventions")
        else:
            self.print_test("Pattern naming conventions", False, f"Invalid: {', '.join(invalid_patterns[:5])}")
            all_passed = False
        
        return all_passed
    
    def test_no_duplicate_patterns(self) -> bool:
        """Test that there are no duplicate pattern names"""
        self.print_header("Pattern Uniqueness")
        
        try:
            response = requests.get(f"{self.api_base}/patterns", timeout=10)
            if response.status_code == 200:
                patterns = response.json()
                unique_patterns = set(patterns)
                
                if len(patterns) == len(unique_patterns):
                    self.print_test("No duplicate patterns", True, f"All {len(patterns)} patterns are unique")
                    return True
                else:
                    duplicates = len(patterns) - len(unique_patterns)
                    self.print_test("No duplicate patterns", False, f"Found {duplicates} duplicates")
                    return False
        except:
            pass
        
        # Fallback to filesystem
        if not self.patterns_dir.exists():
            self.print_test("Pattern uniqueness check", False, "Cannot verify")
            return False
        
        patterns = [d.name for d in self.patterns_dir.iterdir() if d.is_dir()]
        unique = set(patterns)
        
        if len(patterns) == len(unique):
            self.print_test("No duplicate patterns", True, "All patterns unique")
            return True
        else:
            self.print_test("No duplicate patterns", False, "Duplicates found")
            return False
    
    def print_summary(self) -> bool:
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
    """Run all pattern validation tests"""
    suite = PatternValidationTests()
    
    print(f"{BLUE}{'='*60}{NC}")
    print(f"{BLUE}{'Pattern Validation Test Suite':^60}{NC}")
    print(f"{BLUE}{'='*60}{NC}")
    
    # Run all tests
    suite.test_patterns_api_available()
    suite.test_pattern_directory_exists()
    suite.test_minimum_pattern_count()
    suite.test_core_patterns_exist()
    suite.test_pattern_structure()
    suite.test_pattern_content_format()
    suite.test_pattern_names_valid()
    suite.test_no_duplicate_patterns()
    suite.test_pattern_api_execution()
    
    # Print summary
    all_passed = suite.print_summary()
    
    return all_passed


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
