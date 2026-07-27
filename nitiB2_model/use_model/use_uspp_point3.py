import os
import sys
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))) # Erweitert den Arbeitsbereich von Python auf parallele Ordner.
from lib.run_model_use import run

# ---------------------------------------------------------------------------------------
# Erstellung des regulären Gitters
# ---------------------------------------------------------------------------------------
# Bankreuzung an der Fermi-Energie
k0 = (0.5, 0.5, 0.09513568) 
# Gittergrenzen des regulären Gitters
axis_1 = np.linspace(-0.007, 0.007, 30)
axis_2 = np.linspace(0, 0.016, 30)
axis_3 = np.linspace(0, 2*np.pi, 140, endpoint=False)

#axis_1 = np.array([0])
#axis_2 = np.array([0])
#axis_3 = np.array([0])

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

# OPTION 2: Über Pfad
load_coeffs_from_path = False
path_coeffs = "/home/chris/Dokumente/Digitaler Anhang/Modellkoeffizienten/Ordnungen/uspp/Punkt 3/diff/2-3-1/nitiB2_model_coeffs_diff.txt"

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
path_QE = "/home/chris/nitiB2_uspp/nitiB2_model_out/punkt3_center_thz_p0007-0019-00_n21-28-64/model_path_point3_2/nitiB2_model_df.csv"

# 4D-Plots: Plot in 3D + Farbachse
plot_4Dplots = False

if __name__ == "__main__":
    run(cfg=__import__(__name__))
