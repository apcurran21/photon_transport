import utils
from pathlib import Path
from time import time
import json
import concurrent.futures
import time
import numpy as np


OUTPUT_DIR = "/home/apc6353/Documents/school/bme333/simulation_outputs"
NUM_CORES = 20


def run_trial(params):
    # currently `params` is just an integer
    num_photons = params

    n0 = 1.0
    n1 = 1.37
    start_time = time.time()
    sim = utils.Simulation(num_photons, n0, n1)
    sim.run_sim()
    return (sim.A, sim.r_gb, sim.z_gb)


if __name__ == "__main__":

    print("Beginning the experiment...")
    
    # create an output directory
    output_path = Path(OUTPUT_DIR).joinpath(utils.get_curr_time())
    output_path.mkdir(parents=True, exist_ok=True)

    # initialize some time tracking
    metadata={}

    # create params for the processes
    num_photons_total = 1000000
    # num_photons_total = 1000
    num_photons_per = int( num_photons_total / NUM_CORES )  
    params = [num_photons_per for _ in range(NUM_CORES)]
    
    # get accumulators for the trial results
    A = np.zeros((200, 66))
    r_gb = np.zeros(200)
    z_gb = np.zeros(66)
    start_time = time.time()

    with concurrent.futures.ProcessPoolExecutor(max_workers=NUM_CORES) as executor:
        trials_results = list(executor.map(run_trial, params))
    
    print("combining arrays")
    for curr_A, curr_r_gb, curr_z_gb in trials_results:
        A += curr_A
        r_gb += curr_r_gb
        z_gb += curr_z_gb

    # save to file
    print("writing the arrays to disk...")
    A_str = f"A_{num_photons_total}packets_{1.0}n0_{1.37}n1.npy".replace(".", "-")
    rgb_str = f"rgb_{num_photons_total}packets_{1.0}n0_{1.37}n1.npy".replace(".", "-")
    zgb_str = f"zgb_{num_photons_total}packets_{1.0}n0_{1.37}n1.npy".replace(".", "-")
    np.save(output_path.joinpath(A_str), A)
    np.save(output_path.joinpath(rgb_str), r_gb)
    np.save(output_path.joinpath(zgb_str), z_gb)

    metadata['total_runtime'] = time.time() - start_time 

    with open(output_path.joinpath("experiment_metadata"), "w") as f:
        json.dump(metadata, f)

    print("Finished the experiment!")
