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
R = 0.345
r = 0.2
phi_steps = 48
bandnumbers = (14, 15)
zero = (R, 0.119, 0.119) # Startpunkt der Suche

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
# Berechnungen am Schnittpunkt 1, Gitterdefinition

# Gitter Nr 0 ; Punkteabstand 0.0002
#R = 0.345
#zero = (R, 0.119, 0.119)
#k0=zero; p=0.001; n=11; grid_type="regular"; datlabel="punkt1_find_00"; rotation=False

# Gitter Nr 1 ; Punkteabstand 0.00004
#k0=(0.3454, 0.1184, 0.1184); p=0.0002; n=11; grid_type="regular"; datlabel="punkt1_find_01"; rotation=False

# Gitter Nr 2 ; Punkteabstatnd 0.000008
#k0=(0.34548, 0.11834, 0.11834); p=0.00004; n=11; grid_type="regular"; datlabel="punkt1_find_02"; rotation=False

# Gitter Nr 3 ; Punkteabstand 0.0000016
#k0=(0.345496, 0.118332, 0.118332); p=0.000008; n=11; grid_type="regular"; datlabel="punkt1_find_03"; rotation=False

# Gitter Nr 4 ; Punkteabstand 3.2e-7
#k0=(0.345496, 0.118331, 0.118331); p=0.0000016; n=11; grid_type="regular"; datlabel="punkt1_find_04"; rotation=False

# Gitter Nr 5 ; Punkteabstand 6.4e-8
#k0=(0.34549568, 0.11833116, 0.11833116); p=0.00000032; n=11; grid_type="regular"; datlabel="punkt1_find_05"; rotation=False

# Finales Gitter Nr 6 (Kontrollgitter)
k0=(0.345495616, 0.118331096, 0.118331096); p=0.00000032; n=11; grid_type="regular"; datlabel="punkt1_find_06"; rotation=False

# Finales Ergebnis: Energien in Größenordnung e-7
# (0.345495616, 0.118331096, 0.118331096)

# ---------------------------------------------------------------------------------------
# grundlegende Prameter für 5. und 7. 
# ---------------------------------------------------------------------------------------
# Energie, an dem die Berechnungen durchgeführt werden 
energy="diff"

# verwendete Koordinatenachsen für Analysis und Modellierung    
#coord_system="path"
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
find_intersection=True
intersect_point="point_1"

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
p_order_list = [2]
f_order_list = [17]
l_order_list = [20]
k_order_list = [3]
p1_order_list = [0]
p2_order_list = [0]
p3_order_list = [0]

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
