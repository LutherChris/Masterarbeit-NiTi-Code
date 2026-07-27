from matplotlib.transforms import Bbox

""" Konfigurationsdatei für globale Plot-Settings"""

# Plot im Fenster Anzeigen?
SHOW = True
# Plots speichern?
SAVE = False
# Name der Datei zum Speichern der Abbildung
DATEIENNAME = "figure"
# Titel in manchen Plots aktivieren?
TITEL = True

# Größe der Figur plt.figure(figsize=(FIGWIDTH,FIGWIDTH*HFACTOR))
TEXTWIDTH_CM = 15.5
FIGWIDTH = 1 * TEXTWIDTH_CM / 2.54  # Umrechnung in Zoll für matplotlib
HFACTOR = 0.6

# Einstellungen für SCATTER-Plots
SCATTER_CONFIG = {"marker": ".",
                  "s": 20}

# Zuschnitt der Abbildung für die Speicherung: xmin, ymin, xmax, yman ODER BBOX=None zur Deaktivierung
xmin = 0.13
ymin = 0.07
xmax = 1.05
ymax = 0.83

BBOX = Bbox([[xmin * FIGWIDTH, ymin * FIGWIDTH * HFACTOR], [xmax * FIGWIDTH, ymax * FIGWIDTH * HFACTOR]])

# Zuschnitt der 

# 3D-Plot (TRUE) ODER 2D-Plot (FALSE)

PLOT3D = True

if PLOT3D:

    # Allgemeine Settings für 3D-Plots
    PLOT_SETTINGS = {
        # Figur
        "figure.dpi": 300,
        "figure.constrained_layout.use": False,
        "figure.autolayout": False,
        # Schriftart
        "text.usetex": True,
        "font.family": "serif",
        "text.latex.preamble": r"""
            \usepackage[T1]{fontenc}
            \usepackage{lmodern}
            \usepackage{siunitx}
        """,
        # Schriftgröße
        "font.size": 9,
        "axes.labelsize": 9,
        "axes.titlesize": 9,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "legend.fontsize": 8,
        # Save
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.05,
        "savefig.dpi": 300,
        # Lage und Beschriftung
        "axes.labelpad": -1, 
        "xtick.major.pad": 0,
        "ytick.major.pad": 0,
        # Linien, Marker
        "lines.linewidth": 0.5,
        "lines.markersize": 1,
        "scatter.edgecolors": "none"
    }

else:

    # Allgemeine Settings für 2D-Plots
    PLOT_SETTINGS = {
        # Figur
        "figure.dpi": 400,
        #"figure.constrained_layout.use": True,
        "figure.constrained_layout.use": False, # Sliderplots
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
        "savefig.dpi": 400,
        # Linien, Marker
        "lines.linewidth": 1,
        "lines.markersize": 2,
        "scatter.edgecolors": "none"
    }