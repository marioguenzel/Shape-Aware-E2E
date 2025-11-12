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


# Synthetic Evaluation - WATERS
echo "== Synthetic Evaluation - WATERS Benchmark =="

python3 generate.py --bench WATERS --tasks 5 --sets 100 --startid 0 EvalWATERS/chains05.jsonl
python3 generate.py --bench WATERS --tasks 20 --sets 100 --startid 1000 EvalWATERS/chains20.jsonl
python3 generate.py --bench WATERS --tasks 40 --sets 100 --startid 2000 EvalWATERS/chains50.jsonl

echo "Chains stored in EvalWATERS/chains<tasks-per-set>.jsonl"

for i in {0..2}; do
    python3 analysis.py EvalWATERS/chains05.jsonl --info --relative-bound 0.95 --no-print --output EvalWATERS/results05_${i}.jsonl
done

for i in {0..2}; do
    python3 analysis.py EvalWATERS/chains20.jsonl --info --relative-bound 0.95 --no-print --output EvalWATERS/results20_${i}.jsonl
done

for i in {0..2}; do
    python3 analysis.py EvalWATERS/chains50.jsonl --info --relative-bound 0.95 --no-print --output EvalWATERS/results50_${i}.jsonl
done

echo "Analysis stored in EvalWATERS/results<tasks-per-set>.jsonl"

python plot.py -o paperdata/WATERS_runtime.png paperdata/WATERS_anchors.png -c 3 EvalWATERS/results50_{0..2}.jsonl  EvalWATERS/results20_{0..2}.jsonl  EvalWATERS/results05_{0..2}.jsonl

echo "Plots stored in paperdata/"


# Synthetic Evaluation - UNI 
echo "== Synthetic Evaluation - UNIFORM Benchmark =="

python3 generate.py --bench UNI --tasks 5 --sets 100 --startid 0 EvalUNI/chains05.jsonl --maxHTp 350
python3 generate.py --bench UNI --tasks 20 --sets 100 --startid 1000 EvalUNI/chains20.jsonl --maxHTp 350
python3 generate.py --bench UNI --tasks 40 --sets 100 --startid 2000 EvalUNI/chains50.jsonl --maxHTp 350

echo "Chains stored in EvalUNI/chains<tasks-per-set>.jsonl"

for i in {0..2}; do
    python3 analysis.py EvalUNI/chains05.jsonl --info --relative-bound 0.95 --no-print --output EvalUNI/results05_${i}.jsonl
done

for i in {0..2}; do
    python3 analysis.py EvalUNI/chains20.jsonl --info --relative-bound 0.95 --no-print --output EvalUNI/results20_${i}.jsonl
done

for i in {0..2}; do
    python3 analysis.py EvalUNI/chains50.jsonl --info --relative-bound 0.95 --no-print --output EvalUNI/results50_${i}.jsonl
done

echo "Analysis stored in EvalUNI/results<tasks-per-set>.jsonl"

python plot.py -o paperdata/UNI_runtime.png paperdata/UNI_anchors.png -c 3 EvalUNI/results50_{0..2}.jsonl  EvalUNI/results20_{0..2}.jsonl  EvalUNI/results05_{0..2}.jsonl

echo "Plots stored in paperdata/"


