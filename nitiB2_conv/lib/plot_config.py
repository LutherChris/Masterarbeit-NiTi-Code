""" Konfigurationsdatei für globale Plot-Settings """

# Plot im Fenster Anzeigen?
SHOW = True
# Plots speichern?
SAVE = False
# Titel in manchen Plots aktivieren?
TITEL = True

# Größe der Figur plt.figure(figsize=(FIGWIDTH,FIGWIDTH*HFACTOR))
TEXTWIDTH_CM = 15.5
FIGWIDTH = 1 * TEXTWIDTH_CM / 2.54  # Umrechnung in Zoll für matplotlib
HFACTOR = 0.4

# Name der Datei zum Speichern der Abbildung
DATEIENNAME = "figure"

# Allgemeine Settings für 2D-Plots

PLOT_SETTINGS = {
    # Figur
    "figure.dpi": 300,
    "figure.constrained_layout.use": True,
    # Schriftart
    "text.usetex": True,
    "font.family": "serif",
    "text.latex.preamble": r"""
        \usepackage[T1]{fontenc}
        \usepackage{lmodern}
        \usepackage{siunitx}
    """,
    # Schriftgröße
    "font.size": 10,
    "axes.labelsize": 10,
    "axes.titlesize": 10,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
    # Save
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.02,
    "savefig.dpi": 300,
    # Linien, Marker
    "lines.linewidth": 1,
    "lines.markersize":4,
    "scatter.edgecolors": "none"
}