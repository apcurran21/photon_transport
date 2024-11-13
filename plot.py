import utils
from pathlib import Path


SIM_DIR = "/home/apc6353/Documents/school/bme333/simulation_outputs"
SIM_RUN = "2024-11-04+11-41-11"
DATA_PATH = Path(r"C:\Users\Andy\OneDrive - Northwestern University\Documents\_Year 4\1st Quarter\BME 333\assignments\mc\good_simresults")

if __name__ == "__main__":
    
    print("Beginning plotting...")
    
    results_path = Path(SIM_DIR).joinpath(SIM_RUN)

    # utils.plot_fluence(results_path)
    utils.plot_fluence(DATA_PATH)

    print("Finished plotting.")


