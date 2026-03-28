from transformers import pipeline


classifier = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli",
)

LABELS = [
    "physical abuse",
    "threat",
    "verbal abuse",
    "financial abuse",
]


def classify_event(text, top_k=1):
    result = classifier(text, LABELS)

    classified = []

    for label, score in zip(result["labels"], result["scores"]):
        classified.append(
            {
                "label": label,
                "confidence": round(score, 2),
            }
        )

    classified = sorted(classified, key=lambda x: x["confidence"], reverse=True)

    return classified[:top_k]


def clean_events(events):
    labels = [event["label"] for event in events]

    if "physical abuse" in labels:
        return [event for event in events if event["label"] == "physical abuse"]

    if "threat" in labels:
        return [event for event in events if event["label"] == "threat"]

    return events


if __name__ == "__main__":
    text = "He shouted at me and threatened to hurt me."

    output = classify_event(text)

    print("\n--- Classification ---")
    print(output)
