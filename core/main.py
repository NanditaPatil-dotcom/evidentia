from speech import process_audio
from classifier import classify_event
from entity_extractor import extract_entities
from legal_mapper import legal_mapping

def full_pipeline(audio_path):
    # 🎤 Step 1: Speech → English
    speech_output = process_audio(audio_path)

    text = speech_output["transcript"].strip().lower()

    # 🧠 Step 2: Event classification
    events = classify_event(text)
    # 🏷️ Step 3: Entity extraction
    entities = extract_entities(text)

    # ⚖️ Step 4: Legal mapping
    legal = legal_mapping(events, entities)

    return {
        "original_audio": speech_output["original_audio"],
        "transcript": text,
        "events": events,
        "entities": entities,
        "laws": legal["laws"],
        "statements": legal["statements"]
    }


# 🧪 Run test
if __name__ == "__main__":
    result = full_pipeline("sample.wav")

    print("\noutput")
    print(result)