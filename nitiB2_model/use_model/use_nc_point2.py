import os
import sys
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))) # Erweitert den Arbeitsbereich von Python auf parallele Ordner.
from lib.run_model_use import run

# ---------------------------------------------------------------------------------------
# Erstellung des regulären Gitters
# ---------------------------------------------------------------------------------------
# Bankreuzung an der Fermi-Energie
k0 = (0.30299328, 0.30299328, 0.30299328) # Punkt 2A
# Gittergrenzen des regulären Gitters
axis_1 = np.linspace(-0.007, 0.007, 20)
axis_2 = np.linspace(0, 0.05, 30)
axis_3 = np.linspace(0, 2*np.pi, 120, endpoint=False)

# Gittertyp
grid_type="path_grid_2B"
a_coeffs=[0.011819218568454061, 1.635300724593384, 9.917263532898168, 92.51868349101855, -938.6129963109424]
b_coeffs=None
modeltype_path="path_point2B"

# -----------------------------------------------------------------------------------
# Berechnung der Modellenergien
# -----------------------------------------------------------------------------------
# Modelltyp und Ordnungen des Modells
# ===================================
modeltype = "model_path_point2_2"
p_order = 5
f_order = 0
l_order = 0
k_order = 2
p1_order = 11
p2_order = 0
p3_order = 0

# Zusätzliche Modelleinstellungen
# ===============================
symmetry=3

# Laden der Modell-Koeffizienten
# ==============================

# OPTION 1: Über Parameter aus Modellberechnung
p=(0.007, 0.05, 0); n=(21,29,60); datlabel="punkt2_2A2B"; energy="diff"

# Optionale Speicherung der Modell-Energien
# =========================================
save_dataframe = True
# OPTION 2:  (Speichern über Pfad)
path_save = "/home/chris/Schreibtisch/save.csv"

# OPTION 1: (Speichern im Ordner der Modell-Parameter)
#path_save = None

# ---------------------------------------------------------------------------------------
# Plot des Dataframes
# ---------------------------------------------------------------------------------------

# 2D - Sliderpolts
plot_axis = "phi"; plot_2Dplots = False
nk_model = 2000
plot_QE_grid = True
path_QE = ""

# 4D-Plots: Plot in 3D + Farbachse
plot_4Dplots = False

if __name__ == "__main__":
    run(cfg=__import__(__name__))
