import os
import sys
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from lib.run_model_plot import run

# ######################################################################################
# Main parameters
# ######################################################################################
# Calculations at intersection point 1, grid definition

# Grid No. 0 ; Point distance 0.0002
#R = 0.345
#zero = (R, 0.119, 0.119)
#k0=zero; p=0.001; n=11; grid_type="regular"; datlabel="punkt1_find_00"; rotation=False

# Grid No. 1 ; Point distance 0.00004
#k0=(0.3454, 0.1188, 0.1188); p=0.0002; n=11; grid_type="regular"; datlabel="punkt1_find_01"; rotation=False

# Grid No. 2 ; Point distance 0.000008
#k0=(0.34548, 0.11872, 0.11872); p=0.00004; n=11; grid_type="regular"; datlabel="punkt1_find_02"; rotation=False

# Grid No. 3 ; Point distance 0.0000016
#k0=(0.345472, 0.11872, 0.11872); p=0.000008; n=11; grid_type="regular"; datlabel="punkt1_find_03"; rotation=False

# Grid No. 4 ; Point distance 3.2e-7
#k0=(0.345475, 0.118718, 0.118718); p=0.0000016; n=11; grid_type="regular"; datlabel="punkt1_find_04"; rotation=False

# Final Grid #5 (Control Grid)
k0=(0.34547436, 0.11871832, 0.11871832); p=0.0000016; n=11; grid_type="regular"; datlabel="punkt1_find_05"; rotation=False

# Final result: Energies on the order of e-7
# (0.34547436, 0.11871832, 0.11871832)

# --------------------------------------------------------------------------------------
# Basic configuration
# --------------------------------------------------------------------------------------

# Ordnungen
p_order = 2
f_order = 17
l_order = 20
k_order = 3
p1_order = 0
p2_order = 0
p3_order = 0

# --------------------------------------------------------------------------------------
# Energy data frame design
# --------------------------------------------------------------------------------------
thz_cut_diff=False; thz_cut_band0=False; thz_cut_band1=False
cut_value_diff=0.0124; cut_value_bands=0.05

# --------------------------------------------------------------------------------------
# Plot configuration
# --------------------------------------------------------------------------------------
# Defining the axes
coord_system = "xyz"

# Energy axis for all plots
plot_energy_axis = "diff"
plot_titel = ""

# --------------------------------------------------------------------------------------
# 2D - Sliderpolts
# --------------------------------------------------------------------------------------
plot_2Dplots = False
plot_model = False
axis_2D = "x"; nk_model = 1000; error = False

# --------------------------------------------------------------------------------------
# 3D - Sliderpolts
# --------------------------------------------------------------------------------------
plot_3Dplots = False
axis_3D = "x"

# --------------------------------------------------------------------------------------
# 4D plots: plot in 3D + color axis
# --------------------------------------------------------------------------------------
plot_4Dplots = False
black_plot = False; plot_cube = True

# --------------------------------------------------------------------------------------
# 4D Plots: Plot of the momentum matrix elements
# --------------------------------------------------------------------------------------
plot_4Dplots_mme_in_thz = False
merge_decimals = 5

# --------------------------------------------------------------------------------------
# Plot of gradients and curvature
# --------------------------------------------------------------------------------------
plot_gradient = False
plot_curv = False
step = 5

# --------------------------------------------------------------------------------------
# Plot of errors for different orders in 2D
# --------------------------------------------------------------------------------------
plot_errors_2D = False
axis1 = "len_diff"
max_error_2D = None; thz_range_2D = True

# --------------------------------------------------------------------------------------
# Plot of errors for different orders in 3D
# --------------------------------------------------------------------------------------
plot_errors_3D = False
axis1_3D = "p_order"; axis2_3D = "k_order"
max_error_3D = None; thz_range_3D = True

if __name__ == "__main__":
    run(cfg=__import__(__name__))