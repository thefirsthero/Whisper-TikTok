from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional


class ITTSService(ABC):
    """Interface for text-to-speech services."""

    @abstractmethod
    async def synthesize(
        self, text: str, output_file: Path, voice: str, rate: Optional[str] = None
    ) -> None:
        """Synthesize speech from text."""
