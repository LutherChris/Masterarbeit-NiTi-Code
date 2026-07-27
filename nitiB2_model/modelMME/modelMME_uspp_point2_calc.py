import os
import sys
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))) # Erweitert den Arbeitsbereich von Python auf parallele Ordner.
from lib.run_model_calc import run

# ---------------------------------------------------------------------------------------
# feste Parameter aus der Schnittpunkte und Pfad-Berechnung
# ---------------------------------------------------------------------------------------
# Schnittpunkte-Berechnung
u = (1, 1, 1)
u = u / np.linalg.norm(u)
a = (1, 1, -2)
a = a / np.linalg.norm(a)
v = (0, 0, 0)
R = 0.5250253376091207 # Punkt 2A
r = 0.1
phi_steps = 48
bandnumbers = (14, 15)
zero = (0.30312352, 0.30312352, 0.30312352) # Punkt 2A

# Pfad-Berechnung
coord_basis="xyz"
a_coeffs=[0.01148933207155924, 1.6317263844478398, 9.795159198026282, 99.08785267481657, 382.3674749566283]
b_coeffs=None
modeltype_path="path_point2B"

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
# ===================================================================================
# finales Gitter: Bestimmung des THz-aktiven Bereichs in rho-Richtung - bislang bekannt: t-Intervall
#k0=zero; p=(0.007, 0.05, 0); n=(41,120,3); grid_type="path_grid_2B"; datlabel="punkt2_rho"; rotation=False; path_phi_sym=3; path_phi_sigma=(np.pi/180)*5; path_rho_sigma=0.003; path_rho_sigmaB=0.006; path_no_rho0=False

# finales Gitter:
k0=zero; p=(0.007, 0.05, 0); n=(21,29,60); grid_type="path_grid_2B"; datlabel="punkt2_2A2B"; rotation=False; path_phi_sym=3; path_phi_sigma=(np.pi/180)*5; path_rho_sigma=0.003; path_rho_sigmaB=0.006; path_no_rho0=False

# Kontrollgitter:
#k0=zero; p=(0.007, 0.05, 0); n=(21,29,60); grid_type="path_grid_2B"; datlabel="punkt2_2A2B_kontrolle"; rotation=False; path_phi_sym=3; path_phi_sigma=None; path_rho_sigma=None; path_rho_sigmaB=None; path_no_rho0=False
# ===================================================================================

# ---------------------------------------------------------------------------------------
# Parameter für 5. Berechnung, Analyse und Anpassung der Dataframes
# ---------------------------------------------------------------------------------------
# Hauptkomponentenanalyse
pca=False

# Entfernung von 0-Werten aus den Daten
no_000=False

# Filterung des Dataframes auf den THz-aktiven Bereich
cut_df_for_fit=True
cut_value_diff=0.0124; cut_value_bands=0.05; complete_cut=True

# Berechnung der statistischen Werte der Matrix-Impuls-Elemente
mme_statistics=True
merge_decimals=5

# Berechnung des Schnittpunktes
find_intersection=False
intersect_point="point_2A"

# ---------------------------------------------------------------------------------------
# Parameter für die Modellberechnung
# ---------------------------------------------------------------------------------------
#  0-te Polynom-Ordnungen weglassen?
no_a0 = False

# Maximale Anzahl an Koeffizienten
max_coeffs = 3000

# ---------------------------------------------------------------------------------------

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
