"""
Analyze test results and generate validation report

This script reads the test results JSON and formats them for LLM analysis.
The LLM will manually validate each query.
"""

import json
import sys
import re
from pathlib import Path

def extract_cypher_from_output(output: str) -> str:
    """Extract Cypher query from output, removing reasoning blocks"""
    # Remove <think> blocks
    output = re.sub(r'<think>.*?</think>', '', output, flags=re.DOTALL | re.IGNORECASE)
    
    # Find Cypher query (starts with MATCH, CREATE, etc.)
    cypher_patterns = [
        r'(MATCH.*?)(?:\n\n|$)',
        r'(CREATE.*?)(?:\n\n|$)',
        r'(MERGE.*?)(?:\n\n|$)',
        r'(RETURN.*?)(?:\n\n|$)',
        r'(WITH.*?)(?:\n\n|$)',
        r'(SELECT.*?)(?:\n\n|$)',  # SQL fallback
    ]
    
    for pattern in cypher_patterns:
        match = re.search(pattern, output, re.DOTALL | re.IGNORECASE)
        if match:
            cypher = match.group(1).strip()
            # Clean up escape sequences
            cypher = cypher.replace('\\n', '\n')
            return cypher
    
    # If no pattern found, return cleaned output
    cleaned = output.replace('\\n', '\n').strip()
    # Remove reasoning text at start
    cleaned = re.sub(r'^(Okay|Let me|I need|Wait|Hmm|So|First|The user|Looking at).*?\n', '', cleaned, flags=re.MULTILINE | re.IGNORECASE)
    return cleaned[:500]  # Limit length

def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_test_results.py <results_json_file>")
        sys.exit(1)
    
    results_file = Path(sys.argv[1])
    if not results_file.exists():
        print(f"Error: File not found: {results_file}")
        sys.exit(1)
    
    with open(results_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    version = data.get('version', 'unknown')
    results = data.get('results', [])
    
    print("=" * 80)
    print(f"TEST RESULTS ANALYSIS - EXPERT NEO4J v{version}")
    print("=" * 80)
    print(f"Total tests: {len(results)}")
    print()
    
    # Group by category
    by_category = {}
    for result in results:
        category = result['category']
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(result)
    
    # Analyze each category
    print("ANALYSIS BY CATEGORY")
    print("=" * 80)
    print()
    
    for category in sorted(by_category.keys()):
        tests = by_category[category]
        print(f"\n{'=' * 80}")
        print(f"CATEGORY: {category.upper()} ({len(tests)} tests)")
        print(f"{'=' * 80}\n")
        
        for test in tests:
            test_id = test['test_id']
            user_prompt = test['user_prompt']
            output = test['output']
            cypher = extract_cypher_from_output(output)
            
            print(f"Test: {test_id}")
            print(f"Prompt: {user_prompt}")
            print(f"Generated Query:")
            print("-" * 80)
            print(cypher)
            print("-" * 80)
            print()
    
    # Save formatted results for LLM analysis
    output_file = results_file.parent / f"{results_file.stem}_formatted.json"
    
    formatted_results = {
        'version': version,
        'total_tests': len(results),
        'by_category': {}
    }
    
    for category, tests in by_category.items():
        formatted_results['by_category'][category] = []
        for test in tests:
            formatted_results['by_category'][category].append({
                'test_id': test['test_id'],
                'user_prompt': test['user_prompt'],
                'system_prompt': test['system_prompt'],
                'raw_output': test['output'],
                'extracted_cypher': extract_cypher_from_output(test['output'])
            })
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(formatted_results, f, indent=2, ensure_ascii=False)
    
    print(f"\nFormatted results saved to: {output_file}")
    print("=" * 80)

if __name__ == "__main__":
    main()

