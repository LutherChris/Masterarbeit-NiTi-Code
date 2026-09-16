import os
import os.path
import numpy as np
import pandas as pd
from itertools import product
import matplotlib.pyplot as plt

import lib.qe_model_calc as model
import lib.config as config
from lib.plot_config import PLOT_SETTINGS

"""
Diese Datei lädt cfg.-Parameter aus z.B. model_uspp_point1_calc.py und führt den folgenden Aufbau aus.
Abschnitte sind teilweise optional und werden über Parameter aktiviert.

# =======================================================================================
# grundsätzlicher Aufbau:
# =======================================================================================
Hauptparameter: grid_type, rotation, plot_grid 
1. Berechnung des Gitter mit der Hilfsfunktion (make_grid)
    - Festlegung des Gitters durch den Parameter cfg.grid_type und entsprechende Funktionsvariablen
    - Rotation bei bestimmten Gittertypen
2.  - Plot des Gitters

# ---------------------------------------------------------------------------------------
Hauptparameter: calc_dft
3. Berechnung der Bandenergie durch Quantum Espresso

# ---------------------------------------------------------------------------------------
Hauptparameter: calc_mme
4. Berechnung der Matrix-Impuls-Elemente (MME) durch Quantum Espresso

# ---------------------------------------------------------------------------------------
Hauptparameter: analysis
5. Einlesen der Ausgabe-Dateien und Analyse/Anpassung des Dataframes der Energie und der MME mit den folgenden Hilfsfunktionen:
    - Hilfsfunktion (make_analysis_energy) zur Berechnung/Analyse/Anpassung des Dataframes der Energie
        - lädt Daten aus der xml-Datei von Quantum Espresso und speichert diese als pandas-Dataframe
        - Koordinatentransformationen:
            - Skalierung des Gitters
            - Transformation des Gitters in Pfadvektoren
        - Hauptkomponentenanalyse
        - Entfernen von 0-Werten aus den Daten (z.B. Koordinatenursprung)
        - Zuschnitt auf den THz-aktiven Bereich
    - Hilfsfunktion (make_analysis_mme) zur Berechnung/Analyse/Anpassung des Dataframes der Matrix-Impuls-Elemente
        - läst Daten aus der Ausgabe-Datei der Quantum Espresso Berechnung und speichert diese als pandas-Dataframe
        - Berechnung statistischer Größen für die Matrix-Impuls-Elemente

# ---------------------------------------------------------------------------------------
Hauptparameter: load_scv
6. Laden der pandas-Dataframes

# ---------------------------------------------------------------------------------------
Hauptparameter: calc_model
7. Modellierung mit der Hilfsfunktion (make_model) über alle Ordnungen
    - Anpassung des (einzigen!) konstanten Koeffizienten
    - Auswertung des Modells auf dem Gitter und Berechnung der macimalen Fehler an den Gitterpunkten

# =======================================================================================
# Übersicht aller Parameter
# =======================================================================================
- Grundsätzliche Koordinatensysteme:
k_grid_center:      {x,y,z} = Gitter im Zentrum, egal welche Art des Gitter-Typs
k_grid:             {kx,ky,kz} = Gitter für Quantum Espresso
k_grid_rot:         {kx',ky',kz'} = Gedrehtes Gitter für Quantum Espresso
t_grid:             {t,rho,phi} = Gitter für Polarkoordinaten entlang des Pfades
v_grid:             {t,vN,vB} = Gitter mit verschobenen Pfaden in N- und B-Richung
                        vN = Komponente des Normalenvektors
                        vB = Komponente des Binormalenvektors
# ---------------------------------------------------------------------------------------
# feste Parameter
# ---------------------------------------------------------------------------------------
# aus thz Untersuchung
cfg.u:              (list) Einheitsvektor der Ursprungsgerade, um die gedreht wird
cfg.a:              (list) Einheitsvektor für Anfangspfad, der orthogonal zu u liegt
cfg.v:              (list) Verschiebevektor für den Anfangspfad
cfg.R:              (float) Radius für den Einheitsvektor u
cfg.r:              (float) Radius für den Einheitsvektor a
cfg.phi_steps:      (int) Anzahl der Zwischenpfade zwischen 0° und 180°
cfg.bandnumbers:    (list) Auswahl der Bänder für die Auslesung der xml-Datei von QE

# aus der Pfad-Bestimmung
cfg.coord_basis:    (str) Welches Koordinatensystem wurde bei der Pfad-Bestimmung verwendet?
                        "xyz" oder "xyz_scaled"
cfg.a_coeffs:       (list) a-Koeffizienten von r(t)
cfg.b_coeffs:       (list) b-Koeffizienten von r(t)
cfg.modeltype_path: (str) Modell des Pfades
                        "path_point1": Pfad für Punkt1
                        "path_point2A": Pfad für Punkt2A
                        "path_point2B": Pfad für Punkt2B
                        "path_point3": Pfad für Punkt3
                        "path_point1_center": Pfad für Punkt1 entlang des Zentrums der Schale
cfg.decimals:       (float) legt fest, auf wie viele Nachkommastellen die QE-Vektoren gerundet werden, standart:12
# #######################################################################################
# Haupt-Parameter zur Aktivierung der Blöcke
# #######################################################################################
cfg.plot_grid:      (bool) Soll das Gitter geplottet werden?
cfg.calc_dft:       (bool) aktiviert DFT-Rechnung der Energie durch Quantum Espresso (QE)
cfg.calc_mme        (bool) aktiviert DFT-Rechnung der Matrix-Impuls-Elemente durch QE
cfg.analysis:       (bool) aktiviert analysis-Block nach der DFT-Rechnungg

cfg.load_csv:       (bool) aktiviert Laden der csv-Dateien nach der Analyse
cfg.calc_model:     (bool) aktiverit Modell-Berechnungen

# ---------------------------------------------------------------------------------------
# grundlegende Prameter für 5. und 7. 
# ---------------------------------------------------------------------------------------
cfg.energy:         (str) Energie, an dem die Berechnungen durchgeführt werden
                        "diff": Energiedifferenz
                        "band0": unteres Band
                        "band1": oberes Band

cfg.coord_system:   (str) Wählt bestimmte Achsen des Koordinatensystems aus dem Dataframe, um Berechnungen im Block Analyse und Modellierung durchzuführen
                "kxyz":       Originales Koordinatensystem - Achsen: ("kx", "ky", "kz")
                "xyz":        Koordinatensystem im Zentrum - Achsen: ("x", "y", "z")
                "xyz_scaled": skaliertes Koordinatensystem im Zentrum auf [-1,1] - Achsen: ("x_scaled", "y_scaled", "z_scaled")
                "path":       Koordinatensysteme entlang des Pfades r(t) - Achsen: ("t", "rho", "phi")
                "tNB":        Koordinatensystem der verschobenen Pfade r(t)

    Bemerkung: Wenn coord_sytem="path" aber grid_type kein Pfad-Koordinatensystem ist,
    dann werden die Achsen ("t", "rho", "phi") numerisch durch die Koordinatentransformation berechnet.
    Dabei werden folgende Parameter verwendet:
cfg.bounds:         (list) Intervall von t für Suche des Minimums
cfg.tol:            (float) Toleranz für Nichtorthogonalität
cfg.xatol:          (flaot) Toleranz in der Suchfunktion des Minimums

# ---------------------------------------------------------------------------------------
# Parameter für 1. Berechnung des Gitters
# ---------------------------------------------------------------------------------------
cfg.k0:             (list) Versatzvektors für das Gitter im Ursprung (zero oder zero_0)
cfg.p:              (float),(list) Gitterlängen-array bzw. float des Gitters
cfg.n:              (int),(list) Anzahl-der-Datenpunkte-array bzw. float des Gitters
cfg.grid_type:      (str) Definiert die Form des Gitters; Beispiel: 
                        "regular"=kartesisches Gitter
                        "cylindrical"=Zylindrisches Gitter
                        "path"=Polargitter entlang des Pfades
                        "path_grid_semi_regular"=regelmäßiges Gitter aus Verschiebung des Pfades
                        "path_grid_2B"=Gitter für Punkt2A und Punkt2B
cfg.datlabel:       (str) Label in Dateienname (Für Ordner und Dateien)

# Rotation des Gitters
cfg.rotation:       (bool) aktiviert die Rotation des Gitters {x,y,z}->{kx',ky',kz'}
cfg.u_axis:         (list) bei rotation=True ursprüngliche Hauptachse des k-Gitters zB(0,0,1)
cfg.a_axis:         (list) bei Rotation=True Zielachse des neuen Gitters zB(0,1,1)

# speziell bei grid_type="cylindrical":
cfg.z_axis:         (list) Hauptachse des Zylinders
cfg.phi_sym:        (int) Anzahl der Symmetrie-Sektoren 
cfg.R_dense:        (float) Radius der radialen Gaus-Dichte
cfg.r_sigma:        (float) Stärke der radialen Gaus-Dichte
cfg.n_phi_min:      (int) Minimale Anzahl an phi-Punkten pro Sym.Sektor
cfg.base_weight:    (float) Basiswert für Dichte außerhalb des Gauß

# speziell bei grid_type="path":
cfg.path_phi_sym    (int) Anzahl der Symmetrie-Sektoren, keine Symmetrie: {0,1}
cfg.path_n_phi_min  (int) Minimale Anzahl an phi-Punkten pro Sym.Sektor
cfg.non_equidistant (float) verschobane Winkel um  non_equidistant*np.sin(np.arange(n_phi))
cfg.path_rho_dense  (float) Radius der radialen Gaus-Dichte
cfg.path_rho_sigma  (float) Stärke der radialen Gaus-Dichte
cfg.path_base_weight(float) Basiswert für Dichte außerhalb des Gauß
cfg.path_no_rho0    (bool) Punkte mit rho=0 werden nicht definiert

# speziell bei grid_type="path_grid_2B":
cfg.path_phi_sym    (int) Anzahl der Symmetrie-Sektoren, keine Symmetrie: {0,1}
cfg.path_phi_sigma  (float) phi-abhängige Gauß-Verdichtung um Punkte 2B in Abhängigkeit von t
cfg.path_rho_sigma  (float) Stärke der radialen Gaus-Dichte um rho=0 (Punkt2A)
cfg.path_rho_sigmaB (float) Stärke der radialen Gaus-Dichte um rho=0 (Punkt2A) in Abhängigkeit von t
cfg.path_no_rho0    (bool) Punkte mit rho=0 werden nicht definiert

# ---------------------------------------------------------------------------------------
# Parameter für 5. Berechnung, Analyse und Anpassung der Dataframes
# ---------------------------------------------------------------------------------------
# Hauptkomponentenanalyse
cfg.pca:            (bool) aktiviert Hauptkomponentenanalyse im analysis-Block

# Entfernung von 0-Werten aus den Daten
cfg.no_000:         (bool) aktiviert die Entfernung von 0-Werten aus den Daten
        wenn coord_system="xyz: entfernt x=y=z=0 aus den Daten vor der Modellierung
        wenn coord_system="path: entfernt rho=0 aus den Daten vor der Modellierung

# Filterung des Dataframes auf den THz-aktiven Bereich
cfg.cut_df_for_fit: (bool) aktiviert die Filterung des Dataframes auf den thz-aktiven Bereich
cfg.cut_value_diff:     (float) THz-Bedingung für die Differenz der Bänder
cfg.cut_value_bands:    (float) THz-Bedingung für die Bänder
cfg.complete_cut:       (bool) Die Bänder werden exakt auf die THz-Bedingungen zugeschnitten!

# Berechnung des Schnittpunktes k0
cfg.find_intersection:  (bool) Soll der Schnittpunkt k0 im Dataframe berechnet werden?
cfg.intersect_point:    (str) Um welchen Schnittpunkt handelt es sich?

# Berechnung der statistischen Werte der Matrix-Impuls-Elemente
cfg.mme_statistics:     (bool) aktiviert die Berechnung der statistischen Werte der Matrix-Impuls-Elemente
cfg.merge_decimals: (int) Anzahl der Nachkommastellen, auf denen die Dataframes miteinander verglichen werden

# ---------------------------------------------------------------------------------------
# Parameter für 7. Modellberechnung
# ---------------------------------------------------------------------------------------
#  0-te Polynom-Ordnungen weglassen?
cfg.no_a0:          (bool) Soll in den Polynommodellen die 0-te Ordnung weggelassen werden?

# Maximale Anzahl an Koeffizienten
cfg.max_coeffs:     (int) Maximale Anzahl an Koeffizienten zum Abbruch bei Modellberechnungen

# Konfiguration
cfg.modeltype:      (str) legt den Modell-Typ fest
cfg.symmetry:       (int),(None) Symmetriefaktor in den Modell-Funktionen

# Zu berechnende Ordnungen
cfg.p_order_list:   (list) p-Ordnungen für die Modellberechnungsschleife
cfg.f_order_list:   (list) f-Ordnungen für die Modellberechnungsschleife
cfg.l_order_list:   (list) l-Ordnungen für die Modellberechnungsschleife
cfg.k_order_list:   (list) k-Ordnungen für die Modellberechnungsschleife
cfg.p1_order_list:  (list) p1-Ordnungen für die Modellberechnungsschleife
cfg.p2_order_list:  (list) p2-Ordnungen für die Modellberechnungsschleife
cfg.p3_order_list:  (list) p3-Ordnungen für die Modellberechnungsschleife

# Anpassung des (einzigen!) konstanten Koeffizienten
cfg.a0_correction:  (bool) Verschiebung der konstanten Ordnung für Energie bei (0,0,0)
                    Achtung: Funktioniert nur, wenn erster Koeffizient der (einzige!) konstante Term

# Ridge-Lösungsverfahren anstatt linearer Regression
cfg.ridgeCV:        (bool) aktiviert Ridge-Lösungsverfahren anstatt lineare Regression
cfg.ridge_alphas:   (list) Liste von alphas im Ridge-Verfahren zum testen

# Spaltenskalierung der Datenmatrix
cfg.col_weighting:  (bool) aktiviert Spaltenskalierung der Datenmatrix nach GOLUB & VAN LOAN

# Speichern der Fehler als csv-Datei
cfg.save_errors:    (bool) speichert die Fehler der Modell-Berechnungen

- Modeltypen siehe qe_model_models.py
- Rotation der Gitter funktioniert in Winkelsystemen nicht, da sie mit einer Matrix rotiert wird und die Anzahl der Datenpunkte pro Achse gleich bleiben muss
- bei Rotation funktioniert die Gradient und Krümmungsberechnung nicht (pca). Die Numpy-Funktionen benötigen ein regelmäßiges Gitter.
"""

def run(cfg):
    # Laden der Plot-Einstellungen aus plot_config.py
    plt.rcParams.update(PLOT_SETTINGS)
    
    # ###################################################################################
    # Standard-Parameter, wenn nicht vorhanden
    decimals = cfg.decimals if hasattr(cfg, "decimals") else (print("Achtung: 'decimals' fehlt - setze Standard: 12"), 12)[1]
    rotation = cfg.rotation if hasattr(cfg, "rotation") else (print("Achtung: 'rotation' fehlt - setze Standard: False"), False)[1]             
    modeltype = cfg.modeltype if hasattr(cfg, "modeltype") else (print("Achtung: 'modeltype' fehlt - setze Standard: 'out-Dateien'"), "out-Dateien")[1]
    symmetry = cfg.symmetry if hasattr(cfg, "symmetry") else (print("Achtung: 'symmetry' fehlt - setze Standard: 1"), 1)[1]
    no_a0 = cfg.no_a0 if hasattr(cfg, "no_a0") else (print("Achtung: 'no_a0' fehlt - setze Standard: False"), False)[1]

    coord_basis = cfg.coord_basis if hasattr(cfg, "coord_basis") else (print("Achtung: 'coord_basis' fehlt - noch keine Pfad-Berechnung? - setze: None"), None)[1]
    a_coeffs = cfg.a_coeffs if hasattr(cfg, "a_coeffs") else (print("Achtung: 'a_coeffs' fehlt - noch keine Pfad-Berechnung? - setze: []"), None)[1]
    b_coeffs = cfg.b_coeffs if hasattr(cfg, "b_coeffs") else (print("Achtung: 'b_coeffs' fehlt - noch keine Pfad-Berechnung? - setze: []"), None)[1]
    modeltype_path = cfg.modeltype_path if hasattr(cfg, "modeltype_path") else (print("Achtung: 'modeltype_path' fehlt - noch keine Pfad-Berechnung? - setze: None"), None)[1]
    
    # ###################################################################################
    # Hilfsfunktionen für:
    #   Generierung des Gitters
    #   Berechnung/Analyse/Anpassung des Dataframes der Energie
    #   Berechnung/Analyse des Dataframes der Matrix-Impuls-Elemente
    #   Berechnung des Modells
    # ###################################################################################

    def make_grid(p, n, grid_type, rotation, plot=False):
        """
        - Generierung der Gitter, je nachdem welche Form und ob es rotiert wird
        - Rotation des Gitters für bestimmte Gittertypen (optional)
        - Plotten des Gitters (optional)
        """
        print(f"Generierung des Gitters: grid_type={grid_type}")

        # -------------------------------------------------------------------------------
        # Festlegung des Gitters durch Parameter grid_type und entsprechende Funktionsvariablen; optionale Rotation für bestimmte Gittertypen
        # -------------------------------------------------------------------------------
        if grid_type == "regular":
            print("- kartesisches Gitters")
            k_grid, k_grid_center, coords = model.regular_grid(cfg.k0, p, n, decimals=decimals)
            t_grid, v_grid = None, None
            if rotation:
                print(f"- Rotation des Gitters:")
                k_grid, coords = model.rotation_grid(k_grid_center, cfg.k0, cfg.u_axis, cfg.a_axis, decimals=decimals)
        elif grid_type == "cylindrical":
            print("- zylindrisches Gitter")

            # Standartparameter
            z_axis = cfg.z_axis if hasattr(cfg, "z_axis") else (print("Achtung: 'z_axis' fehlt - setze Standard: None"), None)[1]
            phi_sym = cfg.phi_sym if hasattr(cfg, "phi_sym") else (print("Achtung: 'phi_sym' fehlt - setze Standard: 1"), 1)[1]
            n_phi_min = cfg.n_phi_min if hasattr(cfg, "n_phi_min") else (print("Achtung: 'n_phi_min' fehlt - setze Standard: 2"), 2)[1]
            R_dense = cfg.R_dense if hasattr(cfg, "R_dense") else (print("Achtung: 'R_dense' fehlt - setze Standard: None"), None)[1]
            r_sigma = cfg.r_sigma if hasattr(cfg, "r_sigma") else (print("Achtung: 'r_sigma' fehlt - setze Standard: None"), None)[1]
            base_weight = cfg.base_weight if hasattr(cfg, "base_weight") else (print("Achtung: 'base_weight' fehlt - setze Standard: 0.25"), 0.25)[1]

            
            k_grid, k_grid_center, coords = model.cylindrical_grid(cfg.k0, z_axis, p, n, phi_sym, n_phi_min, R_dense, r_sigma, base_weight, decimals=decimals)
            t_grid, v_grid = None, None
            if rotation:
                raise ValueError(f"Achtung: Rotation funktioniert nicht in diesem Gitter!")
        elif grid_type == "path":
            print("- Polar-Gitter entlang des Pfades")

            # Standartparameter
            path_phi_sym = cfg.path_phi_sym if hasattr(cfg, "path_phi_sym") else (print("Achtung: 'path_phi_sym' fehlt - setze Standard: 1"), 1)[1]
            path_n_phi_min = cfg.path_n_phi_min if hasattr(cfg, "path_n_phi_min") else (print("Achtung: 'path_n_phi_min' fehlt - setze Standard: None"), None)[1]
            non_equidistant = cfg.non_equidistant if hasattr(cfg, "non_equidistant") else (print("Achtung: 'non_equidistant' fehlt - setze Standard: None"), None)[1]
            path_rho_dense = cfg.path_rho_dense if hasattr(cfg, "path_rho_dense") else (print("Achtung: 'path_rho_dense' fehlt - setze Standard: None"), None)[1]
            path_rho_sigma = cfg.path_rho_sigma if hasattr(cfg, "path_rho_sigma") else (print("Achtung: 'path_rho_sigma' fehlt - setze Standard: None"), None)[1]
            path_base_weight = cfg.path_base_weight if hasattr(cfg, "path_base_weight") else (print("Achtung: 'path_base_weight' fehlt - setze Standard: 0.25"), 0.25)[1]
            path_no_rho0 = cfg.path_no_rho0 if hasattr(cfg, "path_no_rho0") else (print("Achtung: 'path_no_rho0' fehlt - setze Standard: False"), False)[1]

            k_grid, k_grid_center, coords, t_grid = model.path_grid(modeltype_path, cfg.k0, p, n, a_coeffs, b_coeffs, path_phi_sym, path_n_phi_min, non_equidistant, path_rho_dense, path_rho_sigma, path_base_weight, path_no_rho0, decimals=decimals)
            v_grid = None
            if rotation:
                raise ValueError(f"Achtung: Rotation funktioniert nicht in diesem Gitter!")
        elif grid_type == "path_grid_semi_regular":
            print("- Gitter entlang des Pfades aus verschobenen Pfaden")
            k_grid, k_grid_center, coords, t_grid, v_grid = model.path_grid_semi_regular(modeltype_path, cfg.k0, p, n, a_coeffs, b_coeffs, decimals=decimals)
            if rotation:
                raise ValueError(f"Achtung: Rotation funktioniert nicht in diesem Gitter!")
        elif grid_type == "path_grid_2B":
            print("- Gitter für Punkt 2B")

            # Standartparameter
            path_phi_sym = cfg.path_phi_sym if hasattr(cfg, "path_phi_sym") else (print("Achtung: 'path_phi_sym' fehlt - setze Standard: 1"), 1)[1]
            path_phi_sigma = cfg.path_phi_sigma if hasattr(cfg, "path_phi_sigma") else (print("Achtung: 'path_phi_sigma' fehlt - setze Standard: 1"), 1)[1]
            path_rho_sigma = cfg.path_rho_sigma if hasattr(cfg, "path_rho_sigma") else (print("Achtung: 'path_rho_sigma' fehlt - setze Standard: None"), None)[1]
            path_rho_sigmaB = cfg.path_rho_sigmaB if hasattr(cfg, "path_rho_sigmaB") else (print("Achtung: 'path_rho_sigmaB' fehlt - setze Standard: None"), None)[1]
            path_no_rho0 = cfg.path_no_rho0 if hasattr(cfg, "path_no_rho0") else (print("Achtung: 'path_no_rho0' fehlt - setze Standard: False"), False)[1]

            k_grid, k_grid_center, coords, t_grid = model.path_grid_2B(cfg.k0, p, n, a_coeffs, path_phi_sym, path_phi_sigma, path_rho_sigma, path_rho_sigmaB, path_no_rho0, decimals=decimals)
            v_grid = None
            if rotation:
                raise ValueError(f"Achtung: Rotation funktioniert nicht in diesem Gitter!")
        else:
            raise ValueError(f"Folgende grid_type sind momentan möglich:\n regular\n cylindrical\n path\n path_grid_semi_regular\n path_grid_2B")
        
        # -------------------------------------------------------------------------------
        # Plot des Gitters
        # -------------------------------------------------------------------------------
        if plot:
            # Unterscheidung für verschiedene Titel
            if rotation:
                model.plot_grid(k_grid, cfg.k0, cfg.u, cfg.R, cfg.a, cfg.r, cfg.v, cfg.phi_steps, "k-Gitter gedreht")
            else:
                model.plot_grid(k_grid, cfg.k0, cfg.u, cfg.R, cfg.a, cfg.r, cfg.v, cfg.phi_steps, "k-Gitter für QE")
            model.plot_grid(k_grid_center, cfg.k0, cfg.u, cfg.R, cfg.a, cfg.r, cfg.v, cfg.phi_steps, "k-Gitter im Koordinatenursprung")
        print(f"Gitter erfolgreich definiert")
        print()
        return k_grid, k_grid_center, coords, t_grid, v_grid

    def make_analysis_energy(p, p_str, n_str, k_grid_center, t_grid, v_grid, coord_system, grid_type, coord_basis, pca, no_000, cut_df_for_fit, find_intersection):
        """
        - Lade Daten aus der Ausgabe-Dateie der QE-Berechnung 
            df:     xml-file für die Energieberechnung
        - Koordinatentransformationen (optional)
            Skalierung des Gitters
            Transformation des Gitters in Pfadvektoren
        - Hauptkomponentenanalyse der Energie (optional)
        - Entfernung von 0-Werten aus den Daten (optional)
        - Zuschneiden der Daten auf den THz-aktiven Bereich (optional)
        """
        # -------------------------------------------------------------------------------
        # Lade Daten aus der Ausgabe-Dateie der QE-Berechnung + Speicherung
        # -------------------------------------------------------------------------------
        print("- Lade Daten aus xml-File und speichere als Dataframe (Energie)")
        df_original, df = model.model_xml_to_df(cfg.k0, p_str, n_str, k_grid_center, cfg.datlabel, cfg.bandnumbers, t_grid, v_grid)
        # Speichern
        model.model_save_csv(df_original, p_str, n_str, cfg.datlabel, "df_original", modeltype)

        # -------------------------------------------------------------------------------
        # Koordinatentransformationen (optional)
        # -------------------------------------------------------------------------------
        # Skalierung des Gitters
        if coord_system == "xyz_scaled":
            print("- Skalierung des Gitters im Koordinatenursprung auf [-1,1]")
            df = model.scale_grid(df, k_grid_center, p, grid_type)

        # Transformation des Gitters in Pfadvektoren, wenn grid_type kein Pfadgitter ist.
        if (coord_system == "path") and (grid_type != "path") and (grid_type != "path_grid_semi_regular") and (grid_type != "path_grid_2B"):
            print("- Transformaion des Gitters in Pfadkoordinaten")
            
            if coord_basis == "xyz_scaled":
                df = model.scale_grid(df, k_grid_center, p, grid_type)
            
            # Standartparameter
            bounds = cfg.bounds if hasattr(cfg, "bounds") else (print("Achtung: 'bounds' fehlt - setze Standard: (-2,2)"), (-2,2))[1]
            tol = cfg.tol if hasattr(cfg, "tol") else (print("Achtung: 'tol' fehlt - setze Standard: 1e-7"), 1e-7)[1]
            xatol = cfg.xatol if hasattr(cfg, "xatol") else (print("Achtung: 'xatol' fehlt - setze Standard: 1e-8"), 1e-8)[1]   

            df = model.path_transformation(df, a_coeffs, b_coeffs, modeltype_path, coord_basis, bounds, tol, xatol)

        # -------------------------------------------------------------------------------
        # Hauptkomponentenanalyse (optional) ; funktioniert nur im regular-Gitter
        # -------------------------------------------------------------------------------
        if pca:
            if grid_type == "regular":
                print(f"- Hauptkomponentenanalyse von {cfg.energy}")
                # Berechnung des Gradienten und Krümmung
                df = model.model_gradient(df, cfg.energy)
                df = model.model_gradient(df, f"grad_{cfg.energy}")
                # Hauptkomponentenanalyse
                model.model_PCA(df, cfg.energy)
                model.model_mean_curv(df, cfg.energy)
            else:
                raise ValueError("Hauptkomponentenanalyse kann nur in karteschen Gittern berechnet werden.")

        # -------------------------------------------------------------------------------
        # Entfernung von 0-Werten aus den Daten (optional)
        # -------------------------------------------------------------------------------
        if no_000:
            print(f"- Entfernung von 0-Werte aus den Daten")
            df = model.model_cut_000(df, coord_system)
                        
        # -------------------------------------------------------------------------------
        # Zuschneiden der Daten auf den THz-aktiven Bereich (optional)
        # -------------------------------------------------------------------------------
        if cut_df_for_fit: 
            print("- Zuschneiden der Daten auf den THz-aktiven Bereich")
            df = model.model_cut_df_to_thz_range(df, cfg.cut_value_diff, cfg.cut_value_bands, coord_system, cfg.complete_cut)
        
        # -------------------------------------------------------------------------------
        # Berechnung des Schnittpunktes
        # -------------------------------------------------------------------------------
        if find_intersection:
            print("- Berechnung des Schnittpunktes")
            model.model_find_intersect(df, cfg.intersect_point)

        # -------------------------------------------------------------------------------
        # Speichern
        # -------------------------------------------------------------------------------
        model.model_save_csv(df, p_str, n_str, cfg.datlabel, "df", modeltype)
        return df

    def make_analysis_mme(p_str, n_str, k_grid_center, t_grid, v_grid, cut_df_for_fit, mme_statistics):
        """
         - Lade Daten aus den Ausgabe-Dateien der QE-Berechnung 
            df_mme: p_avg.dat-file der Impulselemente-Berechnung
        - Berechnung statistischer Größen für die Matrix-Elemente (optional)
        """
        # -------------------------------------------------------------------------------
        # Lade Daten aus den Ausgabe-Dateie der QE-Berechnung + Speicherung
        # -------------------------------------------------------------------------------
        # Prüfe, ob Daten der Matrix-Elemente vorliegen und falls ja, werden sie gelesen
        if os.path.exists(config.path_p_avg_copy(cfg.datlabel, p_str, n_str)):
            print("Lade Daten aus p_avg.dat und speichere als Dataframe (Matrix-Impuls-Elemente)")
            df_mme = model.mme_to_df(p_str, n_str, cfg.datlabel)
            # Speichern
            model.model_save_csv(df_mme, p_str, n_str, cfg.datlabel, "df_mme", modeltype)
        else:
            print("Es liegen keine Matrix-Impuls-Elemente als p_avg.dat vor!")
            df_mme = None
        
        # -------------------------------------------------------------------------------
        # Berechnung statistischer Größen für die Matrix-Elemente (optional)
        # -------------------------------------------------------------------------------
        if mme_statistics:
            print("- Berechnung statistische Größen der Matrix-Impuls-Elemente")
            # Lade Original-Daten der Energie (verhindert den Fall, dass Koordinatentransformationen etc. durchgeführt wurden)
            print("----> Lade Energie-Daten aus dem xml-File")
            _, df = model.model_xml_to_df(cfg.k0, p_str, n_str, k_grid_center, cfg.datlabel, cfg.bandnumbers, t_grid, v_grid)
            # Zuschneiden der Daten auf den THz-aktiven Bereich (optional)
            if cut_df_for_fit: 
                print("----> Zuschneiden der Energie-Daten auf den THz-aktiven Bereich")
                df = model.model_cut_df_to_thz_range(df, cfg.cut_value_diff, cfg.cut_value_bands, cfg.coord_system, cfg.complete_cut)

            # Berechnung statistischer Größen
            print("----> Berechne statistische Größen")
            model.mme_statistics(df, df_mme, cfg.merge_decimals)
        return df_mme

    def make_model(p_str, n_str, df, orders, a0_correction):
        """       
        - Anpassung des (einzigen!) konstanten Koeffizienten (optional)
        - Speichern der Koeffizienten und deren Indizes
        - Auswertung des Modells auf dem Gitter
        - Berechnung der maximalen Fehler an den Gitterpunkten 
        """
        # -------------------------------------------------------------------------------
        # Modellierung
        # -------------------------------------------------------------------------------
        """
        Ist die Anzahl der Koeffizieten > max_coeffs, wird kein Modell berechnet. Der Parameter stop_loop wird von der Funktion model_solve_LS auf True gesetzt und np.nan wird zurückgegeben. Gilt Anzahl der Koeffizieten < max_coeffs,, wird die Loop-Schleife innerhalb model_solve_LS durchgeführt.
        """
        coeffs, stop_loop = model.model_solve_LS(df, modeltype, cfg.energy, orders, symmetry, cfg.coord_system, no_a0, cfg.max_coeffs, ridgeCV=cfg.ridgeCV, ridge_alphas=cfg.ridge_alphas, col_weighting=cfg.col_weighting, a_coeffs=a_coeffs, b_coeffs=b_coeffs)

        if stop_loop:
            return np.nan, np.nan, np.nan
        else:
            # ---------------------------------------------------------------------------
            # Anpassung des (einzigen!) konstanten Koeffizienten (optional)
            # ---------------------------------------------------------------------------
            if a0_correction:
                coeffs = model.model_a0_correction(df, modeltype, cfg.energy, coeffs, orders, symmetry, no_a0, a_coeffs, b_coeffs)

            # ---------------------------------------------------------------------------
            # Speichern der Koeffizienten und deren Indizes
            # ---------------------------------------------------------------------------
            model.model_save_array(coeffs, p_str, n_str, cfg.datlabel, f"coeffs_{cfg.energy}", modeltype)
            
            # ---------------------------------------------------------------------------
            # Auswertung des Modells auf dem Gitter
            # ---------------------------------------------------------------------------
            df = model.model_use_on_grid(df, cfg.energy, modeltype, orders, coeffs, cfg.coord_system, symmetry, no_a0, a_coeffs, b_coeffs)
            model.model_save_csv(df, p_str, n_str, cfg.datlabel, "df", modeltype)
            
            # ---------------------------------------------------------------------------
            # Berechnung der maximalen Fehler an den Gitterpunkten
            # ---------------------------------------------------------------------------
            err = float(max(df[f"error_{cfg.energy}"]))
            # THz-Bedingung
            df_thz = df.copy()
            df_thz = df_thz.loc[(df_thz["diff"] < cfg.cut_value_diff) & (df_thz["band1"] < cfg.cut_value_bands) & (df_thz["band0"] > -cfg.cut_value_bands)]
            err_thz = float(max(df_thz[f"error_{cfg.energy}"]))
            
            return err, err_thz

    # ###################################################################################
    # Hauptteil
    # ###################################################################################
    print()
    print(f"Hauptpfad der Berechnung:\n main_directory={config.main_directory}")
    print()
    
    # Umrechnung der Parameter n und p in arrays und strings
    n, n_str = model.change_parameter_pn(cfg.n)
    p, p_str = model.change_parameter_pn(cfg.p)

    # -----------------------------------------------------------------------------------
    # Berechnung des Gitters
    # -----------------------------------------------------------------------------------
    k_grid, k_grid_center, coords, t_grid, v_grid = make_grid(p, n, cfg.grid_type, rotation, cfg.plot_grid)

    #print(np.shape(k_grid_center))
    #print(len(k_grid_center[:, 0]))
    #print(np.shape(coords))
    # -----------------------------------------------------------------------------------
    # Berechnung durch Quantum Espresso
    # -----------------------------------------------------------------------------------
    if cfg.calc_dft:
        print("scf und nscf-Berechnungen durch Quantum Espresso")
        model.model_calc(coords, p_str, n_str, cfg.datlabel, enable_logging=True)
        print("Alle scf und nscf-Berechnungen abgeschlossen!")
        print()
    
    if cfg.calc_mme:
        print("Berechnung der Matrix-Elemente")
        model.calc_mme(p_str, n_str, cfg.datlabel, enable_logging=True)
        print("Alle Berechnungen der Matrix-Elemente abgeschlossen!")
        print()

    # -----------------------------------------------------------------------------------
    # Analyse und Anpassung
    # -----------------------------------------------------------------------------------
    if cfg.analysis:
        df = make_analysis_energy(p, p_str, n_str, k_grid_center, t_grid, v_grid, cfg.coord_system, cfg.grid_type, coord_basis, cfg.pca, cfg.no_000, cfg.cut_df_for_fit, cfg.find_intersection)
        df_mme = make_analysis_mme(p_str, n_str, k_grid_center, t_grid, v_grid, cfg.cut_df_for_fit, cfg.mme_statistics)
        print(len(df))

    # -----------------------------------------------------------------------------------
    # Laden der pandas-Dataframes
    # -----------------------------------------------------------------------------------
    if cfg.load_csv:
        print("Laden der Pandas Dataframes")
        df = model.model_load_df(p_str, n_str, cfg.datlabel, "df", modeltype)
        print(df)

        path_p_avg = config.path_p_avg_copy(cfg.datlabel, p_str, n_str)
        if os.path.exists(path_p_avg):
            df_mme = model.model_load_df(p_str, n_str, cfg.datlabel, "df_mme", modeltype)
            print(df_mme)
        else:
            print("Es liegt kein Dataframe mit den Matrixelementen vor!")
        print()

    # -----------------------------------------------------------------------------------
    # Modellierung
    # -----------------------------------------------------------------------------------
    if cfg.calc_model:
        print("Modellierung")
        print(f"- Modeltyp: {modeltype} für Energie: {cfg.energy}")
        print(f"- maximale Anzahl Koeffizienten: {cfg.max_coeffs}")
        print(f"- Definition des THz-aktiven Bereich: diff<{cfg.cut_value_diff}, E0>-{cfg.cut_value_bands}, E1<{cfg.cut_value_bands}")

        rows = []
        rows_thz = []
        orders_lists = [cfg.p_order_list, cfg.f_order_list, cfg.l_order_list, cfg.k_order_list, cfg.p1_order_list, cfg.p2_order_list, cfg.p3_order_list]

        # verschachtelte Schleifen über alle Ordnungen
        for p_order, f_order, l_order, k_order, p1_order, p2_order, p3_order in product(*orders_lists):
            orders = (p_order, f_order, l_order, k_order, p1_order, p2_order, p3_order)
            print(f"-- Ordnung = {orders}")
            err, err_thz = make_model(p_str, n_str, df, orders, cfg.a0_correction)
            rows.append({
                "p_order": p_order,
                "f_order": f_order,
                "l_order": l_order,
                "k_order": k_order,
                "p1_order": p1_order,
                "p2_order": p2_order,
                "p3_order": p3_order,
                f"error_{cfg.energy}": err,
            })
            rows_thz.append({
                "p_order": p_order,
                "f_order": f_order,
                "l_order": l_order,
                "k_order": k_order,
                "p1_order": p1_order,
                "p2_order": p2_order,
                "p3_order": p3_order,
                f"error_{cfg.energy}": err_thz,
            })

        # Erstelle pandas Dataframes
        df_errors = pd.DataFrame(rows)
        df_errors_thz = pd.DataFrame(rows_thz)

        # Hinzufügen der Anzahl der Koeffizienten
        len_coeffs = []
        for p_order, f_order, l_order, k_order, p1_order, p2_order, p3_order in product(*orders_lists):
            orders = (p_order, f_order, l_order, k_order, p1_order, p2_order, p3_order)
            A = model.load_model(modeltype, orders, [1], [1], [1], symmetry=symmetry, no_a0=no_a0, a_coeffs=a_coeffs, b_coeffs=b_coeffs)
            len_coeffs.append(np.shape(A)[1])

        df_errors["len_coeffs"] = len_coeffs
        df_errors_thz["len_coeffs"] = len_coeffs

        # -------------------------------------------------------------------------------
        # Speichern der Fehler als csv-Datei und Berechnung der Minima
        # -------------------------------------------------------------------------------

        if cfg.save_errors:
            model.model_save_csv(df_errors, p_str, n_str, cfg.datlabel, f"errors_{cfg.energy}", modeltype)
            model.model_save_csv(df_errors_thz, p_str, n_str, cfg.datlabel, f"errors_thz_{cfg.energy}", modeltype)

        # Minima der Maximalfehler der Dataframes
        min_error = np.min(np.array(df_errors[f"error_{cfg.energy}"]))
        min_error_thz = np.min(np.array(df_errors_thz[f"error_{cfg.energy}"]))
        print("Fehler an den Datenpunkten. Warnung: Die Fehler zwischen den Datenpunkten können größer sein!")
        print(f"Bester maximaler Fehler [eV]:\n{min_error:.4e}")
        print(f"Bester maximaler Fehler im THz-Bereich [eV]:\n{min_error_thz:.4e}")      

    #diff_max = np.max(df["diff"])
    #print(f"Maximale Bandendergie im Dataframe; {diff_max}")
