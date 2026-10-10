import os
import os.path
import numpy as np
import matplotlib.pyplot as plt

import lib.qe_model_calc as model
import lib.qe_model_plot as plot
import lib.config as config
from lib.plot_config import PLOT_SETTINGS

# --------------------------------------------------------------------------------------

def run(cfg):
    # Laden der Plot-Einstellungen aus plot_config.py
    plt.rcParams.update(PLOT_SETTINGS)
    
    # Standard-Parameter, wenn nicht vorhanden
    modeltype = cfg.modeltype if hasattr(cfg, "modeltype") else (print("Achtung: 'modeltype' fehlt - setze Standard: 'out-Dateien'"), "out-Dateien")[1]
    no_a0 = cfg.no_a0 if hasattr(cfg, "no_a0") else (print("Achtung: 'no_a0' fehlt - setze Standard: False"), False)[1]
    a_coeffs = cfg.a_coeffs if hasattr(cfg, "a_coeffs") else (print("Achtung: 'a_coeffs' fehlt - noch keine Pfad-Berechnung? - setze: []"), None)[1]
    b_coeffs = cfg.b_coeffs if hasattr(cfg, "b_coeffs") else (print("Achtung: 'b_coeffs' fehlt - noch keine Pfad-Berechnung? - setze: []"), None)[1]

    orders = (cfg.p_order, cfg.f_order, cfg.l_order, cfg.k_order, cfg.p1_order, cfg.p2_order, cfg.p3_order)
    print()
    print(f"-- Ordnung = {orders}")
    print()
    print(f"Hauptpfad der Berechnung:\n main_directory={config.main_directory}")
    print()
    
    # Umrechnung der Parameter n und p in arrays und strings
    n, n_str = model.change_parameter_pn(cfg.n)
    p, p_str = model.change_parameter_pn(cfg.p)

    # Wahl des Koordinatensystems
    if cfg.coord_system == "kxyz":
        axes = ("kx", "ky", "kz")
    elif cfg.coord_system == "xyz":
        axes = ("x", "y", "z")
    elif cfg.coord_system == "xyz_scaled":
        axes = ("x_scaled", "y_scaled", "z_scaled")
    elif cfg.coord_system == "path":
        axes = ("t", "rho", "phi")
    elif cfg.coord_system == "tNB":
        axes = ("t", "vN", "vB")
    else:
        raise ValueError(f"coord_system={cfg.coord_system}; Falsches Koordinatensystem für Plots. Verfügbar:\n kxyz,\n xyz,\n xyz_scaled,\n path,\n tNB")

    # Laden des Dataframes der Energie
    df = model.model_load_df(p_str, n_str, cfg.datlabel, "df", modeltype)
    #print(len(df))
    # Laden des Dataframes der Matrix-Impuls-Elemente
    path_p_avg = config.path_p_avg_copy(cfg.datlabel, p_str, n_str)
    if os.path.exists(path_p_avg):
        df_mme = model.model_load_df(p_str, n_str, cfg.datlabel, "df_mme", modeltype)
    else:
        print("Es liegt kein Dataframe mit den Matrixelementen vor!")
    print()
       
    # Zuschnitt des Dataframes df
    if cfg.thz_cut_diff:
        df = df.loc[(df["diff"] < cfg.cut_value_diff)]
    if cfg.thz_cut_band0:
        df = df.loc[(df["band0"] < cfg.cut_value_bands) & (df["band0"] > -cfg.cut_value_bands)]
    if cfg.thz_cut_band1:
        df = df.loc[(df["band1"] < cfg.cut_value_bands) & (df["band1"] > -cfg.cut_value_bands)]

    # print der Gittergrenzen von df
    x_range = np.unique(df["x"].to_numpy())
    y_range = np.unique(df["y"].to_numpy())
    z_range = np.unique(df["z"].to_numpy())
    x_min, x_max = float(min(x_range)), float(max(x_range))
    y_min, y_max = float(min(y_range)), float(max(y_range))
    z_min, z_max = float(min(z_range)), float(max(z_range))
    
    print(f"Gittergrenzen des Dataframes für Bedingung:")
    print(f"thz_cut_diff = {cfg.thz_cut_diff}; thz_cut_band0 = {cfg.thz_cut_band0}; thz_cut_band1 = {cfg.thz_cut_band1}")
    print(f"----cut_value = {cfg.cut_value_diff};----cut_value_bands = {cfg.cut_value_bands}")
    print()
    print(f"----(min(x), max(x), Kantenlänge) = {(x_min, x_max, float(abs((x_range[1]-x_range[0]))))}")
    print(f"----(min(y), max(y), Kantenlänge) = {(y_min, y_max, float(abs((y_range[1]-y_range[0]))))}")
    print(f"----(min(z), max(z), Kantenlänge) = {(z_min, z_max, float(abs((z_range[1]-z_range[0]))))}")
    print()

    if "t" and "rho" in df.columns:
        if np.unique(df["t"].to_numpy()).any() != 1:
            t_range = np.unique(df["t"].to_numpy())
            rho_range = np.unique(df["rho"].to_numpy())
            if len(t_range) > 1 and len(rho_range) > 1:
                t_min, t_max = float(min(t_range)), float(max(t_range))
                rho_min, rho_max = float(min(rho_range)), float(max(rho_range))
                print(f"----(min(t), max(t), Kantenlänge) = {(t_min, t_max, float(abs((t_range[1]-t_range[0]))))}")
                print(f"----(min(rho), max(rho), Kantenlänge) = {(rho_min, rho_max, float(abs((rho_range[1]-rho_range[0]))))}")
                print()
        
    # ###################################################################################
    # Plots
    # ###################################################################################

    # Auswahl des richtigen Dataframes für den Plot
    if cfg.plot_energy_axis in ["px", "py", "pz"]:
        df_plots = df_mme
    else:
        df_plots = df

    # -----------------------------------------------------------------------------------
    # 2D - Sliderpolts
    # -----------------------------------------------------------------------------------
    if cfg.plot_2Dplots:
        # Laden der Coeffs
        try:
            coeffs = np.array(model.model_load_txt(p_str, n_str, cfg.datlabel, f"coeffs_{cfg.plot_energy_axis}", modeltype))
        except:
            coeffs = None
        # Plot
        plot.model_2Dplots_xyz(cfg.axis_2D, cfg.plot_energy_axis, df_plots, modeltype, coeffs, cfg.nk_model, orders, cfg.plot_model, cfg.symmetry, cfg.error, cfg.coord_system, cfg.modeltype_path, no_a0, a_coeffs, b_coeffs)
    
    # -----------------------------------------------------------------------------------
    # 3D - Sliderpolts
    # -----------------------------------------------------------------------------------
    if cfg.plot_3Dplots:
        plot.model_3Dsurface(cfg.axis_3D, df_plots, cfg.plot_energy_axis, cfg.coord_system, cfg.grid_type)

    # -----------------------------------------------------------------------------------
    # 4D-Plots: Plot in 3D + Farbachse
    # -----------------------------------------------------------------------------------
    if cfg.plot_4Dplots:
        plot.model_4Dplots(p, df_plots, (axes[0], axes[1], axes[2], cfg.plot_energy_axis), cfg.plot_titel, black=cfg.black_plot, activate_plot_cube=cfg.plot_cube)

    if cfg.plot_4Dplots_mme_in_thz:
        plot.model_4Dplots_mme_in_thz(p, df, df_mme, (axes[0], axes[1], axes[2], cfg.plot_energy_axis), cfg.plot_titel, cfg.merge_decimals)

    # -----------------------------------------------------------------------------------
    # Gradienten
    # -----------------------------------------------------------------------------------
    # Plot des Gradienten und der Krümmung
    if cfg.plot_gradient:
        plot.model_plot_gradient(df, (axes[0], axes[1], axes[2], cfg.plot_energy_axis), cfg.step)
    if cfg.plot_curv:
        plot.model_plot_gradient(df, (axes[0], axes[1], axes[2], f"grad_{cfg.plot_energy_axis}"), cfg.step)

    # -----------------------------------------------------------------------------------
    # Plot der Fehler für verschiedene Ordnungen
    # -----------------------------------------------------------------------------------
    # 2D-Plot
    if cfg.plot_errors_2D:
        if cfg.thz_range_2D:
            df_errors_thz = model.model_load_df(p_str, n_str, cfg.datlabel, f"errors_thz_{cfg.plot_energy_axis}", modeltype)
            plot.model_errors(cfg.axis1, df_errors_thz, f"{cfg.plot_energy_axis}", modeltype, max_error=cfg.max_error_2D, thz_range=cfg.thz_range_2D)
        else:
            df_errors = model.model_load_df(p_str, n_str, cfg.datlabel, f"errors_{cfg.plot_energy_axis}", modeltype)
            plot.model_errors(cfg.axis1, df_errors, f"{cfg.plot_energy_axis}", modeltype, max_error=cfg.max_error_2D, thz_range=cfg.thz_range_2D)
    
    # 3D-Plot
    if cfg.plot_errors_3D:
        if cfg.thz_range_3D:
            df_errors_thz = model.model_load_df(p_str, n_str, cfg.datlabel, f"errors_thz_{cfg.plot_energy_axis}", modeltype)
            plot.model_errors_3D(cfg.axis1_3D, cfg.axis2_3D, df_errors_thz, f"{cfg.plot_energy_axis}", modeltype, max_error=cfg.max_error_3D, thz_range=cfg.thz_range_3D)
        else:
            df_errors = model.model_load_df(p_str, n_str, cfg.datlabel, f"errors_{cfg.plot_energy_axis}", modeltype)
            plot.model_errors_3D(cfg.axis1_3D, cfg.axis2_3D, df_errors, f"{cfg.plot_energy_axis}", modeltype, max_error=cfg.max_error_3D, thz_range=cfg.thz_range_3D)
