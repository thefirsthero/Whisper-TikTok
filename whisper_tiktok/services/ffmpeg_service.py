import json
import os
from logging import Logger
from pathlib import Path
from typing import NamedTuple

from whisper_tiktok.execution.command_executor import CommandExecutor, ExecutionResult


class FFmpegError(Exception):
    """Custom exception for FFmpeg errors."""


class MediaInfo(NamedTuple):
    """Represents the result of running FFprobe.

    Attributes:
        return_code (int): The return code of the FFprobe process.
        json (str): The JSON output from FFprobe.
        error (str): The error message from FFprobe, if any.
    """

    return_code: int
    json: str
    error: str

    @staticmethod
    def from_json(result: ExecutionResult) -> "MediaInfo":
        """Creates a MediaInfo instance from FFprobe execution result."""
        return MediaInfo(
            return_code=result.returncode, json=result.stdout, error=result.stderr
        )

    @staticmethod
    def convert_time(time_in_seconds: float) -> str:
        """
        Converts time in seconds to a string in the format "hh:mm:ss.mmm".

        Args:
            time_in_seconds (float): The time in seconds to be converted.

        Returns:
            str: The time in the format "hh:mm:ss.mmm".
        """
        hours = int(time_in_seconds // 3600)
        minutes = int((time_in_seconds % 3600) // 60)
        seconds = int(time_in_seconds % 60)
        milliseconds = int((time_in_seconds - int(time_in_seconds)) * 1000)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"

    @property
    def duration(self) -> float:
        """Extracts the duration of the audio stream from the FFprobe JSON output."""
        d = json.loads(self.json)

        streams = d.get("streams", [])
        audio_stream = None
        for stream in streams:
            if stream["codec_type"] == "audio":
                audio_stream = stream
                break

        if audio_stream is None:
            raise ValueError("No audio stream found")

        return float(audio_stream["duration"])


class FFmpegService:
    """Service for FFmpeg operations."""

    def __init__(self, executor: CommandExecutor, logger: Logger):
        self.executor = executor
        self.logger = logger

    def _build_video_filters(self, subtitles: Path) -> str:
        # FFmpeg will use system fonts automatically via fontconfig
        return rf"crop=ih/16*9:ih,scale=w=1080:h=1920:flags=lanczos,gblur=sigma=2,ass={subtitles.as_posix()}"

    def _build_ffmpeg_command(
        self,
        background: Path,
        audio: Path,
        output: Path,
        start_time: int,
        duration: str,
        filters: str,
    ) -> str:
        return rf"ffmpeg -ss {start_time} -t {duration} -i {background.as_posix()} -i {audio.as_posix()} -map 0:v -map 1:a -filter:v {filters} -c:v libx264 -crf 23 -c:a aac -ac 2 -b:a 192K {output.as_posix()} -y -threads {os.cpu_count()}"

    def compose_video(
        self,
        background: Path,
        audio: Path,
        subtitles: Path,
        output: Path,
        start_time: int,
        duration: str,
    ) -> Path:
        """Compose final video with background, audio, and subtitles."""

        # Build filter complex
        filters = self._build_video_filters(subtitles)

        command = self._build_ffmpeg_command(
            background, audio, output, start_time, duration, filters
        )
        result = self.executor.execute(command)

        if result.returncode != 0:
            raise FFmpegError(f"Failed to compose video: {result.stderr}")

        return output

    def get_media_info(self, file_path: Path) -> MediaInfo:
        """Get media information using ffprobe."""
        command = f"ffprobe -v quiet -print_format json -show_format -show_streams {file_path.as_posix()}"
        result = self.executor.execute(command)

        if result.returncode != 0:
            raise FFmpegError(f"Failed to probe media: {result.stderr}")

        return MediaInfo.from_json(result)

    def mix_audio(
        self,
        tts_audio: Path,
        background_audio: Path,
        output: Path,
        tts_volume: float = 1.0,
        background_volume: float = 0.3,
    ) -> Path:
        """Mix TTS audio with background audio at specified volumes.
        
        Args:
            tts_audio: Path to the TTS audio file
            background_audio: Path to the background audio file
            output: Path for the mixed audio output
            tts_volume: Volume multiplier for TTS (0.0 to 1.0+)
            background_volume: Volume multiplier for background audio (0.0 to 1.0+)
            
        Returns:
            Path to the mixed audio file
        """
        # Use amix filter to mix the two audio streams
        # Volume levels are normalized (0.0 to 1.0)
        command = (
            f"ffmpeg -i {tts_audio.as_posix()} -i {background_audio.as_posix()} "
            f"-filter_complex \""
            f"[0:a]volume={tts_volume}[a1];"
            f"[1:a]volume={background_volume}[a2];"
            f"[a1][a2]amix=inputs=2:duration=first:dropout_transition=2\" "
            f"-c:a libmp3lame -q:a 2 {output.as_posix()} -y"
        )
        
        result = self.executor.execute(command)
        
        if result.returncode != 0:
            raise FFmpegError(f"Failed to mix audio: {result.stderr}")
        
        return output
