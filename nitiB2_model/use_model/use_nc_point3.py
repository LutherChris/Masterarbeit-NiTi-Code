import os
import sys
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))) # Erweitert den Arbeitsbereich von Python auf parallele Ordner.
from lib.run_model_use import run

# ---------------------------------------------------------------------------------------
# Erstellung des regulären Gitters
# ---------------------------------------------------------------------------------------
# Bankreuzung an der Fermi-Energie
k0 = (0.5, 0.5, 0.09401408) # Punkt 3
# Gittergrenzen des regulären Gitters
axis_1 = np.linspace(-0.007, 0.007, 30)
axis_2 = np.linspace(0, 0.016, 30)
axis_3 = np.linspace(0, 2*np.pi, 140, endpoint=False)

# Gittertyp
grid_type="path"
a_coeffs = None
b_coeffs = None
modeltype_path="path_point3"

# -----------------------------------------------------------------------------------
# Berechnung der Modellenergien
# -----------------------------------------------------------------------------------
# Modelltyp und Ordnungen des Modells
# ===================================
modeltype="model_path_point3_2"
p_order = 4
f_order = 0
l_order = 6
k_order = 2
p1_order = 0
p2_order = 0
p3_order = 0

# Zusätzliche Modelleinstellungen
# ===============================
symmetry = 4

# Laden der Modell-Koeffizienten
# ==============================
# OPTION 1: Über Parameter aus Modellberechnung
p=(0.007, 0.019, 0); n=(21,28,64); datlabel="punkt3_center_thz"; energy="diff"

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
