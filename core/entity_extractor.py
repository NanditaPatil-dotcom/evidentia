import re

import spacy

nlp = spacy.load("en_core_web_sm")

LOCATION_PREPOSITIONS = {"in", "at", "near", "from", "inside", "outside"}


def _extract_location_from_context(text):
    match = re.search(
        r"\b(?:in|at|near|from|inside|outside)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b",
        text,
    )
    if match:
        return match.group(1)

    return None

def extract_entities(text):
    doc = nlp(text)

    entities = {
        "date": None,
        "time": None,
        "location": None,
        "person": None
    }

    for ent in doc.ents:
        if ent.label_ == "DATE":
            entities["date"] = ent.text

        elif ent.label_ == "TIME":
            entities["time"] = ent.text

        elif ent.label_ in ["GPE", "LOC"]:
            entities["location"] = ent.text

        elif ent.label_ == "PERSON":
            prev_token = doc[ent.start - 1].text.lower() if ent.start > 0 else ""

            # spaCy can occasionally tag place names as PERSON.
            if prev_token in LOCATION_PREPOSITIONS and not entities["location"]:
                entities["location"] = ent.text
            elif not entities["person"]:
                entities["person"] = ent.text

    text_lower = text.lower()

    # location rules
    if "home" in text_lower:
        entities["location"] = "residence"

    if "house" in text_lower:
        entities["location"] = "residence"

    if not entities["location"]:
        entities["location"] = _extract_location_from_context(text)

    # person rules
    if not entities["person"] and re.search(r"\bhe\b", text_lower):
        entities["person"] = "accused"

    if entities["person"] == entities["location"]:
        entities["person"] = "accused"

    return entities

