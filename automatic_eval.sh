# Benchmarks
echo "== Evaluate Benchmarks =="

start_time=$(date +%s.%N)
python3 analysis.py chains/case_studies.jsonl --info --relative-bound 0.95 --no-print --output results/case_studies.jsonl
end_time=$(date +%s.%N)
elapsed=$(echo "$end_time - $start_time" | bc)

echo "Evaluation results stored in: results/case_studies.jsonl"

echo "- Total elapsed time: ${elapsed}s"
python3 -c "import json; total = sum(json.loads(line).get('analysis_time_sec', 0) for line in open('results/case_studies.jsonl')); print(f'- SUM analysis_time_sec: {total}')"

# python3 -c "import json; anchors = [(json.loads(line).get('ID', []), json.loads(line).get('#AnchorsRT', [])) for line in open('results/case_studies.jsonl')]; print('Anchor points:', anchors)"
python3 -c "import json; anchors = [json.loads(line).get('#AnchorsRT', []) for line in open('results/case_studies.jsonl')]; print('- Anchor points:', anchors); print('- SUM:', sum(anchors)); print('- #LEQ 3:', sum((a<=3 for a in anchors)), '/', len(anchors));"

mkdir -p paperdata
python3 make_table.py results/case_studies.jsonl > paperdata/case_studies.tex

echo "Table of Case-Study results stored in: paperdata/case_studies.tex"


# Synthetic Evaluation




