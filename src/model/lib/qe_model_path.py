import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import lib.qe_model_pathmodels as pathmodels
import lib.qe_model_plot as plot
from lib.plot_config import FIGWIDTH, HFACTOR, SCATTER_CONFIG, BBOX, DATEIENNAME, SHOW, SAVE, TITEL

# ######################################################################################
# Definition des Gitters
# ######################################################################################

# --------------------------------------------------------------------------------------
# Richtiges Gitter laden
# --------------------------------------------------------------------------------------

def load_grid_for_fit(point, model_axis, df, delta_path1, n_grid_path1, x_order, y_order, z_order, coeffs, no_a0, k0, decimals: int=12):
    """
    - Hilfsfunktion: lädt die richtige Funktion zur Berechnung des Gitters für Quantum Espresso (je nach Punkt)
    """
    if point == "punkt1":
        k_grid, k_grid_center, coords = path_grid_point1(point, model_axis, df, delta_path1, n_grid_path1, x_order, y_order, z_order, coeffs, no_a0, k0, decimals=decimals)
        t_grid = None
    elif point == "punkt2":
        k_grid, k_grid_center, coords, t_grid = path_grid_point2(point, model_axis, df, delta_path1, n_grid_path1, x_order, y_order, z_order, coeffs, no_a0, k0, decimals=decimals)
    else:
        raise ValueError(f"Falscher Parameter für den Punkt: {point}")
        
    return k_grid, k_grid_center, coords, t_grid

# --------------------------------------------------------------------------------------
# Gitter für Punkt 1 und Punkt 2
# --------------------------------------------------------------------------------------

def path_grid_point1(point: str,
                     model_axis: str,
                     df: list,
                     delta: float,
                     n_grid: list,
                     x_order: int,
                     y_order: int,
                     z_order: int,
                     coeffs: list,
                     no_a0: bool,
                     k0: list,
                     decimals: int=12):
    """
    - verwendet von Funkton load_grid_for_fit
    - verwendet Funktion load_curve_model

    - funktioniert nur, wenn der Pfad nach der x-Achse parametrisisert wird
    - Funktion definiert ein Gitter aus in x- und y-Richtung verschobenen Pfaden
    Args:
        point:              Punkt in der BZ: "punkt1"
        model_axis:         Achse, entlang das Minimum der Energie bestimmt wird       
        df:                 das Pandas Dataframe
        delta:              Gittergrenzen in y und z-Richtung des neuen Gitters
        n_grid:             Anzahl der Datenpunkte in (x,y,z)-Richtung
        x_order:            Ordnung in x-Richtung
        y_order:            Ordnung in y-Richtung
        z_order:            Ordnung in z-Richtung
        coeffs:             Modellkoeffizieten der Pfadfunktion als array
        no_a0:              Soll der erste Koeffizient (konstanter Term) entfernt werden?
        k0:                 Verschiebungsvektor auf Schnittpunkt der Bänder
        decimals:           legt fest, auf wie viele Nachkommastellen die Pfadvektoren gerundet werden, standart:12
    Return:
        k_grid:         Vektoren des k-Gitters {kx_ky_kz}
        k_grid_center:  Vektoren des Gitters im Koordinatenursprung {x,y,z}
        coords:         Liste der kpoints Koordinaten für Quantum Espresso
    """
    print()
    print(f"----> Neues Gitter")

    if point != "punkt1":
        raise ValueError("ACHTUNG: Die Funktion path_grid_punkt1 funktioniert nur, mit Modell point=punkt1 ! ")

    if not (n_grid[1] % 2 != 0) and (n_grid[2] % 2 != 0):
        raise ValueError("WICHTIG: Anzahl der Datenpunkte in y- und z-Richtung muss ungerade sein!")

    vals = df[f"{model_axis}"].unique()
    x_min = np.min(vals)
    x_max = np.max(vals)

    x_range = np.linspace(x_min, x_max, n_grid[0])
    xyz = load_curve_model(point, x_order, y_order, z_order, x_range, coeffs, no_a0=no_a0)

    x = xyz[0]
    y = xyz[1]
    z = xyz[2]

    # Verschiebung in y und z
    shift_y = np.linspace(-delta, delta, n_grid[1])
    shift_z = np.linspace(-delta, delta, n_grid[2])

    # Kombinationen der Verschiebung
    paths = []
    for sy in shift_y:
        for sz in shift_z:
            y_shifted = y + sy
            z_shifted = z + sz
            path = np.column_stack((x,y_shifted, z_shifted))
            paths.append(path)

    # Alle Pfade zusammenfassen
    k_grid_center = np.vstack(paths)
    k_grid = k_grid_center + np.array(k0)

    coords = []
    for k in k_grid:
        kvec = np.round(k, decimals)
        c = str(kvec[0])+" "+str(kvec[1])+" "+str(kvec[2])+" "+str(1.0)
        coords.append(c)
    
    print(f"----> mittlere Gitterabstände | Anzahl der Datenpunkte")
    print(f"----> mittlerer Gitterabstand in x-Richtung: {np.mean(np.abs(np.diff(x_range)))} | N_x={len(x_range)}")
    if len(shift_y) > 1:
        print(f"----> mittlerer Gitterabstand in y-Richtung: {np.mean(np.abs(np.diff(shift_y)))} | N_y={len(shift_y)}")
    if len(shift_z) > 1:
        print(f"----> mittlerer Gitterabstand in z-Richtung: {np.mean(np.abs(np.diff(shift_z)))} | N_z={len(shift_z)}")
    #print(f"----> Gitter in t-Richtung:\n{t_lin}")
    #print(f"----> Gitter in rho-Richtung:\n{vN_lin}")
    #print(f"----> Gitter in phi-Richtung:\n{(180/np.pi)*vB_lin}")
    print(f"----> Anzahl der k-Punkte: {len(k_grid)}")

    return k_grid, k_grid_center, coords

def path_grid_point2(point: str,
                     model_axis: str,
                     df: list,
                     delta: float,
                     n_grid: list,
                     x_order: int,
                     y_order: int,
                     z_order: int,
                     coeffs: list,
                     no_a0: bool,
                     k0: list,
                     decimals: int=12):
    """
    - verwendet von Funkton load_grid_for_fit
    - verwendet Funktion load_curve_model

    - funktioniert nur, wenn die Energie nach t gefittet wird, wobei t = Wert in Pfad entlang der 111-Achse
    - Funktion definiert ein Gitter aus in N- und B-Richtung verschobenen Pfaden
    Args:
        point:              Punkt in der BZ: "punkt2"
        model_axis:         Achse, entlang das Minimum der Energie bestimmt wird       
        df:                 das Pandas Dataframe
        delta:              Gittergrenzen in y und z-Richtung des neuen Gitters
        n_grid:             Anzahl der Datenpunkte in (x,y,z)-Richtung
        x_order:            Ordnung in x-Richtung
        y_order:            Ordnung in y-Richtung
        z_order:            Ordnung in z-Richtung
        coeffs:             Modellkoeffizieten der Pfadfunktion als array
        no_a0:              Soll der erste Koeffizient (konstanter Term) entfernt werden?
        k0:                 Verschiebungsvektor auf Schnittpunkt der Bänder
        decimals:           legt fest, auf wie viele Nachkommastellen die Pfadvektoren gerundet werden, standart:12
    Return:
        k_grid:         {kx,ky,kz} = Gitter für Quantum Espresso
        k_grid_center:  {x,y,z} = Gitter im Zentrum, egal welche Art des Gitter-Typs
        coords:         Liste der kpoints Koordinaten für Quantum Espresso
        t_grid:         {t,rho,phi} = Gitter für Polarkoordinaten entlang des Pfades
    """
    print()
    print(f"----> Neues Gitter")

    if point != "punkt2":
        raise ValueError("ACHTUNG: Die Funktion path_grid_punkt2 funktioniert nur, mit point=punkt2 ")

    if not (n_grid[1] % 2 != 0) and (n_grid[2] % 2 != 0):
        raise ValueError("WICHTIG: Anzahl der Datenpunkte in y- und z-Richtung muss ungerade sein!")
    
    vals = df[f"{model_axis}"].unique() # t-Wert in Vektor (t,t,t) entlang der (111)-Richtung
    t_min = np.min(vals) # t_min
    t_max = np.max(vals) # t_max

    t_lin = np.linspace(t_min, t_max, n_grid[0]) # Einteilung in t
    if n_grid[1] > 1:
        vN_lin = np.linspace(-delta, delta, n_grid[1])
    else:
        vN_lin = [0]
        print(f"----> vN_lin={vN_lin}")
    if n_grid[2] > 1:
        vB_lin = np.linspace(-delta, delta, n_grid[2])
    else:
        vB_lin = [0]
        print(f"----> vB_lin={vB_lin}")

    # Laden der Kurve
    r = load_curve_model(point, x_order, y_order, z_order, t_lin, coeffs, no_a0=no_a0)
    r = np.array(r).T
    # Berechnung von N und B
    B = np.array([1.0, 1.0, -2.0])
    B = B / np.linalg.norm(B) # Normierung
    B = np.tile(B, (len(t_lin), 1))   # shape (n, 3)
    # Tangentenvekor liegt in 111-Richtung; Normalenvektor N=BxT:
    N = np.array([1.0, -1.0, 0.0])
    N = N / np.linalg.norm(N)
    N = np.tile(N, (len(t_lin), 1))   # shape (n, 3)

    # Kombinationen der Verschiebung
    k_grid = []
    k_grid_center = []
    t_grid = []

    for i in range(len(t_lin)):
        # Fügt (111)-Achse hinzu)
        #k_grid_center.append(np.array([t_lin[i],t_lin[i],t_lin[i]]))
        #k_grid.append(np.array([t_lin[i],t_lin[i],t_lin[i]])+k0)
        #t_grid_center.append(np.array([t_lin[i], 0, 0]))
        for vN in vN_lin:
            for vB in vB_lin:
                x = r[i,0] + vN*N[i,0] + vB*B[i,0]
                y = r[i,1] + vN*N[i,1] + vB*B[i,1]
                z = r[i,2] + vN*N[i,2] + vB*B[i,2]
                rho = np.sqrt(vN**2 + vB**2)
                phi = np.arctan2(vN, vB)
                k_grid_center.append(np.array([x,y,z]))
                k_grid.append(np.array([x,y,z])+k0)
                t_grid.append(np.array([t_lin[i], rho, phi]))

    k_grid = np.vstack(k_grid)
    k_grid_center = np.vstack(k_grid_center)
    t_grid = np.vstack(t_grid)
    print(f"----> mittlere Gitterabstände | Anzahl der Datenpunkte")
    print(f"----> mittlerer Gitterabstand in t-Richtung: {np.mean(np.abs(np.diff(t_lin)))} | N_t={len(t_lin)}")
    if len(vN_lin) > 1:
        print(f"----> mittlerer Gitterabstand in vN-Richtung: {np.mean(np.abs(np.diff(vN_lin)))} | N_vN={len(vN_lin)}")
    if len(vB_lin) > 1:
        print(f"----> mittlerer Gitterabstand in vB-Richtung: {np.mean(np.abs(np.diff(vB_lin)))} | N_vB={len(vB_lin)}")
    #print(f"----> Gitter in t-Richtung:\n{t_lin}")
    #print(f"----> Gitter in rho-Richtung:\n{vN_lin}")
    #print(f"----> Gitter in phi-Richtung:\n{(180/np.pi)*vB_lin}")
    print(f"----> Anzahl der k-Punkte: {len(k_grid)}")

    coords = []
    for k in k_grid:
        kvec = np.round(k, decimals)
        c = str(kvec[0])+" "+str(kvec[1])+" "+str(kvec[2])+" "+str(1.0) # 1.0: gleichmäßige Gewichtung in QE
        coords.append(c)

    return k_grid, k_grid_center, coords, t_grid


# ######################################################################################
# Fit entlang des Minimums des Gitters
# ######################################################################################

# --------------------------------------------------------------------------------------
# Zuschnitt der Daten auf das Minimum
# --------------------------------------------------------------------------------------

def load_cut_df_to_min(point, df, model_axis, model_energy, filter_intersection, filter_tol, cut_energy):
    """
    - Hilfsfunktion: lädt die richtige Funktion zum Zuschneiden des Dataframes kurz vor dem Fit
    """
    if point == "punkt1":
        df_mins = path_cut_df_to_min_point1(df, model_axis, model_energy)
    elif point == "punkt2":
        df_mins = path_cut_df_to_min_point2(df, model_axis, model_energy, filter_intersection=filter_intersection, filter_tol=filter_tol, cut_energy=cut_energy)
    else:
        raise(ValueError(f"Noch keine Filterung des Dataframes {model_energy}({model_axis}) für point={point} definiert."))
    
    return df_mins

# --------------------------------------------------------------------------------------
# Funktionen für Punkt 1 und Punkt 2
# --------------------------------------------------------------------------------------

def path_cut_df_to_min_point1(df: list,
                              model_axis: str,
                              model_energy: str):
    """
    - verwendet von Funktion load_cut_df_to_min

    - Funktion schneidet das Pandas Dataframe auf die Minima entlang der Achse axis zu
    Args:
        df:             Pandas Dataframe
        model_axis:     Achse, entlang das Minimum der Energie bestimmt wird
        model_energy:   Energie-Achse, nach der das Dataframe gefilert wird
    Return:
        df_mins:    Pandas Dataframe mit den Minima
    """
    vals = df[f"{model_axis}"].unique()
    df_list = []
    for i in vals:
        dfi = df[(df[f"{model_axis}"] == i)]
        dfi_min = dfi[dfi[f"{model_energy}"] == min(np.array(dfi[f"{model_energy}"]))]
        df_list.append(dfi_min)
    df_mins = pd.concat(df_list, ignore_index=True)
    return df_mins

def path_cut_df_to_min_point2(df: list,
                              model_axis: str,
                              model_energy: str,
                              filter_intersection: bool,
                              filter_tol: float = 1e-6,
                              cut_energy: float = None):
    """
    - verwendet von Funktion load_cut_df_to_min
    
    - Funktion filtert die (111)-Richtung heraus und schneidet das Dataframe auf die globalen Minima der Achse axis zu
    - Die Parameter filter_intersection und filter_tol steuern den Vergleich der Koordinaten in (111)-Richtung
    Args:
        df:                     Pandas Dataframe
        model_axis:             Achse, entlang das Minimum der Energie bestimmt wird
        model_energy:           Energie-Achse, nach der das Dataframe gefilert wird
        filter_intersection:    Soll der Bereich in der Nähe (111)-Richtung herausgeschnitten werden? (nicht nur die Daten exakt in (111)-Richtung)
        filter_tol:             numerische Toleranz für den Vergleich in (111)-Richtung
        cut_energy:             Filtert die Energien auf kleiner als cut_energy
    Return:
        df_mins:    Pandas Dataframe mit den Minima
    """
    vals = df[f"{model_axis}"].unique()
    mask = (np.isclose(df["x"], df["y"], atol=filter_tol) & np.isclose(df["y"], df["z"], atol=filter_tol))
    M = df.loc[mask, "t"].unique()

    # (optional) Entfernung des Schnittbereichs aus 2A und 2B
    if filter_intersection:
        df = df.loc[~df["t"].isin(M)]

    # Energien in (111)-Richtung
    df_111 = df.loc[((df["x"] == df["y"]) &(df["y"] == df["z"]))]
    print(f"maximale Banddifferenz in (111-Richtung): {float(np.max(df_111["diff"]))}")

    # Entfernen der exakten (111)-Richtung
    df = df.loc[~((df["x"] == df["y"]) &(df["y"] == df["z"]))]

    df_list = []
    for i in vals:
        dfi = df[(df[f"{model_axis}"] == i)].copy()

        # Energie-Filter
        if cut_energy is not None:
            dfi = dfi[dfi[f"{model_energy}"] < cut_energy]

        if dfi.empty:
            continue # Leere Gruppen überspringen.
        # Globales Minimum
        global_min_idx = np.argmin(dfi[f"{model_energy}"].values)
        dfi_min = dfi.iloc[[global_min_idx]]
        df_list.append(dfi_min)

    df_mins = pd.concat(df_list, ignore_index=True)
    return df_mins

# --------------------------------------------------------------------------------------
# Design_Matrizen des Modells laden
# --------------------------------------------------------------------------------------

def load_curve_model(point, x_order, y_order, z_order, x_model, coeffs=None, no_a0=False):
    """
    - verwendet Funktonen aus qe_model_pathmodels.py

    - lädt die Designmatrix (oder Modell-Werte) für verschiedene Funktionen
    """
    if point == "punkt1":
        A = pathmodels.path_point1(y_order, z_order, x_model, coeffs=coeffs, no_a0=no_a0)
    elif point == "punkt2":
        A = pathmodels.path_point2(x_order, y_order, z_order, x_model, coeffs=coeffs, no_a0=no_a0)
    else:
        raise ValueError(f"Für Funktion load_curve_model: point={point} existiert nicht!")
    return A

# --------------------------------------------------------------------------------------
# Berechnung des Modells (FIT)
# --------------------------------------------------------------------------------------

def path_solve_LS(df: list,
                  point: str,
                  model_axis: str,
                  x_order: int = None,
                  y_order: int = None,
                  z_order: int = None,
                  coord_system: str = None,
                  no_a0: bool = False):
    """
    - verwendet Funktion load_curve_model

    - Funktion hat einen ähnlichen Aufbau wie model_solve_LS aus qe_model_calc.py
    - Funktion berechnet den Pfad entlang der Minima der Energie

    Args:
        df:             das Pandas Dataframe mit den Minima durch path_cut_df_to_min
        point:          Punkt in der BZ. z.B. "punkt1" - bestimmt die Funktion für den Fit
        model_axis:     Achse, nach der der Pfad parametrisiert ist
                    Punkt 1: "x"
                    Punkt 2: "t"
        x_order:        Ordnung in x-Richtung des Pfadmodells
        y_order:        Ordnung in y-Richtung des Pfadmodells
        z_order:        Ordnung in z-Richtung des Pfadmodells
        coord_system:   Koordinatensystem, in dem der Fit durchgeführt wird
        no_a0:          Soll in den Polynommodellen die 0-te Ordnung weggelassen werden?
    Return:
        coeffs_copy:        Modellkoeffizieten der Pfadfunktion als array:
                            Beispiel:   r(x,y,z) = (x, ax+bx**2, cx+cx**2)
                                        coeffs_copy = [None, [a, b], [c, d]]
    """
    # Wahl des Koordinatensystems
    if coord_system == "xyz":
        x = np.array(df["x"])
        y = np.array(df["y"])
        z = np.array(df["z"])
    elif coord_system == "xyz_scaled":
        x = np.array(df["x_scaled"])
        y = np.array(df["y_scaled"])
        z = np.array(df["z_scaled"])
    elif coord_system == "path":
        x = np.array(df["t"])
        y = np.array(df["rho"])
        z = np.array(df["phi"])
    else:
        raise ValueError(f"coord_system={coord_system}; Dieses Koordinatensystem existiert nicht!")

    x_model = np.array(df[f"{model_axis}"])

    # Laden der Design-Matrizen
    b_list = (x,y,z)
    A_list = load_curve_model(point, x_order, y_order, z_order, x_model, no_a0=no_a0)

    # Lösung der linearen Gleichungssysteme
    coeffs = [None, None, None]
    for i in (0,1,2):
        A = A_list[i]
        b = b_list[i]
        if A is not None:
            coeffs[i], *_ = np.linalg.lstsq(A, b, rcond=None)
    
    coeffs_copy = coeffs.copy()
    
    if coeffs[0] is not None:
        len_0 = len(coeffs[0])
    else: len_0 = 0
    if coeffs[1] is not None:
        len_1 = len(coeffs[1])
    else: len_1 = 0
    if coeffs[2] is not None:
        len_2 = len(coeffs[2])
    else: len_2 = 0
    print(f"----Anzahl der Koeffizienten: {len_0}, {len_1}, {len_2}")
    #print(f"Koeffizienten:\n  {coeffs[0]}\n  {coeffs[1]}\n  {coeffs[2]}")

    return coeffs_copy

# --------------------------------------------------------------------------------------
# Dataframe aus den Modellkoeffizieten
# --------------------------------------------------------------------------------------

def coeffs_to_df(coeffs: list,
                 x_order: int,
                 y_order: int,
                 z_order: int):
    """
    - Funktion erstellt ein Pandas Dataframe aus den Modellkoeffizieten und Indizes
    Args:
        coeffs:     Modellkoeffizieten der Pfadfunktion als array
        x_order:    Ordnung in x-Richtung
        y_order:    Ordnung in y-Richtung
        z_order:    Ordnung in z-Richtung
    Return:
        df_coeffs:         Pandas Dataframe mit den Modellkoeffizienten und Indizes
    """
    orders = np.array([x_order, y_order, z_order], dtype=object)
    orders = np.where(orders == None, np.nan, orders)
    max_orders = np.nanmax(orders)

    def conv_array(arr, target_len):
        """
        - Hilfsfunktion zum ersetzen von None->NaN und auffüllen der arrays
        """
        if arr is None: # None oder []
            arr = []
        else:
            arr = list(arr)
        
        for _ in range((target_len - len(arr))+1):
            arr.insert(0, np.nan)
        return np.array(arr, dtype=float)
    
    coeffs_ = []
    for arr in coeffs:
        coeffs_.append(conv_array(arr, max_orders))
    d_coeffs = {"coeffs_x":coeffs_[0], "coeffs_y":coeffs_[1], "coeffs_z":coeffs_[2]}
    df_coeffs = pd.DataFrame(d_coeffs)
    
    return df_coeffs

# ######################################################################################
# Plots
# ######################################################################################

def path_4Dplots(p: list,
                 df: list,
                 axes: list,
                 title: str,
                 black: str = False,
                 activate_plot_cube = False,
                 path: list = None):
    """
    - Funktion verwendet plot_cube aus qe_model_plot.py als Hilfsfunktion

    - Modifikation der Funktion model_4Dplots aus qe_model_plot.py
    - Funktion plottete die Daten des Dataframes und den zugehörigen Pfad, falls path nicht None
    - dabei gilt:
        x = axes[0]
        y = axes[1]
        z = axes[2]
        E = axes[3]

    Args:
        p:                  halbe Kantenlängen des Gitters im Zentrum: [x_max, y_max, z_max]
        df:                 das Pandas Dataframe
        axes:               Welche Achsen sollen verwendet werden?
                            Beispiel: axes = ("x", ""y", "z", "diff")
        title:              Titel der Abbildung
        black:              alle Punkte sind Schwarz
        activate_plot_cube: Soll ein Würfelgitter um die Daten geplottet werden?
        path:               Soll der Pfad geplottet werten? None oder Koordinaten des Pfades als array
    """
    # Falls das Würfelgitter geplottet wird, Festlegung dessen Seitenlängen
    pmax = np.max(p)
    if axes[0] == "x_scaled":
        cube_min = -1
        cube_max = 1
    else:
        cube_min = -pmax
        cube_max = pmax

    # Erstellung der Abbildung
    fig = plt.figure(figsize=(FIGWIDTH,FIGWIDTH*HFACTOR))
    ax = fig.add_subplot(projection='3d')

    # Plot des Würfelgitters
    if activate_plot_cube:
        plot.plot_cube(ax, bounds=(cube_min,cube_max), alpha=0.0, face_color='cyan', edge_color='black', edge_width=0.5)

    # Plot der Daten
    if black:
        im = ax.scatter(df[f"{axes[0]}"], df[f"{axes[1]}"], df[f"{axes[2]}"], c="black", zorder=1, **SCATTER_CONFIG)
    else:
        im = ax.scatter(df[f"{axes[0]}"], df[f"{axes[1]}"], df[f"{axes[2]}"], c=df[f"{axes[3]}"], cmap="gist_heat", zorder=1, **SCATTER_CONFIG)

    # Plot des Pfades
    if path is not None:
        x_data = path[0]
        y_data = path[1]
        z_data = path[2]
        # ax.scatter(x_data, y_data, z_data, **SCATTER_CONFIG)
        ax.plot(x_data, y_data, z_data, zorder=10)
    
    # Titel und Achsenbeschriftung  
    plt.xlabel(f"{axes[0]}")
    plt.ylabel(f"{axes[1]}")
    ax.set_zlabel(f"{axes[2]}")
    
    # Colorbar hinzufügen
    #cbar_ax = fig.add_axes([1, 0.14, 0.03, 0.58])
    #fig.colorbar(im, cax=cbar_ax)
    fig.colorbar(im)

    #ax.set_axis_off()
    #ax.set_box_aspect((1, 1, 1.3)) 
    ax.axis("equal")
    
    if TITEL:
        plt.title(f"{title}")   
    if SAVE:
        plt.savefig(f"{DATEIENNAME}.jpg", bbox_inches=BBOX)
        plt.savefig(f"{DATEIENNAME}.png", bbox_inches=BBOX)
        plt.savefig(f"{DATEIENNAME}.pdf", bbox_inches=BBOX)
    if SHOW:
        #fig.canvas.manager.window.showMaximized()
        plt.show()

def path_4Dplots_both(p: list,
                      df_0: list,
                      df_1: list,
                      axes: list,
                      title: str,
                      activate_plot_cube = True,
                      path_0: list = None,
                      path_1: list = None):
    """
    - Funktion verwendet plot_cube aus qe_model_plot.py als Hilfsfunktion
    
    - Modifikation der Funktion model_4Dplots aus qe_model_plot.py
    - Funktion plottet die Pfade verschiedener loops
    - Loop1: df_0, path_0
    - Loop2: df_1, path_1
    - dabei gilt:
        x = axes[0]
        y = axes[1]
        z = axes[2]
        E = axes[3]

    Args:
        p:                  halbe Kantenlängen des Gitters im Zentrum: [x_max, y_max, z_max]
        df_0:               das Pandas Dataframe des ersten Pfades
        df_1:               Pandas Dataframe des zweiten Pfades
        axes:               Welche Achsen sollen verwendet werden?
                            Beispiel: axes = ("x", ""y", "z", "band0")
        title:              Titel der Abbildung
        activate_plot_cube: Soll ein Würfelgitter um die Daten geplottet werden?
        path_0:             erster Pfad als array
        path_1:             zweiter Pfad als array
    """
    # Falls das Würfelgitter geplottet wird, Festlegung dessen Seitenlängen
    pmax = np.max(p)
    if axes[0] == "x_scaled":
        cube_min = -1
        cube_max = 1
    else:
        cube_min = -pmax
        cube_max = pmax

    # Erstellung der Abbildung
    fig = plt.figure(figsize=(FIGWIDTH,FIGWIDTH*HFACTOR))
    ax = fig.add_subplot(projection='3d')

    # Plot des Würfelgitters
    if activate_plot_cube:
        plot.plot_cube(ax, bounds=(cube_min,cube_max), alpha=0.0, face_color='cyan', edge_color='black', edge_width=1)
    
    # Plot der Daten als rote und blaue Punkte
    ax.scatter(df_0[f"{axes[0]}"], df_0[f"{axes[1]}"], df_0[f"{axes[2]}"], color="red", zorder=1, alpha=0.5, **SCATTER_CONFIG)
    ax.scatter(df_1[f"{axes[0]}"], df_1[f"{axes[1]}"], df_1[f"{axes[2]}"], color="blue", zorder=1, alpha=0.5, **SCATTER_CONFIG)
    
    # Plot der Pfade als rote und blaue Punkte
    if path_0 is not None:
        x_data = path_0[0]
        y_data = path_0[1]
        z_data = path_0[2]
        ax.scatter(x_data, y_data, z_data, color="red", zorder=10, **SCATTER_CONFIG)
    
    if path_1 is not None:
        x_data = path_1[0]
        y_data = path_1[1]
        z_data = path_1[2]
        ax.scatter(x_data, y_data, z_data, color="blue", zorder=10, **SCATTER_CONFIG)
    
    # Achsenbeschriftung 
    ax.set(xlabel=f"{axes[0]}", ylabel=f"{axes[1]}", zlabel=f"{axes[2]}")  

    ax.axis("equal")

    if TITEL:
        plt.title(f"{title}")   
    if SAVE:
        plt.savefig(f"{DATEIENNAME}.jpg", bbox_inches=BBOX)
        plt.savefig(f"{DATEIENNAME}.png", bbox_inches=BBOX)
        plt.savefig(f"{DATEIENNAME}.pdf", bbox_inches=BBOX)
    if SHOW:
        plt.show()

def plot_path_kgrid(k_grid: list,
                    df: list,
                    title: str,
                    alpha: float=0.1):
    """
    - Einfacher Plot des Gitters k_grid zusammen mit den Punkten aus dem Dataframe
    - Aus dem Dataframe wird immer die Differenz der Bänder geplottet
    Args:
        k_grid:     das zu plottende neue Gitter
        df:         Pandas Dataframe
        title:      Titel der Abbildung
        alpha:      Transparenz der Gitterpunkte aus dem Dataframe
    """
    # Erstellung der Abbildung
    fig = plt.figure(figsize=[FIGWIDTH,FIGWIDTH*HFACTOR])
    ax = fig.add_subplot(projection='3d')
    
    # Plot der Daten
    #ax.scatter(df[f"kx"], df[f"ky"], df[f"kz"], c=df[f"diff"], s=50, cmap="gist_heat", zorder=1, alpha=alpha)
    ax.scatter(df[f"x"], df[f"y"], df[f"z"], c="black", zorder=1, alpha=alpha, **SCATTER_CONFIG)
    ax.scatter(k_grid[:, 0], k_grid[:, 1], k_grid[:, 2], zorder=10, **SCATTER_CONFIG)

    # Titel und Achsenbeschriftung
    plt.xlabel("x")
    plt.ylabel("y")
    ax.set_zlabel("z")
    
    #ax.set_axis_off()
    plt.axis('equal')

    if TITEL:
        plt.title(f"{title}")   
    if SAVE:
        plt.savefig(f"{DATEIENNAME}.jpg", bbox_inches=BBOX)
        plt.savefig(f"{DATEIENNAME}.png", bbox_inches=BBOX)
        plt.savefig(f"{DATEIENNAME}.pdf", bbox_inches=BBOX)
    if SHOW:
        #fig.canvas.manager.window.showMaximized()
        plt.show()

# ######################################################################################
# finale Analyse
# ######################################################################################

def path_final_analysis_point1(df: list,
                               cut_value_diff: float,
                               cut_value_bands: float,
                               plot_data: bool = False):
    """
    - Analyse-Funktion speziell für Punkt 1:
        - Energien des THz-aktiven Bereichs
        - Grenzen des THz-aktiven Bereichs
        - Intervall des um den Faktor 3/2 vergrößerten THz-Bereichs
        - optionaler Plot der Intervalle entlang des Pfades
    Args:
        df:                 Pandas Dataframe
        cut_value_diff:     Energie in eV, auf der die Differenz der Bänder zugeschnitten wird
        cut_value_bands:    Energie in eV, auf der die Bänder zugeschnitten werden
        plot_data:          Plot der Intervalle entlang des Pfades
    Return:
        df_thz_32:          Dataframe des 3/2-THz-aktiven Bereichs
    """

    df_thz_32 = None

    # Energien des THz-aktiven Bereichs
    print("----------------------------------------------------------------\n")
    print(f"Definition des THz-Aktiven Bereichs: diff<{cut_value_diff}, band1<{cut_value_bands}, band0>{-cut_value_bands}")

    df_area = df.loc[(df["diff"] < cut_value_diff) & (df["band1"] < cut_value_bands) & (df["band0"] > -cut_value_bands)]

    print(f"maximale Energie der Banddifferenz im THz-aktiven Bereich:\n{np.max(df_area["diff"])} eV")
    print(f"maximale Energie der Banddifferenz im Gesamten-Dataframe:\n{np.max(df["diff"])} eV")

    # Grenzen des THz-aktiven Bereichs
    print("----------------------------------------------------------------\n")
    print("Grenzen des THz-aktiven Bereichs")
    x_min, x_max = np.min(df_area["x"]), np.max(df_area["x"])
    print(f"x_min, x_max: {x_min}, {x_max}")
    
    # Intervall *3/2 des THz-aktiven Bereichs
    x_array = df["x"].to_numpy()
    x_min32, x_max32 = x_min*3/2, x_max*3/2
    t1_indizes = np.where( x_array > x_max32)[0]
    t2_indizes = np.where( x_array > x_min32)[0]

    if len(t1_indizes > 0) and len(t2_indizes > 0):
        t1_index = np.where( x_array > x_max32)[0][0]
        t2_index = np.where( x_array > x_min32)[0][0]
        if t1_index < t2_index:
            df_thz_32 = df.iloc[t1_index:t2_index]
        else:
            df_thz_32 = df.iloc[t2_index:t1_index]
        print(f"maximale Energie der Banddifferenz im *3/2-Intervall des THz-Bereichs:")
        print(f"Anzahl der Datenpunkte: {len(df_thz_32)}")
        print(f"x*3/2-Intervall: {float(np.min(df_thz_32["x"])), float(np.max(df_thz_32["x"]))}")
        print(f"maximale Energie der Banddifferenz: {np.max(df_thz_32["diff"])} eV")
        print(f"zur Konrolle (x): {float(x_min32), float(x_max32)}")
        print()
    else:
        t1_index = None
        t2_index = None
        df_thz_32 = None

    if plot_data:
        # Plot der Daten
        if df_thz_32 is None:
            print("Plot ist nicht für die Berechnung im THz-Bereich*3/2 gedacht")
        else:
            fig = plt.figure(figsize=(FIGWIDTH,FIGWIDTH*HFACTOR))
            ax = fig.add_subplot(projection='3d')

            df_black = df[~df.index.isin(df_thz_32.index)]
            df_orange = df_thz_32[~df_thz_32.index.isin(df_area.index)]

            ax.scatter(df_black["x"], df_black["y"], df_black["z"], c="black", zorder=1, **SCATTER_CONFIG)
            ax.scatter(df_area["x"], df_area["y"], df_area["z"], c="red", label=f"THz-aktiver Bereich", **SCATTER_CONFIG)
            ax.scatter(df_orange["x"], df_orange["y"], df_orange["z"], c="orange", label=f"3/2-Intervall um den THz-aktiven Bereich", **SCATTER_CONFIG)

            # Titel und Achsenbeschriftung  
            plt.xlabel("x")
            plt.ylabel("y")
            ax.set_zlabel("z")
            plt.legend()
            
            ax.set_axis_off()   
            ax.axis("equal")

            if SAVE:
                plt.savefig(f"{DATEIENNAME}.jpg", bbox_inches=BBOX)
                plt.savefig(f"{DATEIENNAME}.png", bbox_inches=BBOX)
                plt.savefig(f"{DATEIENNAME}.pdf", bbox_inches=BBOX)
            if SHOW:
                #fig.canvas.manager.window.showMaximized()
                plt.show()

    return df_thz_32, None

def path_final_analysis_point2(df: list,
                               cut_value_diff: float,
                               cut_value_bands: float,
                               plot_data: bool = False):
    """
    - Funktion analysiert das Dataframe df von Punkt 2:
        - Schnittpunkt von Punkt 2A und 2B
        - Energien des THz-aktiven Bereichs
        - Grenzen des THz-aktiven Bereichs aus Sicht von Pfad 2A
        - Intervall *3/2 des THz-aktiven Bereichs
        - Definition des neuen THz-Gitters
        - Intervall *3/2 am Schnittpunkt 2A und 2B
        - optionaler Plot der Intervalle entlang des Pfades
    Args:
        df:                 Pandas Dataframe
        cut_value_diff:     Energie in eV, auf der die Differenz der Bänder zugeschnitten wird
        cut_value_bands:    Energie in eV, auf der die Bänder zugeschnitten werden
        plot_data:          Plot der Intervalle entlang des Pfades 
    Return:
        df_thz_32:          Dataframe des 3/2-THz-aktiven Bereichs
        p:                  Definitionsarray des neuen THz-Gitters    
    """
    df_thz_32, p = None, None
    # Schnittpunkt von 2A und 2B:
    t_array = df["t"].to_numpy()
    x_array = df["x"].to_numpy()
    y_array = df["y"].to_numpy()
    z_array = df["z"].to_numpy()
    rho_array = np.sqrt( (t_array-x_array)**2 + (t_array-y_array)**2 + (t_array-z_array)**2 )
    rho_index = np.where(rho_array==np.min(rho_array))[0]
    df_2AB = df.iloc[rho_index]
    if len(df_2AB) >= 1:
        print("----------------------------------------------------------------\n")
        print("Eintrag des Dataframes bei dem am ehesten gilt: x=y=z (Schnittpunkt von Punkt 2A und 2B)")
        print(f"(x, y, z) = {df_2AB["x"].iloc[0].item(), df_2AB["y"].iloc[0].item(), df_2AB["z"].iloc[0].item()}")
        print(f"(kx, ky, kz) = {df_2AB["kx"].iloc[0].item(), df_2AB["ky"].iloc[0].item(), df_2AB["kz"].iloc[0].item()}")
        print(f"(t,rho,phi) = {df_2AB["t"].iloc[0].item(), df_2AB["rho"].iloc[0].item(), df_2AB["phi"].iloc[0].item()}")
        print(f"diff = {df_2AB["diff"].iloc[0].item()} eV")
        print(f"band0 = {df_2AB["band0"].iloc[0].item()} eV")
        print(f"band1 = {df_2AB["band1"].iloc[0].item()} eV")

    # Energien des THz-aktiven Bereichs
    print("----------------------------------------------------------------\n")
    print(f"Definition des THz-Aktiven Bereichs: diff<{cut_value_diff}, band1<{cut_value_bands}, band0>{-cut_value_bands}")

    df_area = df.loc[(df["diff"] < cut_value_diff) & (df["band1"] < cut_value_bands) & (df["band0"] > -cut_value_bands)]

    print(f"maximale Energie der Banddifferenz im THz-aktiven Bereich:\n{np.max(df_area["diff"])} eV")
    print(f"maximale Energie der Banddifferenz im Gesamten-Dataframe:\n{np.max(df["diff"])} eV")

    # Grenzen des THz-aktiven Bereichs
    print("----------------------------------------------------------------\n")
    print("Grenzen des THz-aktiven Bereichs aus Sicht von Pfad 2A")
    
    t_min, t_max = np.min(df_area["t"]), np.max(df_area["t"])
    print(f"t_min, t_max: {t_min}, {t_max}")

    x_min, x_max = np.min(df_area["x"]), np.max(df_area["x"])
    y_min, y_max = np.min(df_area["y"]), np.max(df_area["y"])
    z_min, z_max = np.min(df_area["z"]), np.max(df_area["z"])
    rho_max = np.sqrt( (t_max-x_max)**2 + (t_max-y_max)**2 + (t_max-z_max)**2 )
    rho_min = np.sqrt( (t_min-x_min)**2 + (t_min-y_min)**2 + (t_min-z_min)**2 )
    print(f"rho_min, rho_max: {rho_min}, {rho_max}")
    
    
    # Intervall *3/2 des THz-aktiven Bereichs
    
    t_min32, t_max32 = t_min*3/2, t_max*3/2
    t1_indizes = np.where( t_array > t_max32)[0]
    t2_indizes = np.where( t_array > t_min32)[0]

    if len(t1_indizes > 0) and len(t2_indizes > 0):
        t1_index = np.where( t_array > t_max32)[0][0]
        t2_index = np.where( t_array > t_min32)[0][0]
        if t1_index < t2_index:
            df_thz_32 = df.iloc[t1_index:t2_index]
        else:
            df_thz_32 = df.iloc[t2_index:t1_index]
        print(f"maximale Energie der Banddifferenz im *3/2-Intervall des THz-Bereichs:")
        print(f"Anzahl der Datenpunkte: {len(df_thz_32)}")
        print(f"t*3/2-Intervall: {float(np.min(df_thz_32["t"])), float(np.max(df_thz_32["t"]))}")
        print(f"maximale Energie der Banddifferenz: {np.max(df_thz_32["diff"])} eV")
        print(f"zur Konrolle (t): {float(t_min32), float(t_max32)}")
        print()
    else:
        t1_index = None
        t2_index = None
        df_thz_32 = None

    # Definition des neuen THz-Gitters
    p0 = np.max([t_min32, t_max32])
    p0 = np.round(p0,2)

    rho_min32, rho_max32 = rho_min*3/2, rho_max*3/2
    p1 = np.max([rho_min32, rho_max32])
    p1 = np.round(p1,2)
    p=(p0, p1, 0)
    print(f"Gitter des THz-Aktiven Bereichs*3/2:\n p={float(p0), float(p1), 0}")

    # Intervall *3/2 am Schnittpunkt 2A und 2B
    if len(df_2AB) >= 1:
        t_2AB = df_2AB["t"].iloc[0].item() # t-Wert des Schnittpunktes
        dt = np.abs(t_2AB*3/2)-np.abs(t_2AB)
        t1_index = np.where( t_array > t_2AB+dt)[0][0] # der Erste Index, deshalb immer >
        t2_index = np.where( t_array > t_2AB-dt)[0][0]
        if t1_index < t2_index:
            df_2AB_32 = df.iloc[t1_index:t2_index]
        else:
            df_2AB_32 = df.iloc[t2_index:t1_index]
        print("----------------------------------------------------------------\n")
        print(f"*3/2-Intervall um den Schnittpunkt von 2A und 2B:")
        print(f"Anzahl der Datenpunkte: {len(df_2AB_32)}")
        print(f"t*3/2-Intervall: {float(np.min(df_2AB_32["t"])), float(np.max(df_2AB_32["t"]))}")
        print(f"maximale Energie der Banddifferenz: {np.max(df_2AB_32["diff"])} eV")
        print(f"zur Konrolle (t): {float(t_array[t1_index]), float(t_array[t2_index])}")
        print()

    if plot_data:
        # Plot der Daten
        if df_thz_32 is None:
            print("Plot ist nicht für die Berechnung im THz-Bereich*3/2 gedacht")
        else:
            fig = plt.figure(figsize=(FIGWIDTH,FIGWIDTH*HFACTOR))
            ax = fig.add_subplot(projection='3d')

            df_black = df[~df.index.isin(df_2AB_32.index)]
            df_black = df_black[~df_black.index.isin(df_thz_32.index)]
            df_orange = df_thz_32[~df_thz_32.index.isin(df_area.index)]
            df_blue = df_2AB_32[~df_2AB_32.index.isin(df_2AB.index)]

            ax.scatter(df_black["x"], df_black["y"], df_black["z"], c="black", zorder=1, **SCATTER_CONFIG)
            ax.scatter(df_blue["x"], df_blue["y"], df_blue["z"], c="#0099FF",label=f"$\\frac{3}{2}$-Intervall (Überlapp 2A \& 2B)", **SCATTER_CONFIG)
            ax.scatter(df_area["x"], df_area["y"], df_area["z"], c="red", label=f"THz-aktiver Bereich", **SCATTER_CONFIG)
            ax.scatter(df_orange["x"], df_orange["y"], df_orange["z"], c="orange", label=f"$\\frac{3}{2}$-Intervall um THz-Bereich", **SCATTER_CONFIG)
            ax.scatter(df_2AB["x"], df_2AB["y"], df_2AB["z"], c="green", label="Überlapppunkt 2A \& 2B", **SCATTER_CONFIG)

            # Titel und Achsenbeschriftung  
            plt.xlabel("x")
            plt.ylabel("y")
            ax.set_zlabel("z")
            plt.legend(bbox_to_anchor=(0.77, 0.812),  bbox_transform=fig.transFigure)
            
            #ax.set_axis_off()  
            ax.axis("equal")

            if SAVE:
                plt.savefig(f"{DATEIENNAME}.jpg", bbox_inches=BBOX)
                plt.savefig(f"{DATEIENNAME}.png", bbox_inches=BBOX)
                plt.savefig(f"{DATEIENNAME}.pdf", bbox_inches=BBOX)
            if SHOW:
                #fig.canvas.manager.window.showMaximized()
                plt.show()

    return df_thz_32, p

def calc_point_2A_2B(coeffs_0: list,
                     point: str,
                     x_order_0: int,
                     y_order_0: int,
                     z_order_0: int,
                     no_a0_0: bool,
                     k0: list,
                     plot_data: bool = False):
    """
    - Funktion zur numerischen Berechnung des Schnittpunktes von 2A und 2B
    Args:
        coeffs_0:   Modellkoeffizieten der Pfadfunktion als array
        point:      Punkt in der BZ. z.B. "punkt1"
        x_order_0:  Ordnung in x-Richtung des Pfadmodells
        y_order_0:  Ordnung in y-Richtung des Pfadmodells
        z_order_0:  Ordnung in z-Richtung des Pfadmodells
        no_a0_0:    Soll in den Polynommodellen die 0-te Ordnung weggelassen werden?
        k0:         Versatzvektors für das Gitter im Koordinatenursprung
        plot_data:  Plot der Raumkurven 2A und 2B
    """
    
    def r_point2(t):
        t = np.atleast_1d(t).astype(float)
        r = np.stack([t, t, t], axis=-1)
        return r

    def r_point2B(t, a, phi, N, B):
        a0, a1, a2, a3, a4, a5, a6, a7 = a[0], a[1], a[2], a[3], a[4], a[5], a[6], a[7]
        t = np.atleast_1d(t).astype(float)
        phi = np.atleast_1d(phi).astype(float)

        delta = a0 + a1*t + a2*t**2 + a3*t**3 + a4*t**4 + a5*t**5 + a6*t**6 + a7*t**7 - t

        rho = np.sqrt(6) * delta
        #print(np.shape(rho))
        #print(np.shape(t))
        #print(np.shape(N.T[0]))
        #print(np.shape(B.T[0]))

        rx = t + rho*np.sin(phi)*N.T[0] + rho*np.cos(phi)*B.T[0]
        ry = t + rho*np.sin(phi)*N.T[1] + rho*np.cos(phi)*B.T[1]
        rz = t + rho*np.sin(phi)*N.T[2] + rho*np.cos(phi)*B.T[2]

        return np.stack([rx, ry, rz], axis=-1)
    
    def path_point2B(t_lin, a_coeffs, phi):
         # Pfad und Frenetsches Dreibei
        B = np.array([1.0, 1.0, -2.0])
        B = B / np.linalg.norm(B) # Normierung
        B = np.tile(B, (len(t_lin), 1))   # shape (n, 3)
        # Tangentenvekor liegt in 111-Richtung; Normalenvektor N=BxT:
        N = np.array([1.0, -1.0, 0.0])
        N = N / np.linalg.norm(N)
        N = np.tile(N, (len(t_lin), 1))   # shape (n, 3)
        r = r_point2B(t_lin, a_coeffs, phi, N, B)
        return r

    # Punkt 2B
    t_max = 0.04
    t_lin = np.linspace(-t_max, t_max, 100)
    
    r1 = path_point2B(t_lin, coeffs_0[0], 0)
    r2 = path_point2B(t_lin, coeffs_0[0], (np.pi/180)*120)
    r3 = path_point2B(t_lin, coeffs_0[0], (np.pi/180)*240)
    r2A = r_point2(t_lin)
    r2B = load_curve_model(point, x_order_0, y_order_0, z_order_0, t_lin, coeffs_0, no_a0=no_a0_0)


    # Numerische Lösung
    def solve(a, k0):
        # Koeffizienten in umgekehrter Reihenfolge
        coeffs = np.array(a)[::-1].astype(float)
        a0, a1, a2, a3, a4, a5, a6, a7 = a[0], a[1], a[2], a[3], a[4], a[5], a[6], a[7]
        # Wichtig: Der Koeffizient für den t-Term ist (a1 - 1)
        coeffs[-2] -= 1
        koeffizienten = [a7, a6, a5, a4, a3, a2, (a1 - 1), a0]
        # Nullstellen berechnen
        loesungen = np.roots(koeffizienten)
        # Relle Lösungen
        reelle_loesungen = loesungen[np.isreal(loesungen)].real
        print("----------------------------------------------------------------\n")
        print("Schnittpunkt von Punkt 2A und 2B")
        print(f"\nAnzahl der Koeffizieten: {len(a)}")
        print("Numerische Lösungen des Schnittpunktes von Punkt 2A und 2B:")
        print("Reelle Lösungen für t:", reelle_loesungen)
        k_lösung = reelle_loesungen + k0[0]
        print("Reelle Lösungen für kx=ky=kz:", k_lösung)

    solve(coeffs_0[0], k0)

    if plot_data:
        fig = plt.figure(figsize=(FIGWIDTH,FIGWIDTH*HFACTOR))
        ax = fig.add_subplot(projection='3d')
        ax.scatter(r2A.T[0], r2A.T[1], r2A.T[2], **SCATTER_CONFIG)
        ax.scatter(r2B[0], r2B[1], r2B[2], **SCATTER_CONFIG)
        ax.scatter(r1.T[0], r1.T[1], r1.T[2], **SCATTER_CONFIG)
        ax.scatter(r2.T[0], r2.T[1], r2.T[2], **SCATTER_CONFIG)
        ax.scatter(r3.T[0], r3.T[1], r3.T[2], **SCATTER_CONFIG)
        ax.set(xlabel=f"x", ylabel=f"y", zlabel=f"z")
        ax.axis("equal")
        ax.set_axis_off()

        if SAVE:
            plt.savefig(f"{DATEIENNAME}.jpg", bbox_inches=BBOX)
            plt.savefig(f"{DATEIENNAME}.png", bbox_inches=BBOX)
            plt.savefig(f"{DATEIENNAME}.pdf", bbox_inches=BBOX)
        if SHOW:
            #fig.canvas.manager.window.showMaximized()
            plt.show()