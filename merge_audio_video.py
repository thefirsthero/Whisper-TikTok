from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip
import os
import tempfile

def merge_video_and_audio(video_path, audio_path, output_path, mixing_percentage):
    # Load video clip
    video_clip = VideoFileClip(video_path)

    # Load audio clip
    audio_clip = AudioFileClip(audio_path)

    # Trim audio to match the video duration
    if audio_clip.duration > video_clip.duration:
        audio_clip = audio_clip.subclip(0, video_clip.duration)
    else:
        audio_clip = audio_clip.set_duration(video_clip.duration)

    # Adjust audio volumes
    video_clip = video_clip.volumex(1 - mixing_percentage)
    audio_clip = audio_clip.volumex(mixing_percentage)

    # Combine original and background audio clips
    final_audio = CompositeAudioClip([video_clip.audio, audio_clip])

    # Set audio of the video to the loaded audio clip
    video_clip = video_clip.set_audio(final_audio)

    # Write the result to a temporary file
    temp_output_file = os.path.join(tempfile.mkdtemp(), 'temp_output.mp4')
    video_clip.write_videofile(temp_output_file, codec='libx264', audio_codec='aac')

    # Close the clips
    video_clip.close()
    audio_clip.close()

    # Remove the original video file
    os.remove(video_path)

    # Rename the temporary file to the output path
    os.rename(temp_output_file, output_path)

    print("Video merged successfully!")
