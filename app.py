import os
import sys
import json
from pathlib import Path
import asyncio
import platform
from argparse import Namespace

import edge_tts
import streamlit as st
import pandas as pd

from src.video_creator import VideoCreator
from utils import rgb_to_bgr

# Import the function for merging audio and video
from merge_audio_video import merge_video_and_audio

result = None


async def generate_video(
        model,
        tts_voice,
        sub_position,
        font,
        font_color,
        font_size,
        url,
        non_english,
        upload_tiktok,
        verbose,
        video_json,
        background_tab,
        video_num,
        max_words,
        add_audio,  
        selected_audio_path,
        mixing_percentage, 
        *args,
        **kwargs):

    args = Namespace(
        model=model,
        tts=tts_voice.split('|')[0].strip(),
        font=font,
        font_color=rgb_to_bgr(font_color.lower()),
        font_size=font_size,
        sub_position=sub_position,
        url=url,
        non_english=non_english,
        upload_tiktok=upload_tiktok,
        verbose=verbose,
        mp4_background=background_tab,
        max_words=max_words
    )

    async def get_video(video_data, args, add_audio):  # Pass checkbox state to function
        with st.status("Generating video...", expanded=False) as status:
            video_creator = VideoCreator(video_data, args)

            status.update(label="Downloading video...")
            video_creator.download_video()

            status.update(label="Loading model...")
            video_creator.load_model()

            status.update(label="Creating text...")
            video_creator.create_text()

            status.update(label="Generating audio...")
            await video_creator.text_to_speech()

            status.update(label="Generating transcription...")
            video_creator.generate_transcription()

            status.update(label="Selecting background...")
            video_creator.select_background()

            status.update(label="Integrating subtitles...")
            video_creator.integrate_subtitles()

            # Check if "Add Audio?" checkbox is checked
            if add_audio:
                # Merge video with uploaded audio using the original video file name
                merge_video_and_audio(str(video_creator.mp4_final_video), selected_audio_path, str(video_creator.mp4_final_video), mixing_percentage)

                # Delete the temporary audio file after merging
                os.remove(selected_audio_path)

            if upload_tiktok:
                status.update(label="Uploading to TikTok...")
                video_creator.upload_to_tiktok()

            status.update(label="Video generated!",
                          state="complete", expanded=False)
            return str(video_creator.mp4_final_video)  # Return the original video file path

    tasks = [get_video(video_json[i], args, add_audio)  # Pass checkbox state to function
             for i, name in enumerate(video_num)]
    results = await asyncio.gather(*tasks)

    if len(results) == 1:
        return results[0]

    else:
        return results[-1]



@st.cache_data
def json_to_df(json_file):
    return pd.read_json(json_file)


@st.cache_data
def df_to_json(df):
    try:
        # Convert the DataFrame to a JSON string
        json_str = df.to_json(orient='records', indent=4, force_ascii=False)

        # raise an error if the dataframe has no rows (at least one is required)
        if df.shape[0] == 0:
            st.error("You must add at least one video to the JSON")
            return

        # Save the JSON string to a file
        with open('video.json', 'w', encoding='UTF-8') as f:
            f.write(json_str)

        st.success("JSON saved successfully!")

    except ValueError as e:
        st.error("You must fill all the fields in the JSON")
    except Exception as e:
        st.error(f"Error saving JSON: {e}")


# Streamlit Config
st.set_page_config(
    page_title="Whisper-TikTok",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/thefirsthero/Whisper-TikTok',
        'Report a bug': "https://github.com/thefirsthero/Whisper-TikTok/issues",
        'About':
            """
            # Whisper-TikTok
            Whisper-TikTok is an innovative AI-powered tool that leverages the prowess of Edge TTS, OpenAI-Whisper, and FFMPEG to craft captivating TikTok videos also with a web application interface!

            Mantainer: https://github.com/thefirsthero

            If you find a bug or if you just have questions about the project feel free to reach me at https://github.com/thefirsthero/Whisper-TikTok
            Any contribution to this project is welcome to improve the quality of work!
            """
    }
)

st.page_link("pages/reddit.py", label="Reddit", icon="🤖")
st.page_link("https://github.com/thefirsthero/Whisper-TikTok",
             label="GitHub", icon="🌎")


async def main():

    st.title("🏆 Whisper-TikTok 🚀")
    st.write("Create a TikTok video with text-to-speech of Microsoft Edge's TTS and subtitles of Whisper model.")

    st.subheader("JSON Editor", help="Here you can edit the JSON file with the videos. Copy-and-paste is supported and compatible with Google Sheets, Excel, and others. You can do bulk-editing by dragging the handle on a cell (similar to Excel)!")
    st.write("ℹ️ The JSON file is saved automatically when you click the button below. Every time you edit the JSON file, you must click the button to save the changes otherwise they will be lost.")
    edited_df = st.data_editor(json_to_df('video.json'),
                               num_rows="dynamic")
    st.button("Save JSON", on_click=df_to_json, args=(
        edited_df,), help="Save the JSON file with the videos")

    st.divider()

    with st.sidebar:
        model = st.selectbox(
            "Whisper Model", ["tiny", "base", "small", "medium", "large"], index=2, help="The model used to generate the subtitles. The bigger the model, the better the results, but the slower the generation. The tiny model is recommended for testing purposes. Medium model is enough for good results in many languages.")

        with st.expander("ℹ️ How to use"):
            st.write(
                """
                1. Choose the video to generate using the dropdown menu.
                2. Choose the model to use for the subtitles.
                3. Choose the voice to use for the text-to-speech.
                4. Choose the background video to use for the TikTok video.
                5. Choose the position of the subtitles.
                6. Choose the font, font color, and font size for the subtitles.
                7. Choose the URL of the background video to use for the TikTok video.
                8. Check the "Non-english" checkbox if you want to generate a video in a non-english language.
                9. Check the "Upload to TikTok" checkbox if you want to upload the video to TikTok using the TikTok session cookie. For this step it is required to have a TikTok account and to be logged in on your browser. Then the required cookies.txt file can be generated using this guide
                """)

    LEFT, RIGHT = st.columns(2)

    with LEFT:
        st.subheader("General settings")
        tts_voice = st.selectbox(
            "TTS Voice",
            [f"{i['ShortName']} | {i['Gender']} | Tags: {i['VoiceTag']['VoicePersonalities']}" for i in await edge_tts.list_voices()], index=111, help="The voice used to generate the audio. The voice must be in the same language as the subtitles."
        )

        left, mid, right = st.columns(3)

        with left:
            # Subtitle font
            font = st.selectbox(
                "Subtitle font", ["Lexend Bold", "Lexend Regular", "Arial", "Roboto", "Big Condensed Black"], index=0, help="The font used for the subtitles.")
        with mid:
            # Subtitle font size
            font_size = st.slider(
                "Subtitle font size", 15, 50, 15, help="The font size for the subtitles. It is recommended to use a font size between 18 and 21.")
        with right:
            # Subtitle font color
            font_color = st.color_picker(
                "Subtitle font color", "#1EB102", help="The color of the subtitles.")

        # Subtitle position
        left, right = st.columns(2)
        with left:
            sub_position = st.slider(
                "Subtitle alignment (position)", 1, 9, 5, help="The position of the subtitles. 1 is the bottom left corner, 5 is the center, 9 is the top right corner. This is the alignment feature of FFMPEG subtitles.")
        with right:
            max_words = st.number_input(
                "Maximum number of words per line", min_value=2, max_value=5, value=2, step=1, help="The maximum number of words per line for the subtitles. This is the feature for stable whisper model. It is recommended to use a value between 2 and 3.")

        # Background Video URL
        url = st.text_input(
            "URL Background Video", "https://www.youtube.com/watch?v=intRX7BRA90", help="The URL of the background video to use for the TikTok video", placeholder="https://www.youtube.com/watch?v=intRX7BRA90")

        left, mid, right = st.columns(3)

        with left:
            # Non-english
            non_english = st.checkbox(
                "Non-english", help="Check this if you want to generate a video in a non-english language")

        with mid:
            # Upload to TikTok
            upload_tiktok = st.checkbox(
                "Upload to TikTok", help="Upload the video to TikTok using the TikTok session cookie. For this step it is required to have a TikTok account and to be logged in on your browser. Then the required cookies.txt file can be generated using this guide (https://github.com/kairi003/Get-cookies.txt-LOCALLY). The cookies.txt file must be placed in the root folder of the project.")

        with right:
            # Verbose
            verbose = st.checkbox(
                "Verbose", help="Print the output of the commands used to create the video on your terminal. Useful for debugging.")

        st.divider()

        st.subheader("Video settings")

        st.write("JSON file with the videos")
        with open('video.json', encoding='utf-8') as fh:
            video_json = st.json(json.load(fh), expanded=False)

        # Get the list of files in "background"
        folder_path = Path("background").absolute()
        files = folder_path.glob('*.mp4')
        files = [file.name for file in files]

        # Create a Dropdown with the list of files
        background_tab = st.selectbox(
            "Your Backgrounds", files, index=0, help="The background video to use for the TikTok video")

        # Choose which video to generate
        videos = json.load(open("video.json"))

        video_num = st.multiselect(
            "Video",
            options=videos,
            format_func=lambda video: f"{video['series']} - {video['part']}",
            default=[videos[0]],
            help="The video to generate. If you want to generate multiple videos, select them as a multiselect."
        )

        st.divider()

        st.subheader("Audio Settings")

        add_audio = st.checkbox("Add Audio?", help="Add background audio to the video")
        mixing_percentage = 0.3  # Default mixing percentage

        if add_audio:
            selected_audio = st.file_uploader("Choose Audio File", type=["mp3", "wav"], help="Select an audio file to add to the video")
            mixing_percentage = st.slider("Mixing Percentage", 0.0, 1.0, 0.3, help="Adjust the mixing percentage for audio")
        
        st.divider()
        
        st.subheader("Generate Video")

        # Display the "Generate Video" button only if "Add Audio?" is not selected or if an audio file was added
        if not add_audio or (add_audio and selected_audio):
            if st.button("Generate Video"):
                if not video_num:
                    st.error("You must select at least one video to generate")
                    return
                global result
                selected_audio_path = None
                if add_audio and selected_audio:
                    with open("temp_audio_file.wav", "wb") as audio_file:
                        audio_file.write(selected_audio.read())
                    selected_audio_path = "temp_audio_file.wav"
                result = await generate_video(model, tts_voice, sub_position, font, font_color, font_size,
                                            url, non_english, upload_tiktok, verbose, videos, background_tab, video_num, max_words, add_audio, selected_audio_path, mixing_percentage)
        else:
            st.button("Generate Video", disabled=True)


    with RIGHT:
        if result:
            # Put the video in a container
            st.video(result)

if __name__ == "__main__":

    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    loop = asyncio.new_event_loop()

    loop.run_until_complete(main())

    loop.close()

    sys.exit(0)
