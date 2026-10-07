import os
import sys
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from lib.run_model_calc import run

# --------------------------------------------------------------------------------------
# fixed parameters from the intersection and path calculation
# --------------------------------------------------------------------------------------
# from Intersection calculation (sect)
u = (1, 0, 0)
u = u / np.linalg.norm(u)
a = (0,1,0)
a = a / np.linalg.norm(a)
v = (0, 0, 0)
r = 0.2
phi_steps = 48
bandnumbers = (14, 15)
zero = (0.34547436, 0.11871832, 0.11871832) # Punkt 1

# from path_calculations (path)
coord_basis="xyz"
a_coeffs=[-0.7332429642612501, 1.7826111869586354, -8.391775184580466, 99.06024644165981]
b_coeffs=[-0.7332557473726407, 1.7698517082611422, -8.400680635383303, 222.30588634644334]
modeltype_path="path_point1"

# ######################################################################################
# main parameters for activating the blocks
# ######################################################################################

plot_grid = False
calc_dft = False
calc_mme = False
analysis = False
load_csv = False
calc_model = False

# --------------------------------------------------------------------------------------
# basic parameters for 5th and 7th block.
# --------------------------------------------------------------------------------------
# Energy on which the calculations are performed
energy="diff"

# Coordinate axes used for analysis and modeling
coord_system="path" 

# --------------------------------------------------------------------------------------
# parameters for 1st block: calculation of the grid
# --------------------------------------------------------------------------------------
# ======================================================================================
k0=zero
p=(0.009, 0.04, 0)
n=(19,34,60)
datlabel="punkt1"
grid_type="path"
rotation=False
path_phi_sym=1; path_no_rho0=False; path_rho_dense=0; path_rho_sigma=0.006; path_base_weight=0.2

# ======================================================================================

# --------------------------------------------------------------------------------------
# parameters for 5th block: calculation, analysis and adjustment of the data frames
#---------------------------------------------------------------------------------------
# principal component analysis
pca=False

# removal of zero values ​​from the data
no_000=True

# filtering the data frame to the THz-active area
cut_df_for_fit=False
cut_value_diff=0.0124; cut_value_bands=0.05; complete_cut=True

# calculation of the statistical values ​​of the matrix momentum elements
mme_statistics=False
merge_decimals=5

# calculating the intersection point
find_intersection=False
intersect_point="point_1"

# --------------------------------------------------------------------------------------
# parameters for model calculation
# --------------------------------------------------------------------------------------
# Should omit the 0th order of the polynomial?
no_a0 = True

# maximum number of coefficients
max_coeffs = 3000

# --------------------------------------------------------------------------------------
# band difference
#modeltype= "model_path_abs_4"; coord_system="path"; symmetry=1; no_000 = True; energy="diff"
# lower band
#modeltype= "model_path_abs_5"; coord_system="path"; symmetry=1; no_000 = True; energy="band0"
# upper band
modeltype= "model_path_abs_5"; coord_system="path"; symmetry=1; no_000 = True; energy="band1"

# orders to be calculated
p_order_list = [5]
f_order_list = [27]
l_order_list = [29]
k_order_list = [5]
p1_order_list = [0]
p2_order_list = [0]
p3_order_list = [0]

"""p_order_list = np.arange(2,6,1)
f_order_list = np.arange(20,30,1)
l_order_list = np.arange(20,30,1)
k_order_list = np.arange(2,6,1)
p1_order_list = [0]
p2_order_list = [0]
p3_order_list = [0]"""

# adjustment of the (only!) constant coefficient
a0_correction = False

# Ridge solution method instead of linear regression
ridgeCV = False 
ridge_alphas = np.logspace(-6, 2, 9) 

# column scaling of the design matrix
col_weighting = True

# saving the errors as a CSV file
save_errors = False

if __name__ == "__main__":
    run(cfg=__import__(__name__))
