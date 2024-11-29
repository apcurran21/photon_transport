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
    # currently `params` is a tuple of a (integer, float)
    num_photons, angle_rad = params

    n0 = 1.0
    n1 = 1.37
    start_time = time.time()
    # HARDCODED
    Nz = 10000
    Nx = int( Nz / 3 )
    Ny = int( Nz / 3 )
    sim = utils.Simulation(num_photons, n0, n1, Nx=Nx, Ny=Ny, Nz=Nz, incident_angle=angle_rad)
    sim.run_sim()
    return sim.A


if __name__ == "__main__":

    print("Beginning the experiment...")
    
    # create an output directory
    output_path = Path(OUTPUT_DIR).joinpath(utils.get_curr_time())
    output_path.mkdir(parents=True, exist_ok=True)

    # initialize some time tracking
    metadata={}

    # create params for the processes
    num_photons_total = 5000000
    num_photons_per = int( num_photons_total / NUM_CORES )

    # define dimensions for the grid
    Nz = 10000
    Nx = int( Nz / 3 )
    Ny = int( Nz / 3 )

    # run simulations for each of the specified photon entry angles
    angles = [20, 45, 70]
    for angle in angles:
        
        print(f"Simulating {num_photons_total} with an incident angle of {angle} degrees in {NUM_CORES} processes ({num_photons_per} per process)...")
        
        # convert angle from degrees to radians
        angle_rad = np.deg2rad(angle)

        params = [(num_photons_per, angle_rad) for _ in range(NUM_CORES)]
        
        # get accumulators for the trial results
        A = np.zeros((Nx + 2, Ny + 2, Nz + 1))         # choose (x, y, z) for simplicity
        start_time = time.time()

        with concurrent.futures.ProcessPoolExecutor(max_workers=NUM_CORES) as executor:
            trials_results = list(executor.map(run_trial, params))
        
        print("combining arrays")
        for curr_A in trials_results:
            A += curr_A

        # save to file
        print("writing the arrays to disk...")
        A_str = f"A_{num_photons_total}packets_{1.0}n0_{1.37}n1.npy".replace(".", "-")
        np.save(output_path.joinpath(A_str), A)

        metadata['total_runtime'] = time.time() - start_time 

        with open(output_path.joinpath("experiment_metadata"), "w") as f:
            json.dump(metadata, f)

        print("Finished the experiment!")
