"""
Qualitative Checkpoint Comparison - Expert Neo4j

This script runs the same prompts on all available checkpoints
and displays results for qualitative analysis.

Run with: F:/Node/hivellm/expert/cli/venv_windows/Scripts/python.exe compare.py
"""

import sys
import os

# Add experts root directory to path to import template
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

# Import functions from template
from compare_checkpoints_template import (
    detect_device, find_checkpoints, load_base_model, load_checkpoints,
    generate_output, print_separator, print_test_header, print_output, main as template_main
)
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import json

# ============================================================================
# EXPERT-NEO4J SPECIFIC CONFIGURATION
# ============================================================================

BASE_MODEL_PATH = "F:/Node/hivellm/expert/models/Qwen3-0.6B"
CHECKPOINT_DIR = "weights/qwen3-06b"

GEN_CONFIG = {
    "max_new_tokens": 200,
    "temperature": 0.6,
    "top_p": 0.95,
    "top_k": 20,
    "min_p": 0.0,
    "do_sample": True,
}

# ============================================================================
# TEST CASES - EXPERT-NEO4J (Cypher Queries)
# ============================================================================

test_cases = [
    # Basic MATCH queries
    {
        "id": "match_001",
        "category": "basic_match",
        "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\n  - `age`: INTEGER\nRelationships:\nNone",
        "user_prompt": "Find all people",
        "expected_type": "cypher"
    },
    {
        "id": "match_002",
        "category": "basic_match",
        "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Movie**\n  - `title`: STRING\n  - `released`: INTEGER\nRelationships:\nNone",
        "user_prompt": "List all movies",
        "expected_type": "cypher"
    },
    # MATCH with WHERE
    {
        "id": "where_001",
        "category": "where_filter",
        "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\n  - `age`: INTEGER\nRelationships:\nNone",
        "user_prompt": "Find people older than 30",
        "expected_type": "cypher"
    },
    {
        "id": "where_002",
        "category": "where_filter",
        "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Product**\n  - `name`: STRING\n  - `price`: FLOAT\nRelationships:\nNone",
        "user_prompt": "Find products with price less than 100",
        "expected_type": "cypher"
    },
    # Relationship traversal
    {
        "id": "rel_001",
        "category": "relationship",
        "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Movie**\n  - `title`: STRING\n- **Person**\n  - `name`: STRING\nRelationships:\n(:Person)-[:ACTED_IN]->(:Movie)",
        "user_prompt": "Find all actors in movies",
        "expected_type": "cypher"
    },
    {
        "id": "rel_002",
        "category": "relationship",
        "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\nRelationships:\n(:Person)-[:KNOWS]->(:Person)",
        "user_prompt": "Find people who know each other",
        "expected_type": "cypher"
    },
    # Aggregations
    {
        "id": "agg_001",
        "category": "aggregation",
        "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **User**\n  - `name`: STRING\nRelationships:\nNone",
        "user_prompt": "Count total users",
        "expected_type": "cypher"
    },
    {
        "id": "agg_002",
        "category": "aggregation",
        "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Order**\n  - `total`: FLOAT\nRelationships:\n(:Customer)-[:PLACED]->(:Order)",
        "user_prompt": "Sum of all order totals",
        "expected_type": "cypher"
    },
    # ORDER BY and LIMIT
    {
        "id": "order_001",
        "category": "ordering",
        "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Product**\n  - `name`: STRING\n  - `price`: FLOAT\nRelationships:\nNone",
        "user_prompt": "Find top 5 most expensive products",
        "expected_type": "cypher"
    },
    {
        "id": "order_002",
        "category": "ordering",
        "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Employee**\n  - `name`: STRING\n  - `salary`: FLOAT\nRelationships:\nNone",
        "user_prompt": "Show the 3 highest paid employees",
        "expected_type": "cypher"
    },
    # Multi-hop relationships
    {
        "id": "multihop_001",
        "category": "multi_hop",
        "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\nRelationships:\n(:Person)-[:KNOWS]->(:Person)\n(:Person)-[:FOLLOWS]->(:Person)",
        "user_prompt": "Find people who know someone who follows another person",
        "expected_type": "cypher"
    },
    # Complex WHERE with multiple conditions
    {
        "id": "complex_001",
        "category": "complex",
        "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\n  - `age`: INTEGER\n  - `city`: STRING\nRelationships:\nNone",
        "user_prompt": "Find people aged between 25 and 40 living in New York",
        "expected_type": "cypher"
    },
    # Pattern matching
    {
        "id": "pattern_001",
        "category": "pattern",
        "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Business**\n  - `name`: STRING\n  - `category`: STRING\nRelationships:\n(:Business)-[:LOCATED_IN]->(:City)",
        "user_prompt": "Find all restaurants in cities",
        "expected_type": "cypher"
    },
    # RETURN with specific properties
    {
        "id": "return_001",
        "category": "return",
        "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\n  - `age`: INTEGER\n  - `email`: STRING\nRelationships:\nNone",
        "user_prompt": "Get names and emails of all people",
        "expected_type": "cypher"
    }
]

# ============================================================================
# MAIN CODE
# ============================================================================

def format_prompt(system_prompt: str, user_prompt: str) -> str:
    """Format prompt using Qwen3 native format"""
    # Qwen3 format: <|im_start|>role\ncontent<|im_end|>
    return (
        f"<|im_start|>system\n{system_prompt}<|im_end|>\n"
        f"<|im_start|>user\n{user_prompt}<|im_end|>\n"
        f"<|im_start|>assistant\n"
    )


def clean_reasoning_text(text: str) -> str:
    """Remove reasoning/thinking blocks and extract only Cypher query"""
    import re
    
    # Remove <think> or <think> blocks
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Try to extract Cypher query (starts with MATCH, CREATE, MERGE, RETURN, WITH, etc.)
    cypher_patterns = [
        r'(MATCH.*?)(?:\n\n|$)',
        r'(CREATE.*?)(?:\n\n|$)',
        r'(MERGE.*?)(?:\n\n|$)',
        r'(RETURN.*?)(?:\n\n|$)',
        r'(WITH.*?)(?:\n\n|$)',
    ]
    
    for pattern in cypher_patterns:
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            cypher = match.group(1).strip()
            # Clean up - remove any remaining reasoning text after the query
            cypher = re.sub(r'\n\n.*', '', cypher, flags=re.DOTALL)
            # Remove any trailing explanation text
            lines = cypher.split('\n')
            cypher_lines = []
            for line in lines:
                line = line.strip()
                # Stop if we hit explanation text (common patterns)
                if any(stop_word in line.lower() for stop_word in ['okay', 'let me', 'i need', 'wait', 'hmm', 'so', 'first']):
                    if cypher_lines:  # Only stop if we already have some Cypher
                        break
                if line and not line.startswith('...'):
                    cypher_lines.append(line)
            if cypher_lines:
                return '\n'.join(cypher_lines)
    
    # If no Cypher pattern found, try to extract text that looks like Cypher
    # (has MATCH, CREATE, etc. keywords)
    if any(keyword in text.upper() for keyword in ['MATCH', 'CREATE', 'MERGE', 'RETURN', 'WITH']):
        # Extract lines that contain Cypher keywords
        lines = text.split('\n')
        cypher_lines = []
        for line in lines:
            line_upper = line.upper().strip()
            if any(keyword in line_upper for keyword in ['MATCH', 'CREATE', 'MERGE', 'RETURN', 'WITH', 'WHERE', 'ORDER BY', 'LIMIT']):
                cypher_lines.append(line.strip())
            elif cypher_lines and (line.strip().startswith('(') or line.strip().startswith('[') or ':' in line):
                # Continue collecting if it looks like part of Cypher pattern
                cypher_lines.append(line.strip())
            elif cypher_lines and not line.strip():
                # Empty line might be end of query
                break
        
        if cypher_lines:
            return '\n'.join(cypher_lines)
    
    # Fallback: return cleaned text (remove common reasoning prefixes)
    cleaned = re.sub(r'^(Okay|Let me|I need|Wait|Hmm|So|First|The user|Looking at).*?\n', '', text, flags=re.MULTILINE | re.IGNORECASE)
    return cleaned.strip()


def generate_cypher_output(model, tokenizer, system_prompt: str, user_prompt: str, gen_config: dict, device: str) -> str:
    """Generate Cypher output from model"""
    prompt = format_prompt(system_prompt, user_prompt)
    inputs = tokenizer([prompt], return_tensors="pt").to(device)
    
    gen_params = {
        **gen_config,
        "pad_token_id": tokenizer.eos_token_id,
        "eos_token_id": tokenizer.eos_token_id
    }
    
    with torch.no_grad():
        outputs = model.generate(**inputs, **gen_params)
        generated_text = tokenizer.decode(
            outputs[0][inputs['input_ids'].shape[1]:],
            skip_special_tokens=False
        )
    
    # Extract assistant response
    if "<|im_start|>assistant" in generated_text:
        cypher = generated_text.split("<|im_start|>assistant")[-1]
        cypher = cypher.replace("<|im_end|>", "").strip()
    else:
        cypher = generated_text.strip()
    
    # Clean up
    cypher = cypher.split("<|im_end|>")[0].strip()
    cypher = cypher.split("<|im_start|>")[0].strip()
    
    # Remove reasoning text and extract only Cypher
    cypher = clean_reasoning_text(cypher)
    
    return cypher


def main():
    """Main function"""
    device = detect_device()
    
    print_separator()
    print("QUALITATIVE CHECKPOINT COMPARISON - EXPERT NEO4J")
    print("This script generates Cypher outputs for analysis")
    print("Does not evaluate quality automatically")
    print_separator()
    
    # Find checkpoints
    checkpoints = find_checkpoints(CHECKPOINT_DIR)
    if not checkpoints:
        print(f"ERROR: No checkpoints found in: {CHECKPOINT_DIR}")
        print(f"Checkpoint directory: {os.path.abspath(CHECKPOINT_DIR)}")
        print("\nNote: If training hasn't started yet, checkpoints will appear after training begins.")
        sys.exit(1)
    
    print(f"\nCheckpoints found: {[c[0] for c in checkpoints]}")
    print(f"Total tests: {len(test_cases)}")
    print(f"Device: {device}")
    
    # Load models
    base_model, tokenizer = load_base_model(BASE_MODEL_PATH, device)
    checkpoint_models = load_checkpoints(BASE_MODEL_PATH, checkpoints, device)
    
    # Run tests
    print(f"\n[3/3] Running {len(test_cases)} tests...")
    print_separator()
    
    results = []
    
    for test_idx, test_case in enumerate(test_cases, 1):
        print_test_header(test_case, test_idx, len(test_cases))
        
        # Generate with base model
        base_output = generate_cypher_output(
            base_model, tokenizer,
            test_case['system_prompt'],
            test_case['user_prompt'],
            GEN_CONFIG,
            device
        )
        print_output("BASE MODEL", base_output)
        
        # Generate with each checkpoint
        checkpoint_outputs = {}
        for step, model in checkpoint_models.items():
            ckp_output = generate_cypher_output(
                model, tokenizer,
                test_case['system_prompt'],
                test_case['user_prompt'],
                GEN_CONFIG,
                device
            )
            checkpoint_outputs[step] = ckp_output
            print_output(f"CHECKPOINT-{step}", ckp_output)
        
        # Store result
        results.append({
            "test_id": test_case.get('id', f'test_{test_idx}'),
            "category": test_case.get('category', 'N/A'),
            "expected_type": test_case.get('expected_type', 'N/A'),
            "system_prompt": test_case['system_prompt'],
            "user_prompt": test_case['user_prompt'],
            "base_output": base_output,
            "checkpoint_outputs": checkpoint_outputs
        })
        
        print_separator()
    
    # Final summary
    print_separator()
    print("\nEXECUTION SUMMARY")
    print_separator()
    print(f"Total tests executed: {len(test_cases)}")
    print(f"Checkpoints tested: {[c[0] for c in checkpoints]}")
    print(f"Base model: {BASE_MODEL_PATH}")
    print(f"\nAll outputs have been displayed above.")
    print("\n" + "="*80)
    print("INSTRUCTIONS FOR ANALYSIS:")
    print("="*80)
    print("Analyze the results above to determine:")
    print("  1. Which checkpoint produces best quality Cypher queries")
    print("  2. Which checkpoint should be used to generate the package")
    print("  3. If training is progressing correctly")
    print("  4. Identify common issues:")
    print("     - Syntax errors (missing RETURN, invalid MATCH patterns)")
    print("     - Missing WHERE clauses when needed")
    print("     - Incorrect relationship traversal")
    print("     - Excessive reasoning text instead of direct Cypher")
    print("  5. Compare evolution between checkpoints")
    print("  6. Check Cypher correctness:")
    print("     - Valid syntax")
    print("     - Proper node/relationship references")
    print("     - Correct property access")
    print("     - Appropriate use of MATCH, WHERE, RETURN")
    print("="*80)
    
    # Save results to JSON for later analysis
    output_file = "checkpoint_comparison_results.json"
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                "expert": "expert-neo4j",
                "base_model": BASE_MODEL_PATH,
                "checkpoints_tested": [c[0] for c in checkpoints],
                "device": device,
                "test_config": GEN_CONFIG,
                "results": results
            }, f, indent=2, ensure_ascii=False)
        print(f"\nResults saved to: {output_file}")
    except Exception as e:
        print(f"\nWarning: Could not save results to JSON: {e}")

if __name__ == "__main__":
    main()

