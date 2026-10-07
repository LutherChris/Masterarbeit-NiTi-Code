import os
import sys
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from lib.run_model_plot import run

# ######################################################################################
# Main parameters
# ######################################################################################

# ===================================================================================
zero = (0.34547436, 0.11871832, 0.11871832)
a_coeffs=[-0.7332429642612501, 1.7826111869586354, -8.391775184580466, 99.06024644165981]
b_coeffs=[-0.7332557473726407, 1.7698517082611422, -8.400680635383303, 222.30588634644334]
modeltype_path="path_point1"
# ===================================================================================
k0=zero
p=(0.009, 0.04, 0)
n=(19,34,60)
datlabel="punkt1"
grid_type="path"
rotation=False
path_phi_sym=1; path_no_rho0=False; path_rho_dense=0; path_rho_sigma=0.006; path_base_weight=0.2
# ===================================================================================

# --------------------------------------------------------------------------------------
# Basic configuration
# --------------------------------------------------------------------------------------
# band difference
#modeltype= "model_path_abs_4"; coord_system="path"; symmetry=1; no_000 = True; energy="diff"
# lower band
#modeltype= "model_path_abs_5"; coord_system="path"; symmetry=1; no_000 = True; energy="band0"
# upper band
modeltype= "model_path_abs_5"; coord_system="path"; symmetry=1; no_000 = True; energy="band1"

# Orders
p_order = 5
f_order = 27
l_order = 29
k_order = 5
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
coord_system = "kxyz" # möglich: "kxyz", "xyz", "xyz_scaled", "path", "tNB"

# Energy axis for all plots
plot_energy_axis = "pz"
plot_titel = ""

# --------------------------------------------------------------------------------------
# 2D - Sliderpolts
# --------------------------------------------------------------------------------------
plot_2Dplots = False
plot_model = True
axis_2D = "phi"; nk_model = 2000; error = False

# --------------------------------------------------------------------------------------
# 3D - Sliderpolts
# --------------------------------------------------------------------------------------
plot_3Dplots = False
axis_3D = "y"

# --------------------------------------------------------------------------------------
# 4D plots: plot in 3D + color axis
# --------------------------------------------------------------------------------------
plot_4Dplots = False
black_plot = False; plot_cube = False

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
axis1 = "len_coeffs"
max_error_2D = 0.0001; thz_range_2D = True
#max_error_2D = None

# --------------------------------------------------------------------------------------
# Plot of errors for different orders in 3D
# --------------------------------------------------------------------------------------
plot_errors_3D = False
axis1_3D = "f_order"; axis2_3D = "l_order"
max_error_3D = None; thz_range_3D = True

if __name__ == "__main__":
    run(cfg=__import__(__name__))