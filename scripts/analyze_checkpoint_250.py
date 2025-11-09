#!/usr/bin/env python3
"""
Analyze checkpoint-250 results to assess impact of dataset corrections
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
        'all people', 'no people', 'none', 'person names', 'are listed', 'as follows'
    ])
    
    # Check for SQL (wrong language)
    has_sql = any(pattern in text_upper for pattern in ['SELECT', 'FROM', 'WHERE', 'SPARQL']) and not starts_with_cypher
    
    return starts_with_cypher and not has_reasoning and not has_sql

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
    
    return True

def main():
    results_file = Path("checkpoint_comparison_results.json")
    
    if not results_file.exists():
        print(f"ERROR: Results file not found: {results_file}")
        return
    
    with open(results_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    checkpoint = data['checkpoints_tested'][0] if data['checkpoints_tested'] else None
    results = data['results']
    
    print("="*80)
    print(f"ANÁLISE DO CHECKPOINT-{checkpoint} - DATASET CORRIGIDO")
    print("="*80)
    print(f"\nTotal de testes: {len(results)}\n")
    
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
            has_sql_count += 1
            continue
        
        # Check if Cypher-only
        if is_cypher_only(output):
            cypher_only_count += 1
            if is_valid_cypher(output):
                valid_cypher_count += 1
        else:
            has_explanations_count += 1
    
    print("="*80)
    print("ESTATÍSTICAS DETALHADAS")
    print("="*80)
    print(f"\nTotal de testes: {len(results)}")
    print(f"\nCypher-only (sem explicações): {cypher_only_count} ({cypher_only_count/len(results)*100:.1f}%)")
    print(f"Cypher válido: {valid_cypher_count} ({valid_cypher_count/len(results)*100:.1f}%)")
    print(f"Com explicações/texto: {has_explanations_count} ({has_explanations_count/len(results)*100:.1f}%)")
    print(f"SQL (linguagem errada): {has_sql_count} ({has_sql_count/len(results)*100:.1f}%)")
    print(f"Tags de reasoning: {has_reasoning_tags_count} ({has_reasoning_tags_count/len(results)*100:.1f}%)")
    print(f"Vazios/inválidos: {empty_or_invalid_count} ({empty_or_invalid_count/len(results)*100:.1f}%)")
    
    # Exemplos
    print("\n" + "="*80)
    print("EXEMPLOS DE CYPHER VÁLIDO:")
    print("="*80)
    
    valid_examples = []
    for result in results:
        output = result['checkpoint_outputs'].get(str(checkpoint), '')
        if is_valid_cypher(output):
            valid_examples.append((result['test_id'], output[:150]))
    
    for i, (test_id, example) in enumerate(valid_examples[:5], 1):
        print(f"\n{i}. Teste {test_id}:")
        print(f"   {example}...")
    
    print("\n" + "="*80)
    print("EXEMPLOS COM PROBLEMAS:")
    print("="*80)
    
    # SQL examples
    sql_examples = []
    for result in results:
        output = result['checkpoint_outputs'].get(str(checkpoint), '')
        if any(sql_word in output.upper() for sql_word in ['SELECT', 'FROM']) and not output.upper().startswith('MATCH'):
            sql_examples.append((result['test_id'], output[:150]))
    
    if sql_examples:
        print("\nSQL (linguagem errada):")
        for i, (test_id, example) in enumerate(sql_examples[:3], 1):
            print(f"  {i}. Teste {test_id}: {example}...")
    
    # Reasoning examples
    reasoning_examples = []
    for result in results:
        output = result['checkpoint_outputs'].get(str(checkpoint), '')
        if '<think>' in output.lower() or '<think>' in output.lower():
            reasoning_examples.append((result['test_id'], output[:200]))
    
    if reasoning_examples:
        print("\nTags de reasoning:")
        for i, (test_id, example) in enumerate(reasoning_examples[:2], 1):
            print(f"  {i}. Teste {test_id}: {example}...")
    
    # Avaliação final
    print("\n" + "="*80)
    print("AVALIAÇÃO FINAL")
    print("="*80)
    
    cypher_only_rate = cypher_only_count / len(results)
    valid_cypher_rate = valid_cypher_count / len(results)
    
    print(f"\nTaxa de Cypher-only: {cypher_only_rate*100:.1f}%")
    print(f"Taxa de Cypher válido: {valid_cypher_rate*100:.1f}%")
    
    if valid_cypher_rate >= 0.7:
        print("\n[✓] EXCELENTE - Checkpoint está gerando Cypher válido consistentemente")
        print("   - 70%+ de Cypher válido indica que o dataset corrigido está funcionando")
        print("   - Continue o treinamento para melhorar ainda mais")
    elif valid_cypher_rate >= 0.5:
        print("\n[~] BOM - Checkpoint está melhorando")
        print("   - 50-70% de Cypher válido mostra progresso")
        print("   - Continue o treinamento - modelo está aprendendo")
    elif valid_cypher_rate >= 0.3:
        print("\n[!] REGULAR - Checkpoint precisa de mais treinamento")
        print("   - 30-50% de Cypher válido indica que precisa mais steps")
        print("   - Verifique se o dataset foi realmente regenerado")
    else:
        print("\n[X] PROBLEMA - Checkpoint não está gerando Cypher adequadamente")
        print("   - Menos de 30% de Cypher válido")
        print("   - Verifique se o dataset foi regenerado corretamente")
        print("   - Pode precisar ajustar parâmetros de treinamento")
    
    if has_sql_count > 0:
        print(f"\n[!] ATENÇÃO: {has_sql_count} testes geraram SQL em vez de Cypher")
        print("   - Isso indica que ainda há exemplos SQL no dataset ou modelo não aprendeu")
    
    if has_reasoning_tags_count > 0:
        print(f"\n[!] ATENÇÃO: {has_reasoning_tags_count} testes têm tags de reasoning")
        print("   - Isso indica que o modelo ainda está gerando explicações")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    main()

