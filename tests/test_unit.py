#!/usr/bin/env python3
"""
Fabric Unit Tests
Tests for configuration, strategies, environment, and system components
"""

import os
import sys
import json
import subprocess
from typing import Dict, List, Optional
from pathlib import Path

# Color codes
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'


class FabricUnitTests:
    """Unit test suite for Fabric components"""
    
    def __init__(self):
        self.test_results = []
        self.project_root = Path(__file__).parent.parent
        self.env_path = self.project_root / '.env'
        self.config = {}
        
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
    
    # ===== Environment Tests =====
    
    def test_env_file_exists(self) -> bool:
        """Test .env file exists"""
        self.print_header("Environment Configuration")
        
        passed = self.env_path.exists()
        self.print_test(".env file exists", passed, 
                      str(self.env_path) if passed else "File not found")
        return passed
    
    def test_load_env_file(self) -> bool:
        """Load and parse .env file"""
        if not self.env_path.exists():
            self.print_test("Load .env file", False, "File not found")
            return False
        
        try:
            with open(self.env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        self.config[key.strip()] = value.strip()
            
            passed = len(self.config) > 0
            self.print_test("Load .env file", passed, 
                          f"Loaded {len(self.config)} variables")
            return passed
        except Exception as e:
            self.print_test("Load .env file", False, str(e))
            return False
    
    def test_required_api_keys(self) -> bool:
        """Test required API keys are present"""
        required_keys = ['ANTHROPIC_API_KEY', 'OPENAI_API_KEY', 'GROQ_API_KEY']
        all_passed = True
        
        for key in required_keys:
            if key in self.config:
                value = self.config[key]
                passed = len(value) > 20  # Basic length check
                self.print_test(f"{key} present", passed, 
                              f"Length: {len(value)}" if passed else "Too short")
                if not passed:
                    all_passed = False
            else:
                self.print_test(f"{key} present", False, "Missing")
                all_passed = False
        
        return all_passed
    
    def test_api_key_formats(self) -> bool:
        """Test API key format validation"""
        key_formats = {
            'ANTHROPIC_API_KEY': 'sk-ant-',
            'OPENAI_API_KEY': 'sk-',
            'GROQ_API_KEY': 'gsk_',
            'GEMINI_API_KEY': 'AIza'
        }
        
        all_passed = True
        
        for key_name, expected_prefix in key_formats.items():
            if key_name in self.config:
                value = self.config[key_name]
                passed = value.startswith(expected_prefix)
                self.print_test(f"{key_name} format", passed, 
                              f"Expected prefix: {expected_prefix}")
                if not passed:
                    all_passed = False
        
        return all_passed
    
    def test_default_config(self) -> bool:
        """Test default vendor and model configuration"""
        all_passed = True
        
        # Check DEFAULT_VENDOR
        if 'DEFAULT_VENDOR' in self.config:
            vendor = self.config['DEFAULT_VENDOR']
            valid_vendors = ['OpenAI', 'Anthropic', 'Groq', 'Gemini', 'Ollama']
            passed = vendor in valid_vendors
            self.print_test("DEFAULT_VENDOR valid", passed, 
                          f"Value: {vendor}")
            if not passed:
                all_passed = False
        else:
            self.print_test("DEFAULT_VENDOR present", False, "Missing")
            all_passed = False
        
        # Check DEFAULT_MODEL
        if 'DEFAULT_MODEL' in self.config:
            model = self.config['DEFAULT_MODEL']
            passed = len(model) > 0
            self.print_test("DEFAULT_MODEL present", passed, 
                          f"Value: {model}")
            if not passed:
                all_passed = False
        else:
            self.print_test("DEFAULT_MODEL present", False, "Missing")
            all_passed = False
        
        return all_passed
    
    # ===== File Structure Tests =====
    
    def test_dockerfile_existence(self) -> bool:
        """Test Dockerfile files exist"""
        self.print_header("File Structure")
        
        dockerfiles = [
            ('Dockerfile.api', self.project_root / 'Dockerfile.api'),
            ('Dockerfile.svelte', self.project_root / 'Dockerfile.svelte'),
            ('docker-compose.yml', self.project_root / 'docker-compose.yml'),
        ]
        
        all_passed = True
        
        for name, path in dockerfiles:
            passed = path.exists()
            self.print_test(f"{name} exists", passed, 
                          str(path) if passed else "Not found")
            if not passed:
                all_passed = False
        
        return all_passed
    
    def test_dockerfile_syntax(self) -> bool:
        """Test Dockerfile basic syntax"""
        dockerfiles = [
            ('Dockerfile.api', self.project_root / 'Dockerfile.api'),
            ('Dockerfile.svelte', self.project_root / 'Dockerfile.svelte'),
        ]
        
        all_passed = True
        
        for name, path in dockerfiles:
            if not path.exists():
                self.print_test(f"{name} syntax", False, "File not found")
                all_passed = False
                continue
            
            try:
                with open(path, 'r') as f:
                    content = f.read()
                    has_from = 'FROM ' in content
                    has_cmd = 'CMD ' in content or 'ENTRYPOINT ' in content
                    
                    passed = has_from and has_cmd
                    if passed:
                        self.print_test(f"{name} syntax", True, "Valid structure")
                    else:
                        missing = []
                        if not has_from:
                            missing.append("FROM")
                        if not has_cmd:
                            missing.append("CMD/ENTRYPOINT")
                        self.print_test(f"{name} syntax", False, 
                                      f"Missing: {', '.join(missing)}")
                        all_passed = False
            except Exception as e:
                self.print_test(f"{name} syntax", False, str(e))
                all_passed = False
        
        return all_passed
    
    def test_documentation_files(self) -> bool:
        """Test documentation files exist"""
        docs = [
            'QUICKSTART.md',
            'DOCKER_GUIDE.md',
            'REST_API_GUIDE.md',
            'STRATEGIES_GUIDE.md',
        ]
        
        all_passed = True
        
        for doc in docs:
            path = self.project_root / doc
            passed = path.exists()
            self.print_test(f"{doc} exists", passed, 
                          str(path) if passed else "Not found")
            if not passed:
                all_passed = False
        
        return all_passed
    
    # ===== Docker Tests =====
    
    def test_docker_installed(self) -> bool:
        """Test Docker is installed"""
        self.print_header("Docker Environment")
        
        try:
            result = subprocess.run(
                ['docker', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            passed = result.returncode == 0
            version = result.stdout.strip() if passed else "Not found"
            self.print_test("Docker installed", passed, version)
            return passed
        except FileNotFoundError:
            self.print_test("Docker installed", False, "Docker not found")
            return False
        except Exception as e:
            self.print_test("Docker installed", False, str(e))
            return False
    
    def test_docker_running(self) -> bool:
        """Test Docker daemon is running"""
        try:
            result = subprocess.run(
                ['docker', 'info'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            passed = result.returncode == 0
            self.print_test("Docker daemon running", passed, 
                          "Active" if passed else "Not running")
            return passed
        except Exception as e:
            self.print_test("Docker daemon running", False, str(e))
            return False
    
    def test_docker_compose_installed(self) -> bool:
        """Test docker-compose is installed"""
        try:
            result = subprocess.run(
                ['docker-compose', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            passed = result.returncode == 0
            version = result.stdout.strip() if passed else "Not found"
            self.print_test("docker-compose installed", passed, version)
            return passed
        except FileNotFoundError:
            self.print_test("docker-compose installed", False, "Not found")
            return False
        except Exception as e:
            self.print_test("docker-compose installed", False, str(e))
            return False
    
    def test_docker_compose_syntax(self) -> bool:
        """Test docker-compose.yml syntax"""
        compose_path = self.project_root / 'docker-compose.yml'
        
        if not compose_path.exists():
            self.print_test("docker-compose.yml syntax", False, "File not found")
            return False
        
        try:
            result = subprocess.run(
                ['docker-compose', '-f', str(compose_path), 'config'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            passed = result.returncode == 0
            self.print_test("docker-compose.yml syntax", passed, 
                          "Valid YAML" if passed else "Syntax error")
            return passed
        except Exception as e:
            self.print_test("docker-compose.yml syntax", False, str(e))
            return False
    
    # ===== Strategy Tests =====
    
    def test_strategies_directory(self) -> bool:
        """Test strategies directory exists"""
        self.print_header("Strategy Configuration")
        
        strategies_dir = Path.home() / '.config' / 'fabric' / 'strategies'
        passed = strategies_dir.exists() and strategies_dir.is_dir()
        self.print_test("Strategies directory exists", passed, 
                      str(strategies_dir))
        return passed
    
    def test_strategy_files(self) -> bool:
        """Test strategy files exist"""
        strategies_dir = Path.home() / '.config' / 'fabric' / 'strategies'
        
        if not strategies_dir.exists():
            self.print_test("Strategy files present", False, 
                          "Strategies dir not found")
            return False
        
        strategy_files = list(strategies_dir.glob('*.json'))
        passed = len(strategy_files) > 0
        self.print_test("Strategy files present", passed, 
                      f"Found {len(strategy_files)} strategies")
        return passed
    
    def test_strategy_json_format(self) -> bool:
        """Test strategy JSON files are valid"""
        strategies_dir = Path.home() / '.config' / 'fabric' / 'strategies'
        
        if not strategies_dir.exists():
            self.print_test("Strategy JSON validation", True, 
                          "Strategies not installed (optional)")
            return True
        
        strategy_files = list(strategies_dir.glob('*.json'))
        all_passed = True
        valid_count = 0
        
        for strategy_file in strategy_files[:5]:  # Test first 5
            try:
                with open(strategy_file, 'r') as f:
                    data = json.load(f)
                    # Basic structure check
                    has_name = 'name' in data
                    has_description = 'description' in data
                    
                    if has_name and has_description:
                        valid_count += 1
            except Exception:
                all_passed = False
        
        self.print_test("Strategy JSON format", all_passed, 
                      f"{valid_count} valid strategies")
        return all_passed
    
    def test_expected_strategies(self) -> bool:
        """Test expected strategies are present"""
        expected = ['cot', 'tot', 'standard', 'reflexion']
        strategies_dir = Path.home() / '.config' / 'fabric' / 'strategies'
        
        if not strategies_dir.exists():
            self.print_test("Expected strategies", True, 
                          "Strategies not installed (optional)")
            return True
        
        found = []
        for strategy_name in expected:
            strategy_file = strategies_dir / f"{strategy_name}.json"
            if strategy_file.exists():
                found.append(strategy_name)
        
        passed = len(found) >= 2  # At least 2 strategies
        self.print_test("Expected strategies", passed, 
                      f"Found: {', '.join(found)}")
        return passed
    
    # ===== Fabric CLI Tests =====
    
    def test_fabric_installed(self) -> bool:
        """Test Fabric CLI is installed"""
        self.print_header("Fabric CLI")
        
        try:
            result = subprocess.run(
                ['which', 'fabric'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            passed = result.returncode == 0
            path = result.stdout.strip() if passed else "Not found"
            self.print_test("Fabric CLI installed", passed, path)
            return passed
        except Exception as e:
            self.print_test("Fabric CLI installed", False, str(e))
            return False
    
    def test_fabric_version(self) -> bool:
        """Test Fabric version"""
        try:
            result = subprocess.run(
                ['fabric', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                version = result.stdout.strip()
                passed = 'fabric' in version.lower() or 'version' in version.lower()
                self.print_test("Fabric version", passed, version)
                return passed
            else:
                self.print_test("Fabric version", False, "Version command failed")
                return False
        except Exception as e:
            self.print_test("Fabric version", False, str(e))
            return False
    
    def test_fabric_config_dir(self) -> bool:
        """Test Fabric config directory exists"""
        config_dir = Path.home() / '.config' / 'fabric'
        passed = config_dir.exists() and config_dir.is_dir()
        self.print_test("Fabric config directory", passed, 
                      str(config_dir))
        return passed
    
    def test_fabric_patterns_dir(self) -> bool:
        """Test Fabric patterns directory exists"""
        patterns_dir = Path.home() / '.config' / 'fabric' / 'patterns'
        passed = patterns_dir.exists() and patterns_dir.is_dir()
        
        if passed:
            pattern_count = len(list(patterns_dir.iterdir()))
            self.print_test("Fabric patterns directory", True, 
                          f"{pattern_count} patterns")
        else:
            self.print_test("Fabric patterns directory", False, "Not found")
        
        return passed
    
    # ===== Shell Tests =====
    
    def test_shell_completions(self) -> bool:
        """Test shell completions are installed"""
        self.print_header("Shell Configuration")
        
        # Check for Zsh completions
        zsh_completion = Path.home() / '.zfunc' / '_fabric'
        if zsh_completion.exists():
            self.print_test("Zsh completions", True, str(zsh_completion))
            return True
        
        # Check alternative location
        zsh_alt = Path.home() / '.zsh' / 'completions' / '_fabric'
        if zsh_alt.exists():
            self.print_test("Zsh completions", True, str(zsh_alt))
            return True
        
        self.print_test("Zsh completions", False, "Not installed")
        return False
    
    def test_zshrc_config(self) -> bool:
        """Test .zshrc has completion config"""
        zshrc = Path.home() / '.zshrc'
        
        if not zshrc.exists():
            self.print_test(".zshrc completion config", False, "File not found")
            return False
        
        try:
            with open(zshrc, 'r') as f:
                content = f.read()
                has_fpath = 'fpath=' in content and 'compinit' in content
                
                self.print_test(".zshrc completion config", has_fpath, 
                              "Configured" if has_fpath else "Not configured")
                return has_fpath
        except Exception as e:
            self.print_test(".zshrc completion config", False, str(e))
            return False
    
    # ===== Test Scripts =====
    
    def test_test_scripts_exist(self) -> bool:
        """Test that test scripts exist"""
        self.print_header("Test Infrastructure")
        
        test_scripts = [
            'test_fabric_setup.py',
            'test_smoke.py',
            'test_api_integration.py',
            'test_unit.py',
        ]
        
        tests_dir = Path(__file__).parent
        all_passed = True
        
        for script in test_scripts:
            path = tests_dir / script
            passed = path.exists()
            self.print_test(f"{script} exists", passed, 
                          str(path) if passed else "Not found")
            if not passed:
                all_passed = False
        
        return all_passed
    
    def test_test_scripts_executable(self) -> bool:
        """Test that test scripts are executable"""
        test_scripts = [
            'test_fabric_setup.py',
            'test_smoke.py',
            'test_api_integration.py',
        ]
        
        tests_dir = Path(__file__).parent
        all_passed = True
        
        for script in test_scripts:
            path = tests_dir / script
            if path.exists():
                passed = os.access(path, os.X_OK)
                self.print_test(f"{script} executable", passed, 
                              "Executable" if passed else "Not executable")
                if not passed:
                    all_passed = False
        
        return all_passed
    
    # ===== Build Scripts =====
    
    def test_build_script_exists(self) -> bool:
        """Test build.sh exists"""
        self.print_header("Build Scripts")
        
        build_script = self.project_root / 'build.sh'
        passed = build_script.exists()
        self.print_test("build.sh exists", passed, 
                      str(build_script) if passed else "Not found")
        return passed
    
    def test_start_script_exists(self) -> bool:
        """Test start-fabric.sh exists"""
        start_script = self.project_root / 'start-fabric.sh'
        passed = start_script.exists()
        self.print_test("start-fabric.sh exists", passed, 
                      str(start_script) if passed else "Not found")
        return passed
    
    # ===== Summary =====
    
    def print_summary(self):
        """Print test summary"""
        self.print_header("Unit Test Summary")
        
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
        
        print(f"\n{BLUE}{'='*60}{NC}")
        if failed == 0:
            print(f"{GREEN}{'🎉 ALL UNIT TESTS PASSED! 🎉':^60}{NC}")
        else:
            print(f"{YELLOW}{'⚠️  SOME TESTS FAILED':^60}{NC}")
        print(f"{BLUE}{'='*60}{NC}")
        
        return failed == 0


def run_unit_tests():
    """Run all unit tests"""
    suite = FabricUnitTests()
    
    print(f"{BLUE}{'='*60}{NC}")
    print(f"{BLUE}{'Fabric Unit Tests':^60}{NC}")
    print(f"{BLUE}{'='*60}{NC}")
    
    # Environment tests
    suite.test_env_file_exists()
    suite.test_load_env_file()
    suite.test_required_api_keys()
    suite.test_api_key_formats()
    suite.test_default_config()
    
    # File structure tests
    suite.test_dockerfile_existence()
    suite.test_dockerfile_syntax()
    suite.test_documentation_files()
    
    # Docker tests
    suite.test_docker_installed()
    suite.test_docker_running()
    suite.test_docker_compose_installed()
    suite.test_docker_compose_syntax()
    
    # Strategy tests
    suite.test_strategies_directory()
    suite.test_strategy_files()
    suite.test_strategy_json_format()
    suite.test_expected_strategies()
    
    # Fabric CLI tests
    suite.test_fabric_installed()
    suite.test_fabric_version()
    suite.test_fabric_config_dir()
    suite.test_fabric_patterns_dir()
    
    # Shell tests
    suite.test_shell_completions()
    suite.test_zshrc_config()
    
    # Test infrastructure
    suite.test_test_scripts_exist()
    suite.test_test_scripts_executable()
    
    # Build scripts
    suite.test_build_script_exists()
    suite.test_start_script_exists()
    
    # Print summary
    all_passed = suite.print_summary()
    
    return all_passed


if __name__ == '__main__':
    success = run_unit_tests()
    sys.exit(0 if success else 1)
