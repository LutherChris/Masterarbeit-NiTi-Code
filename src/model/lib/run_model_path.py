import numpy as np
import matplotlib.pyplot as plt

import lib.qe_model_calc as model
import lib.qe_model_path as path
from lib.plot_config import PLOT_SETTINGS

"""
Diese Datei lädt cfg.-parameter aus z.B. path_uspp_point1.py und führt den folgenden Aufbau aus:

- Ausgangspunkt der Berechnung ist ein Pandas-Dataframe der DFT-Berechnung (Energie).
- Auf diesen Daten wird der erste Pfad berechnet, welcher dann iterativ verfeinert wird.
- Die Iteration erfolgt manuell und nicht automatisch:

1. Entlang einer Koordinate (model_axis) werden die Energie-Werte nach dem Minimum gefiltert. Dann wird entlang dieser gefilterten Punkte der Pfad gefittet. Anschließend werdn die Daten gespeichert und optional geplottet.
2. Auf Basis dieses Fits wird ein neues Gitter erzeugt, welches dem Pfad folgt.
3. Auf diesem Gitter werden Quantum Espresso-Berechnungen durchgeführt und gespeichert.
4. Die Dataframes können dann geladen werden.
5. Dann erfolgt analog zu (1.) die Filterung der Energie-Werte nach dem Minimum, mit anschließendem Fit.

Weitere Plot:
Mit diesem Abschnitt können zusätzliche Plots erstellt werden, wie das Darstellen beider Pfade gleichzeitig.

# ---------------------------------------------------------------------------------------
# feste Ausgangsparameter
# ---------------------------------------------------------------------------------------
cfg.point:          (str) Punkt in der BZ. z.B. "punkt1"
                    - bestimmt, welche Funktionen für Filterung und Fit geladen werden
cfg.bandnumbers:    (list) Auswahl der Bänder für die Auslesung der xml-Datei von QE
cfg.modeltype:      (str) Ordner des ersten Dataframes für die Iteration
cfg.model_energy:   (str) Energie-Achse, nach der das Dataframe gefilert wird
cfg.k0=zero:        (list) Versatzvektors für das Gitter im Koordinatenursprung (Schnittpunkt der Bänder)
cfg.p:              (float),(list) Gitterlängen-array bzw. float des ersten Dataframes
cfg.n:              (int),(list) Anzahl-der-Datenpunkte-array bzw. float des ersten Dataframes
cfg.datlabel:       (str) datlabel des ersten Dataframes
cfg.coord_system:   (str) Koordinatensystem, in dem der Fit durchgeführt wird
cfg.model_axis:     (str) Achse, nach der der Pfad parametrisiert ist
                    - Punkt 1: "x"
                    - Punkt 2: "t"

# =======================================================================================
# Parameter der Iteration
# =======================================================================================

# ---------------------------------------------------------------------------------------
# Berechnung des ersten Pfades
# ---------------------------------------------------------------------------------------
cfg.x_order_0:      (int) Ordnung in x-Richtung des Pfadmodells; Beispiel Punkt 1: 0
cfg.y_order_0:      (int) Ordnung in y-Richtung des Pfadmodells; Beispiel Punkt 1: 4
cfg.z_order_0:      (int) Ordnung in z-Richtung des Pfadmodells; Beispiel Punkt 1: 4
cfg.no_a0_0:        (bool) Soll in den Polynommodellen die 0-te Ordnung weggelassen werden?
cfg.filter_intersection_0   (bool) Soll der Bereich in der Nähe (111)-Richtung bei Punkt 2 herausgeschnitten werden?
cfg.filter_tol_0            (float) numerische Toleranz für den Vergleich in (111)-Richtung
cfg.cut_energy_0            (float) Filtert die Energien auf kleiner als cut_energy

cfg.plot_nk_model_0:    (int) Anzahl der Datenpunkte für den Plot des Pfades
cfg.plot_path_0:        (bool) Soll der berechnete Pfad geplottet werden?
cfg.calc_path_0:        (bool) aktiviert die Berechnung des Pfades durch den Fit

# ---------------------------------------------------------------------------------------
# Berechnung des neuen Gitters
# ---------------------------------------------------------------------------------------
cfg.delta:          (float) legt die Gittergrenzen des neuen Gitters entlang des Pfades fest
                Beispiel Punkt 1: Gittergrenzen in y und z-Richtung (symmetrisch)
cfg.n_grid:         (list) Anzahl der Datenpunkte in (x,y,z)-Richtung
cfg.path_step:      (int) Nummer der Iteration; Über path_step werden neue datlabel generiert

cfg.alpha:          (flaot) Transparenz der Gitterpunkte aud dem Dataframe im Plot
cfg.plot_grid:      (bool) Soll das neue Gitter geplottet werden?
cfg.path_grid:      (bool) aktiviert die Defition des neuen Gitters
cfg.calc_dft:       (bool) aktiviert die Berechnug des neuen Gitters durch QE und speichert neues DF
cfg.load_new_csv:   (bool) lädt das neue Dataframe

# ---------------------------------------------------------------------------------------
# Berechnung des neuen Pfades
- analoge Parameter zum ersten Pfad, nur mit _1 statt _0
# ---------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------
# weitere Plots
# ---------------------------------------------------------------------------------------
- die Plot benutzen immer das am letzten aktive Dataframe
cfg.plot_titel:         (str) Titel für die Plots
## 4D Plots
cfg.black_plot:         (bool) alle Punkte sind Schwarz
cfg.plot_cut_value:     (float) filtert das Dataframe: Energie-Achse < plot_cut_value
cfg.plot_thz_cut_diff:  (bool) aktiviert die Filterung des Dataframes nach plot_cut_value
cfg.energy_4D:          (str) legt die Energie-Achse des Plottes fest (auch nach der gefiltert wird)
cfg.plot_data:          (bool) aktiviert den Plot
## Plot beider Pfade gleichzeitig
cfg.plot_path_both:     (bool) plotet den alten und neuen Pfad gleichzeitig

# ---------------------------------------------------------------------------------------
# Energien im THz-aktiven Bereich
# ---------------------------------------------------------------------------------------
cfg.final_analysis_point2:  (bool) aktiviert die Analyse am Punkt 2
cfg.plot_analysis_point2:   (bool) Plot der Intervalle entlang des Pfades 
cfg.cut_value_diff:         (float) Energie in eV, auf der die Differenz der Bänder zugeschnitten wird
cfg.cut_value_bands:        (float) Energie in eV, auf der die Bänder zugeschnitten werden

cfg.calc_point_2A_2B:       (bool) aktiviert Schnittpunkt-Berechnung von 2A und 2B
cfg.plot_2A_2B:             (bool) Plot der Raumkurven 2A und 2B

cfg.final_analysis_point1:  (bool) aktiviert Analyse am Punkt 1
cfg.plot_analysis_point1:   (bool) Plot der Intervalle entlang des Pfades
"""

def run(cfg):
    # Laden der Plot-Einstellungen aus plot_config.py
    plt.rcParams.update(PLOT_SETTINGS)

    # Standard-Parameter, wenn nicht vorhanden
    path_step = cfg.path_step if hasattr(cfg, "path_step") else (print("Achtung: 'path_step' fehlt - setze Standard: 0"), 0)[1]
    filter_intersection_0 = cfg.filter_intersection_0 if hasattr(cfg, filter_intersection_0) else (print("Achtung: 'filter_intersection_0' fehlt - setze Standard: False"), False)[1]
    filter_intersection_1 = cfg.filter_intersection_1 if hasattr(cfg, filter_intersection_1) else (print("Achtung: 'filter_intersection_1' fehlt - setze Standard: False"), False)[1]
    filter_tol_0 = cfg.filter_tol_0 if hasattr(cfg, filter_tol_0) else (print("Achtung: 'filter_tol_0' fehlt - setze Standard: 1e-6"), 1e-6)[1]
    filter_tol_1 = cfg.filter_tol_1 if hasattr(cfg, filter_tol_1) else (print("Achtung: 'filter_tol_1' fehlt - setze Standard: 1e-6"), 1e-6)[1]
    cut_energy_0 = cfg.cut_energy_0 if hasattr(cfg, cut_energy_0) else (print("Achtung: 'cut_energy_0' fehlt - setze Standard: None"), None)[1]
    cut_energy_1 = cfg.cut_energy_1 if hasattr(cfg, cut_energy_1) else (print("Achtung: 'cut_energy_1' fehlt - setze Standard: None"), None)[1]
    plot_analysis_point2 = cfg.plot_analysis_point2 if hasattr(cfg, plot_analysis_point2) else (print("Achtung: 'plot_analysis_point2' fehlt - setze Standard: False"), False)[1]
    final_analysis_point2 = cfg.final_analysis_point2 if hasattr(cfg, final_analysis_point2) else (print("Achtung: 'final_analysis_point2' fehlt - setze Standard: False"), False)[1]
    plot_2A_2B = cfg.plot_2A_2B if hasattr(cfg, plot_2A_2B) else (print("Achtung: 'plot_2A_2B' fehlt - setze Standard: False"), False)[1]
    calc_point_2A_2B = cfg.calc_point_2A_2B if hasattr(cfg, calc_point_2A_2B) else (print("Achtung: 'calc_point_2A_2B' fehlt - setze Standard: False"), False)[1]
    plot_analysis_point1 = cfg.plot_analysis_point1 if hasattr(cfg, plot_analysis_point1) else (print("Achtung: 'plot_analysis_point1' fehlt - setze Standard: False"), False)[1]
    final_analysis_point1 = cfg.final_analysis_point1 if hasattr(cfg, final_analysis_point1) else (print("Achtung: 'final_analysis_point1' fehlt - setze Standard: False"), False)[1]

    # Umrechnung der Parameter n und p in arrays und strings
    n, n_str = model.change_parameter_pn(cfg.n)
    p, p_str = model.change_parameter_pn(cfg.p)

    # Wahl des Koordinatensystems
    if cfg.coord_system == "xyz":
        axes = ("x", "y", "z")
    elif cfg.coord_system == "xyz_scaled":
        axes = ("x_scaled", "y_scaled", "z_scaled")
    elif cfg.coord_system == "path":
        axes = ("t", "rho", "phi")
    else:
        raise ValueError(f"Falsche Wahl des Koordinatensystems: {cfg.coord_system}. Vefügbar:\n xyz\n xyz_scaled\n path")
    
    # Definition für Dateien- und Ordernamen
    if path_step == 0:
        datlabel_0 = cfg.datlabel
        datlabel_1 = cfg.datlabel + f"_path1"
    else:
        datlabel_0 = cfg.datlabel + f"_path{path_step}"
        datlabel_1 = cfg.datlabel + f"_path{path_step+1}"
    
    # Laden des Dataframes datlabel_0
    df = model.model_load_df(p_str, n_str, datlabel_0, "df", cfg.modeltype)
    # Kopie des Dataframes datlabel_0
    df_copy = df.copy()
    
    # ###################################################################################
    # 1. Fit entlang des Minimums des Gitters aus datlabel_0
    # ###################################################################################

    if cfg.calc_path_0:
        print()
        print(f"Fit im Gitter datlabel={datlabel_0}:")

        # -------------------------------------------------------------------------------
        # Zuschnitt des Dataframes auf das Minimum entlang der Achse model_axis
        # -------------------------------------------------------------------------------
        df_mins_0 = path.load_cut_df_to_min(cfg.point, df, cfg.model_axis, cfg.model_energy, filter_intersection_0, filter_tol_0, cut_energy_0)

        # -------------------------------------------------------------------------------
        # Fit: Lösung der linearen Gleichungssysteme
        # -------------------------------------------------------------------------------
        coeffs_0 = path.path_solve_LS(df_mins_0, cfg.point, cfg.model_axis, cfg.x_order_0, cfg.y_order_0, cfg.z_order_0, cfg.coord_system, no_a0=cfg.no_a0_0)
        # -------------------------------------------------------------------------------
        # Speichern der Koeffizienten und der Minima
        # -------------------------------------------------------------------------------
        # Speichern der Koeffizienten und deren Indizes in Ordner von datlabel_1
        df_coeffs = path.coeffs_to_df(coeffs_0, cfg.x_order_0, cfg.y_order_0, cfg.z_order_0)
        print(f"Koeffizieten:\n {df_coeffs}")
        model.model_save_csv(df_coeffs, p_str, n_str, datlabel_1, f"coeffs_{path_step}", cfg.modeltype, index=False)

        # Speichern des Minima-Dataframes in Ordner von datlabel_1
        model.model_save_csv(df_mins_0, p_str, n_str, datlabel_1, f"mins_{path_step}", cfg.modeltype, index=False)

        # -------------------------------------------------------------------------------
        # Plot des Fits
        # -------------------------------------------------------------------------------
        if cfg.plot_path_0:
            # Plot der Datenpunkte
            path.path_4Dplots(p, df_mins_0, (axes[0], axes[1], axes[2], cfg.energy_4D), cfg.plot_titel, black=cfg.black_plot)

            # Plot des Pfad-Modells
            pmax = np.max(p[0])
            if cfg.coord_system == "xyz_scaled":
                plot_min = -1
                plot_max = 1
            else:
                plot_min = -pmax
                plot_max = pmax
            plot_range = np.linspace(plot_min, plot_max, cfg.plot_nk_model_0)
            xyz = path.load_curve_model(cfg.point, cfg.x_order_0, cfg.y_order_0, cfg.z_order_0, plot_range, coeffs_0, no_a0=cfg.no_a0_0)
            
            path.path_4Dplots(p, df_mins_0, (axes[0], axes[1], axes[2], cfg.energy_4D), cfg.plot_titel, black=True, path=xyz)

    # ###################################################################################
    # 2. Definition des neuen Gitters entlang des Pfades
    # ###################################################################################

    if cfg.path_grid:
        k_grid, k_grid_center, coords, t_grid = path.load_grid_for_fit(cfg.point, cfg.model_axis, df, cfg.delta, cfg.n_grid, cfg.x_order_0, cfg.y_order_0, cfg.z_order_0, coeffs_0, cfg.no_a0_0, cfg.k0)
        print(f"Anzahl der Datenpunkte: {np.shape(coords)[0]}")

        # Plot der Gitter
        if cfg.plot_grid:
            path.plot_path_kgrid(k_grid_center, df, cfg.plot_titel, alpha=cfg.alpha)
    
    # ###################################################################################
    # 3. Berechnung des neuen Gitters in QE
    # ###################################################################################
    if cfg.calc_dft:
        model.model_calc(coords, p_str, n_str, datlabel_1, enable_logging=True)
        # Auslesen der xml-Datei und speichern als Pandas-Dataframe
        df_original, df = model.model_xml_to_df(cfg.k0, p_str, n_str, k_grid_center, datlabel_1, bandnumbers=cfg.bandnumbers, t_grid=t_grid)
        # Dataframe speichern
        model.model_save_csv(df_original, p_str, n_str, datlabel_1, "df_original", cfg.modeltype)
        model.model_save_csv(df, p_str, n_str, datlabel_1, "df", cfg.modeltype)

    # ###################################################################################
    # 4. Laden des Dataframes
    # ###################################################################################
    if cfg.load_new_csv:
        df = model.model_load_df(p_str, n_str, datlabel_1, "df", cfg.modeltype)

    # ###################################################################################
    # 5. Fit entlang der Minima des Gitters aus datlabel_1
    # ###################################################################################
    
    if cfg.calc_path_1:
        print()
        print(f"Fit im Gitter datlabel={datlabel_1}:")

        # -------------------------------------------------------------------------------
        # Zuschnitt des Dataframes auf das Minimum entlang der Achse model_axis
        # -------------------------------------------------------------------------------
        df_mins_1 = path.load_cut_df_to_min(cfg.point, df, cfg.model_axis, cfg.model_energy, filter_intersection_1, filter_tol_1, cut_energy_1)

        # -------------------------------------------------------------------------------
        # Fit: Lösung der linearen Gleichungssysteme
        # -------------------------------------------------------------------------------
        coeffs_1 = path.path_solve_LS(df_mins_1, cfg.point, cfg.model_axis, cfg.x_order_1, cfg.y_order_1, cfg.z_order_1, cfg.coord_system, no_a0=cfg.no_a0_1)

        # -------------------------------------------------------------------------------
        # Speichern der Koeffizienten und der Minima
        # -------------------------------------------------------------------------------
        # Speichern der Koeffizienten und deren Indizes in Ordner von datlabel_1
        df_coeffs = path.coeffs_to_df(coeffs_1, cfg.x_order_1, cfg.y_order_1, cfg.z_order_1)
        print("Koeffizieten:")
        print(df_coeffs)
        model.model_save_csv(df_coeffs, p_str, n_str, datlabel_1, f"coeffs_{path_step+1}", cfg.modeltype, index=False)

        # Speichern des Minima-Dataframes in Ordner von datlabel_1
        model.model_save_csv(df_mins_1, p_str, n_str, datlabel_1, f"mins_{path_step+1}", cfg.modeltype, index=False)

        # -------------------------------------------------------------------------------
        # Plot des Fits
        # -------------------------------------------------------------------------------
        if cfg.plot_path_1:
            # Plot der Datenpunkte
            path.path_4Dplots(p, df_mins_1, (axes[0], axes[1], axes[2], cfg.energy_4D), cfg.plot_titel, black=cfg.black_plot)

            # Plot des Pfad-Modells
            pmax = np.max(p[0])
            if cfg.coord_system == "xyz_scaled":
                plot_min = -1
                plot_max = 1
            else:
                plot_min = -pmax
                plot_max = pmax
            plot_range = np.linspace(plot_min, plot_max, cfg.plot_nk_model_1)
            xyz = path.load_curve_model(cfg.point, cfg.x_order_1, cfg.y_order_1, cfg.z_order_1, plot_range, coeffs_1, no_a0=cfg.no_a0_1)
            
            path.path_4Dplots(p, df_mins_1, (axes[0], axes[1], axes[2], cfg.energy_4D), cfg.plot_titel, black=True, path=xyz)

    # ###################################################################################
    # weitere Plots
    # ###################################################################################
    
    # -----------------------------------------------------------------------------------
    # Plot der Daten zusammen mit einem Plot des Pfades
    # -----------------------------------------------------------------------------------
    if cfg.plot_data:
        if cfg.plot_thz_cut_diff:
            df_plot = df[(df[f"{cfg.energy_4D}"] < cfg.plot_cut_value)]
        else:
            df_plot = df
        if cfg.load_new_csv:
            path.path_4Dplots(p, df_plot, (axes[0], axes[1], axes[2], cfg.energy_4D), cfg.plot_titel, black=cfg.black_plot)
        else:
            path.path_4Dplots(p, df_plot, (axes[0], axes[1], axes[2], cfg.energy_4D), cfg.plot_titel, black=cfg.black_plot)
    
    # -----------------------------------------------------------------------------------
    # Plot der Pfade
    # -----------------------------------------------------------------------------------
    if cfg.plot_path_both:
        # Laden der Koeffizienten
        df_coeffs_0 = model.model_load_df(p_str, n_str, datlabel_1, f"coeffs_{path_step}", cfg.modeltype)
        df_coeffs_1 = model.model_load_df(p_str, n_str, datlabel_1, f"coeffs_{path_step+1}", cfg.modeltype)

        coeffs_0 = [np.array(df_coeffs_0["coeffs_x"]), np.array(df_coeffs_0["coeffs_y"]), np.array(df_coeffs_0["coeffs_z"])]
        if cfg.no_a0_0:
            coeffs_0 = [arr[:-1] for arr in coeffs_0]

        coeffs_1 = [np.array(df_coeffs_1["coeffs_x"]), np.array(df_coeffs_1["coeffs_y"]), np.array(df_coeffs_1["coeffs_z"])]
        if cfg.no_a0_1:
            coeffs_1 = [arr[:-1] for arr in coeffs_1]

        # Laden der Dataframes
        df_mins_0 = model.model_load_df(p_str, n_str, datlabel_1,  f"mins_{path_step}", cfg.modeltype)
        df_mins_1 = model.model_load_df(p_str, n_str, datlabel_1,  f"mins_{path_step+1}", cfg.modeltype)

        # Plot der Pfad-Modelle
        pmax = np.max(p[0])
        if cfg.coord_system == "xyz_scaled":
            plot_min = -1
            plot_max = 1
        else:
            plot_min = -pmax
            plot_max = pmax
        plot_range = np.linspace(plot_min, plot_max, cfg.plot_nk_model_0)

        xyz_0 = path.load_curve_model(cfg.point, cfg.x_order_0, cfg.y_order_0, cfg.z_order_0, plot_range, coeffs_0, no_a0=cfg.no_a0_0)
        xyz_1 = path.load_curve_model(cfg.point, cfg.x_order_0, cfg.y_order_0, cfg.z_order_0, plot_range, coeffs_1, no_a0=cfg.no_a0_1)
        
        path.path_4Dplots_both(p, df_mins_0, df_mins_1, (axes[0], axes[1], axes[2], cfg.energy_4D), cfg.plot_titel, path_0=xyz_0, path_1=xyz_1)

    # -----------------------------------------------------------------------------------
    # Energien im THz-aktiven Bereich
    # -----------------------------------------------------------------------------------
    
    if final_analysis_point2:
        df_thz_32, p_neu = path.path_final_analysis_point2(df, cfg.cut_value_diff, cfg.cut_value_bands, plot_analysis_point2)
        datlabel_2 = cfg.datlabel + f"_path{path_step+2}"
        # Speichern des um 3/2 erweiterten THz-aktiven Bereichs
        if p_neu is not None and df_thz_32 is not None:
            n_neu = (1,2,3) # nur für Ordner-Bezeichnung; irrelevant für das Gitter
            n_neu, n_str_neu = model.change_parameter_pn(n_neu)
            p_neu, p_neu_str = model.change_parameter_pn(p_neu)
            model.model_save_csv(df_thz_32, p_neu_str, n_str_neu, datlabel_2, "df", cfg.modeltype)
            print(" n=(1,2,3)")

    if calc_point_2A_2B:
        # Numerische Berechnung und Plot des Schnittpunktes
        path.calc_point_2A_2B(coeffs_0, cfg.point, cfg.x_order_0, cfg.y_order_0, cfg.z_order_0, cfg.no_a0_0, cfg.k0, plot_2A_2B)

    if final_analysis_point1:
        df_thz_32, p_neu = path.path_final_analysis_point1(df, cfg.cut_value_diff, cfg.cut_value_bands, plot_analysis_point1)

    print()




