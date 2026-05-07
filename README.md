# Hardware-Security-Final-Project
Hardware Security Final Project

## OpenRouter Setup

This repo is configured to use OpenRouter by default.

1. Copy `.env.example` to `.env`.
2. Set `OPENROUTER_API_KEY` in `.env`.
3. Run the script with an OpenRouter model slug, for example:

```bash
python GHOST_Trojan_GPT.py --backend OpenRouter --model google/gemini-3-flash-preview
```

The local `.env` file is ignored by git so API keys are not pushed.
