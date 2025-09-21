import csv
import re
import sys
import os
import json

def parse_log(file_path):
    color = None
    ff_tokeep = None
    result = None
    runtime_dqbf = None
    runtime_pedant = None
    instance = None

    with open(file_path, "r") as f:
        ins_seen = False
        for line in f:
            # Extract instance name (from .bench path)
            if not ins_seen and line.strip().endswith(".bench") and "/" in line:
                instance = os.path.splitext(os.path.basename(line.strip()))[0]
                ins_seen = True

            # Extract color
            elif line.startswith("color="):
                color = int(line.strip().split("=")[1])
            # Extract FF_tokeep
            elif line.startswith("FF_tokeep="):
                ff_tokeep = int(line.strip().split("=")[1])
            # Extract result
            elif "UNSATISFIABLE" in line:
                result = "UNSATISFIABLE"
            elif "SATISFIABLE" in line:
                result = "SATISFIABLE"
            # Extract runtimes
            elif line.startswith("Runtime for DQBF"):
                print(instance, color, ff_tokeep)
                print(line)
                runtime_dqbf = float(re.findall(r"[\d.]+", line)[0])
            elif line.startswith("Runtime for pedant"):
                runtime_pedant = float(re.findall(r"[\d.]+", line)[0])

    # Print summary
    # print("======== SUMMARY ========")
    # print(f"Instance: {instance}")
    # print(f"Color: {color}")
    # print(f"FF_tokeep: {ff_tokeep}")
    # print(f"Result: {result}")
    # print(f"Runtime for DQBF: {runtime_dqbf} seconds")
    # print(f"Runtime for pedant: {runtime_pedant} seconds")

    return {
        "instance": instance,
        "color": color,
        "ff_tokeep": ff_tokeep,
        "result": result,
        "runtime_dqbf": runtime_dqbf,
        "runtime_pedant": runtime_pedant
    }

def parse_log_sat(file_path):
    instance = None
    ff_tokeep = None
    time_for_construction = {}   # store multiple n→time
    upper_bound = None
    lower_bound = None
    runtime_sat = None
    runtime_explicit = None
    runtime_popsat = None

    with open(file_path, "r") as f:
        ins_seen = False
        for line in f:
            line = line.strip()

            # instance name
            if not ins_seen and line.strip().endswith(".bench") and "/" in line:
                instance = os.path.splitext(os.path.basename(line.strip()))[0]
                ins_seen = True

            # FF_tokeep
            if line.startswith("FF_tokeep="):
                ff_tokeep = int(line.split("=")[1])

            if line.startswith('Traceback'):
                print(f'Found Traceback in instance {instance} with FF_tokeep={ff_tokeep}. Skipping this log.')
                # Reset all variables
                time_for_construction = {}
                upper_bound = None
                lower_bound = None
                runtime_sat = -1
                runtime_explicit = -1
                runtime_popsat = -1
                break

            # Time for n-Construction (can appear multiple times)
            m = re.match(r"Time for (\d+)-Construction:\s*([\d.]+)s", line)
            if m:
                n = int(m.group(1))
                t = float(m.group(2))
                time_for_construction[n] = t

            # Upper and lower bound
            if line.startswith("upper_bound"):
                upper_bound = int(line.split()[-1])
            if line.startswith("lower_bound"):
                lower_bound = int(line.split()[-1])

            # Runtimes at the end
            if line.startswith("Runtime for SAT"):
                m = re.search(r"(\d*\.\d+|\d+)", line)
                if m:
                    runtime_sat = float(m.group(1))

            elif "explicit_gen_iscas.py" in line:
                m = re.search(r"(\d*\.\d+|\d+)", line)
                if m:
                    runtime_explicit = float(m.group(1))

            elif "POPSAT solver" in line:
                m = re.search(r"(\d*\.\d+|\d+)", line)
                if m:
                    runtime_popsat = float(m.group(1))

    return {
        "instance": instance,
        "ff_tokeep": ff_tokeep,
        "time_for_construction": time_for_construction,
        "upper_bound": upper_bound,
        "lower_bound": lower_bound,
        "runtime_sat": runtime_sat,
        "runtime_explicit": runtime_explicit,
        "runtime_popsat": runtime_popsat,
    }

def dump_json(results_map, file_name="results.json"):
    with open(file_name, "w") as json_file:
        json.dump(results_map, json_file, indent=4)

    print("Results dumped to", file_name)

def dump_csv(result, file_name='combined_result.csv'):
    with open(file_name, "w", newline="") as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["Instance", "FF_tokeep", "Color", "DQBF Result", "Lower Bound", "Upper Bound", "Runtime SAT", "Runtime DQBF"])
        for row in result:
            csv_writer.writerow(row)
    print("Results dumped to", file_name)

def parse_logs_in_directory(dir_path):

    results_map = {}

    for file in os.listdir(dir_path):
        file_path = os.path.join(dir_path, file)
        if os.path.isfile(file_path):
            summary = parse_log(file_path)
            instance = summary["instance"]
            ff = summary["ff_tokeep"]
            color = summary["color"]

            if instance not in results_map:
                results_map[instance] = {}
            if ff not in results_map[instance]:
                results_map[instance][ff] = {}
            
            results_map[instance][ff][color] = {
                "result": summary["result"],
                "runtime_dqbf": summary["runtime_dqbf"],
                "runtime_pedant": summary["runtime_pedant"]
            }

    # Sort keys properly, skipping None keys
    valid_instances = [inst for inst in results_map.keys() if inst is not None]
    sorted_results = {
        inst: {
            ff: {c: results_map[inst][ff][c] for c in sorted([k for k in results_map[inst][ff].keys() if k is not None])}
            for ff in sorted([k for k in results_map[inst].keys() if k is not None])
        }
        for inst in sorted(valid_instances)
    }

    # print("======== ALL RESULTS ========")
    # for inst, inst_data in results_map.items():
    #     print(inst, "=>", inst_data)

    return sorted_results

def parse_logs_sat_in_directory(dir_path):
    """Parse all log files in a directory into nested result map."""
    results_map = {}

    for file in os.listdir(dir_path):
        file_path = os.path.join(dir_path, file)
        if os.path.isfile(file_path):
            summary = parse_log_sat(file_path)
            instance = summary["instance"]
            ff = summary["ff_tokeep"]

            if not instance or ff is None:
                continue  # skip incomplete logs

            if instance not in results_map:
                results_map[instance] = {}

            results_map[instance][ff] = {
                "time_for_construction": summary["time_for_construction"],
                "upper_bound": summary["upper_bound"],
                "lower_bound": summary["lower_bound"],
                "runtime_sat": summary["runtime_sat"],
                "runtime_explicit": summary["runtime_explicit"],
                "runtime_popsat": summary["runtime_popsat"],
            }

    # Sort for readability
    sorted_results = {
        inst: {
            ff: results_map[inst][ff]
            for ff in sorted(results_map[inst])
        }
        for inst in sorted(results_map)
    }

    return sorted_results

def compare_results(dqbf_result, sat_result):

    TIME_LIMIT = 3600 # time limit 3600s = 1hr

    combined_result = []

    print("======== COMPARISON ========")
    for inst in dqbf_result:
        if inst not in sat_result:
            print(f"[Warning] Instance {inst} missing in SAT results.")
            continue

        for ff in dqbf_result[inst]:
            if ff not in sat_result[inst]:
                print(f"[Warning] Instance {inst} with FF_tokeep={ff} missing in SAT results.")
                continue

            dqbf_colors = dqbf_result[inst][ff]
            sat_data = sat_result[inst][ff]

            # if sat_data["runtime_sat"] is None or float(sat_data["runtime_sat"]) >= TIME_LIMIT:
            #     print(f"[Timeout] Instance {inst}, FF_tokeep={ff} exceeds time limit: {sat_data['runtime_sat']}")
            #     continue

            for color in dqbf_colors:
                dqbf_entry = dqbf_colors[color]
                dqbf_res = dqbf_entry["result"]
                upper_bound = sat_data["upper_bound"]
                lower_bound = sat_data["lower_bound"]

                sat_data_runtime = sat_data["runtime_sat"] if (sat_data["runtime_sat"] is not None) and float(sat_data["runtime_sat"]) >=0 and float(sat_data["runtime_sat"]) < 3600 else 'Timeout'
                dqbf_runtime = dqbf_entry["runtime_dqbf"] if (dqbf_entry["runtime_dqbf"] is not None) and float(dqbf_entry["runtime_dqbf"]) >=0 and float(dqbf_entry["runtime_dqbf"]) < 3600 else 'Timeout'
                combined_result.append([inst, ff, color, dqbf_res, lower_bound, upper_bound, sat_data_runtime, dqbf_runtime])

                if sat_data["runtime_sat"] == -1 or sat_data["runtime_sat"] is None or float(sat_data["runtime_sat"]) >= TIME_LIMIT:
                    continue

                if upper_bound != lower_bound:
                    print(f"[Warning] Discrepancy for {inst}, FF_tokeep={ff}, color={color}: DQBF result={dqbf_res} but SAT bounds=({lower_bound}, {upper_bound})")
                elif lower_bound == color and dqbf_res == "SATISFIABLE":
                    print(f"[Info] Match for {inst}, FF_tokeep={ff}, color={color}: Both DQBF and SAT indicate SATISFIABLE at this color.")

                if dqbf_res == "UNSATISFIABLE":
                    if lower_bound is not None and color >= lower_bound:
                        print(f"[Warning] Discrepancy for {inst}, FF_tokeep={ff}, color={color}: DQBF UNSAT but SAT bounds=({lower_bound}, {upper_bound})")
                elif dqbf_res == "SATISFIABLE":
                    if lower_bound is not None and color < lower_bound:
                        print(f"[Warning] Discrepancy for {inst}, FF_tokeep={ff}, color={color}: DQBF SAT but SAT bounds=({lower_bound}, {upper_bound})")
    print("=======================")
    # print(combined_result)
    return combined_result

def main():
    dir_path = sys.argv[1]
    sat_dir_path = sys.argv[2]
    
    dqbf_results = parse_logs_in_directory(dir_path)
    dump_json(dqbf_results, os.path.join(dir_path, "results.json"))

    sat_result = parse_logs_sat_in_directory(sat_dir_path)
    dump_json(sat_result, os.path.join(sat_dir_path, "results_sat.json"))

    combined_result = compare_results(dqbf_results, sat_result)
    dump_csv(combined_result, "combined_result.csv")

if __name__ == "__main__":
    main()
        