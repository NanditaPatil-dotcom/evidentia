EVENT_TO_LAW = {
    "physical abuse": ["BNS Section 115", "IPC 323"],
    "threat": ["IPC 506"],
    "verbal abuse": ["Domestic Violence Act"],
    "harassment": ["Domestic Violence Act"],
    "emotional abuse": ["Domestic Violence Act"],
    "financial abuse": ["Domestic Violence Act"]
}

EVENT_TO_PHRASE = {
    "physical abuse": "physically assaulted the complainant",
    "threat": "criminally intimidated the complainant",
    "verbal abuse": "verbally abused the complainant",
    "harassment": "harassed the complainant",
    "emotional abuse": "caused emotional distress to the complainant",
    "financial abuse": "financially exploited the complainant"
}

from datetime import datetime, timedelta

def normalize_date(date_text):
    today = datetime.today()

    if date_text == "today":
        return today.strftime("%d %B %Y")

    elif date_text == "yesterday":
        return (today - timedelta(days=1)).strftime("%d %B %Y")

    return date_text  


def interpret_time(text):
    text = (text or "").lower()

    if "night" in text:
        return "between 8:00 PM and 11:00 PM"
    if "morning" in text:
        return "between 6:00 AM and 10:00 AM"

    return None

def map_laws(events):
    laws = []

    for event in events:
        label = event["label"]

        if label in EVENT_TO_LAW:
            for law in EVENT_TO_LAW[label]:
                if law not in laws:
                    laws.append(law)

    return laws

def generate_statement(events, entities):
    date = normalize_date(entities.get("date"))
    time = entities.get("time") or interpret_time(entities.get("text", "")) or "unknown time"

    statements = []

    for event in events:
        label = event["label"]

        phrase = EVENT_TO_PHRASE.get(label, "committed an offense")

        sentence = f"On {date}, at approximately {time}, the accused allegedly {phrase}."
        statements.append(sentence)

    return statements

def legal_mapping(events, entities):
    laws = map_laws(events)
    statements = generate_statement(events, entities)

    return {
        "laws": laws,
        "statements": statements
    }


