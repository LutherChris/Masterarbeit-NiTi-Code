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
R = 0.34547436
r = 0.2
phi_steps = 48
bandnumbers = (14, 15)
zero = (R, 0.11871832, 0.11871832)

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
# Energie, an dem die Berechnungen durchgeführt werden 
energy="diff"

# verwendete Koordinatenachsen für Analysis und Modellierung    
coord_system="xyz"

# --------------------------------------------------------------------------------------
# parameters for 1st block: calculation of the grid
# --------------------------------------------------------------------------------------
# ======================================================================================
# Berechnungen am Schnittpunkt, Gitterdefinition zur Pfadsuche
k0=zero; p=0.012; n=11; grid_type="regular"; datlabel="punkt1_000"; rotation=False

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
find_intersection=False
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
p_order_list = []
f_order_list = []
l_order_list = []
k_order_list = []
p1_order_list = []
p2_order_list = []
p3_order_list = []

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
