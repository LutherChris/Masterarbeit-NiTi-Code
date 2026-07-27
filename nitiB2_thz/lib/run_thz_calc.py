import numpy as np
from multiprocessing import Process
import matplotlib.pyplot as plt
# --------------------------------------------------------------------------------------
import lib.qe_thz_calc as thz
from lib.plot_config import PLOT_SETTINGS

"""
Diese Datei lädt cfg.-Parameter aus z.B. nitiB2_thz_calc_uspp_punkt1.py und aktiviert verschiedene Abschnitte:
- Definition der Pfade
- Plot der Pfade
- Berechnung der Pfade
- Laden und Analyse der Daten

- Es werden mit pw.x bands-Rechnungen entlang verschiedener Pfade berechnet. 
- Die Pfade sind othogonal zu einem Einheitsvektor u.
- Der Anfangsvektor ist: R*u + v + r*a
- v = Verschiebungsvektor
- a = Einheitsvektor für Anfangspfad
- weitere Pfade werden durch Drehung des Anfangsvektors ind er Ebene orthogonal zu u definiert
- a und u müssten orthogonal sein

# ===================================================================================
# Übersicht aller Parameter
# ===================================================================================
# -----------------------------------------------------------------------------------
# Definition der Pfade
# -----------------------------------------------------------------------------------
cfg.nks_list    (list) Liste verschiedener nks-Werte
                        nks: (int) Anzahl der Datenpunkte pro Pfad
cfg.R_list      (list) Liste verschiedener R-Werte
                        R: (float) Radius für den Einheitsvektor u 
cfg.u           (list) (ux,uy,uz) - Einheitsvektor der Ursprungsgerade, um die gedreht wird
cfg.a           (list) (ax, ay, az) - Einheitsvektor für Anfangspfad, der orthogonal zu u liegt
cfg.r           (float) Radius für den Einheitsvektor a
cfg.v           (list) (vx, vy, vz) - Verschiebevektor für den Anfangspfad
cfg.phi_steps   (int) Anzahl der Zwischenpfade zwischen 0° und 180°
cfg.minangle    (float) in deg, minimaler Winkel der Berechnungen (für den Plot)
cfg.maxangle    (flaot) in deg, maximaler Winkel der Berechnungen (für den Plot)
cfg.decimals    (int) legt fest, auf wie viele Nachkommastellen die Pfadvektoren gerundet werden, standart:12

# -----------------------------------------------------------------------------------
# Plot der Pfade
# -----------------------------------------------------------------------------------
cfg.plot_coords (bool) Aktiviert den Plot der Pfade

# -----------------------------------------------------------------------------------
# Berechnung der Pfade
# -----------------------------------------------------------------------------------
cfg.calc        (bool) Aktiviert die Berechung der Pfade durch QE
cfg.datlabel    (str) extra Label in Dateienname, um Rechnungen zu unterscheiden

# -----------------------------------------------------------------------------------
# Laden und Analyse der Daten
# -----------------------------------------------------------------------------------
cfg.analysis    (bool) Aktiviert das Laden und die Analyse der Daten
cfg.bandnumbers (list) Liste der Bänder, die für den Plot ausgewählt werden.
                    Werden genau zwei Bänder gewählt, wird die Differenz berechnet.
                    Achtung: Zählung beginnt bei 0.
"""
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
