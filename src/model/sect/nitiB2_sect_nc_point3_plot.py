import os
import sys
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))) # Erweitert den Arbeitsbereich von Python auf parallele Ordner.
from lib.run_model_plot import run

# #######################################################################################
# Haupt-Parameter
# #######################################################################################
# Werte aus nitiB2_thz_model_calc_punktX-Vorlage.py zum Laden der Dataframes

# ---------------------------------------------------------------------------------------
# Parameter für 1. Berechnung des Gitters
# ---------------------------------------------------------------------------------------
# Berechnungen am Schnittpunkt 3, Gitterdefinition

# Gitter Nr 0 ; Punkteabstand 0.0002
#zero = (0.5, 0.5, 0.095) # Startpunkt der Suche
#k0=zero; p=0.001; n=11; grid_type="regular"; datlabel="punkt3_find_00"; rotation=False

# Gitter Nr 1 ; Punkteabstand 0.0002
#k0=(0.5, 0.5, 0.094); p=0.001; n=11; grid_type="regular"; datlabel="punkt3_find_01"; rotation=False

# Gitter Nr 2 ; Punkteabstand 0.00004
#k0=(0.5, 0.5, 0.094); p=0.0002; n=11; grid_type="regular"; datlabel="punkt3_find_02"; rotation=False

# Gitter Nr 3 ; Punkteabstand 0.000008
#k0=(0.5, 0.5, 0.094); p=0.00004; n=11; grid_type="regular"; datlabel="punkt3_find_03"; rotation=False

# Gitter Nr 4 ; Punkteabstand 0.0000016
#k0=(0.5, 0.5, 0.094016); p=0.000008; n=11; grid_type="regular"; datlabel="punkt3_find_04"; rotation=False

# Gitter Nr 5 ; Punkteabstand 3.2e-7
#k0=(0.5, 0.5, 0.0940144); p=0.0000016; n=11; grid_type="regular"; datlabel="punkt3_find_05"; rotation=False

# Finales Gitter Nr 6 (Kontrollgitter)
k0=(0.5, 0.5, 0.09401408); p=0.0000016; n=11; grid_type="regular"; datlabel="punkt3_find_06"; rotation=False

# Finales Ergebnis: Energien in Größenordnung e-7
# (0.5, 0.5, 0.09401408)

# ---------------------------------------------------------------------------------------
# Grundlegende Konfiguration
# ---------------------------------------------------------------------------------------
# Modell und Symmetrie
# modeltype= "model_path_abs_4"; symmetry=1; no_a0 = False

# Ordnungen
p_order = 2
f_order = 17
l_order = 20
k_order = 3
p1_order = 0
p2_order = 0
p3_order = 0

# ---------------------------------------------------------------------------------------
# Zuschnitt des Dataframes der Energie
# ---------------------------------------------------------------------------------------
thz_cut_diff=False; thz_cut_band0=False; thz_cut_band1=False
cut_value_diff=0.0124; cut_value_bands=0.05

# ---------------------------------------------------------------------------------------
# Konfiguration der Plots
# ---------------------------------------------------------------------------------------
# Festlegung der Achsen
coord_system = "xyz" # möglich: "kxyz", "xyz", "xyz_scaled", "path", "tNB"

#Energie-Achse für alle Plots
plot_energy_axis = "diff"
plot_titel = ""

# ---------------------------------------------------------------------------------------
# 2D - Sliderpolts
# ---------------------------------------------------------------------------------------
plot_2Dplots = False
plot_model = False
axis_2D = "x"; nk_model = 1000; error = False

# ---------------------------------------------------------------------------------------
# 3D - Sliderpolts
# ---------------------------------------------------------------------------------------
plot_3Dplots = False
axis_3D = "z"

# ---------------------------------------------------------------------------------------
# 4D-Plots: Plot in 3D + Farbachse
# ---------------------------------------------------------------------------------------
plot_4Dplots = False
black_plot = False; plot_cube = True

# ---------------------------------------------------------------------------------------
# 4D Plots: PLot der Matrix-Impuls-Elemente
# ---------------------------------------------------------------------------------------
plot_4Dplots_mme_in_thz = False
merge_decimals = 5

# ---------------------------------------------------------------------------------------
# Plot der Gradienten und der Krümmung
# ---------------------------------------------------------------------------------------
plot_gradient = False
plot_curv = False
step = 5

# ---------------------------------------------------------------------------------------
# Plot der Fehler für verschiedene Ordnungen in 2D
# ---------------------------------------------------------------------------------------
plot_errors_2D = False
axis1 = "len_diff"
max_error_2D = None; thz_range_2D = True

# ---------------------------------------------------------------------------------------
# Plot der Fehler für verschiedene Ordnungen in 3D
# ---------------------------------------------------------------------------------------
plot_errors_3D = False
axis1_3D = "p_order"; axis2_3D = "k_order"
max_error_3D = None; thz_range_3D = True

if __name__ == "__main__":
    run(cfg=__import__(__name__))