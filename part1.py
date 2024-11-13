import utils
from pathlib import Path
from time import time


# OUTPUT_DIR = "/home/apc6353/Documents/school/bme333/simulation_outputs"
OUTPUT_DIR = r"C:\Users\Andy\OneDrive - Northwestern University\Documents\_Year 4\1st Quarter\BME 333\assignments\mc\simulation_results"


if __name__ == "__main__":

    print("Beginning the experiment...")
    
    # set the numbers of simulated photon
    photon_nums = [1000, 10000, 100000, 1000000]

    # create an output directory
    output_path = Path(OUTPUT_DIR).joinpath(utils.get_curr_time())
    output_path.mkdir(parents=True, exist_ok=True)

    # initialize some time tracking
    metadata=[]
    
    # simulate with n0=1, n1=1
    n0 = 1.0
    n1 = 1.0
    for photon_num in photon_nums:
        start_time = time()
        sim = utils.Simulation(photon_num, n0, n1, output_path)
        sim.run_sim()
        metadata.append({
            'num_packets' : photon_num,
            'n0' : n0,
            'n1' : n1,
            'duration' : time() - start_time
        })

    # simulate with n0=1, n1=1.37
    n1 = 1.37
    for photon_num in photon_nums:
        sim = utils.Simulation(photon_num, n0, n1, output_path)
        sim.run_sim()

    print("Finished the experiment!")
