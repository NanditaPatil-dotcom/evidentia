from transformers import pipeline


classifier = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli",
)

LABELS = [
"physical abuse (assault, hitting, violence)",
"criminal intimidation (threat to harm, kill)",
"verbal abuse (insults, shouting, humiliation)",
"financial abuse (money control, denial of resources)",
"emotional abuse (mental harassment, distress)",
"domestic violence",
"dowry harassment"
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


def clean_events(events, threshold=0.5):
    return [
        event for event in events
        if event["confidence"] >= threshold
    ]


if __name__ == "__main__":
    text = "He shouted at me and threatened to hurt me."

    output = classify_event(text)

    print("\n--- Classification ---")
    print(output)
