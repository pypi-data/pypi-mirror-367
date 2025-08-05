# This file initializes the my_app module. It can be used to define what is exported when the module is imported.

from .audio import record_audio_from_michrophone, text_to_speech
from .transcription import speech_to_text
from .responses import ai_response

__all__ = [
    "record_audio_from_michrophone",
    "text_to_speech",
    "speech_to_text",
    "ai_response",
    "main"
]