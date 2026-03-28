
import os

from google import genai
from dotenv import load_dotenv

# Load .env
load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def speech_to_english(audio_path):
    audio_file = client.files.upload(file=audio_path)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            "Transcribe this audio and translate it into clear English. Only output the final sentence.",
            audio_file,
        ],
    )

    text = (response.text or "").strip()

    # safety fallback
    if not text or len(text) < 3:
        text = "Unable to transcribe clearly"

    return text


def process_audio(audio_path):
    text = speech_to_english(audio_path)

    return {
        "original_audio": audio_path,
        "transcript": text,
    }


# Test
if __name__ == "__main__":
    output = process_audio("sample.wav")
    print(output)
