import os
import sys
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))) # Erweitert den Arbeitsbereich von Python auf parallele Ordner.
from lib.run_model_use import run

# ---------------------------------------------------------------------------------------
# Erstellung des regulären Gitters
# ---------------------------------------------------------------------------------------
# Bankreuzung an der Fermi-Energie
k0 = (0.345495616, 0.118331096, 0.118331096) # Punkt 1
# Gittergrenzen des regulären Gitters
axis_1 = np.linspace(-0.009, 0.009, 20)
axis_2 = np.linspace(0, 0.033, 20)
axis_3 = np.linspace(0, 2*np.pi, 300, endpoint=False)

# Gittertyp
grid_type="path"
a_coeffs=[-0.7300042576783502, 1.7632114278333084, -9.04935814745873, 108.88722959947157]
b_coeffs=[-0.7299667586279922, 1.7696441060531072, -9.784393919450363, 50.20398048428685]
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
