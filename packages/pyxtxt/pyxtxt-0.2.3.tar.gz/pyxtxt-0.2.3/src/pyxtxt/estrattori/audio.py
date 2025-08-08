# pyxtxt/extractors/audio_whisper.py
from . import register_extractor
import tempfile
import os

try:
    import whisper
except ImportError:
    whisper = None

if whisper:
    _whisper_model = None
    
    def _get_model():
        global _whisper_model
        if _whisper_model is None:
            _whisper_model = whisper.load_model("base")
        return _whisper_model
    
    def xtxt_audio_whisper(file_buffer):
        try:
            # Usa un suffixe generico - Whisper + FFmpeg gestiscono il formato
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(file_buffer.read())
                temp_file.flush()
                
                model = _get_model()
                result = model.transcribe(temp_file.name)
                
                os.unlink(temp_file.name)
                
                return result['text'].strip()
                
        except Exception as e:
            print(f"⚠️ Error while extracting audio with Whisper: {e}")
            return ""
    
    # Registra per tutti i formati audio comuni
    audio_formats = [
        "audio/wav", "audio/wave",
        "audio/mp3", "audio/mpeg",
        "audio/m4a", "audio/mp4",
        "audio/flac",
        "audio/ogg", "audio/ogg-vorbis",
        "audio/opus",
        "audio/aac",
        "audio/wma",
        "audio/webm"
    ]
    
    for format_type in audio_formats:
        register_extractor(format_type, xtxt_audio_whisper, name="Whisper Audio")
