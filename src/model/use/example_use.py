import os
import sys
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from lib.run_model_use import run

# --------------------------------------------------------------------------------------
# Creating the regular grid
# --------------------------------------------------------------------------------------
k0 = (0.34547436, 0.11871832, 0.11871832)

# --------------------------------------------------------------------------------------
# fixed parameters
# --------------------------------------------------------------------------------------
# Intersection points and path calculation
axis_1 = np.linspace(-0.009, 0.009, 20)
axis_2 = np.linspace(0, 0.033, 20)
axis_3 = np.linspace(0, 2*np.pi, 300, endpoint=False)

# Grid type
grid_type="path"
a_coeffs=[-0.7332429642612501, 1.7826111869586354, -8.391775184580466, 99.06024644165981]
b_coeffs=[-0.7332557473726407, 1.7698517082611422, -8.400680635383303, 222.30588634644334]
modeltype_path="path_point1"

# ----------------------------------------------------------------------------------
# Calculation of the model energies
# ----------------------------------------------------------------------------------
# Model type and orders of the model
# ===================================
modeltype= "model_path_abs_4"
p_order = 5
f_order = 27
l_order = 29
k_order = 5
p1_order = 0
p2_order = 0
p3_order = 0

# Additional model settings
# ===============================
symmetry=1

# Loading the model coefficients
# ==============================

# OPTION 1: Via parameters from model calculation
p=(0.009, 0.04, 0); n=(19,34,60); datlabel="punkt1"; energy="diff" 

# OPTION 2: Via path
load_coeffs_from_path = False
path_coeffs = "/home/chris/Dokumente/Digitaler Anhang/Modellkoeffizienten/Ordnungen/uspp/Punkt 3/diff/2-3-1/nitiB2_model_coeffs_diff.txt"

# Optional storage of model energies
# =========================================
save_dataframe = True
# OPTION 2: (Save via path)
path_save = "/home/chris/Schreibtisch/save.csv"

# OPTION 1: (Save in the model parameters folder)
#path_save = None

# --------------------------------------------------------------------------------------
# Plot of the data frame
# --------------------------------------------------------------------------------------

# 2D - Sliderpolts
plot_axis = "phi"; plot_2Dplots = False
nk_model = 2000
plot_QE_grid = False
path_QE = ""

# 4D plots: plot in 3D + color axis
plot_4Dplots = False

if __name__ == "__main__":
    run(cfg=__import__(__name__))
