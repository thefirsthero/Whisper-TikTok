from abc import ABC, abstractmethod
from pathlib import Path


class ITranscriptionService(ABC):
    """Interface for transcription services."""

    @abstractmethod
    def transcribe(
        self,
        audio_file: Path,
        srt_file: Path,
        ass_file: Path,
        model: str,
        options: dict,
    ) -> tuple[Path, Path]:
        """Transcribe audio and generate SRT/ASS files."""
    
    @abstractmethod
    def generate_from_text(
        self,
        text: str,
        word_timings: list[dict],
        srt_file: Path,
        ass_file: Path,
        options: dict,
    ) -> tuple[Path, Path]:
        """Generate SRT/ASS files from text and word timings."""
    
    @abstractmethod
    def transcribe_with_text_correction(
        self,
        audio_file: Path,
        original_text: str,
        srt_file: Path,
        ass_file: Path,
        model: str,
        options: dict,
    ) -> tuple[Path, Path]:
        """Transcribe audio and align with original text for accurate subtitles."""
