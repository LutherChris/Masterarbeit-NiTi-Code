import os
import sys
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))) # Erweitert den Arbeitsbereich von Python auf parallele Ordner.
from lib.run_model_use import run

# ---------------------------------------------------------------------------------------
# Erstellung des regulären Gitters
# ---------------------------------------------------------------------------------------
# Bankreuzung an der Fermi-Energie
k0 = (0.30312352, 0.30312352, 0.30312352) # Punkt 2A
# Gittergrenzen des regulären Gitters
axis_1 = np.linspace(-0.007, 0.007, 20)
axis_2 = np.linspace(0, 0.05, 30)
axis_3 = np.linspace(0, 2*np.pi, 120, endpoint=False)

# Gittertyp
grid_type="path_grid_2B"
a_coeffs=[0.01148933207155924, 1.6317263844478398, 9.795159198026282, 99.08785267481657, 382.3674749566283]
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
k_order = 3
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

# ---------------------------------------------------------------------------------------
# Plot des Dataframes
# ---------------------------------------------------------------------------------------

# 2D - Sliderpolts
plot_axis = "phi"; plot_2Dplots = False
plot_QE_grid = True
nk_model = 2000
path_QE = "/home/chris/nitiB2_uspp/nitiB2_model_out/punkt2_2A2B_kontrolle_p0007-005-00_n21-29-60/out-Dateien/nitiB2_model_df.csv"

# 4D-Plots: Plot in 3D + Farbachse
plot_4Dplots = False

if __name__ == "__main__":
    run(cfg=__import__(__name__))
