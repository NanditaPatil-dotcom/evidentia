from speech import process_audio
from classifier import classify_event


def full_pipeline(audio_path):
    # 🎤 Step 1: Speech → English
    speech_output = process_audio(audio_path)

    text = speech_output["transcript"].strip().lower()

    # 🧠 Step 2: Event classification
    events = classify_event(text)

    return {
        "original_audio": speech_output["original_audio"],
        "transcript": text,
        "events": events
    }


# 🧪 Run test
if __name__ == "__main__":
    result = full_pipeline("sample.wav")

    print("\noutput")
    print(result)