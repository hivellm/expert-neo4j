#!/usr/bin/env python3
"""
Analyze final checkpoints (1750, 2000, 2250) to assess training progress
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
        'this is', 'example:', 'answer:', 'result:', 'query:', 'explanation',
        'all people', 'no people', 'none', 'person names', 'are listed', 'as follows',
        'with their', 'with properties', 'the count', 'the total', 'the sum'
    ])
    
    # Check for SQL (wrong language) - but allow if it's part of Cypher
    has_sql = any(pattern in text_upper for pattern in ['SELECT', 'FROM']) and not starts_with_cypher
    
    # Check for Python code blocks
    has_python = '```python' in text.lower() or '```' in text and 'SELECT' in text_upper
    
    return starts_with_cypher and not has_reasoning and not has_sql and not has_python

def is_valid_cypher(text: str) -> bool:
    """Check if Cypher query is syntactically valid"""
    if not is_cypher_only(text):
        return False
    
    text_upper = text.upper()
    
    # Basic syntax checks
    # Must have MATCH or CREATE or MERGE
    if not any(kw in text_upper for kw in ['MATCH', 'CREATE', 'MERGE']):
        return False
    
    # Must have RETURN (unless it's CREATE/MERGE without RETURN)
    if 'MATCH' in text_upper and 'RETURN' not in text_upper:
        return False
    
    # Check for common syntax errors
    # Invalid: {age: (p.age > 30)} - can't use expressions in {}
    if re.search(r'\{[^}]*\([^)]*\)[^}]*\}', text):
        return False
    
    # Invalid: SELECT instead of MATCH
    if text_upper.startswith('SELECT'):
        return False
    
    # Invalid: Multiple WHERE clauses
    if text_upper.count('WHERE') > 1:
        return False
    
    # Invalid: WHERE after RETURN
    if 'RETURN' in text_upper and 'WHERE' in text_upper:
        return_pos = text_upper.find('RETURN')
        where_pos = text_upper.find('WHERE')
        if where_pos > return_pos:
            return False
    
    return True

def main():
    results_file = Path("checkpoint_comparison_results.json")
    
    if not results_file.exists():
        print(f"ERROR: Results file not found: {results_file}")
        return
    
    with open(results_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    checkpoints = data['checkpoints_tested']
    results = data['results']
    
    print("="*80)
    print("ANÁLISE DOS CHECKPOINTS FINAIS - DATASET CORRIGIDO")
    print("="*80)
    print(f"\nCheckpoints testados: {checkpoints}")
    print(f"Total de testes: {len(results)}\n")
    
    checkpoint_stats = {}
    
    for checkpoint in checkpoints:
        cypher_only_count = 0
        valid_cypher_count = 0
        has_explanations_count = 0
        has_sql_count = 0
        has_reasoning_tags_count = 0
        empty_or_invalid_count = 0
        
        for result in results:
            output = result['checkpoint_outputs'].get(str(checkpoint), '')
            
            if not output or output.strip() == '' or output.lower() in ['none', '0', '[]']:
                empty_or_invalid_count += 1
                continue
            
            # Check for reasoning tags
            if '<think>' in output.lower() or '<think>' in output.lower():
                has_reasoning_tags_count += 1
            
            # Check for SQL
            if any(sql_word in output.upper() for sql_word in ['SELECT', 'FROM']) and not output.upper().startswith('MATCH'):
                if '```python' in output.lower() or '```' in output:
                    has_sql_count += 1
                elif not output.upper().startswith('MATCH'):
                    has_sql_count += 1
                continue
            
            # Check if Cypher-only
            if is_cypher_only(output):
                cypher_only_count += 1
                if is_valid_cypher(output):
                    valid_cypher_count += 1
            else:
                has_explanations_count += 1
        
        checkpoint_stats[checkpoint] = {
            'cypher_only': cypher_only_count,
            'valid_cypher': valid_cypher_count,
            'has_explanations': has_explanations_count,
            'has_sql': has_sql_count,
            'has_reasoning_tags': has_reasoning_tags_count,
            'empty_or_invalid': empty_or_invalid_count,
            'total': len(results)
        }
    
    # Print statistics for each checkpoint
    print("="*80)
    print("ESTATÍSTICAS POR CHECKPOINT")
    print("="*80)
    
    for checkpoint in sorted(checkpoints):
        stats = checkpoint_stats[checkpoint]
        print(f"\nCHECKPOINT-{checkpoint}:")
        print(f"  Cypher-only: {stats['cypher_only']}/{stats['total']} ({stats['cypher_only']/stats['total']*100:.1f}%)")
        print(f"  Cypher válido: {stats['valid_cypher']}/{stats['total']} ({stats['valid_cypher']/stats['total']*100:.1f}%)")
        print(f"  Com explicações: {stats['has_explanations']}/{stats['total']} ({stats['has_explanations']/stats['total']*100:.1f}%)")
        print(f"  SQL (errado): {stats['has_sql']}/{stats['total']} ({stats['has_sql']/stats['total']*100:.1f}%)")
        print(f"  Tags reasoning: {stats['has_reasoning_tags']}/{stats['total']} ({stats['has_reasoning_tags']/stats['total']*100:.1f}%)")
        print(f"  Vazios/inválidos: {stats['empty_or_invalid']}/{stats['total']} ({stats['empty_or_invalid']/stats['total']*100:.1f}%)")
    
    # Compare evolution
    print("\n" + "="*80)
    print("EVOLUÇÃO ENTRE CHECKPOINTS")
    print("="*80)
    
    if len(checkpoints) >= 2:
        prev_checkpoint = checkpoints[0]
        for curr_checkpoint in checkpoints[1:]:
            prev_stats = checkpoint_stats[prev_checkpoint]
            curr_stats = checkpoint_stats[curr_checkpoint]
            
            print(f"\nCHECKPOINT-{prev_checkpoint} -> CHECKPOINT-{curr_checkpoint}:")
            
            cypher_change = curr_stats['cypher_only'] - prev_stats['cypher_only']
            valid_change = curr_stats['valid_cypher'] - prev_stats['valid_cypher']
            sql_change = curr_stats['has_sql'] - prev_stats['has_sql']
            reasoning_change = curr_stats['has_reasoning_tags'] - prev_stats['has_reasoning_tags']
            
            print(f"  Cypher-only: {prev_stats['cypher_only']} -> {curr_stats['cypher_only']} ({cypher_change:+d})")
            print(f"  Cypher válido: {prev_stats['valid_cypher']} -> {curr_stats['valid_cypher']} ({valid_change:+d})")
            print(f"  SQL: {prev_stats['has_sql']} -> {curr_stats['has_sql']} ({sql_change:+d})")
            print(f"  Reasoning tags: {prev_stats['has_reasoning_tags']} -> {curr_stats['has_reasoning_tags']} ({reasoning_change:+d})")
            
            if valid_change > 0:
                print(f"  [OK] MELHORANDO - Mais Cypher valido")
            elif valid_change < 0:
                print(f"  [X] REGREDINDO - Menos Cypher valido")
            else:
                print(f"  [=] ESTAVEL - Mesma quantidade de Cypher valido")
            
            prev_checkpoint = curr_checkpoint
    
    # Best checkpoint
    best_checkpoint = max(checkpoints, key=lambda c: checkpoint_stats[c]['valid_cypher'])
    best_stats = checkpoint_stats[best_checkpoint]
    
    print("\n" + "="*80)
    print("AVALIAÇÃO FINAL")
    print("="*80)
    
    print(f"\nMelhor checkpoint: CHECKPOINT-{best_checkpoint}")
    print(f"  Cypher válido: {best_stats['valid_cypher']}/{best_stats['total']} ({best_stats['valid_cypher']/best_stats['total']*100:.1f}%)")
    print(f"  Cypher-only: {best_stats['cypher_only']}/{best_stats['total']} ({best_stats['cypher_only']/best_stats['total']*100:.1f}%)")
    
    valid_rate = best_stats['valid_cypher'] / best_stats['total']
    
    if valid_rate >= 0.7:
        print("\n[OK] EXCELENTE - Checkpoint esta gerando Cypher valido consistentemente")
        print("   - 70%+ de Cypher valido indica que o dataset corrigido esta funcionando")
        print(f"   - CHECKPOINT-{best_checkpoint} deve ser usado para packaging")
    elif valid_rate >= 0.5:
        print("\n[~] BOM - Checkpoint esta melhorando")
        print("   - 50-70% de Cypher valido mostra progresso significativo")
        print(f"   - CHECKPOINT-{best_checkpoint} pode ser usado, mas precisa mais treinamento")
    elif valid_rate >= 0.3:
        print("\n[!] REGULAR - Checkpoint precisa de mais treinamento")
        print("   - 30-50% de Cypher valido indica que precisa mais steps")
        print("   - Verifique se o dataset foi realmente regenerado")
    else:
        print("\n[X] PROBLEMA - Checkpoint nao esta gerando Cypher adequadamente")
        print("   - Menos de 30% de Cypher valido")
        print("   - Verifique se o dataset foi regenerado corretamente")
        print("   - Pode precisar ajustar parametros de treinamento")
    
    if best_stats['has_sql'] > 0:
        print(f"\n[!] ATENÇÃO: {best_stats['has_sql']} testes ainda geram SQL em vez de Cypher")
    
    if best_stats['has_reasoning_tags'] > 0:
        print(f"[!] ATENÇÃO: {best_stats['has_reasoning_tags']} testes têm tags de reasoning")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    main()

