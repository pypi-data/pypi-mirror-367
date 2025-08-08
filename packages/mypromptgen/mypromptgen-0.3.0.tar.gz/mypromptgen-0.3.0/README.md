# Prompt and Answer Generation Tool

This tool generates structured conversations (prompts and answers) based on specified topics using language models.

## Requirements
- Requires LiteLLM for API access

## Features
- Generate multiple prompts per topic
- Generate assistant answers for each prompt
- Save conversations to JSON file
- Environment variables for configuration
- Interactive prompts for missing values
- Batch processing for prompt/answer generation
- Asynchronous API calls for improved performance

## Setup

1. Clone repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Create virtual environment (optional but recommended):
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or 
.venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

1. Create `.env` file from example:
```bash
cp .env.example .env
```

2. Configure `.env` file:
```ini
# Prompt/Answer Generation (.env)
PROMPTGEN_MODEL=gpt-3.5-turbo
ANSWERGEN_MODEL=gpt-4-turbo
TOPICS=Python,JavaScript,AI
AMOUNTS=5,3,2
MODEL_SPLIT=70,30
TEMPERATURE=0.7
MULTI_PROMPT=y
LOGITS=y
OUTPUT_FILE=conversations.json
BATCH_SIZE=5
ASYNC_GEN=y

# Distillation (distill.py)
MODEL_NAME=meta-llama/Llama-2-7b-hf
DATA_FILE=conversations.json
BATCH_SIZE=4
GRAD_ACC_STEPS=4
LEARNING_RATE=2e-5
ALPHA=0.7
TEMPERATURE=2.0

# QLoRA (qlora.py)
MODEL_NAME=unsloth/Qwen2.5-Coder-1.5B-Instruct
MAX_SEQ_LENGTH=2048
LOAD_IN_4BIT=True
LORA_R=16
TARGET_MODULES=q_proj,k_proj,v_proj
```

3. Set API keys (in shell or `.env`):
```bash
export OPENAI_API_KEY=sk-xxx       # For OpenAI
export ANTHROPIC_API_KEY=sk-xxx    # For Claude
# See https://litellm.vercel.app/docs/providers for other providers
```

## Usage Commands

1. Generate prompts/answers:
```bash
python -m mypromptgen.main
```

2. Perform migration (convert conversation file formats):
```bash
python migrate.py input.json
# Creates input.json.bak and updates input.json
```

3. Run distillation training:
```bash
python distill.py
# Outputs: distill_output/
```

4. Run QLoRA training:
```bash
python qlora.py
# Outputs: outputs/
# Saves merged model: unsloth_final_model/
```

5. Build and publish to PyPI:
```bash
# Clean previous builds
rm -rf build dist *.egg-info

# Install build tools
pip install --upgrade setuptools build twine

# Create distribution
python -m build

# Upload to PyPI
twine upload dist/*
```

> Note: You'll need a PyPI account and `.pypirc` file configured with your credentials

## Environment Variable Reference

| Variable | Scope | Description | 
|----------|-------|-------------|
| `PROMPTGEN_MODEL` | main | Prompt gen model (e.g., gpt-3.5-turbo) |
| `ANSWERGEN_MODEL` | main | Comma-separated answer gen models |
| `MODEL_SPLIT` | main | Percentage split for answer models |
| `TOPICS` | main | Comma-separated topics |
| `AMOUNTS` | main | Prompt counts per topic |
| `TEMPERATURE` | main | Creativity level (0.0-1.0) |
| `MULTI_PROMPT` | main | Multi-prompt generation (y/n) |
| `LOGITS` | main | Capture log probabilities (y/n) |
| `OUTPUT_FILE` | main | JSON output filename |
| `BATCH_SIZE` | main,distill | Generation batch size |
| `ASYNC_GEN` | main | Parallel API calls (y/n) |
| `MODEL_NAME` | distill,qlora | Base model for training |
| `DATA_FILE` | distill,qlora | Training data file |
| `GRAD_ACC_STEPS` | distill,qlora | Gradient accumulation steps |
| `LEARNING_RATE` | distill,qlora | Training learning rate |
| `ALPHA` | distill | Distillation loss weighting |
| `TEMPERATURE` | distill | Distillation temperature |
| `LOAD_IN_4BIT` | qlora | 4-bit quantization (True/False) |
| `LORA_R` | qlora | LoRA rank |
| `TARGET_MODULES` | qlora | Comma-separated target modules |

## Logits Capture
When `LOGITS=y`:
- Assistant responses will include token-level probability data from the model
- This data includes the top 10 token candidates at each position with their log probabilities

## Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `PROMPTGEN_MODEL` | Model for prompt generation | *Required* |
| `ANSWERGEN_MODEL` | Model for answer generation | *Required* |
| `TEMPERATURE` | Creativity level (0.0-1.0) | 0.7 |
| `TOPICS` | Comma-separated list of topics | *Required* |
| `AMOUNTS` | Number of prompts per topic (single or comma-separated) | *Required* |
| `MULTI_PROMPT` | Use multi-prompt generation? (Y/n) | y |
| `MODEL_SPLIT` | Percentage split for answer models (comma-separated, sum=100) | Required for multiple models |
| `LOGITS` | Use logits for answer generation? (y/n) | n |
| `OUTPUT_FILE` | Output JSON filename | conversations.json |
| `BATCH_SIZE` | Batch size for prompt generation | 5 |
| `ASYNC_GEN` | Enable asynchronous generation? (y/n) | n |
| `VERBOSE_LOGGING` | Print request/response bodies | n |

## Usage
Run the script:
```bash
python main.py
```

The tool will:
1. Check for required environment variables
2. Prompt for missing values
3. Generate prompts for each topic
4. Generate answers for each prompt
5. Save conversations to specified JSON file

## Output Format
Conversations are saved in JSON format:
```json
[
  {
    "messages": [
      {
        "role": "user",
        "content": "Explain quantum computing in simple terms",
        "generation_model": "gpt-3.5-turbo"  // New field for prompt model
      },
      {
        "role": "assistant",
        "content": "Quantum computing leverages quantum mechanics to process information...",
        "logprobs": {
          "content": [
            {
              "token": "Quantum",
              "logprob": -0.1,
              "top_logprobs": [
                {"token": "Quantum", "logprob": -0.1},
                {"token": "This", "logprob": -1.2},
                ...
              ]
            }
          ]
        },
        "generation_model": "gpt-4"  // New field for answer model
      }
    ],
    "model": "gpt-4"  // Model used for answer generation in this conversation
  }
]
```
- The conversation object now includes a top-level "model" field indicating the answer generation model
- User messages include "generation_model" showing which model created the prompt

## Example
```bash
# .env file:
PROMPTGEN_MODEL=gpt-3.5-turbo
ANSWERGEN_MODEL=gpt-4
TOPICS=Python,JavaScript
AMOUNTS=2
BATCH_SIZE=5          # Add this line
ASYNC_GEN=n           # Add this line

# Command:
python main.py
```

## Notes
- Uses [LiteLLM](https://github.com/BerriAI/liteLLM) format for API access
- Check `.env.example` for configuration reference
```
