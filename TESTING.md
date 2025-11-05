🌐 Hugging Face Space live demo: [https://huggingface.co/spaces/zxc1232/koreantoenglish](https://huggingface.co/spaces/zxc1232/koreantoenglish) — No installation required—try it in your browser!

# Testing the App Locally

## App Status
✅ App is running on: **http://127.0.0.1:7860**

## To Test with API Credentials

The app now requires Papago API credentials from environment variables. To test locally:

### Option 1: Set Environment Variables
```bash
export PAPAGO_CLIENT_ID="your_client_id"
export PAPAGO_CLIENT_SECRET="your_client_secret"
source venv/bin/activate
python app.py
```

### Option 2: Create a .env file (for testing)
```bash
# Create .env file (don't commit this!)
echo "PAPAGO_CLIENT_ID=your_client_id" > .env
echo "PAPAGO_CLIENT_SECRET=your_client_secret" >> .env
```

Then modify app.py temporarily to load from .env:
```python
from dotenv import load_dotenv
load_dotenv()
```

### Option 3: Test the Interface (without API)
The app will show an error message if credentials aren't set, but you can still test:
- The interface loads correctly
- File upload works
- Error messages display properly

## Test Checklist

- [ ] App loads at http://127.0.0.1:7860
- [ ] File upload interface works
- [ ] Error message shows if credentials missing
- [ ] With credentials: transcription works
- [ ] With credentials: SRT file generates
- [ ] With credentials: Video with subtitles generates (if video uploaded)

## Current Features

✅ No credential input fields (uses environment variables)
✅ Automatic Whisper large-v3 model selection
✅ SRT file output for CapCut
✅ Video with burned-in subtitles (for video inputs)
✅ Clean, simple interface

Open http://127.0.0.1:7860 in your browser to test!


