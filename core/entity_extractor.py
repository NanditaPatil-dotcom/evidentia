import spacy

nlp = spacy.load("en_core_web_sm")

def extract_entities(text):
    doc = nlp(text)

    entities = {
        "person": None
    }

    for ent in doc.ents:
        if ent.label_ == "PERSON":
            entities["person"] = ent.text

    text_lower = text.lower()

    if any(word in text_lower for word in ["he", "him", "husband"]):
        entities["person"] = "accused"

    return entities
