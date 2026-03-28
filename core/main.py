from datetime import datetime

try:
    from core.speech import process_audio
    from core.classifier import classify_event, clean_events
    from core.entity_extractor import extract_entities
    from core.legal_mapper import legal_mapping
except ModuleNotFoundError:
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


def full_pipeline(audio_input, browser_location=None):
    if isinstance(audio_input, dict):
        speech_output = audio_input
    else:
        speech_output = process_audio(audio_input)

    english_text = speech_output.get("english_text", "").strip()
    analysis_text = english_text.lower()
    timestamp = datetime.now()
    location_text, coordinates = _normalize_browser_location(browser_location)

    events = clean_events(classify_event(analysis_text, top_k=2))
    entities = extract_entities(analysis_text)
    entities.update(
        {
            "date": timestamp.strftime("%d %B %Y"),
            "time": timestamp.strftime("%I:%M %p"),
            "location": location_text,
        }
    )
    legal_output = legal_mapping(events, entities)

    return {
        "original_audio": speech_output.get("original_audio"),
        "regional_text": speech_output.get("regional_text"),
        "english_text": english_text,
        "logged_at": timestamp.isoformat(),
        "coordinates": coordinates,
        "events": events,
        "entities": entities,
        "laws": legal_output.get("laws", []),
        "statements": legal_output.get("statements", []),
    }


if __name__ == "__main__":
    audio_path = "sample1.wav"
    speech_output = process_audio(audio_path)
    result = full_pipeline(speech_output)
    print(result)
