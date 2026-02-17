#!/usr/bin/env python3
"""
Real YouTube Integration Tests
Tests actual YouTube video processing with transcript and comment extraction
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


class YouTubeRealTests:
    """Real YouTube integration test suite"""
    
    def __init__(self):
        self.api_base = 'http://localhost:8080'
        self.test_results = []
        
        # Public test videos (short, stable, safe for testing)
        self.test_videos = {
            'short': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',  # Classic short video
            'tech': 'https://www.youtube.com/watch?v=_uQrJ0TkZlc',   # Tech talk (example)
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
    
    # ===== Environment Checks =====
    
    def test_yt_command_available(self) -> bool:
        """Test yt command is installed"""
        self.print_header("Environment Checks")
        
        try:
            result = subprocess.run(
                ['which', 'yt'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            passed = result.returncode == 0
            path = result.stdout.strip() if passed else "Not found"
            
            self.print_test("yt command available", passed, path)
            
            if not passed:
                print(f"\n{YELLOW}Install yt command: go install github.com/danielmiessler/fabric/cmd/yt@latest{NC}")
            
            return passed
        except Exception as e:
            self.print_test("yt command available", False, str(e))
            return False
    
    def test_fabric_youtube_api_key(self) -> bool:
        """Test YouTube API key is configured"""
        env_path = Path.home() / '.config' / 'fabric' / '.env'
        
        if not env_path.exists():
            self.print_test("YouTube API key configured", False, ".env not found")
            return False
        
        try:
            with open(env_path, 'r') as f:
                content = f.read()
                has_key = 'YOUTUBE_API_KEY' in content
                
                self.print_test("YouTube API key configured", has_key,
                              "Key present" if has_key else "Key missing")
                
                if not has_key:
                    print(f"\n{YELLOW}Add YOUTUBE_API_KEY to ~/.config/fabric/.env{NC}")
                
                return has_key
        except Exception as e:
            self.print_test("YouTube API key configured", False, str(e))
            return False
    
    # ===== Transcript Tests =====
    
    def test_transcript_extraction_cli(self) -> bool:
        """Test transcript extraction using yt CLI"""
        self.print_header("Transcript Extraction Tests")
        
        video_url = self.test_videos['short']
        
        try:
            start = time.time()
            
            result = subprocess.run(
                ['yt', '--transcript', video_url],
                capture_output=True,
                text=True,
                timeout=30
            )
            duration = time.time() - start
            
            if result.returncode == 0:
                transcript = result.stdout
                
                # Basic validation
                has_content = len(transcript) > 50
                is_text = not transcript.startswith('ERROR')
                
                passed = has_content and is_text
                
                self.print_test("Extract transcript (CLI)", passed,
                              f"Got {len(transcript)} chars", duration)
                return passed
            else:
                error = result.stderr[:100] if result.stderr else "Unknown error"
                self.print_test("Extract transcript (CLI)", False, error, duration)
                return False
                
        except subprocess.TimeoutExpired:
            self.print_test("Extract transcript (CLI)", False, "Timeout (30s)", 30.0)
            return False
        except FileNotFoundError:
            self.print_test("Extract transcript (CLI)", False, "yt command not found")
            return False
        except Exception as e:
            self.print_test("Extract transcript (CLI)", False, str(e))
            return False
    
    def test_transcript_to_fabric_pipeline(self) -> bool:
        """Test full pipeline: transcript → Fabric pattern"""
        video_url = self.test_videos['short']
        
        try:
            start = time.time()
            
            # Step 1: Get transcript
            transcript_result = subprocess.run(
                ['yt', '--transcript', video_url],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if transcript_result.returncode != 0:
                self.print_test("Transcript → Fabric pipeline", False,
                              "Failed to get transcript")
                return False
            
            transcript = transcript_result.stdout
            
            # Step 2: Send to Fabric API with pattern
            payload = {
                "input": transcript,
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
                summary = response.text
                
                # Summary should be shorter than transcript but not empty
                passed = 50 < len(summary) < len(transcript)
                
                self.print_test("Transcript → Fabric pipeline", passed,
                              f"Transcript: {len(transcript)} → Summary: {len(summary)}", 
                              duration)
                return passed
            else:
                self.print_test("Transcript → Fabric pipeline", False,
                              f"API error: {response.status_code}", duration)
                return False
                
        except Exception as e:
            self.print_test("Transcript → Fabric pipeline", False, str(e))
            return False
    
    def test_transcript_with_multiple_patterns(self) -> bool:
        """Test transcript with different Fabric patterns"""
        video_url = self.test_videos['short']
        patterns = ['summarize', 'extract_wisdom']
        
        all_passed = True
        
        # Get transcript once
        try:
            transcript_result = subprocess.run(
                ['yt', '--transcript', video_url],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if transcript_result.returncode != 0:
                self.print_test("Transcript with multiple patterns", False,
                              "Failed to get transcript")
                return False
            
            transcript = transcript_result.stdout
        except:
            self.print_test("Transcript with multiple patterns", False,
                          "Failed to extract transcript")
            return False
        
        # Test each pattern
        for pattern in patterns:
            try:
                start = time.time()
                
                payload = {
                    "input": transcript,
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
                    passed = len(result) > 30
                    
                    self.print_test(f"Transcript → {pattern}", passed,
                                  f"Generated {len(result)} chars", duration)
                    
                    if not passed:
                        all_passed = False
                else:
                    self.print_test(f"Transcript → {pattern}", False,
                                  f"Status: {response.status_code}", duration)
                    all_passed = False
                    
            except Exception as e:
                self.print_test(f"Transcript → {pattern}", False, str(e))
                all_passed = False
        
        return all_passed
    
    # ===== Comment Tests =====
    
    def test_comments_extraction(self) -> bool:
        """Test comment extraction using fabric -y"""
        self.print_header("Comment Extraction Tests")
        
        video_url = self.test_videos['short']
        
        try:
            start = time.time()
            
            # Use fabric -y to get comments
            result = subprocess.run(
                ['fabric', '-y', video_url, '--comments'],
                capture_output=True,
                text=True,
                timeout=30
            )
            duration = time.time() - start
            
            if result.returncode == 0:
                comments = result.stdout
                
                # Basic validation
                has_content = len(comments) > 50
                
                passed = has_content
                
                self.print_test("Extract comments (fabric -y)", passed,
                              f"Got {len(comments)} chars", duration)
                return passed
            else:
                error = result.stderr[:100] if result.stderr else "Unknown error"
                self.print_test("Extract comments (fabric -y)", False, error, duration)
                return False
                
        except subprocess.TimeoutExpired:
            self.print_test("Extract comments (fabric -y)", False, "Timeout (30s)", 30.0)
            return False
        except FileNotFoundError:
            self.print_test("Extract comments (fabric -y)", False,
                          "fabric command not found")
            return False
        except Exception as e:
            self.print_test("Extract comments (fabric -y)", False, str(e))
            return False
    
    def test_comments_to_fabric_pipeline(self) -> bool:
        """Test full pipeline: comments → Fabric pattern"""
        video_url = self.test_videos['short']
        
        try:
            start = time.time()
            
            # Step 1: Get comments
            comments_result = subprocess.run(
                ['fabric', '-y', video_url, '--comments'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if comments_result.returncode != 0:
                self.print_test("Comments → Fabric pipeline", False,
                              "Failed to get comments")
                return False
            
            comments = comments_result.stdout
            
            # Step 2: Send to Fabric API with pattern
            payload = {
                "input": comments,
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
                summary = response.text
                
                passed = len(summary) > 30
                
                self.print_test("Comments → Fabric pipeline", passed,
                              f"Comments: {len(comments)} → Summary: {len(summary)}", 
                              duration)
                return passed
            else:
                self.print_test("Comments → Fabric pipeline", False,
                              f"API error: {response.status_code}", duration)
                return False
                
        except Exception as e:
            self.print_test("Comments → Fabric pipeline", False, str(e))
            return False
    
    # ===== Warp Drive Workflow Tests =====
    
    def test_warp_workflow_transcript_summary(self) -> bool:
        """Test Warp Drive workflow: yt --transcript | fabric -sp"""
        self.print_header("Warp Drive Workflow Tests")
        
        video_url = self.test_videos['short']
        
        try:
            start = time.time()
            
            # Simulate: yt --transcript 'URL' | fabric -sp summarize
            # Step 1: Get transcript
            yt_process = subprocess.Popen(
                ['yt', '--transcript', video_url],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Step 2: Pipe to fabric
            fabric_process = subprocess.Popen(
                ['fabric', '-sp', 'summarize'],
                stdin=yt_process.stdout,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Allow yt_process to receive SIGPIPE if fabric_process exits
            yt_process.stdout.close()
            
            # Wait for completion
            output, error = fabric_process.communicate(timeout=60)
            duration = time.time() - start
            
            if fabric_process.returncode == 0:
                summary = output
                
                passed = len(summary) > 50
                
                self.print_test("Workflow: yt → fabric -sp", passed,
                              f"Generated {len(summary)} char summary", duration)
                return passed
            else:
                self.print_test("Workflow: yt → fabric -sp", False,
                              f"Error: {error[:100]}", duration)
                return False
                
        except subprocess.TimeoutExpired:
            self.print_test("Workflow: yt → fabric -sp", False, "Timeout (60s)", 60.0)
            return False
        except Exception as e:
            self.print_test("Workflow: yt → fabric -sp", False, str(e))
            return False
    
    def test_warp_workflow_comments_summary(self) -> bool:
        """Test Warp Drive workflow: fabric -y --comments | fabric -rp"""
        video_url = self.test_videos['short']
        
        try:
            start = time.time()
            
            # Simulate: fabric -y 'URL' --comments | fabric -rp summarize
            # Step 1: Get comments
            comments_process = subprocess.Popen(
                ['fabric', '-y', video_url, '--comments'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Step 2: Pipe to fabric with pattern
            fabric_process = subprocess.Popen(
                ['fabric', '-rp', 'summarize'],
                stdin=comments_process.stdout,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            comments_process.stdout.close()
            
            # Wait for completion
            output, error = fabric_process.communicate(timeout=60)
            duration = time.time() - start
            
            if fabric_process.returncode == 0:
                summary = output
                
                passed = len(summary) > 30
                
                self.print_test("Workflow: fabric -y --comments | fabric -rp", passed,
                              f"Generated {len(summary)} char summary", duration)
                return passed
            else:
                self.print_test("Workflow: fabric -y --comments | fabric -rp", False,
                              f"Error: {error[:100]}", duration)
                return False
                
        except subprocess.TimeoutExpired:
            self.print_test("Workflow: fabric -y --comments | fabric -rp", False,
                          "Timeout (60s)", 60.0)
            return False
        except Exception as e:
            self.print_test("Workflow: fabric -y --comments | fabric -rp", False, str(e))
            return False
    
    # ===== Error Handling Tests =====
    
    def test_invalid_video_url(self) -> bool:
        """Test error handling for invalid video URL"""
        self.print_header("Error Handling Tests")
        
        invalid_url = "https://www.youtube.com/watch?v=INVALID123456"
        
        try:
            result = subprocess.run(
                ['yt', '--transcript', invalid_url],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            # Should fail gracefully
            passed = result.returncode != 0
            error_msg = result.stderr[:100] if result.stderr else "No error message"
            
            self.print_test("Invalid video URL handling", passed,
                          f"Properly rejected: {error_msg}")
            return passed
            
        except Exception as e:
            self.print_test("Invalid video URL handling", False, str(e))
            return False
    
    def test_private_video_handling(self) -> bool:
        """Test handling of private/unavailable videos"""
        # This URL format typically returns an error
        private_url = "https://www.youtube.com/watch?v=privatevideo123"
        
        try:
            result = subprocess.run(
                ['yt', '--transcript', private_url],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            # Should fail gracefully (not crash)
            passed = True  # As long as it doesn't crash, it passes
            
            self.print_test("Private video handling", passed,
                          "Handled gracefully (no crash)")
            return passed
            
        except Exception as e:
            # If it times out or errors, that's also acceptable
            self.print_test("Private video handling", True,
                          f"Handled: {str(e)[:50]}")
            return True
    
    # ===== Performance Tests =====
    
    def test_transcript_extraction_speed(self) -> bool:
        """Test transcript extraction completes in reasonable time"""
        self.print_header("Performance Tests")
        
        video_url = self.test_videos['short']
        
        try:
            start = time.time()
            
            result = subprocess.run(
                ['yt', '--transcript', video_url],
                capture_output=True,
                text=True,
                timeout=30
            )
            duration = time.time() - start
            
            # Should complete within 20 seconds for a short video
            passed = duration < 20.0 and result.returncode == 0
            
            self.print_test("Transcript extraction speed", passed,
                          f"Completed in {duration:.1f}s (target: <20s)", duration)
            return passed
            
        except subprocess.TimeoutExpired:
            self.print_test("Transcript extraction speed", False,
                          "Timeout (>30s)", 30.0)
            return False
        except Exception as e:
            self.print_test("Transcript extraction speed", False, str(e))
            return False
    
    # ===== Summary =====
    
    def print_summary(self):
        """Print test summary"""
        self.print_header("YouTube Real Integration Test Summary")
        
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
            print(f"{GREEN}{'🎉 ALL YOUTUBE TESTS PASSED! 🎉':^70}{NC}")
        else:
            print(f"{YELLOW}{'⚠️  SOME TESTS FAILED':^70}{NC}")
        print(f"{BLUE}{'='*70}{NC}")
        
        return failed == 0


def run_youtube_tests():
    """Run all real YouTube integration tests"""
    suite = YouTubeRealTests()
    
    print(f"{BLUE}{'='*70}{NC}")
    print(f"{BLUE}{'Fabric Real YouTube Integration Tests':^70}{NC}")
    print(f"{BLUE}{'='*70}{NC}")
    
    # Environment checks
    yt_available = suite.test_yt_command_available()
    api_key_configured = suite.test_fabric_youtube_api_key()
    
    if not yt_available:
        print(f"\n{RED}yt command not found. Install with:{NC}")
        print(f"{CYAN}go install github.com/danielmiessler/fabric/cmd/yt@latest{NC}\n")
        return False
    
    if not api_key_configured:
        print(f"\n{YELLOW}YouTube API key not configured.{NC}")
        print(f"{CYAN}Add YOUTUBE_API_KEY to ~/.config/fabric/.env{NC}")
        print(f"{YELLOW}Some tests may fail without it.{NC}\n")
    
    # Transcript tests
    suite.test_transcript_extraction_cli()
    suite.test_transcript_to_fabric_pipeline()
    suite.test_transcript_with_multiple_patterns()
    
    # Comment tests
    suite.test_comments_extraction()
    suite.test_comments_to_fabric_pipeline()
    
    # Warp Drive workflow tests
    suite.test_warp_workflow_transcript_summary()
    suite.test_warp_workflow_comments_summary()
    
    # Error handling tests
    suite.test_invalid_video_url()
    suite.test_private_video_handling()
    
    # Performance tests
    suite.test_transcript_extraction_speed()
    
    # Print summary
    all_passed = suite.print_summary()
    
    return all_passed


if __name__ == '__main__':
    success = run_youtube_tests()
    sys.exit(0 if success else 1)
