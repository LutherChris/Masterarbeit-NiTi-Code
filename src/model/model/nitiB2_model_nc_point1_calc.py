import os
import sys
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))) # Erweitert den Arbeitsbereich von Python auf parallele Ordner.
from lib.run_model_calc import run

# ---------------------------------------------------------------------------------------
# feste Parameter aus der Schnittpunkte und Pfad-Berechnung
# ---------------------------------------------------------------------------------------
# Schnittpunkte-Berechnung
u = (1, 0, 0)
u = u / np.linalg.norm(u)
a = (0,1,0)
a = a / np.linalg.norm(a)
v = (0, 0, 0)
R = 0.345495616
r = 0.2
phi_steps = 48
bandnumbers = (14, 15)
zero = (0.345495616, 0.118331096, 0.118331096) # Punkt 1

# Pfad-Berechnung
coord_basis="xyz"
a_coeffs=[-0.7300042576783502, 1.7632114278333084, -9.04935814745873, 108.88722959947157]
b_coeffs=[-0.7299667586279922, 1.7696441060531072, -9.784393919450363, 50.20398048428685]
modeltype_path="path_point1"

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
# finales Gitter: Höhere Punkte-Dichte im Zentrum
k0=zero; p=(0.009, 0.04, 0); n=(19,34,60); grid_type="path"; datlabel="punkt1_center_thz"; rotation=False; path_phi_sym=1; path_no_rho0=False; path_rho_dense=0; path_rho_sigma=0.006; path_base_weight=0.2
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
intersect_point="point_1"

# ---------------------------------------------------------------------------------------
# Parameter für die Modellberechnung
# ---------------------------------------------------------------------------------------
#  0-te Polynom-Ordnungen weglassen?
no_a0 = False

# Maximale Anzahl an Koeffizienten
max_coeffs = 3000

# ---------------------------------------------------------------------------------------
#modeltype= "model_path_abs_4"; coord_system="path"; symmetry=1; no_000 = True; energy="diff"# Banddifferenz0
#modeltype= "model_path_abs_5"; coord_system="path"; symmetry=1; no_000 = True; energy="band0"# unteres Band
modeltype= "model_path_abs_5"; coord_system="path"; symmetry=1; no_000 = True; energy="band1"# oberes Band

p_order_list = [5]
f_order_list = [27]
l_order_list = [29]
k_order_list = [5]
p1_order_list = [0]
p2_order_list = [0]
p3_order_list = [0]

"""p_order_list = np.arange(2,6,1)
f_order_list = np.arange(20,30,1)
l_order_list = np.arange(20,30,1)
k_order_list = np.arange(2,6,1)
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
