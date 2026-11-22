from app.utils.burnout_engine import (
    analyze_burnout
)

async def analyze_weekly_journals(
    journals
):

    labels = []

    results = []

    i = 0

    for journal in journals:
        i += 1
        label = journal.label.lower()

        labels.append(label)

        results.append({
            "day": i,
            "translated_text": journal.translated_text,
            "label": label
        })

    burnout_result = analyze_burnout(
        labels
    )
    return {
        "state": burnout_result[
            "state"
        ],
    }