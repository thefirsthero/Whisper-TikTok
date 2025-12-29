from logging import Logger
from pathlib import Path

import edge_tts

from whisper_tiktok.interfaces.tts_service import ITTSService


class TTSService(ITTSService):
    """Text-to-Speech service using edge-tts."""

    def __init__(self, logger: Logger):
        self.logger = logger

    async def synthesize(
        self,
        text: str,
        output_file: Path,
        voice: str = "en-US-ChristopherNeural",
        rate: str = None,
    ) -> None:
        """
        Synthesize speech from text and save to output file.

        Args:
            text (str): The text to be converted to speech.
            output_file (Path): The path to save the synthesized audio file.
            voice (str): The voice to be used for synthesis.
            rate (str): The speech rate (e.g., "+50%", "-25%"). Default is normal speed.
        """
        self.logger.debug(
            f"Synthesizing speech to {output_file} using voice {voice}"
            + (f" at rate {rate}" if rate else "")
        )
        communicate = edge_tts.Communicate(text, voice, rate=rate)
        await communicate.save(output_file.as_posix())
