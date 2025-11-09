#!/usr/bin/env python3
"""
Quality analysis script for Neo4j expert checkpoint
Compares checkpoint with base model on various test cases
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any
from datetime import datetime

try:
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    import torch
except ImportError:
    print("ERROR: Required packages not installed. Install with:")
    print("  pip install transformers peft torch")
    sys.exit(1)

# Paths
BASE_MODEL_PATH = "F:/Node/hivellm/expert/models/Qwen3-0.6B"
EXPERT_DIR = Path(__file__).parent.parent
CHECKPOINT_PATH = EXPERT_DIR / "weights" / "qwen3-06b" / "checkpoint-250"

# Test cases (reduced to 4 for faster testing)
TEST_CASES = [
    {
        "name": "Simple MATCH query",
        "schema": """Node properties:
- **Person**
  - `name`: STRING
  - `age`: INTEGER
Relationships:
None""",
        "question": "Find all people",
        "expected_keywords": ["MATCH", "Person", "RETURN"],
        "category": "basic"
    },
    {
        "name": "MATCH with WHERE filter",
        "schema": """Node properties:
- **Person**
  - `name`: STRING
  - `age`: INTEGER
Relationships:
None""",
        "question": "Find people older than 30",
        "expected_keywords": ["MATCH", "Person", "WHERE", "age", "RETURN"],
        "category": "basic"
    },
    {
        "name": "Relationship traversal",
        "schema": """Node properties:
- **Movie**
  - `title`: STRING
- **Person**
  - `name`: STRING
Relationships:
(:Person)-[:ACTED_IN]->(:Movie)""",
        "question": "Find all actors in movies",
        "expected_keywords": ["MATCH", "ACTED_IN", "Person", "Movie", "RETURN"],
        "category": "intermediate"
    },
    {
        "name": "Aggregation COUNT",
        "schema": """Node properties:
- **User**
  - `name`: STRING
Relationships:
None""",
        "question": "Count total users",
        "expected_keywords": ["MATCH", "COUNT", "RETURN"],
        "category": "intermediate"
    }
]


def load_base_model():
    """Load base model without adapter"""
    print("Loading base model...")
    print("  This may take a minute...")
    sys.stdout.flush()
    
    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL_PATH,
        device_map="auto",
        dtype=torch.bfloat16,
        trust_remote_code=True,
        low_cpu_mem_usage=True
    )
    print("  Model loaded, loading tokenizer...")
    sys.stdout.flush()
    
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_PATH, trust_remote_code=True)
    print("  [OK] Base model loaded")
    sys.stdout.flush()
    return model, tokenizer


def load_checkpoint_model(checkpoint_path: Path):
    """Load base model with checkpoint adapter"""
    if not checkpoint_path.exists():
        raise FileNotFoundError(f"Checkpoint not found: {checkpoint_path}")
    
    print(f"Loading checkpoint from {checkpoint_path}...")
    print("  Loading base model first...")
    sys.stdout.flush()
    
    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL_PATH,
        device_map="auto",
        dtype=torch.bfloat16,
        trust_remote_code=True,
        low_cpu_mem_usage=True
    )
    
    print("  Loading adapter...")
    sys.stdout.flush()
    model = PeftModel.from_pretrained(model, str(checkpoint_path))
    
    print("  Loading tokenizer...")
    sys.stdout.flush()
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_PATH, trust_remote_code=True)
    print("  [OK] Checkpoint model loaded")
    sys.stdout.flush()
    return model, tokenizer


def format_prompt(schema: str, question: str) -> str:
    """Format prompt using Qwen3 native format"""
    system_content = f"Dialect: cypher\nSchema:\n{schema}"
    
    # Qwen3 format: <|im_start|>role\ncontent<|im_end|>
    return (
        f"<|im_start|>system\n{system_content}<|im_end|>\n"
        f"<|im_start|>user\n{question}<|im_end|>\n"
        f"<|im_start|>assistant\n"
    )


def generate_cypher(model, tokenizer, schema: str, question: str, max_tokens: int = 200) -> str:
    """Generate Cypher query"""
    prompt = format_prompt(schema, question)
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            temperature=0.6,
            top_p=0.95,
            top_k=20,
            min_p=0.0,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id
        )
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=False)
    
    # Extract assistant response
    if "<|im_start|>assistant" in response:
        cypher = response.split("<|im_start|>assistant")[-1]
        cypher = cypher.replace("<|im_end|>", "").strip()
    else:
        cypher = response[len(prompt):].strip()
    
    # Clean up
    cypher = cypher.split("<|im_end|>")[0].strip()
    cypher = cypher.split("<|im_start|>")[0].strip()
    
    return cypher


def validate_cypher_syntax(cypher: str) -> bool:
    """Basic Cypher syntax validation"""
    if not cypher or len(cypher.strip()) < 5:
        return False
    
    cypher_upper = cypher.upper()
    
    # Must have at least one key command
    has_command = any(cmd in cypher_upper for cmd in [
        "MATCH", "CREATE", "MERGE", "RETURN", "WITH", "UNWIND"
    ])
    
    # Check for balanced parentheses and brackets
    balanced_parens = cypher.count('(') == cypher.count(')')
    balanced_brackets = cypher.count('[') == cypher.count(']')
    
    return has_command and balanced_parens and balanced_brackets


def check_keywords(cypher: str, expected_keywords: List[str]) -> Tuple[int, List[str]]:
    """Check how many expected keywords are present"""
    cypher_upper = cypher.upper()
    found = []
    missing = []
    
    for keyword in expected_keywords:
        if keyword.upper() in cypher_upper:
            found.append(keyword)
        else:
            missing.append(keyword)
    
    return len(found), missing


def analyze_quality(cypher: str, expected_keywords: List[str]) -> Dict[str, Any]:
    """Analyze quality of generated Cypher"""
    is_valid = validate_cypher_syntax(cypher)
    keyword_count, missing_keywords = check_keywords(cypher, expected_keywords)
    keyword_score = keyword_count / len(expected_keywords) if expected_keywords else 0
    
    # Additional quality checks
    has_return = "RETURN" in cypher.upper()
    has_match = "MATCH" in cypher.upper()
    length_ok = 10 <= len(cypher) <= 500
    
    quality_score = 0.0
    if is_valid:
        quality_score += 0.4
    if has_return:
        quality_score += 0.2
    if has_match:
        quality_score += 0.2
    if length_ok:
        quality_score += 0.1
    quality_score += keyword_score * 0.1
    
    return {
        "is_valid": is_valid,
        "keyword_count": keyword_count,
        "keyword_total": len(expected_keywords),
        "keyword_score": keyword_score,
        "missing_keywords": missing_keywords,
        "has_return": has_return,
        "has_match": has_match,
        "length_ok": length_ok,
        "quality_score": quality_score,
        "length": len(cypher)
    }


def run_comparison(base_model, base_tokenizer, checkpoint_model, checkpoint_tokenizer):
    """Run comparison tests"""
    results = {
        "base": [],
        "checkpoint": [],
        "comparison": []
    }
    
    print("\n" + "=" * 80)
    print("RUNNING QUALITY TESTS")
    print("=" * 80)
    
    for i, test_case in enumerate(TEST_CASES, 1):
        print(f"\n{'=' * 80}")
        print(f"TEST {i}/{len(TEST_CASES)}: {test_case['name']} ({test_case['category']})")
        print(f"{'=' * 80}")
        print(f"\nQuestion: {test_case['question']}")
        
        # Generate with base model
        print("\n[Base Model]")
        print(f"  Generating...")
        sys.stdout.flush()
        try:
            base_cypher = generate_cypher(
                base_model, base_tokenizer,
                test_case['schema'], test_case['question']
            )
            base_analysis = analyze_quality(base_cypher, test_case['expected_keywords'])
            print(f"  Cypher: {base_cypher[:150]}...")
            print(f"  Valid: {base_analysis['is_valid']}, Score: {base_analysis['quality_score']:.2f}")
            results["base"].append({
                "test_name": test_case['name'],
                "cypher": base_cypher,
                "analysis": base_analysis
            })
        except Exception as e:
            print(f"  ERROR: {e}")
            results["base"].append({
                "test_name": test_case['name'],
                "cypher": "",
                "analysis": {"quality_score": 0.0, "is_valid": False, "error": str(e)}
            })
        
        # Generate with checkpoint
        print("\n[Checkpoint Model]")
        print(f"  Generating...")
        sys.stdout.flush()
        try:
            checkpoint_cypher = generate_cypher(
                checkpoint_model, checkpoint_tokenizer,
                test_case['schema'], test_case['question']
            )
            checkpoint_analysis = analyze_quality(checkpoint_cypher, test_case['expected_keywords'])
            print(f"  Cypher: {checkpoint_cypher[:150]}...")
            print(f"  Valid: {checkpoint_analysis['is_valid']}, Score: {checkpoint_analysis['quality_score']:.2f}")
            results["checkpoint"].append({
                "test_name": test_case['name'],
                "cypher": checkpoint_cypher,
                "analysis": checkpoint_analysis
            })
        except Exception as e:
            print(f"  ERROR: {e}")
            results["checkpoint"].append({
                "test_name": test_case['name'],
                "cypher": "",
                "analysis": {"quality_score": 0.0, "is_valid": False, "error": str(e)}
            })
        
        # Compare
        if len(results["base"]) > 0 and len(results["checkpoint"]) > 0:
            base_score = results["base"][-1]["analysis"]["quality_score"]
            checkpoint_score = results["checkpoint"][-1]["analysis"]["quality_score"]
            improvement = checkpoint_score - base_score
            
            comparison = {
                "test_name": test_case['name'],
                "base_score": base_score,
                "checkpoint_score": checkpoint_score,
                "improvement": improvement,
                "improvement_percent": (improvement / base_score * 100) if base_score > 0 else 0
            }
            results["comparison"].append(comparison)
            
            print(f"\n[Comparison]")
            print(f"  Base: {base_score:.2f} | Checkpoint: {checkpoint_score:.2f} | Improvement: {improvement:+.2f} ({comparison['improvement_percent']:+.1f}%)")
    
    return results


def generate_report(results: Dict, checkpoint_path: Path):
    """Generate quality report"""
    print("\n" + "=" * 80)
    print("QUALITY REPORT")
    print("=" * 80)
    
    # Calculate averages
    base_scores = [r["analysis"]["quality_score"] for r in results["base"]]
    checkpoint_scores = [r["analysis"]["quality_score"] for r in results["checkpoint"]]
    
    avg_base = sum(base_scores) / len(base_scores) if base_scores else 0
    avg_checkpoint = sum(checkpoint_scores) / len(checkpoint_scores) if checkpoint_scores else 0
    improvement = avg_checkpoint - avg_base
    improvement_percent = (improvement / avg_base * 100) if avg_base > 0 else 0
    
    # Validity rates
    base_valid = sum(1 for r in results["base"] if r["analysis"].get("is_valid", False))
    checkpoint_valid = sum(1 for r in results["checkpoint"] if r["analysis"].get("is_valid", False))
    
    print(f"\nOverall Scores:")
    print(f"  Base Model:     {avg_base:.2f} ({base_valid}/{len(results['base'])} valid)")
    print(f"  Checkpoint:     {avg_checkpoint:.2f} ({checkpoint_valid}/{len(results['checkpoint'])} valid)")
    print(f"  Improvement:    {improvement:+.2f} ({improvement_percent:+.1f}%)")
    
    print(f"\nBy Category:")
    categories = {}
    for comp in results["comparison"]:
        test_name = comp["test_name"]
        category = next(t["category"] for t in TEST_CASES if t["name"] == test_name)
        if category not in categories:
            categories[category] = []
        categories[category].append(comp)
    
    for category, comps in categories.items():
        cat_base = sum(c["base_score"] for c in comps) / len(comps)
        cat_checkpoint = sum(c["checkpoint_score"] for c in comps) / len(comps)
        cat_improvement = cat_checkpoint - cat_base
        print(f"  {category.capitalize():12s}: Base={cat_base:.2f}, Checkpoint={cat_checkpoint:.2f}, Improvement={cat_improvement:+.2f}")
    
    # Save report
    report_path = EXPERT_DIR / "docs" / f"checkpoint_250_quality_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    report = {
        "checkpoint": str(checkpoint_path),
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "avg_base_score": avg_base,
            "avg_checkpoint_score": avg_checkpoint,
            "improvement": improvement,
            "improvement_percent": improvement_percent,
            "base_valid_count": base_valid,
            "checkpoint_valid_count": checkpoint_valid,
            "total_tests": len(results["base"])
        },
        "results": results
    }
    
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n[OK] Report saved to: {report_path}")
    
    return report


def main():
    """Main function"""
    print("=" * 80)
    print("NEO4J EXPERT CHECKPOINT QUALITY ANALYSIS")
    print("=" * 80)
    print(f"Checkpoint: {CHECKPOINT_PATH}")
    print(f"Base Model: {BASE_MODEL_PATH}")
    
    # Load models
    try:
        base_model, base_tokenizer = load_base_model()
        checkpoint_model, checkpoint_tokenizer = load_checkpoint_model(CHECKPOINT_PATH)
    except Exception as e:
        print(f"\nERROR: Failed to load models: {e}")
        sys.exit(1)
    
    # Run comparison
    try:
        results = run_comparison(base_model, base_tokenizer, checkpoint_model, checkpoint_tokenizer)
        report = generate_report(results, CHECKPOINT_PATH)
        
        # Final verdict
        print("\n" + "=" * 80)
        print("VERDICT")
        print("=" * 80)
        improvement = report["summary"]["improvement_percent"]
        if improvement > 10:
            print("[EXCELLENT] Significant improvement over base model!")
        elif improvement > 5:
            print("[GOOD] Noticeable improvement over base model")
        elif improvement > 0:
            print("[MARGINAL] Small improvement, may need more training")
        else:
            print("[POOR] No improvement or regression detected")
            print("   Consider: More training data, different hyperparameters, or longer training")
            print("   Note: checkpoint-250 is early in training, continue training for better results")
        
    except Exception as e:
        print(f"\nERROR during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

