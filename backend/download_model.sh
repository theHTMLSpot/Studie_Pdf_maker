#!/bin/bash

# Script to download a GPT4All model directly from HuggingFace

TARGET_DIR="$(dirname "$0")/models"

echo "GPT4All Model Downloader"
echo "========================"
echo ""
echo "Select a model to download:"
echo ""
echo "[1] Llama 3.2 1B Instruct (~1GB) - RECOMMENDED - Fast and efficient"
echo "[2] Phi-3 Mini 4K (~2.5GB) - Good balance of speed and quality"
echo "[3] Mistral 7B Instruct v0.3 (~4GB) - Most powerful, slower"
echo ""
echo -n "Enter your choice (1-3): "
read choice

case $choice in
    1)
        MODEL_NAME="Llama-3.2-1B-Instruct.Q4_K_M.gguf"
        MODEL_URL="https://huggingface.co/QuantFactory/Llama-3.2-1B-Instruct-GGUF/resolve/main/Llama-3.2-1B-Instruct.Q4_K_M.gguf"
        ;;
    2)
        MODEL_NAME="Phi-3-mini-4k-instruct.Q4_0.gguf"
        MODEL_URL="https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf"
        ;;
    3)
        MODEL_NAME="mistral-7b-instruct-v0.3.Q4_0.gguf"
        MODEL_URL="https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.3-GGUF/resolve/main/mistral-7b-instruct-v0.3.Q4_0.gguf"
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "Downloading $MODEL_NAME..."
echo "This may take a few minutes depending on your internet connection."
echo ""

cd "$TARGET_DIR" || exit 1

# Check if curl is available
if command -v curl &> /dev/null; then
    curl -L -o "$MODEL_NAME" "$MODEL_URL" --progress-bar
elif command -v wget &> /dev/null; then
    wget -O "$MODEL_NAME" "$MODEL_URL"
else
    echo "❌ Error: Neither curl nor wget is available"
    echo "Please install curl or wget first"
    exit 1
fi

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Model downloaded successfully!"
    echo ""
    echo "Model saved to: $TARGET_DIR/$MODEL_NAME"
    echo ""
    echo "The backend will automatically detect and use this model."
    echo "Just restart your backend server if it's running."
else
    echo ""
    echo "❌ Download failed"
    exit 1
fi
