import os
import sys
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))) # Erweitert den Arbeitsbereich von Python auf parallele Ordner.
from lib.run_model_use import run

# ---------------------------------------------------------------------------------------
# Erstellung des regulären Gitters
# ---------------------------------------------------------------------------------------
# Bankreuzung an der Fermi-Energie
k0 = (0.34547436, 0.11871832, 0.11871832) # Punkt 1
# Gittergrenzen des regulären Gitters


# ---------------------------------------------------------------------------------------
# feste Parameter
# ---------------------------------------------------------------------------------------
# Schnittpunkte und Pfad-Berechnung
axis_1 = np.linspace(-0.009, 0.009, 20)
axis_2 = np.linspace(0, 0.033, 20)
axis_3 = np.linspace(0, 2*np.pi, 300, endpoint=False)

# Gittertyp
grid_type="path"
a_coeffs=[-0.7332429642612501, 1.7826111869586354, -8.391775184580466, 99.06024644165981]
b_coeffs=[-0.7332557473726407, 1.7698517082611422, -8.400680635383303, 222.30588634644334]
modeltype_path="path_point1"

# -----------------------------------------------------------------------------------
# Berechnung der Modellenergien
# -----------------------------------------------------------------------------------
# Modelltyp und Ordnungen des Modells
# ===================================
modeltype= "model_path_abs_4"
p_order = 5
f_order = 27
l_order = 29
k_order = 5
p1_order = 0
p2_order = 0
p3_order = 0

# Zusätzliche Modelleinstellungen
# ===============================
symmetry=1

# Laden der Modell-Koeffizienten
# ==============================

# OPTION 1: Über Parameter aus Modellberechnung
p=(0.009, 0.04, 0); n=(19,34,60); datlabel="punkt1_center_thz"; energy="diff" 

# Optionale Speicherung der Modell-Energien
# =========================================
save_dataframe = True
# OPTION 2:  (Speichern über Pfad)
path_save = "/home/chris/Schreibtisch/save.csv"

# ---------------------------------------------------------------------------------------
# Plot des Dataframes
# ---------------------------------------------------------------------------------------

# 2D - Sliderpolts
plot_axis = "phi"; plot_2Dplots = False
nk_model = 2000
plot_QE_grid = False
path_QE = ""

# 4D-Plots: Plot in 3D + Farbachse
plot_4Dplots = False

if __name__ == "__main__":
    run(cfg=__import__(__name__))
