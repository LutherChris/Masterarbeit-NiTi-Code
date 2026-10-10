import matplotlib.pyplot as plt
# --------------------------------------------------------------------------------------
import lib.config as config
import lib.qe_fermi as bands
from lib.plot_config import FIGWIDTH, HFACTOR, DATEIENNAME, SHOW, SAVE, PLOT_SETTINGS

# --------------------------------------------------------------------------------------

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