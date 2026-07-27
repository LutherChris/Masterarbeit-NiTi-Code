import os
import sys
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))) # Erweitert den Arbeitsbereich von Python auf parallele Ordner.
from lib.run_model_plot import run

# #######################################################################################
# Haupt-Parameter
# #######################################################################################
# ---------------------------------------------------------------------------------------
# Parameter für 1. Berechnung des Gitters
# ---------------------------------------------------------------------------------------

# ===================================================================================
zero = (0.345495616, 0.118331096, 0.118331096) # Punkt 1
a_coeffs=[-0.7300042576783502, 1.7632114278333084, -9.04935814745873, 108.88722959947157]
b_coeffs=[-0.7299667586279922, 1.7696441060531072, -9.784393919450363, 50.20398048428685]
modeltype_path="path_point1"
# ===================================================================================
# finales Gitter: Höhere Punkte-Dichte im Zentrum
k0=zero; p=(0.009, 0.04, 0); n=(19,34,60); grid_type="path"; datlabel="punkt1_center_thz"; rotation=False; path_phi_sym=1; path_no_rho0=False; path_rho_dense=0; path_rho_sigma=0.006; path_base_weight=0.2
# ===================================================================================

# ===================================================================================

# ---------------------------------------------------------------------------------------
# Grundlegende Konfiguration
# ---------------------------------------------------------------------------------------
# Modell und Symmetrie
#modeltype= "model_path_abs_4"; coord_system="path"; symmetry=1; no_000 = True; energy="diff"; plot_energy_axis = "diff"
#modeltype= "model_path_abs_5"; coord_system="path"; symmetry=1; no_000 = True; energy="band0"; plot_energy_axis = "band0"# unteres Band
modeltype= "model_path_abs_5"; coord_system="path"; symmetry=1; no_000 = True; energy="band1"; plot_energy_axis = "band1"# oberes Band

# Ordnungen
p_order = 5
f_order = 27
l_order = 29
k_order = 5
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
coord_system = "path" # möglich: "kxyz", "xyz", "xyz_scaled", "path", "tNB"

#Energie-Achse für alle Plots
#plot_energy_axis = "band1"
plot_titel = ""

# ---------------------------------------------------------------------------------------
# 2D - Sliderpolts
# ---------------------------------------------------------------------------------------
plot_2Dplots = False
plot_model = True
axis_2D = "phi"; nk_model = 2000; error = False

# ---------------------------------------------------------------------------------------
# 3D - Sliderpolts
# ---------------------------------------------------------------------------------------
plot_3Dplots = False
axis_3D = "x"

# ---------------------------------------------------------------------------------------
# 4D-Plots: Plot in 3D + Farbachse
# ---------------------------------------------------------------------------------------
plot_4Dplots = False
black_plot = False; plot_cube = False

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
axis1 = "len_coeffs"
max_error_2D = 0.0001; thz_range_2D = True
max_error_2D = None
# ---------------------------------------------------------------------------------------
# Plot der Fehler für verschiedene Ordnungen in 3D
# ---------------------------------------------------------------------------------------
plot_errors_3D = False
axis1_3D = "f_order"; axis2_3D = "l_order"
max_error_3D = None; thz_range_3D = True

if __name__ == "__main__":
    run(cfg=__import__(__name__))