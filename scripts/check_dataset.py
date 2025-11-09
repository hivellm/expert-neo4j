#!/usr/bin/env python3
"""
Check if dataset contains Cypher-only responses
"""

import json
import re
from pathlib import Path

def is_sql_or_sparql(text: str) -> bool:
    """Detect if text is SQL or SPARQL (not Cypher) - same logic as preprocessing"""
    import re
    if not text or not text.strip():
        return False
    
    text_upper = text.upper().strip()
    
    # SQL keywords that are NOT Cypher
    sql_keywords = ['SELECT', 'FROM', 'INSERT INTO', 'UPDATE', 'DELETE FROM', 
                    'CREATE TABLE', 'ALTER TABLE', 'DROP TABLE', 'JOIN', 'INNER JOIN',
                    'LEFT JOIN', 'RIGHT JOIN', 'FULL JOIN', 'GROUP BY', 'HAVING',
                    'UNION ALL', 'EXISTS', 'NOT EXISTS', 'INNER', 'OUTER']
    
    # SPARQL keywords
    sparql_keywords = ['PREFIX', 'SELECT', 'WHERE', 'FILTER', 'OPTIONAL', 
                       'GRAPH', 'UNION', 'ASK', 'CONSTRUCT', 'DESCRIBE']
    
    # Check if starts with SQL/SPARQL keywords (strong indicator)
    if text_upper.startswith(('SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE TABLE', 
                               'ALTER', 'DROP', 'PREFIX', 'ASK', 'CONSTRUCT', 'DESCRIBE')):
        return True
    
    # Check for SQL patterns
    sql_patterns = [
        r'\bFROM\s+\w+',  # FROM table
        r'\bJOIN\s+\w+',  # JOIN table
        r'\bGROUP\s+BY\b',  # GROUP BY
        r'\bHAVING\s+',  # HAVING
        r'\bINSERT\s+INTO\b',  # INSERT INTO
        r'\bCREATE\s+TABLE\b',  # CREATE TABLE
    ]
    
    for pattern in sql_patterns:
        if re.search(pattern, text_upper):
            return True
    
    # Check for SPARQL patterns
    sparql_patterns = [
        r'\bPREFIX\s+\w+:',  # PREFIX prefix:
        r'\{\s*\?',  # { ?variable
        r'\?\w+\s+\?\w+',  # ?var1 ?var2
    ]
    
    for pattern in sparql_patterns:
        if re.search(pattern, text_upper):
            return True
    
    # If it has SQL keywords but no Cypher keywords, it's likely SQL
    has_sql_kw = any(kw in text_upper for kw in sql_keywords)
    has_cypher_kw = any(kw in text_upper for kw in ['MATCH', 'MERGE', 'RETURN', 'WITH', 'UNWIND'])
    
    if has_sql_kw and not has_cypher_kw:
        return True
    
    return False

def is_cypher_only(text: str) -> bool:
    """Check if response contains only Cypher query"""
    if not text or len(text.strip()) == 0:
        return False
    
    text_upper = text.upper().strip()
    
    # Check if starts with Cypher keywords
    starts_with_cypher = text_upper.startswith(('MATCH', 'CREATE', 'MERGE', 'RETURN', 'WITH', 'UNWIND', 'CALL'))
    
    # Check for reasoning/explanation patterns
    has_reasoning = any(pattern in text.lower() for pattern in [
        '<think>', '<think>', 'okay', 'let me', 'i need', 'wait', 'hmm', 
        'so', 'first', 'the user', 'looking at', 'here is', 'note:', 'please note',
        'this is', 'example:', 'answer:', 'result:', 'query:', 'explanation',
        'all people', 'no people', 'none', 'person names'
    ])
    
    # Check for SQL/SPARQL (wrong language) - use proper detection
    has_sql = is_sql_or_sparql(text)
    
    return starts_with_cypher and not has_reasoning and not has_sql

def main():
    dataset_file = Path("datasets/train.jsonl")
    
    if not dataset_file.exists():
        print(f"ERROR: Dataset file not found: {dataset_file}")
        return
    
    print("="*80)
    print("DATASET ANALYSIS - CYPHER-ONLY RESPONSE CHECK")
    print("="*80)
    print(f"\nReading dataset: {dataset_file}")
    
    responses = []
    cypher_only_count = 0
    has_explanations_count = 0
    has_sql_count = 0
    empty_count = 0
    
    sample_size = 1000  # Check first 1000 examples
    
    with open(dataset_file, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= sample_size:
                break
            
            try:
                data = json.loads(line)
                text = data.get('text', '')
                
                # Extract assistant response
                if '<|im_start|>assistant' in text:
                    response = text.split('<|im_start|>assistant')[-1]
                    response = response.split('<|im_end|>')[0].strip()
                else:
                    response = text.strip()
                
                responses.append(response)
                
                if not response or response.lower() == 'none':
                    empty_count += 1
                elif any(sql_word in response.upper() for sql_word in ['SELECT', 'FROM', 'WHERE', 'SPARQL']):
                    has_sql_count += 1
                elif is_cypher_only(response):
                    cypher_only_count += 1
                else:
                    has_explanations_count += 1
                    
            except json.JSONDecodeError as e:
                print(f"ERROR parsing line {i+1}: {e}")
                continue
    
    total = len(responses)
    
    print(f"\nAnalyzed {total} examples from dataset")
    print(f"\nResults:")
    print(f"  Cypher-only responses: {cypher_only_count} ({cypher_only_count/total*100:.1f}%)")
    print(f"  Responses with explanations: {has_explanations_count} ({has_explanations_count/total*100:.1f}%)")
    print(f"  SQL/SPARQL (wrong language): {has_sql_count} ({has_sql_count/total*100:.1f}%)")
    print(f"  Empty/None responses: {empty_count} ({empty_count/total*100:.1f}%)")
    
    # Show examples
    print("\n" + "="*80)
    print("EXAMPLES OF CYPHER-ONLY RESPONSES:")
    print("="*80)
    
    cypher_only_examples = [r for r in responses if is_cypher_only(r)]
    for i, example in enumerate(cypher_only_examples[:5], 1):
        print(f"\n{i}. {example[:150]}...")
    
    print("\n" + "="*80)
    print("EXAMPLES OF RESPONSES WITH EXPLANATIONS:")
    print("="*80)
    
    explanation_examples = [r for r in responses if not is_cypher_only(r) and r and r.lower() != 'none' and not any(sql_word in r.upper() for sql_word in ['SELECT', 'FROM', 'WHERE', 'SPARQL'])]
    for i, example in enumerate(explanation_examples[:5], 1):
        print(f"\n{i}. {example[:150]}...")
    
    # Recommendation
    print("\n" + "="*80)
    print("RECOMMENDATION")
    print("="*80)
    
    cypher_only_rate = cypher_only_count / total
    
    if cypher_only_rate >= 0.9:
        print("\n[OK] DATASET IS GOOD")
        print("  - 90%+ Cypher-only responses")
        print("  - Dataset is ready for training")
        print("  - If checkpoints are bad, training may need more steps or different parameters")
    elif cypher_only_rate >= 0.7:
        print("\n[WARNING] DATASET NEEDS IMPROVEMENT")
        print("  - 70-90% Cypher-only responses")
        print("  - Some examples still have explanations")
        print("  - Consider regenerating dataset with stricter sanitization")
    else:
        print("\n[CRITICAL] DATASET NEEDS REGENERATION")
        print("  - Less than 70% Cypher-only responses")
        print("  - Dataset was not properly sanitized")
        print("  - MUST regenerate dataset before continuing training")
        print("  - Check preprocessing script for issues")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    main()

