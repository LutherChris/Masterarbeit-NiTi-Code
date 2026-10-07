import os
import sys
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from lib.run_model_calc import run

# --------------------------------------------------------------------------------------
# fixed parameters from the intersection and path calculation
# --------------------------------------------------------------------------------------
u = (1, 0, 0)
u = u / np.linalg.norm(u)
a = (0,1,0)
a = a / np.linalg.norm(a)
v = (0, 0, 0)
R = 0.345
r = 0.2
phi_steps = 48
bandnumbers = (14, 15)
zero = (R, 0.119, 0.119)

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
# Calculations at intersection point 1, grid definition

# Grid No. 0 ; Point distance 0.0002
#R = 0.345
#zero = (R, 0.119, 0.119)
#k0=zero; p=0.001; n=11; grid_type="regular"; datlabel="punkt1_find_00"; rotation=False

# Grid No. 1 ; Point distance 0.00004
k0=(0.3454, 0.1188, 0.1188); p=0.0002; n=11; grid_type="regular"; datlabel="punkt1_find_01"; rotation=False

# Grid No. 2 ; Point distance 0.000008
#k0=(0.34548, 0.11872, 0.11872); p=0.00004; n=11; grid_type="regular"; datlabel="punkt1_find_02"; rotation=False

# Grid No. 3 ; Point distance 0.0000016
#k0=(0.345472, 0.11872, 0.11872); p=0.000008; n=11; grid_type="regular"; datlabel="punkt1_find_03"; rotation=False

# Grid No. 4 ; Point distance 3.2e-7
#k0=(0.345475, 0.118718, 0.118718); p=0.0000016; n=11; grid_type="regular"; datlabel="punkt1_find_04"; rotation=False

# Final Grid #5 (Control Grid)
#k0=(0.34547436, 0.11871832, 0.11871832); p=0.0000016; n=11; grid_type="regular"; datlabel="punkt1_find_05"; rotation=False

# Final result: Energies on the order of e-7
# (0.34547436, 0.11871832, 0.11871832)

# ======================================================================================

# --------------------------------------------------------------------------------------
# parameters for 5th block: calculation, analysis and adjustment of the data frames
# --------------------------------------------------------------------------------------
# principal component analysis
pca=False

# removal of zero values ​​from the data
no_000=False

# filtering the data frame to the THz-active area
cut_df_for_fit=False
cut_value_diff=0.0124; cut_value_bands=0.05; complete_cut=True

# calculation of the statistical values ​​of the matrix momentum elements
mme_statistics=False
merge_decimals=5

# calculating the intersection point
find_intersection=True
intersect_point="point_1"

# --------------------------------------------------------------------------------------
# parameters for model calculation
# --------------------------------------------------------------------------------------
#  Should omit the 0th order of the polynomial?
no_a0 = False

# maximum number of coefficients
max_coeffs = 10000

# --------------------------------------------------------------------------------------

# orders to be calculated
p_order_list = [2]
f_order_list = [17]
l_order_list = [20]
k_order_list = [3]
p1_order_list = [0]
p2_order_list = [0]
p3_order_list = [0]

#adjustment of the (only!) constant coefficient
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
