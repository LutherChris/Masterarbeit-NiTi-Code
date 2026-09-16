import os
import sys
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))) # Erweitert den Arbeitsbereich von Python auf parallele Ordner.
from lib.run_model_calc import run

# ---------------------------------------------------------------------------------------
# feste Parameter aus der Schnittpunkte und Pfad-Berechnung
# ---------------------------------------------------------------------------------------
# Schnittpunkte-Berechnung
u = (0, 0, 1)
u = u / np.linalg.norm(u)
a = (1, 1, 0)
a = a / np.linalg.norm(a)
v = (0.5, 0.5, 0)
R = 0.09513568
r = 0.05
phi_steps = 48
bandnumbers = (14, 15)
zero = (0.5, 0.5, 0.09513568) # Punkt 3

# Pfad-Berechnung
coord_basis="xyz"
a_coeffs = None
b_coeffs = None
modeltype_path="path_point3"

# #######################################################################################
# Haupt-Parameter zur aktivierung der Blöcke
# #######################################################################################

# 1. Berechnung des Gitters ist dauerhaft aktiv
# 2. Plot des Gitters
plot_grid = False
# 3. Berechnung der Bandenergien durch Quantum Espresso
calc_dft = False
# 4. Berechnung der Matrix-Impuls-Elemente durch QE
calc_mme = False
# 5. Berechnung, Analyse und Anpassung der Dataframes
analysis = False
# ---------------------------------------------------------------------------------------
# 6. Laden der pandas-Dataframe
load_csv = False
# 7. Modellierung mit Schleife über alle Ordnungen
calc_model = False

# ---------------------------------------------------------------------------------------
# grundlegende Prameter für 5. und 7. 
# ---------------------------------------------------------------------------------------
# Energie, an dem die Berechnungen durchgeführt werden 
energy="diff"

# verwendete Koordinatenachsen für Analysis und Modellierung    
coord_system="path" 

# ---------------------------------------------------------------------------------------
# Parameter für 1. Berechnung des Gitters
# ---------------------------------------------------------------------------------------
# =======================================================================================
# finales Gitter: Bestimmung des THz-aktiven Bereichs in rho-Richtung - bislang bekannt: t-Intervall
#k0=zero; p=(0.008, 0.02, 0); n=(41,40,4); grid_type="path"; datlabel="punkt3_rho"; path_phi_sym=4

# finales Gitter:
k0=zero; p=(0.007, 0.019, 0); n=(21,28,64); grid_type="path"; datlabel="punkt3_center_thz"; path_phi_sym=4; path_no_rho0=False; path_rho_dense=0; path_rho_sigma=0.006; path_base_weight=0.2
# =======================================================================================

# ---------------------------------------------------------------------------------------
# Parameter für 5. Berechnung, Analyse und Anpassung der Dataframes
# ---------------------------------------------------------------------------------------
# Hauptkomponentenanalyse
pca=False

# Entfernung von 0-Werten aus den Daten
no_000=False

# Filterung des Dataframes auf den THz-aktiven Bereich
cut_df_for_fit=False
cut_value_diff=0.0124; cut_value_bands=0.05; complete_cut=True

# Berechnung der statistischen Werte der Matrix-Impuls-Elemente
mme_statistics=False
merge_decimals=5

# Berechnung des Schnittpunktes
find_intersection=False
intersect_point="point_3"

# ---------------------------------------------------------------------------------------
# Parameter für die Modellberechnung
# ---------------------------------------------------------------------------------------
#  0-te Polynom-Ordnungen weglassen?
no_a0 = False

# Maximale Anzahl an Koeffizienten
max_coeffs = 2000

# ---------------------------------------------------------------------------------------
#modeltype="model_path_point3_2"; coord_system="path"; symmetry=4; no_000 = True; energy="diff" # Differenz
#modeltype="model_path_point3_3"; coord_system="path"; symmetry=4; no_000 = True; energy="band0" # unteres Band
modeltype="model_path_point3_3"; coord_system="path"; symmetry=4; no_000 = True; energy="band1" # oberes Band

# Zu berechnende Ordnungen
p_order_list = [3]
f_order_list = [0]
l_order_list = [5]
k_order_list = [3]
p1_order_list = [0]
p2_order_list = [0]
p3_order_list = [0]

"""p_order_list = np.arange(1, 6, 1)
f_order_list = [0]
l_order_list = np.arange(1, 8, 1)
k_order_list = np.arange(1, 6, 1)
p1_order_list = [0]
p2_order_list = [0]
p3_order_list = [0]"""

# Anpassung des (einzigen!) konstanten Koeffizienten
a0_correction = False

# Ridge-Lösungsverfahren anstatt linearer Regression
ridgeCV = False 
ridge_alphas = np.logspace(-6, 2, 9) 

# Spaltenskalierung der Design-Matrix
col_weighting = True

# Speichern der Fehler als csv-Datei
save_errors = False

if __name__ == "__main__":
    run(cfg=__import__(__name__))
