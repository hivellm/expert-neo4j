import json

with open('checkpoint_comparison_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Find TEST 12 (complex_001)
test12 = None
for result in data['results']:
    if result['test_id'] == 'complex_001':
        test12 = result
        break

if test12:
    print("=" * 80)
    print("TEST 12: Complex Query (People aged 25-40 in New York)")
    print("=" * 80)
    print(f"\nPrompt: {test12['user_prompt']}")
    print(f"\nCheckpoint-2000 Output:")
    print("-" * 80)
    output = test12['checkpoint_outputs']['2000']
    print(output)
    print("-" * 80)
    
    # Check if it's valid Cypher
    is_valid = output.startswith('MATCH') and 'WHERE' in output and 'RETURN' in output
    print(f"\nValid Cypher: {is_valid}")
    
    if is_valid:
        print("✅ RESOLVED: Complex OR/AND logic works!")
    else:
        print("❌ NOT RESOLVED: Still generating text or incomplete queries")
else:
    print("TEST 12 not found in results")

