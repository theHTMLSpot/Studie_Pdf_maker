# GPT4All Models

This directory contains the GPT4All models used by the backend.

## How to add a model:

### Option 1: Download via GPT4All GUI (Recommended)
1. Open the GPT4All application (already installed in `/Applications/gpt4all`)
2. Go to the Models tab and download a model (recommended: Llama 3.2 1B Instruct, Phi-3 Mini, or Mistral 7B)
3. Once downloaded, models will be in: `~/Library/Application Support/nomic.ai/GPT4All/`
4. Copy the model file here:
   ```bash
   cp ~/Library/Application\ Support/nomic.ai/GPT4All/your-model.gguf backend/models/
   ```

### Option 2: Download directly
Download a model from HuggingFace:
```bash
# Example: Download Llama 3.2 1B Instruct
cd backend/models
wget https://huggingface.co/QuantFactory/Llama-3.2-1B-Instruct-GGUF/resolve/main/Llama-3.2-1B-Instruct.Q4_K_M.gguf
```

## Recommended Models:
- **Llama 3.2 1B Instruct** (~1GB) - Fast, good for summaries
- **Phi-3 Mini** (~2.5GB) - Microsoft's efficient model
- **Mistral 7B Instruct** (~4GB) - More powerful, slower

## Current Model in Code:
The backend is configured to use: `models/gpt4all-j.bin`

Update `backend/main.py` line 30 to point to your downloaded model:
```python
llm = Llama(
    model_path="models/your-downloaded-model.gguf",
    n_ctx=2048,
    n_threads=4
)
```
