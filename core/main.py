from datetime import datetime

from speech import process_audio
from classifier import classify_event, clean_events
from entity_extractor import extract_entities
from legal_mapper import legal_mapping

def _normalize_browser_location(browser_location):
    if not isinstance(browser_location, dict):
        return browser_location, None

    city = browser_location.get("city")
    coordinates = browser_location.get("coordinates")

    if city:
        return city, coordinates

    if isinstance(coordinates, dict):
        latitude = coordinates.get("latitude")
        longitude = coordinates.get("longitude")
        if latitude is not None and longitude is not None:
            return f"{latitude}, {longitude}", coordinates

    return None, coordinates


def full_pipeline(audio_path, browser_location=None):
    # 🎤 Step 1: Speech → English
    speech_output = process_audio(audio_path)

    text = speech_output["transcript"].strip().lower()
    timestamp = datetime.now()
    location_text, coordinates = _normalize_browser_location(browser_location)

    # 🧠 Step 2: Event classification
    events = classify_event(text, top_k=2)
    events = clean_events(events)
    # 🏷️ Step 3: Entity extraction
    entities = extract_entities(text)
    entities.update(
        {
            "date": timestamp.strftime("%d %B %Y"),
            "time": timestamp.strftime("%I:%M %p"),
            "location": location_text,
        }
    )

    # ⚖️ Step 4: Legal mapping
    legal = legal_mapping(events, entities)

    return {
        "original_audio": speech_output["original_audio"],
        "transcript": text,
        "logged_at": timestamp.isoformat(),
        "coordinates": coordinates,
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
