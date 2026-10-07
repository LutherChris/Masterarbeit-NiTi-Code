import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from lib.run_model_path import run

# ---------------------------------------------------------------------------------------
# fixed output parameters
# ---------------------------------------------------------------------------------------
bandnumbers = (14, 15)
R=0.34547436
k0=(R, 0.11871832, 0.11871832)
p=0.012
n=11
datlabel="punkt1_000"
modeltype="out-Dateien"
coord_system="xyz"
# ------------------------------------------------------------
point="punkt1"
model_energy="diff"
model_axis="x"
# =======================================================================================
# Parameters of the iteration
# =======================================================================================
## Calculation of the first path
x_order_0=None; y_order_0=4; z_order_0=4; no_a0_0=True

plot_nk_model_0=1000; plot_path_0=False; calc_path_0=False
# ---------------------------------------------------------------------------------------
## Calculation of the new grid
#delta=0.003; n_grid=(50, 10, 10); path_step=0 #->path1-folder
#delta=0.0005; n_grid=(50, 10, 10); path_step=1 #->path2-folder
#delta=0.00005; n_grid=(50, 10, 10); path_step=2 #->path3-folder
#delta=0.000005; n_grid=(50, 10, 10); path_step=3 #->path4-folder

## Control calculation
#delta=0; n_grid=(1000, 1, 1); path_step=4 #->path5-folder

alpha=0.3; plot_grid = False; path_grid = False # Definition of the grid
calc_dft = False # Computation of the grid using QE and save of the df
load_new_csv = False # Loading the df
# ---------------------------------------------------------------------------------------
## Calculation of the new path
x_order_1=None; y_order_1=4; z_order_1=4; no_a0_1=True

plot_nk_model_1=1000; plot_path_1 = False; calc_path_1=False
# ---------------------------------------------------------------------------------------
## further plots
plot_titel = ""
## 4D Plots
black_plot=False; plot_cut_value=0.005; plot_thz_cut_diff=False; energy_4D = "diff"; plot_data=False
## Plot both paths simultaneously
plot_path_both = False
# ---------------------------------------------------------------------------------------
# THz active region
cut_value_diff=0.01241; cut_value_bands=0.05
# ---------------------------------------------------------------------------------------
# final analysis
plot_analysis_point1=False; final_analysis_point1 = False
# #######################################################################################

if __name__ == "__main__":
    run(cfg=__import__(__name__))
