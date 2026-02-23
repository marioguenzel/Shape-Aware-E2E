import argparse
import json

# === Configuration for mapping IDs to LaTeX short names and citations ===
ID_MAP = {
    "WATERS16/17 EffectChain1": ("Wat17-C1", "hamann2017waters"),
    "WATERS16/17 EffectChain2": ("Wat17-C2", "hamann2017waters"),
    "1": None,
    "WATERS2019, LG->LOC->EKF->Planner->DASM": ("Wat19-C1", "hamann2019waters"),
    "WATERS2019, CAN->LOC->EKF->Planner->DASM": ("Wat19-C2", "hamann2019waters"),
    "WATERS2019, CAN->EKF->Planner->DASM": ("Wat19-C3", "hamann2019waters"),
    "WATERS2019, SFM->Planner->DASM": ("Wat19-C4", "hamann2019waters"),
    "WATERS2019, LaneDet->Planner->DASM": ("Wat19-C5", "hamann2019waters"),
    "WATERS2019, Detection->Planner->DASM": ("Wat19-C6", "hamann2019waters"),
    "2": None,
    "RTSS 2021 - 1 - mmWaveRadar": ("RTSS-C1", "perceptin2021rtss"),
    "RTSS 2021 - 2 - camera": ("RTSS-C2", "perceptin2021rtss"),
    "RTSS 2021 - 3 - Lidar(long)": ("RTSS-C3", "perceptin2021rtss"),
    "RTSS 2021 - 4 - Lidar(short)": ("RTSS-C4", "perceptin2021rtss"),
    "RTSS 2021 - 5 - GNSS/IMU": ("RTSS-C5", "perceptin2021rtss"),
    "3": None,
    "AUTOSAR-Adaptive Brake Assistant": ("APD", "Bellasani:JSA2025"),
    "4": None,
    "Brake-By-Wire JSA 2024": ("Bec24", "becker2024material"),
    "5": None,
    "Gemlau TCPS 2021 Fig. 7a, upper path": ("Gem21-UP", "Gemlau2021"),
    "Gemlau TCPS 2021 Fig. 7a, lower path": ("Gem21-LP", "Gemlau2021"),
    "6": None,
    "Iyenghar ENASE 2020, Figure 7": ("Iye20", "iyenghar2020automated"),
    "7": None,
    "Frey 2010: Tech. report, Fig. 10 1st path from top": ("Fre10-C1", "Frey2010"),
    "Frey 2010: Tech. report, Fig. 10 2nd path from top": ("Fre10-C2", "Frey2010"),
    "Frey 2010: Tech. report, Fig. 10 3rd path from top, angleSync with 10ms period": ("Fre10-C3", "Frey2010"),
    "Frey 2010: Tech. report, Fig. 10 4rd path from top, angleSync with 10ms period": ("Fre10-C4", "Frey2010"),
    "8": None,
    "ROSACE - 1 - h_filter->altitude_hold->Vz_control": ("Pag14-C1", "Pagetti:RTAS14"),
    "ROSACE - 2 - x_filter->x_control": ("Pag14-C2", "Pagetti:RTAS14"),
}

parser = argparse.ArgumentParser(description="Create the table shown in the paper.")
parser.add_argument("input", help="Input file: results from the case studies as '.jsonl'")
args = parser.parse_args()

# === Load precomputed results from results/case_studies.jsonl ===
results = {}
with open(args.input, "r") as rf:
    for line in rf:
        entry = json.loads(line)
        results[entry["ID"]] = entry

# === Main Processing ===
latex_rows = []

for id_full in ID_MAP.keys():
    if ID_MAP[id_full] is None:
        latex_rows.append("\\midrule")
        continue
    if id_full not in results:
        raise KeyError(f"ID '{id_full}' is not found in the results file.")
    
    short_id, cite = ID_MAP[id_full]
    res = results[id_full]


    row = (
        f"{short_id}~\\cite{{{cite}}} & "
        f"{res['MaxRT']} & {res['MinRT']} & {res['AvRT']} & {res['throughp']:.3f} & ({res['mkRT'][9][0]},{res['mkRT'][9][1]}) & {res['LE-RT']:.2f} \\\\"
    )
    latex_rows.append(row)


# === Output as LaTeX table ===
print("\\begin{tabular}{lrrrrrrr}")
print("\\toprule")
print("\\textbf{Case Study} & \\textbf{Max} & \\textbf{Min} & \\textbf{Av} & \\textbf{Thr} & \\textbf{(m,k)} & \\textbf{LE} \\\\")
print("\\midrule")
for r in latex_rows:
    print(r)
print("\\bottomrule")
print("\\end{tabular}")
