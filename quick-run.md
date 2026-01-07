# Quick Run Guide - Confession Videos

## 🚀 Basic Command

Before running, make sure you have:

1. A background video file in the `background/` directory
2. Optionally, a background audio file in the `background_audio/` directory

```powershell
C:/GitClones/Whisper-TikTok/.venv/Scripts/python.exe -m whisper_tiktok.main create --background-video background/your_video.mp4 --tts en-ZA-LeahNeural --font-color FF1493
```

## 🎵 Background Audio

You can add background music or ambient audio to your videos using local files:

```powershell
# Add background music at 30% volume (default)
--background-audio "background_audio/your_audio.mp3"

# Adjust background audio volume (0-100)
--audio-mix 50                   # 50% volume
--audio-mix 20                   # Subtle background (20%)
--audio-mix 80                   # Prominent background (80%)
```

**Example with background music:**

```powershell
python -m whisper_tiktok.main create --background-video background/your_video.mp4 --tts en-ZA-LeahNeural --background-audio "background_audio/your_audio.mp3" --audio-mix 25
```

## 📝 Setup

### 1. Prepare Your Videos and Audio

Place your video and audio files in the appropriate directories:

- Background video: `background/your_video.mp4`
- Background audio: `background_audio/your_audio.mp3`

### 2. Configure video.json

Your `video.json` should have this structure:

```json
[
  {
    "series": "Your Confessions",
    "part": "7",
    "outro": "Visit confess.coraxi.com to anonymously confess",
    "text": "Your confession text here...",
    "background_video_path": "background/your_video.mp4",
    "background_audio_path": "background_audio/your_audio.mp3"
  }
]
```

## 🎙️ Voice Options

### Current Voice (Recommended)

```powershell
--tts en-ZA-LeahNeural
```

South African English, female voice with great pronunciation.

### Other English Voices to Try

**American English:**

```powershell
--tts en-US-JennyNeural          # Female, warm and friendly
--tts en-US-AriaNeural           # Female, natural and conversational
--tts en-US-GuyNeural            # Male, professional
--tts en-US-DavisNeural          # Male, young and energetic
```

**British English:**

```powershell
--tts en-GB-SoniaNeural          # Female, clear and professional
--tts en-GB-RyanNeural           # Male, friendly
--tts en-GB-LibbyNeural          # Female, warm
```

**Australian English:**

```powershell
--tts en-AU-NatashaNeural        # Female, clear
--tts en-AU-WilliamNeural        # Male, natural
```

**South African English:**

```powershell
--tts en-ZA-LeahNeural           # Female (current)
--tts en-ZA-LukeNeural           # Male
```

## 🎨 Font Options

### Currently Using

```powershell
--font "Impact"
```

### Best for Confession/Story Videos

**Bold & Attention-Grabbing:**

```powershell
--font "Impact"                  # Current default - bold, meme-style
--font "Arial Black"             # Very bold, rounded
--font "Segoe UI Black"          # Ultra-bold, modern
```

**Fun & Casual:**

```powershell
--font "Comic Sans MS Bold"      # Friendly, casual
--font "Ink Free"                # Handwritten style
--font "Bahnschrift"             # Modern geometric
```

**Elegant & Emotional:**

```powershell
--font "Gabriola"                # Flowing, decorative
--font "Georgia Bold"            # Serif, storytelling
--font "Trebuchet MS Bold"       # Humanist, informal
```

**Clean & Readable:**

```powershell
--font "Verdana Bold"            # Wide, clear
--font "Calibri Bold"            # Professional
```

## 🎨 Color Options

### Current Color

```powershell
--font-color FF1493              # Deep Pink (default)
```

### Popular Color Choices

**Emotional/Romance:**

```powershell
--font-color FF1493              # Deep Pink (default)
--font-color 800080              # Purple
--font-color FF69B4              # Hot Pink
--font-color DC143C              # Crimson
```

**Bold/Energetic:**

```powershell
--font-color FF0000              # Red
--font-color FF6600              # Orange
--font-color FFD700              # Gold
--font-color FFFF00              # Yellow
```

**Cool/Calm:**

```powershell
--font-color 00FFFF              # Cyan
--font-color 1E90FF              # Dodger Blue
--font-color 9370DB              # Medium Purple
--font-color 00FF00              # Lime Green
```

**Classic:**

```powershell
--font-color FFFFFF              # White
--font-color FFF000              # Yellow-white
```

## ⚙️ Other Customization Options

### Font Size

```powershell
--font-size 28                   # Current default (increased for better visibility)
--font-size 24                   # Slightly smaller
--font-size 32                   # Larger
```

### Speech Rate

```powershell
--rate "+50%"                    # 50% faster speech
--rate "+25%"                    # 25% faster speech
--rate "-25%"                    # 25% slower speech
--rate "-50%"                    # 50% slower speech
# Leave empty for normal speed
```

Note: Use quotes when specifying negative values to avoid shell interpretation issues.

### Whisper Model

```powershell
# Default: turbo (fast, good quality)
--model turbo                    # Fast, recommended
--model base                     # Faster, lower accuracy
--model small                    # Balanced
--model medium                   # More accurate, slower
--model large                    # Most accurate, slowest
```

### Background Video

```powershell
# Use a local video file
--background-video "background/your_video.mp4"
```

## 📋 Complete Examples

### Default Confession Video

```powershell
python -m whisper_tiktok.main create --background-video background/your_video.mp4 --tts en-ZA-LeahNeural --font-color FF1493
```

### With Custom Font

```powershell
python -m whisper_tiktok.main create --background-video background/your_video.mp4 --tts en-ZA-LeahNeural --font-color FF1493 --font "Arial Black"
```

### Emotional Style (Pink text, elegant font)

```powershell
python -m whisper_tiktok.main create --background-video background/your_video.mp4 --tts en-ZA-LeahNeural --font-color FF1493 --font "Gabriola" --font-size 30
```

### Faster Speech (50% speed increase)

```powershell
python -m whisper_tiktok.main create --background-video background/your_video.mp4 --tts en-ZA-LeahNeural --font-color FF1493 --rate "+50%"
```

### Slower, More Dramatic Speech

```powershell
python -m whisper_tiktok.main create --background-video background/your_video.mp4 --tts en-ZA-LeahNeural --font-color FF1493 --rate "-25%"
```

### With Background Music

```powershell
python -m whisper_tiktok.main create --background-video background/your_video.mp4 --tts en-ZA-LeahNeural --font-color FF1493 --background-audio "background_audio/your_audio.mp3" --audio-mix 25
```

### Full Customization (Music, Faster Speech, Custom Font)

```powershell
python -m whisper_tiktok.main create --background-video background/your_video.mp4 --tts en-ZA-LeahNeural --font-color FF1493 --font "Arial Black" --font-size 32 --rate "+25%" --background-audio "background_audio/your_audio.mp3" --audio-mix 30
```

### Bold Style (Red text, impact font, larger)

```powershell
python -m whisper_tiktok.main create --background-video background/your_video.mp4 --tts en-ZA-LeahNeural --font-color FF0000 --font "Impact" --font-size 32
```

### American Voice Style

```powershell
python -m whisper_tiktok.main create --background-video background/your_video.mp4 --tts en-US-AriaNeural --font-color FF1493
```

## 🔧 Technical Notes

### URL Pronunciation

- URLs like "confess.coraxi.com" are automatically handled
- TTS will say "confess dot core-AX-ee dot com"
- Subtitles will wrap URLs intelligently at dots

### Text Alignment

- Subtitles aligned 161/163 words successfully
- Some words may be missed by Whisper (usually filler words)

### Output Location

Videos are saved to: `output/[uuid]/[uuid].mp4`

## 💡 Pro Tips

1. **Deep pink works great for confession videos** - it's emotional and stands out
2. **Impact font is perfect for readability** on mobile screens
3. **Test different voices** - South African accent adds unique flavor
4. **Keep font size 28-32** for mobile viewing
5. **Use bold fonts** - better visibility over video backgrounds
6. **Pre-download your videos** - No more YouTube dependency!

## 🎬 Quick Start Workflow

1. Download or prepare your background video and audio files
2. Place them in `background/` and `background_audio/` directories
3. Edit your confession in `video.json` with paths to your files
4. Run the command with your preferred options
5. Video will be in `output/[uuid]/[uuid].mp4`
6. Upload to TikTok!

---

**Last Updated:** January 7, 2026
**Version:** 2.0 - Now using local files instead of YouTube downloads!
