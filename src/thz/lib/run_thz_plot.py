import matplotlib.pyplot as plt
# --------------------------------------------------------------------------------------
import lib.config as config
import lib.qe_thz_plot as plot
from lib.plot_config import PLOT_SETTINGS

# --------------------------------------------------------------------------------------

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