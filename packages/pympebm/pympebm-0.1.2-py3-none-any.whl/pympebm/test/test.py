from pympebm import run_mpebm
import os
import json 
import re 

def extract_components(filename):
    pattern = r'^j(\d+)_r([\d.]+)_E(.*?)_m(\d+)$'
    match = re.match(pattern, filename)
    if match:
        return match.groups()  # returns tuple (J, R, E, M)
    return None

cwd = os.getcwd()
print("Current Working Directory:", cwd)
data_dir = f"{cwd}/pympebm/test/my_data"
data_files = os.listdir(data_dir) 

OUTPUT_DIR = 'algo_results'

with open(f"{cwd}/pympebm/test/true_order_and_stages.json", "r") as f:
    true_order_and_stages = json.load(f)

for data_file in data_files:
    estimated_partial_rankings = []

    fname = data_file.replace('.csv', '')
    J, R, E, M = extract_components(fname)
    true_order_dict = true_order_and_stages[fname]['true_order']
    true_stages = true_order_and_stages[fname]['true_stages']
    partial_rankings = true_order_and_stages[fname]['ordering_array']
    n_partial_rankings = len(partial_rankings)

    for idx in range(n_partial_rankings):
        # partial ranking data file path
        pr_data_file = f"{cwd}/pympebm/test/data{idx}/PR{idx}_j{J}_r{R}_E{E}_m0_m{M}.csv"

        results = run_mpebm(
            partial_rankings=None, 
            mp_method=None,
            data_file=pr_data_file,
            save_results=False,
            n_iter=1000,
            burn_in=50
        )
        order_with_highest_ll = results['order_with_highest_ll']
        # Sort by value, the sorted result will be a list of tuples
        partial_ordering = [k for k, v in sorted(order_with_highest_ll.items(), key=lambda item: item[1])]
        estimated_partial_rankings.append(partial_ordering)

    for mp_method in ['Pairwise', 'Mallows', 'BT', 'PL']:
        run_mpebm(
            partial_rankings=estimated_partial_rankings,
            mp_method=mp_method,
            save_results=True,
            data_file= os.path.join(data_dir, data_file),
            output_dir=OUTPUT_DIR,
            output_folder=mp_method,
            n_iter=1000,
            n_shuffle=2,
            burn_in=50,
            thinning=1,
            true_order_dict=true_order_dict,
            true_stages = true_stages,
            skip_heatmap=True,
            skip_traceplot=True,
            seed = 53
        )

    run_mpebm(
        save_results=True,
        data_file= os.path.join(data_dir, data_file),
        output_dir=OUTPUT_DIR,
        output_folder='saebm',
        n_iter=1000,
        n_shuffle=2,
        burn_in=50,
        thinning=1,
        true_order_dict=true_order_dict,
        true_stages = true_stages,
        skip_heatmap=True,
        skip_traceplot=True,
        seed = 53
    )