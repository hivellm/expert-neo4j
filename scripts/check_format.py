#!/usr/bin/env python3
"""Check the format of the generated dataset"""

import json

with open('datasets/train.jsonl', 'r', encoding='utf-8') as f:
    lines = [json.loads(line) for line in f.readlines()[:5]]

print('Checking format in 5 examples:')
print('='*60)

qwen3_count = 0
old_count = 0

for i, ex in enumerate(lines, 1):
    text = ex['text']
    has_qwen3 = '<|im_start|>' in text
    has_old = '<|system|>' in text and '<|im_start|>' not in text
    
    if has_qwen3:
        qwen3_count += 1
    if has_old:
        old_count += 1
    
    print(f'Example {i}: Qwen3={has_qwen3}, Old ChatML={has_old}')
    print(f'  Preview: {text[:100]}...')
    print()

print('='*60)
print(f'Total checked: {len(lines)}')
print(f'Qwen3 format: {qwen3_count}')
print(f'Old ChatML format: {old_count}')
print('='*60)

