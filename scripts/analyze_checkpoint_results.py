#!/usr/bin/env python3
"""
Analyze checkpoint comparison results to determine if training is progressing
and if dataset changes are taking effect
"""

import json
import re
from pathlib import Path

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
        'this is', 'example:', 'answer:', 'result:', 'query:', 'explanation'
    ])
    
    # Check for SQL (wrong language)
    has_sql = any(pattern in text_upper for pattern in ['SELECT', 'FROM', 'WHERE', 'SPARQL'])
    
    # Check if it's mostly Cypher syntax
    cypher_keywords = ['MATCH', 'WHERE', 'RETURN', 'WITH', 'ORDER BY', 'LIMIT', 'CREATE', 'MERGE']
    cypher_keyword_count = sum(1 for keyword in cypher_keywords if keyword in text_upper)
    
    # Check for natural language explanations
    explanation_words = ['the', 'is', 'are', 'can', 'would', 'should', 'might', 'maybe']
    explanation_word_count = sum(1 for word in explanation_words if f' {word} ' in f' {text.lower()} ')
    
    # Decision logic
    if starts_with_cypher and not has_reasoning and not has_sql:
        # Check if it's mostly Cypher (more keywords than explanation words)
        if cypher_keyword_count >= 2 and explanation_word_count < 5:
            return True
    
    # If it has SQL, it's wrong
    if has_sql:
        return False
    
    # If it has reasoning blocks, it's not Cypher-only
    if has_reasoning:
        return False
    
    return False

def extract_cypher(text: str) -> str:
    """Extract Cypher query from response"""
    # Remove reasoning blocks
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Try to find Cypher query
    cypher_pattern = re.compile(r'(?i)(MATCH|CREATE|MERGE|RETURN|WITH|UNWIND|CALL).*?$', re.DOTALL)
    match = cypher_pattern.search(text)
    if match:
        return match.group(0).strip()
    
    return text.strip()

def analyze_results():
    """Analyze checkpoint comparison results"""
    results_file = Path("checkpoint_comparison_results.json")
    
    if not results_file.exists():
        print(f"ERROR: Results file not found: {results_file}")
        return
    
    with open(results_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    checkpoints = data['checkpoints_tested']
    results = data['results']
    
    print("="*80)
    print("CHECKPOINT ANALYSIS - CYPHER-ONLY RESPONSE EVALUATION")
    print("="*80)
    print(f"\nCheckpoints tested: {checkpoints}")
    print(f"Total tests: {len(results)}\n")
    
    # Analyze each checkpoint
    checkpoint_stats = {}
    
    for checkpoint in checkpoints:
        cypher_only_count = 0
        has_explanations_count = 0
        has_sql_count = 0
        empty_count = 0
        valid_cypher_count = 0
        
        for result in results:
            output = result['checkpoint_outputs'].get(str(checkpoint), '')
            
            if not output or output.strip() == '' or output.lower() == 'none':
                empty_count += 1
                continue
            
            # Check for SQL
            if any(sql_word in output.upper() for sql_word in ['SELECT', 'FROM', 'WHERE', 'SPARQL']):
                has_sql_count += 1
                continue
            
            # Check if Cypher-only
            if is_cypher_only(output):
                cypher_only_count += 1
                # Check if valid Cypher
                cypher = extract_cypher(output)
                if cypher.startswith(('MATCH', 'CREATE', 'MERGE', 'RETURN', 'WITH', 'CALL')):
                    valid_cypher_count += 1
            else:
                has_explanations_count += 1
        
        checkpoint_stats[checkpoint] = {
            'cypher_only': cypher_only_count,
            'has_explanations': has_explanations_count,
            'has_sql': has_sql_count,
            'empty': empty_count,
            'valid_cypher': valid_cypher_count,
            'total': len(results)
        }
    
    # Print analysis
    print("\n" + "="*80)
    print("DETAILED STATISTICS BY CHECKPOINT")
    print("="*80)
    
    for checkpoint in sorted(checkpoints):
        stats = checkpoint_stats[checkpoint]
        print(f"\nCHECKPOINT-{checkpoint}:")
        print(f"  Total tests: {stats['total']}")
        print(f"  Cypher-only responses: {stats['cypher_only']} ({stats['cypher_only']/stats['total']*100:.1f}%)")
        print(f"  Valid Cypher queries: {stats['valid_cypher']} ({stats['valid_cypher']/stats['total']*100:.1f}%)")
        print(f"  Responses with explanations: {stats['has_explanations']} ({stats['has_explanations']/stats['total']*100:.1f}%)")
        print(f"  SQL/SPARQL (wrong language): {stats['has_sql']} ({stats['has_sql']/stats['total']*100:.1f}%)")
        print(f"  Empty/None responses: {stats['empty']} ({stats['empty']/stats['total']*100:.1f}%)")
    
    # Compare checkpoints
    print("\n" + "="*80)
    print("COMPARISON BETWEEN CHECKPOINTS")
    print("="*80)
    
    if len(checkpoints) >= 2:
        prev_checkpoint = checkpoints[0]
        for curr_checkpoint in checkpoints[1:]:
            prev_stats = checkpoint_stats[prev_checkpoint]
            curr_stats = checkpoint_stats[curr_checkpoint]
            
            print(f"\nCHECKPOINT-{prev_checkpoint} -> CHECKPOINT-{curr_checkpoint}:")
            
            cypher_improvement = curr_stats['cypher_only'] - prev_stats['cypher_only']
            valid_improvement = curr_stats['valid_cypher'] - prev_stats['valid_cypher']
            explanation_change = curr_stats['has_explanations'] - prev_stats['has_explanations']
            
            print(f"  Cypher-only: {prev_stats['cypher_only']} -> {curr_stats['cypher_only']} ({cypher_improvement:+d})")
            print(f"  Valid Cypher: {prev_stats['valid_cypher']} -> {curr_stats['valid_cypher']} ({valid_improvement:+d})")
            print(f"  Explanations: {prev_stats['has_explanations']} -> {curr_stats['has_explanations']} ({explanation_change:+d})")
            
            if cypher_improvement > 0:
                print(f"  [IMPROVING] More Cypher-only responses")
            elif cypher_improvement < 0:
                print(f"  [REGRESSING] Fewer Cypher-only responses")
            else:
                print(f"  [STABLE] Same number of Cypher-only responses")
            
            prev_checkpoint = curr_checkpoint
    
    # Recommendations
    print("\n" + "="*80)
    print("RECOMMENDATIONS")
    print("="*80)
    
    best_checkpoint = max(checkpoints, key=lambda c: checkpoint_stats[c]['cypher_only'])
    best_stats = checkpoint_stats[best_checkpoint]
    
    print(f"\nBest checkpoint: CHECKPOINT-{best_checkpoint}")
    print(f"  Cypher-only rate: {best_stats['cypher_only']/best_stats['total']*100:.1f}%")
    print(f"  Valid Cypher rate: {best_stats['valid_cypher']/best_stats['total']*100:.1f}%")
    
    if best_stats['cypher_only'] / best_stats['total'] >= 0.8:
        print("\n[RECOMMENDATION] CHECKPOINT IS READY")
        print("  - 80%+ Cypher-only responses indicates good training progress")
        print("  - Continue training to improve further")
    elif best_stats['cypher_only'] / best_stats['total'] >= 0.5:
        print("\n[RECOMMENDATION] TRAINING IS PROGRESSING")
        print("  - 50-80% Cypher-only responses shows improvement")
        print("  - Continue training - model is learning")
    else:
        print("\n[RECOMMENDATION] DATASET ISSUE LIKELY")
        print("  - Less than 50% Cypher-only responses")
        print("  - Check if dataset was regenerated with query-only format")
        print("  - Verify preprocessing is enforcing Cypher-only outputs")
        print("  - May need to regenerate dataset and restart training")
    
    # Check if explanations are decreasing
    if len(checkpoints) >= 2:
        first_explanations = checkpoint_stats[checkpoints[0]]['has_explanations']
        last_explanations = checkpoint_stats[checkpoints[-1]]['has_explanations']
        
        if last_explanations < first_explanations:
            print("\n[POSITIVE SIGN] Explanations are decreasing between checkpoints")
            print("  - Training is working, continue training")
        elif last_explanations > first_explanations:
            print("\n[WARNING] Explanations are increasing between checkpoints")
            print("  - May need to check dataset or training parameters")
        else:
            print("\n[STABLE] Explanation count is stable")
            print("  - May need more training or dataset adjustment")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    analyze_results()

