"""
Uploads are currently limited to 25 MB and the following input
file types are supported: mp3, mp4, mpeg, mpga, m4a, wav, and webm
"""

import openai
import os
from dotenv import load_dotenv

class AudioToText:
    """
    A class for transcribing audio files using OpenAI's Audio API.
    """
    def __init__(self, audio, output_transcription_file="transcript.txt"):
        load_dotenv()
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.audio = audio
        self.output_transcription_file = output_transcription_file

    def transcribe(self):
        """
        Transcribes the audio file specified by `self.file_name` using OpenAI's
        Audio API and saves the transcription to a file named `transcript.txt`.
        """

        audio_file = open(self.audio, "rb")
        transcript = openai.Audio.transcribe(
            model="whisper-1",
            file=audio_file
        )
        # save transcription to file
        with open(self.output_transcription_file, "w", encoding="utf8") as f:
            f.write(transcript.text)
        return transcript.text
