🌐 Hugging Face Space live demo: [https://huggingface.co/spaces/zxc1232/koreantoenglish](https://huggingface.co/spaces/zxc1232/koreantoenglish) — No installation required—try it in your browser!

# Deploying to Hugging Face Spaces

## Quick Start Guide

### Step 1: Create a Hugging Face Account
1. Go to [https://huggingface.co/](https://huggingface.co/)
2. Sign up for a free account (if you don't have one)

### Step 2: Create a New Space
1. Go to [https://huggingface.co/spaces](https://huggingface.co/spaces)
2. Click **"Create new Space"**
3. Fill in the details:
   - **Space name**: e.g., `papago-korean-translation`
   - **SDK**: Select **Gradio**
   - **Hardware**: Choose **CPU Basic** (free) or **GPU** (if you have credits)
   - **Visibility**: Public or Private

### Step 3: Upload Files

You need to upload these files to your Space:

#### Required Files:
1. **`app.py`** - Main Gradio application
2. **`papago_translation.py`** - Core translation module
3. **`requirements.txt`** - Python dependencies (use `requirements_hf.txt` content)
4. **`README.md`** - Space description (use `README_HF.md` content)

#### File Upload Methods:

**Option A: Using Git (Recommended)**
```bash
# Clone your Space repository
git clone https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME
cd YOUR_SPACE_NAME

# Copy files
cp /path/to/papago-translation/app.py .
cp /path/to/papago-translation/papago_translation.py .
cp /path/to/papago-translation/requirements_hf.txt requirements.txt
cp /path/to/papago-translation/README_HF.md README.md

# Commit and push
git add .
git commit -m "Initial commit: Papago Korean Translation"
git push
```

**Option B: Using Web Interface**
1. Go to your Space page
2. Click **"Files"** tab
3. Click **"Add file"** → **"Upload file"**
4. Upload each file individually:
   - `app.py`
   - `papago_translation.py`
   - `requirements.txt` (copy content from `requirements_hf.txt`)
   - `README.md` (copy content from `README_HF.md`)

### Step 4: Wait for Build
- Hugging Face will automatically build your Space
- Check the **"Logs"** tab for build progress
- This may take 5-10 minutes for the first build

### Step 5: Test Your Space
- Once built, your Space will be live at:
  `https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME`
- Test the interface and make sure everything works

## Files Summary

### What to Upload:
- ✅ `app.py` - Main application
- ✅ `papago_translation.py` - Translation module
- ✅ `requirements.txt` - Dependencies (use `requirements_hf.txt`)
- ✅ `README.md` - Space description (use `README_HF.md`)

### What NOT to Upload:
- ❌ `venv/` - Virtual environment (not needed)
- ❌ `__pycache__/` - Python cache
- ❌ `test_*.py` - Test files
- ❌ `pytest.ini` - Test configuration
- ❌ `run_app.sh` - Local script
- ❌ `requirements.txt` - Use `requirements_hf.txt` instead (without pytest)

## Troubleshooting

### Build Fails
- Check the **Logs** tab for error messages
- Verify all required files are uploaded
- Ensure `requirements.txt` has correct dependencies

### App Doesn't Start
- Check that `app.py` has `if __name__ == "__main__": demo.launch()`
- Verify all imports are available in requirements.txt

### Missing Dependencies
- Add any missing packages to `requirements.txt`
- Push changes and wait for rebuild

## Notes

- The Space uses Python 3.10+ (provided by Hugging Face)
- Whisper models will be downloaded automatically on first use
- Users need to provide their own Papago API credentials
- For GPU acceleration, upgrade your Space hardware tier

## Space URL Format
Your Space will be available at:
```
https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME
```

Replace `YOUR_USERNAME` and `YOUR_SPACE_NAME` with your actual values.


