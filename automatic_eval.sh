NUM_ITERATIONS=2  # number of runs for the time measurements of the synthetic evaluation
REPEATING_RUNS=$((NUM_ITERATIONS - 1))
TASKSETS_PER_CONFIG=100 # number of tasksets per configuration for the runtime evaluation (Change to: 1000)


# == Section A: Evaluation of Benchmarks ==
echo "== Evaluate Benchmarks =="

# = Our analysis
echo "= Run our analysis"
start_time=$(date +%s.%N)
python3 analysis.py chains/case_studies.jsonl --info --relative-bound 0.95 --no-print --output results/case_studies.jsonl
end_time=$(date +%s.%N)
elapsed=$(echo "$end_time - $start_time" | bc)
echo "Evaluation results stored in: results/case_studies.jsonl"

# Elapsed time
echo "- Total elapsed time for case studies: ${elapsed}s"
python3 -c "import json; total = sum(json.loads(line).get('analysis_time_sec', 0) for line in open('results/case_studies.jsonl')); print(f'- SUM analysis_time_sec: {total}')"

# Information about anchor points
python3 -c "import json; anchors = [json.loads(line).get('#AnchorsRT', []) for line in open('results/case_studies.jsonl')]; print('- Anchor points:', anchors); print('- SUM:', sum(anchors)); print('- #LEQ 3:', sum((a<=3 for a in anchors)), '/', len(anchors));"

# Create table for the paper
mkdir -p paperdata
python3 make_table.py results/case_studies.jsonl > paperdata/case_studies.tex
echo "Table of Case-Study results stored in: paperdata/case_studies.tex"

# Additional investigation of L = 80% of Max (used in evaluation)
python3 analysis.py chains/case_studies.jsonl --info --relative-bound 0.80 --no-print --output results/case_studies80.jsonl
echo "Evaluation results with L=80% of Max are stored in: results/case_studies80.jsonl"

# = SOTA analyses
echo "= Run SOTA analyses"
start_time=$(date +%s.%N)
python3 compare_methods.py chains/case_studies.jsonl results/case_studies_other.jsonl --no-print
end_time=$(date +%s.%N)
elapsed=$(echo "$end_time - $start_time" | bc)
echo "Evaluation results stored in: results/case_studies_other.jsonl"

# Elapsed time 
echo "- Total elapsed time for case studies: ${elapsed}s"
python3 -c "import json; total = sum(json.loads(line).get('BW_TIME', 0) for line in open('results/case_studies_other.jsonl')); print(f'- SUM BW_TIME: {total}')"
python3 -c "import json; total = sum(json.loads(line).get('FW_TIME', 0) for line in open('results/case_studies_other.jsonl')); print(f'- SUM FW_TIME: {total}')"
python3 -c "import json; total = sum(json.loads(line).get('P_TIME', 0) for line in open('results/case_studies_other.jsonl')); print(f'- SUM P_TIME: {total}')"

# Check that results match
echo "= Check that results match"
python3 -c "import json; results_our = [json.loads(line).get('MaxRT') for line in open('results/case_studies.jsonl')]; results_other = [json.loads(line).get('FW_MRT') for line in open('results/case_studies_other.jsonl')]; print(f'- FW differs in {sum([res1 != res2 for res1, res2 in zip(results_our, results_other)])} cases')"

python3 -c "import json; results_our = [json.loads(line).get('MaxRT') for line in open('results/case_studies.jsonl')]; results_other = [json.loads(line).get('P_MRT') for line in open('results/case_studies_other.jsonl')]; print(f'- Partitioned differs in {sum([res1 != res2 for res1, res2 in zip(results_our, results_other)])} cases')"

python3 -c "import json; results_our = [json.loads(line).get('Reac') for line in open('results/case_studies.jsonl')]; results_other = [json.loads(line).get('BW_Reac') for line in open('results/case_studies_other.jsonl')]; print(f'- BW differs in {sum([res1 != res2 for res1, res2 in zip(results_our, results_other)])} cases')"


# == Section B: Runtime Comparison ==
echo " "
echo "== Runtime Comparison =="

# = Part 1: WATERS Benchmark
echo "= WATERS Benchmark"

python3 generate.py --bench WATERS --tasks 5 --sets $TASKSETS_PER_CONFIG RuntimeComparison/WATERS/chains05.jsonl
python3 generate.py --bench WATERS --tasks 20 --sets $TASKSETS_PER_CONFIG RuntimeComparison/WATERS/chains20.jsonl
python3 generate.py --bench WATERS --tasks 50 --sets $TASKSETS_PER_CONFIG RuntimeComparison/WATERS/chains50.jsonl
echo "Chains stored in RuntimeComparison/WATERS/chains<tasks-per-set>.jsonl"

for i in $(seq 0 $((NUM_ITERATIONS - 1))); do
    python3 analysis.py RuntimeComparison/WATERS/chains05.jsonl --info --relative-bound 0.95 --no-print --output RuntimeComparison/WATERS/Our_results05_${i}.jsonl
    python3 analysis.py RuntimeComparison/WATERS/chains20.jsonl --info --relative-bound 0.95 --no-print --output RuntimeComparison/WATERS/Our_results20_${i}.jsonl
    python3 analysis.py RuntimeComparison/WATERS/chains50.jsonl --info --relative-bound 0.95 --no-print --output RuntimeComparison/WATERS/Our_results50_${i}.jsonl

    python3 compare_methods.py RuntimeComparison/WATERS/chains05.jsonl RuntimeComparison/WATERS/Other_results05_${i}.jsonl --no-print
    python3 compare_methods.py RuntimeComparison/WATERS/chains20.jsonl RuntimeComparison/WATERS/Other_results20_${i}.jsonl --no-print
    python3 compare_methods.py RuntimeComparison/WATERS/chains50.jsonl RuntimeComparison/WATERS/Other_results50_${i}.jsonl --no-print
done
echo "Runtime results stored in RuntimeComparison/WATERS"

eval python plot_runtimecomparison.py -o RuntimeComparison/WATERS/plot05.png -i FW FW_TIME RuntimeComparison/WATERS/Other_results05_{0..$REPEATING_RUNS}.jsonl -i BW BW_TIME RuntimeComparison/WATERS/Other_results05_{0..$REPEATING_RUNS}.jsonl -i P P_TIME RuntimeComparison/WATERS/Other_results05_{0..$REPEATING_RUNS}.jsonl -i Our analysis_time_sec RuntimeComparison/WATERS/Our_results05_{0..$REPEATING_RUNS}.jsonl

eval python plot_runtimecomparison.py -o RuntimeComparison/WATERS/plot20.png -i FW FW_TIME RuntimeComparison/WATERS/Other_results20_{0..$REPEATING_RUNS}.jsonl -i BW BW_TIME RuntimeComparison/WATERS/Other_results20_{0..$REPEATING_RUNS}.jsonl -i P P_TIME RuntimeComparison/WATERS/Other_results20_{0..$REPEATING_RUNS}.jsonl -i Our analysis_time_sec RuntimeComparison/WATERS/Our_results20_{0..$REPEATING_RUNS}.jsonl

eval python plot_runtimecomparison.py -o RuntimeComparison/WATERS/plot50.png -i FW FW_TIME RuntimeComparison/WATERS/Other_results50_{0..$REPEATING_RUNS}.jsonl -i BW BW_TIME RuntimeComparison/WATERS/Other_results50_{0..$REPEATING_RUNS}.jsonl -i P P_TIME RuntimeComparison/WATERS/Other_results50_{0..$REPEATING_RUNS}.jsonl -i Our analysis_time_sec RuntimeComparison/WATERS/Our_results50_{0..$REPEATING_RUNS}.jsonl
echo "Plots stored in RuntimeComparison/WATERS"

# Check that results match
echo "-> Check that results match"
python3 -c "import json; results_our = [json.loads(line).get('MaxRT') for line in open('RuntimeComparison/WATERS/Our_results05_0.jsonl')] + [json.loads(line).get('MaxRT') for line in open('RuntimeComparison/WATERS/Our_results20_0.jsonl')] + [json.loads(line).get('MaxRT') for line in open('RuntimeComparison/WATERS/Our_results50_0.jsonl')]; results_other = [json.loads(line).get('FW_MRT') for line in open('RuntimeComparison/WATERS/Other_results05_0.jsonl')] + [json.loads(line).get('FW_MRT') for line in open('RuntimeComparison/WATERS/Other_results20_0.jsonl')] + [json.loads(line).get('FW_MRT') for line in open('RuntimeComparison/WATERS/Other_results50_0.jsonl')]; print(f'- FW differs in {sum([res1 != res2 for res1, res2 in zip(results_our, results_other)])} cases')"

python3 -c "import json; results_our = [json.loads(line).get('MaxRT') for line in open('RuntimeComparison/WATERS/Our_results05_0.jsonl')] + [json.loads(line).get('MaxRT') for line in open('RuntimeComparison/WATERS/Our_results20_0.jsonl')] + [json.loads(line).get('MaxRT') for line in open('RuntimeComparison/WATERS/Our_results50_0.jsonl')]; results_other = [json.loads(line).get('P_MRT') for line in open('RuntimeComparison/WATERS/Other_results05_0.jsonl')] + [json.loads(line).get('P_MRT') for line in open('RuntimeComparison/WATERS/Other_results20_0.jsonl')] + [json.loads(line).get('P_MRT') for line in open('RuntimeComparison/WATERS/Other_results50_0.jsonl')]; print(f'- Partitioned differs in {sum([res1 != res2 for res1, res2 in zip(results_our, results_other)])} cases')"

python3 -c "import json; results_our = [json.loads(line).get('Reac') for line in open('RuntimeComparison/WATERS/Our_results05_0.jsonl')] + [json.loads(line).get('Reac') for line in open('RuntimeComparison/WATERS/Our_results20_0.jsonl')] + [json.loads(line).get('Reac') for line in open('RuntimeComparison/WATERS/Our_results50_0.jsonl')]; results_other = [json.loads(line).get('BW_Reac') for line in open('RuntimeComparison/WATERS/Other_results05_0.jsonl')] + [json.loads(line).get('BW_Reac') for line in open('RuntimeComparison/WATERS/Other_results20_0.jsonl')] + [json.loads(line).get('BW_Reac') for line in open('RuntimeComparison/WATERS/Other_results50_0.jsonl')]; print(f'- BW differs in {sum([res1 != res2 for res1, res2 in zip(results_our, results_other)])} cases')"


# = Part 2: UNIFORM Benchmark
echo "= UNIFORM Benchmark"

python3 generate.py --bench UNI --tasks 5 --sets $TASKSETS_PER_CONFIG RuntimeComparison/UNI/chains05.jsonl --maxH 1000000
python3 generate.py --bench UNI --tasks 20 --sets $TASKSETS_PER_CONFIG RuntimeComparison/UNI/chains20.jsonl --maxH 1000000
python3 generate.py --bench UNI --tasks 50 --sets $TASKSETS_PER_CONFIG RuntimeComparison/UNI/chains50.jsonl --maxH 1000000
echo "Chains stored in RuntimeComparison/UNI/chains<tasks-per-set>.jsonl"

for i in $(seq 0 $((NUM_ITERATIONS - 1))); do
    python3 analysis.py RuntimeComparison/UNI/chains05.jsonl --info --relative-bound 0.95 --no-print --output RuntimeComparison/UNI/Our_results05_${i}.jsonl
    python3 analysis.py RuntimeComparison/UNI/chains20.jsonl --info --relative-bound 0.95 --no-print --output RuntimeComparison/UNI/Our_results20_${i}.jsonl
    python3 analysis.py RuntimeComparison/UNI/chains50.jsonl --info --relative-bound 0.95 --no-print --output RuntimeComparison/UNI/Our_results50_${i}.jsonl

    python3 compare_methods.py RuntimeComparison/UNI/chains05.jsonl RuntimeComparison/UNI/Other_results05_${i}.jsonl --no-print
    python3 compare_methods.py RuntimeComparison/UNI/chains20.jsonl RuntimeComparison/UNI/Other_results20_${i}.jsonl --no-print
    python3 compare_methods.py RuntimeComparison/UNI/chains50.jsonl RuntimeComparison/UNI/Other_results50_${i}.jsonl --no-print
done

echo "Runtime results stored in RuntimeComparison/UNI"

eval python plot_runtimecomparison.py -o RuntimeComparison/UNI/plot05.png -i FW FW_TIME RuntimeComparison/UNI/Other_results05_{0..$REPEATING_RUNS}.jsonl -i BW BW_TIME RuntimeComparison/UNI/Other_results05_{0..$REPEATING_RUNS}.jsonl -i P P_TIME RuntimeComparison/UNI/Other_results05_{0..$REPEATING_RUNS}.jsonl -i Our analysis_time_sec RuntimeComparison/UNI/Our_results05_{0..$REPEATING_RUNS}.jsonl

eval python plot_runtimecomparison.py -o RuntimeComparison/UNI/plot20.png -i FW FW_TIME RuntimeComparison/UNI/Other_results20_{0..$REPEATING_RUNS}.jsonl -i BW BW_TIME RuntimeComparison/UNI/Other_results20_{0..$REPEATING_RUNS}.jsonl -i P P_TIME RuntimeComparison/UNI/Other_results20_{0..$REPEATING_RUNS}.jsonl -i Our analysis_time_sec RuntimeComparison/UNI/Our_results20_{0..$REPEATING_RUNS}.jsonl

eval python plot_runtimecomparison.py -o RuntimeComparison/UNI/plot50.png -i FW FW_TIME RuntimeComparison/UNI/Other_results50_{0..$REPEATING_RUNS}.jsonl -i BW BW_TIME RuntimeComparison/UNI/Other_results50_{0..$REPEATING_RUNS}.jsonl -i P P_TIME RuntimeComparison/UNI/Other_results50_{0..$REPEATING_RUNS}.jsonl -i Our analysis_time_sec RuntimeComparison/UNI/Our_results50_{0..$REPEATING_RUNS}.jsonl
echo "Plots stored in RuntimeComparison/UNI"


# Check that results match
echo "-> Check that results match"
python3 -c "import json; results_our = [json.loads(line).get('MaxRT') for line in open('RuntimeComparison/UNI/Our_results05_0.jsonl')] + [json.loads(line).get('MaxRT') for line in open('RuntimeComparison/UNI/Our_results20_0.jsonl')] + [json.loads(line).get('MaxRT') for line in open('RuntimeComparison/UNI/Our_results50_0.jsonl')]; results_other = [json.loads(line).get('FW_MRT') for line in open('RuntimeComparison/UNI/Other_results05_0.jsonl')] + [json.loads(line).get('FW_MRT') for line in open('RuntimeComparison/UNI/Other_results20_0.jsonl')] + [json.loads(line).get('FW_MRT') for line in open('RuntimeComparison/UNI/Other_results50_0.jsonl')]; print(f'- FW differs in {sum([res1 != res2 for res1, res2 in zip(results_our, results_other)])} cases')"

python3 -c "import json; results_our = [json.loads(line).get('MaxRT') for line in open('RuntimeComparison/UNI/Our_results05_0.jsonl')] + [json.loads(line).get('MaxRT') for line in open('RuntimeComparison/UNI/Our_results20_0.jsonl')] + [json.loads(line).get('MaxRT') for line in open('RuntimeComparison/UNI/Our_results50_0.jsonl')]; results_other = [json.loads(line).get('P_MRT') for line in open('RuntimeComparison/UNI/Other_results05_0.jsonl')] + [json.loads(line).get('P_MRT') for line in open('RuntimeComparison/UNI/Other_results20_0.jsonl')] + [json.loads(line).get('P_MRT') for line in open('RuntimeComparison/UNI/Other_results50_0.jsonl')]; print(f'- Partitioned differs in {sum([res1 != res2 for res1, res2 in zip(results_our, results_other)])} cases')"

python3 -c "import json; results_our = [json.loads(line).get('Reac') for line in open('RuntimeComparison/UNI/Our_results05_0.jsonl')] + [json.loads(line).get('Reac') for line in open('RuntimeComparison/UNI/Our_results20_0.jsonl')] + [json.loads(line).get('Reac') for line in open('RuntimeComparison/UNI/Our_results50_0.jsonl')]; results_other = [json.loads(line).get('BW_Reac') for line in open('RuntimeComparison/UNI/Other_results05_0.jsonl')] + [json.loads(line).get('BW_Reac') for line in open('RuntimeComparison/UNI/Other_results20_0.jsonl')] + [json.loads(line).get('BW_Reac') for line in open('RuntimeComparison/UNI/Other_results50_0.jsonl')]; print(f'- BW differs in {sum([res1 != res2 for res1, res2 in zip(results_our, results_other)])} cases')"



# == Section C: Controlling number of Anchor Points ==
echo " "
echo "== Controlling Anchor Points =="

# = Part 1: WATERS Benchmark
echo "= WATERS Benchmark"
start_time=$(date +%s.%N)

python3 generate.py --bench WATERS --tasks 5 --sets $TASKSETS_PER_CONFIG --startid 0 Relation/WATERS/chains05.jsonl
python3 generate.py --bench WATERS --tasks 20 --sets $TASKSETS_PER_CONFIG --startid 10000 Relation/WATERS/chains20.jsonl 
python3 generate.py --bench WATERS --tasks 50 --sets $TASKSETS_PER_CONFIG --startid 20000 Relation/WATERS/chains50.jsonl
# Note: the steps of startid must be larger than the $TASKSETS_PER_CONFIG variable

echo "Chains stored in Relation/WATERS/chains<tasks-per-set>.jsonl"

for i in $(seq 0 $((NUM_ITERATIONS - 1))); do
    python3 analysis.py Relation/WATERS/chains05.jsonl --info --relative-bound 0.95 --no-print --output Relation/WATERS/results05_${i}.jsonl
done

for i in $(seq 0 $((NUM_ITERATIONS - 1))); do
    python3 analysis.py Relation/WATERS/chains20.jsonl --info --relative-bound 0.95 --no-print --output Relation/WATERS/results20_${i}.jsonl
done

for i in $(seq 0 $((NUM_ITERATIONS - 1))); do
    python3 analysis.py Relation/WATERS/chains50.jsonl --info --relative-bound 0.95 --no-print --output Relation/WATERS/results50_${i}.jsonl
done

echo "Analysis stored in Relation/WATERS/results<tasks-per-set>.jsonl"

eval python plot.py -o paperdata/WATERS_runtime.png paperdata/WATERS_anchors.png -c $NUM_ITERATIONS Relation/WATERS/results50_{0..$REPEATING_RUNS}.jsonl  Relation/WATERS/results20_{0..$REPEATING_RUNS}.jsonl  Relation/WATERS/results05_{0..$REPEATING_RUNS}.jsonl

echo "Plots stored in paperdata/"

end_time=$(date +%s.%N)
elapsed=$(echo "$end_time - $start_time" | bc)
echo "- Total elapsed time for synthetic evaluation with WATERS benchmark: ${elapsed}s"


# = Part 2: UNIFORM Benchmark
echo "= UNIFORM Benchmark"
start_time=$(date +%s.%N)

python3 generate.py --bench UNI --tasks 5 --sets 1000 --startid 0 Relation/UNI/chains05.jsonl --maxHTp 350 --maxH 1000000
python3 generate.py --bench UNI --tasks 20 --sets 1000 --startid 10000 Relation/UNI/chains20.jsonl --maxHTp 350 --maxH 1000000
python3 generate.py --bench UNI --tasks 50 --sets 1000 --startid 20000 Relation/UNI/chains50.jsonl --maxHTp 350 --maxH 1000000

echo "Chains stored in Relation/UNI/chains<tasks-per-set>.jsonl"

for i in $(seq 0 $((NUM_ITERATIONS - 1))); do
    python3 analysis.py Relation/UNI/chains05.jsonl --info --relative-bound 0.95 --no-print --output Relation/UNI/results05_${i}.jsonl
done

for i in $(seq 0 $((NUM_ITERATIONS - 1))); do
    python3 analysis.py Relation/UNI/chains20.jsonl --info --relative-bound 0.95 --no-print --output Relation/UNI/results20_${i}.jsonl
done


for i in $(seq 0 $((NUM_ITERATIONS - 1))); do
    python3 analysis.py Relation/UNI/chains50.jsonl --info --relative-bound 0.95 --no-print --output Relation/UNI/results50_${i}.jsonl
done

echo "Analysis stored in Relation/UNI/results<tasks-per-set>.jsonl"

eval python plot.py -o paperdata/UNI_runtime.png paperdata/UNI_anchors.png -c $NUM_ITERATIONS Relation/UNI/results50_{0..$REPEATING_RUNS}.jsonl  Relation/UNI/results20_{0..$REPEATING_RUNS}.jsonl  Relation/UNI/results05_{0..$REPEATING_RUNS}.jsonl

echo "Plots stored in paperdata/"

end_time=$(date +%s.%N)
elapsed=$(echo "$end_time - $start_time" | bc)
echo "- Total elapsed time for synthetic evaluation with UNIFORM benchmark: ${elapsed}s"
