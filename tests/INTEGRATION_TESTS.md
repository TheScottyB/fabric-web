# Fabric Integration Tests

Tests for real-world Fabric workflows and integrations.

## YouTube Transcript Integration

**Workflow:** `yt --transcript 'URL' | fabric -sp pattern`

This tests the complete pipeline:
1. Fetch YouTube video transcript
2. Pipe to Fabric
3. Apply pattern (summarize, extract_wisdom, etc.)
4. Return processed result

### Test Coverage

The smoke test includes a YouTube integration test that validates:
- ✅ API accepts transcript-style input
- ✅ Pattern processes longer text correctly  
- ✅ Response is generated successfully
- ✅ End-to-end pipeline works

### Manual Testing

Once services are running, test the full workflow:

```bash
# Example 1: Summarize a video transcript
yt --transcript 'https://youtu.be/VJyGDeshXfM' | fabric -sp summarize

# Example 2: Extract wisdom from a talk
yt --transcript 'https://youtu.be/dQw4w9WgXcQ' | fabric -sp extract_wisdom

# Example 3: Create 5-sentence summary
yt --transcript 'YOUR_VIDEO_URL' | fabric -rp create_5_sentence_summary

# Example 4: Summarize YouTube comments
fabric -y 'https://youtu.be/VJyGDeshXfM' --comments | fabric -rp summarize

# Example 5: Extract sentiment from comments
fabric -y 'YOUR_VIDEO_URL' --comments | fabric -rp analyze_claims
```

### Warp Drive Workflows

These workflows are available in Warp:

#### 1. Fetch transcript and create summary
```bash
yt --transcript '{{video_url}}' | fabric -sp {{summary_type}}
```
**Default:** `summarize` pattern  
**Arguments:**
- `video_url`: YouTube URL
- `summary_type`: Pattern name (summarize, extract_wisdom, etc.)

#### 2. Retrieve and summarize YouTube transcript
```bash
yt --transcript '{{video_url}}' | fabric -rp {{summary_type}}
```
**Default:** `create_5_sentence_summary` pattern  
**Arguments:**
- `video_url`: YouTube URL
- `summary_type`: Pattern name

#### 3. Extract wisdom from YouTube
```bash
yt --transcript '{{video_url}}' | fabric -rp {{summary_type}}
```
**Default:** `extract_wisdom` pattern  
**Arguments:**
- `video_url`: YouTube URL
- `summary_type`: Pattern name

#### 4. Fetch YouTube comments and generate summary
```bash
fabric -y '{{video_url}}' --comments | fabric -rp {{summary_action}}
```
**Default:** `summarize` pattern  
**Arguments:**
- `video_url`: YouTube URL
- `summary_action`: Pattern name (summarize, analyze_claims, etc.)

**Use cases:**
- Aggregate viewer feedback
- Analyze sentiment
- Extract common themes
- Identify trending topics

### Pattern Options

Common patterns for video transcripts:
- **summarize** - General summary
- **extract_wisdom** - Key insights and lessons
- **create_5_sentence_summary** - Brief 5-sentence overview
- **extract_main_idea** - Core concept
- **create_keynote** - Presentation outline
- **explain_like_im_5** - Simplified explanation

### Prerequisites

**For CLI usage:**
```bash
# Install YouTube transcript tool (if not already installed)
pip install youtube-transcript-api

# Or if using fabric's yt command
fabric --setup
# Select YouTube integration during setup
```

**For Docker usage:**
The API endpoint accepts transcript text directly, so you can:
1. Get transcript via API or CLI
2. Send to Fabric API with pattern
3. Receive processed result

### API Integration Example

```python
import requests

# Step 1: Get YouTube transcript (using your preferred method)
transcript = "Your video transcript text here..."

# Step 2: Send to Fabric with pattern
response = requests.post(
    'http://localhost:8080/chat',
    json={
        'input': transcript,
        'pattern': 'summarize',
        'stream': False
    }
)

summary = response.text
print(summary)
```

### Testing with Docker

```bash
# Start services
cd ~/workspace/fabric-web
docker-compose up -d

# Run smoke tests (includes YT integration test)
cd tests
python3 test_smoke.py

# Test manually via API
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Long transcript text here...",
    "pattern": "summarize",
    "stream": false
  }'
```

### Automated Testing

The smoke test suite automatically validates:

```bash
cd ~/workspace/fabric-web/tests
python3 test_smoke.py
```

Look for:
```
======================================================================
                    YouTube Integration Test
======================================================================

✓ PASS - YT transcript -> Fabric pattern (2.34s)
       Pipeline works: 156 char response
```

### Troubleshooting

**"yt command not found"**
- Install: `pip install youtube-transcript-api`
- Or use Fabric's setup: `fabric --setup`

**"Pattern not found"**
- List available patterns: `fabric --listpatterns`
- Update patterns: `fabric --updatepatterns`

**API timeout**
- Transcripts can be long, increase timeout
- Consider using streaming mode: `"stream": true`

**No API key**
- Check `.env` has at least one AI provider key configured
- Default is Groq (fast, free tier available)

### Performance Notes

**Expected timing:**
- Short video (5 min): ~3-10 seconds
- Medium video (30 min): ~10-30 seconds  
- Long video (1+ hour): ~30-60+ seconds

**Model selection affects speed:**
- **Groq** (default): Fastest (llama-3.3-70b)
- **Anthropic**: Fast (Claude Sonnet)
- **OpenAI**: Medium (GPT-4)
- **Gemini**: Variable

### Example Output

**Input:** YouTube transcript about AI (1000 words)  
**Pattern:** `summarize`  
**Output:**
```
The video discusses the transformative impact of artificial 
intelligence on software development, highlighting key trends 
in automated code generation, testing, and deployment. It 
explores how AI tools are augmenting developer productivity 
while raising important questions about code quality and 
security implications.
```

## YouTube Comments Integration

**Workflow:** `fabric -y 'URL' --comments | fabric -rp pattern`

This tests the complete comments pipeline:
1. Fetch YouTube video comments
2. Pipe to Fabric
3. Apply pattern (summarize, analyze_claims, etc.)
4. Return aggregated insights

### Test Coverage

The smoke test includes a YouTube comments test that validates:
- ✅ API accepts comment-style input
- ✅ Pattern aggregates multiple comments
- ✅ Response synthesizes viewer feedback
- ✅ End-to-end comments pipeline works

### Use Cases

**Aggregate feedback:**
```bash
fabric -y 'https://youtu.be/VIDEO_ID' --comments | fabric -rp summarize
```

**Analyze sentiment:**
```bash
fabric -y 'https://youtu.be/VIDEO_ID' --comments | fabric -rp analyze_claims
```

**Extract common themes:**
```bash
fabric -y 'https://youtu.be/VIDEO_ID' --comments | fabric -rp extract_patterns
```

**Identify questions:**
```bash
fabric -y 'https://youtu.be/VIDEO_ID' --comments | fabric -rp extract_questions
```

### Pattern Recommendations for Comments

- **summarize** - Overall comment sentiment and themes
- **analyze_claims** - Fact-check common assertions
- **extract_patterns** - Identify recurring topics
- **extract_questions** - Find unanswered questions
- **rate_content** - Aggregate ratings/opinions

### Example Output

**Input:** 500 YouTube comments on AI tutorial  
**Pattern:** `summarize`  
**Output:**
```
Viewers overwhelmingly praised the tutorial's clarity and 
practical examples. Common themes included appreciation for 
the step-by-step approach and requests for more advanced 
content. Several commenters noted this was the best explanation 
they'd found. A few users requested additional coverage of 
deployment strategies.
```

## Other Integrations

### CLI Piping
Any command can pipe to Fabric:
```bash
cat document.txt | fabric -sp summarize
curl https://example.com/article | fabric -sp extract_wisdom
echo "Explain quantum computing" | fabric -sp explain_like_im_5
```

### File Input
```bash
fabric -p summarize < long_document.txt
cat code.py | fabric -sp explain_code
```

### API Direct
All integrations work via API too:
```bash
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d @request.json
```

## Adding New Integration Tests

To add a new integration test to `test_smoke.py`:

```python
def test_your_integration(self) -> bool:
    """Test your integration workflow"""
    self.print_header("Your Integration Test")
    
    try:
        start = time.time()
        
        # Your test logic here
        # ...
        
        duration = time.time() - start
        self.print_test("Test name", True, "Message", duration)
        return True
    except Exception as e:
        self.print_test("Test name", False, str(e))
        return False
```

Then add to `run_smoke_tests()`:
```python
suite.test_your_integration()
```
