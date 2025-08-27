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

def dump_json(results_map, file_name="results.json"):
    with open(file_name, "w") as json_file:
        json.dump(results_map, json_file, indent=4)

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

def main():
    dir_path = sys.argv[1]
    results = parse_logs_in_directory(dir_path)
    dump_json(results, os.path.join(dir_path, "results.json"))

if __name__ == "__main__":
    main()
        