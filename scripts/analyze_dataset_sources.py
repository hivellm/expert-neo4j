#!/usr/bin/env python3
"""
Analyze available dataset sources and their distribution of Cypher command types.
This helps identify which sources have more CREATE examples.
"""

import json
import re
from pathlib import Path
from collections import Counter
from typing import Dict, List

def detect_cypher_type(cypher: str) -> str:
    """Detect Cypher command type"""
    if not cypher:
        return "UNKNOWN"
    
    cypher_upper = cypher.upper().strip()
    
    # Prioritize CREATE/MERGE (write operations) even if MATCH appears first
    if re.search(r'\b(CREATE|MERGE)\b', cypher_upper):
        return "CREATE"
    elif cypher_upper.startswith('MATCH'):
        return "MATCH"
    elif cypher_upper.startswith('CALL'):
        return "CALL"
    elif cypher_upper.startswith('DELETE') or cypher_upper.startswith('DETACH'):
        return "DELETE"
    elif cypher_upper.startswith('SET'):
        return "SET"
    elif cypher_upper.startswith('RETURN'):
        return "RETURN"
    elif cypher_upper.startswith('WITH'):
        return "WITH"
    elif cypher_upper.startswith('UNWIND'):
        return "UNWIND"
    else:
        return "OTHER"

def extract_cypher_from_chatml(text: str) -> str:
    """Extract Cypher query from ChatML format"""
    # Remove reasoning blocks first
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    
    # Extract assistant response
    assistant_match = re.search(r'<\|im_start\|>assistant\n(.*?)<\|im_end\|>', text, re.DOTALL)
    if assistant_match:
        content = assistant_match.group(1).strip()
        # Remove reasoning if still present
        content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
        return content.strip()
    
    # Try legacy ChatML format
    assistant_match = re.search(r'<\|assistant\|>\s*\n(.*?)\n<\|end\|>', text, re.DOTALL)
    if assistant_match:
        content = assistant_match.group(1).strip()
        content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
        return content.strip()
    
    return ""

def analyze_source(file_path: Path, source_name: str):
    """Analyze a single source file"""
    print(f"\n{'='*60}")
    print(f"Analyzing: {source_name}")
    print(f"File: {file_path}")
    print(f"{'='*60}")
    
    if not file_path.exists():
        print(f"  [SKIP] File not found")
        return None
    
    examples = []
    types = Counter()
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            
            try:
                example = json.loads(line)
                examples.append(example)
                
                # Extract Cypher
                cypher = ""
                if "text" in example:
                    cypher = extract_cypher_from_chatml(example["text"])
                elif "cypher" in example:
                    cypher = example["cypher"]
                elif "gold_cypher" in example:
                    cypher = example["gold_cypher"]
                
                if cypher:
                    cypher_type = detect_cypher_type(cypher)
                    types[cypher_type] += 1
                    
            except json.JSONDecodeError as e:
                print(f"  [WARN] Invalid JSON on line {line_num}: {e}")
                continue
            except Exception as e:
                print(f"  [WARN] Error processing line {line_num}: {e}")
                continue
    
    total = len(examples)
    if total == 0:
        print(f"  [SKIP] No examples found")
        return None
    
    print(f"\nTotal examples: {total:,}")
    print(f"\nCommand type distribution:")
    for cmd_type in ["MATCH", "CREATE", "CALL", "DELETE", "SET", "RETURN", "WITH", "UNWIND", "OTHER"]:
        count = types.get(cmd_type, 0)
        pct = (count / total * 100) if total > 0 else 0
        print(f"  {cmd_type:10s}: {count:6,} ({pct:5.1f}%)")
    
    create_count = types.get("CREATE", 0)
    match_count = types.get("MATCH", 0)
    create_pct = (create_count / total * 100) if total > 0 else 0
    match_pct = (match_count / total * 100) if total > 0 else 0
    
    print(f"\nKey metrics:")
    print(f"  CREATE: {create_count:,} ({create_pct:.1f}%)")
    print(f"  MATCH:  {match_count:,} ({match_pct:.1f}%)")
    
    return {
        "source": source_name,
        "file": str(file_path),
        "total": total,
        "types": dict(types),
        "create_count": create_count,
        "match_count": match_count,
        "create_pct": create_pct,
        "match_pct": match_pct
    }

def main():
    """Analyze all available dataset sources"""
    base_dir = Path(__file__).parent.parent
    
    sources = [
        ("neo4j_documentation", base_dir / "datasets" / "neo4j_documentation.jsonl"),
        ("train.jsonl (current)", base_dir / "datasets" / "train.jsonl"),
    ]
    
    results = []
    
    for source_name, file_path in sources:
        result = analyze_source(file_path, source_name)
        if result:
            results.append(result)
    
    # Summary
    print(f"\n\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    
    total_examples = sum(r["total"] for r in results)
    total_create = sum(r["create_count"] for r in results)
    total_match = sum(r["match_count"] for r in results)
    
    print(f"\nTotal examples across all sources: {total_examples:,}")
    print(f"Total CREATE: {total_create:,} ({total_create/total_examples*100:.1f}%)")
    print(f"Total MATCH:  {total_match:,} ({total_match/total_examples*100:.1f}%)")
    
    print(f"\nRecommendations:")
    if total_create < 2000:
        print(f"  [WARNING] Need at least 2,000 CREATE examples for 20% of 10k dataset")
        print(f"  [WARNING] Current: {total_create:,} CREATE examples")
        print(f"  [ACTION] Consider:")
        print(f"    1. Adding more CREATE examples from Neo4j documentation")
        print(f"    2. Improving synthetic CREATE generation")
        print(f"    3. Using additional datasets with more CREATE examples")
    
    if total_match / total_examples > 0.70:
        print(f"  [WARNING] MATCH ratio is {total_match/total_examples*100:.1f}% (should be <= 70%)")
        print(f"  [ACTION] Rebalancing is needed to reduce MATCH to 70%")
    
    print(f"\nFor 10k dataset with 20-30% CREATE:")
    target_create_min = 2000
    target_create_max = 3000
    target_match_max = 7000
    
    print(f"  Required CREATE: {target_create_min:,} - {target_create_max:,}")
    print(f"  Available CREATE: {total_create:,}")
    print(f"  Required MATCH:  <= {target_match_max:,}")
    print(f"  Available MATCH: {total_match:,}")
    
    if total_create >= target_create_min:
        print(f"  [OK] Sufficient CREATE examples available")
    else:
        print(f"  [ACTION] Need {target_create_min - total_create:,} more CREATE examples")

if __name__ == "__main__":
    main()

