import utils
from pathlib import Path


SIM_DIR = "/home/apc6353/Documents/school/bme333/simulation_outputs"
SIM_RUN = "2024-11-04+11-41-11"


if __name__ == "__main__":
    
    print("Beginning plotting...")
    
    results_path = Path(SIM_DIR).joinpath(SIM_RUN)

    utils.plot_fluence(results_path)

    print("Finished plotting.")


