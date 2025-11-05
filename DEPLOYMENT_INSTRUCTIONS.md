🌐 Hugging Face Space live demo: [https://huggingface.co/spaces/zxc1232/koreantoenglish](https://huggingface.co/spaces/zxc1232/koreantoenglish) — No installation required—try it in your browser!

# 🤖 Automated Deployment Script

I've created a script that will help automate the deployment process. However, I cannot directly create the Space or authenticate with your Hugging Face account. Here's what I can do:

## What I've Prepared:

✅ All files are ready and properly formatted
✅ Created `deploy_to_hf.sh` script to automate the Git workflow

## What You Need to Do:

### Step 1: Create the Space (I can't do this for you)
1. Go to: **https://huggingface.co/new-space**
2. Fill in:
   - **Space name**: `papago-korean-translation` (or your choice)
   - **SDK**: **Gradio**
   - **Hardware**: **CPU Basic** (free)
   - **Visibility**: Public or Private
3. Click **"Create Space"**

### Step 2: Login to Hugging Face CLI
```bash
# Install if needed
pip install huggingface_hub[cli]

# Login
huggingface-cli login
```

### Step 3: Run the Deployment Script
```bash
./deploy_to_hf.sh
```

The script will:
- Ask for your Hugging Face username and Space name
- Clone your Space repository
- Copy all necessary files
- Commit and push everything

## Alternative: Manual Upload (No Git Required)

If you prefer not to use Git:

1. **Create Space** at https://huggingface.co/new-space
2. Go to your Space page
3. Click **"Files"** tab
4. Click **"Add file"** → **"Upload file"**
5. Upload these files:
   - `app.py`
   - `papago_translation.py`
   - `requirements.txt` (use content from `requirements_hf.txt`)
   - `README.md` (use content from `README_HF.md`)

## Files Ready to Upload:

All files are in: `/Users/valencia/papago-translation/`

- ✅ `app.py` - Main application
- ✅ `papago_translation.py` - Translation module  
- ✅ `requirements_hf.txt` - Dependencies (copy to `requirements.txt`)
- ✅ `README_HF.md` - Space description (copy to `README.md`)

## Quick Manual Method:

1. Create Space at https://huggingface.co/new-space
2. In your Space, go to **Files** tab
3. Upload these files from your project directory:
   - `app.py`
   - `papago_translation.py`
   - Copy `requirements_hf.txt` content → paste as `requirements.txt`
   - Copy `README_HF.md` content → paste as `README.md`

The Space will automatically build after files are uploaded!


