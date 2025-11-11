import json
from collections import Counter, defaultdict
from pathlib import Path

DATASET_DIR = Path(__file__).resolve().parent.parent / "datasets"
TARGET_FILES = [
    "synthetic_return.jsonl",
    "synthetic_merge.jsonl",
    "synthetic_with.jsonl",
    "synthetic_call.jsonl",
    "synthetic_remove.jsonl",
]


def parse_entry(raw_text: str) -> dict:
    """Extract system, user, assistant blocks from the text."""
    segments = {}
    parts = raw_text.split("<|im_start|>")
    for part in parts:
        if not part.strip():
            continue
        try:
            role, content = part.split("\n", 1)
        except ValueError:
            continue
        role = role.strip()
        content = content.replace("<|im_end|>", "").strip()
        segments[role] = content
    return segments


def analyze_file(path: Path) -> dict:
    """Return statistics about repetition and uniqueness for a dataset."""
    system_counter = Counter()
    user_counter = Counter()
    assistant_counter = Counter()
    errors = 0

    with path.open("r", encoding="utf-8") as f:
        for idx, line in enumerate(f, start=1):
            if not line.strip():
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError as exc:
                errors += 1
                print(f"    JSON error on line {idx}: {exc}")
                continue
            text = data.get("text", "")
            segments = parse_entry(text)

            system_counter[segments.get("system", "")] += 1
            user_counter[segments.get("user", "")] += 1
            assistant_counter[segments.get("assistant", "")] += 1

    total = sum(assistant_counter.values())
    return {
        "total_samples": total,
        "system_unique": len(system_counter),
        "user_unique": len(user_counter),
        "assistant_unique": len(assistant_counter),
        "repeated_user_prompts": [item for item, count in user_counter.items() if count > 1],
        "repeated_assistant_queries": [item for item, count in assistant_counter.items() if count > 1],
        "max_user_repeat": max(user_counter.values()) if user_counter else 0,
        "max_assistant_repeat": max(assistant_counter.values()) if assistant_counter else 0,
        "errors": errors,
    }


def main():
    print("Synthetic Dataset Consistency Report\n" + "=" * 40)

    aggregated = defaultdict(int)

    for filename in TARGET_FILES:
        path = DATASET_DIR / filename
        if not path.exists():
            print(f"- {filename}: not found")
            continue

        stats = analyze_file(path)
        aggregated["total_samples"] += stats["total_samples"]
        aggregated["assistant_unique"] += stats["assistant_unique"]

        print(f"\nDataset: {filename}")
        print(f"  Total samples           : {stats['total_samples']}")
        print(f"  Unique system prompts   : {stats['system_unique']}")
        print(f"  Unique user prompts     : {stats['user_unique']}")
        print(f"  Unique assistant queries: {stats['assistant_unique']}")
        print(f"  Max user repetition     : {stats['max_user_repeat']}")
        print(f"  Max assistant repetition: {stats['max_assistant_repeat']}")
        if stats["errors"]:
            print(f"    Errors detected         : {stats['errors']}")

        if stats["max_user_repeat"] > 1:
            print(f"    Warning: {len(stats['repeated_user_prompts'])} user prompts repeat.")
        if stats["max_assistant_repeat"] > 1:
            print(f"    Warning: {len(stats['repeated_assistant_queries'])} assistant queries repeat.")

    print("\nSummary")
    print("  Total samples analyzed      :", aggregated["total_samples"])
    print("  Total unique assistant text :", aggregated["assistant_unique"])


if __name__ == "__main__":
    main()
