NUM_ITERATIONS=50  # number of runs for the time measurements of the synthetic evaluation
TASKSETS_PER_CONFIG=1000 # number of tasksets per configuration for the runtime evaluation (Change to: 1000)
PARALLELIZE=true

if [ "$1" = "0" ]; then
    echo "<< Running a simplified version of the experiment >>"
    echo " "
    NUM_ITERATIONS=2
    TASKSETS_PER_CONFIG=10
    PARALLELIZE=false
fi

# Set help variables
REPEATING_RUNS=$((NUM_ITERATIONS - 1))

# == Section A: Evaluation of Case Studies ==
echo "== Evaluate Case Studies =="

# = Our analysis
echo "= Run our analysis"
start_time=$(date +%s.%N)
python3 analysis.py chains/case_studies.jsonl --info --relative-bound 0.95 --no-print --output AutomaticEval/CaseStudies/results.jsonl
end_time=$(date +%s.%N)
elapsed=$(echo "$end_time - $start_time" | bc)
echo "Evaluation results stored in: AutomaticEval/CaseStudies/results.jsonl"

# Elapsed time
echo "- Total elapsed time for case studies: ${elapsed}s"
python3 -c "import json; total = sum(json.loads(line).get('analysis_time_sec', 0) for line in open('AutomaticEval/CaseStudies/results.jsonl')); print(f'- SUM analysis_time_sec: {total}')"

# Information about anchor points
python3 -c "import json; anchors = [json.loads(line).get('#AnchorsRT', []) for line in open('AutomaticEval/CaseStudies/results.jsonl')]; print('- Anchor points:', anchors); print('- SUM:', sum(anchors)); print('- #LEQ 3:', sum((a<=3 for a in anchors)), '/', len(anchors));"

# Create table for the paper
mkdir -p AutomaticEval/paperdata
python3 make_table.py AutomaticEval/CaseStudies/results.jsonl > AutomaticEval/paperdata/case_studies.tex
echo "Table of Case-Study results stored in: AutomaticEval/paperdata/case_studies.tex"

# Additional investigation of L = 80% of Max (used in evaluation)
python3 analysis.py chains/case_studies.jsonl --info --relative-bound 0.80 --no-print --output AutomaticEval/CaseStudies/results80.jsonl
echo "Evaluation results with L=80% of Max are stored in: AutomaticEval/CaseStudies/results80.jsonl"

# = SOTA analyses
echo "= Run SOTA analyses"
start_time=$(date +%s.%N)
python3 compare_methods.py chains/case_studies.jsonl AutomaticEval/CaseStudies/results_other.jsonl --no-print
end_time=$(date +%s.%N)
elapsed=$(echo "$end_time - $start_time" | bc)
echo "Evaluation results stored in: AutomaticEval/CaseStudies/results_other.jsonl"

# Elapsed time 
echo "- Total elapsed time for case studies: ${elapsed}s"
python3 -c "import json; total = sum(json.loads(line).get('BW_TIME', 0) for line in open('AutomaticEval/CaseStudies/results_other.jsonl')); print(f'- SUM BW_TIME: {total}')"
python3 -c "import json; total = sum(json.loads(line).get('FW_TIME', 0) for line in open('AutomaticEval/CaseStudies/results_other.jsonl')); print(f'- SUM FW_TIME: {total}')"
python3 -c "import json; total = sum(json.loads(line).get('P_TIME', 0) for line in open('AutomaticEval/CaseStudies/results_other.jsonl')); print(f'- SUM P_TIME: {total}')"

# Check that results match
echo "= Check that results match"
python3 -c "import json; results_our = [json.loads(line).get('MaxRT') for line in open('AutomaticEval/CaseStudies/results.jsonl')]; results_other = [json.loads(line).get('FW_MRT') for line in open('AutomaticEval/CaseStudies/results_other.jsonl')]; print(f'- FW differs in {sum([res1 != res2 for res1, res2 in zip(results_our, results_other)])} cases')"

python3 -c "import json; results_our = [json.loads(line).get('MaxRT') for line in open('AutomaticEval/CaseStudies/results.jsonl')]; results_other = [json.loads(line).get('P_MRT') for line in open('AutomaticEval/CaseStudies/results_other.jsonl')]; print(f'- Partitioned differs in {sum([res1 != res2 for res1, res2 in zip(results_our, results_other)])} cases')"

python3 -c "import json; results_our = [json.loads(line).get('Reac') for line in open('AutomaticEval/CaseStudies/results.jsonl')]; results_other = [json.loads(line).get('BW_Reac') for line in open('AutomaticEval/CaseStudies/results_other.jsonl')]; print(f'- BW differs in {sum([res1 != res2 for res1, res2 in zip(results_our, results_other)])} cases')"


# == Section B: Runtime Comparison ==
echo " "
echo "== Runtime Comparison =="

# = Part 1: WATERS Benchmark
echo "= WATERS Benchmark"

python3 generate.py --bench WATERS --tasks 5 --sets $TASKSETS_PER_CONFIG AutomaticEval/RuntimeComparison/WATERS/chains05.jsonl
python3 generate.py --bench WATERS --tasks 20 --sets $TASKSETS_PER_CONFIG AutomaticEval/RuntimeComparison/WATERS/chains20.jsonl
python3 generate.py --bench WATERS --tasks 50 --sets $TASKSETS_PER_CONFIG AutomaticEval/RuntimeComparison/WATERS/chains50.jsonl
echo "Chains stored in AutomaticEval/RuntimeComparison/WATERS/chains<tasks-per-set>.jsonl"

for i in $(seq 0 $((NUM_ITERATIONS - 1))); do
(
    python3 analysis.py AutomaticEval/RuntimeComparison/WATERS/chains05.jsonl --info --relative-bound 0.95 --no-print --output AutomaticEval/RuntimeComparison/WATERS/Our_results05_${i}.jsonl
    python3 analysis.py AutomaticEval/RuntimeComparison/WATERS/chains20.jsonl --info --relative-bound 0.95 --no-print --output AutomaticEval/RuntimeComparison/WATERS/Our_results20_${i}.jsonl
    python3 analysis.py AutomaticEval/RuntimeComparison/WATERS/chains50.jsonl --info --relative-bound 0.95 --no-print --output AutomaticEval/RuntimeComparison/WATERS/Our_results50_${i}.jsonl

    python3 compare_methods.py AutomaticEval/RuntimeComparison/WATERS/chains05.jsonl AutomaticEval/RuntimeComparison/WATERS/Other_results05_${i}.jsonl --no-print
    python3 compare_methods.py AutomaticEval/RuntimeComparison/WATERS/chains20.jsonl AutomaticEval/RuntimeComparison/WATERS/Other_results20_${i}.jsonl --no-print
    python3 compare_methods.py AutomaticEval/RuntimeComparison/WATERS/chains50.jsonl AutomaticEval/RuntimeComparison/WATERS/Other_results50_${i}.jsonl --no-print
) &
    if [ $PARALLELIZE = false ]; then
        wait
    fi
done
wait
echo "Runtime results stored in AutomaticEval/RuntimeComparison/WATERS"

eval python plot_runtimecomparison.py -o AutomaticEval/paperdata/runtime_comparison_waters_05.png --stat AutomaticEval/paperdata/runtime_comparison_waters_05.json -i FW FW_TIME AutomaticEval/RuntimeComparison/WATERS/Other_results05_{0..$REPEATING_RUNS}.jsonl -i BW BW_TIME AutomaticEval/RuntimeComparison/WATERS/Other_results05_{0..$REPEATING_RUNS}.jsonl -i P P_TIME AutomaticEval/RuntimeComparison/WATERS/Other_results05_{0..$REPEATING_RUNS}.jsonl -i Our analysis_time_sec AutomaticEval/RuntimeComparison/WATERS/Our_results05_{0..$REPEATING_RUNS}.jsonl

eval python plot_runtimecomparison.py -o AutomaticEval/paperdata/runtime_comparison_waters_20.png --stat AutomaticEval/paperdata/runtime_comparison_waters_20.json -i FW FW_TIME AutomaticEval/RuntimeComparison/WATERS/Other_results20_{0..$REPEATING_RUNS}.jsonl -i BW BW_TIME AutomaticEval/RuntimeComparison/WATERS/Other_results20_{0..$REPEATING_RUNS}.jsonl -i P P_TIME AutomaticEval/RuntimeComparison/WATERS/Other_results20_{0..$REPEATING_RUNS}.jsonl -i Our analysis_time_sec AutomaticEval/RuntimeComparison/WATERS/Our_results20_{0..$REPEATING_RUNS}.jsonl

eval python plot_runtimecomparison.py -o AutomaticEval/paperdata/runtime_comparison_waters_50.png --stat AutomaticEval/paperdata/runtime_comparison_waters_50.json -i FW FW_TIME AutomaticEval/RuntimeComparison/WATERS/Other_results50_{0..$REPEATING_RUNS}.jsonl -i BW BW_TIME AutomaticEval/RuntimeComparison/WATERS/Other_results50_{0..$REPEATING_RUNS}.jsonl -i P P_TIME AutomaticEval/RuntimeComparison/WATERS/Other_results50_{0..$REPEATING_RUNS}.jsonl -i Our analysis_time_sec AutomaticEval/RuntimeComparison/WATERS/Our_results50_{0..$REPEATING_RUNS}.jsonl
echo "Plots stored in AutomaticEval/RuntimeComparison/WATERS"

# Check that results match
echo "-> Check that results match"
python3 -c "import json; results_our = [json.loads(line).get('MaxRT') for line in open('AutomaticEval/RuntimeComparison/WATERS/Our_results05_0.jsonl')] + [json.loads(line).get('MaxRT') for line in open('AutomaticEval/RuntimeComparison/WATERS/Our_results20_0.jsonl')] + [json.loads(line).get('MaxRT') for line in open('AutomaticEval/RuntimeComparison/WATERS/Our_results50_0.jsonl')]; results_other = [json.loads(line).get('FW_MRT') for line in open('AutomaticEval/RuntimeComparison/WATERS/Other_results05_0.jsonl')] + [json.loads(line).get('FW_MRT') for line in open('AutomaticEval/RuntimeComparison/WATERS/Other_results20_0.jsonl')] + [json.loads(line).get('FW_MRT') for line in open('AutomaticEval/RuntimeComparison/WATERS/Other_results50_0.jsonl')]; print(f'- FW differs in {sum([res1 != res2 for res1, res2 in zip(results_our, results_other)])} cases')"

python3 -c "import json; results_our = [json.loads(line).get('MaxRT') for line in open('AutomaticEval/RuntimeComparison/WATERS/Our_results05_0.jsonl')] + [json.loads(line).get('MaxRT') for line in open('AutomaticEval/RuntimeComparison/WATERS/Our_results20_0.jsonl')] + [json.loads(line).get('MaxRT') for line in open('AutomaticEval/RuntimeComparison/WATERS/Our_results50_0.jsonl')]; results_other = [json.loads(line).get('P_MRT') for line in open('AutomaticEval/RuntimeComparison/WATERS/Other_results05_0.jsonl')] + [json.loads(line).get('P_MRT') for line in open('AutomaticEval/RuntimeComparison/WATERS/Other_results20_0.jsonl')] + [json.loads(line).get('P_MRT') for line in open('AutomaticEval/RuntimeComparison/WATERS/Other_results50_0.jsonl')]; print(f'- Partitioned differs in {sum([res1 != res2 for res1, res2 in zip(results_our, results_other)])} cases')"

python3 -c "import json; results_our = [json.loads(line).get('Reac') for line in open('AutomaticEval/RuntimeComparison/WATERS/Our_results05_0.jsonl')] + [json.loads(line).get('Reac') for line in open('AutomaticEval/RuntimeComparison/WATERS/Our_results20_0.jsonl')] + [json.loads(line).get('Reac') for line in open('AutomaticEval/RuntimeComparison/WATERS/Our_results50_0.jsonl')]; results_other = [json.loads(line).get('BW_Reac') for line in open('AutomaticEval/RuntimeComparison/WATERS/Other_results05_0.jsonl')] + [json.loads(line).get('BW_Reac') for line in open('AutomaticEval/RuntimeComparison/WATERS/Other_results20_0.jsonl')] + [json.loads(line).get('BW_Reac') for line in open('AutomaticEval/RuntimeComparison/WATERS/Other_results50_0.jsonl')]; print(f'- BW differs in {sum([res1 != res2 for res1, res2 in zip(results_our, results_other)])} cases')"


# = Part 2: UNIFORM Benchmark
echo "= UNIFORM Benchmark"

python3 generate.py --bench UNI --tasks 5 --sets $TASKSETS_PER_CONFIG AutomaticEval/RuntimeComparison/UNI/chains05.jsonl --maxH 1000000
python3 generate.py --bench UNI --tasks 20 --sets $TASKSETS_PER_CONFIG AutomaticEval/RuntimeComparison/UNI/chains20.jsonl --maxH 1000000
python3 generate.py --bench UNI --tasks 50 --sets $TASKSETS_PER_CONFIG AutomaticEval/RuntimeComparison/UNI/chains50.jsonl --maxH 1000000
echo "Chains stored in AutomaticEval/RuntimeComparison/UNI/chains<tasks-per-set>.jsonl"

for i in $(seq 0 $((NUM_ITERATIONS - 1))); do
(
    python3 analysis.py AutomaticEval/RuntimeComparison/UNI/chains05.jsonl --info --relative-bound 0.95 --no-print --output AutomaticEval/RuntimeComparison/UNI/Our_results05_${i}.jsonl
    python3 analysis.py AutomaticEval/RuntimeComparison/UNI/chains20.jsonl --info --relative-bound 0.95 --no-print --output AutomaticEval/RuntimeComparison/UNI/Our_results20_${i}.jsonl
    python3 analysis.py AutomaticEval/RuntimeComparison/UNI/chains50.jsonl --info --relative-bound 0.95 --no-print --output AutomaticEval/RuntimeComparison/UNI/Our_results50_${i}.jsonl

    python3 compare_methods.py AutomaticEval/RuntimeComparison/UNI/chains05.jsonl AutomaticEval/RuntimeComparison/UNI/Other_results05_${i}.jsonl --no-print
    python3 compare_methods.py AutomaticEval/RuntimeComparison/UNI/chains20.jsonl AutomaticEval/RuntimeComparison/UNI/Other_results20_${i}.jsonl --no-print
    python3 compare_methods.py AutomaticEval/RuntimeComparison/UNI/chains50.jsonl AutomaticEval/RuntimeComparison/UNI/Other_results50_${i}.jsonl --no-print
) & 
    if [ $PARALLELIZE = false ]; then
        wait
    fi
done
wait

echo "Runtime results stored in AutomaticEval/RuntimeComparison/UNI"

eval python plot_runtimecomparison.py -o AutomaticEval/paperdata/runtime_comparison_uni_05.png --stat AutomaticEval/paperdata/runtime_comparison_uni_05.json -i FW FW_TIME AutomaticEval/RuntimeComparison/UNI/Other_results05_{0..$REPEATING_RUNS}.jsonl -i BW BW_TIME AutomaticEval/RuntimeComparison/UNI/Other_results05_{0..$REPEATING_RUNS}.jsonl -i P P_TIME AutomaticEval/RuntimeComparison/UNI/Other_results05_{0..$REPEATING_RUNS}.jsonl -i Our analysis_time_sec AutomaticEval/RuntimeComparison/UNI/Our_results05_{0..$REPEATING_RUNS}.jsonl

eval python plot_runtimecomparison.py -o AutomaticEval/paperdata/runtime_comparison_uni_20.png --stat AutomaticEval/paperdata/runtime_comparison_uni_20.json -i FW FW_TIME AutomaticEval/RuntimeComparison/UNI/Other_results20_{0..$REPEATING_RUNS}.jsonl -i BW BW_TIME AutomaticEval/RuntimeComparison/UNI/Other_results20_{0..$REPEATING_RUNS}.jsonl -i P P_TIME AutomaticEval/RuntimeComparison/UNI/Other_results20_{0..$REPEATING_RUNS}.jsonl -i Our analysis_time_sec AutomaticEval/RuntimeComparison/UNI/Our_results20_{0..$REPEATING_RUNS}.jsonl

eval python plot_runtimecomparison.py -o AutomaticEval/paperdata/runtime_comparison_uni_50.png --stat AutomaticEval/paperdata/runtime_comparison_uni_50.json -i FW FW_TIME AutomaticEval/RuntimeComparison/UNI/Other_results50_{0..$REPEATING_RUNS}.jsonl -i BW BW_TIME AutomaticEval/RuntimeComparison/UNI/Other_results50_{0..$REPEATING_RUNS}.jsonl -i P P_TIME AutomaticEval/RuntimeComparison/UNI/Other_results50_{0..$REPEATING_RUNS}.jsonl -i Our analysis_time_sec AutomaticEval/RuntimeComparison/UNI/Our_results50_{0..$REPEATING_RUNS}.jsonl
echo "Plots stored in AutomaticEval/RuntimeComparison/UNI"


# Check that results match
echo "-> Check that results match"
python3 -c "import json; results_our = [json.loads(line).get('MaxRT') for line in open('AutomaticEval/RuntimeComparison/UNI/Our_results05_0.jsonl')] + [json.loads(line).get('MaxRT') for line in open('AutomaticEval/RuntimeComparison/UNI/Our_results20_0.jsonl')] + [json.loads(line).get('MaxRT') for line in open('AutomaticEval/RuntimeComparison/UNI/Our_results50_0.jsonl')]; results_other = [json.loads(line).get('FW_MRT') for line in open('AutomaticEval/RuntimeComparison/UNI/Other_results05_0.jsonl')] + [json.loads(line).get('FW_MRT') for line in open('AutomaticEval/RuntimeComparison/UNI/Other_results20_0.jsonl')] + [json.loads(line).get('FW_MRT') for line in open('AutomaticEval/RuntimeComparison/UNI/Other_results50_0.jsonl')]; print(f'- FW differs in {sum([res1 != res2 for res1, res2 in zip(results_our, results_other)])} cases')"

python3 -c "import json; results_our = [json.loads(line).get('MaxRT') for line in open('AutomaticEval/RuntimeComparison/UNI/Our_results05_0.jsonl')] + [json.loads(line).get('MaxRT') for line in open('AutomaticEval/RuntimeComparison/UNI/Our_results20_0.jsonl')] + [json.loads(line).get('MaxRT') for line in open('AutomaticEval/RuntimeComparison/UNI/Our_results50_0.jsonl')]; results_other = [json.loads(line).get('P_MRT') for line in open('AutomaticEval/RuntimeComparison/UNI/Other_results05_0.jsonl')] + [json.loads(line).get('P_MRT') for line in open('AutomaticEval/RuntimeComparison/UNI/Other_results20_0.jsonl')] + [json.loads(line).get('P_MRT') for line in open('AutomaticEval/RuntimeComparison/UNI/Other_results50_0.jsonl')]; print(f'- Partitioned differs in {sum([res1 != res2 for res1, res2 in zip(results_our, results_other)])} cases')"

python3 -c "import json; results_our = [json.loads(line).get('Reac') for line in open('AutomaticEval/RuntimeComparison/UNI/Our_results05_0.jsonl')] + [json.loads(line).get('Reac') for line in open('AutomaticEval/RuntimeComparison/UNI/Our_results20_0.jsonl')] + [json.loads(line).get('Reac') for line in open('AutomaticEval/RuntimeComparison/UNI/Our_results50_0.jsonl')]; results_other = [json.loads(line).get('BW_Reac') for line in open('AutomaticEval/RuntimeComparison/UNI/Other_results05_0.jsonl')] + [json.loads(line).get('BW_Reac') for line in open('AutomaticEval/RuntimeComparison/UNI/Other_results20_0.jsonl')] + [json.loads(line).get('BW_Reac') for line in open('AutomaticEval/RuntimeComparison/UNI/Other_results50_0.jsonl')]; print(f'- BW differs in {sum([res1 != res2 for res1, res2 in zip(results_our, results_other)])} cases')"



# == Section C: Controlling number of Anchor Points ==
echo " "
echo "== Controlling Anchor Points =="

# = Part 1: WATERS Benchmark
echo "= WATERS Benchmark"
start_time=$(date +%s.%N)

python3 generate.py --bench WATERS --tasks 5 --sets $TASKSETS_PER_CONFIG --startid 0 AutomaticEval/Relation/WATERS/chains05.jsonl
python3 generate.py --bench WATERS --tasks 20 --sets $TASKSETS_PER_CONFIG --startid 10000 AutomaticEval/Relation/WATERS/chains20.jsonl 
python3 generate.py --bench WATERS --tasks 50 --sets $TASKSETS_PER_CONFIG --startid 20000 AutomaticEval/Relation/WATERS/chains50.jsonl
# Note: the steps of startid must be larger than the $TASKSETS_PER_CONFIG variable

echo "Chains stored in AutomaticEval/Relation/WATERS/chains<tasks-per-set>.jsonl"

for i in $(seq 0 $((NUM_ITERATIONS - 1))); do
(
    python3 analysis.py AutomaticEval/Relation/WATERS/chains05.jsonl --info --relative-bound 0.95 --no-print --output AutomaticEval/Relation/WATERS/results05_${i}.jsonl
) &
    if [ $PARALLELIZE = false ]; then
        wait
    fi
done
wait

for i in $(seq 0 $((NUM_ITERATIONS - 1))); do
(
    python3 analysis.py AutomaticEval/Relation/WATERS/chains20.jsonl --info --relative-bound 0.95 --no-print --output AutomaticEval/Relation/WATERS/results20_${i}.jsonl
) &
    if [ $PARALLELIZE = false ]; then
        wait
    fi
done
wait

for i in $(seq 0 $((NUM_ITERATIONS - 1))); do
(
    python3 analysis.py AutomaticEval/Relation/WATERS/chains50.jsonl --info --relative-bound 0.95 --no-print --output AutomaticEval/Relation/WATERS/results50_${i}.jsonl
) &
    if [ $PARALLELIZE = false ]; then
        wait
    fi
done
wait

echo "Analysis stored in AutomaticEval/Relation/WATERS/results<tasks-per-set>.jsonl"

eval python plot.py -o AutomaticEval/paperdata/WATERS_runtime.png AutomaticEval/paperdata/WATERS_anchors.png -c $NUM_ITERATIONS AutomaticEval/Relation/WATERS/results50_{0..$REPEATING_RUNS}.jsonl  AutomaticEval/Relation/WATERS/results20_{0..$REPEATING_RUNS}.jsonl  AutomaticEval/Relation/WATERS/results05_{0..$REPEATING_RUNS}.jsonl

echo "Plots stored in AutomaticEval/paperdata/"

end_time=$(date +%s.%N)
elapsed=$(echo "$end_time - $start_time" | bc)
echo "- Total elapsed time for synthetic evaluation with WATERS benchmark: ${elapsed}s"


# = Part 2: UNIFORM Benchmark
echo "= UNIFORM Benchmark"
start_time=$(date +%s.%N)

python3 generate.py --bench UNI --tasks 5 --sets $TASKSETS_PER_CONFIG --startid 0 AutomaticEval/Relation/UNI/chains05.jsonl --maxHTp 350 --maxH 1000000
python3 generate.py --bench UNI --tasks 20 --sets $TASKSETS_PER_CONFIG --startid 10000 AutomaticEval/Relation/UNI/chains20.jsonl --maxHTp 350 --maxH 1000000
python3 generate.py --bench UNI --tasks 50 --sets $TASKSETS_PER_CONFIG --startid 20000 AutomaticEval/Relation/UNI/chains50.jsonl --maxHTp 350 --maxH 1000000

echo "Chains stored in AutomaticEval/Relation/UNI/chains<tasks-per-set>.jsonl"

for i in $(seq 0 $((NUM_ITERATIONS - 1))); do
(
    python3 analysis.py AutomaticEval/Relation/UNI/chains05.jsonl --info --relative-bound 0.95 --no-print --output AutomaticEval/Relation/UNI/results05_${i}.jsonl
) &
    if [ $PARALLELIZE = false ]; then
        wait
    fi
done
wait

for i in $(seq 0 $((NUM_ITERATIONS - 1))); do
(
    python3 analysis.py AutomaticEval/Relation/UNI/chains20.jsonl --info --relative-bound 0.95 --no-print --output AutomaticEval/Relation/UNI/results20_${i}.jsonl
) &
    if [ $PARALLELIZE = false ]; then
        wait
    fi
done
wait


for i in $(seq 0 $((NUM_ITERATIONS - 1))); do
(
    python3 analysis.py AutomaticEval/Relation/UNI/chains50.jsonl --info --relative-bound 0.95 --no-print --output AutomaticEval/Relation/UNI/results50_${i}.jsonl
) &
    if [ $PARALLELIZE = false ]; then
        wait
    fi
done
wait

echo "Analysis stored in AutomaticEval/Relation/UNI/results<tasks-per-set>.jsonl"

eval python plot.py -o AutomaticEval/paperdata/UNI_runtime.png AutomaticEval/paperdata/UNI_anchors.png -c $NUM_ITERATIONS AutomaticEval/Relation/UNI/results50_{0..$REPEATING_RUNS}.jsonl  AutomaticEval/Relation/UNI/results20_{0..$REPEATING_RUNS}.jsonl  AutomaticEval/Relation/UNI/results05_{0..$REPEATING_RUNS}.jsonl

echo "Plots stored in AutomaticEval/paperdata/"

end_time=$(date +%s.%N)
elapsed=$(echo "$end_time - $start_time" | bc)
echo "- Total elapsed time for synthetic evaluation with UNIFORM benchmark: ${elapsed}s"
