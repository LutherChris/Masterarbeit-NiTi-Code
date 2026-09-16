import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
# -------------------------------------------------------------------------------------
import lib.config as config
from lib.plot_config import FIGWIDTH, HFACTOR, SCATTER_CONFIG, BBOX, DATEIENNAME, SHOW, SAVE, TITEL

# #####################################################################################
# Tricontour und trisurf-Plots
# #####################################################################################

# Globale Einstellungen des THz-aktiven Bereichs
thz_diff=0.01241
thz_diff_mev=12.41
thz_bands=0.05
thz_bands_mev=50.0

def contourplots(a: list,
                 r: float,
                 df_all_df_for_plots: list,
                 df_all_peaks: list,
                 plottype: str,
                 levels: int = 30,
                 peaks: bool = True,
                 xlim_values: tuple = None,
                 ylim_values: tuple = None):
    """
    - erstellt verschiedene contourplots, je nach Keyword plottype

    Args:
        a:                      (ax, ay, az) - Einheitsvektor für Anfangspfad, der orthogonal zu u liegt
        r:                      Radius für den Einheitsvektor a
        df_all_df_for_plots:    Dataframe mit den Daten aller Pfade (aus all_df_for_plots.csv)
        df_all_peaks:           Pandas-Dataframe mit allen Peaks (lokale Minima) aller Pfade (all_peaks.csv)
        plottype:               Keywords:   
                                    "tricontour_diff"     "tricontour_band0"    "tricontour_band1"    "tricontour_limit_diff"
                                    "trisurf_diff"        "trisurf_band0"       "trisurf_band1"       "trisurf_all_bands"
        levels:                 Anzahl der Positionslinien im Plot
        peaks:                  Sollen auch die Peaks als Punkte geplottet werden?
        xlim_values:            Einschränkung der Plots auf einen Bereich der X-Achse
        ylim_values:            Einschränkung der Plots auf einen Bereich der y-Achse
    """
    a = np.array(a)
    avec = a*r
    avec_str = f"[{avec[0]}, {avec[1]}, {avec[2]}]"

    if plottype == "tricontour_diff":
        plt.figure(figsize=(FIGWIDTH,FIGWIDTH*HFACTOR))
        #plt.plot(x_val, y_val, color="red", marker="o", label="Anfangspunkt: "+f"$\\phi$ = 0"+ f"\na={avec_str}")
        plt.scatter(df_all_df_for_plots["x"], df_all_df_for_plots["y"], c="black", **SCATTER_CONFIG)
        plt.tricontour(df_all_df_for_plots["x"], df_all_df_for_plots["y"], df_all_df_for_plots["diff"], levels)
        plt.tricontour(df_all_df_for_plots["x"], df_all_df_for_plots["y"], df_all_df_for_plots["diff"])
        if TITEL:
            plt.title(f"Differenz der Bänder")
        plt.colorbar(format="{x:.2f}")
        #plt.legend() 
        plt.axis('equal')

    elif plottype == "tricontour_band0":
        plt.figure(figsize=(FIGWIDTH,FIGWIDTH*HFACTOR))
        #plt.plot(x_val, y_val, color="red", marker="o", label="Anfangspunkt: "+f"$\\phi$ = 0"+ f"\na={avec_str}")
        plt.scatter(df_all_df_for_plots["x"], df_all_df_for_plots["y"], c="black", **SCATTER_CONFIG)
        plt.tricontour(df_all_df_for_plots["x"], df_all_df_for_plots["y"], df_all_df_for_plots["band0"], levels)
        plt.tricontour(df_all_df_for_plots["x"], df_all_df_for_plots["y"], df_all_df_for_plots["band0"])
        if TITEL:
            plt.title(f"Unteres Band")
        plt.colorbar(format="{x:.2f}")
        #plt.legend() 
        plt.axis('equal')
 
    elif plottype == "tricontour_band1":
        plt.figure(figsize=(FIGWIDTH,FIGWIDTH*HFACTOR))
        #plt.plot(x_val, y_val, color="red", marker="o", label="Anfangspunkt: "+f"$\\phi$ = 0"+ f"\na={avec_str}")
        plt.scatter(df_all_df_for_plots["x"], df_all_df_for_plots["y"], c="black", **SCATTER_CONFIG)
        plt.tricontour(df_all_df_for_plots["x"], df_all_df_for_plots["y"], df_all_df_for_plots["band1"], levels)
        plt.tricontour(df_all_df_for_plots["x"], df_all_df_for_plots["y"], df_all_df_for_plots["band1"])
        if TITEL:
            plt.title(f"Oberes Band")
        plt.colorbar(format="{x:.2f}")
        #plt.legend() 
        plt.axis('equal')
    
    elif plottype == "tricontour_limit_diff":
        plt.figure(figsize=(FIGWIDTH,FIGWIDTH*HFACTOR))
        #plt.plot(x_val, y_val, color="red", marker="o", label="Anfangspunkt: "+f"$\\phi$ = 0"+ f"\na={avec_str}")
        plt.scatter(df_all_df_for_plots["x"], df_all_df_for_plots["y"], c="black", **SCATTER_CONFIG)
        plt.tricontour(df_all_df_for_plots["x"], df_all_df_for_plots["y"], df_all_df_for_plots["diff"], levels=np.linspace(0, max(np.array(df_all_df_for_plots["diff"])), 20), zorder=0)
        plt.colorbar(format="{x:.2f}")
        plt.tricontour(df_all_df_for_plots["x"], df_all_df_for_plots["y"], df_all_df_for_plots["diff"], levels=np.linspace(0, thz_diff, 50), vmin=0, vmax=thz_diff, zorder=1, cmap="Reds")
        #plt.colorbar(label=f"Energie-$E_f$ [eV]", ticks=np.linspace(0, thz_value_diff, 10))
        if peaks:
            plt.scatter(df_all_peaks["x"], df_all_peaks["y"], c="black", zorder=2, s=5)
        if TITEL:
            plt.title(f"Differenz der Bänder")
        #plt.legend() 
        plt.axis('equal')

    elif plottype == "trisurf_diff":
        fig = plt.figure(figsize=(FIGWIDTH,FIGWIDTH*HFACTOR))
        ax = fig.add_subplot(projection='3d')
        ax.plot_trisurf(df_all_df_for_plots["x"], df_all_df_for_plots["y"], df_all_df_for_plots["diff"], cmap='viridis', edgecolor='none')
        ax.scatter(df_all_df_for_plots["x"], df_all_df_for_plots["y"], df_all_df_for_plots["diff"], c="black", **SCATTER_CONFIG)
        ax.set_zlabel(f"$\\Delta E$ [eV]")
        if TITEL:
            plt.title(f"Differenz der Bänder")

    elif plottype == "trisurf_band0":
        fig = plt.figure(figsize=(FIGWIDTH,FIGWIDTH*HFACTOR))
        ax = fig.add_subplot(projection='3d')
        ax.plot_trisurf(df_all_df_for_plots["x"], df_all_df_for_plots["y"], df_all_df_for_plots["band0"], cmap='viridis', edgecolor='none')
        ax.scatter(df_all_df_for_plots["x"], df_all_df_for_plots["y"], df_all_df_for_plots["band0"], c="black", **SCATTER_CONFIG)
        ax.set_zlabel(f"$E-E_f$ [eV]")
        if TITEL:
            plt.title(f"Unteres Band")
    
    elif plottype == "trisurf_band1":
        fig = plt.figure(figsize=(FIGWIDTH,FIGWIDTH*HFACTOR))
        ax = fig.add_subplot(projection='3d')
        ax.plot_trisurf(df_all_df_for_plots["x"], df_all_df_for_plots["y"], df_all_df_for_plots["band1"], cmap='viridis', edgecolor='none')
        ax.scatter(df_all_df_for_plots["x"], df_all_df_for_plots["y"], df_all_df_for_plots["band1"], c="black", **SCATTER_CONFIG)
        ax.set_zlabel(f"$E-E_f$ [eV]")
        if TITEL:
            plt.title(f"Oberes Band")
    
    elif plottype == "trisurf_all_bands":
        fig = plt.figure(figsize=(FIGWIDTH,FIGWIDTH*HFACTOR))
        ax = fig.add_subplot(projection='3d')
        ax.plot_trisurf(df_all_df_for_plots["x"], df_all_df_for_plots["y"], df_all_df_for_plots["band0"], cmap='Purples', edgecolor='none')
        ax.plot_trisurf(df_all_df_for_plots["x"], df_all_df_for_plots["y"], df_all_df_for_plots["band1"], cmap='autumn', edgecolor='none')
        ax.scatter(df_all_df_for_plots["x"], df_all_df_for_plots["y"], df_all_df_for_plots["band0"], c="black", **SCATTER_CONFIG)
        ax.scatter(df_all_df_for_plots["x"], df_all_df_for_plots["y"], df_all_df_for_plots["band1"], c="black", **SCATTER_CONFIG)
        ax.set_zlabel(f"$E-E_f$ [eV]")
        if TITEL:
            plt.title(f"Beide Bänder")

    else:
        raise ValueError(f"Unbekannter Parametername: {plottype}\n verfügbare Parameter:\n tricontour_diff\n tricontour_band0\n tricontour_band1\n tricontour_limit_diff\n trisurf_diff\n trisurf_band0\n trisurf_band1\n trisurf_all_bands")

    if xlim_values is not None:                                              
        plt.xlim(xlim_values)
    if ylim_values is not None:
        plt.ylim(ylim_values)

    # Achsenbeschriftung
    plt.xlabel(r"$\parallel \vec{a}$")
    plt.ylabel(r"$\bot \vec{a}$")
    #plt.axis('off')

    if SAVE:
        plt.savefig(f"{DATEIENNAME}.jpg", bbox_inches=BBOX)
        plt.savefig(f"{DATEIENNAME}.png", bbox_inches=BBOX)
        plt.savefig(f"{DATEIENNAME}.pdf", bbox_inches=BBOX)
    if SHOW:
        plt.show()
    
# #####################################################################################
# Plot der Bänder entlang eines der Pfade
# #####################################################################################

def plot_bandsbands(df_all_df_for_plots: list,
                    df_all_peaks: list,
                    deg: float,
                    sym: bool,
                    R: float,
                    xlim_values: tuple = None,
                    ylim_values: tuple = None):
    """
    - plottet die zwei ausgewählten Energiebänder, zusammen mit deren Differenz
    - geplottet wird der Pfad, dessen Winkel am nächsten zu deg liegt

    Args:
        df_all_df_for_plots:    Dataframe mit den Daten aller Pfade (aus all_df_for_plots.csv)
        df_all_peaks:           Pandas-Dataframe mit allen Peaks (lokale Minima) aller Pfade (all_peaks.csv)
        deg:                    Plottet den Pfad in der kx-Ebene, welcher am nächsten am Winkel deg (in °) liegt
        sym:                    mit sym=True wird auch der um 180° gedrehte gegenüberliegende Pfad geplottet
        R:                      Radius für den Einheitsvektor u
        xlim_values:            Einschränkung der Plots auf einen Bereich der X-Achse
        ylim_values:            Einschränkung der Plots auf einen Bereich der y-Achse
    """
    # Finde alle verfügbaren phi-Werte
    phi_list = pd.unique(df_all_df_for_plots["phi"])

    # Finde den Wert, der am nächsten an deg liegt und definiere neue Dataframe mit nur diesem phi
    phi_nearest_0 = phi_list[np.abs(phi_list - deg).argmin()]
    df_0 = df_all_df_for_plots.loc[df_all_df_for_plots["phi"] == phi_nearest_0]
    df_peaks_0 = df_all_peaks.loc[df_all_peaks["phi"] == phi_nearest_0]
    print(df_peaks_0)
    # Dataframe für 180°-gedrehten Pfad
    if sym:
        deg1 = (deg + 180) % 360
        phi_nearest_1 = phi_list[np.abs(phi_list - deg1).argmin()]
        df_1 = df_all_df_for_plots.loc[df_all_df_for_plots["phi"] == phi_nearest_1]
        df_peaks_1 = df_all_peaks.loc[df_all_peaks["phi"] == phi_nearest_1]

    # Plot der Bänder und der Differenz der Bänder in Abhängigkeit des Polar-Radius rho
    plt.figure(figsize=(FIGWIDTH,FIGWIDTH*HFACTOR))
    colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
    plt.plot(df_0["rho"], df_0["band0"], ".",  color=colors[0])
    #plt.plot(df_0["rho"], df_0["band0"], "-", color=colors[0])
    plt.plot(df_0["rho"], df_0["band0"], "-", color=colors[0], label=f"$E_0$")
    plt.plot(df_0["rho"], df_0["band1"], ".",  color=colors[1])
    #plt.plot(df_0["rho"], df_0["band1"], "-", color=colors[1])
    plt.plot(df_0["rho"], df_0["band1"], "-", color=colors[1], label=f"$E_1$")
    plt.plot(df_0["rho"], df_0["diff"], "-", color="black")
    plt.plot(df_0["rho"], df_0["diff"], "-", color="black", label=f"$\\Delta E$")
    if sym:
        plt.plot(-df_1["rho"], df_1["band0"], ".",  color=colors[0])
        plt.plot(-df_1["rho"], df_1["band0"], "-", color=colors[0])
        plt.plot(-df_1["rho"], df_1["band1"], ".",  color=colors[1])
        plt.plot(-df_1["rho"], df_1["band1"], "-", color=colors[1])
        plt.plot(-df_1["rho"], df_1["diff"], "-", color="black")

    # Plot der Fermi-Energie
    plt.axhline(0, ls="--", color="red")
    plt.axhline(0, ls="--", color="red", label=f"Fermi-Energie = {df_0["fermi_energy"].iloc[0]:.4f} eV")

    # Plot der Peaks    
    #label_0 = f"$\\Delta E_1$={np.min(np.array(df_peaks_0["diff"])*1e3):.3f} meV,    $\\rho_1$={np.unique(np.array(df_peaks_0["rho"]))}"
    band0 = np.unique(df_peaks_0["band0"].values * 1e3)
    band1 = np.unique(df_peaks_0["band1"].values * 1e3)
    diffs = np.unique(df_peaks_0["diff"].values * 1e3)
    rhos = np.unique(df_peaks_0["rho"].values)

    label_0 = "\n".join([ f"$E_{{0,{i}}} = {e0:.3f}$ meV, $E_{{1,{i}}} = {e1:.3f}$ meV, \n$\\Delta E_{i} = {d:.3f}$ meV, $\\rho_{i} = {r:.5f}$"for i, (e0, e1, d, r) in enumerate(zip(band0, band1, diffs, rhos)) ])

    plt.plot(df_peaks_0["rho"], df_peaks_0["diff"], ".", color="lime", label=label_0, markersize=4)
    
    if sym:
        label_1 = f"$\\Delta E_2$={np.min(np.array(df_peaks_1["diff"])*1e3):.3f} meV,    $\\rho_2$={np.unique(np.array(df_peaks_1["rho"]))}"
        plt.plot(-df_peaks_1["rho"], df_peaks_1["diff"], ".",  color="lime", label=label_1)
        plt.plot(-df_peaks_1["rho"], df_peaks_1["diff"], ".", color="lime", markersize=4)

    # Ploteinstellungen und Plot der vertikalen Linien
    plt.axvline(df_0["rho"].iloc[-1], color="black")
    if sym:
        plt.axvline(-df_0["rho"].iloc[-1], color="black")
    else:
        plt.axvline(0, color="black")

    if xlim_values is not None:                                              
        plt.xlim(xlim_values)
    if ylim_values is not None:
        plt.ylim(ylim_values)

    if sym:
        if TITEL:
            plt.title(f"Bandenergien und Differenz der Bänder für Pfad $\\phi$={phi_nearest_0:.1f}° und $\\phi$={phi_nearest_1:.1f}°; R={R}")
        plt.xlabel(f"{phi_nearest_1:.1f}°    $\\leftarrow$    Radius in Polarebene    $\\rightarrow$    {phi_nearest_0:.1f}°")
    else:
        if TITEL:
            plt.title(f"Bandenergien und Differenz der Bänder für Pfad $\\phi$={phi_nearest_0:.1f}°; R={R}")
        plt.xlabel(f"Radius in Polarebene    $\\rightarrow$    {phi_nearest_0:.1f}°")
    
    plt.ylabel(f"$E - E_f$ [eV]")
    #plt.legend(loc='upper left', bbox_to_anchor=(0, -0.2))  
    plt.legend(framealpha=0.9, ncols=2)
    
    if SAVE:
        plt.savefig(f"{DATEIENNAME}.jpg", bbox_inches=BBOX)
        plt.savefig(f"{DATEIENNAME}.png", bbox_inches=BBOX)
        plt.savefig(f"{DATEIENNAME}.pdf", bbox_inches=BBOX)
    if SHOW:
        plt.show()
    
# #####################################################################################
# Plot in Abhängigkeit des Rotationswinkels
# #####################################################################################

def plot_vs_phi(df_all_peaks: list,
                df_phi_peaks: list,
                R: float):
    """
    - plottet die Banddifferenz und Bänder in Abhängigkeit des Rotationswinkels
    Args:
        df_all_peaks:   Pandas-Dataframe mit allen Peaks (lokale Minima) aller Pfade (all_peaks.csv)
        df_phi_peaks:   Pandas-Dataframe mit den Minima der Peaks
        R:              Radius für den Einheitsvektor u
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(FIGWIDTH,FIGWIDTH*HFACTOR)) # zwei Abbildungen nebeneinander
    
    # pro Winkel (phi) genau den Datenpunkt, bei dem die Differenz (diff) am geringsten ist
    df_Emin = df_all_peaks.loc[df_all_peaks.groupby("phi")["diff"].idxmin()]

    # Alle Daten als Arrays, Umrechnung der Energie im meV
    phi_all = df_all_peaks["phi"] # Winkel in deg
    diff_all = np.multiply(np.array(df_all_peaks["diff"]), 1e3)   # Differenz der Bänder in meV
    band0_all = np.multiply(np.array(df_all_peaks["band0"]), 1e3) # unteres Band in meV
    band1_all = np.multiply(np.array(df_all_peaks["band1"]), 1e3) # oberes Band in meV

    phi_all_Emin = df_Emin["phi"] # Winkel in deg
    diff_all_Emin = np.multiply(np.array(df_Emin["diff"]), 1e3)   # Differenz der Bänder in meV
    band0_all_Emin = np.multiply(np.array(df_Emin["band0"]), 1e3) # unteres Band in meV
    band1_all_Emin = np.multiply(np.array(df_Emin["band1"]), 1e3) # oberes Band in meV
    
    # Plot der Energien
    ax1.plot(phi_all, diff_all, ".", color="black")
    ax1.plot(phi_all_Emin, diff_all_Emin, "-", label=f"$\\Delta E$")
    ax2.plot(phi_all, band0_all, ".", color="black")
    ax2.plot(phi_all_Emin, band0_all_Emin, "-", label=f"$E_0$")
    ax2.plot(phi_all, band1_all, ".", color="black")
    ax2.plot(phi_all_Emin, band1_all_Emin, "-", label=f"$E_1$")

    # globale Minima als horizontale Linien
    index = np.argmin(np.array(df_phi_peaks["diff"]))
    diff_mins = np.multiply(np.array(df_phi_peaks["diff"]), 1e3)[index]
    band0_mins = np.multiply(np.array(df_phi_peaks["band0"]), 1e3)[index]
    band1_mins = np.multiply(np.array(df_phi_peaks["band1"]), 1e3)[index]

    ax1.axhline(diff_mins, color="lime", label=f"{diff_mins:.1f} meV", linestyle="-.", zorder=1)
    ax2.axhline(band0_mins, color="lime", label=f"$E_0$: {band0_mins:.1f} meV\n$E_1$: {band1_mins:.1f} meV", linestyle="-.", zorder=1)
    ax2.axhline(band1_mins, color="lime", linestyle="-.", zorder=1)

    # Horizontale Linien des THz-Bereichs
    ax1.axhline(thz_diff_mev, color="blue", label=f"$\\pm${thz_diff_mev} meV")
    ax1.axhline(-thz_diff_mev, color="blue")

    ax2.axhline(thz_bands_mev, color="blue", label=f"$\\pm${thz_bands_mev} meV")
    ax2.axhline(-thz_bands_mev, color="blue")
    
    # Fermi-Energie
    ax1.axhline(0, ls="--", color="red", label=f"$E_f$={df_phi_peaks["fermi_energy"][0]:.4f}eV")
    ax2.axhline(0, ls="--", color="red")

    # Ploteinstellungen
    ax1.set_ylabel("$\\Delta E$ [meV]")
    ax1.set_xlabel(f"$\\phi$ [°]")
    ax1.legend(framealpha=0.9, ncols=2)
    ax1.grid()
    ax2.set_ylabel("$E - E_f$ [meV]")
    ax2.set_xlabel(f"$\\phi$ [°]")
    ax2.legend(framealpha=0.9, ncols=2)
    ax2.grid()
    
    if TITEL:
        ax1.set_title(f"Minima der Banddifferenz in Abhängigkeit des Winkels\nfür R={np.round(R,6)}")
        ax2.set_title(f"Minima der Bänder in Abhängigkeit des Winkels\nfür R={np.round(R,6)}")

    plt.setp((ax1, ax2), xticks=np.linspace(0, 360, 5))
    #ax1.set_ylim(-max(abs(diff_all))*1.5, max(abs(diff_all))*1.5)

    if SAVE:
        plt.savefig(f"{DATEIENNAME}.jpg", bbox_inches=BBOX)
        plt.savefig(f"{DATEIENNAME}.png", bbox_inches=BBOX)
        plt.savefig(f"{DATEIENNAME}.pdf", bbox_inches=BBOX)
    if SHOW:
        plt.show()

# #####################################################################################
# Plot in Abhängigkeit von R
# #####################################################################################

def plot_vs_R(R_list: list,
              r: float,
              phi_steps: int,
              nks: int,
              datlabel: str,
              symmetry: int,
              philabel=True,
              thz_area=False):
    """
    - plottet die Minima aller Pfade in Abhängigkeit von R
    - das jeweilige globale Minima wird extra beschriftet
    
    Args:
        R_list:     Liste der R-Werte
        r:          Radius für den Einheitsvektor a
        phi_steps:  Anzahl der Zwischenpfade zwischen 0° und 180°
        nks:        Anzahl der Datenpunkte pro Pfad
        datlabel:   extra Label in Dateienname, um Rechnungen nochmal gezielt zu unterscheiden
        symmetry:   Symmetrie der Daten (für Label der globalen Minima)
        philabel:   Sollen die globalen Mimima farbig in die Legende geplottet werden?
        thz_area:   Datenpunkte werden nach der THz-Bedingung gefiltert
    """
    # lade Dateien
    df_1_list = [] # "all_peaks"
    df_2_list = [] # "phi_global_peaks
    for R in R_list:
        path_out_directory = config.path_out_directory(datlabel, nks, phi_steps, R, r)
        df_1 = config.load_csv(path_out_directory, "all_peaks")
        df_2 = config.load_csv(path_out_directory, "phi_global_peaks")
        df_1_list.append(df_1)
        df_2_list.append(df_2)

    # füge alle Dataframes zusammen
    df_all_1 = pd.concat(df_1_list, ignore_index=True)
    df_all_2 = pd.concat(df_2_list, ignore_index=True)

    # Umrechnung der Energien in meV
    x_1 = np.array(df_all_1["R"])
    diff_1 = np.multiply(np.array(df_all_1["diff"]), 1e3)   # in meV
    band0_1 = np.multiply(np.array(df_all_1["band0"]), 1e3) # in meV
    band1_1 = np.multiply(np.array(df_all_1["band1"]), 1e3) # in meV

    x_2 = np.array(df_all_2["R"])
    diff_2 = np.multiply(np.array(df_all_2["diff"]), 1e3)   # in meV
    band0_2 = np.multiply(np.array(df_all_2["band0"]), 1e3) # in meV
    band1_2 = np.multiply(np.array(df_all_2["band1"]), 1e3) # in meV

    # Filterung nach der THz-Bedinung
    if thz_area:
        diff_1_indis = np.where(diff_1 < thz_diff_mev)[0]
        band0_1_indis = np.where(band0_1 > -thz_bands_mev)[0]
        band1_1_indis = np.where(band1_1 < thz_bands_mev)[0]
        
        # Schnittmenge aller drei Bedinungen
        thz_1_indis = set(diff_1_indis) & set(band0_1_indis) & set(band1_1_indis)
        thz_1_indis = list(thz_1_indis)
        x_1_ = x_1[thz_1_indis]
        diff_1_ = diff_1[thz_1_indis]
        band0_1_ = band0_1[thz_1_indis]
        band1_1_ = band1_1[thz_1_indis]

    # Plot der Datenpunkte
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(FIGWIDTH,FIGWIDTH*HFACTOR)) # zwei Abbildungen nebeneinander

    # alle Datenpunkte
    ax1.plot(x_1, diff_1, ".", color="black", zorder=1)
    ax2.plot(x_1, band0_1, ".", color="black", zorder=1)
    ax2.plot(x_1, band1_1, ".", color="black", zorder=1)

    thz_color = "#6DDF21"
    if thz_area:
        ax1.plot(x_1_, diff_1_, "x", markersize=4, color=thz_color, zorder=3, label=f"$\\Delta E <$ {thz_diff_mev} meV\n $E_0>$-{thz_bands_mev} meV\n $E_1<${thz_bands_mev} meV")
        ax2.plot(x_1_, band0_1_, "x", markersize=4, color=thz_color, zorder=3)
        #ax2.plot(x_1_, band1_1_, "x", color=thz_color, zorder=3, label=f"$\\Delta E <$ {thz_diff_mev} meV\n $E_0 >$-{thz_bands_mev} meV\n $E_1<${thz_bands_mev} meV")


    # globale Minima
    color_ = ["#0095ff", "#d121ec", "#49c945", "#ff9900", "#ff0004", "#1100ff"]

    # Label erstellen
    if philabel and not thz_area:
        minima_set = np.unique(df_all_2['phi'] % int(360/symmetry))
        
        for j, phi in enumerate(minima_set):
            ax1.plot([], [], "o", color=color_[j], label=f"$\\phi$={phi:.1f}")
            #ax2.plot([], [], ".", color=color_[j], label=f"$\\phi$={phi:.1f}")

        for i, x in enumerate(x_2):
            for j, phi in enumerate(minima_set):
                if phi == df_all_2['phi'][i]:
                    color = color_[j]
            ax1.plot(x, diff_2[i], "o", color=color, zorder=2)
            ax2.plot(x, band0_2[i], "o", color=color, zorder=2)
            ax2.plot(x, band1_2[i], "o", color=color, zorder=2)

    # Konvergenzkriterium
    ax1.axhline(thz_diff_mev, color="blue", label=f"$\\pm${thz_diff_mev} meV")
    ax1.axhline(-thz_diff_mev, color="blue")

    ax2.axhline(thz_bands_mev, color="blue", label=f"$\\pm${thz_bands_mev} meV")
    ax2.axhline(-thz_bands_mev, color="blue")

    # Ploteinstellungen
    ax1.axhline(0, color="red",ls="--")
    ax1.set_xlabel("R")
    ax1.set_ylabel(f"$\\Delta E$ [meV]")
    ax1.legend(framealpha=1, ncols=1)

    # Fermi-Energie
    ax2.axhline(0, color="red",ls="--", label=f"$E_f$ = {df_all_1["fermi_energy"][0]:.4f} eV")

    # Achsenbeschriftung
    ax2.set_xlabel("R")
    ax2.set_ylabel(f"E - $E_f$ [meV]")

    # Legende
    ax2.legend(framealpha=1, ncols=1)
    #ax.legend(loc='upper left', bbox_to_anchor=(0, -0.1))

    if TITEL:
        ax1.set_title("Minima aller Banddifferenzen in Abhängigkeit von R")
        ax2.set_title("Minima aller Bänder in Abhängigkeit von R")
    if SAVE:
        plt.savefig(f"{DATEIENNAME}.jpg", bbox_inches=BBOX)
        plt.savefig(f"{DATEIENNAME}.png", bbox_inches=BBOX)
        plt.savefig(f"{DATEIENNAME}.pdf", bbox_inches=BBOX)
    if SHOW:
        plt.show()


# #####################################################################################
# 3D - Plot in Abhängigkeit von R und phi
# #####################################################################################

def plot_vs_phi_R(R_list: list,
                  r: float,
                  phi_steps: int,
                  nks: int,
                  datlabel: str,
                  plottype: str,
                  thz_area = True):
    """
    - plottet die Differenz der Bänder oder Bänder selbst in Abhängigkeit von R und phi als Flächen in 3D
    Args:
        R_list:     Liste der R-Werte
        r:          Radius für den Einheitsvektor a
        phi_steps:  Anzahl der Zwischenpfade zwischen 0° und 180°
        nks:        Anzahl der Datenpunkte pro Pfad
        datlabel:   extra Label in Dateienname, um Rechnungen nochmal gezielt zu unterscheiden
        plottype:   Keywords: "diff", "bands", "R"
        thz_area:   aktiviert Filterung nach der THz-Bedinung
    """
    # Dateien laden
    df_list = []
    for R in R_list:
        path_out_directory = config.path_out_directory(datlabel, nks, phi_steps, R, r)
        df_ = config.load_csv(path_out_directory, "all_peaks")
        df_list.append(df_)
    df_all = pd.concat(df_list, ignore_index=True)
    
    # Umrechnung in meV
    phi = np.array(df_all["phi"])
    R_data = np.array(df_all["R"])
    diff = np.multiply(np.array(df_all["diff"]), 1e3) # in meV
    band0 = np.multiply(np.array(df_all["band0"]), 1e3) # in meV
    band1 = np.multiply(np.array(df_all["band1"]), 1e3) # in meV

    # Filterung nach der THz-Bedinung
    if thz_area:
        diff_indis = np.where(diff < thz_diff_mev)[0]
        band0_indis = np.where(band0 > -thz_bands_mev)[0]
        band1_indis = np.where(band1 < thz_bands_mev)[0]
        
        # Schnittmenge aller drei Bedinungen
        mask = np.isin(diff_indis, band0_indis) & np.isin(diff_indis, band1_indis)
        thz_indis = diff_indis[mask]

        phi_ = phi[thz_indis]
        R_data_ = R_data[thz_indis]
        diff_ = diff[thz_indis]
        band0_ = band0[thz_indis]
        band1_ = band1[thz_indis]
    
    if plottype == "diff":
        fig = plt.figure(figsize=(FIGWIDTH,FIGWIDTH*HFACTOR))
        ax = fig.add_subplot(projection='3d', computed_zorder=False)

        ax.plot_trisurf(R_data, phi, diff, cmap='viridis', edgecolor='none')
        if thz_area:
            ax.scatter(R_data_, phi_, diff_, c='red', alpha=1, depthshade=False, **SCATTER_CONFIG)  
        
        ticks = np.arange(0, 361, 90) 
        ax.set_yticks(ticks) 
        plt.xlabel(" R")
        plt.ylabel(f" $\\phi$ [°]")
        ax.set_zlabel(f" $\\Delta E~[meV]$")

        if TITEL:
            plt.title(f"Differenz der Bänder [meV]")
        if SAVE:
            plt.savefig(f"{DATEIENNAME}.jpg", bbox_inches=BBOX)
            plt.savefig(f"{DATEIENNAME}.png", bbox_inches=BBOX)
            plt.savefig(f"{DATEIENNAME}.pdf", bbox_inches=BBOX)
        if SHOW:
            plt.show()

    elif plottype == "bands":
        fig = plt.figure(figsize=(FIGWIDTH,FIGWIDTH*HFACTOR))
        ax = fig.add_subplot(projection='3d')
        ax.plot_trisurf(R_data, phi, band0, cmap='viridis', edgecolor='none')
        ax.plot_trisurf(R_data, phi, band1, cmap='autumn', edgecolor='none')
        ax.scatter(R_data, phi, band0, c="black", **SCATTER_CONFIG)
        ax.scatter(R_data, phi, band1, c="black", **SCATTER_CONFIG)
        plt.xlabel("R")
        plt.ylabel(f"$\\phi [°]$")

        if TITEL:
            plt.title(f"Beide Bänder [meV]")
        if SAVE:
            plt.savefig(f"{DATEIENNAME}.jpg", bbox_inches=BBOX)
            plt.savefig(f"{DATEIENNAME}.png", bbox_inches=BBOX)
            plt.savefig(f"{DATEIENNAME}.pdf", bbox_inches=BBOX)
        if SHOW:
            plt.show()

    elif plottype == "R":
        fig = plt.figure(figsize=(FIGWIDTH,FIGWIDTH*HFACTOR))
        plt.plot(R_data, diff, ".", color="black")
        plt.xlabel("R")
        plt.ylabel("Energie [eV]")

        if TITEL:
            plt.title(f"Projektion: Differenz in Abhängigkeit von R")
        if SAVE:
            plt.savefig(f"{DATEIENNAME}.jpg", bbox_inches=BBOX)
            plt.savefig(f"{DATEIENNAME}.png", bbox_inches=BBOX)
            plt.savefig(f"{DATEIENNAME}.pdf", bbox_inches=BBOX)
        if SHOW:
            plt.show()

    else:
        raise ValueError(f"Unbekannter Parametername: {plottype}")

