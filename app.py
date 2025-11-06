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
import time
import gradio as gr
import tempfile
import subprocess
try:
    import whisper
    USE_WHISPER = True
except ImportError:
    USE_WHISPER = False
        
from papago_translation import PapagoTranslator, segments_to_srt, timestamp_to_srt


def _extract_file_path(file_obj) -> str | None:
    if file_obj is None:
        return None
    if isinstance(file_obj, str):
        return file_obj
    if hasattr(file_obj, 'name'):
        return file_obj.name
    if isinstance(file_obj, dict) and 'name' in file_obj:
        return file_obj['name']
    try:
        return str(file_obj)
    except Exception:
        return None


def _format_eta(seconds_total: int) -> str:
    minutes = seconds_total // 60
    seconds = seconds_total % 60
    if minutes > 0:
        return f"{minutes}m {seconds}s"
    return f"{seconds}s"


def on_upload_complete(file_obj):
    """Return upload-complete message. Processing continues server-side even if tab closes."""
    base = (
        "✅ Upload complete. When you tap ‘Process’, processing runs on the server and will continue even if you leave the app."
    )
    return base


def get_media_duration_seconds(media_path: str) -> float | None:
    """Return media duration in seconds using ffprobe, or None if unknown."""
    try:
        probe = subprocess.run(
            [
                'ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',
                media_path
            ], capture_output=True, text=True, timeout=15
        )
        if probe.returncode == 0:
            val = probe.stdout.strip()
            return float(val) if val else None
    except Exception:
        pass
    return None


def create_ass_subtitles(segments, translator, play_res_x: int | None = None, play_res_y: int | None = None):
    """Create ASS subtitle file for burning into video.
    Optionally specify PlayResX/PlayResY to make Fontsize ~pixels.
    """
    ass_lines = [
        "[Script Info]",
        "Title: Bilingual Subtitles",
        "ScriptType: v4.00+",
    ]
    # Set PlayRes to the input video resolution if known; this makes fontsize ≈ pixels
    if isinstance(play_res_x, int) and isinstance(play_res_y, int) and play_res_x > 0 and play_res_y > 0:
        ass_lines.append(f"PlayResX: {play_res_x}")
        ass_lines.append(f"PlayResY: {play_res_y}")
    ass_lines += [
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        # Korean style: 12pt NanumGothic, light blue (#A7C1E8), positioned above English at bottom
        # Alignment=2 = bottom center, MarginV=44 = above English
        # Encoding=1 for Unicode support, NanumGothic is a Korean font
        "Style: Korean,NanumGothic,36,&H00FFFFFF&,&H00FFFFFF&,&H20202020&,&H00000000&,0,0,0,0,100,100,0,0,1,0.4,0.8,2,10,10,160,1",
        # English style: unified spec, positioned at bottom
        # Alignment=2 = bottom center, MarginV=50 near bottom edge
        "Style: English,NanumGothic,36,&H00FFFFFF&,&H00FFFFFF&,&H20202020&,&H00000000&,0,0,0,0,100,100,0,0,1,0.4,0.8,2,10,10,120,1",
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
        
        # Korean line (above English) using unified spec; layer 1 to ensure it renders above English
        ko_colored = f"{{\\an2\\fs36\\c&H00FFFFFF&\\3c&H20202020&}}{text_ko}"
        ass_lines.append(f"Dialogue: 1,{start_ass},{end_ass},Korean,,0,0,160,,{ko_colored}")
        
        # English line (bottom) using unified spec; layer 0
        en_colored = f"{{\\an2\\fs36\\c&H00FFFFFF&\\3c&H20202020&}}{text_en}"
        ass_lines.append(f"Dialogue: 0,{start_ass},{end_ass},English,,0,0,120,,{en_colored}")
        # Two line breaks between segments (empty line)
        ass_lines.append("")
    
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
    # Create temporary ASS subtitle file with UTF-8 encoding
    # Use UTF-8 with BOM to ensure Korean characters display correctly
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ass', delete=False, encoding='utf-8-sig') as f:
        # Probe video resolution to set PlayRes for pixel-accurate fontsize
        try:
            probe = subprocess.run(
                [
                    'ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height','-of','csv=s=x:p=0',
                    video_path
                ], capture_output=True, text=True, timeout=15
            )
            if probe.returncode == 0 and 'x' in probe.stdout.strip():
                w_str, h_str = probe.stdout.strip().split('x')
                play_w = int(w_str)
                play_h = int(h_str)
            else:
                play_w = play_h = None
        except Exception:
            play_w = play_h = None

        ass_content = create_ass_subtitles(segments, translator, play_res_x=play_w, play_res_y=play_h)
        f.write(ass_content)
        ass_file = f.name
    
    try:
        # Use raw ASS path (no shell quoting needed for /tmp paths)
        ass_file_escaped = ass_file
        
        # Use ffmpeg to burn subtitles
        # Try to find NanumGothic font in common locations
        # NanumGothic is a Korean font that should be available or can be installed
        font_dirs = [
            '/usr/share/fonts/truetype/nanum/',
            '/usr/share/fonts/truetype/',
            '/usr/share/fonts/TTF/',
            '/usr/share/fonts/opentype/',
            '/System/Library/Fonts/Supplemental/',
            '/usr/share/fonts/truetype/liberation/'
        ]
        
        # Find existing font directories
        existing_font_dirs = [d for d in font_dirs if os.path.exists(d)]
        
        # Keep only FontName in force_style so colors and sizes defined in ASS are preserved
        subtitle_filter = (
            f"subtitles={ass_file_escaped}:charenc=UTF-8:force_style=FontName=NanumGothic"
        )
        
        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-vf', subtitle_filter,
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-c:a', 'aac',
            '-b:a', '192k',
            '-y',  # Overwrite output file
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            error_msg = f"FFmpeg error (code {result.returncode}): {result.stderr}"
            if result.stdout:
                error_msg += f"\nFFmpeg output: {result.stdout}"
            raise Exception(error_msg)
        
        # Verify output file exists and has content
        if not os.path.exists(output_path):
            raise Exception("FFmpeg completed but output file was not created")
        if os.path.getsize(output_path) == 0:
            raise Exception("FFmpeg created an empty output file")
        
        return output_path
    finally:
        # Clean up temporary ASS file
        if os.path.exists(ass_file):
            os.unlink(ass_file)


def transcribe_and_translate(
    audio_file,
    url_input: str | None = None,
    progress=gr.Progress()
):
    """
    Transcribe Korean audio and create bilingual subtitles.
    Also generates video with burned-in subtitles.
    
    Args:
        audio_file: Uploaded audio/video file
        progress: Gradio progress tracker
        
    Returns:
        Tuple of (SRT file, video with subtitles, Korean text, English text, SRT ETA text, Video ETA text)
    """
    if audio_file is None and not url_input:
        yield None, None, "Please upload an audio or video file or provide a URL.", None
        return
    
    # Get credentials from environment variables (Hugging Face Secrets)
    papago_client_id = os.getenv("PAPAGO_CLIENT_ID")
    papago_client_secret = os.getenv("PAPAGO_CLIENT_SECRET")
    
    if not papago_client_id or not papago_client_secret:
        yield None, None, "Error: Papago API credentials not found in Space secrets. Please add PAPAGO_CLIENT_ID and PAPAGO_CLIENT_SECRET in Settings → Secrets.", None
        return
    
    try:
        # Handle Gradio File object
        if audio_file is None and not url_input:
            yield None, None, "Please upload an audio or video file or provide a URL.", None
            return
        
        # Determine source: uploaded file or server-side download from URL
        if audio_file is not None:
            # Extract file path from Gradio File object
            if isinstance(audio_file, str):
                audio_path = audio_file
            elif hasattr(audio_file, 'name'):
                audio_path = audio_file.name
            elif isinstance(audio_file, dict) and 'name' in audio_file:
                audio_path = audio_file['name']
            else:
                audio_path = str(audio_file)
        else:
            # Download from URL to temp file on server (faster than mobile upload)
            try:
                import urllib.request
                progress(0.08, desc="Fetching media from URL on server...")
                tmp_dir = tempfile.gettempdir()
                url_fname = f"download_{int(time.time())}.bin"
                audio_path = os.path.join(tmp_dir, url_fname)
                urllib.request.urlretrieve(url_input, audio_path)
            except Exception as e:
                yield None, None, f"Failed to download from URL: {e}", None
                return
        
        # Check if input is video or audio
        is_video = any(audio_path.lower().endswith(ext) for ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm'])
        print(f"📹 Input file: {audio_path}")
        print(f"📹 Is video: {is_video}")
        print(f"📹 File exists: {os.path.exists(audio_path)}")
        if os.path.exists(audio_path):
            print(f"📹 File size: {os.path.getsize(audio_path) / 1024 / 1024:.2f} MB")
        
        # Pre-calc video duration for ETA (if video)
        vid_duration = get_media_duration_seconds(audio_path) if is_video else None

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
            yield None, None, "Error: Whisper package not installed.", None
            return
        
        if not segments:
            yield None, None, "No speech detected in the audio.", None
            return
        
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
        
        # Save SRT with a stable filename, UTF-8 encoding (no BOM), and Unix LF line endings
        srt_basename = f"subtitles_{int(time.time())}.srt"
        srt_file = os.path.join(tempfile.gettempdir(), srt_basename)
        try:
            # Normalize line endings to LF and ensure SRT blocks are separated by a single blank line
            srt_norm = srt_content.replace("\r\n", "\n").replace("\r", "\n")
            # Collapse triple blank lines to double, then ensure final double newline
            while "\n\n\n" in srt_norm:
                srt_norm = srt_norm.replace("\n\n\n", "\n\n")
            if not srt_norm.endswith("\n\n"):
                srt_norm = srt_norm.rstrip("\n") + "\n\n"
            # Write with LF endings and UTF-8 (no BOM)
            with open(srt_file, 'w', encoding='utf-8', newline='\n') as f:
                f.write(srt_norm)
        except Exception:
            # Fallback to raw content if normalization fails
            with open(srt_file, 'w', encoding='utf-8') as f:
                f.write(srt_content)
        
        # Yield SRT immediately so user can download it (don't wait for video)
        srt_label_ready = "📄 SRT Subtitle File (for CapCut) ✅ Ready"
        yield (
            gr.update(value=srt_file, label=srt_label_ready),
            gr.update(value=None, label="🎬 Video with Burned-in Subtitles (Korean + English) ⏳ Processing..."),  # Video not ready yet
            korean_text,
            english_text,
        )
        
        # Generate video with burned-in subtitles if input is video
        video_output = None
        video_error = None
        if is_video:
            progress(0.8, desc=f"Burning subtitles into video...")
            # Use a more accessible temp directory for video output
            temp_dir = tempfile.gettempdir()
            video_output_path = os.path.join(temp_dir, f"subtitled_{int(time.time())}.mp4")
            
            try:
                # Verify input video exists
                if not os.path.exists(audio_path):
                    raise Exception(f"Input video file not found: {audio_path}")
                
                progress(0.82, desc="Creating subtitle file...")
                burn_subtitles_to_video(audio_path, segments, translator, video_output_path)
                
                # Verify output
                if not os.path.exists(video_output_path):
                    raise Exception(f"Video output file was not created: {video_output_path}")
                
                video_size = os.path.getsize(video_output_path)
                if video_size == 0:
                    raise Exception(f"Video output file is empty (0 bytes): {video_output_path}")
                
                video_output = video_output_path
                progress(0.95, desc=f"✅ Video created successfully! ({video_size / 1024 / 1024:.1f} MB)")
                
            except Exception as e:
                error_details = str(e)
                import traceback
                tb_str = traceback.format_exc()
                # Log to console for debugging
                print(f"\n❌ Video processing error:")
                print(f"Error: {error_details}")
                print(f"Traceback:\n{tb_str}")
                video_error = f"⚠️ Video processing failed:\n{error_details}"
                progress(0.9, desc=video_error)
                # Clean up failed output file
                if os.path.exists(video_output_path):
                    try:
                        os.unlink(video_output_path)
                    except:
                        pass
        else:
            progress(0.8, desc="Skipping video generation (audio file, not video)")
        
        progress(1.0, desc="Complete!")
        
        # Append video error to English text if video failed (so user can see it)
        if video_error:
            english_text = f"{english_text}\n\n{video_error}"
        
        # Final yield with video ready (or None if not video or failed)
        srt_label_final = "📄 SRT Subtitle File (for CapCut) ✅"
        video_label_final = "🎬 Video with Burned-in Subtitles (Korean + English)"
        if video_output:
            video_label_final = f"{video_label_final} ✅"
        elif is_video:
            video_label_final = f"{video_label_final} ❌ Failed"
        else:
            video_label_final = f"{video_label_final} (Audio only - no video)"
        yield (
            gr.update(value=srt_file, label=srt_label_final),
            gr.update(value=video_output, label=video_label_final),
            korean_text,
            english_text,
        )
        
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        import traceback
        traceback.print_exc()
        yield None, None, error_msg, None


# Create Gradio interface
with gr.Blocks(title="Papago Korean Translation", theme=gr.themes.Soft()) as demo:
    # HERO / BANNER
    gr.Markdown(
        """
        ## Korean-to-English Localized Translator – For Native Korean, Video & Audio
        
        한국어 사용자와 현지 방언을 위한 최고의 번역 도구입니다. 오디오와 비디오 모두 지원합니다.
        """
    )
    # Features block (directly under subtitle)
    gr.Markdown(
        """
        #### Features
        - 🎯 **Korean Speech Recognition** - Uses Whisper large-v3 model automatically for best accuracy
        - 🌐 **Automatic Translation** - Translates Korean to English using Papago API
        - 📝 **SRT Subtitle File** - Downloadable SRT file perfect for editing in CapCut
        - 🎬 **Video with Subtitles** - Automatically generates video with Korean and English subtitles burned in
        """
    )
    # (Removed inline Features/How to use block to avoid duplication)
    
    # Removed step headers to avoid redundancy

    # NOTE (avoid repeating features listed below)
    gr.Markdown("Note: Papago API credentials are configured in Space settings (Secrets).")

    with gr.Row():
        with gr.Column():
            upload_type = gr.Radio(
                ["Video", "Audio"],
                value="Video",
                label="Upload Type"
            )
            audio_input = gr.File(
                label="Audio/Video File (한국어로 된 영상 또는 음성을 업로드하세요)",
                file_types=[".mp3", ".wav", ".mp4", ".avi", ".m4a", ".flac", ".mov", ".mkv"]
            )
            upload_status = gr.Markdown("", elem_id="upload-status")
            url_input = gr.Textbox(
                label="Or paste a direct media URL (optional)",
                placeholder="https://... (MP4/MOV/MP3/WAV)",
            )
            
            process_btn = gr.Button("🚀 Process", variant="primary", size="lg")
            gr.Markdown(
                """
                Upload auto-starts processing when finished. You can switch apps after upload—processing continues in the background.
                
                Tip: Larger videos upload slower over mobile data. For fastest results, use Wi‑Fi.
                """
            )
        
        with gr.Column():
            video_output = gr.Video(label="🎬 Video with Burned-in Subtitles (Korean + English)")
            srt_output = gr.File(label="📄 SRT Subtitle File (for CapCut)")
            
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
    
    # BOTTOM: HOW TO USE + NOTE
    gr.Markdown(
        """
        ### 📥 How to use:
        - Upload an audio or video file containing Korean speech  
        - Click ‘Process’ to transcribe and translate  
        - Download: **SRT file**; **Video with subtitles**
        """
    )

    # FOOTER (removed on request)
    
    # Connect the processing function (manual trigger)
    process_btn.click(
        fn=transcribe_and_translate,
        inputs=[audio_input, url_input],
        outputs=[srt_output, video_output, korean_output, english_output]
    )

    # Mark upload completion explicitly to guide mobile usage
    audio_input.upload(
        fn=on_upload_complete,
        inputs=[audio_input],
        outputs=[upload_status]
    )

    # Auto-start processing immediately after upload so job is queued server-side
    audio_input.upload(
        fn=transcribe_and_translate,
        inputs=[audio_input],
        outputs=[srt_output, video_output, korean_output, english_output]
    )


if __name__ == "__main__":
    # Enable queue with increased timeout to prevent mobile disconnection issues
    # Jobs continue server-side even if client disconnects
    demo.queue(
        default_concurrency_limit=2,
        max_size=64,
        status_update_rate=1
    )
    # Let Gradio auto-detect for Hugging Face Spaces
    demo.launch()
