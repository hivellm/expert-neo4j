#!/usr/bin/env python3
"""Check for SQL/SPARQL examples in dataset"""

import json
import re
from pathlib import Path

def is_sql_or_sparql(text: str) -> bool:
    """Detect if text is SQL or SPARQL (not Cypher)"""
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

def main():
    dataset_file = Path("datasets/train.jsonl")
    
    print("="*80)
    print("CHECKING FOR SQL/SPARQL IN DATASET")
    print("="*80)
    
    sql_examples = []
    cypher_examples = []
    
    with open(dataset_file, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= 1000:  # Check first 1000
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
                
                if is_sql_or_sparql(response):
                    sql_examples.append((i+1, response[:200]))
                else:
                    cypher_examples.append((i+1, response[:200]))
                    
            except Exception as e:
                print(f"Error on line {i+1}: {e}")
                continue
    
    print(f"\nTotal checked: {len(sql_examples) + len(cypher_examples)}")
    print(f"SQL/SPARQL found: {len(sql_examples)} ({len(sql_examples)/(len(sql_examples)+len(cypher_examples))*100:.1f}%)")
    print(f"Cypher found: {len(cypher_examples)} ({len(cypher_examples)/(len(sql_examples)+len(cypher_examples))*100:.1f}%)")
    
    print("\n" + "="*80)
    print("SQL/SPARQL EXAMPLES:")
    print("="*80)
    for idx, (line_num, example) in enumerate(sql_examples[:10], 1):
        print(f"\n{idx}. Line {line_num}:")
        print(f"   {example}...")
    
    print("\n" + "="*80)
    print("CYPHER EXAMPLES:")
    print("="*80)
    for idx, (line_num, example) in enumerate(cypher_examples[:5], 1):
        print(f"\n{idx}. Line {line_num}:")
        print(f"   {example}...")

if __name__ == "__main__":
    main()

