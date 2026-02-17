# Fabric Strategies Guide

## Overview

Fabric includes **prompt strategies** that modify how AI models approach problem-solving. Strategies provide structured reasoning patterns for better analysis, code review, planning, and decision-making.

---

## 🚀 Quick Start

### Install Strategies
```bash
# Use fabric -S to install strategies interactively
fabric -S

# Strategies are installed to:
~/.config/fabric/strategies/
```

### List Available Strategies
```bash
# CLI
fabric --liststrategies

# Docker
docker exec fabric-api fabric --liststrategies

# API
curl http://localhost:8080/strategies
```

### Use a Strategy
```bash
# CLI with pattern
echo "Analyze this code" | fabric --strategy cot -p analyze_code

# CLI shorthand
fabric --strategy cot -p analyze_code < input.txt

# Docker
echo "Your text" | docker exec -i fabric-api fabric --strategy tot -p summarize

# API
curl -X POST "http://localhost:8080/patterns/analyze_code/execute?strategy=cot" \
  -H "Content-Type: application/json" \
  -d '{"input": "Your code here"}'
```

---

## 🧠 Available Strategies

### 1. **Chain-of-Thought (cot)**
**Best for:** Step-by-step reasoning, debugging, mathematical problems

**How it works:** Breaks down complex problems into sequential logical steps

**Example:**
```bash
echo "Why does this function return NaN?" | fabric --strategy cot -p explain_code
```

**Use cases:**
- Debugging complex issues
- Mathematical calculations
- Logic-heavy analysis
- Root cause analysis

---

### 2. **Chain-of-Draft (cod)**
**Best for:** Iterative writing, content creation, refining ideas

**How it works:** Creates multiple drafts with minimal notes (≤5 words per step)

**Example:**
```bash
echo "Write a blog post about AI safety" | fabric --strategy cod -p write_essay
```

**Use cases:**
- Blog posts and articles
- Documentation drafting
- Creative writing
- Proposal generation

---

### 3. **Tree-of-Thought (tot)**
**Best for:** Exploring multiple solutions, decision-making, planning

**How it works:** Generates multiple reasoning paths and selects the best one

**Example:**
```bash
echo "Design a scalable microservices architecture" | fabric --strategy tot -p create_design_document
```

**Use cases:**
- Architecture decisions
- Strategic planning
- Complex problem-solving
- Evaluating trade-offs

---

### 4. **Atom-of-Thought (aot)**
**Best for:** Breaking down complex systems, modular analysis

**How it works:** Decomposes problems into smallest independent atomic sub-problems

**Example:**
```bash
echo "Refactor this monolithic application" | fabric --strategy aot -p improve_code
```

**Use cases:**
- System decomposition
- Refactoring planning
- Modular design
- Dependency analysis

---

### 5. **Least-to-Most (ltm)**
**Best for:** Learning paths, incremental improvements, progressive complexity

**How it works:** Solves problems from easiest to hardest sub-problems

**Example:**
```bash
echo "Build a distributed task queue" | fabric --strategy ltm -p create_tutorial
```

**Use cases:**
- Tutorial creation
- Learning roadmaps
- Project planning
- Progressive feature rollouts

---

### 6. **Self-Consistent (self-consistent)**
**Best for:** Validation, consensus-building, reducing errors

**How it works:** Multiple reasoning paths with majority-vote consensus

**Example:**
```bash
echo "Is this security vulnerability critical?" | fabric --strategy self-consistent -p analyze_security
```

**Use cases:**
- Security analysis
- Risk assessment
- Quality validation
- Critical decisions

---

### 7. **Self-Refinement (self-refine)**
**Best for:** Quality improvement, iterative enhancement

**How it works:** Answer → Critique → Refine

**Example:**
```bash
echo "Optimize this SQL query" | fabric --strategy self-refine -p improve_code
```

**Use cases:**
- Code optimization
- Content refinement
- Performance tuning
- Quality enhancement

---

### 8. **Reflexion (reflexion)**
**Best for:** Quick improvements with brief self-critique

**How it works:** Answer → Brief critique → Refined answer

**Example:**
```bash
echo "Review this pull request" | fabric --strategy reflexion -p analyze_code
```

**Use cases:**
- Code reviews
- Quick iterations
- Feedback loops
- Rapid prototyping

---

### 9. **Standard (standard)**
**Best for:** Simple queries, direct answers

**How it works:** Direct answer without explanation or reasoning steps

**Example:**
```bash
echo "Summarize this article" | fabric --strategy standard -p summarize
```

**Use cases:**
- Simple summaries
- Quick answers
- Direct information
- Minimal overhead

---

## 🎯 Strategy Selection Guide

### Choose by Task Type

| Task Type | Recommended Strategy | Alternative |
|-----------|---------------------|-------------|
| **Debug complex code** | `cot` (Chain-of-Thought) | `tot` |
| **Architecture design** | `tot` (Tree-of-Thought) | `aot` |
| **Write documentation** | `cod` (Chain-of-Draft) | `self-refine` |
| **Code review** | `reflexion` | `self-consistent` |
| **Security analysis** | `self-consistent` | `cot` |
| **Refactoring plan** | `aot` (Atom-of-Thought) | `ltm` |
| **Tutorial creation** | `ltm` (Least-to-Most) | `cod` |
| **Quick summary** | `standard` | N/A |
| **Quality validation** | `self-refine` | `self-consistent` |
| **Decision making** | `tot` (Tree-of-Thought) | `self-consistent` |

### Choose by Complexity

**Low Complexity:**
- `standard` - Fast, direct answers

**Medium Complexity:**
- `cot` - Step-by-step reasoning
- `reflexion` - Quick self-critique

**High Complexity:**
- `tot` - Multiple solution paths
- `aot` - Deep decomposition
- `self-consistent` - Consensus validation

---

## 📋 Strategy Files

Strategies are stored as JSON files in `~/.config/fabric/strategies/`

### File Structure
```json
{
  "name": "chain-of-thought",
  "description": "Step-by-step reasoning approach",
  "system_prompt": "Think through this step-by-step...",
  "user_prompt_template": "Problem: {{input}}\nLet's solve this step by step:"
}
```

### List Your Strategies
```bash
# Local installation
ls ~/.config/fabric/strategies/

# Docker
docker exec fabric-api ls /home/fabric/.config/fabric/strategies/

# Count strategies
ls ~/.config/fabric/strategies/*.json | wc -l
```

---

## 🔧 Using Strategies

### With CLI (Local)
```bash
# Basic usage
fabric --strategy cot -p analyze_code < input.txt

# With pipe
cat code.go | fabric --strategy tot -p improve_code

# With YouTube
yt --transcript 'VIDEO_URL' | fabric --strategy cot -sp summarize

# Multiple patterns
fabric --strategy ltm -p create_tutorial | fabric -p improve_writing
```

### With Docker
```bash
# Execute in container
echo "Your text" | docker exec -i fabric-api \
  fabric --strategy cot -p analyze_code

# YouTube workflow
docker exec fabric-api yt --transcript 'URL' | \
  docker exec -i fabric-api fabric --strategy tot -sp summarize
```

### With REST API
```bash
# Standard endpoint with strategy query parameter
curl -X POST "http://localhost:8080/patterns/analyze_code/execute?strategy=cot" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Your code here",
    "model": "gpt-4"
  }'

# Chat completions with strategy
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4",
    "strategy": "tot",
    "messages": [{"role": "user", "content": "Design a system"}]
  }'
```

### With Ollama API
```bash
# Ollama-compatible endpoint with strategy
curl -X POST http://localhost:11434/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "model": "analyze_code:latest",
    "strategy": "cot",
    "messages": [{"role": "user", "content": "Review this code"}]
  }'
```

---

## 🎨 Real-World Examples

### Example 1: Debug Complex Issue
```bash
# Problem: Mysterious NullPointerException in production
cat error_log.txt | fabric --strategy cot -p analyze_error

# Strategy: Chain-of-Thought walks through:
# 1. Stack trace analysis
# 2. Variable state inspection
# 3. Execution flow mapping
# 4. Root cause identification
# 5. Solution proposal
```

### Example 2: Architecture Decision
```bash
# Problem: Choose between monolith vs microservices
echo "Design a system for 100k users with complex workflows" | \
  fabric --strategy tot -p create_design_document

# Strategy: Tree-of-Thought explores:
# - Path 1: Monolith with modules
# - Path 2: Microservices with event bus
# - Path 3: Hybrid approach
# - Evaluation: Selects best based on trade-offs
```

### Example 3: Create Tutorial
```bash
# Problem: Teach beginners how to build a REST API
echo "Build a REST API in Go" | \
  fabric --strategy ltm -p create_tutorial

# Strategy: Least-to-Most progresses:
# 1. Basic HTTP server
# 2. Add routing
# 3. Add middleware
# 4. Add database
# 5. Add authentication
# 6. Add tests
```

### Example 4: Code Review
```bash
# Problem: Review pull request with 500 lines changed
gh pr diff 123 | fabric --strategy reflexion -p analyze_code

# Strategy: Reflexion provides:
# - Initial review
# - Self-critique of review quality
# - Refined review with better insights
```

### Example 5: Security Analysis
```bash
# Problem: Evaluate security of authentication system
cat auth_implementation.go | \
  fabric --strategy self-consistent -p analyze_security

# Strategy: Self-Consistent generates:
# - 3-5 independent security reviews
# - Consensus on critical issues
# - High confidence in findings
```

---

## 🧪 Testing Strategies

### Test a Strategy
```bash
# Simple test
echo "Test input" | fabric --strategy cot -p summarize

# Compare strategies
echo "Same input" | fabric --strategy standard -p analyze_code > standard.txt
echo "Same input" | fabric --strategy cot -p analyze_code > cot.txt
diff standard.txt cot.txt
```

### Benchmark Strategies
```bash
# Time comparison
time echo "Input" | fabric --strategy standard -p summarize
time echo "Input" | fabric --strategy tot -p summarize

# Quality comparison (subjective)
for strategy in cot tot aot; do
  echo "Testing $strategy..."
  cat input.txt | fabric --strategy $strategy -p analyze_code > "${strategy}_output.txt"
done
```

---

## 📊 Strategy Performance

### Speed (Fastest → Slowest)
1. `standard` - No reasoning overhead
2. `reflexion` - Single critique pass
3. `cot` - Sequential steps
4. `self-refine` - Two iterations
5. `tot` - Multiple paths
6. `self-consistent` - Multiple paths + voting
7. `aot` - Deep decomposition

### Quality (Simple → Comprehensive)
1. `standard` - Direct answer
2. `reflexion` - Quick improvement
3. `cot` - Step-by-step
4. `self-refine` - Iterative improvement
5. `aot` - Detailed decomposition
6. `tot` - Multiple perspectives
7. `self-consistent` - High confidence

### Token Usage (Low → High)
1. `standard` - Minimal tokens
2. `reflexion` - ~2x tokens
3. `cot` - ~2-3x tokens
4. `self-refine` - ~3x tokens
5. `aot` - ~3-4x tokens
6. `tot` - ~4-5x tokens
7. `self-consistent` - ~5-7x tokens

---

## 🔐 Custom Strategies

### Create Your Own Strategy

1. **Create JSON file:**
```bash
nano ~/.config/fabric/strategies/my-strategy.json
```

2. **Define strategy:**
```json
{
  "name": "my-custom-strategy",
  "description": "My custom reasoning approach",
  "system_prompt": "You are a helpful assistant that uses my custom approach.",
  "user_prompt_template": "Task: {{input}}\n\nApproach:\n1. First step\n2. Second step\n3. Final answer"
}
```

3. **Test it:**
```bash
fabric --strategy my-custom-strategy -p summarize < input.txt
```

### Example: Code Review Strategy
```json
{
  "name": "thorough-review",
  "description": "Comprehensive code review with security focus",
  "system_prompt": "You are a senior code reviewer focused on security, performance, and maintainability.",
  "user_prompt_template": "Review this code:\n\n{{input}}\n\nProvide:\n1. Security issues\n2. Performance concerns\n3. Maintainability suggestions\n4. Best practices violations\n5. Overall rating (1-10)"
}
```

---

## 🐛 Troubleshooting

### Strategy Not Found
```bash
# List installed strategies
fabric --liststrategies

# Check file exists
ls ~/.config/fabric/strategies/

# Reinstall strategies
fabric -S
```

### Strategy Not Working
```bash
# Test with standard strategy first
echo "test" | fabric --strategy standard -p summarize

# Check Docker strategy volume
docker exec fabric-api ls /home/fabric/.config/fabric/strategies/

# Check API logs
docker logs fabric-api | grep strategy
```

### Performance Issues
```bash
# Use faster strategy
--strategy reflexion  # Instead of tot or self-consistent

# Reduce model size
--model llama-3.3-70b-versatile  # Instead of gpt-4

# Use standard for simple tasks
--strategy standard
```

---

## 📚 Additional Resources

- [Fabric GitHub](https://github.com/danielmiessler/Fabric)
- [Default Strategies](https://github.com/danielmiessler/Fabric/tree/main/strategies)
- [REST API Guide](./REST_API_GUIDE.md)
- [Docker Guide](./DOCKER_GUIDE.md)
- [Pattern Documentation](https://github.com/danielmiessler/Fabric#patterns)

---

## 🚦 Quick Reference

```bash
# Install
fabric -S

# List
fabric --liststrategies

# Use
fabric --strategy <name> -p <pattern> < input.txt

# API
curl "http://localhost:8080/patterns/<pattern>/execute?strategy=<name>"

# Docker
docker exec -i fabric-api fabric --strategy <name> -p <pattern>
```

**Strategies enhance Fabric's AI capabilities with structured reasoning! 🧠**
