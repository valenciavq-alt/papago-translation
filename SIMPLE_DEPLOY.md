🌐 Hugging Face Space live demo: [https://huggingface.co/spaces/zxc1232/koreantoenglish](https://huggingface.co/spaces/zxc1232/koreantoenglish) — No installation required—try it in your browser!

# Hugging Face Login and Deployment Guide

Since the CLI isn't available, here's the easiest way to deploy:

## Method 1: Using Git (Recommended)

### Step 1: Create Your Space
1. Go to: **https://huggingface.co/new-space**
2. Fill in:
   - **Space name**: `papago-korean-translation` (or your choice)
   - **SDK**: **Gradio**
   - **Hardware**: **CPU Basic** (free)
   - **Visibility**: Public or Private
3. Click **"Create Space"**

### Step 2: Get Your Access Token
1. Go to: **https://huggingface.co/settings/tokens**
2. Click **"New token"**
3. Name it: `space-deploy`
4. Select **"Write"** permissions
5. Click **"Generate token"**
6. **Copy the token** (you'll need it)

### Step 3: Clone and Deploy

```bash
# Replace YOUR_USERNAME and YOUR_SPACE_NAME with your actual values
# Replace YOUR_TOKEN with the token you just created

USERNAME="YOUR_USERNAME"
SPACE_NAME="YOUR_SPACE_NAME"
TOKEN="YOUR_TOKEN"

# Clone the repository
git clone https://huggingface.co/spaces/$USERNAME/$SPACE_NAME
cd $SPACE_NAME

# Copy files
cp ../papago-translation/app.py .
cp ../papago-translation/papago_translation.py .
cp ../papago-translation/requirements_hf.txt requirements.txt
cp ../papago-translation/README_HF.md README.md

# Configure git with token
git config user.name "$USERNAME"
git config user.email "$USERNAME@users.noreply.huggingface.co"

# Commit and push
git add .
git commit -m "Initial commit: Papago Korean Translation"
git push https://$USERNAME:$TOKEN@huggingface.co/spaces/$USERNAME/$SPACE_NAME

cd ..
```

## Method 2: Web Interface (No Git Required)

1. **Create Space** at https://huggingface.co/new-space
2. Go to your Space page
3. Click **"Files"** tab → **"Add file"** → **"Upload file"**
4. Upload these files:
   - `app.py`
   - `papago_translation.py`
   - Create `requirements.txt` (paste content from `requirements_hf.txt`)
   - Create `README.md` (paste content from `README_HF.md`)

The Space will automatically build after files are uploaded!

## Quick Reference

**Files to upload:**
- `app.py`
- `papago_translation.py`
- `requirements.txt` (use `requirements_hf.txt` content)
- `README.md` (use `README_HF.md` content)

**Your Space URL will be:**
`https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME`


