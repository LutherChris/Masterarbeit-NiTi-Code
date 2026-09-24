import matplotlib.pyplot as plt
# --------------------------------------------------------------------------------------
import lib.config as config
import lib.qe_fermi as bands
from lib.plot_config import FIGWIDTH, HFACTOR, DATEIENNAME, SHOW, SAVE, PLOT_SETTINGS

"""
Diese Datei lädt cfg.-Parameter aus z.B. nitiB2_fermi_uspp.py zum plotten der Bandstruktur.

# =======================================================================================
# Übersicht aller Parameter
# =======================================================================================

cfg.gnufile             (str) Dateiname der gnuplot-Datei von QE
                                z.B. "nitiB2bands.dat.gnu"
cfg.fermi_energy        (float) Fermi-Energie aus QE
cfg.plot_fermilevel     (bool) Soll das Fermi-Niveau geplottet werden?
cfg.x_coordinates       (list) Koordinaten des Pfades 
                                z.B. [0, 0.5000, 1.0000, 1.7071, 2.5731]
cfg.x_labels            (list) Koordinatenbezeichnungen des Pfades
cfg.y_lim               (list) Y-Achse wird nur im Berich y_lim[0] undy_lim[1] geplottet (in eV)
"""

def run(cfg):
    # Laden der Plot-Einstellungen aus plot_config.py
    plt.rcParams.update(PLOT_SETTINGS)

    # Laden der Dateienpfade
    gnufile = config.path_gnufile(cfg.gnufile)

    # Erstellung eines Padas-Dataframes aus dem gnufile
    df_list = bands.open_bands_and_split(gnufile)

    # Plot der Energiebänder
    plt.figure(figsize=(FIGWIDTH,FIGWIDTH*HFACTOR))
    bands.plot_bands(df_list, cfg.fermi_energy, fermi=cfg.plot_fermilevel)

    # Plot der Koordinaten
    for i in cfg.x_coordinates:
        plt.axvline(i, color="grey", linestyle="--")

    plt.axhline(0, color="black")
    plt.ylabel(f"$E-E_f$ [eV]")
    plt.xlabel(r"$\vec{k}$-Werte")

    if cfg.x_labels:
        plt.xticks(cfg.x_coordinates, cfg.x_labels)
        plt.tick_params(axis='both',which='both',bottom=False,left=True,top=False)

    if cfg.y_lim:
        plt.ylim(cfg.y_lim[0], cfg.y_lim[1])

    if SAVE:
        plt.savefig(f"{DATEIENNAME}.jpg")
        plt.savefig(f"{DATEIENNAME}.png")
        plt.savefig(f"{DATEIENNAME}.pdf")
    if SHOW:
        plt.show()