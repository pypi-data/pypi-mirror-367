"""
WaoN - Wave-to-Notes Transcriber

A Python library for transcribing audio to MIDI using spectral analysis.
"""

from waon._waon import (
    # Classes
    WaonContext,
    WaonOptions,
    
    # Core transcription functions
    transcribe,
    transcribe_file,
    
    # File output convenience functions
    transcribe_to_file,
    transcribe_array_to_file,
    
    # Batch processing
    transcribe_batch,
    
    # Utility functions
    save_midi,
    get_supported_formats,
    get_version,
    __version__,
)

__all__ = [
    # Classes
    "WaonContext",
    "WaonOptions",
    
    # Core transcription functions
    "transcribe",
    "transcribe_file",
    
    # File output convenience functions
    "transcribe_to_file",
    "transcribe_array_to_file",
    
    # Batch processing
    "transcribe_batch",
    
    # Utility functions
    "save_midi",
    "get_supported_formats",
    "get_version",
    "__version__",
]