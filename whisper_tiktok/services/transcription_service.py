from pathlib import Path

import stable_whisper
import torch

from whisper_tiktok.interfaces.transcription_service import ITranscriptionService


class TranscriptionService(ITranscriptionService):
    """Service for transcribing audio using Whisper."""

    def __init__(self, logger):
        self.logger = logger

    def transcribe(
        self,
        audio_file: Path,
        srt_file: Path,
        ass_file: Path,
        model: str,
        options: dict,
    ) -> tuple[Path, Path]:
        self.logger.debug(
            f"Transcribing {audio_file} with model {model} and options {options}"
        )

        whisper_model = stable_whisper.load_model(
            model, device=torch.device("cuda" if torch.cuda.is_available() else "cpu")
        )
        self.logger.debug(f"Loaded Whisper model: {model}")

        transcription = whisper_model.transcribe(
            audio_file.as_posix(),
            regroup=True,
            fp16=False,
            word_timestamps=True,
        )
        transcription.to_srt_vtt(srt_file.as_posix(), word_level=True)
        transcription.to_ass(ass_file.as_posix(), word_level=True, **options)
        return (srt_file, ass_file)
    
    def generate_from_text(
        self,
        text: str,
        word_timings: list[dict],
        srt_file: Path,
        ass_file: Path,
        options: dict,
    ) -> tuple[Path, Path]:
        """Generate subtitle files directly from text and word timings."""
        self.logger.debug(
            f"Generating subtitles from text with {len(word_timings)} word timings"
        )
        
        # Since edge-tts doesn't provide word timings, we'll use Whisper for forced alignment
        # but we'll keep the original text for accuracy
        # For now, we'll fall back to regular transcription and post-process to match original text
        self.logger.warning("Word timings not available from TTS. Using Whisper with text alignment.")
        
        # We need the audio file for this approach
        # This is a temporary limitation - we'll implement proper forced alignment
        raise NotImplementedError(
            "Direct text-to-subtitle generation requires audio file for alignment. "
            "Use transcribe_with_text_correction instead."
        )
    
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
        self.logger.info("Transcribing with text correction to ensure subtitle accuracy")
        
        # Load Whisper model
        whisper_model = stable_whisper.load_model(
            model, device=torch.device("cuda" if torch.cuda.is_available() else "cpu")
        )
        self.logger.debug(f"Loaded Whisper model: {model}")

        # Transcribe with word timestamps
        transcription = whisper_model.transcribe(
            audio_file.as_posix(),
            regroup=True,
            fp16=False,
            word_timestamps=True,
        )
        
        # Align transcription with original text
        # This ensures the subtitle text matches the original while keeping Whisper's timing
        transcription = self._align_with_original_text(transcription, original_text)
        
        # Generate output files
        transcription.to_srt_vtt(srt_file.as_posix(), word_level=True)
        transcription.to_ass(ass_file.as_posix(), word_level=True, **options)
        
        return (srt_file, ass_file)
    
    def _align_with_original_text(self, transcription, original_text: str):
        """Align Whisper transcription with original text to fix recognition errors."""
        import re
        
        # Clean and split original text into words, preserving punctuation
        original_words = []
        # Split by whitespace but keep punctuation attached to words
        for word in original_text.split():
            if word:
                original_words.append(word)
        
        # Get all segments and words from transcription
        segments = transcription.segments
        
        # Flatten all words from all segments
        all_words = []
        for segment in segments:
            if hasattr(segment, 'words') and segment.words:
                all_words.extend(segment.words)
        
        # Align original words with transcribed words using simple matching
        self.logger.debug(f"Aligning {len(original_words)} original words with {len(all_words)} transcribed words")
        
        # Simple word-by-word replacement
        min_length = min(len(original_words), len(all_words))
        for i in range(min_length):
            # Remove punctuation for comparison but keep original word intact
            orig_clean = re.sub(r'[^\w]', '', original_words[i]).lower()
            trans_clean = re.sub(r'[^\w]', '', all_words[i].word).lower()
            
            # Replace with original text, ensuring proper spacing
            # Whisper adds a leading space to words except the first one
            if i == 0:
                all_words[i].word = original_words[i]
            else:
                # Add leading space for proper word separation
                all_words[i].word = ' ' + original_words[i]
            
            # Log significant differences for debugging
            if orig_clean != trans_clean:
                self.logger.debug(f"Replaced transcription -> '{original_words[i]}'")
        
        # Handle remaining words
        if len(original_words) > len(all_words):
            self.logger.warning(
                f"Original text has {len(original_words) - len(all_words)} more words than transcription. "
                f"Some words may not appear in subtitles."
            )
        elif len(all_words) > len(original_words):
            # Remove extra transcribed words
            self.logger.warning(
                f"Transcription has {len(all_words) - len(original_words)} extra words. "
                f"Removing them."
            )
            # Remove extra words from segments
            word_count = 0
            for segment in segments:
                if hasattr(segment, 'words') and segment.words:
                    filtered_words = []
                    for w in segment.words:
                        if word_count < len(original_words):
                            filtered_words.append(w)
                            word_count += 1
                    segment.words = filtered_words
        
        return transcription
    
    def _generate_srt(self, text: str, word_timings: list[dict], srt_file: Path) -> None:
        """Generate SRT subtitle file with word-level timing."""
        with open(srt_file, 'w', encoding='utf-8') as f:
            for idx, timing in enumerate(word_timings, 1):
                start = self._format_srt_time(timing['start'])
                end = self._format_srt_time(timing['end'])
                f.write(f"{idx}\n")
                f.write(f"{start} --> {end}\n")
                f.write(f"{timing['word']}\n\n")
    
    def _generate_ass(self, text: str, word_timings: list[dict], ass_file: Path, options: dict) -> None:
        """Generate ASS subtitle file with word-level timing and styling."""
        # Extract styling options
        font_name = options.get('font', 'Lexend Bold')
        font_size = options.get('font_size', 24)
        font_color = options.get('font_color', 'FFFFFF')
        
        # Convert font_color to ASS format (&HBBGGRR)
        if font_color and not font_color.startswith('&H'):
            # Handle hex color like "800080" -> "&H800080"
            font_color = f"&H{font_color}"
        
        # Write ASS file
        with open(ass_file, 'w', encoding='utf-8') as f:
            # Write header
            f.write("[Script Info]\n")
            f.write("ScriptType: v4.00+\n")
            f.write("PlayResX: 384\n")
            f.write("PlayResY: 288\n")
            f.write("ScaledBorderAndShadow: yes\n\n")
            
            # Write styles
            f.write("[V4+ Styles]\n")
            f.write("Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n")
            f.write(f"Style: Default,{font_name},{font_size},{font_color},&Hffffff,&H0,&H0,0,0,0,0,100,100,0,0,1,1,2,5,0,0,10,0\n\n")
            
            # Write events
            f.write("[Events]\n")
            f.write("Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n\n")
            
            # Group words into phrases (by punctuation or every few words)
            phrases = self._group_words_into_phrases(word_timings)
            
            for idx, phrase in enumerate(phrases):
                start = self._format_ass_time(phrase['start'])
                end = self._format_ass_time(phrase['end'])
                text = phrase['text']
                
                # Add karaoke-style timing for each word in the phrase
                karaoke_text = ""
                for word_data in phrase['words']:
                    duration_cs = int((word_data['end'] - word_data['start']) * 100)
                    karaoke_text += f"{{\\k{duration_cs}}}{word_data['word']} "
                
                f.write(f"Dialogue: {idx},{start},{end},Default,,0,0,0,,{karaoke_text.rstrip()}\n")
    
    def _group_words_into_phrases(self, word_timings: list[dict]) -> list[dict]:
        """Group words into logical phrases based on punctuation and timing."""
        if not word_timings:
            return []
        
        phrases = []
        current_phrase = {
            'start': word_timings[0]['start'],
            'end': word_timings[0]['end'],
            'words': [word_timings[0]],
            'text': word_timings[0]['word']
        }
        
        for i in range(1, len(word_timings)):
            word_data = word_timings[i]
            word = word_data['word']
            
            # Check if we should start a new phrase
            # Based on punctuation or significant pause
            prev_word = current_phrase['words'][-1]['word']
            time_gap = word_data['start'] - current_phrase['end']
            
            should_break = (
                any(punct in prev_word for punct in ['.', ',', '!', '?', ';', ':']) or
                time_gap > 1.0 or  # More than 1 second gap
                len(current_phrase['words']) >= 10  # Max 10 words per phrase
            )
            
            if should_break:
                phrases.append(current_phrase)
                current_phrase = {
                    'start': word_data['start'],
                    'end': word_data['end'],
                    'words': [word_data],
                    'text': word
                }
            else:
                current_phrase['end'] = word_data['end']
                current_phrase['words'].append(word_data)
                current_phrase['text'] += ' ' + word
        
        # Add the last phrase
        phrases.append(current_phrase)
        
        return phrases
    
    def _format_srt_time(self, seconds: float) -> str:
        """Format time for SRT (HH:MM:SS,mmm)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    def _format_ass_time(self, seconds: float) -> str:
        """Format time for ASS (H:MM:SS.cc)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours}:{minutes:02d}:{secs:05.2f}"
