from transformers import pipeline


classifier = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli",
)

LABELS = [
    "physical abuse",
    "verbal abuse",
    "threat",
    "financial abuse",
    "harassment",
    "emotional abuse",
]


def classify_event(text):
    result = classifier(text, LABELS, multi_label=True)

    classified = []

    for label, score in zip(result["labels"], result["scores"]):
        if score > 0.5:
            classified.append(
                {
                    "label": label,
                    "confidence": round(score, 2),
                }
            )

    return classified


if __name__ == "__main__":
    text = "He shouted at me and threatened to hurt me."

    output = classify_event(text)

    print("\n--- Classification ---")
    print(output)
