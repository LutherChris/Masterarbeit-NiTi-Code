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
zero = (0.30312352, 0.30312352, 0.30312352) # Punkt 2A
a_coeffs=[0.01148933207155924, 1.6317263844478398, 9.795159198026282, 99.08785267481657, 382.3674749566283]
b_coeffs=None
modeltype_path="path_point2B"
# ===================================================================================
# finales Gitter: Bestimmung des THz-aktiven Bereichs in rho-Richtung - bislang bekannt: t-Intervall
#k0=zero; p=(0.007, 0.05, 0); n=(41,120,3); grid_type="path_grid_2B"; datlabel="punkt2_rho"; rotation=False; path_phi_sym=3; path_phi_sigma=(np.pi/180)*5; path_rho_sigma=0.003; path_rho_sigmaB=0.006; path_no_rho0=False

# finales Gitter:modeltype_path
k0=zero; p=(0.007, 0.05, 0); n=(21,29,60); grid_type="path_grid_2B"; datlabel="punkt2_2A2B"; rotation=False; path_phi_sym=3; path_phi_sigma=(np.pi/180)*5; path_rho_sigma=0.003; path_rho_sigmaB=0.006; path_no_rho0=False
# ===================================================================================

# ===================================================================================

# ---------------------------------------------------------------------------------------
# Grundlegende Konfiguration
# ---------------------------------------------------------------------------------------
# Modell und Symmetrie
#modeltype = "model_path_point2_2"; coord_system="path"; symmetry=3; no_000 = True; energy="diff"; plot_energy_axis = "diff" # Differenz
#modeltype = "model_path_point2_3"; coord_system="path"; symmetry=3; no_000 = True; energy="band0"; plot_energy_axis = "band0" # # unteres Band
#modeltype = "model_path_point2_3"; coord_system="path"; symmetry=3; no_000 = True; energy="band1"; plot_energy_axis = "band1" # # oberes Band

# Ordnungen
p_order = 3
f_order = 0
l_order = 0
k_order = 5
p1_order = 3
p2_order = 0
p3_order = 0

# ---------------------------------------------------------------------------------------
# Zuschnitt des Dataframes der Energie
# ---------------------------------------------------------------------------------------
thz_cut_diff=True; thz_cut_band0=True; thz_cut_band1=True
cut_value_diff=0.0124; cut_value_bands=0.05

# ---------------------------------------------------------------------------------------
# Konfiguration der Plots
# ---------------------------------------------------------------------------------------
# Festlegung der Achsen
coord_system = "kxyz" # möglich: "kxyz", "xyz", "xyz_scaled", "path", "tNB"

#Energie-Achse für alle Plots
plot_energy_axis = "pz"
plot_titel = ""

# ---------------------------------------------------------------------------------------
# 2D - Sliderpolts
# ---------------------------------------------------------------------------------------
plot_2Dplots = False
plot_model = True
axis_2D = "t"; nk_model = 200; error = False

# ---------------------------------------------------------------------------------------
# 3D - Sliderpolts
# ---------------------------------------------------------------------------------------
plot_3Dplots = False
axis_3D = "z"

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
#max_error_2D = None

# ---------------------------------------------------------------------------------------
# Plot der Fehler für verschiedene Ordnungen in 3D
# ---------------------------------------------------------------------------------------
plot_errors_3D = False
axis1_3D = "p_order"; axis2_3D = "p1_order"
max_error_3D = None; thz_range_3D = True

if __name__ == "__main__":
    run(cfg=__import__(__name__))