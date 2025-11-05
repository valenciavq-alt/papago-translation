# Papago Translation

A Python module for transcribing Korean videos and creating bilingual subtitles using OpenAI Whisper and Papago API.

## Features

- Transcribe Korean audio/video using Whisper
- Translate Korean subtitles to English using Papago API
- Generate bilingual SRT subtitle files (Korean + English)
- Format subtitles with custom styling

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```python
from papago_translation import PapagoTranslator, segments_to_srt

# Initialize translator
translator = PapagoTranslator(
    client_id="your_client_id",
    client_secret="your_client_secret"
)

# Translate text
english_text = translator.translate_ko_to_en("안녕하세요")

# Generate SRT from Whisper segments
segments = [
    {"start": 0.0, "end": 2.0, "text": "안녕하세요"},
    {"start": 2.5, "end": 5.0, "text": "반갑습니다"}
]
srt_content = segments_to_srt(segments, translator)
```

## Testing

Run tests with pytest:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=papago_translation --cov-report=html
```

## Gradio Web App (Hugging Face Space)

Run the interactive web interface:

```bash
# Using the helper script (recommended)
./run_app.sh

# Or manually activate virtual environment and run
source venv/bin/activate
python app.py
```

The app will start on `http://127.0.0.1:7860`

**Note:** This project uses Python 3.12 for compatibility. A virtual environment has been set up at `venv/`.

## Project Structure

- `papago_translation.py` - Main module with translation and SRT generation functions
- `app.py` - Gradio web interface for Hugging Face Spaces
- `test_papago_translation.py` - Unit tests
- `requirements.txt` - Python dependencies
- `pytest.ini` - Pytest configuration
- `venv/` - Python 3.12 virtual environment
- `run_app.sh` - Quick start script for the web app

