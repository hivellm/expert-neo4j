import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from typing import Dict, List, Tuple


PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")
)
CLI_PATH = os.path.join(PROJECT_ROOT, "cli", "target", "release", "expert-cli.exe")

if not os.path.exists(CLI_PATH):
    raise FileNotFoundError(f"expert-cli binary not found at: {CLI_PATH}")


ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def strip_ansi(text: str) -> str:
    return ANSI_RE.sub("", text)


TEST_CASES = [
    {
        "id": "match_001",
        "category": "basic_match",
        "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\n  - `age`: INTEGER\nRelationships:\nNone",
        "user_prompt": "Find all people",
    },
    {
        "id": "match_002",
        "category": "basic_match",
        "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Movie**\n  - `title`: STRING\n  - `released`: INTEGER\nRelationships:\nNone",
        "user_prompt": "List all movies",
    },
    {
        "id": "where_001",
        "category": "where_filter",
        "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\n  - `age`: INTEGER\nRelationships:\nNone",
        "user_prompt": "Find people older than 30",
    },
    {
        "id": "where_002",
        "category": "where_filter",
        "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Product**\n  - `name`: STRING\n  - `price`: FLOAT\nRelationships:\nNone",
        "user_prompt": "Find products with price less than 100",
    },
    {
        "id": "rel_001",
        "category": "relationship",
        "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Movie**\n  - `title`: STRING\n- **Person**\n  - `name`: STRING\nRelationships:\n(:Person)-[:ACTED_IN]->(:Movie)",
        "user_prompt": "Find all actors in movies",
    },
    {
        "id": "rel_002",
        "category": "relationship",
        "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\nRelationships:\n(:Person)-[:KNOWS]->(:Person)",
        "user_prompt": "Find people who know each other",
    },
    {
        "id": "agg_001",
        "category": "aggregation",
        "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **User**\n  - `name`: STRING\nRelationships:\nNone",
        "user_prompt": "Count total users",
    },
    {
        "id": "agg_002",
        "category": "aggregation",
        "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Order**\n  - `total`: FLOAT\nRelationships:\n(:Customer)-[:PLACED]->(:Order)",
        "user_prompt": "Sum of all order totals",
    },
    {
        "id": "order_001",
        "category": "ordering",
        "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Product**\n  - `name`: STRING\n  - `price`: FLOAT\nRelationships:\nNone",
        "user_prompt": "Find top 5 most expensive products",
    },
    {
        "id": "order_002",
        "category": "ordering",
        "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Employee**\n  - `name`: STRING\n  - `salary`: FLOAT\nRelationships:\nNone",
        "user_prompt": "Show the 3 highest paid employees",
    },
    {
        "id": "multihop_001",
        "category": "multi_hop",
        "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\nRelationships:\n(:Person)-[:KNOWS]->(:Person)\n(:Person)-[:FOLLOWS]->(:Person)",
        "user_prompt": "Find people who know someone who follows another person",
    },
    {
        "id": "complex_001",
        "category": "complex",
        "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\n  - `age`: INTEGER\n  - `city`: STRING\nRelationships:\nNone",
        "user_prompt": "Find people aged between 25 and 40 living in New York",
    },
    {
        "id": "pattern_001",
        "category": "pattern",
        "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Business**\n  - `name`: STRING\n  - `category`: STRING\nRelationships:\n(:Business)-[:LOCATED_IN]->(:City)",
        "user_prompt": "Find all restaurants in cities",
    },
    {
        "id": "return_001",
        "category": "return",
        "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\n  - `age`: INTEGER\n  - `email`: STRING\nRelationships:\nNone",
        "user_prompt": "Get names and emails of all people",
    },
]


EXPERT_SPECS = {
    "current": "expert-neo4j",
    "v0.1.1": "expert-neo4j@0.1.1",
}


class CLIChatSession:
    def __init__(self, expert_spec: str) -> None:
        self.expert_spec = (
            expert_spec
            if expert_spec.startswith("expert-")
            else f"expert-{expert_spec}"
        )
        self.prompt_marker = f"{self.expert_spec}> "
        self.process = subprocess.Popen(
            [
                CLI_PATH,
                "chat",
                "--experts",
                expert_spec,
                "--device",
                "cuda",
                "--max-tokens",
                "200",
                "--temperature",
                "0.6",
                "--top-p",
                "0.95",
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            encoding="utf-8",
            errors="replace",
        )

        self.initial_stdout = strip_ansi(self._collect_until_prompt())

    def _collect_until_prompt(self) -> str:
        buffer: List[str] = []
        clean_buffer = ""

        while True:
            line = self.process.stdout.readline()
            if not line:
                break

            buffer.append(line)
            clean_buffer += strip_ansi(line)

            if clean_buffer.rstrip().endswith(self.prompt_marker.rstrip()):
                break

        return "".join(buffer)

    def ask(self, prompt: str) -> Dict[str, str]:
        if self.process.poll() is not None:
            raise RuntimeError("CLI process terminated unexpectedly.")

        self.process.stdin.write(prompt.replace("\r", "") + "\n")
        self.process.stdin.flush()

        raw_output = self._collect_until_prompt()
        clean_output = strip_ansi(raw_output)

        marker_index = clean_output.rfind(self.prompt_marker)
        if marker_index != -1:
            clean_output = clean_output[:marker_index]

        return {
            "raw_output": raw_output,
            "clean_output": clean_output.strip(),
        }

    def close(self) -> Tuple[str, str]:
        if self.process.poll() is None:
            try:
                self.process.stdin.write("exit\n")
                self.process.stdin.flush()
            except BrokenPipeError:
                pass

        remaining_stdout = self.process.stdout.read() or ""
        remaining_stderr = self.process.stderr.read() or ""

        self.process.terminate()

        return strip_ansi(remaining_stdout), strip_ansi(remaining_stderr)


def main() -> None:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(
        os.path.dirname(__file__),
        f"cli_comparison_results_{timestamp}.json",
    )

    comparison = {
        "generated_at_utc": timestamp,
        "cli_path": CLI_PATH,
        "experts": EXPERT_SPECS,
        "sessions": {},
        "results": [],
    }

    sessions = {
        label: CLIChatSession(spec) for label, spec in EXPERT_SPECS.items()
    }

    for label, session in sessions.items():
        comparison["sessions"][label] = {
            "initial_stdout": session.initial_stdout.strip(),
        }

    try:
        for case in TEST_CASES:
            prompt = f"{case['system_prompt']}\n\n{case['user_prompt']}"
            case_result = {
                "id": case["id"],
                "category": case["category"],
                "system_prompt": case["system_prompt"],
                "user_prompt": case["user_prompt"],
            }

            for label, session in sessions.items():
                print(f"[{case['id']}] running {label}...")
                case_result[label] = session.ask(prompt)

            comparison["results"].append(case_result)
    finally:
        for label, session in sessions.items():
            final_stdout, final_stderr = session.close()
            comparison["sessions"][label]["final_stdout"] = final_stdout.strip()
            if final_stderr.strip():
                comparison["sessions"][label]["stderr"] = final_stderr.strip()

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(comparison, f, ensure_ascii=False, indent=2)

    print(f"\nCLI comparison results saved to: {output_path}")


if __name__ == "__main__":
    sys.exit(main())

