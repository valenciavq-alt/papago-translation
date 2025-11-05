🌐 Hugging Face Space live demo: [https://huggingface.co/spaces/zxc1232/koreantoenglish](https://huggingface.co/spaces/zxc1232/koreantoenglish) — No installation required—try it in your browser!

# Sync Script Usage

## Quick Sync

To sync your main repository to Hugging Face Space:

```bash
./sync_to_hf.sh
```

Or with a custom commit message:

```bash
./sync_to_hf.sh "Add new feature: video subtitle burning"
```

## What It Does

1. ✅ Copies necessary files from main repo to `hf-space/`:
   - `app.py`
   - `papago_translation.py`
   - `requirements_hf.txt` → `requirements.txt`
   - `README_HF.md` → `README.md`

2. ✅ Commits and pushes to Hugging Face Space
3. ✅ Optionally pushes to GitHub too

## Files Synced

- `app.py` - Main Gradio application
- `papago_translation.py` - Translation module
- `requirements_hf.txt` → `requirements.txt` (renamed)
- `README_HF.md` → `README.md` (renamed)

## Example Workflow

```bash
# 1. Make changes to app.py in main repo
vim app.py

# 2. Sync to Hugging Face Space
./sync_to_hf.sh "Update app.py with new features"

# 3. Space rebuilds automatically
# 4. Check logs: https://huggingface.co/spaces/zxc1232/koreantoenglish/logs
```

## Manual Sync

If you prefer manual control:

```bash
cd hf-space
cp ../app.py .
cp ../papago_translation.py .
cp ../requirements_hf.txt requirements.txt
cp ../README_HF.md README.md
git add .
git commit -m "Your message"
git push origin main
```

The sync script automates this process!


