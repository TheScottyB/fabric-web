#!/usr/bin/env python3
"""
Infisical Integration Tests for Fabric
Tests Infisical CLI installation, authentication, and secrets export.
"""

import os
import sys
import subprocess
import json
from pathlib import Path

# Color codes
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
CYAN = '\033[0;36m'
NC = '\033[0m'


class InfisicalTests:
    """Test suite for Infisical secrets management integration"""
    
    def __init__(self):
        self.project_dir = Path(__file__).parent.parent
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
            print(f"       {message}")
        self.test_results.append((name, passed, message))
    
    def print_info(self, name: str, message: str = ""):
        """Print informational test (always passes)"""
        print(f"{YELLOW}ℹ INFO{NC} - {name}")
        if message:
            print(f"       {message}")
        self.test_results.append((name, True, message))
    
    def run_command(self, cmd: list, timeout: int = 30) -> tuple:
        """Run a command and return stdout, stderr, returncode"""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(self.project_dir)
            )
            return result.stdout, result.stderr, result.returncode
        except subprocess.TimeoutExpired:
            return "", "Command timed out", 1
        except FileNotFoundError:
            return "", "Command not found", 127
        except Exception as e:
            return "", str(e), 1
    
    def test_cli_installed(self) -> bool:
        """Test that Infisical CLI is installed"""
        self.print_header("Infisical CLI Installation")
        
        stdout, stderr, rc = self.run_command(['infisical', '--version'])
        
        if rc == 0:
            version = stdout.strip() or stderr.strip()
            self.print_test("Infisical CLI installed", True, f"Version: {version}")
            return True
        elif rc == 127:
            self.print_test("Infisical CLI installed", False, 
                          "Not installed. Run: brew install infisical/get-cli/infisical")
            return False
        else:
            self.print_test("Infisical CLI installed", False, stderr[:100])
            return False
    
    def test_cli_help(self) -> bool:
        """Test that CLI help works (basic functionality)"""
        stdout, stderr, rc = self.run_command(['infisical', '--help'])
        
        if rc == 0 and ('export' in stdout or 'run' in stdout):
            self.print_test("CLI help available", True, "Commands: export, run, login")
            return True
        else:
            self.print_test("CLI help available", False, "Help command failed")
            return False
    
    def test_project_scripts(self) -> bool:
        """Test that package.json has Infisical scripts"""
        self.print_header("Project Integration")
        
        package_json = self.project_dir / 'package.json'
        
        if not package_json.exists():
            self.print_test("package.json exists", False, "File not found")
            return False
        
        try:
            with open(package_json) as f:
                pkg = json.load(f)
            
            scripts = pkg.get('scripts', {})
            
            # Check for Infisical-related scripts
            infisical_scripts = {
                'dev:infisical': 'Development with secrets',
                'build:infisical': 'Build with secrets', 
                'secrets:init': 'Initialize Infisical project',
                'env:pull:dev': 'Pull dev environment',
                'env:pull:prod': 'Pull prod environment'
            }
            
            all_found = True
            for script, desc in infisical_scripts.items():
                if script in scripts:
                    self.print_test(f"Script: {script}", True, desc)
                else:
                    self.print_test(f"Script: {script}", False, "Not found in package.json")
                    all_found = False
            
            return all_found
            
        except json.JSONDecodeError as e:
            self.print_test("package.json valid JSON", False, str(e))
            return False
    
    def test_docker_script(self) -> bool:
        """Test that docker-up.sh uses Infisical"""
        docker_script = self.project_dir / 'scripts' / 'docker-up.sh'
        
        if not docker_script.exists():
            self.print_test("docker-up.sh exists", False, "Script not found")
            return False
        
        content = docker_script.read_text()
        
        if 'infisical export' in content:
            self.print_test("docker-up.sh uses Infisical", True, "Exports secrets before Docker start")
            return True
        else:
            self.print_test("docker-up.sh uses Infisical", False, "No infisical export found")
            return False
    
    def test_authentication_status(self) -> bool:
        """Test Infisical authentication status"""
        self.print_header("Authentication Status")
        
        # Check if user is logged in by trying to get user info
        stdout, stderr, rc = self.run_command(['infisical', 'user', 'get'])
        
        if rc == 0:
            self.print_test("Infisical authenticated", True, "User is logged in")
            return True
        else:
            # This is informational - user might not be logged in during CI
            self.print_info("Infisical authenticated", 
                          "Not logged in (run: infisical login)")
            return True  # Don't fail the test
    
    def test_export_dry_run(self) -> bool:
        """Test that export command syntax is valid (without actually exporting)"""
        self.print_header("Export Configuration")
        
        # Test help for export command
        stdout, stderr, rc = self.run_command(['infisical', 'export', '--help'])
        
        if rc == 0:
            self.print_test("Export command available", True, "Supports --env, --format options")
        else:
            self.print_test("Export command available", False, "Export help failed")
            return False
        
        # Check if .infisical.json or infisical.json exists (project config)
        config_files = [
            self.project_dir / '.infisical.json',
            self.project_dir / 'infisical.json'
        ]
        
        config_found = any(f.exists() for f in config_files)
        if config_found:
            self.print_test("Infisical project config", True, "Config file exists")
        else:
            self.print_info("Infisical project config", 
                          "No config file (run: pnpm secrets:init)")
        
        return True
    
    def test_env_validation_script(self) -> bool:
        """Test that environment validation script exists"""
        self.print_header("Environment Validation")
        
        validate_script = self.project_dir / 'scripts' / 'validate-env.mjs'
        
        if validate_script.exists():
            self.print_test("validate-env.mjs exists", True, "Environment validation available")
            
            # Check if it's referenced in docker-up.sh
            docker_script = self.project_dir / 'scripts' / 'docker-up.sh'
            if docker_script.exists():
                content = docker_script.read_text()
                if 'validate-env' in content:
                    self.print_test("Validation in docker-up.sh", True, "Validates before Docker start")
                else:
                    self.print_test("Validation in docker-up.sh", False, "Not integrated")
            
            return True
        else:
            self.print_test("validate-env.mjs exists", False, "Script not found")
            return False
    
    def test_env_file_security(self) -> bool:
        """Test .env file security (if exists)"""
        self.print_header("Security Checks")
        
        env_file = self.project_dir / '.env'
        gitignore = self.project_dir / '.gitignore'
        
        # Check .gitignore includes .env
        if gitignore.exists():
            content = gitignore.read_text()
            if '.env' in content:
                self.print_test(".env in .gitignore", True, "Secrets won't be committed")
            else:
                self.print_test(".env in .gitignore", False, "WARNING: .env might be committed!")
                return False
        
        # Check .env permissions if it exists
        if env_file.exists():
            import stat
            mode = env_file.stat().st_mode
            # Check if group/other readable
            if mode & (stat.S_IRGRP | stat.S_IROTH):
                self.print_info(".env file permissions", 
                              f"Consider: chmod 600 .env (current: {oct(mode)[-3:]})")
            else:
                self.print_test(".env file permissions", True, "Restricted permissions")
        else:
            self.print_info(".env file", "Not present (will be created by infisical export)")
        
        return True
    
    def test_required_secrets_documented(self) -> bool:
        """Test that required secrets are documented"""
        readme = self.project_dir / 'README.md'
        
        if readme.exists():
            content = readme.read_text().lower()
            if 'infisical' in content or 'secret' in content or 'environment' in content:
                self.print_test("Secrets documented", True, "README mentions secrets/environment")
                return True
        
        self.print_info("Secrets documented", "Consider documenting required secrets in README")
        return True
    
    def run_all_tests(self) -> bool:
        """Run all Infisical tests"""
        print(f"\n{CYAN}{'='*60}{NC}")
        print(f"{CYAN}{'Infisical Integration Test Suite':^60}{NC}")
        print(f"{CYAN}{'='*60}{NC}")
        
        # Run tests in order
        self.test_cli_installed()
        self.test_cli_help()
        self.test_project_scripts()
        self.test_docker_script()
        self.test_authentication_status()
        self.test_export_dry_run()
        self.test_env_validation_script()
        self.test_env_file_security()
        self.test_required_secrets_documented()
        
        # Print summary
        self.print_header("Test Summary")
        
        passed = sum(1 for _, p, _ in self.test_results if p)
        failed = sum(1 for _, p, _ in self.test_results if not p)
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {GREEN}{passed}{NC}")
        print(f"Failed: {RED}{failed}{NC}")
        print(f"Success Rate: {100*passed/total:.1f}%")
        
        if failed > 0:
            print(f"\n{RED}Failed Tests:{NC}")
            for name, p, msg in self.test_results:
                if not p:
                    print(f"  - {name}: {msg}")
        
        return failed == 0


def main():
    """Main entry point"""
    tests = InfisicalTests()
    success = tests.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
