# 🚀 Quick Start Guide - AI CustomURL

## Simple 3-Step Process

### 1️⃣ Find Your API Details

Visit your API provider's documentation to get:
- **Base URL** (the API endpoint)
- **API Key** (your authentication token)
- **Model Name** (which model you want to use)

### 2️⃣ Enter in ComfyUI Node

Add a generation node and fill in these three fields:
- `base_url`: Your API's base URL
- `api_key`: Your API key
- `model`: The model name

### 3️⃣ Execute!

Enter your prompt and run the workflow!

---

## 📚 Common API Configurations

### OpenAI
```
base_url: https://api.openai.com/v1
api_key: sk-proj-...
models:
  - Text: gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-3.5-turbo
  - Image: dall-e-3, dall-e-2
  - Video: sora-1.0, sora-turbo (if you have access)
  - Speech: tts-1, tts-1-hd
```

### Venice.ai
```
base_url: https://api.venice.ai/api/v1
api_key: <your_venice_key>
models:
  - Text: llama-3.3-70b, llama-3.1-405b, qwen-2.5-72b
  - Image: flux-dev, flux-pro, stable-diffusion-3.5
  - Speech: tts-kokoro
```

### OpenRouter
```
base_url: https://openrouter.ai/api/v1
api_key: sk-or-v1-...
models:
  - Text: openai/gpt-4o, anthropic/claude-3.5-sonnet, meta-llama/llama-3.1-405b
  (Check https://openrouter.ai/models for full list)
```

### Together.ai
```
base_url: https://api.together.xyz/v1
api_key: <your_together_key>
models:
  - Text: meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo
  - Image: black-forest-labs/FLUX.1-schnell
  (Check https://docs.together.ai/docs/inference-models for list)
```

### Local Ollama
```
base_url: http://localhost:11434/v1
api_key: not-needed (or leave blank)
models:
  - Whatever you've pulled: llama3, mistral, codellama, etc.
  (Run: ollama list to see your models)
```

---

## 🎯 Example: Text Generation with OpenAI

1. Add "Generate Text (AI CustomURL)" node
2. Fill in:
   ```
   base_url: https://api.openai.com/v1
   api_key: sk-proj-YOUR_KEY_HERE
   model: gpt-4o-mini
   prompt: Write me a haiku about coding
   system_prompt: You are a helpful assistant.
   temperature: 0.7
   max_tokens: 1024
   ```
3. Execute → Get your generated text!

## 🎯 Example: Image Generation with Venice

1. Add "Generate Image (AI CustomURL)" node
2. Fill in:
   ```
   base_url: https://api.venice.ai/api/v1
   api_key: YOUR_VENICE_KEY
   model: flux-dev
   prompt: A futuristic city at sunset
   size: 1024x1024
   ```
3. Execute → Get your generated image!

## 🎯 Example: Using Advanced Parameters

1. Add "Text Advanced Parameters" node
2. Set your custom parameters:
   ```
   top_p: 0.9
   frequency_penalty: 0.5
   seed: 12345
   ```
3. Connect `params_json` output → `advanced_params_json` input on your Text Generation node
4. The parameters will be merged into the API call!

---

## 💡 Tips

### Finding Model Names

**OpenAI:**
- Docs: https://platform.openai.com/docs/models
- List: `curl https://api.openai.com/v1/models -H "Authorization: Bearer YOUR_KEY"`

**Venice.ai:**
- Docs: https://docs.venice.ai/
- Dashboard: https://venice.ai/models

**OpenRouter:**
- Models: https://openrouter.ai/models

**Together.ai:**
- Models: https://docs.together.ai/docs/inference-models

**Ollama:**
- Run: `ollama list` in terminal

### Using Environment Variables

Instead of entering API keys in nodes, set environment variables:

```bash
# Linux/Mac - add to ~/.bashrc
export OPENAI_API_KEY="sk-..."
export VENICE_API_KEY="..."

# Then use in node:
api_key: ${OPENAI_API_KEY}  # (if ComfyUI supports env var expansion)
```

### Testing Different APIs

Keep the same workflow but just change:
- `base_url`
- `api_key`  
- `model`

Everything else stays the same!

---

## ✅ That's It!

No complex setup, no model caching, no JavaScript - just **enter your API details and go**! 🚀

