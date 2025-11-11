#!/usr/bin/env python3
"""
Test Known Limitations via CLI - Expert Neo4j v0.2.3
Tests each limitation to verify if resolved
"""
import subprocess
import sys
from pathlib import Path

CLI_PATH = Path(__file__).parent.parent.parent / "cli" / "target" / "release" / "expert-cli.exe"

TEST_CASES = [
    {
        "id": "complex_or_and_logic",
        "name": "Complex OR/AND logic",
        "description": "Multi-condition WHERE filters",
        "prompt": """Dialect: cypher
Schema:
Node properties:
- **Person**
  - `name`: STRING
  - `age`: INTEGER
  - `city`: STRING
Relationships:
None

Find people aged between 25 and 40 living in New York"""
    },
    {
        "id": "string_pattern_contains",
        "name": "String pattern matching (CONTAINS)",
        "description": "CONTAINS pattern matching",
        "prompt": """Dialect: cypher
Schema:
Node properties:
- **Product**
  - `name`: STRING
  - `description`: STRING
Relationships:
None

Find products whose name contains 'laptop'"""
    },
    {
        "id": "avg_group_by",
        "name": "AVG with GROUP BY",
        "description": "Complex aggregation grouping",
        "prompt": """Dialect: cypher
Schema:
Node properties:
- **Movie**
  - `title`: STRING
  - `genre`: STRING
  - `rating`: FLOAT
Relationships:
None

Find the average rating for each genre"""
    },
    {
        "id": "relationship_properties_dates",
        "name": "Relationship properties with dates",
        "description": "Temporal filters on relationships",
        "prompt": """Dialect: cypher
Schema:
Node properties:
- **Person**
  - `name`: STRING
- **Company**
  - `name`: STRING
Relationships:
(:Person)-[:WORKS_AT {start_date: DATE}]->(:Company)

Find people who started working after 2020-01-01"""
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
        "--temperature", "0.6"
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

def is_valid_cypher(output: str) -> bool:
    """Check if output is valid Cypher query"""
    output_lower = output.lower()
    # Check for Cypher keywords
    has_match = "match" in output_lower
    has_return = "return" in output_lower
    
    # Check if it's NOT just explanatory text
    is_explanatory = any(phrase in output_lower for phrase in [
        "the user wants",
        "i need to",
        "let me",
        "the schema",
        "the dialect",
        "could you",
        "maybe"
    ])
    
    return has_match and has_return and not is_explanatory

def check_specific_patterns(test_id: str, output: str) -> dict:
    """Check for specific patterns based on test type"""
    output_lower = output.lower()
    results = {}
    
    if test_id == "complex_or_and_logic":
        results["has_multiple_conditions"] = "and" in output_lower or "or" in output_lower
        results["has_age_range"] = "age" in output_lower and ("25" in output or "40" in output)
        results["has_city_filter"] = "city" in output_lower and "new york" in output_lower
        results["valid"] = is_valid_cypher(output) and results["has_multiple_conditions"]
    
    elif test_id == "string_pattern_contains":
        results["has_contains"] = "contains" in output_lower or "=~" in output
        results["has_laptop"] = "laptop" in output_lower
        results["valid"] = is_valid_cypher(output) and results["has_contains"]
    
    elif test_id == "avg_group_by":
        results["has_avg"] = "avg" in output_lower
        results["has_group_by"] = "group by" in output_lower or "with" in output_lower
        results["has_genre"] = "genre" in output_lower
        results["valid"] = is_valid_cypher(output) and results["has_avg"] and results["has_group_by"]
    
    elif test_id == "relationship_properties_dates":
        results["has_relationship"] = "works_at" in output_lower or "[:works_at" in output_lower
        results["has_date_filter"] = "2020" in output or "date" in output_lower
        results["has_start_date"] = "start_date" in output_lower
        results["valid"] = is_valid_cypher(output) and results["has_relationship"] and results["has_date_filter"]
    
    return results

def main():
    print("=" * 80)
    print("TESTING KNOWN LIMITATIONS - EXPERT NEO4J v0.2.3")
    print("Testing via CLI")
    print("=" * 80)
    print()
    
    results = {}
    
    for test in TEST_CASES:
        print(f"\n{'=' * 80}")
        print(f"TEST: {test['name']}")
        print(f"Description: {test['description']}")
        print(f"{'=' * 80}\n")
        
        print(f"[PROMPT]")
        print(test['prompt'])
        print()
        
        # Test v0.2.3
        print(f"[VERSION 0.2.3 OUTPUT]")
        output = run_cli_chat("0.2.3", test['prompt'])
        print(output)
        print()
        
        # Analyze output
        is_valid = is_valid_cypher(output)
        specific_checks = check_specific_patterns(test['id'], output)
        
        print(f"[ANALYSIS]")
        print(f"Valid Cypher: {is_valid}")
        for key, value in specific_checks.items():
            if key != "valid":
                print(f"  {key}: {value}")
        
        status = "[OK] RESOLVED" if (is_valid and specific_checks.get("valid", False)) else "[FAIL] NOT RESOLVED"
        print(f"\nStatus: {status}")
        
        results[test['id']] = {
            "output": output,
            "is_valid_cypher": is_valid,
            "specific_checks": specific_checks,
            "resolved": is_valid and specific_checks.get("valid", False)
        }
        
        print("-" * 80)
    
    # Summary
    print(f"\n{'=' * 80}")
    print("SUMMARY")
    print(f"{'=' * 80}\n")
    
    for test in TEST_CASES:
        result = results[test['id']]
        status_icon = "[OK]" if result['resolved'] else "[FAIL]"
        print(f"{status_icon} {test['name']}: {'RESOLVED' if result['resolved'] else 'NOT RESOLVED'}")
    
    resolved_count = sum(1 for r in results.values() if r['resolved'])
    total_count = len(results)
    
    print(f"\nTotal: {resolved_count}/{total_count} limitations resolved")
    print(f"{'=' * 80}")

if __name__ == "__main__":
    main()

