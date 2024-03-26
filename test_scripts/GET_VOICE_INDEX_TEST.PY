import asyncio

import edge_tts

async def get_voices():
    # Assuming edge_tts.list_voices() returns a coroutine
    voices = await edge_tts.list_voices()
    return voices

async def main():
    voices = await get_voices()

    if voices:
        for index, voice in enumerate(voices):
            short_name = voice["ShortName"]
            gender = voice["Gender"]
            tags = voice["VoiceTag"]["VoicePersonalities"]
            if short_name == "en-US-ChristopherNeural" and gender == "Male" and "Reliable" in tags and "Authority" in tags:
                print(f"Index number: {index}, Voice: {short_name} | {gender} | Tags: {tags}")

asyncio.run(main())
