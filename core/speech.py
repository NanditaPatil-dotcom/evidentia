
import json
import os

from google import genai
from dotenv import load_dotenv

# Load .env
load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def _extract_json_payload(payload):
    text = (payload or "").strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start : end + 1]

    return text


def speech_to_english(audio_path):
    audio_file = client.files.upload(file=audio_path)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            """Analyze this audio and return valid JSON only.
Use exactly this schema:
{
  "regional_text": "<verbatim transcript in the original spoken language and script>",
  "english_text": "<faithful English translation of the same speech>"
}

Rules:
- Transcribe the spoken words exactly in `regional_text`.
- Translate the same spoken content faithfully in `english_text`.
- Do not add labels like "Language Detected" or "Transcription".
- Do not add markdown fences or explanations.
- Do not paraphrase or invent details.
- If the meaning is ambiguous, stay literal and conservative.
""",
            audio_file,
        ],
    )

    text1 = ""
    text2 = ""

    try:
        parsed = json.loads(_extract_json_payload(response.text))
        text1 = (parsed.get("regional_text") or "").strip()
        text2 = (parsed.get("english_text") or "").strip()
    except (json.JSONDecodeError, AttributeError):
        text2 = (response.text or "").strip()

    # safety fallback
    if not text1 or len(text1) < 3:
        text1 = "Unable to transcribe clearly"

    if not text2 or len(text2) < 3:
        text2 = "Unable to transcribe clearly"

    return text1, text2


def process_audio(audio_path):
    text1, text2 = speech_to_english(audio_path)

    return {
        "original_audio": audio_path,
        "regional_text": text1,
        "english_text": text2,
    }


# Test
if __name__ == "__main__":
    output = process_audio("sample1.wav")
    print(output)
