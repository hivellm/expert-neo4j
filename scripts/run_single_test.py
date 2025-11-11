"""
Run a single test via CLI and update checklist
"""

import subprocess
import json
import sys
from pathlib import Path

CLI_PATH = Path("../../cli/target/release/expert-cli.exe")
CHECKLIST_FILE = Path("../test_checklist.json")
VERSION = "0.2.3"

# Test cases (same structure)
TEST_CASES = [
    {"id": "match_001", "category": "basic_match", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\n  - `age`: INTEGER\nRelationships:\nNone", "user_prompt": "Find all people"},
    {"id": "match_002", "category": "basic_match", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Movie**\n  - `title`: STRING\n  - `released`: INTEGER\nRelationships:\nNone", "user_prompt": "List all movies"},
    {"id": "match_003", "category": "basic_match", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Product**\n  - `name`: STRING\n  - `price`: FLOAT\nRelationships:\nNone", "user_prompt": "Get all products"},
    {"id": "match_004", "category": "basic_match", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **User**\n  - `username`: STRING\n  - `email`: STRING\nRelationships:\nNone", "user_prompt": "Show all users"},
    {"id": "match_005", "category": "basic_match", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Book**\n  - `title`: STRING\n  - `author`: STRING\nRelationships:\nNone", "user_prompt": "Find all books"},
]

def load_checklist():
    """Load checklist from file"""
    if CHECKLIST_FILE.exists():
        with open(CHECKLIST_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "version": VERSION,
        "total_tests": len(TEST_CASES),
        "completed": 0,
        "tests": []
    }

def save_checklist(checklist):
    """Save checklist to file"""
    with open(CHECKLIST_FILE, 'w', encoding='utf-8') as f:
        json.dump(checklist, f, indent=2, ensure_ascii=False)

def run_cli_test(test_id, full_prompt):
    """Run single test via CLI"""
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
            check=True
        )
        output = result.stdout.strip()
        # Remove "Assistant:" prefix if present
        if "Assistant:" in output:
            output = output.split("Assistant:", 1)[1].strip()
        return output, None
    except subprocess.CalledProcessError as e:
        return None, str(e)

def main():
    if len(sys.argv) < 2:
        print("Usage: python run_single_test.py <test_id>")
        print(f"Available tests: {', '.join([t['id'] for t in TEST_CASES])}")
        sys.exit(1)
    
    test_id = sys.argv[1]
    
    # Find test case
    test_case = None
    for tc in TEST_CASES:
        if tc['id'] == test_id:
            test_case = tc
            break
    
    if not test_case:
        print(f"Error: Test {test_id} not found")
        sys.exit(1)
    
    # Load checklist
    checklist = load_checklist()
    
    # Check if already completed
    for test in checklist['tests']:
        if test['test_id'] == test_id:
            print(f"Test {test_id} already completed:")
            print(f"Output: {test['output']}")
            sys.exit(0)
    
    # Run test
    print(f"Running test: {test_id}")
    print(f"Category: {test_case['category']}")
    print(f"Prompt: {test_case['user_prompt']}")
    print()
    
    full_prompt = f"{test_case['system_prompt']}\n\n{test_case['user_prompt']}"
    output, error = run_cli_test(test_id, full_prompt)
    
    if error:
        print(f"Error: {error}")
        result = {
            "test_id": test_id,
            "category": test_case['category'],
            "system_prompt": test_case['system_prompt'],
            "user_prompt": test_case['user_prompt'],
            "output": None,
            "error": error
        }
    else:
        print(f"Output: {output}")
        result = {
            "test_id": test_id,
            "category": test_case['category'],
            "system_prompt": test_case['system_prompt'],
            "user_prompt": test_case['user_prompt'],
            "output": output
        }
    
    # Update checklist
    checklist['tests'].append(result)
    checklist['completed'] = len(checklist['tests'])
    
    save_checklist(checklist)
    
    print()
    print(f"Checklist updated: {checklist['completed']}/{checklist['total_tests']} tests completed")

if __name__ == "__main__":
    main()

