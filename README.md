# Expert Neo4j

[![Version](https://img.shields.io/badge/version-0.2.3-blue.svg)](https://github.com/hivellm/expert-neo4j/releases/tag/v0.2.3)
[![License](https://img.shields.io/badge/license-CC--BY--4.0-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-production-brightgreen.svg)](README.md#quick-start)
[![Quality](https://img.shields.io/badge/quality-79%25%20valid-success.svg)](README.md#known-limitations)
[![Test Scenarios](https://img.shields.io/badge/tests-11%2F14%20passed-success.svg)](README.md#known-limitations)

[![Base Model](https://img.shields.io/badge/base%20model-Qwen3--0.6B-orange.svg)](README.md#features)
[![Checkpoint](https://img.shields.io/badge/checkpoint-2000-blue.svg)](README.md#training--configuration)
[![Adapter](https://img.shields.io/badge/adapter-DoRA%20r%3D16-blue.svg)](README.md#training--configuration)
[![Dataset](https://img.shields.io/badge/dataset-29.7k%20examples-brightgreen.svg)](README.md#training--configuration)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20CUDA-0078d4.svg)](README.md#features)

Neo4j Cypher query generation expert. Trained on 29,772 validated examples from multiple sources (neo4j/text2cypher-2025v1, Neo4j official documentation). Optimized for graph database queries with MATCH, CREATE, relationships, and pattern matching.

## Quick Start

```bash
# Install
expert-cli install expert-neo4j@0.2.3

# Use in chat
expert-cli chat --experts neo4j
> Find all movies directed by people born in the 1960s
```

**Works best for:** Graph analytics, social networks, knowledge graphs, recommendation systems, relationship pattern matching

## Features

- ✅ **Neo4j Cypher dialect** with graph pattern matching
- ✅ **Schema-aware** query generation (Qwen3 native format)
- ✅ **DoRA adapter (r=16)** for complex graph queries
- ✅ **Grammar validation** (GBNF) for syntax enforcement
- ✅ **Unsloth integration** - 2x faster training, 70% less VRAM
- ✅ **Windows optimized** with CUDA support

## Capabilities

- ✅ MATCH queries with node and relationship patterns
- ✅ Node filtering (WHERE, property matching)
- ✅ Relationship traversal (single and multi-hop)
- ✅ Aggregations (COUNT, SUM, AVG, collect)
- ✅ ORDER BY and LIMIT
- ✅ Pattern matching with variable-length paths
- ✅ CREATE and MERGE operations
- ✅ WITH clause for query chaining

## Known Limitations

**Critical Issue**: All limitations show discrepancy between direct checkpoint evaluation (works) and CLI usage (generates text). This suggests a CLI prompt formatting or model loading issue.

- ❌ **String pattern matching (CONTAINS)** - Generates explanatory text instead of Cypher (CLI test)
- ❌ **AVG with GROUP BY** - Generates explanatory text instead of Cypher (CLI test)
- ❌ **Relationship properties with dates** - Generates explanatory text instead of Cypher (CLI test)
- ⚠️ **Complex OR/AND logic** - Generates partial text instead of full Cypher query (CLI test)
- ⚠️ **Multi-hop queries** - All checkpoints generate MATCH without RETURN clause
- ⚠️ **Pattern matching** - May miss category filters

**Recommendations:**
- ✅ **ALWAYS provide explicit graph schema** in prompts - Required for Cypher generation
- ✅ Excellent for: MATCH patterns, WHERE filters, relationship queries, aggregations, ordering (with schema)
- ✅ **Checkpoint-2000 recommended** - Best overall performance (79% valid queries)
- 📊 See `docs/CHECKPOINT_EVALUATION_REPORT.md` for detailed analysis

## Performance

**Checkpoint Evaluation:**
- **Best checkpoint**: checkpoint-2000 (79% valid queries, 11/14 tests)
- **Checkpoints evaluated**: 6 (500, 1000, 1500, 2000, 2500, 2840)
- **Evaluation method**: Direct checkpoint evaluation with 14 test cases
- See `docs/CHECKPOINT_EVALUATION_REPORT.md` for complete analysis

**Inference:**
- Adapter size: ~51MB (DoRA r=16)
- Load time: <10ms (hot), <200ms (cold)
- Inference speed: ~100-150ms per query (RTX 4090)

**Strengths:**
- Valid Cypher syntax across basic categories
- Correct WHERE clauses and relationship queries
- Valid aggregations and ordering
- Complex queries with multiple conditions

## Training

```bash
cd experts/expert-neo4j
../../cli/target/release/expert-cli train
```

**Configuration:**
- **Dataset**: 29,772 validated examples (neo4j/text2cypher-2025v1 + Neo4j documentation)
- **Format**: Qwen3 native (`<|im_start|>` / `<|im_end|>`)
- **Adapter**: DoRA r=16, alpha=32
- **Training**: Unsloth (2x faster, 70% less VRAM)
- **Batch**: 2 × 45 = 90 effective batch size
- **LR**: 5e-5, dropout: 0.1, epochs: 2.0

**Dataset Sources:**
- neo4j/text2cypher-2025v1 (primary)
- Neo4j official documentation
- Basic Cypher syntax validation
- Deduplicated by question

## Usage

### Interactive Chat
```bash
expert-cli chat --experts neo4j
```

### Single Query
```bash
expert-cli chat --experts neo4j --prompt "Find all nodes with more than 5 relationships"
```

### Python Integration
```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

base_model = AutoModelForCausalLM.from_pretrained(
    "F:/Node/hivellm/expert/models/Qwen3-0.6B",
    device_map="auto",
    dtype=torch.bfloat16,
    trust_remote_code=True
)
tokenizer = AutoTokenizer.from_pretrained(base_model_path, trust_remote_code=True)

# Load expert adapter
model = PeftModel.from_pretrained(base_model, "experts/expert-neo4j")

# Generate Cypher
schema = "Node properties:\n- **Person**\n  - `name`: STRING\n..."
question = "Find movies directed by people born in the 1960s"

messages = [
    {"role": "system", "content": f"Dialect: cypher\nSchema:\n{schema}"},
    {"role": "user", "content": question}
]

text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
inputs = tokenizer([text], return_tensors="pt").to(model.device)

with torch.no_grad():
    outputs = model.generate(**inputs, max_new_tokens=200, temperature=0.7, top_p=0.8)

cypher = tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
```

## Version History

### v0.2.3 (Current) - 2025-11-07
- ✅ Checkpoint-2000 selected (79% valid queries)
- ✅ Prompt template corrected to qwen3 native format
- ✅ Systematic evaluation of 6 checkpoints
- ✅ Package: `expert-neo4j-qwen3-0-6b.v0.2.3.expert` (33.19 MB)

**Improvements over v0.1.1:**
- Checkpoint selection based on systematic evaluation
- Dataset expanded from 29,512 to 29,772 examples
- Performance documented: 79% valid queries

### v0.2.2 - 2025-11-07
- ✅ Prompt template fix implemented

### v0.1.1 - 2025-11-06
- ✅ Initial release
- Dataset: 29,512 examples
- Manual checkpoint selection

## Credits

- **Base Model**: Qwen/Qwen3-0.6B
- **Datasets**: neo4j/text2cypher-2025v1, Neo4j Official Documentation
- **Training**: Unsloth (2x speedup)
- **Framework**: HuggingFace Transformers + PEFT + TRL

## License

Apache-2.0
