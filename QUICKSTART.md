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

## 🎯 Example: Video Generation with OpenAI

1. Add "Generate Video (AI CustomURL)" node
2. Fill in:
   ```
   base_url: https://api.openai.com/v1
   api_key: sk-proj-YOUR_KEY_HERE
   model: sora-2
   prompt: A cat playing with a ball of yarn
   resolution: 1080p
   aspect_ratio: 16:9
   duration: 4
   fps: 24
   auto_poll: true
   poll_interval: 5
   max_wait_time: 1200
   ```
3. Execute → The node will automatically wait until video is ready!

**Auto-Polling Feature** (enabled by default):
- `auto_poll: true` → Node automatically checks video status every X seconds
- `poll_interval: 5` → Check every 5 seconds (default)
- `max_wait_time: 1200` → Give up after 20 minutes (default)
- You'll see status updates in the console
- Once completed, `video_url` output contains the download link
- `video_id` output contains the generation ID (for manual retrieval if needed)

**Outputs:**
- `video_url` → Direct link to download video (when completed)
- `video_id` → OpenAI's video generation ID
- `api_key` → Passes your API key to download/preview nodes
- `response_json` → Full API response for debugging

**Note**: The node automatically converts parameters to OpenAI's format:
- `resolution` + `aspect_ratio` → `size` (OpenAI only supports 4 sizes):
  - `16:9` → `"1280x720"` (landscape)
  - `9:16` → `"720x1280"` (portrait)
  - `21:9` or `4:3` → `"1792x1024"` (wide landscape)
  - `1:1` → `"1280x720"` (defaults to landscape)
- `duration` → `seconds` as string ("4", "8", or "12" only)
  - OpenAI only supports 4, 8, or 12 second videos
  - Will round to nearest valid value
- `fps` is filtered out (not supported by OpenAI)
- For image-to-video, connect an image input → `image` parameter

### 🔄 Understanding Video Generation Workflow

**With Auto-Polling (Default - Recommended):**
1. Run "Generate Video" node with `auto_poll: true`
2. Node automatically waits and checks status every 5 seconds
3. Watch the console for progress updates
4. When completed, `video_url` output has the download link
5. Connect `video_url` directly to "Save Video from URL" or preview nodes!

**Console Output Example:**
```
[INFO] Video generation started. ID: video_abc123
[INFO] Initial status: queued
[INFO] Auto-polling enabled. Will check every 5s (max 1200s)
[INFO] Waiting 5s before checking status...
[INFO] Status check (5s elapsed): processing
[INFO] Waiting 5s before checking status...
[INFO] Status check (10s elapsed): completed
[SUCCESS] Video completed after 10s!
[SUCCESS] Video URL: https://...
```

**Manual Polling (If Auto-Poll Disabled):**
If you set `auto_poll: false`, use the "Retrieve Video Status" node:
1. Add "Retrieve Video Status (AI CustomURL)" node
2. Connect `video_id` output from Generate node → `video_id` input
3. Run it to check status
4. When status = "completed", use the `video_url` output

### 🎬 Preview & Save Video

**Complete Workflow:**

```
                              ┌─→ video_url ──→ [Preview Video]
                              │     api_key         (see in UI!)
[Generate Video] ─────────────┤
(auto-polls)                  │
                              └─→ video_url ──→ [Save Video from URL]
                                    api_key         (saved to disk!)
```

**Setup:**

1. **Add "Generate Video (AI CustomURL)" node**
   - Configure your prompt, model, etc.
   - `auto_poll: true` (default)

2. **Add "Preview Video (AI CustomURL)" node**
   - Connect `video_url` → `video_url`
   - Connect `api_key` → `api_key`
   - Video will show in ComfyUI UI!

3. **Add "Save Video from URL" node**
   - Connect `video_url` → `video_url`
   - Connect `api_key` → `api_key` (optional field)
   - Set `filename: my_video_{timestamp}`
   - Set `output_folder: output/videos`

4. **Run the workflow!**
   - Video generates automatically
   - Preview appears in UI
   - Video saves to disk
   - All automatic! 🎉

**Notes:**
- The `api_key` connection enables authenticated downloads for OpenAI
- The `{timestamp}` placeholder adds unique timestamps to filenames
- `output/videos` folder will be created automatically if it doesn't exist

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

