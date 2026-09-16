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
R = 0.09401408 # Punkt 3
r = 0.05
phi_steps = 48
bandnumbers = (14, 15)
# Schnittpunkt der Bänder bei der Fermi-Energie
zero = (0.5, 0.5, 0.09401408) # Punkt 3

# #######################################################################################
# Haupt-Parameter zur Aktivierung der Blöcke
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

# #######################################################################################

# ---------------------------------------------------------------------------------------
# Parameter für 1. Berechnung des Gitters
# ---------------------------------------------------------------------------------------
# Berechnungen am Schnittpunkt, Gitterdefinition zur Pfadsuche
k0=zero; p=(0, 0, 0.06); n=(1,1,1001); grid_type="regular"; datlabel = "punkt3_000"; rotation=False
# ---------------------------------------------------------------------------------------
# grundlegende Prameter für 5. und 7. 
# ---------------------------------------------------------------------------------------
# Energie, an dem die Berechnungen durchgeführt werden 
energy="diff"

# verwendete Koordinatenachsen für Analysis und Modellierung    
coord_system="xyz"

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
# Parameter für 7. Modellberechnung
# ---------------------------------------------------------------------------------------
#  0-te Polynom-Ordnungen weglassen?
no_a0 = False

# Maximale Anzahl an Koeffizienten
max_coeffs = 10000

# Konfiguration
# HINWEIS: hier sollte nochmal alles spezifisch wichtige für das jeweilige Modell festgelegt sein, auch wenn es einige Parameter wie energy und coord_system usw von oben überschreibt.


# Zu berechnende Ordnungen
p_order_list = []
f_order_list = []
l_order_list = []
k_order_list = []
p1_order_list = []
p2_order_list = []
p3_order_list = []

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
