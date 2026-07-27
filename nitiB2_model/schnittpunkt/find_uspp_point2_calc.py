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
R = 0.525 # Punkt 2A
r = 0.1
phi_steps = 48
bandnumbers = (14, 15)

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
# Berechnungen am Schnittpunkt 2A, Gitterdefinition

# Gitter Nr 0 ; Punkteabstand 0.0002
#zero = (0.303, 0.303, 0.303) # Startpunkt der Suche
#k0=zero; p=0.001; n=11; grid_type="regular"; datlabel="punkt2_find_00"; rotation=False

# Gitter Nr 1 ; Punkteabstand 0.00004
#k0=(0.3032, 0.3032, 0.3032); p=0.0002; n=11; grid_type="regular"; datlabel="punkt2_find_01"; rotation=False

# Gitter Nr 2 ; Punkteabstand 0.000008
#k0=(0.30312, 0.30312, 0.30312); p=0.00004; n=11; grid_type="regular"; datlabel="punkt2_find_02"; rotation=False

# Gitter Nr 3 ; Punkteabstand 0.0000016
#k0=(0.30312, 0.30312, 0.30312); p=0.000008; n=11; grid_type="regular"; datlabel="punkt2_find_03"; rotation=False

# Gitter Nr 4 ; Punkteabstand 3.2e-7
#k0=(0.3031232, 0.3031232, 0.3031232); p=0.0000016; n=11; grid_type="regular"; datlabel="punkt2_find_04"; rotation=False

# Finales Gitter Nr 5 (Kontrollgitter)
k0=(0.30312352, 0.30312352, 0.30312352); p=0.0000016; n=11; grid_type="regular"; datlabel="punkt2_find_05"; rotation=False

# Finales Ergebnis: Energien in Größenordnung e-7
# (0.30312352, 0.30312352, 0.30312352)


# =======================================================================================
# Berechnungen am Schnittpunkt 2B, Gitterdefinition

# Gitter Nr 0 ; Punkteabstand 0.0004
#zero = (0.314, 0.314, 0.28) # Startpunkt der Suche
#k0=zero; p=0.002; n=11; grid_type="regular"; datlabel="punkt2B_find_00"; rotation=False

# Gitter Nr 1 ; Punkteabstand 0.0002
#k0=(0.3136, 0.3136, 0.2804); p=0.001; n=11; grid_type="regular"; datlabel="punkt2B_find_01"; rotation=False

# Gitter Nr 2 ; Punkteabstand 0.00004
#k0=(0.3136, 0.3136, 0.2804); p=0.0002; n=11; grid_type="regular"; datlabel="punkt2B_find_02"; rotation=False

# Gitter Nr 3 ; Punkteabstand 0.000008
#k0=(0.31364, 0.31364, 0.28028); p=0.00004; n=11; grid_type="regular"; datlabel="punkt2B_find_03"; rotation=False

# Gitter Nr 4 ; Punkteabstand 0.0000016
#k0=(0.313632, 0.313632, 0.280296); p=0.000008; n=11; grid_type="regular"; datlabel="punkt2B_find_04"; rotation=False

# Gitter Nr 5 ; Punkteabstand 3.2e-7
#k0=(0.313632, 0.313632, 0.280296); p=0.0000016; n=11; grid_type="regular"; datlabel="punkt2B_find_05"; rotation=False

# Finales Gitter Nr 6 (Kontrollgitter)
#k0=(0.31363232, 0.31363232, 0.280296); p=0.0000016; n=11; grid_type="regular"; datlabel="punkt2B_find_06"; rotation=False

# Finales Ergebnis: Energien in Größenordnung e-7
# (0.31363232, 0.31363232, 0.280296)

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
intersect_point="point_2A"

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
