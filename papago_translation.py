"""
Papago Translation Module
Transcribes Korean video and creates bilingual subtitles using Whisper and Papago API.
"""

import urllib.request
import urllib.parse
import json
import time
from typing import List, Dict, Any


class PapagoTranslator:
    """Handles translation using Papago API."""
    
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.url = "https://papago.apigw.ntruss.com/nmt/v1/translation"
    
    def translate_ko_to_en(self, text: str) -> str:
        """Translate Korean text to English using Papago API.
        
        Args:
            text: Korean text to translate
            
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
            with urllib.request.urlopen(req, data=data.encode("utf-8")) as res:
                response = json.loads(res.read().decode("utf-8"))
            return response["message"]["result"]["translatedText"]
        except Exception as e:
            return f"[Translation error: {e}]"


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
                   show_progress: bool = False) -> str:
    """Convert Whisper segments to bilingual SRT format.
    
    Args:
        segments: List of segment dicts with 'start', 'end', and 'text' keys
        translator: PapagoTranslator instance
        show_progress: Whether to print progress updates
        
    Returns:
        SRT file content as string
    """
    lines = []
    start_time = time.time()
    
    for i, seg in enumerate(segments):
        start = seg["start"]
        end = seg["end"]
        text_ko = seg["text"].strip()
        
        en = translator.translate_ko_to_en(text_ko)
        
        # Smaller font, KR above EN
        ko_line = "{\\fs16\\c&HA7C1E8&}" + text_ko
        en_line = "{\\fs15\\c&HFFFFFF&}" + en
        lines.append(f"{i+1}\n{timestamp_to_srt(start)} --> {timestamp_to_srt(end)}\n{ko_line}\\N{en_line}\n")
        
        if show_progress and (i+1) % max(1, len(segments)//10) == 0:
            elapsed = time.time() - start_time
            per_seg = elapsed / (i+1)
            remaining = (len(segments) - (i+1)) * per_seg
            print(f"⏳ {i+1}/{len(segments)} done — ~{remaining/60:.1f} min left")
    
    return "\n".join(lines)

