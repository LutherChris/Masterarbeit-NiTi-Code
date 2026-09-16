import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

import lib.qe_model_calc as model
from lib.plot_config import FIGWIDTH, HFACTOR, SCATTER_CONFIG, BBOX, DATEIENNAME, SHOW, SAVE, TITEL

# ######################################################################################
# Definition des Gitters
# ######################################################################################

# --------------------------------------------------------------------------------------
# regelmäßige einfache Gitter
# --------------------------------------------------------------------------------------

def regular_grid(axis: list):
    """
    - vektorisierte Funktion zum Erzeugen eines kartesischen Gitters am Koordinatenursprung
    Args:
        axis:           Koordinatenachsen [axis[0], axis[1], axis[2]]
                        axis[i] sind Numpy-Arrays
    Return:
        k_grid_center:  Vektoren des Gitters im Koordinatenursprung {x,y,z}
    """
    # Erzeuge 3D Gitter 
    X, Y, Z = np.meshgrid(axis[0], axis[1], axis[2], indexing='ij')
    k_grid_center = np.stack((X, Y, Z), axis=-1).reshape(-1, 3)

    print(f"----> Anzahl der k-Punkte: {len(k_grid_center)}")

    return k_grid_center

def cylindrical_grid(axis: list,
                     z_axis: str):
    """
    - vektorisierte Funktion zum Erzeugen eines zylindrischen Gitter entlang der Hauptachsen am Koordinatenursprung
    Args:
        axis:           Koordinatenachsen [axis[0], axis[1], axis[2]]
                        axis[i] sind Numpy-Arrays
        z_axis:         Achse des Zylinders ("x", "y", oder "z")
    Return:
        k_grid_center:  Vektoren des Gitters im Koordinatenursprung {x,y,z}
    """
    R, PHI, Z = np.meshgrid(axis[0], axis[1], axis[2], indexing='ij')
    
    # Berechne kartesische Koordinaten
    if z_axis == "x":
        k_grid_center = np.stack((Z, R * np.cos(PHI), R * np.sin(PHI)), axis=-1).reshape(-1, 3)
    elif z_axis == "y":
        k_grid_center = np.stack((R * np.cos(PHI), Z, R * np.sin(PHI)), axis=-1).reshape(-1, 3)
    elif z_axis == "z":
        k_grid_center = np.stack((R * np.cos(PHI), R * np.sin(PHI), Z), axis=-1).reshape(-1, 3)
    else:
        raise ValueError(f"Fehler: falscher z_axis-Parameter: {z_axis}! Verfügbare Parameter: ’x’, ’y’, ’z’")

    print(f"----> Anzahl der k-Punkte: {len(k_grid_center)}")

    return k_grid_center

# --------------------------------------------------------------------------------------
# regelmäßige Pfad-Gitter
# --------------------------------------------------------------------------------------

def path_grid(modeltype_path: str,
              axis: list,
              a_coeffs: list,
              b_coeffs: list):
    """
    - vektorisierte Funktion für Polarkoordinaten-Gitter entlang des Pfades
    - verwendet Funktion load_path aus qe_model_calc.py als Hilfsfunktion

    Args: 
        modeltype_path:     Modell des Pfades der Schnittpunktumgebung
        axis:               Koordinatenachsen [axis[0], axis[1], axis[2]]
                            axis[i] sind Numpy-Arrays
        a_coeffs:           a-Koeffizienten des Pfades
        b_coeffs:           b-Koeffizienten des Pfades
    Return:
        k_grid_center:  Vektoren des Gitters im Koordinatenursprung {x,y,z}
        t_grid_center:  Vektoren des Gitters in Pfadkoordinaten {t, rho, phi}
    """
    t_lin, rho_lin, phi_lin = axis[0], axis[1], axis[2]

    # Pfad und Frenetsches Dreibei
    r, _, B, N, _ = model.load_path(modeltype_path, axis[0], a_coeffs, b_coeffs)

    t_idx = np.arange(len(t_lin))
    I, RHO, PHI = np.meshgrid(t_idx, rho_lin, phi_lin, indexing='ij')

    X = r[I, 0] + RHO * np.sin(PHI) * N[I, 0] + RHO * np.cos(PHI) * B[I, 0]
    Y = r[I, 1] + RHO * np.sin(PHI) * N[I, 1] + RHO * np.cos(PHI) * B[I, 1]
    Z = r[I, 2] + RHO * np.sin(PHI) * N[I, 2] + RHO * np.cos(PHI) * B[I, 2]

    k_grid_center = np.stack((X, Y, Z), axis=-1).reshape(-1, 3)
    
    T_mesh = t_lin[I]
    t_grid_center = np.stack((T_mesh, RHO, PHI), axis=-1).reshape(-1, 3)

    print(f"----> Anzahl der k-Punkte: {len(t_grid_center)}")
    
    return k_grid_center, t_grid_center

def path_grid_2B(axis: list,
                 a_coeffs: list):
    """
    - verwendet Funktionen make_rho_phi_grid und load_path als Hilfsfunktionen

    - Polarkoordinaten-Gitter entlang der Pfade von Punkt2A und Punkt2B
    - optionale n-fach-Symmetrie
    - optionale Verdichtung um Punkt2A uns Punkt2B in Richtung von rho und phi

    Args:
        k0:                 Verschiebungsvektor auf Schnittpunkt der Bänder
        p:                  Kantenlängen: [halbe Kantenlänge in t-Richtung, Radius in der Polarebene, 0]
        n:                  Anzahl der Datenpunkte: [N_t, N_rhoA, N_phi]
        a_coeffs:           a-Koeffizienten des Pfades
        phi_sym:            Anzahl der Symmetrie-Sektoren, keine Symmetrie: {0,1}
        phi_sigma:          phi-abhängige Gauß-Verdichtung um Punkte 2B in Abhängigkeit von t
        rho_sigma0:         Stärke der radialen Gaus-Dichte um rho=0 (Punkt2A)
        rho_sigmaB:         Stärke der radialen Gaus-Dichte um rho=0 (Punkt2A) in Abhängigkeit von t
        no_rho0:            rho=0 wird entfernt
        decimals:           legt fest, auf wie viele Nachkommastellen die Pfadvektoren gerundet werden, standart:12
    Return:
        k_grid:             Vektoren des k-Gitters {kx_ky_kz}
        k_grid_center:      Vektoren des Gitters im Koordinatenursprung {x,y,z}
        coords:             Liste der kpoints Koordinaten für Quantum Espresso
        t_grid_center:      Vektoren des Gitters in Pfadkoordinaten {t, rho, phi}
    """
    t_lin, rho_lin, phi_lin = axis[0], axis[1], axis[2]
    
    # Pfade laden
    rA, T, B, N, kappa = model.load_path("path_point2A", t_lin)                  # shape: (n_t, 3)
    rB1, rhoB, _ = model.load_path_point2B("path_point2B", t_lin, a_coeffs, 0)           # shape: (n_t, 3)
    rB2, _ , _ = model.load_path_point2B("path_point2B", t_lin, a_coeffs, (2/3)*np.pi)   # shape: (n_t, 3)
    rB3, _, _ = model.load_path_point2B("path_point2B", t_lin, a_coeffs, (4/3)*np.pi)    # shape: (n_t, 3)

    rho_lin = np.append(rho_lin, rhoB)
    rho_lin = np.sort(rho_lin)
 
    # verwende nur t-Werte, bei denen rhoB >= 0 ist
    mask = rhoB >= 0
    rhoB = rhoB[mask]
    t_lin = t_lin[mask]
    rA, B, N = rA[mask,:], B[mask, :], N[mask, :]
    rB1, rB2, rB3 = rB1[mask,:], rB2[mask,:], rB3[mask,:]
        
    # Definition des Gitters
    t_idx = np.arange(len(t_lin))
    I, RHO, PHI = np.meshgrid(t_idx, rho_lin, phi_lin, indexing='ij')

    X = rA[I, 0] + RHO * np.sin(PHI) * N[I, 0] + RHO * np.cos(PHI) * B[I, 0]
    Y = rA[I, 1] + RHO * np.sin(PHI) * N[I, 1] + RHO * np.cos(PHI) * B[I, 1]
    Z = rA[I, 2] + RHO * np.sin(PHI) * N[I, 2] + RHO * np.cos(PHI) * B[I, 2]

    k_grid_center = np.stack((X, Y, Z), axis=-1).reshape(-1, 3)
    
    T_mesh = t_lin[I]
    t_grid_center = np.stack((T_mesh, RHO, PHI), axis=-1).reshape(-1, 3)

    print(f"----> Anzahl der k-Punkte: {len(t_grid_center)}")

    return k_grid_center, t_grid_center

# ######################################################################################
# Speichern der Modell-Energien
# ######################################################################################

# Erstellung eines Pandas Dataframes

def create_dataframe(k0: list,
                     k_grid_center: list,
                     t_grid: list,
                     energy_model: list):
    """
    - erstellt ein Pandas Dataframe mit den Koordinaten und Modell-Energien

    Args:
        k0:             Verschiebungsvektor auf Schnittpunkt der Bänder
        k_grid_center:  Vektoren des Gitters im Koordinatenursprung {x,y,z}
        t_grid:         Vektoren des Gitters im Pfad-Koordinatensystem {t,rho,phi}
        energy_model:   Modellenergien
    Return:
        df:             Pandas Dataframe 
    """

    df = pd.DataFrame({
        "kx": k_grid_center[:, 0] + k0[0],
        "ky": k_grid_center[:, 1] + k0[1],
        "kz": k_grid_center[:, 2] + k0[2],
        "x": k_grid_center[:, 0],
        "y": k_grid_center[:, 1],
        "z": k_grid_center[:, 2],
        "energy": energy_model
    })
    
    # Füge Pfad-Koordinatensystem hinzu
    if t_grid is not None:
        df["t"] = t_grid[:, 0]
        df["rho"] = t_grid[:, 1]
        df["phi"] = t_grid[:, 2]
    
    return df
    
# ######################################################################################
# Plots
# ######################################################################################

def model_2Dplots(plot_axis: str,
                  axis: list,
                  energy_model: str,
                  coord_system: str):
    """
    - einfache 2D-Slider-Plots entlang der Achse axis
    Args:
        axis:           Achse, entland geplottet wird: z.B. "x"
        energy_model:   Energie-Achse (Parametername im Pandas Dataframe)
        coord_system:   Koordinatensystem der Daten aus dem Dataframe
    """
    # Daten einlesen:
    if coord_system == "xyz":
        x_axis = "x"
        y_axis = "y"
        z_axis = "z"
    elif coord_system == "path":
        x_axis = "t"
        y_axis = "rho"
        z_axis = "phi"
    else:
        raise ValueError(f"coord_system={coord_system}; Dieses Koordinatensystem existiert nicht!")
    
    x_data = axis[0]
    y_data = axis[1]
    z_data = axis[2]
    
    # Wertebereiche
    x_vals = np.unique(x_data)
    y_vals = np.unique(y_data)
    z_vals = np.unique(z_data)

    # Standart-Idizes
    idx_x_init = int((len(x_vals)-1)/2)
    idx_y_init = int((len(y_vals)-1)/2)
    idx_z_init = int((len(z_vals)-1)/2)

    fig, ax = plt.subplots(figsize=(FIGWIDTH,FIGWIDTH*HFACTOR))
    plt.subplots_adjust(bottom=0.25)  # Platz für Slider
    colors = plt.rcParams['axes.prop_cycle'].by_key()['color'] # Farbenliste

    # leere Linienobjekte
    energy_dots, = ax.plot([], [], ".", color=colors[0])
    energy_line, = ax.plot([], [], "-", color=colors[0])

    # Update-Funktion
    def update_plot(axis, idx_x, idx_y, idx_z):
        x = x_vals[int(idx_x)]
        y = y_vals[int(idx_y)]
        z = z_vals[int(idx_z)]

        # ---- Slider-Texte aktualisieren ----
        if axis == x_axis:
            txt_slider_1.set_text(f"{y_axis} = {y:.3g}")
            txt_slider_2.set_text(f"{z_axis} = {z:.3g}")
            mask = (y_data == y) & (z_data == z)
            x_plot = x_data[mask]
            y_plot = energy_model[mask]
        elif axis == y_axis:
            txt_slider_1.set_text(f"{x_axis} = {x:.3g}")
            txt_slider_2.set_text(f"{z_axis} = {z:.3g}")
            mask = (x_data == x) & (z_data == z)
            x_plot = y_data[mask]
            y_plot = energy_model[mask]
        elif axis == z_axis:
            txt_slider_1.set_text(f"{x_axis} = {x:.3g}")
            txt_slider_2.set_text(f"{y_axis} = {y:.3g}")
            mask = (x_data == x) & (y_data == y)
            x_plot = z_data[mask]
            y_plot = energy_model[mask]
        else:
            raise ValueError("Unbekannte Achse")
        
        sort_idx = np.argsort(x_plot)
        energy_dots.set_data(x_plot[sort_idx], y_plot[sort_idx])
        energy_line.set_data(x_plot[sort_idx], y_plot[sort_idx])
        ax.relim()
        ax.autoscale_view()
        fig.canvas.draw_idle()

    # Slider-Achsen erstellen
    ax_slider_1 = plt.axes([0.15, 0.11, 0.65, 0.03])
    ax_slider_2 = plt.axes([0.15, 0.06, 0.65, 0.03])
    # ---- Text neben Slider ----
    txt_slider_1 = ax_slider_1.text(1.08, 0.5, "", transform=ax_slider_1.transAxes, va="center")
    txt_slider_2 = ax_slider_2.text(1.08, 0.5, "", transform=ax_slider_2.transAxes, va="center")

    if plot_axis == x_axis:
        slider_1 = Slider(ax_slider_1, y_axis, 0, len(y_vals)-1, valinit=idx_y_init, valstep=1)
        slider_2 = Slider(ax_slider_2, z_axis, 0, len(z_vals)-1, valinit=idx_z_init, valstep=1)
        slider_1.on_changed(lambda val: update_plot(plot_axis, idx_x_init, val, slider_2.val))
        slider_2.on_changed(lambda val: update_plot(plot_axis, idx_x_init, slider_1.val, val))
    elif plot_axis == y_axis:
        slider_1 = Slider(ax_slider_1, x_axis, 0, len(x_vals)-1, valinit=idx_x_init, valstep=1)
        slider_2 = Slider(ax_slider_2, z_axis, 0, len(z_vals)-1, valinit=idx_z_init, valstep=1)
        slider_1.on_changed(lambda val: update_plot(plot_axis, val, idx_y_init, slider_2.val))
        slider_2.on_changed(lambda val: update_plot(plot_axis, slider_1.val, idx_y_init, val))
    elif plot_axis == z_axis:
        slider_1 = Slider(ax_slider_1, x_axis, 0, len(x_vals)-1, valinit=idx_x_init, valstep=1)
        slider_2 = Slider(ax_slider_2, y_axis, 0, len(y_vals)-1, valinit=idx_y_init, valstep=1)
        slider_1.on_changed(lambda val: update_plot(plot_axis, val, slider_2.val, idx_z_init))
        slider_2.on_changed(lambda val: update_plot(plot_axis, slider_1.val, val,idx_z_init))
    else:
        raise ValueError(f"Unbekannter Parametername: {plot_axis}\n verfügbare Parameter:\n x\n y\n z")
    
    update_plot(plot_axis, idx_x_init, idx_y_init, idx_z_init)
    
    # Ploteinstellungen
    if plot_axis == x_axis:
        plt.xlabel(x_axis)
    elif plot_axis == y_axis:
        plt.xlabel(y_axis)
    elif plot_axis == z_axis:
        plt.xlabel(z_axis)
    else:
        raise ValueError(f"Unbekannter Parametername: {plot_axis}\n verfügbare Parameter:\n x\n y\n z")
    
    ax.set_xlabel(plot_axis)
    ax.set_ylabel("Energie")

    if SAVE:
        plt.savefig(f"{DATEIENNAME}.jpg", bbox_inches=BBOX)
        plt.savefig(f"{DATEIENNAME}.png", bbox_inches=BBOX)
        plt.savefig(f"{DATEIENNAME}.pdf", bbox_inches=BBOX)
    if SHOW:
        plt.show()

# Vergleich mit einem QE-Dataframe

def model_2Dplots_xyz(axis: str,
                      energy_value: str,
                      df: list,
                      modeltype: str, 
                      coeffs: list,
                      nk_model: int,
                      orders: list,
                      plot_model: bool = True,
                      symmetry: int = None,
                      error: bool = False,
                      coord_system: str = None,
                      no_a0: bool = False,
                      a_coeffs: list = None,
                      b_coeffs: list = None):
    """
    - verwendet load_model_tNB als Hilfsfunktion
    - verwendet load_model aus qe_model_calc.py als Hilfsfunktion

    - Funktion erstellt 2D-Schnittplots der Energie energy_value entlang der Achse axis
    - mit Slidern kann durch verschiedene Achsen gewechselt werden
    - dabei werden die Orignalenergien (und die Modellkurven, wenn plot_model=True) geplottet
    
    Args:
        axis:           Achse, entland geplottet wird: z.B. "x"
        energy_value:   Energie-Achse (Parametername im Pandas Dataframe)
        df:             Pandas Dataframe
        modeltype:      Parametername des Modells
        coeffs:         Modellkoeffizienten
        nk_model:       Anzahl der Datenpunte der Modellkurve
        orders:         Liste der Ordnungen für das Modell Bsp: [p_order, f_order, l_order, k_order, ...]
        plot_model:     Soll das Modell geplottet werden?
        symmetry:       Grad der Symmetrie
        error:          anstatt der Bänder wird der Fehler zwischen Modell und Energie geplottet
        coord_system:   Koordinatensystem der Daten aus dem Dataframe
        no_a0:          Soll der erste Koeffizient (konstanter Term) im Modell weggelassen werden?
        a_coeffs, b_coeffs:  Koeffizienten des Pfades
    """
    # Daten einlesen:
    if coord_system == "xyz":
        x_axis = "x"
        y_axis = "y"
        z_axis = "z"
    elif coord_system == "path":
        x_axis = "t"
        y_axis = "rho"
        z_axis = "phi"
    else:
        raise ValueError(f"coord_system={coord_system}; Dieses Koordinatensystem existiert nicht!")
    
    x_data = df[f"{x_axis}"]
    y_data = df[f"{y_axis}"]
    z_data = df[f"{z_axis}"]
    
    # Wertebereiche
    x_vals = np.sort(x_data.unique())
    y_vals = np.sort(y_data.unique())
    z_vals = np.sort(z_data.unique())

    # Standart-Idizes
    idx_x_init = int((len(x_vals)-1)/2)
    idx_y_init = int((len(y_vals)-1)/2)
    idx_z_init = int((len(z_vals)-1)/2)

    fig, ax = plt.subplots(figsize=(FIGWIDTH,FIGWIDTH*HFACTOR))
    plt.subplots_adjust(bottom=0.4)  # Platz für Slider
    colors = plt.rcParams['axes.prop_cycle'].by_key()['color'] # Farbenliste

    # leere Linienobjekte
    energy_dots, = ax.plot([], [], ".", color=colors[0])
    #energy_line, = ax.plot([], [], "-", color=colors[0])

    if plot_model:
        #model_energy_dots, = ax.plot([], [], ".", color=colors[1])
        model_energy_line, = ax.plot([], [], "-", color=colors[1])

    # Update-Funktion
    def update_plot(axis, idx_x, idx_y, idx_z):
        x = x_vals[int(idx_x)]
        y = y_vals[int(idx_y)]
        z = z_vals[int(idx_z)]

        # ---- Slider-Texte aktualisieren ----
        if axis == x_axis:
            txt_slider_1.set_text(f"{y_axis} = {y:.3g}")
            txt_slider_2.set_text(f"{z_axis} = {z:.3g}")
            df0 = df[(y_data == y) & (z_data == z)]
            plot_range = x_vals
        elif axis == y_axis:
            txt_slider_1.set_text(f"{x_axis} = {x:.3g}")
            txt_slider_2.set_text(f"{z_axis} = {z:.3g}")
            df0 = df[(x_data == x) & (z_data == z)]
            plot_range = y_vals
        elif axis == z_axis:
            txt_slider_1.set_text(f"{x_axis} = {x:.3g}")
            txt_slider_2.set_text(f"{y_axis} = {y:.3g}")
            df0 = df[(x_data == x) & (y_data == y)]
            plot_range = z_vals
        else:
            raise ValueError("Unbekannte Achse")
        
        if plot_model:
            energy_model = []

        if axis == x_axis:
            df0 = df[(y_data == y) & (z_data == z)]
            if plot_model:
                plot_range = np.linspace(x_vals[0], x_vals[-1], nk_model)
                for x in plot_range:
                    energy = model.load_model(modeltype, orders, x, y, z, symmetry, coeffs, no_a0, a_coeffs, b_coeffs)
                    energy_model.append(energy)

        elif axis == y_axis:
            df0 = df[(x_data == x) & (z_data == z)]
            if plot_model:
                plot_range = np.linspace(y_vals[0], y_vals[-1], nk_model)
                for y in plot_range:
                    energy = model.load_model(modeltype, orders, x, y, z, symmetry, coeffs, no_a0, a_coeffs, b_coeffs)
                    energy_model.append(energy)
                       
        elif axis == z_axis:
            df0 = df[(x_data == x) & (y_data == y)]
            if plot_model:
                plot_range = np.linspace(z_vals[0], z_vals[-1], nk_model)
                for z in plot_range:
                    energy = model.load_model(modeltype, orders, x, y, z, symmetry, coeffs, no_a0, a_coeffs, b_coeffs)
                    energy_model.append(energy)
        
        else:
            raise ValueError(f"Unbekannter Parametername: {axis}\n verfügbare Parameter:\n x\n y\n z")

        # Daten aktualisieren
        if not error:
            energy_dots.set_data(df0[f"{axis}"], df0[f"{energy_value}"])
            #energy_line.set_data(df0[f"{axis}"], df0[f"{energy_value}"])

            if plot_model:
                #model_energy_dots.set_data(plot_range, energy_model)
                model_energy_line.set_data(plot_range, energy_model)

        if error:
            if plot_model:
                energy_dots.set_data(df0[f"{axis}"], df0[f"error_{energy_value}"])
                #energy_line.set_data(df0[f"{axis}"], df0[f"error_{energy_value}"])

        ax.relim()
        if error:
            ax.set_ylim(0, max(df[f"error_{energy_value}"]))
        else:
            ax.autoscale_view()
        fig.canvas.draw_idle()

    # Slider-Achsen erstellen
    ax_slider_1 = plt.axes([0.15, 0.12, 0.4, 0.03])
    ax_slider_2 = plt.axes([0.15, 0.04, 0.4, 0.03])
    # ---- Text neben Slider ----
    txt_slider_1 = ax_slider_1.text(1.2, 0.5, "", transform=ax_slider_1.transAxes, va="center")
    txt_slider_2 = ax_slider_2.text(1.2, 0.5, "", transform=ax_slider_2.transAxes, va="center")

    if axis == x_axis:
        slider_1 = Slider(ax_slider_1, y_axis, 0, len(y_vals)-1, valinit=idx_y_init, valstep=1)
        slider_2 = Slider(ax_slider_2, z_axis, 0, len(z_vals)-1, valinit=idx_z_init, valstep=1)
        slider_1.on_changed(lambda val: update_plot(axis, idx_x_init, val, slider_2.val))
        slider_2.on_changed(lambda val: update_plot(axis, idx_x_init, slider_1.val, val))
    elif axis == y_axis:
        slider_1 = Slider(ax_slider_1, x_axis, 0, len(x_vals)-1, valinit=idx_x_init, valstep=1)
        slider_2 = Slider(ax_slider_2, z_axis, 0, len(z_vals)-1, valinit=idx_z_init, valstep=1)
        slider_1.on_changed(lambda val: update_plot(axis, val, idx_y_init, slider_2.val))
        slider_2.on_changed(lambda val: update_plot(axis, slider_1.val, idx_y_init, val))
    elif axis == z_axis:
        slider_1 = Slider(ax_slider_1, x_axis, 0, len(x_vals)-1, valinit=idx_x_init, valstep=1)
        slider_2 = Slider(ax_slider_2, y_axis, 0, len(y_vals)-1, valinit=idx_y_init, valstep=1)
        slider_1.on_changed(lambda val: update_plot(axis, val, slider_2.val, idx_z_init))
        slider_2.on_changed(lambda val: update_plot(axis, slider_1.val, val,idx_z_init))
    else:
        raise ValueError(f"Unbekannter Parametername: {axis}\n verfügbare Parameter:\n x\n y\n z")
    
    update_plot(axis, idx_x_init, idx_y_init, idx_z_init)
    
    # Ploteinstellungen
    if axis == x_axis:
        if axis == "t":
            ax.set_xlabel(r"$t$")
        else:
            ax.set_xlabel(x_axis)
    elif axis == y_axis:
        if axis == "rho":
            ax.set_xlabel(r"$\rho$")
        else:
            ax.set_xlabel(y_axis)
    elif axis == z_axis:
        if axis == "phi":
            ax.set_xlabel(r"$\phi$")
        else:
            ax.set_xlabel(z_axis)
    else:
        raise ValueError(f"Unbekannter Parametername: {axis}\n verfügbare Parameter:\n x\n y\n z")
      
    # Achsenbeschriftung
    if energy_value == "diff":
        ax.set_ylabel(r"$\Delta E$")
    elif energy_value == "band0":
        ax.set_ylabel(r"$E_0-E_f$")
    elif energy_value == "band1":
        ax.set_ylabel(r"$E_1-E_f$")
    else:
        ax.set_ylabel(energy_value)

    plt.subplots_adjust(left=0.2)
    ax.ticklabel_format(axis="y", style='sci', scilimits=(0,0))
 
    if SAVE:
        plt.savefig(f"{DATEIENNAME}.jpg", bbox_inches=BBOX)
        plt.savefig(f"{DATEIENNAME}.png", bbox_inches=BBOX)
        plt.savefig(f"{DATEIENNAME}.pdf", bbox_inches=BBOX)
    if SHOW:
        plt.show()

def model_4Dplots(k_grid_center: list,
                  energy_model: list):
    """
    - Funktion verwendet plot_cube als Hilfsfunktion

    - Funktion plottet die Daten (x, y, z, E) in einem 3D Koordinatensystem, wobei E als Colorbar dargestellt wird
    - dabei gilt:
        x = axes[0]
        y = axes[1]
        z = axes[2]
        E = axes[3]

    Args:
        p:              Gitterlängen-array bzw. float des Gitters
        df:             Dataframe mit den Daten
        axes:           Welche Achsen sollen verwendet werden?
                        Beispiel: axes = ("x", ""y", "z", "band0")
        title:          Titel der Abbildung
        back:           alle Punkte sind Schwarz
        activate_plot_cube:      Soll ein Würfelgitter um die Daten geplottet werden?
        **args:         zusätzliche Argumente, die ax.scatter() übergeben werden
    """ 
    axis_0 = k_grid_center[:, 0]
    axis_1 = k_grid_center[:, 1]
    axis_2 = k_grid_center[:, 2]
    
    # Erstellung der Abbildung
    fig = plt.figure(figsize=(FIGWIDTH,FIGWIDTH*HFACTOR))
    ax = fig.add_subplot(projection='3d')

    im = ax.scatter(axis_0, axis_1, axis_2, c=energy_model, cmap="gist_heat", **SCATTER_CONFIG)

    # Titel und Achsenbeschriftung
    plt.xlabel(f"x")
    plt.ylabel(f"y")
    ax.set_zlabel(f"z")
    ax.axis("equal")
    
    cbar = fig.colorbar(im, pad=0.15)

    if SAVE:
        plt.savefig(f"{DATEIENNAME}.jpg", bbox_inches=BBOX)
        plt.savefig(f"{DATEIENNAME}.png", bbox_inches=BBOX)
        plt.savefig(f"{DATEIENNAME}.pdf", bbox_inches=BBOX)
    if SHOW:
        plt.show()