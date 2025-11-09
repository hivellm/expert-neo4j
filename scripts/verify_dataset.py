#!/usr/bin/env python3
"""Verify if dataset contains only Cypher direct queries"""

import json
import re
from pathlib import Path

def is_sql_or_sparql(text: str) -> bool:
    """Detect SQL/SPARQL"""
    if not text or not text.strip():
        return False
    
    text_upper = text.upper().strip()
    
    if text_upper.startswith(('SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE TABLE', 
                               'ALTER', 'DROP', 'PREFIX', 'ASK', 'CONSTRUCT', 'DESCRIBE')):
        return True
    
    if any(pattern in text_upper for pattern in ['FROM', 'JOIN', 'GROUP BY', 'HAVING']):
        if not any(kw in text_upper for kw in ['MATCH', 'MERGE', 'RETURN', 'WITH']):
            return True
    
    return False

def main():
    dataset_file = Path("datasets/train.jsonl")
    
    print("="*80)
    print("VERIFICACAO DO DATASET ATUAL")
    print("="*80)
    
    total = 0
    cypher_direct = 0
    has_explanations = 0
    sql_found = 0
    
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
                
                # Verificar SQL
                if is_sql_or_sparql(response):
                    sql_found += 1
                    continue
                
                # Verificar se é Cypher direto
                if response.startswith(('MATCH', 'CREATE', 'MERGE', 'RETURN', 'WITH', 'UNWIND', 'CALL')):
                    # Verificar se tem explicações
                    has_exp = any(word in response.lower() for word in [
                        'okay', 'let me', 'here is', 'note', 'example', 'all people',
                        'are listed', 'as follows', 'the answer', 'the result'
                    ])
                    
                    if has_exp:
                        has_explanations += 1
                    else:
                        cypher_direct += 1
                else:
                    has_explanations += 1
                    
            except Exception as e:
                print(f"Erro na linha {i+1}: {e}")
                continue
    
    print(f"\nTotal analisados: {total}")
    print(f"Cypher direto (sem explicacoes): {cypher_direct} ({cypher_direct/total*100:.1f}%)")
    print(f"Com explicacoes/texto: {has_explanations} ({has_explanations/total*100:.1f}%)")
    print(f"SQL/SPARQL encontrado: {sql_found} ({sql_found/total*100:.1f}%)")
    
    print("\n" + "="*80)
    print("AVALIACAO")
    print("="*80)
    
    cypher_rate = cypher_direct / total
    
    if cypher_rate >= 0.9:
        print("\n[OK] DATASET EXCELENTE")
        print("   - 90%+ de Cypher direto")
        print("   - Dataset esta correto, problema pode ser no treinamento")
    elif cypher_rate >= 0.7:
        print("\n[~] DATASET BOM")
        print("   - 70-90% de Cypher direto")
        print("   - Dataset esta bom, mas pode melhorar")
    else:
        print("\n[X] DATASET PRECISA SER CORRIGIDO")
        print("   - Menos de 70% de Cypher direto")
        print("   - Precisa regenerar o dataset")
    
    if sql_found > 0:
        print(f"\n[!] ATENCAO: {sql_found} exemplos SQL encontrados no dataset")
        print("   - Dataset precisa ser regenerado com filtros SQL")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    main()

