# Expert Neo4j Version Comparison Report

**Comparison**: v0.1.1 vs v0.2.3  
**Method**: CLI-based testing  
**Date**: 2025-11-07  
**Test Cases**: 8 scenarios covering basic queries, filters, relationships, aggregations, ordering, and complex queries

---

## Executive Summary

This report compares expert-neo4j versions 0.1.1 and 0.2.3 using the CLI chat interface. Both versions were tested with identical prompts across 8 test scenarios.

**Key Finding**: Both versions are generating explanatory text instead of direct Cypher queries when tested via CLI, which differs from the direct checkpoint evaluation results where checkpoint-2000 (v0.2.3) showed 79% valid Cypher generation.

**Possible Causes**:
- CLI prompt formatting differences
- Model loading differences between CLI and direct checkpoint evaluation
- Generation parameters affecting output format

---

## Test Configuration

- **CLI**: expert-cli.exe (CUDA build)
- **Max Tokens**: 300
- **Temperature**: 0.1
- **Device**: CUDA (auto-detected)
- **Prompt Template**: qwen3 (native format)

---

## Test Results

### TEST 1: Basic MATCH (Find all people)

**Prompt**: Find all people (Person node with name, age)

**v0.1.1 Output**:
```
. The user wants me to find all people based on the given dialect and schema. 
The dialect is cypher, and the schema has a Node properties with Person and 
Relationships. The Relationships section is empty.
```

**v0.2.3 Output**:
```
. The user wants me to find all people based on the given dialect and schema. 
The dialect is cypher, and the schema has a Node properties with Person and 
Relationships. The Relationships section is empty.
```

**Analysis**: Both versions generate identical explanatory text. Neither generates Cypher.

---

### TEST 2: Basic MATCH (List all movies)

**Prompt**: List all movies (Movie node with title, released)

**v0.1.1 Output**:
```
. Could you provide the list of movies you'd like to see?
```

**v0.2.3 Output**:
```
asking me to list all movies based on the given dialect. Let me check the schema 
again. The schema has a Node property called Movie with title and released. 
Relationships are none. So, the task is to retrieve all movies from the Movie node.
```

**Analysis**: v0.1.1 asks for clarification. v0.2.3 provides reasoning but no Cypher.

---

### TEST 3: WHERE Filter (People older than 30)

**Prompt**: Find people older than 30

**v0.1.1 Output**:
```
. The user wants to find people older than 30 using the Cypher dialect. The schema 
has a Node with properties name and age, and no relationships. So, I need to query 
the graph where the age is greater than 30.
```

**v0.2.3 Output**:
```
.
```

**Analysis**: v0.1.1 explains the query logic. v0.2.3 generates minimal output (possibly truncated).

---

### TEST 4: WHERE Filter (Products price < 100)

**Prompt**: Find products with price less than 100

**v0.1.1 Output**:
```
with price less than
```

**v0.2.3 Output**:
```
, perhaps in a list format. But since the assistant's answer should be in the box, 
maybe the answer is the query. But the user might just want the query written.
```

**Analysis**: v0.1.1 output is incomplete. v0.2.3 provides meta-commentary about query format.

---

### TEST 5: Relationship Query (Find actors in movies)

**Prompt**: Find all actors in movies (ACTED_IN relationship)

**v0.1.1 Output**:
```
... but since the relationships are between Person and Movie, perhaps the answer is
```

**v0.2.3 Output**:
```
. The user wants to find all actors in movies using the given dialect and schema. 
The schema has a Node with Movie and Person, and there's a relationship between 
Person and Movie via the ACTED_IN relationship.
```

**Analysis**: v0.1.1 output is incomplete. v0.2.3 explains the relationship but doesn't generate Cypher.

---

### TEST 6: Aggregation (Count total users)

**Prompt**: Count total users

**v0.1.1 Output**:
```
and schema. The dialect here is cypher, which I think refers to a specific type of 
graph data model. The schema provided has a Node property called 'User' with a 
'name' field as a string.
```

**v0.2.3 Output**:
```
. The user is asking to count the total number of users based on the given dialect 
and schema. The dialect here is cypher, which I think refers to a specific type of 
graph data model. The schema provided has a Node property called 'User' with a 
'name' field as a string.
```

**Analysis**: Both versions provide similar explanatory text about the schema.

---

### TEST 7: Ordering (Top 5 expensive products)

**Prompt**: Find top 5 most expensive products

**v0.1.1 Output**:
```
, maybe the answer is that the data isn't available. But the user might expect a 
response. Maybe the initial data is in a JSON format, and I need to list the top 5 
products from that data. But since I don't have access to the actual data, perhaps 
the answer is that the data isn't provided. But the
```

**v0.2.3 Output**:
```
ased on the given dialect. The schema has Node properties with Product having name 
and price, and no relationships. So, I need to figure out how to retrieve the top 
products.
```

**Analysis**: v0.1.1 provides extensive reasoning about data availability. v0.2.3 explains the task but doesn't generate Cypher.

---

### TEST 8: Complex Query (People aged 25-40 in New York)

**Prompt**: Find people aged between 25 and 40 living in New York

**v0.1.1 Output**:
```
. The user wants to find people aged between 25 and 40 living in New York. The 
dialect is cypher, so I need to use the cypher schema. The schema has a Person node 
with name, age, and city. Relationships are none.
```

**v0.2.3 Output**:
```
and 40 living in New York. The dialect is cypher, so I need to use the cypher schema. 
The schema has a Person node with name, age, and city. Relationships are none.
```

**Analysis**: Both versions explain the query requirements but don't generate Cypher.

---

## Comparison Summary

| Test | v0.1.1 Behavior | v0.2.3 Behavior | Difference |
|------|----------------|------------------|------------|
| match_001 | Explanatory text | Identical explanatory text | None |
| match_002 | Asks for clarification | Provides reasoning | v0.2.3 more verbose |
| where_001 | Explains query logic | Minimal output | v0.1.1 more complete |
| where_002 | Incomplete output | Meta-commentary | Both problematic |
| rel_001 | Incomplete output | Explains relationship | v0.2.3 more complete |
| agg_001 | Schema explanation | Similar explanation | Similar |
| order_001 | Extensive reasoning | Task explanation | v0.1.1 more verbose |
| complex_001 | Query requirements | Similar explanation | Similar |

---

## Key Observations

1. **No Cypher Generation**: Neither version generates actual Cypher queries when tested via CLI, despite checkpoint-2000 showing 79% valid Cypher in direct evaluation.

2. **Explanatory Text**: Both versions consistently generate explanatory text about the query requirements rather than executing queries.

3. **Output Inconsistency**: Some outputs are incomplete or truncated, particularly in v0.1.1.

4. **Version Differences**: 
   - v0.2.3 tends to be more verbose in explanations
   - v0.1.1 sometimes asks for clarification
   - Both show similar patterns of reasoning without execution

---

## Discrepancy Analysis

**Expected Behavior** (based on checkpoint evaluation):
- Checkpoint-2000 (v0.2.3) should generate valid Cypher queries like:
  - `MATCH (p:Person) RETURN p.name AS name, p.age AS age`
  - `MATCH (p:Person) WHERE p.age > 30 RETURN p.name AS name, p.age AS age`

**Actual Behavior** (CLI testing):
- Both versions generate explanatory text instead of Cypher

**Possible Causes**:
1. **Prompt Formatting**: CLI may format prompts differently than direct checkpoint evaluation
2. **Model Loading**: CLI may load adapters differently than direct Python evaluation
3. **Generation Parameters**: Temperature 0.1 may be too low, causing conservative outputs
4. **Stop Sequences**: CLI stop sequences may be cutting off Cypher generation
5. **Template Differences**: Prompt template application may differ between CLI and direct evaluation

---

## Recommendations

1. **Investigate CLI Prompt Formatting**
   - Compare CLI-formatted prompts with direct evaluation prompts
   - Verify prompt template application in CLI vs. direct evaluation

2. **Adjust Generation Parameters**
   - Test with higher temperature (0.6-0.8) to encourage more direct outputs
   - Increase max_tokens to allow complete query generation
   - Review stop sequences configuration

3. **Verify Adapter Loading**
   - Confirm CLI is correctly loading checkpoint-2000 adapter
   - Compare adapter weights between CLI and direct evaluation

4. **Compare with Direct Evaluation**
   - Run same prompts through direct checkpoint evaluation (compare.py)
   - Identify differences in prompt formatting and generation

5. **Test with Different Prompts**
   - Try simpler prompts without schema information
   - Test with prompts that explicitly request Cypher output

---

## Conclusion

The CLI-based comparison reveals that both v0.1.1 and v0.2.3 generate explanatory text rather than Cypher queries, which contradicts the direct checkpoint evaluation results showing checkpoint-2000 (v0.2.3) achieving 79% valid Cypher generation.

This discrepancy suggests a potential issue with:
- CLI prompt formatting or template application
- Model/adapter loading in CLI vs. direct evaluation
- Generation parameters or stop sequences

Further investigation is needed to reconcile the differences between CLI testing and direct checkpoint evaluation.

---

## Appendix: Test Results File

Full results saved to: `version_comparison_results.json`

**Report Generated**: 2025-11-07  
**Comparison Script**: `compare_versions.py`  
**CLI Version**: expert-cli.exe (CUDA build)

