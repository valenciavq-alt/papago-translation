---
title: Papago Korean Translation
emoji: 🎤
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
license: mit
---

# 🎤 Papago Korean Translation

Transcribe Korean audio/video files and create bilingual subtitles using OpenAI Whisper and Papago API. Generates both SRT files for editing and videos with burned-in subtitles.

## Features

- 🎯 **Korean Speech Recognition** - Uses Whisper large-v3 model automatically for best accuracy
- 🌐 **Automatic Translation** - Translates Korean to English using Papago API
- 📝 **SRT Subtitle File** - Downloadable SRT file perfect for editing in CapCut
- 🎬 **Video with Subtitles** - Automatically generates video with Korean and English subtitles burned in
- 🔒 **Secure Credentials** - Papago API credentials stored in Space Secrets (no need to enter manually)

## How to Use

1. **Configure API Credentials** (First time only):
   - Go to Space Settings → Secrets
   - Add `PAPAGO_CLIENT_ID` with your Papago Client ID
   - Add `PAPAGO_CLIENT_SECRET` with your Papago Client Secret
   
2. **Upload Audio/Video**: Select a file containing Korean speech (MP3, WAV, MP4, AVI, M4A, FLAC, MOV, MKV)

3. **Process**: Click "Process" to transcribe and translate (uses Whisper large-v3 automatically)

4. **Download**:
   - **SRT File** - Use in CapCut for editing subtitles
   - **Video with Subtitles** - Ready-to-use video with Korean (top) and English (bottom) subtitles burned in

## API Setup

To configure Papago API credentials:

1. Visit [Naver Cloud Platform](https://www.ncloud.com/)
2. Sign up for an account
3. Navigate to "AI·NAVER API" → "Papago Translation"
4. Create an application and get your Client ID and Client Secret
5. **Add to Space Secrets**:
   - Go to your Space → Settings → Secrets
   - Add secret: `PAPAGO_CLIENT_ID` = your Client ID
   - Add secret: `PAPAGO_CLIENT_SECRET` = your Client Secret

## Model

- **Whisper large-v3** - Automatically selected for best accuracy (no manual selection needed)

## Output Format

### SRT File:
- Korean text (top line, blue color)
- English translation (bottom line, white color)
- Timestamps synchronized with audio
- Perfect for importing into CapCut for editing

### Video with Subtitles:
- Korean subtitles at the top (blue color)
- English subtitles at the bottom (white color)
- Hardcoded into video (cannot be toggled off)
- Ready to use or share

## Limitations

- Requires Papago API credentials configured in Space Secrets
- Processing time depends on audio/video length
- Best results with clear Korean speech
- Video processing requires ffmpeg (already installed in Space)

## License

MIT License

