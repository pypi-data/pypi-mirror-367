# Prompt and Answer Generation Tool

This tool generates structured conversations (prompts and answers) based on specified topics using language models.

## Quick Start

### Installation
Install the package using pip:
```bash
pip install mypromptgen
```

### Setup
Configure your environment:
1. Create `.env` file from example:
```bash
curl -O https://raw.githubusercontent.com/<username>/<repo>/main/.env.example
mv .env.example .env
```
2. Add your API keys to `.env`:
```ini
OPENAI_API_KEY=sk-xxx       # For OpenAI
ANTHROPIC_API_KEY=sk-xxx    # For Claude
```
3. Configure models and topics in `.env`:
```ini
PROMPTGEN_MODEL=gpt-3.5-turbo
ANSWERGEN_MODEL=gpt-4
TOPICS=Python,JavaScript
AMOUNTS=10
```

### Generate Conversations
Run the main tool:
```bash
mypromptgen
```

## Extended Features

### Advanced Usage
1. **Distillation Training**:
```bash
export DATA_FILE=conversations.json
python distill.py
```

2. **QLoRA Training**:
```bash
export MODEL_NAME=unsloth/Qwen2.5-Coder-1.5B-Instruct
python qlora.py
```

3. **Migration**:
```bash
python migrate.py input.json
```

### Environment Configuration
| Key | Description |
|-----|-------------|
| `PROMPTGEN_MODEL` | Model for prompt generation |
| `ANSWERGEN_MODEL` | Comma-separated answer gen models |
| `TOPICS` | Comma-separated topic list |
| `AMOUNTS` | Number of prompts per topic |
| `MODEL_SPLIT` | Percentage weights for answer models |
| `LOGITS` | Capture log probabilities (y/n) |

Full variable list and detailed documentation at [GitHub Repo](https://github.com/<username>/<repo>)

### PyPI Publishing
1. Create distribution:
```bash
python -m build
```
2. Upload to PyPI:
```bash
twine upload dist/*
```
