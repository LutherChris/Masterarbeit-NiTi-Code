import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import lib.config as config
import lib.qe_model_use as use
import lib.qe_model_calc as model
from lib.plot_config import PLOT_SETTINGS


"""
Diese Datei lädt -Parameter aus z.B. use_uspp_point3.py.

# =======================================================================================
# Übersicht aller Parameter
# =======================================================================================

# ---------------------------------------------------------------------------------------
# Erstellung des Gitters
# ---------------------------------------------------------------------------------------
cfg.k0:         (list) Bandkreuzung an der Fermi-Energie
cfg.axis_1:     (Numpy-array) Einteilung der Koordinatenachse 1
cfg.axis_2:     (Numpy-array) Einteilung der Koordinatenachse 2
cfg.axis_3:     (Numpy-array) Einteilung der Koordinatenachse 3
cfg.grid_type:  (str) Definition des Gittertyps

- Verfügbare Gitter:
	- regelmäßiges kartesisches Gitter: "regular"
	- regelmäßiges zylindrisches Gitter: "cylindrical"
	- regelmäßiges Pfad-Gitter: "path"
	- regelmäßiges Pfad-Gitter für Punkt 2A und 2B: "path_grid_2B"

- Im Fall von Pfad-Gittern:
cfg.a_coeffs:       (list) a-Koeffizienten von r(t)
cfg.b_coeffs:       (list) b-Koeffizienten von r(t)
cfg.modeltype_path: (str) Modell des Pfades

- Pfadmodelle von modeltype_path:
    "path_point1": Pfad für Punkt1
    "path_point2A": Pfad für Punkt2A
    "path_point2B": Pfad für Punkt2B
    "path_point3": Pfad für Punkt3
    "path_point1_center": Pfad für Punkt1 entlang des Zentrums der Schale

# ---------------------------------------------------------------------------------------
# Erstellung des Gitters
# ---------------------------------------------------------------------------------------
cfg.modeltype:  (str) legt den Modell-Typ fest
cfg.symmetry:   (int), (None) Symmetriefaktor in den Modell-Funktionen
cfg.no_a0:      (bool) Soll in den Polynommodellen die 0-te Ordnung weggelassen werden?

Ordnungen:
p_order:        (int) p-Ordnung des Modells
f_order:        (int) f-Ordnung des Modells
l_order:        (int) l-Ordnung des Modells
k_order:        (int) k-Ordnung des Modells
p1_order:       (int) p1-Ordnung des Modells
p2_order:       (int) p2-Ordnung des Modells
p3_order:       (int) p3-Ordnung des Modells

# ---------------------------------------------------------------------------------------
# Laden der Modell-Koeffizienten
# ---------------------------------------------------------------------------------------
cfg.load_coeffs_from_path: (bool) Sollen die Modell-Koeffizienten aus einem Dateienpfad geladen werden?
cfg.path_coeffs:    (str) Gibt den Dateienpfad an.

# ---------------------------------------------------------------------------------------
# Speicherung der Modellenergien
# ---------------------------------------------------------------------------------------
cfg.save_dataframe:     (bool) aktiviert das Speichern der Modellenergien als csv-Datei
cfg.path_save:          (str) Gibt den Dateienpad zum Speichern an.

# ---------------------------------------------------------------------------------------
# Plot der Daten
# ---------------------------------------------------------------------------------------
cfg.plot_2Dplots        (bool) plot_QE_grid
cfg.plot_axis           (str) Zu plottende Koordinatenachse
cfg.nk_model            (int) Anzahl der Datenpunkte
cfg.plot_QE_grid        (bool) Soll die Modellenergie mit QE-Daten verglichen werden?
cfg.path_QE             (str) Dateienpad der QE-Daten
scg.path_4Dplot         (bool) Aktiviert 4D-Plots (3D+Farbachse)
"""

def run(cfg):
    # Laden der Plot-Einstellungen aus plot_config.py
    plt.rcParams.update(PLOT_SETTINGS)

    # ###################################################################################
    # Standard-Parameter, wenn nicht vorhanden
    load_coeffs_from_path = cfg.load_coeffs_from_path if hasattr(cfg, "load_coeffs_from_path") else (print("Achtung: 'load_coeffs_from_path' fehlt - setze Standard: False"), False)[1]
    save_dataframe = cfg.save_dataframe if hasattr(cfg, "save_dataframe") else (print("Achtung: 'save_dataframe' fehlt - setze Standard: False"), False)[1]
    plot_2Dplots = cfg.plot_2Dplots if hasattr(cfg, "plot_2Dplots") else (print("Achtung: 'plot_2Dplots' fehlt - setze Standard: False"), False)[1]
    plot_4Dplots = cfg.plot_4Dplots if hasattr(cfg, "plot_4Dplots") else (print("Achtung: 'plot_4Dplots' fehlt - setze Standard: False"), False)[1]

    modeltype = cfg.modeltype if hasattr(cfg, "modeltype") else (print("Achtung: 'modeltype' fehlt - setze Standard: 'out-Dateien'"), "out-Dateien")[1]

    a_coeffs = cfg.a_coeffs if hasattr(cfg, "a_coeffs") else (print("Achtung: 'a_coeffs' fehlt - noch keine Pfad-Berechnung? - setze: []"), None)[1]
    b_coeffs = cfg.b_coeffs if hasattr(cfg, "b_coeffs") else (print("Achtung: 'b_coeffs' fehlt - noch keine Pfad-Berechnung? - setze: []"), None)[1]
    modeltype_path = cfg.modeltype_path if hasattr(cfg, "modeltype_path") else (print("Achtung: 'modeltype_path' fehlt - noch keine Pfad-Berechnung? - setze: None"), None)[1]

    symmetry = cfg.symmetry if hasattr(cfg, "symmetry") else (print("Achtung: 'symmetry' fehlt - setze Standard: 1"), 1)[1]
    no_a0 = cfg.no_a0 if hasattr(cfg, "no_a0") else (print("Achtung: 'no_a0' fehlt - setze Standard: False"), False)[1]



    # ###################################################################################

    # -----------------------------------------------------------------------------------
    # Erstellung des Gitters
    # -----------------------------------------------------------------------------------
    axis = [cfg.axis_1, cfg.axis_2, cfg.axis_3]

    # Definition des Gitters
    grid_type = cfg.grid_type
    t_grid = None
    if grid_type == "regular":
        print("- regelmäßiges kartesisches Gitters")
        k_grid_center = use.regular_grid(axis)
        coord_system = "xyz"
    elif grid_type == "cylindrical":
        print("- regelmäßiges zylindrisches Gitter")
        k_grid_center = use.cylindrical_grid(axis)
        coord_system = "xyz"
    elif grid_type == "path":
        print("- regelmäßiges Polar-Gitter entlang des Pfades")
        k_grid_center, t_grid = use.path_grid(modeltype_path, axis, a_coeffs, b_coeffs)
        coord_system = "path"
    elif grid_type == "path_grid_2B":
        print("- regelmäßiges Polar-Gitter entlang des Pfades (Punkt 2)")
        k_grid_center, t_grid = use.path_grid_2B(axis, a_coeffs)
        coord_system = "path"
    else:
        raise ValueError(f"Folgende grid_type sind momentan möglich:\n regular\n cylindrical\n path")
    
    # -----------------------------------------------------------------------------------
    # Berechnung der Modellenergien
    # -----------------------------------------------------------------------------------
    print(f"\nHauptpfad der Berechnung:\n main_directory={config.main_directory}\n")
    # Laden der Modell-Koeffizienten
    if load_coeffs_from_path:
        print(f"Lade Koeffizienten aus Pfad:\n {cfg.path_coeffs}\n")
        path_data = cfg.path_coeffs
        with open(path_data, 'r') as txt_file:
            lines = [float(line.rstrip('\n')) for line in txt_file]
        coeffs = np.array(lines)
    else:
        n, n_str = model.change_parameter_pn(cfg.n)
        p, p_str = model.change_parameter_pn(cfg.p)
        print(f"Lade Koeffizienten aus zuvor berechnetem Gitter mit:\n p={p}\n n={n}\n datlabel={cfg.datlabel}\n energy={cfg.energy}\n modeltype={modeltype}\n")
        coeffs = np.array(model.model_load_txt(p_str, n_str, cfg.datlabel, f"coeffs_{cfg.energy}", modeltype))


    # Ordnungen des Modells
    orders = (cfg.p_order, cfg.f_order, cfg.l_order, cfg.k_order, cfg.p1_order, cfg.p2_order, cfg.p3_order)

    # Berechnung der Modell-Energien

    if coord_system == "xyz":
        energy_model = model.load_model(modeltype, orders, k_grid_center[:, 0], k_grid_center[:, 1], k_grid_center[:, 2], symmetry, coeffs, no_a0, a_coeffs, b_coeffs)
    elif coord_system == "path":
        energy_model = model.load_model(modeltype, orders, t_grid[:, 0], t_grid[:, 1], t_grid[:, 2], symmetry, coeffs, no_a0, a_coeffs, b_coeffs)
    else:
        raise ValueError(f"coord_system={coord_system}; Falsches Koordinatensystem zur Modellierung. Verfügbar:\n xyz,\n path")

    # ######################################################################################
    # Speichern der Modell-Energien
    # ######################################################################################

    if save_dataframe:
        df = use.create_dataframe(cfg.k0, k_grid_center, t_grid, energy_model)
        if cfg.path_save is not None:
            print(f"Speichere Dataframe an folgendem Ort:\n{cfg.path_save}\n")
            df.to_csv(cfg.path_save, index=False)
        else:
            model.model_save_csv(df, p_str, n_str, cfg.datlabel, "df_model", modeltype)

    # ###################################################################################
    # -----------------------------------------------------------------------------------
    # Plot des Dataframes
    # -----------------------------------------------------------------------------------

    # -----------------------------------------------------------------------------------
    # 2D - Sliderpolts
    # -----------------------------------------------------------------------------------
    if plot_2Dplots:
        # Auswahl der Koordinatenachsen
        if coord_system == "xyz":
            axis = (k_grid_center[:, 0], k_grid_center[:, 1], k_grid_center[:, 2])
        elif coord_system == "path":
            axis = (t_grid[:, 0], t_grid[:, 1], t_grid[:, 2])
        else:
            raise ValueError(f"coord_system={coord_system}; Falsches Koordinatensystem zur Modellierung. Verfügbar:\n xyz,\n path")
        
        # Vergleich mit QE-Gitter
        if cfg.plot_QE_grid:
            # Lade Dataframe des QE-Gitters
            df_QE = pd.read_csv(cfg.path_QE)
            use.model_2Dplots_xyz(cfg.plot_axis, cfg.energy, df_QE, modeltype, coeffs, cfg.nk_model, orders, True, symmetry, False, coord_system, no_a0, a_coeffs, b_coeffs)
        else:
            use.model_2Dplots(cfg.plot_axis, axis, energy_model, coord_system)
        
    # -----------------------------------------------------------------------------------
    # 4D-Plots: Plot in 3D + Farbachse
    # -----------------------------------------------------------------------------------
    if plot_4Dplots:
        use.model_4Dplots(k_grid_center, energy_model)    
    