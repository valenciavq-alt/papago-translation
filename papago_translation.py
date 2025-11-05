"""
Papago Translation Module
Transcribes Korean video and creates bilingual subtitles using Whisper and Papago API.
"""

import urllib.request
import urllib.parse
import urllib.error
import json
import time
from typing import List, Dict, Any


class PapagoTranslator:
    """Handles translation using Papago API."""
    
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.url = "https://papago.apigw.ntruss.com/nmt/v1/translation"
    
    def translate_ko_to_en(self, text: str, timeout: int = 30) -> str:
        """Translate Korean text to English using Papago API.
        
        Args:
            text: Korean text to translate
            timeout: Request timeout in seconds
            
        Returns:
            Translated English text, or error message if translation fails
        """
        if not text.strip():
            return ""
        
        enc_text = urllib.parse.quote(text)
        data = f"source=ko&target=en&text={enc_text}"
        
        req = urllib.request.Request(self.url)
        req.add_header("X-NCP-APIGW-API-KEY-ID", self.client_id)
        req.add_header("X-NCP-APIGW-API-KEY", self.client_secret)
        
        try:
            with urllib.request.urlopen(req, data=data.encode("utf-8"), timeout=timeout) as res:
                response = json.loads(res.read().decode("utf-8"))
                if "message" in response and "result" in response["message"]:
                    return response["message"]["result"]["translatedText"]
                else:
                    return f"[Translation error: Unexpected response format]"
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8") if hasattr(e, 'read') else str(e)
            return f"[Translation error: HTTP {e.code} - {error_body}]"
        except Exception as e:
            return f"[Translation error: {str(e)}]"


def timestamp_to_srt(seconds: float) -> str:
    """Convert seconds to SRT timestamp format.
    
    Args:
        seconds: Time in seconds
        
    Returns:
        SRT timestamp string (HH:MM:SS,mmm)
    """
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds * 1000) % 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def segments_to_srt(segments: List[Dict[str, Any]], translator: PapagoTranslator, 
                   show_progress: bool = False, progress_callback=None) -> str:
    """Convert Whisper segments to bilingual SRT format.
    
    Args:
        segments: List of segment dicts with 'start', 'end', and 'text' keys
        translator: PapagoTranslator instance
        show_progress: Whether to print progress updates
        progress_callback: Optional function(progress, desc) to update progress
        
    Returns:
        SRT file content as string
    """
    lines = []
    start_time = time.time()
    total_segments = len(segments)
    
    for i, seg in enumerate(segments):
        start = seg["start"]
        end = seg["end"]
        text_ko = seg["text"].strip()
        
        try:
            en = translator.translate_ko_to_en(text_ko)
            # Fallback if translation failed
            if en.startswith("[Translation error"):
                en = "[Translation failed]"
        except Exception as e:
            en = f"[Translation error: {str(e)}]"
        
        # Smaller font, KR above EN
        ko_line = "{\\fs16\\c&HA7C1E8&}" + text_ko
        en_line = "{\\fs15\\c&HFFFFFF&}" + en
        lines.append(f"{i+1}\n{timestamp_to_srt(start)} --> {timestamp_to_srt(end)}\n{ko_line}\\N{en_line}\n")
        
        # Update progress - use try/except to avoid issues with Progress object evaluation
        if total_segments > 0:
            try:
                if progress_callback is not None:
                    progress_value = 0.6 + (0.2 * (i + 1) / total_segments)  # 60% to 80%
                    progress_callback(progress_value, desc=f"Translating segment {i+1}/{total_segments}...")
            except (AttributeError, IndexError, TypeError):
                # If progress callback fails, continue silently
                pass
        
        if show_progress and (i+1) % max(1, len(segments)//10) == 0:
            elapsed = time.time() - start_time
            per_seg = elapsed / (i+1)
            remaining = (len(segments) - (i+1)) * per_seg
            print(f"⏳ {i+1}/{len(segments)} done — ~{remaining/60:.1f} min left")
    
    return "\n".join(lines)

