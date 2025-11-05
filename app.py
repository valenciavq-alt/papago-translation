"""
Hugging Face Space Demo for Papago Translation
Transcribes Korean audio/video and creates bilingual subtitles using Whisper and Papago API.
Generates SRT file and video with burned-in subtitles.
"""

# Monkey patch to fix Gradio schema generation bug
# This MUST be done BEFORE importing gradio
try:
    from gradio_client import utils as client_utils
    
    # Patch get_type to handle boolean schemas
    original_get_type = client_utils.get_type
    
    def patched_get_type(schema):
        # Fix: Handle case where schema is a boolean (for additionalProperties)
        if isinstance(schema, bool):
            return "Any"
        # Also check if schema is a dict before checking 'const' in it
        if not isinstance(schema, dict):
            return "Any"
        return original_get_type(schema)
    
    client_utils.get_type = patched_get_type
    
    # Also patch _json_schema_to_python_type to handle additionalProperties boolean
    original_json_schema_to_python_type = client_utils._json_schema_to_python_type
    
    def patched_json_schema_to_python_type(schema, defs=None):
        # Handle case where additionalProperties is a boolean
        if isinstance(schema, dict) and 'additionalProperties' in schema:
            if isinstance(schema['additionalProperties'], bool):
                # Convert boolean to dict format
                schema = schema.copy()
                schema['additionalProperties'] = {}
        return original_json_schema_to_python_type(schema, defs)
    
    client_utils._json_schema_to_python_type = patched_json_schema_to_python_type
except Exception as e:
    import warnings
    warnings.warn(f"Failed to patch Gradio schema bug: {e}")

# Now import gradio AFTER patching
import os
import gradio as gr
import tempfile
import subprocess
try:
    import whisper
    USE_WHISPER = True
except ImportError:
    USE_WHISPER = False
        
from papago_translation import PapagoTranslator, segments_to_srt, timestamp_to_srt


def create_ass_subtitles(segments, translator):
    """Create ASS subtitle file for burning into video."""
    ass_lines = [
        "[Script Info]",
        "Title: Bilingual Subtitles",
        "ScriptType: v4.00+",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        "Style: Korean,Arial,24,&HA7C1E8,&HFFFFFF,&H000000,&H80000000,0,0,0,0,100,100,0,0,1,2,1,2,10,10,10,1",
        "Style: English,Arial,20,&HFFFFFF,&HFFFFFF,&H000000,&H80000000,0,0,0,0,100,100,0,0,1,2,1,2,10,10,50,1",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"
    ]
    
    for seg in segments:
        start = seg["start"]
        end = seg["end"]
        text_ko = seg["text"].strip()
        text_en = translator.translate_ko_to_en(text_ko)
        
        # Format timestamps for ASS (HH:MM:SS.cc)
        start_ass = timestamp_to_ass(start)
        end_ass = timestamp_to_ass(end)
        
        # Korean line (top)
        ass_lines.append(f"Dialogue: 0,{start_ass},{end_ass},Korean,,0,0,0,,{text_ko}")
        # English line (bottom)
        ass_lines.append(f"Dialogue: 0,{start_ass},{end_ass},English,,0,0,0,,{text_en}")
    
    return "\n".join(ass_lines)


def timestamp_to_ass(seconds: float) -> str:
    """Convert seconds to ASS timestamp format (HH:MM:SS.cc)."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    cs = int((seconds * 100) % 100)  # centiseconds
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def burn_subtitles_to_video(video_path: str, segments: list, translator: PapagoTranslator, output_path: str):
    """Burn subtitles into video using ffmpeg."""
    # Create temporary ASS subtitle file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ass', delete=False, encoding='utf-8') as f:
        ass_content = create_ass_subtitles(segments, translator)
        f.write(ass_content)
        ass_file = f.name
    
    try:
        # Escape the file path for ffmpeg
        import shlex
        ass_file_escaped = shlex.quote(ass_file)
        
        # Use ffmpeg to burn subtitles
        # For Korean fonts, use a font that's likely available: Arial or DejaVu Sans
        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-vf', f"subtitles={ass_file_escaped}:force_style='FontName=Arial,FontSize=24,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,BackColour=&H80000000,BorderStyle=1,Outline=2,Shadow=1'",
            '-c:a', 'copy',
            '-y',  # Overwrite output file
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            raise Exception(f"FFmpeg error: {result.stderr}")
        
        return output_path
    finally:
        # Clean up temporary ASS file
        if os.path.exists(ass_file):
            os.unlink(ass_file)


def transcribe_and_translate(
    audio_file,
    progress=gr.Progress()
):
    """
    Transcribe Korean audio and create bilingual subtitles.
    Also generates video with burned-in subtitles.
    
    Args:
        audio_file: Uploaded audio/video file
        progress: Gradio progress tracker
        
    Returns:
        Tuple of (SRT file, video with subtitles, Korean text, English text)
    """
    if audio_file is None:
        return None, None, "Please upload an audio or video file.", None
    
    # Get credentials from environment variables (Hugging Face Secrets)
    papago_client_id = os.getenv("PAPAGO_CLIENT_ID")
    papago_client_secret = os.getenv("PAPAGO_CLIENT_SECRET")
    
    if not papago_client_id or not papago_client_secret:
        return None, None, "Error: Papago API credentials not found in Space secrets. Please add PAPAGO_CLIENT_ID and PAPAGO_CLIENT_SECRET in Settings → Secrets.", None
    
    try:
        # Handle Gradio File object
        if audio_file is None:
            return None, None, "Please upload an audio or video file.", None
        
        # Extract file path from Gradio File object
        if isinstance(audio_file, str):
            audio_path = audio_file
        elif hasattr(audio_file, 'name'):
            audio_path = audio_file.name
        elif isinstance(audio_file, dict) and 'name' in audio_file:
            audio_path = audio_file['name']
        else:
            audio_path = str(audio_file)
        
        # Check if input is video or audio
        is_video = any(audio_path.lower().endswith(ext) for ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm'])
        
        # Use best Whisper model automatically (large-v3)
        whisper_model = "large-v3"
        
        # Load Whisper model
        progress(0.1, desc="Loading Whisper model (large-v3)...")
        if USE_WHISPER:
            model = whisper.load_model(whisper_model)
            # Transcribe audio
            progress(0.3, desc="Transcribing audio...")
            result = model.transcribe(
                audio_path,
                language="ko",
                task="transcribe"
            )
            segments = result["segments"]
        else:
            return None, None, "Error: Whisper package not installed.", None
        
        if not segments:
            return None, None, "No speech detected in the audio.", None
        
        # Initialize translator
        progress(0.5, desc="Initializing translator...")
        translator = PapagoTranslator(papago_client_id, papago_client_secret)
        
        # Generate bilingual SRT with progress tracking
        progress(0.6, desc=f"Translating {len(segments)} segments...")
        srt_content = segments_to_srt(segments, translator, show_progress=False, progress_callback=progress)
        
        # Extract Korean and English text for preview
        korean_text = "\n".join([seg["text"].strip() for seg in segments])
        
        # Translate full text for preview
        progress(0.7, desc="Generating English translation preview...")
        english_text = translator.translate_ko_to_en(korean_text)
        
        # Save SRT to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.srt', delete=False, encoding='utf-8') as f:
            f.write(srt_content)
            srt_file = f.name
        
        # Generate video with burned-in subtitles if input is video
        video_output = None
        if is_video:
            progress(0.8, desc="Burning subtitles into video...")
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as f:
                video_output_path = f.name
            
            try:
                burn_subtitles_to_video(audio_path, segments, translator, video_output_path)

                if os.path.exists(video_output_path):
                    video_output = video_output_path
            except Exception as e:
                progress(0.9, desc=f"Video processing warning: {str(e)}")
                # Continue without video if ffmpeg fails
                # Clean up failed output file
                if os.path.exists(video_output_path):
                    os.unlink(video_output_path)
        
        progress(1.0, desc="Complete!")
        
        return srt_file, video_output, korean_text, english_text
        
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        import traceback
        traceback.print_exc()
        return None, None, error_msg, None


# Create Gradio interface
with gr.Blocks(title="Papago Korean Translation", theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        """
        # 🎤 Korean Audio Transcription & Translation
        
        Upload Korean audio or video files to:
        - Transcribe Korean speech using Whisper (large-v3 model)
        - Translate to English using Papago API
        - Generate **SRT subtitle file** for editing in CapCut
        - Generate **video with burned-in subtitles** (Korean + English)
        
        **Note:** Papago API credentials are configured in Space settings (Secrets).
        """
    )
    
    with gr.Row():
        with gr.Column():
            audio_input = gr.File(
                label="Audio/Video File",
                file_types=[".mp3", ".wav", ".mp4", ".avi", ".m4a", ".flac", ".mov", ".mkv"]
            )
            
            process_btn = gr.Button("🚀 Process", variant="primary", size="lg")
        
        with gr.Column():
            srt_output = gr.File(
                label="📄 SRT Subtitle File (for CapCut)"
            )
            
            video_output = gr.Video(
                label="🎬 Video with Burned-in Subtitles (Korean + English)"
            )
            
            with gr.Tabs():
                with gr.Tab("Korean Transcription"):
                    korean_output = gr.Textbox(
                        label="Korean Text",
                        lines=15,
                        max_lines=20,
                        placeholder="Korean transcription will appear here..."
                    )
                
                with gr.Tab("English Translation"):
                    english_output = gr.Textbox(
                        label="English Translation",
                        lines=15,
                        max_lines=20,
                        placeholder="English translation will appear here..."
                    )
    
    gr.Markdown(
        """
        ### 📥 How to use:
        1. Upload an audio or video file containing Korean speech
        2. Click "Process" to transcribe and translate
        3. Download:
           - **SRT file** - Use this in CapCut for editing
           - **Video with subtitles** - Ready-to-use video with Korean and English subtitles burned in
        
        ### 💡 Tips:
        - Uses Whisper large-v3 model automatically for best accuracy
        - Video processing requires ffmpeg (already installed)
        - SRT file contains Korean (top) and English (bottom) for easy editing in CapCut
        """
    )
    
    # Connect the processing function
    process_btn.click(
        fn=transcribe_and_translate,
        inputs=[audio_input],
        outputs=[srt_output, video_output, korean_output, english_output]
    )


if __name__ == "__main__":
    # Let Gradio auto-detect for Hugging Face Spaces
    demo.launch()
