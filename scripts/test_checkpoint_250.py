#!/usr/bin/env python3
"""
Test checkpoint-250 to verify if it's generating Cypher-only responses
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import re

BASE_MODEL_PATH = "F:/Node/hivellm/expert/models/Qwen3-0.6B"
CHECKPOINT_PATH = "weights/qwen3-06b/checkpoint-250"

def extract_cypher(text: str) -> str:
    """Extract Cypher query from response"""
    # Remove assistant tags
    text = text.replace("<|im_start|>assistant", "").replace("<|im_end|>", "").strip()
    
    # Try to find Cypher query (starts with MATCH, CREATE, RETURN, etc.)
    cypher_pattern = re.compile(r"(?i)(MATCH|CREATE|MERGE|RETURN|WITH|UNWIND|CALL|CREATE|DELETE|SET|REMOVE|FOREACH).*", re.DOTALL)
    match = cypher_pattern.search(text)
    if match:
        return match.group(0).strip()
    return text.strip()

def test_query(system_prompt: str, user_prompt: str, model, tokenizer, device):
    """Test a single query"""
    prompt = f"<|im_start|>system\n{system_prompt}<|im_end|>\n<|im_start|>user\n{user_prompt}<|im_end|>\n<|im_start|>assistant\n"
    
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=200,
            temperature=0.6,
            top_p=0.95,
            top_k=20,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
    
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=False)
    
    # Extract assistant response
    if "<|im_start|>assistant" in generated_text:
        response = generated_text.split("<|im_start|>assistant")[-1]
        response = response.replace("<|im_end|>", "").strip()
    else:
        response = generated_text.strip()
    
    return response

def main():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}\n")
    
    # Load base model
    print(f"Loading base model from {BASE_MODEL_PATH}...")
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_PATH, trust_remote_code=True)
    base_model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL_PATH,
        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
        device_map="auto" if device == "cuda" else None,
        trust_remote_code=True
    )
    
    # Load checkpoint
    print(f"Loading checkpoint from {CHECKPOINT_PATH}...")
    model = PeftModel.from_pretrained(base_model, CHECKPOINT_PATH)
    model.eval()
    
    # Test cases
    test_cases = [
        {
            "name": "Basic MATCH",
            "system": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\n  - `age`: INTEGER\nRelationships:\nNone",
            "user": "Find all people"
        },
        {
            "name": "MATCH with WHERE",
            "system": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\n  - `age`: INTEGER\nRelationships:\nNone",
            "user": "Find people older than 30"
        },
        {
            "name": "Relationship traversal",
            "system": "Dialect: cypher\nSchema:\nNode properties:\n- **Movie**\n  - `title`: STRING\n- **Person**\n  - `name`: STRING\nRelationships:\n(:Person)-[:ACTED_IN]->(:Movie)",
            "user": "Find all actors in movies"
        }
    ]
    
    print("\n" + "="*80)
    print("TESTING CHECKPOINT-250 - Cypher-Only Response Analysis")
    print("="*80 + "\n")
    
    cypher_only_count = 0
    has_explanations_count = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n[TEST {i}/{len(test_cases)}] {test['name']}")
        print("-" * 80)
        print(f"User: {test['user']}")
        print("-" * 80)
        
        response = test_query(test['system'], test['user'], model, tokenizer, device)
        cypher = extract_cypher(response)
        
        print(f"\nFull Response:\n{response}")
        print(f"\nExtracted Cypher:\n{cypher}")
        
        # Check if response is Cypher-only
        is_cypher_only = (
            cypher.startswith(('MATCH', 'CREATE', 'MERGE', 'RETURN', 'WITH', 'UNWIND', 'CALL'))
            and len(response) == len(cypher)  # No extra text
        )
        
        has_explanations = (
            any(word in response.lower() for word in ['here', 'this', 'let me', 'i', 'we', 'the', 'answer', 'query', 'result'])
            and not is_cypher_only
        )
        
        if is_cypher_only:
            cypher_only_count += 1
            print("\n[OK] CYPHER-ONLY: Response contains only Cypher query")
        elif has_explanations:
            has_explanations_count += 1
            print("\n[X] HAS EXPLANATIONS: Response contains explanatory text")
        else:
            print("\n[?] UNCLEAR: Response format unclear")
        
        print("="*80)
    
    print(f"\n\nSUMMARY:")
    print(f"  Cypher-only responses: {cypher_only_count}/{len(test_cases)}")
    print(f"  Responses with explanations: {has_explanations_count}/{len(test_cases)}")
    if cypher_only_count == len(test_cases):
        print(f"\n[OK] CHECKPOINT IS GENERATING CYPHER-ONLY")
    else:
        print(f"\n[X] CHECKPOINT STILL GENERATING EXPLANATIONS")

if __name__ == "__main__":
    main()

