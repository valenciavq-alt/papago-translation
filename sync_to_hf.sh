#!/bin/bash
# Sync script to update Hugging Face Space from main repository
# Usage: ./sync_to_hf.sh [commit-message]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MAIN_DIR="$SCRIPT_DIR"
HF_SPACE_DIR="$SCRIPT_DIR/hf-space"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Syncing to Hugging Face Space${NC}"
echo "=================================="
echo ""

# Check if hf-space directory exists
if [ ! -d "$HF_SPACE_DIR" ]; then
    echo -e "${YELLOW}⚠️  hf-space directory not found!${NC}"
    echo "Creating it by cloning from Hugging Face..."
    read -p "Enter your Hugging Face username: " HF_USERNAME
    read -p "Enter your Space name: " SPACE_NAME
    git clone "https://huggingface.co/spaces/$HF_USERNAME/$SPACE_NAME" "$HF_SPACE_DIR"
fi

# Check if we're in the main repo
cd "$MAIN_DIR"
if [ ! -f "app.py" ]; then
    echo -e "${YELLOW}⚠️  Error: app.py not found in main directory${NC}"
    exit 1
fi

# Files to sync
FILES_TO_SYNC=(
    "app.py"
    "papago_translation.py"
    "requirements_hf.txt"
    "README_HF.md"
    "packages.txt"
)

echo -e "${BLUE}📋 Copying files to hf-space...${NC}"
cd "$HF_SPACE_DIR"

# Copy files
for file in "${FILES_TO_SYNC[@]}"; do
    if [ -f "$MAIN_DIR/$file" ]; then
        cp "$MAIN_DIR/$file" .
        echo "  ✅ $file"
    else
        echo -e "  ${YELLOW}⚠️  $file not found (skipping)${NC}"
    fi
done

# Rename requirements_hf.txt to requirements.txt
if [ -f "requirements_hf.txt" ]; then
    mv requirements_hf.txt requirements.txt
    echo "  ✅ requirements_hf.txt → requirements.txt"
fi

# Rename README_HF.md to README.md
if [ -f "README_HF.md" ]; then
    mv README_HF.md README.md
    echo "  ✅ README_HF.md → README.md"
fi

echo ""
echo -e "${BLUE}💾 Checking git status...${NC}"
git status --short

# Check if there are changes
if [ -z "$(git status --porcelain)" ]; then
    echo -e "${GREEN}✅ No changes to commit${NC}"
    exit 0
fi

echo ""
read -p "Ready to commit and push to Hugging Face? (y/n): " CONFIRM

if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
    echo "❌ Cancelled"
    exit 0
fi

# Commit message
if [ -n "$1" ]; then
    COMMIT_MSG="$1"
else
    COMMIT_MSG="Update: Sync from main repository"
fi

echo ""
echo -e "${BLUE}💾 Committing changes...${NC}"
git add .
git commit -m "$COMMIT_MSG"

echo ""
echo -e "${BLUE}📤 Pushing to Hugging Face...${NC}"
git push origin main

echo ""
echo -e "${GREEN}✅ Successfully synced to Hugging Face Space!${NC}"
echo ""
echo "Your Space will rebuild automatically."
echo "Check logs: https://huggingface.co/spaces/zxc1232/koreantoenglish/logs"

# Optional: Ask if they want to push to GitHub too
echo ""
read -p "Also push to GitHub? (y/n): " PUSH_GITHUB

if [ "$PUSH_GITHUB" = "y" ] || [ "$PUSH_GITHUB" = "Y" ]; then
    cd "$MAIN_DIR"
    echo ""
    echo -e "${BLUE}📤 Pushing to GitHub...${NC}"
    git add .
    git commit -m "$COMMIT_MSG" || echo "No changes to commit in main repo"
    git push origin main
    echo -e "${GREEN}✅ Also pushed to GitHub!${NC}"
fi

echo ""
echo -e "${GREEN}✨ Done!${NC}"

