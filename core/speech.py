
import os

from google import genai
from dotenv import load_dotenv

# Load .env
load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def speech_to_english(audio_path):
    audio_file = client.files.upload(file=audio_path)
    response1 = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            "Transcribe this audio and translate it into clear English. Only output the final sentence.",
            audio_file,
        ],
    )
    response2 = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            "Transcribe this audio and give me the regional language text. Only output the final sentence.For example, if the audio is in Kannada,in kannada it is 'ನೀವು ಹೇಗಿದ್ದೀರಾ?' but in English it is 'How are you?'. So I want the output in the original language of the audio that is kannada",
            response1.text,
        ],
    )

    text1 = (response1.text or "").strip()
    text2 = (response2.text or "").strip()

    # safety fallback
    if not text1 or len(text1) < 3:
        text1 = "Unable to transcribe clearly"

    return text1, text2


def process_audio(audio_path):
    text1, text2 = speech_to_english(audio_path)

    return {
        "original_audio": audio_path,
        "transcript": text1,
        "regional_text": text2,
    }


# Test
if __name__ == "__main__":
    output = process_audio("sample.wav")
    print(output)
