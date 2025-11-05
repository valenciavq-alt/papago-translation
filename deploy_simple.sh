#!/bin/bash
# Simple deployment script for Hugging Face Spaces
# Usage: ./deploy_simple.sh YOUR_USERNAME YOUR_SPACE_NAME YOUR_TOKEN

set -e

if [ $# -lt 3 ]; then
    echo "🚀 Hugging Face Space Deployment"
    echo "================================="
    echo ""
    echo "Usage: ./deploy_simple.sh <username> <space_name> <token>"
    echo ""
    echo "Or run interactively:"
    echo ""
    read -p "Your Hugging Face username: " USERNAME
    read -p "Your Space name: " SPACE_NAME
    read -sp "Your Hugging Face token (get from https://huggingface.co/settings/tokens): " TOKEN
    echo ""
else
    USERNAME=$1
    SPACE_NAME=$2
    TOKEN=$3
fi

SPACE_URL="https://huggingface.co/spaces/$USERNAME/$SPACE_NAME"
REPO_URL="https://huggingface.co/spaces/$USERNAME/$SPACE_NAME.git"

echo ""
echo "📋 Make sure you've created the Space at:"
echo "   https://huggingface.co/new-space"
echo "   Space name: $SPACE_NAME"
echo ""
read -p "Press Enter after creating the Space (or if it already exists)..."

echo ""
echo "📦 Cloning repository..."
if [ -d "$SPACE_NAME" ]; then
    echo "   Removing existing directory..."
    rm -rf "$SPACE_NAME"
fi

git clone "$REPO_URL" "$SPACE_NAME" || {
    echo "❌ Failed to clone. Make sure:"
    echo "   1. Space exists: $SPACE_URL"
    echo "   2. Token is correct"
    echo "   3. You have write access"
    exit 1
}

cd "$SPACE_NAME"

echo "📋 Copying files..."
cp "../app.py" .
cp "../papago_translation.py" .
cp "../requirements_hf.txt" requirements.txt
cp "../README_HF.md" README.md

echo "💾 Configuring git..."
git config user.name "$USERNAME"
git config user.email "$USERNAME@users.noreply.huggingface.co"

echo "📤 Committing and pushing..."
git add .
git commit -m "Initial commit: Papago Korean Translation" || echo "   (Nothing new to commit)"

# Push using token
git push https://$USERNAME:$TOKEN@huggingface.co/spaces/$USERNAME/$SPACE_NAME.git || {
    echo "❌ Push failed. Check your token and permissions."
    exit 1
}

echo ""
echo "✅ Success! Your Space is being built."
echo "   URL: $SPACE_URL"
echo "   Build logs: $SPACE_URL/logs"

cd ..
