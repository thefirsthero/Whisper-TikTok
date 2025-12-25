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
        
        # Regroup into better phrases for smoother display
        # This creates longer subtitle segments instead of word-by-word
        transcription = transcription.split_by_length(max_chars=42, max_words=7)
        
        # Generate output files with segment-level (not word-level) for smoother playback
        transcription.to_srt_vtt(srt_file.as_posix(), word_level=False)
        transcription.to_ass(ass_file.as_posix(), word_level=False, **options)
        
        return (srt_file, ass_file)
    
    def _preprocess_text_for_wrapping(self, text: str) -> str:
        """Preprocess text to split URLs into separate words at dots for better wrapping."""
        import re
        
        # Split URLs at dots so each part becomes a separate word
        # This allows them to wrap across subtitle lines naturally
        # Match URL patterns like confess.coraxi.com
        def split_url_at_dots(match):
            url = match.group(0)
            # Replace dots with space+dot+space so they become separate tokens
            # "confess.coraxi.com" becomes "confess. coraxi. com"
            url = url.replace('.', '. ')
            return url
        
        # Match URLs (common patterns)
        text = re.sub(
            r'\b(?:https?://)?(?:www\.)?[a-z0-9][a-z0-9-]*(?:\.[a-z0-9-]+)+\.(?:com|org|net|edu|gov)\b',
            split_url_at_dots,
            text,
            flags=re.IGNORECASE
        )
        
        return text
    
    def _align_with_original_text(self, transcription, original_text: str):
        """Align Whisper transcription with original text to fix recognition errors."""
        import re
        from difflib import SequenceMatcher
        
        # Preprocess text to add URL break points
        original_text = self._preprocess_text_for_wrapping(original_text)
        
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
        word_to_segment = {}  # Track which segment each word belongs to
        for seg_idx, segment in enumerate(segments):
            if hasattr(segment, 'words') and segment.words:
                for word in segment.words:
                    all_words.append(word)
                    word_to_segment[len(all_words) - 1] = seg_idx
        
        self.logger.debug(f"Aligning {len(original_words)} original words with {len(all_words)} transcribed words")
        
        # Use sequence matching for better alignment
        transcribed_clean = [re.sub(r'[^\w]', '', w.word).lower() for w in all_words]
        original_clean = [re.sub(r'[^\w]', '', w).lower() for w in original_words]
        
        matcher = SequenceMatcher(None, transcribed_clean, original_clean)
        
        # Build alignment mapping
        alignment = []
        used_trans_indices = set()  # Track which transcribed words we've already used
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal' or tag == 'replace':
                # Map transcribed words to original words (1-to-1)
                for i, j in zip(range(i1, i2), range(j1, j2)):
                    if i not in used_trans_indices:
                        alignment.append((i, j))
                        used_trans_indices.add(i)
            elif tag == 'delete':
                # Transcription has extra words - skip them
                pass
            elif tag == 'insert':
                # Original has words that aren't in transcription
                # This means audio didn't say these words or Whisper missed them
                # We'll skip them to avoid misalignment
                pass
        
        # Apply alignment: replace transcribed words with original text
        aligned_count = 0
        for trans_idx, orig_idx in alignment:
            if trans_idx < len(all_words) and orig_idx < len(original_words):
                # Replace with original text, ensuring proper spacing
                if aligned_count == 0:
                    all_words[trans_idx].word = original_words[orig_idx]
                else:
                    all_words[trans_idx].word = ' ' + original_words[orig_idx]
                aligned_count += 1
        
        # Remove any unaligned words from the transcription
        aligned_indices = {idx for idx, _ in alignment}
        for segment in segments:
            if hasattr(segment, 'words') and segment.words:
                segment.words = [w for i, w in enumerate(all_words) 
                                if w in segment.words and all_words.index(w) in aligned_indices]
        
        self.logger.info(f"Successfully aligned {aligned_count}/{len(original_words)} words")
        if aligned_count < len(original_words):
            missing = len(original_words) - aligned_count
            self.logger.warning(f"{missing} words from original text were not found in transcription")
        
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
        font_name = options.get('font', 'Impact')
        font_size = options.get('font_size', 28)
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
            
            # Write styles with enhanced visual appeal
            # Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
            f.write("[V4+ Styles]\n")
            f.write("Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n")
            # Enhanced style: thicker outline (3), larger shadow (3) for better pop and readability
            f.write(f"Style: Default,{font_name},{font_size},{font_color},&Hffffff,&H000000,&H80000000,-1,0,0,0,100,100,0,0,1,3,3,5,0,0,10,0\n\n")
            
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
