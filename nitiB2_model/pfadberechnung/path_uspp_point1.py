import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))) # Erweitert den Arbeitsbereich von Python auf parallele Ordner.
from lib.run_model_path import run

# ---------------------------------------------------------------------------------------
# feste Ausgangsparameter
# ---------------------------------------------------------------------------------------
point = "punkt1"    # Parametrisiertung nach x
bandnumbers = (14, 15) #!
R = 0.34547436
zero = (R, 0.11871832, 0.11871832)

modeltype = "out-Dateien"
model_energy = "diff"

# Anfangsgitter (Kopie aus nitiB2_thz_model_calc)
k0=zero; p=0.012; n=11; datlabel="punkt1_000"

coord_system="xyz"
model_axis="x"
# =======================================================================================
# Parameter der Iteration
# =======================================================================================
## Berechnung des ersten Pfades
x_order_0=None; y_order_0=4; z_order_0=4; no_a0_0=True

plot_nk_model_0=1000; plot_path_0=False; calc_path_0=False
# ---------------------------------------------------------------------------------------
## Berechnung des neuen Gitters
#delta=0.003; n_grid=(50, 10, 10); path_step=0 #->path1-Ordner
#delta=0.0005; n_grid=(50, 10, 10); path_step=1 #->path2-Ordner
#delta=0.00005; n_grid=(50, 10, 10); path_step=2 #->path3-Ordner
#delta=0.000005; n_grid=(50, 10, 10); path_step=3 #->path4-Ordner

## Kontrollrechnung
#delta=0; n_grid=(1000, 1, 1); path_step=4 #->path5-Ordner

alpha=0.3; plot_grid = False; path_grid = False # Definition des Gitters
calc_dft = False # Berechnung des Gitters durch QE und Speichern des df
load_new_csv = False # Laden des df
# ---------------------------------------------------------------------------------------
## Berechnung des neuen Pfades
x_order_1=None; y_order_1=4; z_order_1=4; no_a0_1=True

plot_nk_model_1=1000; plot_path_1 = False; calc_path_1=False
# ---------------------------------------------------------------------------------------
## weitere Plots
plot_titel = "Differenz der Bänder"
## 4D Plots
black_plot=False; plot_cut_value=0.005; plot_thz_cut_diff=False; energy_4D = "diff"; plot_data=False
## Plot beider Pfade gleichzeitig
plot_path_both = False
# ---------------------------------------------------------------------------------------
# THz-aktiver Bereich
cut_value_diff=0.01241; cut_value_bands=0.05
# ---------------------------------------------------------------------------------------
# finale Analyse
plot_analysis_point1=False; final_analysis_point1 = False
# #######################################################################################

if __name__ == "__main__":
    run(cfg=__import__(__name__))
