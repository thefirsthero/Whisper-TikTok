# Quick Run Guide - Confession Videos

## 🚀 Basic Command

```powershell
C:/GitClones/Whisper-TikTok/.venv/Scripts/python.exe -m whisper_tiktok.main create --background-url https://youtu.be/u7kdVe8q5zs?si=KD2Z7X2snKd0XyTR --tts en-ZA-LeahNeural --font-color 800080
```

## 📝 Setup

Your `video.json` should have this structure:

```json
[
  {
    "series": "Your Confessions",
    "part": "7",
    "outro": "Visit confess.coraxi.com to anonymously confess",
    "text": "Your confession text here..."
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
--font-color 800080              # Purple
```

### Popular Color Choices

**Emotional/Romance:**

```powershell
--font-color 800080              # Purple (current)
--font-color FF1493              # Deep Pink
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
--font-color FFFFFF              # White (default)
--font-color FFF000              # Yellow-white
```

## ⚙️ Other Customization Options

### Font Size

```powershell
--font-size 28                   # Current default (increased for better visibility)
--font-size 24                   # Slightly smaller
--font-size 32                   # Larger
```

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
--background-url "YOUR_YOUTUBE_URL"
# Or use a local file:
--background-video "path/to/video.mp4"
```

## 📋 Complete Examples

### Default Confession Video

```powershell
python -m whisper_tiktok.main create --background-url https://youtu.be/u7kdVe8q5zs --tts en-ZA-LeahNeural --font-color 800080
```

### With Custom Font

```powershell
python -m whisper_tiktok.main create --background-url https://youtu.be/u7kdVe8q5zs --tts en-ZA-LeahNeural --font-color 800080 --font "Arial Black"
```

### Emotional Style (Pink text, elegant font)

```powershell
python -m whisper_tiktok.main create --background-url https://youtu.be/u7kdVe8q5zs --tts en-ZA-LeahNeural --font-color FF1493 --font "Gabriola" --font-size 30
```

### Bold Style (Red text, impact font, larger)

```powershell
python -m whisper_tiktok.main create --background-url https://youtu.be/u7kdVe8q5zs --tts en-ZA-LeahNeural --font-color FF0000 --font "Impact" --font-size 32
```

### American Voice Style

```powershell
python -m whisper_tiktok.main create --background-url https://youtu.be/u7kdVe8q5zs --tts en-US-AriaNeural --font-color 800080
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

1. **Purple works great for confession videos** - it's emotional and stands out
2. **Impact font is perfect for readability** on mobile screens
3. **Test different voices** - South African accent adds unique flavor
4. **Keep font size 28-32** for mobile viewing
5. **Use bold fonts** - better visibility over video backgrounds

## 🎬 Quick Start Workflow

1. Edit your confession in `video.json`
2. Run the command with your preferred options
3. Video will be in `output/[uuid]/[uuid].mp4`
4. Upload to TikTok!

---

**Last Updated:** December 25, 2025
**Version:** 1.0
