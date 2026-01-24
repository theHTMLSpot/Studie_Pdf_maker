#!/bin/bash

# Script to copy GPT4All models from the GPT4All app data directory to backend/models

GPT4ALL_DIR="$HOME/Library/Application Support/nomic.ai/GPT4All"
TARGET_DIR="$(dirname "$0")/models"

echo "Looking for GPT4All models in: $GPT4ALL_DIR"
echo "Target directory: $TARGET_DIR"
echo ""

# Check if GPT4All directory exists
if [ ! -d "$GPT4ALL_DIR" ]; then
    echo "❌ GPT4All directory not found!"
    echo "Please download a model using the GPT4All application first."
    exit 1
fi

# Find all .gguf files
MODELS=$(find "$GPT4ALL_DIR" -name "*.gguf" -type f 2>/dev/null)

if [ -z "$MODELS" ]; then
    echo "❌ No .gguf model files found in GPT4All directory!"
    echo ""
    echo "To download a model:"
    echo "1. Open the GPT4All application"
    echo "2. Go to the 'Models' tab"
    echo "3. Download a model (recommended: Llama 3.2 1B Instruct)"
    echo "4. Run this script again"
    exit 1
fi

echo "Found the following models:"
echo ""

# Display models with numbers
i=1
declare -a model_array
while IFS= read -r model; do
    filename=$(basename "$model")
    size=$(du -h "$model" | cut -f1)
    echo "[$i] $filename ($size)"
    model_array[$i]=$model
    ((i++))
done <<< "$MODELS"

echo ""
echo -n "Enter the number of the model to copy (or 'all' to copy all): "
read choice

if [ "$choice" = "all" ]; then
    # Copy all models
    for model in "${model_array[@]}"; do
        filename=$(basename "$model")
        echo "Copying $filename..."
        cp "$model" "$TARGET_DIR/"
    done
    echo "✅ All models copied successfully!"
elif [ "$choice" -ge 1 ] && [ "$choice" -lt "$i" ]; then
    # Copy selected model
    selected_model="${model_array[$choice]}"
    filename=$(basename "$selected_model")
    echo "Copying $filename..."
    cp "$selected_model" "$TARGET_DIR/"
    echo "✅ Model copied successfully!"
    echo ""
    echo "Update backend/main.py line 30 to use this model:"
    echo "    model_path=\"models/$filename\","
else
    echo "❌ Invalid choice"
    exit 1
fi

echo ""
echo "Models in backend/models:"
ls -lh "$TARGET_DIR"/*.gguf 2>/dev/null || echo "No models found yet"
