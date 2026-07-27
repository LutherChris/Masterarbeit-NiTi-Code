import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))) # Erweitert den Arbeitsbereich von Python auf parallele Ordner.
from lib.run_model_path import run

# ---------------------------------------------------------------------------------------
# feste Ausgangsparameter
# ---------------------------------------------------------------------------------------
point = "punkt2"    # Parametrisiertung nach x
bandnumbers = (14, 15) #!
zero = (0.30299328, 0.30299328, 0.30299328) # Punkt 2A

modeltype = "out-Dateien"
model_energy = "diff"

# Anfangsgitter (Kopie aus path_uspp_point2B_000.py)
k0=zero; p=(0.04, 0.15, 0); n=(81,151,2); grid_type="path"; datlabel="punkt2B_000"; rotation=False; path_phi_sym=2; path_n_phi_min=None

coord_system="xyz"
model_axis="t"
# =======================================================================================
# Parameter der Iteration
# =======================================================================================
## Berechnung des ersten Pfades
x_order_0=7; y_order_0=7; z_order_0=7; no_a0_0=False
filter_intersection_0=False; filter_tol_0=1e-3; cut_energy_0=1e-5

plot_nk_model_0=1000; plot_path_0=False; calc_path_0=False
# ---------------------------------------------------------------------------------------
## Berechnung des neuen Gitters
#delta=0.0025; n_grid=(321, 1, 21); path_step=0 #->path1-Ordner
#delta=0.001; n_grid=(321, 1, 21); path_step=1 #->path2-Ordner
#delta=0.00025; n_grid=(321, 1, 21); path_step=2 #->path3-Ordner
#delta=0.0001; n_grid=(321, 1, 21); path_step=3 #->path4-Ordner

# Datenpunkte entlang des letzten Pfades
delta=0; n_grid=(2000, 1, 1); path_step=4 #->path5-Ordner

alpha=0.1; plot_grid = False; path_grid = False # Definition des Gitters
calc_dft = False # Berechnung des Gitters durch QE und Speichern des df
load_new_csv = True # Laden des df
# ---------------------------------------------------------------------------------------
## Berechnung des neuen Pfades
x_order_1=7; y_order_1=7; z_order_1=7; no_a0_1=False
filter_intersection_1=True; filter_tol_1=1e-3; cut_energy_1=1e-5

plot_nk_model_1=1000; plot_path_1 = False; calc_path_1=False
# ---------------------------------------------------------------------------------------
## weitere Plots
plot_titel = "Differenz der Bänder"
## 4D Plots
black_plot=False; plot_cut_value=0.0005; plot_thz_cut_diff=False; energy_4D = "diff"; plot_data=True
## Plot beider Pfade gleichzeitig
plot_path_both = False
# ---------------------------------------------------------------------------------------
# THz-aktiver Bereich
cut_value_diff=0.01241; cut_value_bands=0.05
# ---------------------------------------------------------------------------------------
# finale Analyse von Punkt 2
plot_analysis_point2 = False; final_analysis_point2 = False 
plot_2A_2B=False; calc_point_2A_2B = False 
# #######################################################################################

if __name__ == "__main__":
    run(cfg=__import__(__name__))
