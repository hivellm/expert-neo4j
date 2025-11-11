"""
Run tests via CLI and display outputs for manual analysis (like compare.py)
"""

import subprocess
from pathlib import Path
import re

CLI_PATH = Path("../../cli/target/release/expert-cli.exe")
VERSION = "0.2.3"
CHECKLIST_MD = Path(__file__).parent.parent / "test_checklist.md"

# Test cases - same as run_all_tests.py
TEST_CASES = {
    "match_001": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\n  - `age`: INTEGER\nRelationships:\nNone", "user_prompt": "Find all people"},
    "match_002": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Movie**\n  - `title`: STRING\n  - `released`: INTEGER\nRelationships:\nNone", "user_prompt": "List all movies"},
    "match_003": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Product**\n  - `name`: STRING\n  - `price`: FLOAT\nRelationships:\nNone", "user_prompt": "Get all products"},
    "match_004": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **User**\n  - `username`: STRING\n  - `email`: STRING\nRelationships:\nNone", "user_prompt": "Show all users"},
    "match_005": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Book**\n  - `title`: STRING\n  - `author`: STRING\nRelationships:\nNone", "user_prompt": "Find all books"},
    "match_006": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **City**\n  - `name`: STRING\n  - `population`: INTEGER\nRelationships:\nNone", "user_prompt": "List all cities"},
    "match_007": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Company**\n  - `name`: STRING\n  - `industry`: STRING\nRelationships:\nNone", "user_prompt": "Get all companies"},
    "match_008": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Order**\n  - `id`: STRING\n  - `total`: FLOAT\nRelationships:\nNone", "user_prompt": "Find all orders"},
    "match_009": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Employee**\n  - `name`: STRING\n  - `department`: STRING\nRelationships:\nNone", "user_prompt": "Show all employees"},
    "match_010": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Customer**\n  - `name`: STRING\n  - `email`: STRING\nRelationships:\nNone", "user_prompt": "List all customers"},
    
    "where_001": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\n  - `age`: INTEGER\nRelationships:\nNone", "user_prompt": "Find people older than 30"},
    "where_002": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Product**\n  - `name`: STRING\n  - `price`: FLOAT\nRelationships:\nNone", "user_prompt": "Find products with price less than 100"},
    "where_003": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Movie**\n  - `title`: STRING\n  - `released`: INTEGER\nRelationships:\nNone", "user_prompt": "Find movies released after 2000"},
    "where_004": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\n  - `age`: INTEGER\n  - `city`: STRING\nRelationships:\nNone", "user_prompt": "Find people aged between 25 and 40"},
    "where_005": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Product**\n  - `name`: STRING\n  - `price`: FLOAT\n  - `category`: STRING\nRelationships:\nNone", "user_prompt": "Find products in Electronics category"},
    "where_006": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Employee**\n  - `name`: STRING\n  - `salary`: FLOAT\nRelationships:\nNone", "user_prompt": "Find employees with salary greater than 50000"},
    "where_007": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Book**\n  - `title`: STRING\n  - `year`: INTEGER\nRelationships:\nNone", "user_prompt": "Find books published before 2010"},
    "where_008": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **User**\n  - `username`: STRING\n  - `active`: BOOLEAN\nRelationships:\nNone", "user_prompt": "Find active users"},
    "where_009": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Order**\n  - `id`: STRING\n  - `total`: FLOAT\n  - `status`: STRING\nRelationships:\nNone", "user_prompt": "Find orders with status 'completed'"},
    "where_010": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\n  - `age`: INTEGER\n  - `city`: STRING\nRelationships:\nNone", "user_prompt": "Find people living in New York"},
    "where_011": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Product**\n  - `name`: STRING\n  - `price`: FLOAT\nRelationships:\nNone", "user_prompt": "Find products with price between 50 and 200"},
    "where_012": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Movie**\n  - `title`: STRING\n  - `rating`: FLOAT\nRelationships:\nNone", "user_prompt": "Find movies with rating above 8.0"},
    "where_013": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\n  - `age`: INTEGER\n  - `city`: STRING\nRelationships:\nNone", "user_prompt": "Find people aged between 25 and 40 living in New York"},
    "where_014": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Employee**\n  - `name`: STRING\n  - `salary`: FLOAT\n  - `department`: STRING\nRelationships:\nNone", "user_prompt": "Find employees in Sales department with salary over 60000"},
    "where_015": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Product**\n  - `name`: STRING\n  - `price`: FLOAT\n  - `in_stock`: BOOLEAN\nRelationships:\nNone", "user_prompt": "Find products in stock with price less than 50"},
}

def run_cli_test(test_id: str, full_prompt: str) -> str:
    """Run test via CLI and return output"""
    cmd = [
        str(CLI_PATH),
        "chat",
        "--experts", f"neo4j@{VERSION}",
        "--prompt", full_prompt,
        "--max-tokens", "500",
        "--temperature", "0.1",
        "--top-p", "0.95",
        "--top-k", "20",
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            check=True,
            timeout=60
        )
        output = result.stdout.strip()
        if "Assistant:" in output:
            output = output.split("Assistant:", 1)[1].strip()
        return output
    except subprocess.TimeoutExpired:
        return "[TIMEOUT]"
    except subprocess.CalledProcessError as e:
        return f"[ERROR: {e.stderr[:100]}]"
    except FileNotFoundError:
        return f"[ERROR: CLI not found]"

def print_separator():
    print("=" * 80)

def print_test_header(test_id: str, test_case: dict, idx: int, total: int):
    print_separator()
    print(f"TEST {idx}/{total}: {test_id}")
    print_separator()
    print(f"Category: {test_id.split('_')[0]}")
    print(f"User Prompt: {test_case['user_prompt']}")
    print()

def print_output(label: str, output: str):
    print(f"[{label}]")
    print("-" * 80)
    print(output)
    print("-" * 80)
    print()

def main():
    print_separator()
    print(f"MANUAL QUALITY ANALYSIS - EXPERT NEO4J v{VERSION}")
    print("Running tests via CLI and displaying outputs for manual analysis")
    print("(Similar to compare.py qualitative analysis)")
    print_separator()
    print()
    
    # Get incomplete tests from checklist
    if not CHECKLIST_MD.exists():
        print(f"Error: Checklist not found at {CHECKLIST_MD}")
        return
    
    content = CHECKLIST_MD.read_text(encoding='utf-8')
    
    # Extract test IDs that are not yet completed
    test_ids = []
    for test_id in TEST_CASES.keys():
        # Check if test is marked as incomplete in checklist
        pattern = rf'- \[ \] {re.escape(test_id)}'
        if re.search(pattern, content):
            test_ids.append(test_id)
    
    print(f"Found {len(test_ids)} tests to analyze")
    print()
    
    # Run tests and display outputs
    for idx, test_id in enumerate(test_ids, 1):
        test_case = TEST_CASES[test_id]
        full_prompt = f"{test_case['system_prompt']}\n\n{test_case['user_prompt']}"
        
        print_test_header(test_id, test_case, idx, len(test_ids))
        
        output = run_cli_test(test_id, full_prompt)
        
        print_output("CLI OUTPUT", output)
        
        print_separator()
        print()
        
        # Pause for manual analysis (optional - can be removed for batch processing)
        # input("Press Enter to continue to next test...")

if __name__ == "__main__":
    main()

