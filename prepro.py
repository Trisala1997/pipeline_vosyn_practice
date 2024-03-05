from moviepy.editor import VideoFileClip
from pydub import AudioSegment
import mimetypes
import os

def process_file(source_directory, target_directory, filename):
    try:
        # Construct full file path
        source_file_path = os.path.join(source_directory, filename)
        filename_without_ext = os.path.splitext(filename)[0]
        target_filename = f"{filename_without_ext}_prepro"

        # Determine the MIME type of the file
        mime_type = mimetypes.guess_type(source_file_path)[0]

        if mime_type and mime_type.startswith('video'):
            # File is a video
            split_audio_video(source_file_path, target_directory, target_filename)
        elif mime_type and mime_type.startswith('audio'):
            # File is an audio
            convert_audio(source_file_path, target_directory, target_filename)
        else:
            print("Unsupported file type")
    except Exception as e:
        print(f"An error occurred: {e}")

def split_audio_video(video_file_path, target_directory, target_filename):
    try:
        # Load video
        with VideoFileClip(video_file_path) as video:
            # Save audio
            audio = video.audio
            audio_filename = os.path.join(target_directory, f"{target_filename}.wav")
            audio.write_audiofile(audio_filename, codec='pcm_s16le')

            # Save video without audio
            video_without_audio = video.without_audio()
            video_without_audio_filename = os.path.join(target_directory, f"{target_filename}.mp4")
            video_without_audio.write_videofile(video_without_audio_filename, codec='libx264')

            # Convert audio to desired format
            convert_audio(audio_filename, target_directory, target_filename)
    except Exception as e:
        print(f"An error occurred: {e}")

def convert_audio(audio_file_path, target_directory, target_filename):
    try:
        # Load audio
        audio = AudioSegment.from_file(audio_file_path)

        # Convert audio to desired format
        audio = audio.set_channels(1)  # Convert to mono
        audio = audio.normalize()  # Normalize audio
        audio = audio.set_frame_rate(16000)  # Resample to 16kHz
        output_audio_filename = os.path.join(target_directory, f"{target_filename}.wav")
        audio.export(output_audio_filename, format="wav")  # Save as .wav
    except Exception as e:
        print(f"An error occurred: {e}")
