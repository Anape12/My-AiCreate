import json
from pathlib import Path


def export_successful_experiences(experiences: list[dict], output_path: str | Path) -> int:
    """Export successful experiences to JSONL suitable for later instruction tuning."""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    successful = [item for item in experiences if item.get("success") and item.get("answer")]
    with output.open("w", encoding="utf-8") as file:
        for item in successful:
            record = {
                "messages": [
                    {"role": "user", "content": item["query"]},
                    {"role": "assistant", "content": item["answer"]},
                ]
            }
            file.write(json.dumps(record, ensure_ascii=False) + "\n")
    return len(successful)
