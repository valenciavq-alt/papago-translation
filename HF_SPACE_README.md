🌐 Try it online: [https://huggingface.co/spaces/zxc1232/koreantoenglish](https://huggingface.co/spaces/zxc1232/koreantoenglish) — Papago Korean-English Subtitle Generator (No installation required—try it in your browser!)

# Hugging Face Space Setup

This directory contains code for deploying to Hugging Face Spaces.

## Files for Hugging Face Space

- `app.py` - Main Gradio application for the Space
- `requirements.txt` - Python dependencies (includes Gradio)
- `README_HF.md` - Space description and metadata

## Deploying to Hugging Face Spaces

1. **Create a new Space** on [Hugging Face Spaces](https://huggingface.co/spaces)

2. **Set Space Configuration**:
   - SDK: Gradio
   - Hardware: CPU (or GPU for faster processing)
   - Visibility: Public or Private

3. **Upload Files**:
   - Upload `app.py` as the main application file
   - Upload `papago_translation.py` (the core module)
   - Upload `requirements.txt` for dependencies
   - Optionally upload `README_HF.md` or use the web interface to configure

4. **Environment Variables** (Optional):
   - You can set default Papago credentials as Space secrets:
     - `PAPAGO_CLIENT_ID`
     - `PAPAGO_CLIENT_SECRET`

## Local Testing

Test the Gradio app locally before deploying:

```bash
pip install -r requirements.txt
python app.py
```

The app will start on `http://127.0.0.1:7860`

## Notes

- The Space requires users to provide their own Papago API credentials
- For production use, consider setting up API credentials as Space secrets
- Large Whisper models require significant memory; consider GPU instances for better performance

