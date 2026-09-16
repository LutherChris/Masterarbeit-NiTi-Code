import matplotlib.pyplot as plt
# --------------------------------------------------------------------------------------
import lib.config as config
import lib.qe_thz_plot as plot
from lib.plot_config import PLOT_SETTINGS

"""
Diese Datei lädt cfg.-Parameter aus z.B. nitiB2_thz_plot_uspp_punkt1.py und aktiviert verschiedene Abschnitte:
- Tricontour und trisurf-Plots
- Plot der Bänder entlang eines der Pfade
- Plot in Abhängigkeit des Rotationswinkels
- Plot in Abhängigkeit von R
- 3D - Plot in Abhängigkeit von R und phi

# ===================================================================================
# Übersicht aller Parameter
# ===================================================================================

# -----------------------------------------------------------------------------------
# Parameter aus der Berechnung
# -----------------------------------------------------------------------------------
cfg.a           (list) (ax, ay, az) - Einheitsvektor für Anfangspfad, der orthogonal zu u liegt
cfg.r           (float) Radius für den Einheitsvektor a
cfg.nks_list    (list) Liste verschiedener nks-Werte
                        nks: (int) Anzahl der Datenpunkte pro Pfad
cfg.R_list      (list) Liste verschiedener R-Werte
                        R: (float) Radius für den Einheitsvektor u
cfg.phi_steps   (int) Anzahl der Zwischenpfade zwischen 0° und 180°
cfg.datlabel    (str) extra Label in Dateienname, um Rechnungen zu unterscheiden

# -----------------------------------------------------------------------------------
# Tricontour und trisurf-Plots
# -----------------------------------------------------------------------------------
cfg.contourplot             (bool) aktiviert Tricontour oder trisurf-Plots
cfg.plottype_contourplot    (str) zur Unterscheidung des Plottyps; möglich sind:
                                "tricontour_diff"     "tricontour_band0"    "tricontour_band1"    "tricontour_limit_diff"
                                "trisurf_diff"        "trisurf_band0"       "trisurf_band1"       "trisurf_all_bands"
cfg.levels                  (int) Anzahl der Positionslinien im Plot
cfg.peaks                   (bool) Sollen auch die Peaks als Punkte geplottet werden?
cfg.xlim_values_contourplot (tupel) Einschränkung der Plots auf einen Bereich der X-Achse
cfg.ylim_values_contourplot (tupel) Einschränkung der Plots auf einen Bereich der y-Achse

# -----------------------------------------------------------------------------------
# Plot der Bänder entlang eines der Pfade
# -----------------------------------------------------------------------------------
cfg.plotbands               (bool) Aktivierung des Plots entlang der Pfade
cfg.deg                     (float) Plottet den Pfad in der kx-Ebene, welcher am nächsten am Winkel deg (in °) liegt
cfg.sym                     (bool) mit sym=True wird auch der um 180° gedrehte gegenüberliegende Pfad geplottet
cfg.xlim_values_plotbands   (tupel) Einschränkung der Plots auf einen Bereich der X-Achse
cfg.ylim_values_plotbands   (tupel) Einschränkung der Plots auf einen Bereich der y-Achse

# -----------------------------------------------------------------------------------
# Plot in Abhängigkeit des Rotationswinkels
# -----------------------------------------------------------------------------------
cfg.plot_vs_phi         (bool) aktiviert Plot in Abhängigkeit des Rotationswinkels

# -----------------------------------------------------------------------------------
# Plot in Abhängigkeit von R
# -----------------------------------------------------------------------------------
cfg.plot_vs_R           (bool) aktiviert Plot in Abhängigkeit von R
cfg.philabel            (bool) Sollen die globalen Mimima farbig in die Legende geplottet werden?
cfg.symmetry            (int) Symmetrie der Daten (für Label der globalen Minima)
cfg.thz_area_R          (bool) Datenpunkte werden nach der THz-Bedingung gefiltert
# -----------------------------------------------------------------------------------
# 3D - Plot in Abhängigkeit von R und phi
# -----------------------------------------------------------------------------------
cfg.plot_vs_phi_R       (bool) aktiviert den 3D-Plot
cfg.plottype_phi_R      (str) zur Unterscheidung des Plottyps; möglich sind:
                            "diff"     "bands"     "R"
cfg.thz_area_3D         (bool) Datenpunkte werden nach der THz-Bedingung gefiltert
"""

def run(cfg):
    # Laden der Plot-Einstellungen aus plot_config.py
    plt.rcParams.update(PLOT_SETTINGS)

    total = len(cfg.nks_list) * len(cfg.R_list)
    count = 1

    for nks in cfg.nks_list:
        for R in cfg.R_list:
            #print(f"[{count}/{total}] nks={nks}, R={R}")
            
            path_out_directory = config.path_out_directory(cfg.datlabel, nks, cfg.phi_steps, R, cfg.r)

            # ###########################################################################
            # Tricontour und trisurf-Plots
            # ###########################################################################

            if cfg.contourplot:
                df_all_df_for_plots = config.load_csv(path_out_directory, "all_df_for_plots")
                df_all_peaks = config.load_csv(path_out_directory, "all_peaks")
                plot.contourplots(cfg.a, cfg.r, df_all_df_for_plots, df_all_peaks, cfg.plottype_contourplot, cfg.levels, cfg.peaks, cfg.xlim_values_contourplot, cfg.ylim_values_contourplot)

            # ###########################################################################
            # Plot der Bänder entlang eines der Pfade
            # ###########################################################################
            
            if cfg.plotbands:
                df_all_df_for_plots = config.load_csv(path_out_directory, "all_df_for_plots")
                df_all_peaks = config.load_csv(path_out_directory, "all_peaks")
                plot.plot_bandsbands(df_all_df_for_plots, df_all_peaks, cfg.deg, cfg.sym, R, cfg.xlim_values_plotbands, cfg.ylim_values_plotbands)

            # ###########################################################################
            # Plot in Abhängigkeit des Rotationswinkels
            # ###########################################################################

            if cfg.plot_vs_phi:
                df_all_peaks = config.load_csv(path_out_directory, "all_peaks")
                df_phi_peaks = config.load_csv(path_out_directory, "phi_peaks")
                plot.plot_vs_phi(df_all_peaks, df_phi_peaks, R)

            #count += 1

        # ###############################################################################
        # Plot in Abhängigkeit von R
        # ###############################################################################

        if cfg.plot_vs_R:
            plot.plot_vs_R(cfg.R_list, cfg.r, cfg.phi_steps, nks, cfg.datlabel, cfg.symmetry, cfg.philabel, cfg.thz_area_R)

        # ###############################################################################
        # 3D - Plot in Abhängigkeit von R und phi
        # ###############################################################################

        if cfg.plot_vs_phi_R:
            plot.plot_vs_phi_R(cfg.R_list, cfg.r, cfg.phi_steps, nks, cfg.datlabel, cfg.plottype_phi_R, cfg.thz_area_3D)