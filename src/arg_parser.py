import argparse
import sys

# voice_manager.py
from src.voice_manager import VoicesManager

import msg
from utils import rgb_to_bgr


async def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="small", help="Model to use",
                        choices=["tiny", "base", "small", "medium", "large"], type=str)
    parser.add_argument("--non_english", action='store_true',
                        help="Don't use the english model.")
    parser.add_argument("--url", metavar='U', default="https://www.youtube.com/watch?v=intRX7BRA90",
                        help="Youtube URL to download as background video.", type=str)
    parser.add_argument("--tts", default="en-US-ChristopherNeural",
                        help="Voice to use for TTS", type=str)
    parser.add_argument(
        "--list-voices", help="Use `edge-tts --list-voices` to list all voices", action='help')
    parser.add_argument("--random_voice", action='store_true',
                        help="Random voice for TTS", default=False)
    parser.add_argument("--gender", choices=["Male", "Female"],
                        help="Gender of the random TTS voice", type=str)
    parser.add_argument(
        "--language", help="Language of the random TTS voice for example: en-US", type=str)
    parser.add_argument("--sub_format",
                        help="Subtitle format", choices=["u", "i", "b"], default="b", type=str)
    parser.add_argument("--sub_position",
                        help="Subtitle position", choices=[i for i in range(1, 10)], default=5, type=int)
    parser.add_argument("--font", help="Subtitle font",
                        default="Lexend Bold", type=str)
    parser.add_argument("--font_color", help="Subtitle font color in hex format: 00FF00",
                        default="#00B400", type=str)
    parser.add_argument(
        "--font_size", help="Subtitle font size", default=21, type=int)
    parser.add_argument('--max_characters', default=38,
                        type=int, help='Max characters per line')
    parser.add_argument('--max_words', default=2, type=int,
                        help='Max words per segment')
    parser.add_argument("--upload_tiktok", help="Upload to TikTok after creating the video",
                        action='store_true', default=False)
    parser.add_argument("-v", "--verbose", action='store_true',
                        help="Verbose")
    args = parser.parse_args()

    if args.random_voice:  # Random voice
        args.tts = None
        if not args.gender:
            print(
                f"{msg.ERROR}When using --random_voice, please specify both --gender and --language arguments.")
            sys.exit(1)

        elif not args.language:
            print(
                f"{msg.ERROR}When using --random_voice, please specify both --gender and --language arguments.")
            sys.exit(1)

        elif args.gender and args.language:
            # Check if voice is valid
            voices_manager_obj = await VoicesManager().create()
            voices = await VoicesManager().find(voices_manager_obj, args.gender, args.language)
            args.tts = voices['Name']

            # Check if language is english
            if not str(args.language).startswith('en'):
                args.non_english = True

    else:
        # Check if voice is valid
        voices = await VoicesManager().create()
        args.language = '-'.join(i for i in args.tts.split('-')[0:2])
        voices = voices.find(Locale=args.language)
        if len(voices) == 0:
            # Voice not found
            print(
                f"{msg.ERROR}Specified TTS voice not found. Use `edge-tts --list-voices` to list all voices.")
            sys.exit(1)

    # Extract language from TTS voice
    if args.tts:
        lang_prefix = args.tts.split('-')[0]
        if not lang_prefix.startswith('en'):
            args.non_english = True

    # Cast font color to lowercase
    args.font_color = args.font_color.lower()

    # Remove # from font color
    if args.font_color.startswith('#'):
        args.font_color = args.font_color[1:]

    # Convert font color from RGB to BGR
    args.font_color = rgb_to_bgr(args.font_color)

    return args
