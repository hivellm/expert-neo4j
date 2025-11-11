import json
import re
from collections import Counter, defaultdict
import matplotlib.pyplot as plt
from pathlib import Path

DOCS_DIR = Path(__file__).resolve().parent.parent / 'docs'

def analyze_cypher_clauses(file_path):
    """Analyze Cypher clauses in a dataset file"""
    clauses = {
        'MATCH': 0, 'MERGE': 0, 'RETURN': 0, 'WITH': 0, 'CALL': 0,
        'ORDER BY': 0, 'SKIP': 0, 'LIMIT': 0, 'WHERE': 0, 'CREATE': 0,
        'DELETE': 0, 'SET': 0, 'REMOVE': 0, 'UNWIND': 0, 'FOREACH': 0,
        'CASE': 0, 'DISTINCT': 0, 'COUNT': 0, 'SUM': 0, 'AVG': 0,
        'MIN': 0, 'MAX': 0, 'COLLECT': 0, 'YIELD': 0
    }

    combinations = defaultdict(int)

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        data = json.loads(line)
                        query = data['text'].split('<|im_start|>assistant\n')[1].split('<|im_end|>')[0]

                        # Count individual clauses
                        for clause in clauses.keys():
                            if clause.upper() in query.upper():
                                clauses[clause] += 1

                        # Count combinations
                        present_clauses = []
                        for clause in ['MATCH', 'MERGE', 'RETURN', 'WITH', 'CALL', 'ORDER BY', 'SKIP', 'LIMIT']:
                            if clause.upper() in query.upper():
                                present_clauses.append(clause)

                        if present_clauses:
                            combo_key = ' + '.join(sorted(present_clauses))
                            combinations[combo_key] += 1

                    except (json.JSONDecodeError, KeyError, IndexError):
                        continue

    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return {}, {}

    return clauses, dict(combinations)

def create_distribution_charts():
    """Create distribution charts for all Cypher datasets"""
    datasets_dir = Path('experts/expert-neo4j/datasets')
    dataset_files = sorted([p.name for p in datasets_dir.glob('synthetic*.jsonl')])
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    all_clauses = {}
    all_combinations = {}

    for file in dataset_files:
        file_path = datasets_dir / file
        dataset_name = file.replace('synthetic_', '').replace('.jsonl', '').upper()

        print(f"Analyzing {dataset_name}...")
        clauses, combinations = analyze_cypher_clauses(file_path)

        all_clauses[dataset_name] = clauses
        all_combinations[dataset_name] = combinations

    # Create comprehensive charts
    create_clause_distribution_chart(all_clauses)
    create_combination_heatmap(all_combinations)
    create_detailed_analysis(all_clauses, all_combinations)

def create_clause_distribution_chart(all_clauses):
    """Create a comprehensive clause distribution chart"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 8))

    # Prepare data
    datasets = list(all_clauses.keys())
    clauses = list(all_clauses[datasets[0]].keys())

    # Create heatmap data
    heatmap_data = []
    for clause in clauses:
        row = []
        for dataset in datasets:
            row.append(all_clauses[dataset].get(clause, 0))
        heatmap_data.append(row)

    # Create heatmap
    im = ax1.imshow(heatmap_data, cmap='YlOrRd', aspect='auto')
    ax1.set_title('Cypher Clauses Distribution Across Datasets')
    ax1.set_xticks(range(len(datasets)))
    ax1.set_yticks(range(len(clauses)))
    ax1.set_xticklabels(datasets, rotation=45)
    ax1.set_yticklabels(clauses)

    # Add text annotations
    for i in range(len(clauses)):
        for j in range(len(datasets)):
            text = ax1.text(j, i, heatmap_data[i][j], ha="center", va="center", color="black")

    plt.colorbar(im, ax=ax1, label='Frequency')

    # Create stacked bar chart
    bottom = [0] * len(clauses)
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']

    for i, dataset in enumerate(datasets):
        values = [all_clauses[dataset].get(clause, 0) for clause in clauses]
        ax2.bar(range(len(clauses)), values, bottom=bottom, label=dataset, color=colors[i % len(colors)])
        bottom = [bottom[j] + values[j] for j in range(len(clauses))]

    ax2.set_title('Cypher Clauses Distribution (Stacked)')
    ax2.set_xlabel('Clause')
    ax2.set_ylabel('Frequency')
    ax2.set_xticks(range(len(clauses)))
    ax2.set_xticklabels(clauses, rotation=45)
    ax2.legend(title='Dataset', bbox_to_anchor=(1.05, 1), loc='upper left')

    plt.tight_layout()
    plt.savefig(DOCS_DIR / 'cypher_clauses_distribution.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_combination_heatmap(all_combinations):
    """Create a heatmap showing clause combinations"""
    # Get all unique combinations across datasets
    all_combo_keys = set()
    for dataset_combos in all_combinations.values():
        all_combo_keys.update(dataset_combos.keys())

    all_combo_keys = sorted(list(all_combo_keys))[:15]  # Limit to top 15 for readability
    datasets = list(all_combinations.keys())

    # Create data matrix
    heatmap_data = []
    for combo in all_combo_keys:
        row = []
        for dataset in datasets:
            row.append(all_combinations[dataset].get(combo, 0))
        heatmap_data.append(row)

    if heatmap_data:
        fig, ax = plt.subplots(figsize=(12, 10))

        # Create heatmap
        im = ax.imshow(heatmap_data, cmap='Blues', aspect='auto')
        ax.set_title('Cypher Clause Combinations Across Datasets')
        ax.set_xticks(range(len(datasets)))
        ax.set_yticks(range(len(all_combo_keys)))
        ax.set_xticklabels(datasets, rotation=45)
        ax.set_yticklabels(all_combo_keys)

        # Add text annotations
        for i in range(len(all_combo_keys)):
            for j in range(len(datasets)):
                text = ax.text(j, i, heatmap_data[i][j], ha="center", va="center", color="white" if heatmap_data[i][j] > 50 else "black")

        plt.colorbar(im, ax=ax, label='Frequency')
        plt.tight_layout()
        plt.savefig(DOCS_DIR / 'cypher_combinations_heatmap.png', dpi=300, bbox_inches='tight')
        plt.show()

def print_analysis_summary(all_clauses, all_combinations):
    """Print detailed analysis summary"""
    print("\n" + "="*60)
    print("        CYPHIER CLAUSES DISTRIBUTION ANALYSIS")
    print("="*60 + "\n")

    datasets = list(all_clauses.keys())

    print("TOTAL SAMPLES PER DATASET:")
    for dataset in datasets:
        print(f"   {dataset}: 200 samples")
    print(f"\nTOTAL ANALYSIS: {len(datasets)} datasets × 200 samples = {len(datasets) * 200} total samples\n")

    print("CLAUSE FREQUENCY ACROSS ALL DATASETS:")
    print("-" * 50)
    all_clause_totals = {}
    for dataset in datasets:
        for clause, count in all_clauses[dataset].items():
            all_clause_totals[clause] = all_clause_totals.get(clause, 0) + count

    for clause, total in sorted(all_clause_totals.items(), key=lambda x: x[1], reverse=True):
        if total > 0:
            percentage = (total / (len(datasets) * 200)) * 100
            print("6")

    print("\nMOST COMMON CLAUSE COMBINATIONS:")
    print("-" * 50)
    all_combo_totals = {}
    for dataset in datasets:
        for combo, count in all_combinations[dataset].items():
            all_combo_totals[combo] = all_combo_totals.get(combo, 0) + count

    for combo, total in sorted(all_combo_totals.items(), key=lambda x: x[1], reverse=True)[:15]:
        percentage = (total / (len(datasets) * 200)) * 100
        print("6")

    print("\nDATASET STATISTICS:")
    print("-" * 50)
    for dataset in datasets:
        clauses_present = sum(1 for count in all_clauses[dataset].values() if count > 0)
        total_clauses = sum(all_clauses[dataset].values())
        avg_clauses_per_sample = total_clauses / 200 if total_clauses > 0 else 0
        print("6")

    print("\nMATCH-RELATED CLAUSES ANALYSIS:")
    print("-" * 50)
    match_related = ['MATCH', 'WHERE', 'ORDER BY', 'SKIP', 'LIMIT', 'RETURN']
    print(f"{'Dataset':<10} {' | '.join([f'{c:<8}' for c in match_related])}")
    print("-" * 50)
    for dataset in datasets:
        counts = [all_clauses[dataset].get(clause, 0) for clause in match_related]
        print(f"{dataset:<10} {' | '.join([f'{c:<8}' for c in counts])}")

    print("\nAGGREGATION FUNCTIONS:")
    print("-" * 50)
    agg_functions = ['COUNT', 'SUM', 'AVG', 'MIN', 'MAX', 'COLLECT']
    print(f"{'Dataset':<10} {' | '.join([f'{f:<6}' for f in agg_functions])}")
    print("-" * 50)
    for dataset in datasets:
        counts = [all_clauses[dataset].get(func, 0) for func in agg_functions]
        print(f"{dataset:<10} {' | '.join([f'{c:<6}' for c in counts])}")

    print("\nMODIFICATION CLAUSES:")
    print("-" * 50)
    mod_clauses = ['CREATE', 'MERGE', 'SET', 'DELETE', 'REMOVE']
    print(f"{'Dataset':<10} {' | '.join([f'{c:<6}' for c in mod_clauses])}")
    print("-" * 50)
    for dataset in datasets:
        counts = [all_clauses[dataset].get(clause, 0) for clause in mod_clauses]
        print(f"{dataset:<10} {' | '.join([f'{c:<6}' for c in counts])}")

    print("\nSPECIAL CLAUSES:")
    print("-" * 50)
    special_clauses = ['WITH', 'CALL', 'UNWIND', 'FOREACH', 'CASE', 'DISTINCT', 'YIELD']
    print(f"{'Dataset':<10} {' | '.join([f'{c:<7}' for c in special_clauses])}")
    print("-" * 50)
    for dataset in datasets:
        counts = [all_clauses[dataset].get(clause, 0) for clause in special_clauses]
        print(f"{dataset:<10} {' | '.join([f'{c:<7}' for c in counts])}")

def create_distribution_charts():
    """Create distribution charts for all Cypher datasets"""
    datasets_dir = Path('experts/expert-neo4j/datasets')
    dataset_files = sorted([p.name for p in datasets_dir.glob('synthetic*.jsonl')])
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    all_clauses = {}
    all_combinations = {}

    for file in dataset_files:
        file_path = datasets_dir / file
        dataset_name = file.replace('synthetic_', '').replace('.jsonl', '').upper()

        print(f"Analyzing {dataset_name}...")
        clauses, combinations = analyze_cypher_clauses(file_path)

        all_clauses[dataset_name] = clauses
        all_combinations[dataset_name] = combinations

    # Create charts
    create_clause_distribution_chart(all_clauses)
    create_combination_heatmap(all_combinations)
    print_analysis_summary(all_clauses, all_combinations)

if __name__ == "__main__":
    create_distribution_charts()
