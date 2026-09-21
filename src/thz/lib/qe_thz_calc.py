import re
import shutil
import os
import os.path
import subprocess
import time
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.pyplot as plt
import pandas as pd
from scipy.signal import find_peaks
import xml.etree.ElementTree as ET
from BoltzTraP2 import units
# --------------------------------------------------------------------------------------
import lib.config as config
from lib.plot_config import FIGWIDTH, HFACTOR, BBOX, DATEIENNAME, SHOW, SAVE


# ######################################################################################
# Definition der Pfade
# ######################################################################################

def calc_coords(u: list,
                R: float,
                a: list,
                r: float,
                v: list,
                phi_steps: int,
                nks: int,
                minangle: float=0,
                maxangle: float=360,
                decimals: int = 12):
    """
    - Definiert lineare Pfade in einer Ebene orthogal zu einem Einheitsvektor u
    
        Anfangsvektor = R*u + v + r*a
    
    - weitere Pfade werden durch Drehung des Anfangsvektors in der Ebene orthogonal zum Einheitsvektor u berechnet
    - u und a müssen orthogonal sein

    Args:
        u:          (ux,uy,uz) - Einheitsvektor der Ursprungsgerade, um die gedreht wird
        R:          Radius für den Einheitsvektor u
        a:          (ax, ay, az) - Einheitsvektor für Anfangspfad, der orthogonal zu u liegt
        r:          Radius für den Einheitsvektor a
        v:          (vx, vy, vz) - Verschiebevektor für den Anfangspfad
        phi_steps:  Anzahl der Zwischenpfade zwischen 0° und 180°
        nks:        Anzahl der Datenpunkte pro Pfad
        minangle:   in deg, minimaler Winkel der Berechnungen (für den Plot)
        maxangle:   in deg, maximaler Winkel der Berechnungen (für den Plot)
        decimals:   legt fest, auf wie viele Nachkommastellen die Pfadvektoren gerundet werden, standart:12

    Return:
        vecs:       Liste der Anfangs und Endvektoren pro Pfad [[a1, a2], [b1, b2], ...]
        coords:     Liste der kpoints Coordinaten für Quantum Espresso (QE)
        uvec:       Vektor R*u als numpy-Array
        vvec:       Vektor v als numpy-Array
        phi_lin:    Winkel der Pfade als numpy-Array
    """
    # prüfe, ob u und a Einheitsvektoren und orthogonal zueinander sind
    if not np.isclose(np.linalg.norm(u),1):
        raise ValueError(f"Einheitsvektor u hat nicht die Länge 1: |{u}| = {np.linalg.norm(u)}")
    if not np.isclose(np.linalg.norm(a), 1):
        raise ValueError(f"Einheitsvektor a hat nicht die Länge 1: |{a}| = {np.linalg.norm(a)}")
    if not np.isclose(np.dot(a, u), 0):
        raise ValueError(f"a und u sind nicht orthogonal: <{a},{u}> = {np.dot(a, u)}")
    
    # Definition wichtiger Größen
    qe_nks = nks-1 # Bei nks=500 erstellt QE 501 Datenpunkte. Deshlab wird hier um 1 verringert.
    avec = np.multiply(np.array(a), r)
    uvec = np.multiply(np.array(u), R)
    vvec = np.array(v)

   # allgemeine Drehmatrix 
    def Rmat(u, alpha):
        """
        - Drehmatrix für Drehung um Ursprungsgerade, die durch den Einheitsvektor u=(x,y,z) definiert ist
        """
        x = u[0]
        y = u[1]
        z = u[2]
        return [[(1-np.cos(alpha))*x*x+np.cos(alpha)  , (1-np.cos(alpha))*y*x-np.sin(alpha)*z, (1-np.cos(alpha))*z*x+np.sin(alpha)*y],
                [(1-np.cos(alpha))*x*y+np.sin(alpha)*z, (1-np.cos(alpha))*y*y+np.cos(alpha)  , (1-np.cos(alpha))*z*y-np.sin(alpha)*x],
                [(1-np.cos(alpha))*x*z-np.sin(alpha)*y, (1-np.cos(alpha))*y*z+np.sin(alpha)*x, (1-np.cos(alpha))*z*z+np.cos(alpha)]]
    
    # Winkel-Einteillung
    phi_lin = np.linspace(0, 2*np.pi, phi_steps, endpoint=False)
    phi0_index = np.abs(phi_lin - minangle*np.pi/180).argmin() # Index des minimalen Winkels
    phi1_index = np.abs(phi_lin - maxangle*np.pi/180).argmin() # Index des maximalen Winkels
    phi_lin = phi_lin[phi0_index : phi1_index+1] # Slicing

    # Berechne alle Pfade: cvec=Anfang des Pfades, dvec=Ende des Pfades; c,d: Strings für QE
    cvec = uvec + vvec
    c = str(cvec[0])+" "+str(cvec[1])+" "+str(cvec[2])+" "+str(qe_nks)
    vecs = []
    coords = []
    for phi in phi_lin:
        dvec = np.round(Rmat(u, phi) @ avec + uvec + vvec, decimals)
        d = str(dvec[0])+" "+str(dvec[1])+" "+str(dvec[2])+" "+str(qe_nks)
        vecs.append([cvec, dvec])
        coords.append([c, d])
   
    return vecs, coords, uvec, vvec, phi_lin

# ######################################################################################
# Plot der Pfade
# ######################################################################################

def plot_cube(ax,
              bounds=(-1, 1),
              alpha=0.1,
              face_color='cyan',
              edge_color='k',
              edge_width=1.5,
              edges=True):
    """
    Zeichnet einen 3D-Würfel mit optional transparenten Flächen und sichtbaren Kanten.

    Args:
        ax:             Achse aus Matplotblib
        bounds:         Grenzen des Würfels in allen drei Dimensionen (Standard: (-1, 1)).
        alpha:          Transparenz der Flächen (0 = durchsichtig, 1 = undurchsichtig).
        face_color:     Farbe der Würfelflächen.
        edge_color:     Farbe der Kanten.
        edge_width:     Linienstärke der Kanten.
        edges:          Sollen die Kanten gezeichnet werden?
    Return:
        ax:             Achse aus Matplotblib
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

def plot_coords(uvec: list,
                vvec: list,
                vecs: list):
    """
    - verwendet Funktion plot_cube als Hilfsfunktion
    - Funktion zum plotten der Pfade
    Args:
        vecs:       Liste der Anfangs und Endvektoren pro Pfad [[a1, a2], [b1, b2], ...]
        uvec:       Vektor R*u als numpy-Array
        vvec:       Vektor v als numpy-Array
    """
    fig = plt.figure(figsize=(FIGWIDTH,FIGWIDTH*HFACTOR))
    ax = fig.add_subplot(projection='3d')

    # Ursprungsvektor
    ax.plot([0,uvec[0]], [0,uvec[1]], [0,uvec[2]], "o", color="black")
    ax.plot([0,uvec[0]], [0,uvec[1]], [0,uvec[2]], "-", color="red")

    # Verschiebevektor
    ax.plot([uvec[0]+vvec[0]], [uvec[1]+vvec[1]], [uvec[2]+vvec[2]], "o", color="black")
    ax.plot([uvec[0],uvec[0]+vvec[0]], [uvec[1],uvec[1]+vvec[1]], [uvec[2],uvec[2]+vvec[2]], "-", color="green")

    # Würfel
    plot_cube(ax, bounds=(-0.5, 0.5), alpha=0.0, face_color='cyan', edge_color='black', edge_width=0.5)

    # Anfangspfad
    array = vecs[0]
    x_data = [array[0][0], array[1][0]]
    y_data = [array[0][1], array[1][1]]
    z_data = [array[0][2], array[1][2]]
    ax.plot(x_data, y_data, z_data, "o", color="blue")
    ax.plot(x_data, y_data, z_data, "-", color="blue")

    # gedrehte Pfade
    for array in vecs[1:]:
        x_data = [array[0][0], array[1][0]]
        y_data = [array[0][1], array[1][1]]
        z_data = [array[0][2], array[1][2]]
        ax.plot(x_data, y_data, z_data, "o", color="black")
        ax.plot(x_data, y_data, z_data, "-", color="black")
    
    plt.xlabel(r"$k_{x}$")
    plt.ylabel(r"$k_{y}$")
    ax.set_zlabel(r"$k_{z}$")
    
    #plt.axis('off') 
    ax.set_box_aspect((1, 1, 1))
    ax.set_xlim(-0.5, 0.5)
    ax.set_ylim(-0.5, 0.5)
    ax.set_zlim(-0.5, 0.5)

    if SAVE:
        plt.savefig(f"{DATEIENNAME}.jpg", bbox_inches=BBOX)
        plt.savefig(f"{DATEIENNAME}.png", bbox_inches=BBOX)
        plt.savefig(f"{DATEIENNAME}.pdf", bbox_inches=BBOX)
    if SHOW:
        #fig.canvas.manager.window.showMaximized()
        plt.show()

# ######################################################################################
# Berechnung der Pfade
# ######################################################################################

def change_config_kpoints(path_in: str,
                          new_values: list,
                          card: str = "K_POINTS {crystal_b}"):
    """
    - Modifikation der Funktion change_config_card aus nitiB2_conv, speziell für die THz-Untersuchung
    - verändert den Wert eines card-Parameters auf einen neuen Wert und speichert die neue in-Datei

    Args:
        path_in:    Pfad der in-Datei von QE
        new_value:  Liste der neuen Parameter (Pfad der K-Punkte)
                    z.B. [[0.5, 0], [-0.5, 0]]
        card:       card-Parameter
                    Hier:  "K_POINTS {crystal_b}"
    """
    filename = path_in.split("/")[-1]
    file = open(path_in, "r")
    file_lines = file.readlines()
    file.close()

    new_lines = []
    continue_again = False
    for i in range(len(file_lines)):
        if re.search(card, file_lines[i]):
            new_lines.append(file_lines[i])
            new_lines.append(" "+str(len(new_values))+"\n")
            #print(">"+" "+str(len(new_values)))
            for line in new_values:
                new_line = " "+str(line)+"\n"
                new_lines.append(new_line)
                #print(">"+" "+str(line))
            continue_again = True
            continue
        if continue_again == True:
            continue
        new_lines.append(file_lines[i])

    tmp_file_path = os.path.join(config.path_tmp(), filename)
    new_file = open(tmp_file_path, 'w')
    for line in new_lines:
        new_file.write(line)
    new_file.close()
    shutil.copyfile(tmp_file_path, path_in)


def thz_calc(coords: list,
             R: float,
             r: float,
             phi_steps: int,
             nks: int,
             datlabel: str,
             enable_logging: bool = True):
    """
    - verwendet die Funktion change_config_kpoints als Hilfsfunktion, um die QE-Input-Datei zu ändern

    Schritte:
    1. scf-Rechnung wird durchgeführt, falls der Ordner bt2_working_directory noch nicht existiert
    2. Inhalt des tmp-Ordners wird in den Ordner path_COPY_directory kopiert
    3. Ändere k-points in bands.in Datei 
    4. bands-Rechnung von pw.x wird durchgeführt
    5. Kopiere bt2_working_directory nach path_tmp_directory_i
    6. Kopieren qe_working_directory nach path_out_directory_i
    7. leere Ordner bt2_working_directory
    8. kopiere scf-Dateien von path_COPY_directory nach bt2_working_directory

    Args:
        coords:     Liste der kpoints Coordinaten für Quantum Espresso (QE)
        R:          Radius für den Einheitsvektor u
        r:          Radius für den Einheitsvektor a
        phi_steps:  Anzahl der Zwischenpfade zwischen 0° und 180°
        nks:        Anzahl der Datenpunkte pro Pfad
        datlabel:   extra Label in Dateienname, um Rechnungen gezielt zu unterscheiden
        enable_logging:    Sollen das log und die print-Ausgabe für die Rechenzeiten aktiv sein?
    """
    suffix = config.suffix(datlabel, nks, phi_steps, R, r)
    bt2_working_directory = config.bt2_working_directory
    qe_working_directory = config.qe_working_directory
    path_scf_in = config.path_scf_in()
    path_scf_out = config.path_scf_out()
    path_bands_in = config.path_bands_in()
    path_bands_out = config.path_bands_out()
    path_COPY_directory = config.path_COPY_directory()
    path_log = config.path_log()

    # log Funktion
    start_time = None
    log_file = None
    def log(message, log_file):
        """ Zur Erstellung des Log """
        nonlocal start_time
        if enable_logging and start_time is not None:
            elapsed = time.time() - start_time
            full_message = f"--- {elapsed:.2f} s --- {message}"
            print(full_message)
            if log_file:
                print(full_message, file=log_file)
            start_time = time.time()
    
    # Starte Zeitmessung und Log
    if enable_logging:
        start_time_0 = time.time()
        start_time = time.time()
        log_file = open(path_log, "w")
        print(f"--- {suffix}", file=log_file)
    
    # scf-Rechnung wird durchgeführt, falls der Ordner bt2_working_directory noch nicht existiert
    if not os.path.exists(bt2_working_directory):
        os.makedirs(bt2_working_directory)
        log("scf-Rechnung wird durchgeführt", log_file)

        num_cores = config.num_cores
        num_pool = config.num_pool
        if num_cores > 1:
            print(f"- Parallele Berechnung mit {num_cores} Kernen")
            process_sc = subprocess.Popen(f"cd {qe_working_directory} && mpirun -np {num_cores} pw.x -npool {num_pool} -in {path_scf_in} > {path_scf_out}", shell=True, stdout=subprocess.DEVNULL)
        else:
            process_sc = subprocess.Popen(f"cd {qe_working_directory} && pw.x -in {path_scf_in} > {path_scf_out}", shell=True, stdout=subprocess.DEVNULL)

        process_sc.wait()
        # Inhalt des tmp-Ordners wird in den Ordner path_COPY_directory kopiert
        config.copy_folder(bt2_working_directory, path_COPY_directory)
        log("scf-Rechnung DONE", log_file)
    
    for i in range(len(coords)):
        
        log(f"R{R:.6f}_r{r:.6f}: Schleife [{i} in {len(coords)}]", log_file)
        # Ändere k-points in bands.in Datei
        change_config_kpoints(path_bands_in, coords[i])
        
        # bands-Rechnung von pw.x wird durchgeführt
        log("bands-Rechnung wird durchgeführt", log_file)

        num_cores = config.num_cores
        num_pool = config.num_pool
        if num_cores > 1:
            print(f"- Parallele Berechnung mit {num_cores} Kernen")
            process_bands = subprocess.Popen(f"cd {qe_working_directory} && mpirun -np {num_cores} pw.x -npool {num_pool} -in {path_bands_in} > {path_bands_out}", shell=True, stdout=subprocess.DEVNULL)
        else:
            process_bands = subprocess.Popen(f"cd {qe_working_directory} && pw.x -in {path_bands_in} > {path_bands_out}", shell=True, stdout=subprocess.DEVNULL)
        
        process_bands.wait()
        log("bands-Rechnung DONE", log_file)
                
        # Kopiere bt2_working_directory nach path_tmp_directory_i
        # Kopieren qe_working_directory nach path_out_directory_i
        path_tmp = config.path_tmp_directory_i(datlabel, nks, phi_steps, R, r, i)
        path_out = config.path_out_directory_i(datlabel, nks, phi_steps, R, r, i)
        
        config.copy_folder(bt2_working_directory, path_tmp)
        config.copy_folder(qe_working_directory, path_out)
        
        # leere Ordner bt2_working_directory
        config.delete_folder(bt2_working_directory)
        
        # kopiere scf-Dateien von path_COPY_directory nach bt2_working_directory
        config.copy_folder(path_COPY_directory, bt2_working_directory)
        log("Kopieren DONE", log_file)
        
    if enable_logging and log_file:
        print("--- %.2f s --- Calculation DONE" % (time.time() - start_time_0))
        print("--- %.2f s --- Calculation DONE" % (time.time() - start_time_0), file=log_file)
        print("")     
        log_file.close()

# ######################################################################################
# Laden und Analyse der Daten
# ######################################################################################

def projection(u, R, a, v, df, plotpath=False):
    """
    - Hilfsfunktion, um die Koordinaten (kx,ky,kz) in die Ebene diagonal zur Ursprungsgeraden zu projezieren
        (kx,ky,kz) -> (x,y)

    Args:
        u:          (ux,uy,uz) - Einheitsvektor der Ursprungsgerade, um die gedreht wird
        R:          Radius für den Einheitsvektor u
        a:          (ax, ay, az) - Einheitsvektor für Anfangspfad, der orthogonal zu u liegt
        v:          (vx, vy, vz) - Verschiebevektor für den Anfangspfad
        df:         Dataframe, welche die Koordinaten (kx,ky,kz) enthält
        plotpath    Sollen die Projektionen geplottet werden?
    Return:
        df:          Das um x und y erweiterte Dataframe
    """
    def Rmat(u, a):
        """
        - Drehmatrix für Drehung um Ursprungsgerade, die durch den Einheitsvektor u=(x,y,z) definiert ist
        """
        x = u[0]
        y = u[1]
        z = u[2]
        return [[(1-np.cos(a))*x*x+np.cos(a)  , (1-np.cos(a))*y*x-np.sin(a)*z, (1-np.cos(a))*z*x+np.sin(a)*y],
                [(1-np.cos(a))*x*y+np.sin(a)*z, (1-np.cos(a))*y*y+np.cos(a)  , (1-np.cos(a))*z*y-np.sin(a)*x],
                [(1-np.cos(a))*x*z-np.sin(a)*y, (1-np.cos(a))*y*z+np.sin(a)*x, (1-np.cos(a))*z*z+np.cos(a)]]
    
    # Ebenenbasis der Ebene diagonal zur Ursprungsgerade (orthonormal)
    e1 = np.array(a)
    e2 = Rmat(u, np.pi/2) @ e1
    if not np.isclose(np.dot(e1, e2),0):
        raise ValueError(f"Ebenenbasis ist nicht orthogonal: {np.dot(e1, e2)}")
    if not np.isclose(np.linalg.norm(e1),1) and np.isclose(np.linalg.norm(e2),1):
        raise ValueError(f"Ebenenbasis ist nicht orhonormal: {np.linalg.norm(e1), np.linalg.norm(e2)}")
    
    # Berechne Koordinaten in der neuen Basis und füge sie dem Dataframe hinzu
    kx_ = df["kx"] - u[0]*R - v[0]
    ky_ = df["ky"] - u[1]*R - v[1]
    kz_ = df["kz"] - u[2]*R - v[2]
    
    df["x"] = e1[0]*kx_ + e1[1]*ky_ + e1[2]*kz_
    df["y"] = e2[0]*kx_ + e2[1]*ky_ + e2[2]*kz_

    # Berechne Ebenenradius und füge ihn dem Dataframe hinzu
    df["rho"] = np.sqrt(df["x"]**2 + df["y"]**2)

    # Visualisierung der Transformation
    if plotpath:
        uvec = np.multiply(np.array(u), R)
        vvec = np.array(v)

        fig = plt.figure(figsize=(FIGWIDTH,FIGWIDTH*HFACTOR))
        ax = fig.add_subplot(projection='3d')

        # Ursprungsvektor
        ax.plot([0,uvec[0]], [0,uvec[1]], [0,uvec[2]], "o", color="black")
        ax.plot([0,uvec[0]], [0,uvec[1]], [0,uvec[2]], "-", color="red")

        # Verschiebevektor
        ax.plot([uvec[0]+vvec[0]], [uvec[1]+vvec[1]], [uvec[2]+vvec[2]], "o", color="black")
        ax.plot([uvec[0],uvec[0]+vvec[0]], [uvec[1],uvec[1]+vvec[1]], [uvec[2],uvec[2]+vvec[2]], "-", color="green")

        # Würfel
        plot_cube(ax, bounds=(-0.5, 0.5), alpha=0.0, face_color='cyan', edge_color='black', edge_width=0.5)

        # Koordinaten
        ax.scatter3D(df["kx"], df["ky"], df["kz"], s=2, label="k_points")
        ax.scatter3D(kx_, ky_, kz_, s=2, label="Verschiebung auf den Ursprung")
        ax.scatter3D(df["x"], df["y"], [0]*len(df["x"]), s=2, label="Projektion auf die Ebene")

        ax.set(xlabel="x", ylabel="y", zlabel="z")
        plt.legend()

        if SAVE:
            plt.savefig(f"{DATEIENNAME}.jpg", bbox_inches=BBOX)
            plt.savefig(f"{DATEIENNAME}.png", bbox_inches=BBOX)
            plt.savefig(f"{DATEIENNAME}.pdf", bbox_inches=BBOX)
        if SHOW:
            #fig.canvas.manager.window.showMaximized()
            plt.show()

    return df

def xml_to_df(u: list,
              R: float,
              a: list,
              r: float,
              v: list,
              nks: int,
              datlabel: str,
              phi_lin: list,
              bandnumbers: list = None):
    """
    - verwendet die Funkton projektion als Hilfsfunktion, um die Daten in die 2D-Ebene zu projezieren
    - lädt Daten aus der xml-Datei von (QE) und speichert die Ergebnisse als Pandas Dataframes in entsprechende Unterordner
        Dataframe (..._df.csv):
        - Energien in Hartree
        - Winkel in rad
        Dataframe (..._df_for_plots.csv):
        - Enegien in eV
        - Winkel in deg
    - alle Dataframes (..._df_for_plots.csv) werden zusammengefasst und als (..._all_df_for_plots.csv) gespeichert
    - Liste aller Dataframe (..._df_for_plots.csv) wird zurückgegeben       

    Args:
        u:          (ux,uy,uz) - Einheitsvektor der Ursprungsgerade, um die gedreht wird
        R:          Radius für den Einheitsvektor u
        a:          (ax, ay, az) - Einheitsvektor für Anfangspfad, der orthogonal zu u liegt
        r:          Radius für den Einheitsvektor a
        v:          (vx, vy, vz) - Verschiebevektor für den Anfangspfad
        nks:            Anzahl der Datenpunkte pro Pfad
        datlabel:       extra Label in Dateienname, um Rechnungen zu unterscheiden
        phi_lin:        Winkel der Pfade als numpy-Array
        bandnumners:    Liste der Bänder, die für den Plot ausgewählt werden. Werden genau zwei Bänder gewählt, wird die Differenz berechnet.
    Return:
        df_list:        Liste von Pandas-Dataframes der Bänder
    """

    phi_steps = len(phi_lin)  
    df_list = []
    for i in range(phi_steps):
        path_out_directory_i = config.path_out_directory_i(datlabel, nks, phi_steps, R, r, i)

        # Laden der xml-Datei
        path_xml = config.path_xml(datlabel, nks, phi_steps, R, r, i)
        tree = ET.parse(path_xml)
        root = tree.getroot()

        # Liste von Dictionaries mit dn Einträgen aus dem xml-File
        dicts = [] 
        for type_tag in root.findall("output/band_structure/ks_energies"):
            
            k_point = type_tag.find("k_point").text.strip().split()
            k_point = list(map(float, k_point))
            line = {"kx": k_point[0], "ky": k_point[1], "kz": k_point[2]}

            eigenvalues = type_tag.find("eigenvalues").text.strip().split()
            eigenvalues = list(map(float, eigenvalues))
            for j in range(len(eigenvalues)):
                line.update({f"band{j}": eigenvalues[j]})

            dicts.append(line)
        
        # Füge alle Dictionaries mit jeweils gleichen Keys zusammen
        merged = {} 
        for d in dicts:
            for key, value in d.items():
                merged.setdefault(key, []).append(value)

        # Erstellung des Pandas-Dataframe
        df = pd.DataFrame(merged)

        # Füge weitere Einträge hinzu
        df["phi"] = [phi_lin[i]] * nks
        df["R"] = [R] * nks
        df["r"] = [r] * nks
        
        fermi_node = root.find("output/band_structure/fermi_energy")
        fermi_energy = float(fermi_node.text)
        df["fermi_energy"] = [fermi_energy] * nks

        # speichern als csv
        config.save_csv(df, path_out_directory_i, "df")

        # -------------------------------------------------------------------

        # Erzeuge Dataframe speziell für die Plots
        if bandnumbers is not None:
            new = df[["kx", "ky", "kz", "phi", "R", "r", "fermi_energy"]].copy()

            # Bandenergien
            for i in range(len(bandnumbers)):
                new[f"band{i}"] = (df[f"band{bandnumbers[i]}"] - df["fermi_energy"])/units.eV

            # Fermi-Energie
            new["fermi_energy"] = new["fermi_energy"]/units.eV

            # Winkel
            new["phi"] = new["phi"]*180/np.pi

            # Banddifferenz
            if bandnumbers is not None and len(bandnumbers) == 2:
                new["diff"] = abs(new["band0"] - new["band1"])
            
            # Projektion in die Ebene und Radius innerhalb der Ebene
            new = projection(u, R, a, v, new, plotpath=False)

            # pd.options.mode.chained_assignment = None # Deaktiviert Index Warnung von Pandas

            # Indizes als Spalte
            new['index1'] = new.index

            # speichern als csv
            config.save_csv(new, path_out_directory_i, "df_for_plots")       
            df_list.append(new)

    # Fasse alle Dataframes in df_list zusammen und speichere das Ergebnis
    if bandnumbers is not None:
        df_merged = pd.concat(df_list, ignore_index=True)
        path_out_directory = config.path_out_directory(datlabel, nks, phi_steps, R, r)
        config.save_csv(df_merged, path_out_directory, "all_df_for_plots")

    return df_list

# -------------------------------------------------------------------------------------

def find_all_peaks(array):
    """
    - Hilfsfunktion, um alle Peaks (lokale Minima) zu berechnen, auch wenn die Minima Plateaus sind
    Args:
        array       numpy-Array
    Return:
        all_peaks   Indizes von allen lokalen Minima bzw. Plateaus
    """
    # lokale Minima außer Randpunkte
    peaks, _ = find_peaks(np.negative(array))
    all_peaks = []
    for peak in peaks:
        for j in range(len(array)):
            if array[j] == array[peak]:
                all_peaks.append(j)

    # Randpunkte
    if array[0] <= array[1]:
        for j in range(len(array)):
            if array[j] == array[0]:
                all_peaks.append(j)
    if array[-1] <= array[-2]:
        for j in range(len(array)):
            if array[j] == array[-1]:
                all_peaks.append(j)
    
    all_peaks = sorted(list(set(all_peaks))) # entfernt doppelte Einträge der Liste und sortiert
    return all_peaks

def find_global_min(array):
    """
    - Hilfsfunktion, die das globale Minimum des Betrags von array berechnet, auch wenn die Minima ein Plateau sind
    Args:
        array:       numpy-Array
    Return:
        minimum_indis:  Indizes von alllen globalen Minima bzw. Plateaus
    """
    minimum_index = np.abs(np.round(array,8) - 0).argmin()
    minimum_indis = []
    for i in range(len(array)):
        if array[i] == array[minimum_index]:
            minimum_indis.append(i)
    minimum_indis = list(set(minimum_indis)) # entfernt doppelte Einträge der Liste
    return minimum_indis

def df_to_peaks(df_list: list,
                R: float,
                r: float,
                phi_steps: int,
                nks: int,
                datlabel: list):
    """
    - Berechnung lokaler und globaler Minima aller Pfade und speichern der Ergebnisse
        - berechnet Peaks (lokale Minima) der einzelnen Pfade
    - Fasst alle Ergebnisse zusammen, speichern und Rückgabe als Dataframe

    Args:
        df_list:        Liste von Pandas-Dataframes der ausgewählten Bänder
        R:              Radius für den Einheitsvektor u
        r:              Radius für den Einheitsvektor a
        phi_steps:      Anzahl der Zwischenpfade zwischen 0° und 180°
        nks:            Anzahl der Datenpunkte pro Pfad
        datlabel:       extra Label in Dateienname, um Rechnungen zu unterscheiden
    Return:
        df_all_peaks   Liste von Dataframes mit den Peaks
    """    
    #pd.options.mode.chained_assignment = None # Deaktiviert Index Warnung von Pandas
    
    df_peaks_list = []
    for i in range(len(df_list)):
        df = df_list[i]

        # Berechnung der Peaks - wenn die Peaks Plateaus bilden, werden diese ausgegeben
        diff = np.array(df["diff"])
        all_peaks = find_all_peaks(diff)
        
        # neues df auf Basis der Peaks
        df_peaks = df.iloc[all_peaks]
        df_peaks_list.append(df_peaks)
        
        # speichere Ergebnisse als csv-Datei
        path_out_directory_i = config.path_out_directory_i(datlabel, nks, phi_steps, R, r, i)
        config.save_csv(df_peaks, path_out_directory_i, "peaks")

    # Fasse alle Dataframes zusammen und speichere das Ergebnis
    df_all_peaks = pd.concat(df_peaks_list, ignore_index=True)
    path_out_directory = config.path_out_directory(datlabel, nks, phi_steps, R, r)
    config.save_csv(df_all_peaks, path_out_directory, "all_peaks")

    return df_all_peaks

def peaks_to_mins(df_all_peaks: list,
                  R: float,
                  r: float,
                  phi_steps: int,
                  nks: int,
                  datlabel: list):
    """
    - Fasse alle Peaks zu einem Dataframe zusammen und speichern als all_peaks.csv
    - Berechnung der lokalen Minima von all_peaks.csv und speichern als all_mins.csv
    - Berechnung der globalen Minima von all_mins.csv und speichern als all_global_min.csv 

    Args:
        df_peaks_list:  Liste von Dataframes mit den Preaks
        R:              Radius für den Einheitsvektor u
        r:              Radius für den Einheitsvektor a
        phi_steps:      Anzahl der Zwischenpfade zwischen 0° und 180°
        nks:            Anzahl der Datenpunkte pro Pfad
        datlabel:       extra Label in Dateienname, um Rechnungen nochmal gezielt zu unterscheiden
    Return:
        df_mins:        Liste mit allen lokalen Minima
        df_global_mins: Liste mit allen globalen Minima
    """
    path_out_directory = config.path_out_directory(datlabel, nks, phi_steps, R, r)

    # Berechnung der lokalen Minima von all_peaks.csv und speichern als all_mins.csv 
    diff = np.array(df_all_peaks["diff"])
    all_mins = find_all_peaks(diff)
    df_mins = df_all_peaks.iloc[all_mins]
    config.save_csv(df_mins, path_out_directory, "phi_peaks")

    # Berechnung der globalen Minima von all_mins.csv und speichern als all_global_min.csv
    diff_mins = np.array(df_mins["diff"])
    minimum_indis = find_global_min(diff_mins)
    df_global_mins = df_mins.iloc[minimum_indis]
    config.save_csv(df_global_mins, path_out_directory, "phi_global_peaks")

    return df_mins, df_global_mins
