#!/usr/bin/env python3
"""Check reasoning blocks distribution in regenerated dataset"""

import json
from pathlib import Path

def main():
    dataset_file = Path("datasets/train.jsonl")
    
    print("="*80)
    print("VERIFICACAO DE REASONING BLOCKS NO DATASET")
    print("="*80)
    
    total = 0
    with_reasoning = 0
    direct_cypher = 0
    
    examples_with_reasoning = []
    examples_direct = []
    
    with open(dataset_file, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= 1000:  # Verificar primeiros 1000
                break
            
            total += 1
            try:
                data = json.loads(line)
                text = data.get('text', '')
                
                # Extrair resposta do assistant
                if '<|im_start|>assistant' in text:
                    response = text.split('<|im_start|>assistant')[-1]
                    response = response.split('<|im_end|>')[0].strip()
                else:
                    response = text.strip()
                
                # Verificar se tem reasoning block
                if '<think>' in response or '<think>' in response or '<think>' in response:
                    with_reasoning += 1
                    if len(examples_with_reasoning) < 3:
                        examples_with_reasoning.append(response[:200])
                elif response.startswith(('MATCH', 'CREATE', 'MERGE', 'RETURN', 'WITH', 'UNWIND')):
                    direct_cypher += 1
                    if len(examples_direct) < 3:
                        examples_direct.append(response[:200])
                    
            except Exception as e:
                print(f"Erro na linha {i+1}: {e}")
                continue
    
    print(f"\nTotal analisados: {total}")
    print(f"Com reasoning blocks (<think>): {with_reasoning} ({with_reasoning/total*100:.1f}%)")
    print(f"Cypher direto (sem reasoning): {direct_cypher} ({direct_cypher/total*100:.1f}%)")
    
    print("\n" + "="*80)
    print("EXEMPLOS COM REASONING:")
    print("="*80)
    for i, ex in enumerate(examples_with_reasoning, 1):
        print(f"\n{i}. {ex}...")
    
    print("\n" + "="*80)
    print("EXEMPLOS DIRETOS (SEM REASONING):")
    print("="*80)
    for i, ex in enumerate(examples_direct, 1):
        print(f"\n{i}. {ex}...")
    
    print("\n" + "="*80)
    print("AVALIACAO")
    print("="*80)
    
    reasoning_rate = with_reasoning / total
    
    # Qwen3 training notebook uses 75% reasoning + 25% direct (as per Unsloth notebook)
    if 0.70 <= reasoning_rate <= 0.80:
        print("\n[OK] DISTRIBUICAO CORRETA")
        print(f"   - {reasoning_rate*100:.1f}% com reasoning (esperado: 70-80% conforme notebook Qwen3)")
        print("   - Dataset pronto para treinamento com Qwen3")
    elif reasoning_rate < 0.70:
        print("\n[~] POUCOS EXEMPLOS COM REASONING")
        print(f"   - {reasoning_rate*100:.1f}% com reasoning (esperado: 70-80% conforme notebook Qwen3)")
        print("   - Pode precisar ajustar a porcentagem")
    else:
        print("\n[~] MUITOS EXEMPLOS COM REASONING")
        print(f"   - {reasoning_rate*100:.1f}% com reasoning (esperado: 70-80% conforme notebook Qwen3)")
        print("   - Pode precisar reduzir a porcentagem")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    main()

