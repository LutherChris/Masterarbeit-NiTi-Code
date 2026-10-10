import numpy as np
from multiprocessing import Process
import matplotlib.pyplot as plt
# --------------------------------------------------------------------------------------
import lib.qe_thz_calc as thz
from lib.plot_config import PLOT_SETTINGS

# --------------------------------------------------------------------------------------

def run_single(coords, R, r, phi_steps, nks, datlabel):
    thz.thz_calc(coords, R, r, phi_steps, nks, datlabel)

def run(cfg):
    # Laden der Plot-Einstellungen aus plot_config.py
    plt.rcParams.update(PLOT_SETTINGS)
    
    total = len(cfg.nks_list) * len(cfg.R_list)
    count = 1

    phi_lin = np.linspace(0, 2*np.pi, cfg.phi_steps, endpoint=False)
    print(f"Winkeleinteilung:\n{phi_lin*180/np.pi}")
    print()
    print(f"R_list:\n{cfg.R_list}")
    print()
    print(f"nks_lsit:\n{cfg.nks_list}")
    print()

    for nks in cfg.nks_list:
        for R in cfg.R_list:
            print(f"[{count}/{total}] nks={nks}, R={R}")
            # ###########################################################################
            # Definition der Pfade
            # ###########################################################################

            vecs, coords, uvec, vvec, phi_lin = thz.calc_coords(cfg.u, R, cfg.a, cfg.r, cfg.v, cfg.phi_steps, nks, cfg.minangle, cfg.maxangle, cfg.decimals)

            # ###########################################################################
            # Plot der Pfade
            # ###########################################################################

            if cfg.plot_coords:
                thz.plot_coords(uvec, vvec, vecs)

            # ###########################################################################
            # Berechnung der Pfade
            # ###########################################################################

            if cfg.calc:
                p = Process(target=run_single, args= (coords, R, cfg.r, cfg.phi_steps, nks, cfg.datlabel))
                p.start()
                p.join()
                print(f"[{count}/{total}] Berechnung abgeschlossen.")
                

            # ###########################################################################
            # Laden und Analyse der Daten
            # ###########################################################################

            if cfg.analysis:
                # Laden der Daten und speichern
                df_list = thz.xml_to_df(cfg.u, R, cfg.a, cfg.r, cfg.v, nks, cfg.datlabel, phi_lin, bandnumbers=cfg.bandnumbers)
                # Berechnung lokaler Minima der einzelnen Pfade
                df_all_peaks = thz.df_to_peaks(df_list, R, cfg.r, cfg.phi_steps, nks, cfg.datlabel)
                # Berechnung lokaler und globaler Minima aller Pfade
                if cfg.phi_steps >= 2:
                    thz.peaks_to_mins(df_all_peaks, R, cfg.r, cfg.phi_steps, nks, cfg.datlabel)
            
            count += 1
