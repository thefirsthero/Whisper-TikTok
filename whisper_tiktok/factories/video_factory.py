import uuid
from datetime import datetime
import re

from whisper_tiktok.container import Container
from whisper_tiktok.processors.video_processor import VideoProcessor
from whisper_tiktok.strategies.processing_strategy import (
    DownloadBackgroundStrategy,
    ProcessingStrategy,
    TikTokUploadStrategy,
    TranscriptionStrategy,
    TTSGenerationStrategy,
    VideoCompositionStrategy,
)


class VideoCreatorFactory:
    """Factory for creating video processor instances."""

    def __init__(self, container: Container):
        self.container = container

    def _generate_filename(self, video_data: dict) -> str:
        """Generate chronological filename from video data."""
        # Get series and part info
        series = video_data.get('series', 'Video')
        part = video_data.get('part', '1')
        
        # Create slug from series name (lowercase, replace spaces with hyphens)
        series_slug = re.sub(r'[^a-z0-9]+', '-', series.lower()).strip('-')
        
        # Generate timestamp for uniqueness
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Format: YYYYMMDD_HHMMSS_series-name_partXX
        return f"{timestamp}_{series_slug}_part{part:0>2}"

    def create_processor(self, video_data: dict, config: dict) -> VideoProcessor:
        """Create a configured video processor."""
        # Generate meaningful filename instead of UUID
        uuid_str = self._generate_filename(video_data)

        return VideoProcessor(
            uuid=uuid_str,
            video_data=video_data,
            config=config,
            strategies=self._build_strategies(config),
            logger=self.container.logger(),
        )

    def _build_strategies(self, config: dict) -> list[ProcessingStrategy]:
        """Build processing pipeline based on config."""
        strategies = [
            DownloadBackgroundStrategy(
                self.container.video_downloader(), self.container.logger()
            ),
            TTSGenerationStrategy(
                self.container.tts_service(), self.container.logger()
            ),
            TranscriptionStrategy(
                self.container.transcription_service(), self.container.logger()
            ),
            VideoCompositionStrategy(
                self.container.ffmpeg_service(), self.container.logger()
            ),
        ]

        if config.get("upload_tiktok"):
            strategies.append(
                TikTokUploadStrategy(self.container.uploader(), self.container.logger())
            )

        return strategies
