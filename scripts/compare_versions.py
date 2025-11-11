#!/usr/bin/env python3
"""
Compare expert-neo4j versions 0.1.1 and 0.2.3 using CLI
"""
import subprocess
import json
import sys
from pathlib import Path

CLI_PATH = Path(__file__).parent.parent.parent / "cli" / "target" / "release" / "expert-cli.exe"

TEST_CASES = [
    {
        "id": "match_001",
        "category": "basic_match",
        "prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\n  - `age`: INTEGER\nRelationships:\nNone\n\nFind all people"
    },
    {
        "id": "match_002",
        "category": "basic_match",
        "prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Movie**\n  - `title`: STRING\n  - `released`: INTEGER\nRelationships:\nNone\n\nList all movies"
    },
    {
        "id": "where_001",
        "category": "where_filter",
        "prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\n  - `age`: INTEGER\nRelationships:\nNone\n\nFind people older than 30"
    },
    {
        "id": "where_002",
        "category": "where_filter",
        "prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Product**\n  - `name`: STRING\n  - `price`: FLOAT\nRelationships:\nNone\n\nFind products with price less than 100"
    },
    {
        "id": "rel_001",
        "category": "relationship",
        "prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Movie**\n  - `title`: STRING\n- **Person**\n  - `name`: STRING\nRelationships:\n(:Person)-[:ACTED_IN]->(:Movie)\n\nFind all actors in movies"
    },
    {
        "id": "agg_001",
        "category": "aggregation",
        "prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **User**\n  - `name`: STRING\nRelationships:\nNone\n\nCount total users"
    },
    {
        "id": "order_001",
        "category": "ordering",
        "prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Product**\n  - `name`: STRING\n  - `price`: FLOAT\nRelationships:\nNone\n\nFind top 5 most expensive products"
    },
    {
        "id": "complex_001",
        "category": "complex",
        "prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\n  - `age`: INTEGER\n  - `city`: STRING\nRelationships:\nNone\n\nFind people aged between 25 and 40 living in New York"
    }
]

def run_cli_chat(version: str, prompt: str) -> str:
    """Run CLI chat command and return output"""
    cmd = [
        str(CLI_PATH),
        "chat",
        "--experts", f"expert-neo4j@{version}",
        "--prompt", prompt,
        "--max-tokens", "300",
        "--temperature", "0.1"
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=CLI_PATH.parent.parent.parent
        )
        if result.returncode != 0:
            return f"[ERROR: {result.stderr}]"
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return "[TIMEOUT]"
    except Exception as e:
        return f"[ERROR: {str(e)}]"

def main():
    print("=" * 80)
    print("EXPERT NEO4J VERSION COMPARISON")
    print("Comparing v0.1.1 vs v0.2.3 using CLI")
    print("=" * 80)
    print()
    
    results = {
        "v0.1.1": {},
        "v0.2.3": {}
    }
    
    for i, test in enumerate(TEST_CASES, 1):
        print(f"\n{'=' * 80}")
        print(f"TEST {i}/{len(TEST_CASES)}: {test['id']}")
        print(f"Category: {test['category']}")
        print(f"{'=' * 80}\n")
        
        print(f"[PROMPT]")
        print(test['prompt'])
        print()
        
        # Test v0.1.1
        print(f"[VERSION 0.1.1]")
        v011_output = run_cli_chat("0.1.1", test['prompt'])
        print(v011_output)
        results["v0.1.1"][test['id']] = v011_output
        print()
        
        # Test v0.2.3
        print(f"[VERSION 0.2.3]")
        v023_output = run_cli_chat("0.2.3", test['prompt'])
        print(v023_output)
        results["v0.2.3"][test['id']] = v023_output
        print()
        
        print("-" * 80)
    
    # Save results
    output_file = Path(__file__).parent / "version_comparison_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'=' * 80}")
    print("COMPARISON COMPLETE")
    print(f"Results saved to: {output_file}")
    print(f"{'=' * 80}")

if __name__ == "__main__":
    main()

