import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from scipy.interpolate import griddata

from lib.qe_model_calc import load_model
from lib.qe_model_calc import load_path
from lib.plot_config import FIGWIDTH, HFACTOR, SCATTER_CONFIG, BBOX, DATEIENNAME, SHOW, SAVE, TITEL

# --------------------------------------------------------------------------------------
# 2D - Sliderpolts
# --------------------------------------------------------------------------------------

def load_model_tNB(modeltype, modeltype_path, orders, t, vN, vB, symmetry=None, coeffs=None, no_a0=False, a_coeffs=None, b_coeffs=None):
    """ 
    - Hilfsfunktion für model_2Dplots_xyz
    - nutzt Funktionen load_path und load_model aus qe_model_calc.py

    - berechnet für bestimmte Modelle die Koordinatentransformation {t,vN,vB} --> {t,rho,phi}
    - dann gibt es die entsprechenden Modell-Werte zurück
    """
    if (modeltype == "path_4") or (modeltype == "model_path_abs_1") or (modeltype == "model_path_abs_4"):
        rho = np.sqrt(vN**2 + vB**2)
        phi = np.arctan2(vN, vB)
        A = load_model(modeltype, orders[0], orders[1], orders[2], orders[3], t, rho, phi, symmetry=symmetry, coeffs=coeffs, no_a0=no_a0, a_coeffs=a_coeffs, b_coeffs=b_coeffs)  

    elif modeltype == "regular_2":
        print("HINWEIS: Koordinatentransformation {t,vN,vB} --> {t,rho,phi}")

        if len(a_coeffs) != 4:
            raise ValueError(f"Das Modell funktioniert nur mit einem Polynom-Modell 4. Ordnung ohne konstanten Term! len(a_coeffs)={len(a_coeffs)}")
        if len(b_coeffs) != 4:
            raise ValueError(f"Das Modell funktioniert nur mit einem Polynom-Modell 4. Ordnung ohne konstanten Term! len(b_coeffs)={len(b_coeffs)}")

        r, T, B, N, kappa = load_path(modeltype_path, t, a_coeffs, b_coeffs)
        x = r[:,0] + vN*N[:,0] + vB*B[:,0]
        y = r[:,1] + vN*N[:,1] + vB*B[:,1]
        z = r[:,2] + vN*N[:,2] + vB*B[:,2]
        x = float(x[0])
        y = float(y[0])
        z = float(z[0])

        A = load_model(modeltype, orders[0], orders[1], orders[2], orders[3], x, y, z, symmetry=symmetry, coeffs=coeffs, no_a0=no_a0, a_coeffs=a_coeffs, b_coeffs=b_coeffs)
    else:
        raise ValueError("Modell-Umrechnung für coord_system == 'tNB' wurde für dieses Modell noch nicht hinzugefügt!")
    return A

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
                      modeltype_path: str = None,
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
        modeltype_path: Pfadmodell für Koordinatentransformation {t,vN,vB} --> {t,rho,phi}, wenn coord_system="tNB"
        no_a0:          Soll der erste Koeffizient (konstanter Term) im Modell weggelassen werden?
        a_coeffs, b_coeffs:  Koeffizienten des Pfades
    """
    # Daten einlesen:
    if coord_system == "xyz":
        x_axis = "x"
        y_axis = "y"
        z_axis = "z"
    elif coord_system == "xyz_scaled":
        x_axis = "x_scaled"
        y_axis = "y_scaled"
        z_axis = "z_scaled"
    elif coord_system == "path":
        x_axis = "t"
        y_axis = "rho"
        z_axis = "phi"
    elif coord_system == "tNB":
        x_axis = "t"
        y_axis = "vN"
        z_axis = "vB"
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

        # Slider-Texte aktualisieren
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
                    if coord_system == "tNB":
                        energy = load_model_tNB(modeltype, modeltype_path, orders, x, y, z, symmetry, coeffs, no_a0, a_coeffs, b_coeffs)
                    else:
                        energy = load_model(modeltype, orders, x, y, z, symmetry, coeffs, no_a0, a_coeffs, b_coeffs)
                    energy_model.append(energy)

        elif axis == y_axis:
            df0 = df[(x_data == x) & (z_data == z)]
            if plot_model:
                plot_range = np.linspace(y_vals[0], y_vals[-1], nk_model)
                for y in plot_range:
                    if coord_system == "tNB":
                        energy = load_model_tNB(modeltype, modeltype_path, orders, x, y, z, symmetry, coeffs, no_a0, a_coeffs, b_coeffs)
                    else:
                        energy = load_model(modeltype, orders, x, y, z, symmetry, coeffs, no_a0, a_coeffs, b_coeffs)
                    energy_model.append(energy)
                       
        elif axis == z_axis:
            df0 = df[(x_data == x) & (y_data == y)]
            if plot_model:
                plot_range = np.linspace(z_vals[0], z_vals[-1], nk_model)
                for z in plot_range:
                    if coord_system == "tNB":
                        energy = load_model_tNB(modeltype, modeltype_path, orders, x, y, z, symmetry, coeffs, no_a0, a_coeffs, b_coeffs)
                    else:
                        energy = load_model(modeltype, orders, x, y, z, symmetry, coeffs, no_a0, a_coeffs, b_coeffs)
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
    # Text neben Slider
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

    # wissenschaftliche Notation erzwingen
    ax.ticklabel_format(axis="y", style='sci', scilimits=(0,0)) 

    if SAVE:
        plt.savefig(f"{DATEIENNAME}.jpg", bbox_inches=BBOX)
        plt.savefig(f"{DATEIENNAME}.png", bbox_inches=BBOX)
        plt.savefig(f"{DATEIENNAME}.pdf", bbox_inches=BBOX)

    if SHOW:
        plt.show()

# --------------------------------------------------------------------------------------
# 3D - Sliderpolts
# --------------------------------------------------------------------------------------

def interpolate_to_regular_grid(df, energy, nx=30, ny=30, nz=30, method="nearest"):
    """
    - Hilfsfunktion für model_3Dsurface
    - die Funktion interpoliert unregelmäßige (x, y, z, E)-Daten auf ein regelmäßiges 3D-Gitter
    - die Standartmethode "nearest" ist ungenau, aber schnell
    """
    x_data = df["x"]
    y_data = df["y"]
    z_data = df["z"]
    E_data = df[f"{energy}"]

    x_data = np.asarray(x_data)
    y_data = np.asarray(y_data)
    z_data = np.asarray(z_data)
    E_data = np.asarray(E_data)
    
    # Gitter definieren
    xi = np.linspace(np.min(x_data), np.max(x_data), nx)
    yi = np.linspace(np.min(y_data), np.max(y_data), ny)
    zi = np.linspace(np.min(z_data), np.max(z_data), nz)
    XI, YI, ZI = np.meshgrid(xi, yi, zi, indexing='ij')

    # Interpolation
    points = np.column_stack((x_data, y_data, z_data))
    EI = griddata(points, E_data, (XI, YI, ZI), method=method)

    # In flache Arrays umwandeln
    x_flat = XI.flatten()
    y_flat = YI.flatten()
    z_flat = ZI.flatten()
    E_flat = EI.flatten()

    # Neuen DataFrame mit interpolierten Werten zurückgeben
    df_interp = pd.DataFrame({
        "x": x_flat,
        "y": y_flat,
        "z": z_flat,
        f"{energy}": E_flat
    })

    return df_interp
    
def model_3Dsurface(axis: str,
                    df: list,
                    energy: str,
                    coord_system: str,
                    grid_type: str):
    """
    - Funktion verwendet interpolate_to_regular_grid als Hilfsfunktin

    - Funktion erstellt 3D-Flächenplots der Energie energy in der Ebene senkrecht zu Achse axis
    - mit Slidern kann durch verschiedene Ebenen von axis gewechselt werden
    - bei unregelmäßigen Gittern wird der Plot auf ein regelmäßiges Gitter interpoliert

    Args:
        axis:           Achse mit den Slindern
        df:             Dataframe
        energy:         Parameter-Name der Energie-Achse
        coord_system:   Koordinatensystem der Daten aus dem Dataframe
        grid_type:      Form des Gitters
    """

    if grid_type == "regular":
        # Daten einlesen:
        if coord_system == "xyz":
            x_axis = "x"
            y_axis = "y"
            z_axis = "z"
        elif coord_system == "xyz_scaled":
            x_axis = "x_scaled"
            y_axis = "y_scaled"
            z_axis = "z_scaled"
            axis = axis + "_scaled"
        elif coord_system == "path":
            x_axis = "t"
            y_axis = "rho"
            z_axis = "phi"
        else:
            raise ValueError(f"coord_system={coord_system}; Dieses Koordinatensystem existiert nicht!")
    else:
        df = interpolate_to_regular_grid(df, energy)
        x_axis = "x"
        y_axis = "y"
        z_axis = "z"
        print("Achtung: Plot besteht aus Interpolation des unregelmäßigen Gitters!")

    # Label für Beschriftungen in den Abbildungen
    if energy == "diff":
        e_label = f"$\\Delta E$"
    elif energy == "band0":
        e_label = f"$E_0$"
    elif energy == "band1":
        e_label = f"$E_1$"

    exponenten = {}
    # Datem skalieren
    for ax in [f"{x_axis}", f"{y_axis}", f"{z_axis}", f"{energy}"]:
        ax_max = np.max(np.abs(df[ax]))
        if ax_max > 0:
            exp = int(np.floor(np.log10(ax_max)))
        else:
            exp = 0
        exponenten[ax] = exp
        df[ax] = df[ax] / (10**exp)
    
    print("Gespeicherte Exponenten:", exponenten)
            
    # Daten
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

    # Globale Farbskala bestimmen
    vmin = df[energy].min()
    vmax = df[energy].max()

    # Figur & Achse
    fig = plt.figure(figsize=(FIGWIDTH,FIGWIDTH*HFACTOR))
    ax = fig.add_subplot(111, projection='3d')
    plt.subplots_adjust(bottom=0.25, right=0.8)  # Platz für Slider & Colorbar
    cmap = "gist_heat"

    # Hilfsfunktion: Meshgrid & Werte extrahieren
    def get_slice(axis, idx_x, idx_y, idx_z):
        x = x_vals[int(idx_x)]
        y = y_vals[int(idx_y)]
        z = z_vals[int(idx_z)]

        if axis == x_axis:
            df0 = df[x_data == x]
            Y, Z = np.meshgrid(y_vals, z_vals)
            F = np.zeros_like(Y)
            for i, y in enumerate(y_vals):
                for j, z in enumerate(z_vals):
                    val = df0[(df0[y_axis]==y) & (df0[z_axis]==z)][energy]
                    F[j,i] = val.values[0] if len(val)>0 else np.nan
            return Y, Z, F, f"x = {x:.8f}"

        elif axis == y_axis:
            y = y_vals[int(idx_y)]
            df0 = df[y_data == y]
            X, Z = np.meshgrid(x_vals, z_vals)
            F = np.zeros_like(X)
            for i, x in enumerate(x_vals):
                for j, z in enumerate(z_vals):
                    val = df0[(df0[x_axis]==x) & (df0[z_axis]==z)][energy]
                    F[j,i] = val.values[0] if len(val)>0 else np.nan
            return X, Z, F, f"y = {y:.8f}"

        elif axis == z_axis:
            z = z_vals[int(idx_z)]
            df0 = df[z_data == z]
            X, Y = np.meshgrid(x_vals, y_vals)
            F = np.zeros_like(X)
            for i, x in enumerate(x_vals):
                for j, y in enumerate(y_vals):
                    val = df0[(df0[x_axis]==x) & (df0[y_axis]==y)][energy]
                    F[j,i] = val.values[0] if len(val)>0 else np.nan
            return X, Y, F, f"z = {z:.8f}"

    # Anfangsplot
    X_plot, Y_plot, Z_plot, title = get_slice(axis, idx_x_init, idx_y_init, idx_z_init)
    norm = plt.Normalize(vmin, vmax)
    ax.plot_surface(X_plot, Y_plot, Z_plot, cmap=cmap, norm=norm, edgecolor='none')
    #ax.plot_wireframe(X_plot, Y_plot, Z_plot)
    ax.set_title(title)

    # Colorbar hinzufügen
    #cbar_ax = fig.add_axes([0.75, 0.25, 0.03, 0.5])
    #fig.colorbar(cm.ScalarMappable(norm=norm, cmap=cmap), cax=cbar_ax, label=e_label)

    # Update-Funktion (gemeinsam für alle Achsen)
    def update(val):
        for c in ax.collections:
            c.remove()  # alte Fläche löschen (schneller als ax.clear())
        if axis == x_axis:
            X_plot, Y_plot, Z_plot, title = get_slice(x_axis, slider.val, idx_y_init, idx_z_init)
        elif axis == y_axis:
            X_plot, Y_plot, Z_plot, title = get_slice(y_axis, idx_x_init, slider.val, idx_z_init)
        elif axis == z_axis:
            X_plot, Y_plot, Z_plot, title = get_slice(z_axis, idx_x_init, idx_y_init, slider.val)
        ax.plot_surface(X_plot, Y_plot, Z_plot, cmap=cmap, norm=norm, edgecolor='none')
        #ax.plot_wireframe(X_plot, Y_plot, Z_plot)
        ax.set_title(title)
        fig.canvas.draw_idle()

    # Slider und Achsen definieren
    if axis == x_axis:
        vals = x_vals
        idx = idx_x_init
        label = 'x index'
        ax.set_xlabel(f"{y_axis} ($\\times 10^{{{exponenten['y']}}}$)")
        ax.set_ylabel(f"{z_axis} ($\\times 10^{{{exponenten['z']}}}$)")
    elif axis == y_axis:
        vals = y_vals
        idx = idx_y_init
        label = 'y index'
        ax.set_xlabel(f"{x_axis} ($\\times 10^{{{exponenten['x']}}}$)")
        ax.set_ylabel(f"{z_axis} ($\\times 10^{{{exponenten['z']}}}$)")
    elif axis == z_axis:
        vals = z_vals
        idx = idx_z_init
        label = 'z index'
        ax.set_xlabel(f"{x_axis} ($\\times 10^{{{exponenten['x']}}}$)")
        ax.set_ylabel(f"{y_axis} ($\\times 10^{{{exponenten['y']}}}$)")

    ax.set_zlabel(f"{e_label} ($\\times 10^{{{exponenten[energy]}}}$)")
    ax_slider = plt.axes([0.2, 0.1, 0.6, 0.03])

    slider = Slider(ax_slider, label, 0, len(vals)-1, valinit=idx, valstep=1)
    slider.on_changed(update)

    if SAVE:
        plt.savefig(f"{DATEIENNAME}.jpg", bbox_inches=BBOX)
        plt.savefig(f"{DATEIENNAME}.png", bbox_inches=BBOX)
        plt.savefig(f"{DATEIENNAME}.pdf", bbox_inches=BBOX)

    if SHOW:
        plt.show()

# --------------------------------------------------------------------------------------
# 4D-Plots: Plot in 3D + Farbachse
# --------------------------------------------------------------------------------------

def plot_cube(ax,
              bounds=(-1, 1),
              alpha=0.1,
              face_color='cyan',
              edge_color='k',
              edge_width=1.5,
              edges=True):
    """
    - Hilfsfunktion für model_4Dplots und für path_4Dplots, model_4Dpots_both aus qe_model_path.py
    - zeichnet einen 3D-Würfel mit optional transparenten Flächen und sichtbaren Kanten.

    Args:
        ax:             Achse aus Matplotblib
        bounds:         Grenzen des Würfels in allen drei Dimensionen (Standard: (-1, 1)).
        alpha:          Transparenz der Flächen (0 = durchsichtig, 1 = undurchsichtig).
        face_color:     Farbe der Würfelflächen.
        edge_color:     Farbe der Kanten.
        edge_width:     Linienstärke der Kanten.
        edges:          Sollen die Kanten gezeichnet werden?
    """
    r = [bounds[0], bounds[1]]

    # Ecken
    v = [
        [r[0], r[0], r[0]], [r[1], r[0], r[0]],
        [r[1], r[1], r[0]], [r[0], r[1], r[0]],
        [r[0], r[0], r[1]], [r[1], r[0], r[1]],
        [r[1], r[1], r[1]], [r[0], r[1], r[1]],
    ]

    # Flächen
    faces = [
        [v[0], v[1], v[2], v[3]],
        [v[4], v[5], v[6], v[7]],
        [v[0], v[1], v[5], v[4]],
        [v[2], v[3], v[7], v[6]],
        [v[1], v[2], v[6], v[5]],
        [v[4], v[7], v[3], v[0]],
    ]

    # Flächen (wenn alpha > 0 oder face_color angegeben)
    if alpha > 0:
        cube = Poly3DCollection(
            faces,
            alpha=alpha,
            facecolor=face_color,
            edgecolor='none',  # Kanten separat zeichnen
        )
        ax.add_collection3d(cube)

    # Kanten separat zeichnen:
    if edges:
        edge_indices = [
            (0,1),(1,2),(2,3),(3,0),
            (4,5),(5,6),(6,7),(7,4),
            (0,4),(1,5),(2,6),(3,7)
        ]
        for s, e in edge_indices:
            ax.plot(
                [v[s][0], v[e][0]],
                [v[s][1], v[e][1]],
                [v[s][2], v[e][2]],
                color=edge_color,
                linewidth=edge_width, zorder=10
            )

    return ax

def model_4Dplots(p: list,
                  df: list,
                  axes: list,
                  title: str,
                  black: str = False,
                  activate_plot_cube = False):
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
        plot_cube(ax, bounds=(cube_min,cube_max), alpha=0.0, face_color='cyan', edge_color='black', edge_width=0.5)

    # Plot der Daten
    if black:
        im = ax.scatter(df[f"{axes[0]}"], df[f"{axes[1]}"], df[f"{axes[2]}"], c="black", zorder=1, **SCATTER_CONFIG)
    else:
        im = ax.scatter(df[f"{axes[0]}"], df[f"{axes[1]}"], df[f"{axes[2]}"], c=df[f"{axes[3]}"], cmap="gist_heat", zorder=1, **SCATTER_CONFIG)

    # Titel und Achsenbeschriftung
    if axes[0] == "kx":
        plt.xlabel(f"$k_x$")
    elif axes[0] == "ky":
        plt.xlabel(f"$k_y$")
    elif axes[0] == "kz":
        plt.xlabel(f"$k_z$")
    else:
        plt.xlabel(f"{axes[0]}")

    if axes[1] == "kx":
        plt.ylabel(f"$k_x$")
    elif axes[1] == "ky":
        plt.ylabel(f"$k_y$")
    elif axes[1] == "kz":
        plt.ylabel(f"$k_z$")
    else:
        plt.ylabel(f"{axes[1]}")

    if axes[2] == "kx":
        ax.set_zlabel(f"$k_x$")
    elif axes[2] == "ky":
        ax.set_zlabel(f"$k_y$")
    elif axes[2] == "kz":
        ax.set_zlabel(f"$k_z$")
    else:
        ax.set_zlabel(f"{axes[2]}")

    ax.axis("equal")

    # Colorbar allgemein
    cbar = fig.colorbar(im)

    if TITEL:
        plt.title(f"{title}")   
    if SAVE:
        plt.savefig(f"{DATEIENNAME}.jpg", bbox_inches=BBOX)
        plt.savefig(f"{DATEIENNAME}.png", bbox_inches=BBOX)
        plt.savefig(f"{DATEIENNAME}.pdf", bbox_inches=BBOX)
    if SHOW:
        
        plt.show()

def model_4Dplots_mme_in_thz(p: list,
                             df: list,
                             df_mme: list,
                             axes: list,
                             title: str,
                             merge_decimals = None,
                             activate_plot_cube = False):
    """
    - Funktion verwendet plot_cube als Hilfsfunktion

    - Funktion entnimmt dem Dataframe df die Koordinaten (x1,y1,z1) und dem Dataframe df_mme die Daten (x2,y2,z2,p)
    - Wenn merge_decimals=None, werden die Daten (x2,y2,z2,p) geplottet.
    - Falls merge_decimals!=None, erfolgt eine Zuordnung zwischen (x1,y1,z1) und (x2,y2,z2) -> (x,y,z). Dabei gibt merge_decimals die Nachkommastelle an, auf die beide Dataframes für die Zuordnung gerundet werden. Dann wird (x1,y1,z1) in schwarz und (x,y,z,p) in Rot geplottet.
    
    Args:
        p:              Gitterlängen-array bzw. float des Gitters
        df:             Dataframe mit den Energien
        df_mme:         Dataframe mit den Matrix-Impuls-Elementen
        axes:           Welche Achsen sollen verwendet werden?
                        Beispiel: axes = ("x", ""y", "z", "px")
        title:          Titel der Abbildung
        merge_decimals: aktiviert die Zuordnung der Koordinatensysteme
        activate_plot_cube:      Soll ein Würfelgitter um die Daten geplottet werden?
        **args:         zusätzliche Argumente, die ax.scatter() übergeben werden
    """
    # Falls der Würfelgitter geplottet wird, Festlegung dessen Seitenlängen
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
        plot_cube(ax, bounds=(cube_min,cube_max), alpha=0.0, face_color='cyan', edge_color='black', edge_width=1)

    # Plot der Daten
    if merge_decimals is not None:
        df_merged = pd.merge(df.round(merge_decimals), df_mme.round(merge_decimals), on=['kx', 'ky', "kz"], how='inner')
        ax.scatter(df[f"{axes[0]}"], df[f"{axes[1]}"], df[f"{axes[2]}"], c="black", zorder=1, alpha=0.1, **SCATTER_CONFIG)
        ax.scatter(df_merged[f"{axes[0]}"], df_merged[f"{axes[1]}"], df_merged[f"{axes[2]}"], c="red", zorder=1, **SCATTER_CONFIG)
    else:
        ax.scatter(df[f"{axes[0]}"], df[f"{axes[1]}"], df[f"{axes[2]}"], c="black", zorder=1, alpha=0.1, **SCATTER_CONFIG)
        ax.scatter(df_mme[f"{axes[0]}"], df_mme[f"{axes[1]}"], df_mme[f"{axes[2]}"], c="red", zorder=1, **SCATTER_CONFIG)

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

# --------------------------------------------------------------------------------------
# Gradienten
# --------------------------------------------------------------------------------------

def model_plot_gradient(df: list,
                        axes: list,
                        step: int):
    """
    - Funktion plottet den Gradienten als Pfeil im 3D-Plot
    - dabei wird die Anzahl der Pfeile mit step reduziert:
        
    Args:
        df:             Dataframe mit den Daten
        axes:           Welche Achsen sollen verwendet werden?
                        Beispiel: axes = ("x", ""y", "z", "band0")
        step:           reduziert die Anzahl der Pfeile:
                        step=3 -> jeder ditte Pfeil wird geplottet    
    """
    fig = plt.figure(figsize=(FIGWIDTH,FIGWIDTH*HFACTOR))
    ax = fig.add_subplot(111, projection='3d')

    # Koordinaten aus dem Dataframe
    x = df[axes[0]].to_numpy()
    y = df[axes[1]].to_numpy()
    z = df[axes[2]].to_numpy()

    # Gradient-Komponenten
    dEdx = df[f"dEdx_{axes[3]}"].to_numpy()
    dEdy = df[f"dEdy_{axes[3]}"].to_numpy()
    dEdz = df[f"dEdz_{axes[3]}"].to_numpy()

    ax.quiver(x[::step], y[::step], z[::step], dEdx[::step], dEdy[::step], dEdz[::step], length=0.001, normalize=True, color='r')

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
 
    if SAVE:
        plt.savefig(f"{DATEIENNAME}.jpg", bbox_inches=BBOX)
        plt.savefig(f"{DATEIENNAME}.png", bbox_inches=BBOX)
        plt.savefig(f"{DATEIENNAME}.pdf", bbox_inches=BBOX)
    if SHOW:
        
        plt.show()

# --------------------------------------------------------------------------------------
# Plot der Fehler für verschiedene Ordnungen
# --------------------------------------------------------------------------------------

def model_errors(axis1: str,
                 df: list,
                 energy: str,
                 modeltype: str,
                 max_error:float=None,
                 thz_range:bool=False):
    """
    - Funktion plottet die Fehler in Anhängigkeit der Ordnungen
    Args:
        axis1           Welche Ordnungen werden auf der x-Achse dargestellt?
        df:             Dataframe mit Spalten x,y,t, band0, band1
        energy:         Parameter-Name der Energie-Achse
        modeltype:      Parametername des Modells: linear oder quadratic
        max_error:      Filtert das Dataframe vorher nach error_energy < max_error
        thz_range:      Plot der Fehler im thz-aktiven Bereich       
    """
    # Dataframe filtern
    if max_error is not None:
        df = df.loc[(df[f"error_{energy}"] < max_error)]

    # Abbildung erstellen
    fig = plt.figure(figsize=(FIGWIDTH,FIGWIDTH*HFACTOR))
    x_data = df[f"{axis1}"]
    y_data = df[f"error_{energy}"]

    # Abbildung plotten
    plt.plot(x_data, y_data, ".", color="red")

    if axis1 == "len_coeffs":
        plt.axhline(1e-4, color="blue", label=f"{1e-4} eV")

    # Achsenbeschriftung
    if energy == "diff":
        plt.ylabel(r"$ |\Delta E_\text{model} - \Delta E_\text{QE} |$")
    elif energy == "band0":
        plt.ylabel(r"$ |E_{0,\text{model}} - E_{0,\text{QE}} |$")
    elif energy == "band1":
        plt.ylabel(r"$ |E_{1,\text{model}} - E_{1,\text{QE}} |$")
    else:
        plt.ylabel(f"error_{energy}")

    if axis1 == "len_coeffs":
        plt.xlabel(f"Anzahl der Koeffizienten")
    else:
        plt.xlabel(f"{axis1}")
    
    # Globales Minimum berechnen
    globalminimums = float(np.min(np.array(df[f"error_{energy}"])))
    print("globale Minima:")
    print(df.loc[df[f"error_{energy}"] == globalminimums])

    # Legende definieren
    #plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.legend()  
    
    plt.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))
    if TITEL:
        plt.title(f"Fehler - {energy}\nModell: {modeltype}, thz_range={thz_range}\nglobales Minimum={globalminimums}") 
    if SAVE:
        plt.savefig(f"{DATEIENNAME}.jpg", bbox_inches=BBOX)
        plt.savefig(f"{DATEIENNAME}.png", bbox_inches=BBOX)
        plt.savefig(f"{DATEIENNAME}.pdf", bbox_inches=BBOX)
    if SHOW:
        plt.show()
       
def model_errors_3D(axis1: str,
                    axis2: str,
                    df: list,
                    energy: str,
                    modeltype: str,
                    max_error: float=None,
                    thz_range: float=False):
    """
    - Funktion plottet die Punkte (axis1, axis2, energy) als 3D-Flächenplot
    Args:
        axis1           Welche Ordnungen werden auf der x-Achse dargestellt?
        axis2           Welche Ordnungen werden auf der y-Achse dargestellt?
        df:             Dataframe mit Spalten x,y,t, band0, band1
        energy:         Parameter-Name der Energie-Achse
        modeltype:      Parametername des Modells: linear oder quadratic
        max_error:      Filtert das Dataframe vorher nach error_energy < max_error
        thz_range:      Plot der Fehler im thz-aktiven Bereich
    """
    # Dataframe filtern
    if max_error is not None:
        df = df.loc[(df[f"error_{energy}"] < max_error)]

    # 2D-Gitter erzeugen:
    x_data = df[f"{axis1}"]
    y_data = df[f"{axis2}"]
    x_data_unique = np.unique(x_data)
    y_data_unique = np.unique(y_data)
    X, Y = np.meshgrid(x_data_unique, y_data_unique)

    # E-Werte auf eine 2D-Matrix bringen
    # Die letzten E-Werte werden hier zurückgegeben.
    z_data = df[f"error_{energy}"]
    Z = np.zeros_like(X, dtype=float) #leeres Gitter
    for xi, yi, Ei in zip(x_data, y_data, z_data):
        ix = np.where(x_data_unique == xi)[0][0]
        iy = np.where(y_data_unique == yi)[0][0]
        Z[iy, ix] = Ei

    # Plot als wireframe
    ax = plt.figure(figsize=(FIGWIDTH,FIGWIDTH*HFACTOR)).add_subplot(projection='3d')
    ax.plot_wireframe(X, Y, Z, color='C0')

    # Globales Minimum berechnen 
    globalminimums = float(np.min(np.array(df[f"error_{energy}"])))
    print("globale Minima:")
    print(df.loc[df[f"error_{energy}"] == globalminimums])

    # Achsenbeschriftung
    ax.set_xlabel(axis1)
    ax.set_ylabel(axis2)
    ax.set_zlabel(energy)
    #ax.set_position([0, 0, 0.9, 1])

    # Legende
    #plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.legend()

    if TITEL:
        plt.title(f"Fehler - {energy}\nModell: {modeltype}, thz_range={thz_range}\nglobales Minimum={globalminimums}")
    if SAVE:
        plt.savefig(f"{DATEIENNAME}.jpg", bbox_inches=BBOX)
        plt.savefig(f"{DATEIENNAME}.png", bbox_inches=BBOX)
        plt.savefig(f"{DATEIENNAME}.pdf", bbox_inches=BBOX)
    if SHOW:
        plt.show()
