import os
import os.path
import shutil
import re
import subprocess
import time
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import xml.etree.ElementTree as ET
import filecmp
from BoltzTraP2 import units
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from sklearn.decomposition import PCA
from sklearn.linear_model import RidgeCV

import lib.config as config
import lib.qe_model_models as models
import lib.qe_model_pathmodels as pathmodels
from lib.plot_config import FIGWIDTH, HFACTOR, SCATTER_CONFIG, BBOX, DATEIENNAME, SHOW, SAVE, TITEL

# ######################################################################################
# --------------------------------------------------------------------------------------
# Hilfsfunktionen
# --------------------------------------------------------------------------------------

def change_parameter_pn(x):
    """
    - Hilfsfunktion für den Parameter p oder n
    - falls x ein float oder int -> x=(x, x, x)
    - erzeugt dann p_str oder n_str für die Dateien- und Ordnerbeschriftungen x_str
    """
    if isinstance(x, (float, int)):
        x = np.array([x,x,x])
    else:
        x = np.array(x)
    x_str = f"{x[0]}-{x[1]}-{x[2]}"
    return x, x_str

# --------------------------------------------------------------------------------------
# Funktion zum Berechnen der Pfad-Vektoren aus dem thz-Modul
# --------------------------------------------------------------------------------------

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

    #print()
    #print(f"Anfangsvektor:\n{R}*({u}) + {v} + {r}*({a})\n={uvec+vvec+avec}")
    #print()

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
# Definition des Gitters
# ######################################################################################

# --------------------------------------------------------------------------------------
# einfache Gitter
# --------------------------------------------------------------------------------------

def regular_grid(k0: list,
                 p: list,
                 n: list,
                 decimals: int=12):
    """
    - Funktion erzeugt ein kartesisches Gitter mit Punktsymmetriezentrum k0

    Args:
        k0:             Verschiebungsvektor auf Schnittpunkt der Bänder
        p:              halbe Kantenlängen des Gitters im Zentrum: [x_max, y_max, z_max]
        n:              Anzahl der Datenpunkte der Kantenlängen [N_x, N_y, N_z]
        decimals:       legt fest, auf wie viele Nachkommastellen die Pfadvektoren gerundet werden, standart:12
    Return:
        k_grid:         Vektoren des k-Gitters {kx_ky_kz}
        k_grid_center:  Vektoren des Gitters im Koordinatenursprung {x,y,z}
        coords:         Liste der kpoints Koordinaten für Quantum Espresso
    """
    k0 = np.array(k0)

    # prüfe, ob Kantenlängen ungerade sind
    if n[0] % 2 == 0:
        raise ValueError("n[0]=n_t muss ungerade sein!")
    if n[1] % 2 == 0:
        raise ValueError("n[0]=n_t muss ungerade sein!")
    if n[2] % 2 == 0:
        raise ValueError("n[0]=n_t muss ungerade sein!")
    
    nkx = n[0]
    nky = n[1]
    nkz = n[2]

    kx_lin = np.linspace(-p[0], p[0], nkx)
    ky_lin = np.linspace(-p[1], p[1], nky)
    kz_lin = np.linspace(-p[2], p[2], nkz)

    if nkx > 1 and nky > 1 and nkz > 1:
        print(f"----> festgelegte Gittergrenzen:")
        print(f"----> (min(kx), max(kx), Punkteabstand = {(float(-p[0]), float(p[0]), float(abs((kx_lin[1]-kx_lin[0]))))}")
        print(f"----> (min(ky), max(ky), Punkteabstand) = {(float(-p[1]), float(p[1]), float(abs((ky_lin[1]-ky_lin[0]))))}")
        print(f"----> (min(kz), max(kz), Punkteabstand) = {(float(-p[2]), float(p[2]), float(abs((kz_lin[1]-kz_lin[0]))))}")

    k_grid = []
    k_grid_center = [] # wird für die Rotation des Gitters benötigt
    for kx in kx_lin:
        for ky in ky_lin:
            for kz in kz_lin:
                k_grid.append(np.array([kx, ky, kz]) + k0)
                k_grid_center.append(np.array([kx, ky, kz]))
    k_grid = np.vstack(k_grid)
    k_grid_center = np.vstack(k_grid_center)
    print(f"----> Anzahl der k-Punkte: {len(k_grid)}")
    #x_vals = np.unique(k_grid_center[:, 0])
    #print(f"----> Schritte der Datenpunkte im k_grid_center:\n{x_vals}")

    coords = []
    for k in k_grid:
        kvec = np.round(k, decimals)
        c = str(kvec[0])+" "+str(kvec[1])+" "+str(kvec[2])+" "+str(1.0) # 1.0: gleichmäßige Gewichtung in QE
        coords.append(c)  
    return k_grid, k_grid_center, coords

def cylindrical_grid(k0: list,
                     z_axis: str,
                     p: list,
                     n: list,
                     phi_sym: int=1,
                     n_phi_min: int=2,
                     R_dense: float=None,
                     r_sigma: float=None,
                     base_weight: float=0.25,
                     decimals: int=12):
    """
    - Funktion erzeugt ein zylindrisches Gitter mit Symmetriezentrum k0
    - optionale n-fach-Symmetrie
    - optionale radiale Gauß-Dichte bei R_dense
    Args:
        k0:             Verschiebungsvektor auf Schnittpunkt der Bänder
        z_axis:         Achse des Zylinders ("x", "y", oder "z")
        p:              Kantenlängen des Gitters im Zentrum: [Radius, 0, halbe Höhe in Richtung z_axis]
        n:              Anzahl der Datenpunkte der Achsen: [N_Radius, N_phi, N_z]
        phi_sym:        Anzahl der Symmetrie-Sektoren (z.B. 4 bei 4-fach-Symmetrie)
        n_phi_min:      Minimale Anzahl an phi-Punkten pro Symmetrie-Sektor
                        None: gleichmäßige phi-Verteilung
        R_dense:        Radius der radialen Gaus-Dichte
        r_sigma:        Ausdehnung und Stärke der radialen Gaus-Dichte
        base_weight:    Basiswert für Dichte außerhalb des Gauß-Dichte-Bereichs
        decimals:       legt fest, auf wie viele Nachkommastellen die Pfadvektoren gerundet werden, standart:12
    Return:
        k_grid:         Vektoren des k-Gitters {kx_ky_kz}
        k_grid_center:  Vektoren des Gitters im Koordinatenursprung {x,y,z}
        coords:         Liste der kpoints Koordinaten für Quantum Espresso
    """
    # Maximum der Koordinatenachsen
    r_max = p[0]
    z_max = p[2]
    k0 = np.array(k0)

    # Anzahl der Punkte pro Koordinatenachse
    if n[1] % 2 == 0:
        raise ValueError("n[0]=n_phi muss ungerade sein!")
    if n[2] % 2 == 0:
        raise ValueError("n[0]=n_z muss ungerade sein!")
    
    n_r = n[0]
    n_phi_max = n[1]
    n_z = n[2]

    # Richtung der z-Achse
    def kx_ky_kz(r, phi, z):
        if z_axis == "x":
            kx = z
            ky = r*np.cos(phi)
            kz = r*np.sin(phi)
        elif z_axis == "y":
            kx = r*np.cos(phi)
            ky = z
            kz = r*np.sin(phi)
        elif z_axis == "z":
            kx = r*np.cos(phi)
            ky = r*np.sin(phi)
            kz = z
        else:
            raise ValueError(f"Fehler: falsher z_axis-Parameter: {z_axis}! Verfügbare Parameter: ’x’, ’y’, ’z’")
        return kx, ky, kz
    
    # gleichmäßige Verteilung der Punkte in z-Richtung:
    z_lin = np.linspace(-z_max, z_max, n_z)

    # gleichmäßige Verteilung der Punkte in phi-Richtung:
    if n_phi_min == None:
        phi_lin = np.linspace(0, 2*np.pi, n_phi_max, endpoint=False)

    # (optional ungleiche) Verteilung der Punkte entlang des Radius:
    if (R_dense is not None) and (r_sigma is not None):
        # gleichverteilte Werte zwischen 0 und 1:
        u = np.linspace(0,1,n_r)
        # Hilfsraster
        r_dense = np.linspace(0, r_max, n_r*10)
        w = np.exp(-0.5 * ((r_dense - R_dense) / r_sigma) ** 2) + base_weight # Gauß ~ Wahrscheinlichkeitsdichte
        distrib = np.cumsum(w) # ~ Verteilung
        distrib = distrib / distrib[-1] # Normierung
        r_lin = np.interp(u, distrib, r_dense)
    else:
        r_lin = np.linspace(0, r_max, n_r)

    # Definition des Gitters und Verteilung der phi-Werte
    k_grid = []
    k_grid_center = []
    for r in r_lin:
        if n_phi_min is not None:
            # Verteilung der phi in Abhängigkeit des Radius
            n_phi_r = max(int(n_phi_max*(r/r_max)), n_phi_min)
            phi_offset = np.pi/4
            phi_sector = np.linspace(0, 2*np.pi/phi_sym, n_phi_r, endpoint=False)
            phi_offsets = np.arange(phi_sym) * (2*np.pi/phi_sym)
            phi_lin = (phi_sector[None, :] + phi_offsets[:, None]+ phi_offset).ravel()
            phi_lin = np.sort(phi_lin) # Sortierung wichtig für QE
        for z in z_lin:
            for phi in phi_lin:
                kx, ky, kz = kx_ky_kz(r, phi, z)
                k_grid.append(np.array([kx, ky, kz]) + k0)
                k_grid_center.append(np.array([kx, ky, kz]))

    k_grid = np.vstack(k_grid)
    k_grid_center = np.vstack(k_grid_center)

    print(f"----> mittlere Gitterabstände | Anzahl der Datenpunkte")
    print(f"----> mittlerer Gitterabstand in t-Richtung: {np.mean(np.abs(np.diff(z_lin)))} | N_t={len(z_lin)}")
    print(f"----> mittlerer Gitterabstand in rho-Richtung: {np.mean(np.abs(np.diff(r_lin)))} | N_rho={len(r_lin)}")
    print(f"----> mittlerer Gitterabstand in phi-Richtung: {np.mean(np.abs(np.diff(phi_lin)))} | N_phi={len(phi_lin)}")
    #print(f"----> Gitter in t-Richtung:\n{z_lin}")
    #print(f"----> Gitter in rho-Richtung:\n{r_lin}")
    #print(f"----> Gitter in phi-Richtung:\n{(180/np.pi)*phi_lin}")
    print(f"----> Anzahl der k-Punkte: {len(k_grid)}")

    coords = []
    for k in k_grid:
        kvec = np.round(k, decimals)
        c = str(kvec[0])+" "+str(kvec[1])+" "+str(kvec[2])+" "+str(1.0)
        coords.append(c)
    return k_grid, k_grid_center, coords

# --------------------------------------------------------------------------------------
# Laden der Pfade an verschiedenen Punkten 1,2,3 für Pfad-Gitter
# --------------------------------------------------------------------------------------

def load_path(modeltype_path, t_lin, a_coeffs=None, b_coeffs=None):
    """
    - Hilfsfunktion zum Laden des richtigen Pfades
    - Return: Raumkurve r ; Binormalenvektor B ; Normalenvektor N
    """
    if modeltype_path=="path_point1":
        r = pathmodels.r_point1(t_lin, a_coeffs, b_coeffs)
        dr = pathmodels.dr_point1(t_lin, a_coeffs, b_coeffs)
        ddr = pathmodels.ddr_point1(t_lin, a_coeffs, b_coeffs)
        dddr = pathmodels.dddr_point1(t_lin, a_coeffs, b_coeffs)
        T, N, B, v, kappa, tau = pathmodels.frenet(dr, ddr, dddr)
    elif modeltype_path=="path_point2A":
        # Pfad r(t):
        r = pathmodels.r_point2A(t_lin) #shape(n,3)
        # Der Tangentenvektor liegt in 111-Richtung
        T = np.array([1.0, 1.0, 1.0])
        T = T / np.linalg.norm(T) # Normierung
        T = np.tile(T, (len(t_lin), 1))   # shape (n, 3)
        # Wahl von N und B ist nicht eindeutig
        # Definiere B über a aus der nitiB2_thz Untersuchung (müsste die Richtung eines Seitenarms sein):
        B = np.array([1.0, 1.0, -2.0])
        B = B / np.linalg.norm(B) # Normierung
        B = np.tile(B, (len(t_lin), 1))   # shape (n, 3)
        # Tangentenvekor liegt in 111-Richtung; Normalenvektor N=BxT:
        N = np.array([1.0, -1.0, 0.0])
        N = N / np.linalg.norm(N)
        N = np.tile(N, (len(t_lin), 1))   # shape (n, 3)
        # Die Krümmung ist Null
        kappa = np.tile(0, (len(t_lin), 1))
    elif modeltype_path=="path_point3":
        # Pfad r(t):
        r = pathmodels.r_point3(t_lin) #shape(n,3)
        # Der Tangentenvektor liegt in 001-Richtung
        T = np.array([0, 0, 1.0])
        T = T / np.linalg.norm(T) # Normierung
        T = np.tile(T, (len(t_lin), 1))   # shape (n, 3)
        # Definiere B über a aus der nitiB2_thz Untersuchung
        B = np.array([1.0, 1.0, 0.0])
        B = B / np.linalg.norm(B) # Normierung
        B = np.tile(B, (len(t_lin), 1))   # shape (n, 3)
        # Tangentenvektor liegt in 001-Richtung; Normalenvektor N=BxT:
        N = np.array([1.0, -1.0, 0.0])
        N = N / np.linalg.norm(N)
        N = np.tile(N, (len(t_lin), 1))   # shape (n, 3)
        # Die Krümmung ist Null
        kappa = np.tile(0, (len(t_lin), 1))
    elif modeltype_path=="path_point1_center":
        # Pfad r(t):
        r = pathmodels.r_point1_center(t_lin) #shape(n,3)
        # Der Tangentenvektor liegt in 001-Richtung
        T = np.array([1.0, 0, 0])
        T = T / np.linalg.norm(T) # Normierung
        T = np.tile(T, (len(t_lin), 1))   # shape (n, 3)
        # Definiere B über 011-Richtung aus der nitiB2_thz Untersuchung
        B = np.array([0, 1.0, 1.0])
        B = B / np.linalg.norm(B) # Normierung
        B = np.tile(B, (len(t_lin), 1))   # shape (n, 3)
        # Tangentenvektor liegt in 100-Richtung; Normalenvektor N=BxT:
        N = np.array([0, -1.0, 1.0])
        N = N / np.linalg.norm(N)
        N = np.tile(N, (len(t_lin), 1))   # shape (n, 3)
        # Die Krümmung ist Null
        kappa = np.tile(0, (len(t_lin), 1))
    else:
        raise ValueError(f"Falscher Parameter: modeltype_path={modeltype_path}; verfügbar:\n path_point1 \n path_point2A \n path_point3 \n path_point1_center")
    return r, T, B, N, kappa

def load_path_point2B(modeltype_path, t_lin, a_coeffs, phi):
    """
    - Hilfsfunktion zum Laden des Pfades 2B, der aus dem Pfad 2A berechnet wird
    - Return: Raumkurve r ; rho ; phi
    """
    if modeltype_path=="path_point2B":
        r, rho, phi = pathmodels.r_point2B(t_lin, a_coeffs, phi)
    else:
        raise ValueError(f"Falscher Parameter: modeltype_path={modeltype_path}; verfügbar:\n path_point2B")
    return r, rho, phi

# --------------------------------------------------------------------------------------
# Pfad-Gitter
# --------------------------------------------------------------------------------------

def path_grid(modeltype_path: str,
              k0: list,
              p: list,
              n: list,
              a_coeffs: list,
              b_coeffs: list,
              phi_sym: int=1,
              n_phi_min: int=None,
              non_equidistant: int=None,
              rho_dense: float=None,
              rho_sigma: float=None,
              base_weight: float=0.25,
              no_rho0: bool=False,
              decimals: int=12):
    """
    - verwendet Funktion load_path als Hilfsfunktion

    - Polarkoordinaten-Gitter entlang des Pfades
    - optionale n-fach-Symmetrie
    - optionale radiale Gauß-Dichte bei rho_dense

    Args: 
        modeltype_path:     Modell des Pfades der Schnittpunktumgebung
        k0:                 Verschiebungsvektor auf Schnittpunkt der Bänder
        p:                  Kantenlängen: [halbe Kantenlänge in t-Richtung, Radius in der Polarebene, 0]
        n:                  Anzahl der Datenpunkte: [N_t, N_rho, N_phi]
        a_coeffs:           a-Koeffizienten des Pfades
        b_coeffs:           b-Koeffizienten des Pfades
        phi_sym:            Anzahl der Symmetrie-Sektoren (z.B. 4 bei 4-fach-Symmetrie)
        n_phi_min:          Minimale Anzahl an phi-Punkten pro Symmetrie-Sektor
                            None: gleichmäßige phi-Verteilung
        non_equidistant:    Winkel sind um den Wert non_equidistant*np.sin(np.arange(n_phi)) nicht mehr äquidistant
        rho_dense:          Radius der radialen Gaus-Dichte
        rho_sigma:          Ausdehnung und Stärke der radialen Gaus-Dichte
        base_weight:        Basiswert für Dichte außerhalb des Gauß-Dichte-Bereichs
        no_rho0:            rho=0 wird entfernt
        decimals:           legt fest, auf wie viele Nachkommastellen die Pfadvektoren gerundet werden, standart:12
    Return:
        k_grid:         Vektoren des k-Gitters {kx_ky_kz}
        k_grid_center:  Vektoren des Gitters im Koordinatenursprung {x,y,z}
        coords:         Liste der kpoints Koordinaten für Quantum Espresso
        t_grid_center:  Vektoren des Gitters in Pfadkoordinaten {t, rho, phi}
    """
    # Maximum der Koordinatenachsen
    t_max = p[0]
    rho_max = p[1]
    k0 = np.array(k0)

    # Anzahl der Punkte pro Koordinatenachse
    if n[0] % 2 == 0:
        raise ValueError("n[0]=n_t muss ungerade sein!")
    
    n_t = n[0]
    n_rho = n[1]
    n_phi_max = n[2]

    # gleichmäßige Verteilung der Punkte in t-Richtung
    t_lin = np.linspace(-t_max, t_max, n_t)

    # gleichmäßige Verteilung der Punkte in phi-Richtung:
    if n_phi_min == None:
        phi_lin = np.linspace(0, 2*np.pi, n_phi_max, endpoint=False)
        if non_equidistant is not None:
            phi_lin += non_equidistant*np.sin(np.arange(n_phi_max)) # macht Winkel nicht äquidistant

    #print(phi_lin*180/np.pi)

    # (optional ungleiche) Verteilung der Punkte in rho-Richtung
    if (rho_dense is not None) and (rho_sigma is not None):
        # gleichverteilte Werte zwischen 0 und 1
        u = np.linspace(0,1,n_rho)
        # Hilfsraster
        r_dense = np.linspace(0, rho_max, n_rho*10)
        w = np.exp(-0.5 * ((r_dense - rho_dense) / rho_sigma) ** 2) + base_weight # Gauß ~ Wahrscheinlichkeitsdichte
        distrib = np.cumsum(w) # ~ Verteilung
        distrib = distrib / distrib[-1] # Normierung
        rho_lin = np.interp(u, distrib, r_dense)
    else:
        rho_lin = np.linspace(0, rho_max, n_rho)
    if no_rho0:
        rho_lin = np.delete(rho_lin, 0)

    # Pfad und Frenetsches Dreibei
        
    r, T, B, N, kappa = load_path(modeltype_path, t_lin, a_coeffs, b_coeffs)

    # Definition des Gitters und Verteilung der phi-Werte
    k_grid = []
    k_grid_center = []
    t_grid_center = []

    for i in range(len(t_lin)):
        for rho in rho_lin:
            if n_phi_min is not None:
                # Verteilung der phi in Abhängigkeit des Radius
                n_phi_rho = max(int(n_phi_max*(rho/rho_max)), n_phi_min)
                phi_offset = np.pi/4
                phi_sector = np.linspace(0, 2*np.pi/phi_sym, n_phi_rho, endpoint=False)
                phi_offsets = np.arange(phi_sym) * (2*np.pi/phi_sym)
                phi_lin = (phi_sector[None, :] + phi_offsets[:, None]+ phi_offset).ravel()
                phi_lin = np.sort(phi_lin) # Sortierung wichtig für QE
            if (n_phi_min is None) and (phi_sym != 1):
                n_phi = int(n_phi_max/phi_sym)
                phi_sector = np.linspace(0, 2*np.pi/phi_sym, n_phi, endpoint=False)
                phi_offsets = np.arange(phi_sym) * (2*np.pi/phi_sym)
                phi_lin = (phi_sector[None, :] + phi_offsets[:, None]).ravel()
                phi_lin = np.sort(phi_lin) # Sortierung wichtig für QE
            for phi in phi_lin:
                x = r[i, 0] + rho*np.sin(phi)*N[i,0] + rho*np.cos(phi)*B[i,0]
                y = r[i, 1] + rho*np.sin(phi)*N[i,1] + rho*np.cos(phi)*B[i,1]
                z = r[i, 2] + rho*np.sin(phi)*N[i,2] + rho*np.cos(phi)*B[i,2]
                k_grid_center.append(np.array([x,y,z]))
                k_grid.append(np.array([x,y,z])+k0)
                t_grid_center.append(np.array([t_lin[i], rho, phi]))
    
    k_grid = np.vstack(k_grid)
    k_grid_center = np.vstack(k_grid_center)
    t_grid_center = np.vstack(t_grid_center)

    print(f"----> mittlere Gitterabstände | Anzahl der Datenpunkte")
    print(f"----> mittlerer Gitterabstand in t-Richtung: {np.mean(np.abs(np.diff(t_lin)))} | N_t={len(t_lin)}")
    print(f"----> mittlerer Gitterabstand in rho-Richtung: {np.mean(np.abs(np.diff(rho_lin)))} | N_rho={len(rho_lin)}")
    print(f"----> mittlerer Gitterabstand in phi-Richtung: {(180/np.pi)*np.mean(np.abs(np.diff(phi_lin)))}° | N_phi={len(phi_lin)}")
    #print(f"----> Gitter in t-Richtung:\n{t_lin}")
    #print(f"----> Gitter in rho-Richtung:\n{rho_lin}")
    #print(f"----> Gitter in phi-Richtung:\n{(180/np.pi)*phi_lin}")
    print(f"----> Anzahl der k-Punkte: {len(k_grid)}")
    
    coords = []
    for k in k_grid:
        kvec = np.round(k, decimals)
        c = str(kvec[0])+" "+str(kvec[1])+" "+str(kvec[2])+" "+str(1.0) # 1.0: gleichmäßige Gewichtung in QE
        coords.append(c) 
    return k_grid, k_grid_center, coords, t_grid_center

def path_grid_semi_regular(modeltype_path:str,
                           k0: list,
                           p: list,
                           n: list,
                           a_coeffs: list,
                           b_coeffs: list,
                           decimals: int=12):
    """
    - verwendet Funktion load_path als Hilfsfunktion

    - Koordinatensystem durch Verschiebung des Pfades r(t) entlang der Vektoren:
                - N = Normalenvektor
                - B = Binormalenvektor
                - vN = Komponente in Richtung von N
                - vB = Komponente in Richtung von B
    Args:
        modeltype_path:     Modell des Pfades der Schnittpunktumgebung
        k0:                 Verschiebungsvektor auf Schnittpunkt der Bänder
        p:                  Kantenlängen: [halbe Kantenlänge in t-Richtung, halbe Kantenlänge in vN-Richtung, halbe Kantenlänge in vB-Richtung]
        n:                  beeinflusst Anzahl der Punkte: [N_t, N_vN, N_vB]
        a_coeffs:           a-Koeffizienten des Pfades
        b_coeffs:           b-Koeffizienten des Pfades
        decimals:           legt fest, auf wie viele Nachkommastellen die Pfadvektoren gerundet werden, standart:12
    Return:
        k_grid:             Vektoren des k-Gitters {kx_ky_kz}
        k_grid_center:      Vektoren des Gitters im Koordinatenursprung {x,y,z}
        coords:             Liste der kpoints Koordinaten für Quantum Espresso
        t_grid_center:      Vektoren des Gitters in Pfadkoordinaten {t, rho, phi}
        v_grid_center:      Vektoren der Komponenten {t, vN, vB}
    """
    # Maximum der Koordinatenachsen
    t_max = p[0]
    vN_max = p[1]
    vB_max = p[2]
    k0 = np.array(k0)

    # Anzahl der Punkte pro Koordinatenachse
    n_t = 2*n[0]-1
    n_vN = 2*n[1]-1
    n_vB = 2*n[2]-1
    
    # gleichmäßige Verteilung der Punkte in t-Richtung
    t_lin = np.linspace(-t_max, t_max, n_t)
    vN_lin = np.linspace(-vN_max, vN_max, n_vN)
    vB_lin = np.linspace(-vB_max, vB_max, n_vB)

    r, T, B, N, kappa = load_path(modeltype_path, t_lin, a_coeffs, b_coeffs)
    k_grid = []
    k_grid_center = []
    t_grid_center = []
    v_grid_center = []
    for i in range(len(t_lin)):
        for vN in vN_lin:
            for vB in vB_lin:
                x = r[i,0] + vN*N[i,0] + vB*B[i,0]
                y = r[i,1] + vN*N[i,1] + vB*B[i,1]
                z = r[i,2] + vN*N[i,2] + vB*B[i,2]
                rho = np.sqrt(vN**2 + vB**2)
                phi = np.arctan2(vN, vB)
                k_grid_center.append(np.array([x,y,z]))
                k_grid.append(np.array([x,y,z])+k0)
                t_grid_center.append(np.array([t_lin[i], rho, phi]))
                v_grid_center.append(np.array([t_lin[i], vN, vB]))

    k_grid = np.vstack(k_grid)
    k_grid_center = np.vstack(k_grid_center)
    t_grid_center = np.vstack(t_grid_center)
    v_grid_center = np.vstack(v_grid_center)

    print(f"----> mittlere Gitterabstände | Anzahl der Datenpunkte")
    print(f"----> mittlerer Gitterabstand in t-Richtung: {np.mean(np.abs(np.diff(t_lin)))} | N_t={len(t_lin)}")
    print(f"----> mittlerer Gitterabstand in vN-Richtung: {np.mean(np.abs(np.diff(vN_lin)))} | N_vN={len(vN_lin)}")
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
    return k_grid, k_grid_center, coords, t_grid_center, v_grid_center

# Speziell für Punkt 2 unter Berücksichtigung von Pfad 2B

def make_phi_grid(n_phi, phi_sym=1, phi_sigma=None):
    """
    - Hilffunktion zum Erzeugen des Winkelgitters für Funktion make_rho_phi_grid
    Fälle:
    - phi_sym = 1 ->  gleichmäßig
    - phi_sym > 1, phi_sigma  = None -> exakt symmetrisch
    - phi_sym > 1, phi_sigma != None -> exakt symmetrisch + Verdichtung an den Symmetrie-Winkeln
    """
    if phi_sym == 1:
        return np.linspace(0, 2*np.pi, n_phi, endpoint=False)

    if n_phi % phi_sym != 0:
        raise ValueError("n_phi muss durch phi_sym teilbar sein")

    n_sector = n_phi // phi_sym
    sector_width = 2*np.pi / phi_sym

    # exakt symmetrisch
    if phi_sigma is None:
        phi_sector = np.linspace(0, sector_width, n_sector, endpoint=False)

    # exakt symmetrisch + periodische Verdichtung
    else:
        phi_fine = np.linspace(0, sector_width, 6000, endpoint=False)

        centers = [0, sector_width]
        density = np.ones_like(phi_fine)

        for c in centers:
            for k in [-sector_width, 0, sector_width]:
                density += np.exp(-(phi_fine - (c + k))**2 / (2*phi_sigma**2))

        # Verteilung und Normierung
        distrib = np.cumsum(density)
        distrib /= distrib[-1]

        u = np.linspace(0, 1, n_sector, endpoint=False)
        phi_sector = np.interp(u, distrib, phi_fine)

    # Symmetrie anwenden
    phi_offsets = np.arange(phi_sym) * sector_width
    phi_lin = (phi_sector[None, :] + phi_offsets[:, None]).ravel()

    return np.sort(phi_lin)

def make_rho_phi_grid(n_rho, rhoA_max, rhoB, rho_sigma0, rho_sigmaB, n_phi, phi_sym, phi_sigma, no_rho0):
    """
    - Hilfsfunktion zum Erzeugen der Polarebenen für Funktion make_rho_phi_grid
    - radiale Gauß-Verdichtung bei rho_dense, aber nur in der Nähe der Symmetrie-Winkel 
    """
    # Erzeuge phi-Liste
    phi_lin = make_phi_grid(n_phi, phi_sym, phi_sigma)

    # Berechne Symmetrie-Winkel der phi_Liste
    centers_phi = np.arange(phi_sym) * (2*np.pi / phi_sym)

    rho_phi = np.empty((len(phi_lin), n_rho+1))

    if (phi_sigma is None) or (rho_sigmaB is None):

        # gleichmäßige rho-Verteilung
        for i, phi in enumerate(phi_lin):
            rho_lin = np.linspace(0, rhoA_max, n_rho, endpoint=True)
            # rhoB hinzufügen und Liste sortieren
            rho_lin = np.append(rho_lin, rhoB)
            rho_lin = np.sort(rho_lin)

            rho_phi[i, :] = rho_lin

    else:
        # radiale Gauß-Verdichtung
        rho_fine = np.linspace(0, rhoA_max, 6000, endpoint=True)
        
        for i, phi in enumerate(phi_lin):
            density = np.ones_like(rho_fine)
            # Verdichtung um rho=0
            if rho_sigma0 is not None:
                density += np.exp(-(rho_fine)**2 / (2 * rho_sigma0**2))

            # Verdichtung um rho=rhoB
            # phi-Abstand zu allen Peaks
            delta_phi = np.min(np.abs((phi - centers_phi + np.pi) % (2*np.pi) - np.pi))
                                
            # phi-abhängige Gauß-Breite
            rho_sigma = rho_sigmaB * np.exp(- (delta_phi**2) / (2*phi_sigma**2))

            # Nur hinzufügen, wenn Sigma groß genug
            if rho_sigma > 1e-6:
                density += np.exp(-(rho_fine - rhoB)**2 / (2*rho_sigma**2))

            # Verteilung und Normierung
            distrib = np.cumsum(density)
            distrib /= distrib[-1]

            # Gleichverteilte n_rho Punkte
            u = np.linspace(0, 1, n_rho, endpoint=True)

            rho_lin = np.interp(u, distrib, rho_fine)

            # rhoB hinzufügen und Liste sortieren
            rho_lin = np.append(rho_lin, rhoB)
            rho_lin = np.sort(rho_lin)

            if no_rho0:
                rho_lin = np.delete(rho_lin, 0)

            rho_phi[i, :] = rho_lin

    return rho_phi, phi_lin

def path_grid_2B(k0: list,
                 p: list,
                 n: list,
                 a_coeffs: list,
                 phi_sym: int=1,
                 phi_sigma: float=None,
                 rho_sigma0: float=None,
                 rho_sigmaB: float=None,
                 no_rho0: bool=False,
                 decimals: int=12):
    """
    - verwendet Funktionen make_rho_phi_grid und load_path als Hilfsfunktionen

    - Polarkoordinaten-Gitter entlang der Pfade von Punkt2A und Punkt2B
    - optionale n-fach-Symmetrie
    - optionale Verdichtung um Punkt2A und Punkt2B in Richtung von rho und phi

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
    if n[0] % 2 == 0:
        raise ValueError("n[0]=n_t muss ungerade sein!")
    
    k0 = np.array(k0)

    # Maximum der Koordinatenachsen
    t_max = p[0]            # Punkt 2A
    rhoA_max = p[1]         # Punkt 2A

    # Anzahl der Punkte pro Koordinatenachse
    n_t = n[0]              # Punkt 2A (ungerade)
    n_rhoA = n[1]           # Punkt 2A
    n_phi = n[2]            # Punkt 2A und 2B

    # gleichmäßige Verteilung in t-Richtung
    t_lin = np.linspace(-t_max, t_max, n_t)
    
    # Pfade laden
    rA, T, B, N, kappa = load_path("path_point2A", t_lin)                  # shape: (n_t, 3)
    rB1, rhoB, _ = load_path_point2B("path_point2B", t_lin, a_coeffs, 0)           # shape: (n_t, 3)
    rB2, _ , _ = load_path_point2B("path_point2B", t_lin, a_coeffs, (2/3)*np.pi)   # shape: (n_t, 3)
    rB3, _, _ = load_path_point2B("path_point2B", t_lin, a_coeffs, (4/3)*np.pi)    # shape: (n_t, 3)
 
    # verwende nur t-Werte, bei denen rhoB >= 0 ist
    mask = rhoB >= 0
    rhoB = rhoB[mask]
    t_lin = t_lin[mask]
    rA, B, N = rA[mask,:], B[mask, :], N[mask, :]
    rB1, rB2, rB3 = rB1[mask,:], rB2[mask,:], rB3[mask,:]
        
    # Definition des Gitters
    k_grid = []
    k_grid_center = []
    t_grid_center = []
    rho_lin = []

    for i_t, t in enumerate(t_lin):
        # Verteilung der rho und phi-Werte mit optionaler Symmetrie und Gauß-Dichte in Abhängigkeit von t
        rho_phi, phi_lin = make_rho_phi_grid(n_rhoA, rhoA_max, rhoB[i_t], rho_sigma0, rho_sigmaB, n_phi, phi_sym, phi_sigma, no_rho0)
        for i_phi, phi in enumerate(phi_lin):
            for i_rho, rho in enumerate(rho_phi[i_phi,:]):
                x = rA[i_t, 0] + rho*np.sin(phi)*N[i_t,0] + rho*np.cos(phi)*B[i_t,0]
                y = rA[i_t, 1] + rho*np.sin(phi)*N[i_t,1] + rho*np.cos(phi)*B[i_t,1]
                z = rA[i_t, 2] + rho*np.sin(phi)*N[i_t,2] + rho*np.cos(phi)*B[i_t,2]
                k_grid_center.append(np.array([x,y,z]))
                k_grid.append(np.array([x,y,z])+k0)
                t_grid_center.append(np.array([t, rho, phi]))
                rho_lin.append(rho)
    
    k_grid = np.vstack(k_grid)
    k_grid_center = np.vstack(k_grid_center)
    t_grid_center = np.vstack(t_grid_center)

    print(f"----> mittlere Gitterabstände | Anzahl der Datenpunkte")
    print(f"----> mittlerer Gitterabstand in t-Richtung: {np.mean(np.abs(np.diff(t_lin)))} | N_t={len(t_lin)}")
    print(f"----> mittlerer Gitterabstand in rho-Richtung: {np.mean(np.abs(np.diff(rho_lin)))} | N_rho={len(rho_phi[1,:])}")
    print(f"----> mittlerer Gitterabstand in phi-Richtung: {(180/np.pi)*np.mean(np.abs(np.diff(phi_lin)))}° | N_phi={len(phi_lin)}")
    print(f"----> Anzahl der k-Punkte: {len(k_grid)}")

    # Überprüfe, ob Pfad-Punkte im Gitter enthalten sind:
    def points_in_grid(k_grid_center, rB, tol=1e-9):
        """
        - prüft, ob alle Punkte in rB in k_grid_center enthalten sind.
        """     
        all_found = True
        for pt in rB:
            if not np.any(np.all(np.isclose(k_grid_center, pt, atol=tol), axis=1)):
                all_found = False
                break
        return all_found
    
    found_rB1 = points_in_grid(k_grid_center, rB1)
    found_rB2 = points_in_grid(k_grid_center, rB2)
    found_rB3 = points_in_grid(k_grid_center, rB3)

    if not (found_rB1 and found_rB2 and found_rB3):
        print("\nACHTUNG!!! -- Mindestens ein Pfad ist nicht vollständig im Gitter enthalten!!")

    coords = []
    for k in k_grid:
        kvec = np.round(k, decimals)
        c = str(kvec[0])+" "+str(kvec[1])+" "+str(kvec[2])+" "+str(1.0) # 1.0: gleichmäßige Gewichtung in QE
        coords.append(c) 

    return k_grid, k_grid_center, coords, t_grid_center

# --------------------------------------------------------------------------------------
# Rotation des Gitters
# --------------------------------------------------------------------------------------

def rotation_grid(k_grid_center: list,
                  k0: list,
                  u_axis: list,
                  a_axis: list,
                  decimals: int = 12):
    """
    - Funktion rotiert das Gitter k_grid {x,y,z} im Raum mittels Drehmatrix Rmat
    Args:
        k_grid_center:  Vektoren des Gitters im Koordinatenursprung {x,y,z}
        k0:             Verschiebungsvektor auf Schnittpunkt der Bänder
        u_axis          ursprüngliche Hauptachse des k-Gitters z.B. (0,0,1)
        a_axis:         Zielachse des neuen Gitters z.B. (0,1,1)
        decimals:       legt fest, auf wie viele Nachkommastellen die Pfadvektoren gerundet werden, standart:12
    Return:
        k_grid_rot:         Vektoren des rotierten k-Gitters am Ort der QE-Berechnungen {kx', ky', kz'}
        coords_rot          kpoints Koordinaten für QE des rotierten Gitters
    """
    print(f"----> ursprüngliche Hauptachse: {u_axis}")
    print(f"----> Zielachse des neuen Gitters: {a_axis}")

    def Rmat(axis, angle):
        """
        - Drehmatrix für Drehung um Achse axis um den Winkel angle
        """
        x = axis[0]
        y = axis[1]
        z = axis[2]
        return [[(1-np.cos(angle))*x*x+np.cos(angle)  , (1-np.cos(angle))*y*x-np.sin(angle)*z, (1-np.cos(angle))*z*x+np.sin(angle)*y],
                [(1-np.cos(angle))*x*y+np.sin(angle)*z, (1-np.cos(angle))*y*y+np.cos(angle)  , (1-np.cos(angle))*z*y-np.sin(angle)*x],
                [(1-np.cos(angle))*x*z-np.sin(angle)*y, (1-np.cos(angle))*y*z+np.sin(angle)*x, (1-np.cos(angle))*z*z+np.cos(angle)]]
    
    uvec = np.array(u_axis)
    avec = np.array(a_axis)
    uvec = uvec / np.linalg.norm(uvec) # Normierung
    avec = avec / np.linalg.norm(avec) # Normierung

    # Rotationsachse = Kreuzprodukt
    axis = np.cross(uvec, avec)
    axis = axis / np.linalg.norm(axis) # Normierung
    # Rotationswinkel
    """
    - für Einheitsvektoren gilt: u*v = cos(angle)
    - np.clip dient dazu, um numerische Rundungsfehler auszugleichen, damit es in np.arccos nicht zu nan kommt
    """
    angle = np.arccos(np.clip(np.dot(uvec, avec), -1.0, 1.0))
    # Rotationsmatrix
    R = np.array(Rmat(axis, angle))
    # Drehung des Gitters
    k_grid_rot = (R@k_grid_center.T).T
    k0 = np.array(k0)
    # Verschiebung auf k0
    k_grid_rot = k_grid_rot + k0

    coords_rot = []
    for k in k_grid_rot:
        kvec = np.round(k, decimals)
        c = str(kvec[0])+" "+str(kvec[1])+" "+str(kvec[2])+" "+str(1.0) # 1.0: gleichmäßige Gewichtung
        coords_rot.append(c)  
    return k_grid_rot, coords_rot

# --------------------------------------------------------------------------------------
# Plot des Gitters
# --------------------------------------------------------------------------------------

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
        ax
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

def plot_grid(grid: list,
              k0: list,
              u: list,
              R: float,
              a: list,
              r: float,
              v: list,
              phi_steps: int,
              title: str):
    """
    - verwendet die Funktionen calc_coords und plot_cube als Hilfsfunktionen
 
    - Funktion plottet das grid zusammen mit den Pfadvektoren.

    Args:
        grid:       Vektoren des k-Gitters
        k0:         Verschiebungsvektor auf Schnittpunkt der Bänder
        u:          (ux,uy,uz) Einheitsvektor der Ursprungsgerade, um die gedreht wird
        R:          Radius für den Einheitsvektor u
        a:          (ax, ay, az) - Einheitsvektor für Anfangspfad, der orthogonal zu u liegt
        r:          Radius für den Einheitsvektor a
        v:          (vx, vy, vz) - Verschiebevektor für den Anfangspfad
        phi_steps:  Anzahl der Zwischenpfade zwischen 0° und 180°
        title:      Titel der Abbildung
    """
    k0 = np.array(k0)
    uvec = np.multiply(np.array(u), R)
    vvec = np.array(v)
    vecs, _, _, _, _ = calc_coords(u, R, a, r, v, phi_steps, 3, 0, 360)
    
    fig = plt.figure(figsize=(FIGWIDTH,FIGWIDTH*HFACTOR))
    ax = fig.add_subplot(projection='3d')

    ax.plot([0,uvec[0]], [0,uvec[1]], [0,uvec[2]], "o", color="red")
    ax.plot([0,uvec[0]], [0,uvec[1]], [0,uvec[2]], "-", color="black")
    ax.plot([uvec[0]+vvec[0]], [uvec[1]+vvec[1]], [uvec[2]+vvec[2]], "o", color="red")
    ax.plot([uvec[0],uvec[0]+vvec[0]], [uvec[1],uvec[1]+vvec[1]], [uvec[2],uvec[2]+vvec[2]], "-", color="black")
    ax.plot([k0[0]], [k0[1]], [k0[2]], "o", color="lime")
    ax.plot([uvec[0]+vvec[0], k0[0]], [uvec[1]+vvec[1], k0[1]], [uvec[2]+vvec[2], k0[2]], "-", color="black")

    # Würfel
    plot_cube(ax, (-0.5, 0.5), alpha=0.0, face_color='cyan', edge_color='black', edge_width=0.5)

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

    # k_grid
    ax.scatter(grid[:, 0], grid[:, 1], grid[:, 2], **SCATTER_CONFIG)

    ax.set(xlabel="x", ylabel="y", zlabel="z")
    #ax.axis('off')
    ax.set_box_aspect((1, 1, 1))
    ax.set_xlim(-0.5, 0.5)
    ax.set_ylim(-0.5, 0.5)
    ax.set_zlim(-0.5, 0.5)

    if TITEL:
        plt.title(f"{title}")
    if SAVE:
        plt.savefig(f"{DATEIENNAME}.jpg", bbox_inches=BBOX)
        plt.savefig(f"{DATEIENNAME}.png", bbox_inches=BBOX)
        plt.savefig(f"{DATEIENNAME}.pdf", bbox_inches=BBOX)
    if SHOW:
        plt.show()

# ######################################################################################
# DFT Berechnungen durch Quantum Espresso
# ######################################################################################

# --------------------------------------------------------------------------------------
# Funktionen zum Ändern der Quantum Espresso (QE) config-Dateien
#   - ändern von namelist
#   - ändern der k-Punkte
# --------------------------------------------------------------------------------------

def change_config_namelist(path_in: str,
                           namelist: str,
                           new_value: int):
    """
    - verändert den Wert eines Namelist-Parameters auf einen neuen Wert und speichert die neue in-Datei

    Args:
        path_in:    Pfad der in-Datei von QE
        namelist:   Namelist-Parameter
                    z.B."ecutwfc"
        new_value:  neuer Wert des Namelist-Parameters
                    z.B. 12
    """
    filename = path_in.split("/")[-1]
    file = open(path_in, "r")
    file_lines = file.readlines()
    file.close()

    new_lines = []
    for line in file_lines:
        if re.search(namelist, line):
            part = line.split("= ")
            new_line = str(part[0])+"= "+str(new_value)+"\n"
            print(f"{line} > {new_line}")
            new_lines.append(new_line)
            continue       
        new_lines.append(line)

    tmp_file_path = os.path.join(config.path_tmp(), filename)
    new_file = open(tmp_file_path, 'w')
    for line in new_lines:
        new_file.write(line)
    new_file.close()
    shutil.copyfile(tmp_file_path, path_in)


def change_config_kpoints(path_in: str,
                          new_values: list,
                          card: str = "K_POINTS {crystal_b}"):
    """
    - Modifikation der Funktion change_config_card, speziell für um eine Liste von k-Punkten zu ändern
    - verändert den Wert eines card-Parameters auf eine Liste neuer Werte und speichert die neue in-Datei

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

# --------------------------------------------------------------------------------------
# Berechnungen der Bandenergien
# --------------------------------------------------------------------------------------

def model_calc(coords: list,
               p_str: str,
               n_str: str,
               datlabel: str,
               enable_logging: bool = True):
    """
    - verwendet die Funktion change_config_kpoints als Hilfsfunktion

    - QE wird auf dem Gitter ausgeführt (analog zu qe_thz_calc)
    - zusätzlich wird die scf-xml-Datei im tmp-Ordner gespeichert
    - optional werden die Zeitstempel der Rechnung in der Text.Datei log gespeichert
    - ausführliche Kommentare siehe Code

    Args:
        coords:         Liste der kpoints Koordinaten für Quantum Espresso
        p_str:          halbe Kantenlängen (p1, p2, p2) des Gitters als string (für Dateienpfad)
        n_str:          Anzahl der Datenpunkte (n1, n2, n3) als string (für Dateienpfad)
        datlabel:       Label in Dateienname
        enable_logging: Sollen das log und die print-Ausgabe für die Rechenzeiten aktiv sein?
    """
    # Laden der Ordner-Struktur
    suffix = config.suffix(datlabel, p_str, n_str)
    bt2_working_directory = config.bt2_working_directory # main_directory/tmp_prefix
    qe_working_directory = config.qe_working_directory # main_directory/prefix
    path_scf_in = config.path_scf_in() # main_directory/qe_working_directory/prefix.scf.in
    path_scf_out = config.path_scf_out() # main_directory/qe_working_directory/prefix.scf.out
    path_nscf_in = config.path_nscf_in() # main_directory/qe_working_directory/prefix.nscf.in
    path_nscf_out = config.path_nscf_out() # main_directory/qe_working_directory/.nscf.out
    path_tmp_directory = config.path_tmp_directory(datlabel, p_str, n_str) # main_directory/prefix_tmp/suffix
    path_out_directory = config.path_out_directory(datlabel, p_str, n_str) # main_directory/prefix_out/suffix
    path_COPY_directory = config.path_COPY_directory() # main_directory/tmp_prefix_COPY
    path_xml = config.path_xml(datlabel, p_str, n_str) # main_directory/prefix_tmp/suffix/prefix.xml
    path_scf_xml = config.path_scf_xml_() # main_directory/tmp_prefix_COPY/prefix.xml
    path_scf_xml_COPY_directory = config.path_scf_xml_COPY_directory(datlabel, p_str, n_str) # main_directory/prefix_out/suffix/scf
    path_nscf_xml_COPY_directory = config.path_nscf_xml_COPY_directory(datlabel, p_str, n_str) # main_directory/prefix_out/suffix/scf/prefix.mxl
    path_log = config.path_log() # main_directory/qe_working_directory/log/log
    
    # log Funktion und Start des Log zum Speichern der Rechenzeiten
    start_time = None
    log_file = None
    def log(message, log_file):
        """ Zur Erstellung des Log """
        nonlocal start_time
        if enable_logging and start_time is not None:
            elapsed = time.time() - start_time
            full_message = f"----> {elapsed:.2f} s --- {message}"
            print(full_message)
            if log_file:
                print(full_message, file=log_file)
            start_time = time.time()
    
    if enable_logging:
        start_time_0 = time.time()
        start_time = time.time()
        log_file = open(path_log, "w")
        print(f"---->{suffix}", file=log_file)

    # führe scf-Rechnung mit Konfigurationsdatei aus Ordner prefix aus, falls diese noch nicht durchgeführt wurde 
    # kopiere die Daten der scf-Rechnung aus tmp_prefix nach tmp_prefix_COPY
    if not os.path.exists(bt2_working_directory):
        os.makedirs(bt2_working_directory)
        log("scf-Rechnung wird durchgeführt", log_file)

        num_cores = config.num_cores
        num_pool = config.num_pool
        if num_cores > 1:
            print(f"- Parallele Berechnung mit {num_cores} Kernen")
            process_scf = subprocess.Popen(f"cd {qe_working_directory} && mpirun -np {num_cores} pw.x -npool {num_pool} -in {path_scf_in} > {path_scf_out}", shell=True, stdout=subprocess.DEVNULL)
        else:
            process_scf = subprocess.Popen(f"cd {qe_working_directory} && pw.x -in {path_scf_in} > {path_scf_out}", shell=True, stdout=subprocess.DEVNULL)

        process_scf.wait()
        config.copy_folder(bt2_working_directory, path_COPY_directory)

    # kopiere die xml-Datei der scf-Rechnung aus tmp_prefix_COPY nach prefix_out/suffix/scf
    shutil.copy(path_scf_xml, path_scf_xml_COPY_directory)       
    log("scf-Rechnung DONE", log_file)
    
    # die k-Punkte der prefix.nscf.in Datei im Ordner prefix werden angepasst
    change_config_kpoints(path_nscf_in, coords)
    print("----> k-Punkte geändert")

    # führe die nscf-Rechnung aus
    print("----> nscf-Rechnung wird durchgeführt")

    num_cores = config.num_cores
    num_pool = config.num_pool
    if num_cores > 1:
        print(f"- Parallele Berechnung mit {num_cores} Kernen")
        process_nscf = subprocess.Popen(f"cd {qe_working_directory} && mpirun -np {num_cores} pw.x -npool {num_pool} -in {path_nscf_in} > {path_nscf_out}", shell=True, stdout=subprocess.DEVNULL)
    else:
        process_nscf = subprocess.Popen(f"cd {qe_working_directory} && pw.x -in {path_nscf_in} > {path_nscf_out}", shell=True, stdout=subprocess.DEVNULL)

    process_nscf.wait()
    log("nscf-Rechnung DONE", log_file)

    # kopiere Daten:
    # - Daten der nscf-Rechnung aus tmp_prefix nach prefix_tmp/suffix
    # - alle Daten des Konfigurationsordners prefix nach prefix_out/suffix
    # - xml-Datei der nscf-Rechnung von prefix_tmp/suffix nach prefix_out/suffix/nscf
    config.copy_folder(bt2_working_directory, path_tmp_directory)
    config.copy_folder(qe_working_directory, path_out_directory)
    shutil.copy(path_xml, path_nscf_xml_COPY_directory)
    
    # lösche alle (nscf)-Dateien im tmp_prefix Ordner
    config.delete_folder(bt2_working_directory)

    # kopiere alle scf-Dateien von tmp_prefix_COPY nach tmp_prefix
    config.copy_folder(path_COPY_directory, bt2_working_directory)
    log("Kopieren DONE", log_file)

    if enable_logging and log_file:
        print("----> %.2f s --- Calculation DONE" % (time.time() - start_time_0))
        print("----> %.2f s --- Calculation DONE" % (time.time() - start_time_0), file=log_file)
        print("")     
        log_file.close()

# --------------------------------------------------------------------------------------
# Berechnungen der Matrix-Impuls-Elemente
# --------------------------------------------------------------------------------------

def calc_mme(p_str: str,
             n_str: str,
             datlabel: str,
             enable_logging: bool = True):
    """
    - verwendet Funktion change_config_namelist als Hilfsfunktion

    - Funktion setzt voraus, dass bereits scf als auch nscf - Rechnungen durchgeführt wurden
    - Funktion führt bands.x von QE mithilfe der Confgi-Datei prefix_bands_x.in aus

    Struktur von bands_x.in:

    &bands
     prefix = 'prefix',
     outdir = '../prefix_tmp/suffix'
     lp = .true.
     filp = 'prefix_p_avg.dat'
     lsym = .false.
     /

    Args:
        p_str:          halbe Kantenlängen (p1, p2, p2) des Gitters als string (für Dateienpfad)
        n_str:          Anzahl der Datenpunkte (n1, n2, n3) als string (für Dateienpfad)
        datlabel:       Label in Dateienname
        enable_logging: Sollen das log und die print-Ausgabe für die Rechenzeiten aktiv sein?
    """
    # Laden der Ordner-Struktur
    suffix = config.suffix(datlabel, p_str, n_str)
    qe_working_directory = config.qe_working_directory
    path_bands_x_in = config.path_bands_x_in()
    path_bands_x_out = config.path_bands_x_out()
    path_out_directory = config.path_out_directory(datlabel, p_str, n_str)
    path_log = config.path_log()+"_vme_calc"
    path_scf_xml_COPY_directory = config.path_scf_xml_COPY_directory(datlabel, p_str, n_str)
    path_nscf_xml_COPY_directory = config.path_nscf_xml_COPY_directory(datlabel, p_str, n_str)
    path_scf_in = config.path_scf_in()
    path_scf_in_out_directory = config.path_scf_in_out_directory(datlabel, p_str, n_str)
    path_nscf_in = config.path_nscf_in()
    path_nscf_in_out_directory = config.path_nscf_in_out_directory(datlabel, p_str, n_str)

    # log Funktion und Start des Log zum Speichern der Rechenzeiten
    start_time = None
    log_file = None
    def log(message, log_file):
        """ Zur Erstellung des Log """
        nonlocal start_time
        if enable_logging and start_time is not None:
            elapsed = time.time() - start_time
            full_message = f"----> {elapsed:.2f} s --- {message}"
            print(full_message)
            if log_file:
                print(full_message, file=log_file)
            start_time = time.time()
    
    if enable_logging:
        start_time_0 = time.time()
        start_time = time.time()
        log_file = open(path_log, "w")
        print(f"---->{suffix}", file=log_file)

    # teste, ob xml-Dateien der scf und nscf Rechnungen im Ordner prefix_out/suffix/scf und prefix_out/suffix/nscf vorliegen. - das soll abfragen, ob beide Berechnungen bereits durchgeführt wurden
    if not (os.path.exists(path_scf_xml_COPY_directory) and os.path.exists(path_nscf_xml_COPY_directory)):
        raise ValueError("Die xml-Dateien der scf und nscf-Rechnungen liegen nicht vor. Bitte diese Rechnungen vorher ausführen!")
    
    # Prüfe, ob die scf und nscf-Dateien in den Ordnern prefix und prefix_out/suffix übereinstimmen
    if not filecmp.cmp(path_scf_in, path_scf_in_out_directory):
        raise ValueError(f"Die scf-Dateien der Ordner {path_scf_in} und {path_scf_in_out_directory} stimmen nicht überein!")
    if not filecmp.cmp(path_nscf_in, path_nscf_in_out_directory):
        raise ValueError(f"Die nscf-Dateien der Ordner {path_nscf_in} und {path_nscf_in_out_directory} stimmen nicht überein!")

    # ändere outdir Konfiguration der bands_x.in-Datei
    change_config_namelist(path_bands_x_in, "outdir", f"'../{config.prefix}_tmp/{suffix}'")
    # ändere filp-Name in bands_x.in-Datei
    change_config_namelist(path_bands_x_in, "filp", f"'{config.prefix}_p_avg.dat'")

    # führe bands_x Rechnung aus
    print("----> bands_x-Rechnung wird durchgeführt")

    num_cores = config.num_cores
    num_pool = config.num_pool
    if num_cores > 1:
        print(f"- Parallele Berechnung mit {num_cores} Kernen")
        process_bands_x = subprocess.Popen(f"cd {qe_working_directory} && mpirun -np {num_cores} pw.x -npool {num_pool} -in {path_bands_x_in} > {path_bands_x_out}", shell=True, stdout=subprocess.DEVNULL)
    else:
        process_bands_x = subprocess.Popen(f"cd {qe_working_directory} && pw.x -in {path_bands_x_in} > {path_bands_x_out}", shell=True, stdout=subprocess.DEVNULL)
    
    process_bands_x.wait()
    log("bands_x-Rechnung DONE", log_file)

    # kopiere Daten des Konfigurationsordners prefix nach prefix_out/suffix
    config.copy_folder(qe_working_directory, path_out_directory)

    if enable_logging and log_file:
        print("----> %.2f s --- Calculation DONE" % (time.time() - start_time_0))
        print("----> %.2f s --- Calculation DONE" % (time.time() - start_time_0), file=log_file)
        print("")     
        log_file.close()

# ######################################################################################
# Koordinatentransformationen
# ######################################################################################

def scale_grid(df: list,
               k_grid_center: list,
               p: list,
               grid_type: str):
    """
    - Funktion skaliert das Gitter im Zentrum {x,y,z} auf das Intervall [-1,1]
    - dabei wird die längste Achse verwendet (np.max(p))
    Args:
        df:             Pandas Dataframe
        k_grid_center:  Vektoren des Gitters im Koordinatenursprung {x,y,z}
        p:              Kantenlängen (je nach grid_type)
        grid_type:      definiert Form des Gitters (regular oder cylindrical)
    Return:
        df:             das um die neuen Koordinaten erweiterte Dataframe
    """
    if grid_type == "regular":
        p_max = np.max(p) # max([x_max, y_max, z_max])
    elif grid_type == "cylindrical":
        p_max = np.max(p) # max([Radius, 0, halbe Höhe in Richtung z_axis])
    else:
        raise ValueError(f"Folgende grid_type sind momentan möglich:\n regular\n cylindrical")
    
    x_scaled = k_grid_center[:, 0]/p_max
    y_scaled = k_grid_center[:, 1]/p_max
    z_scaled = k_grid_center[:, 2]/p_max

    df.insert(0, "x_scaled", x_scaled)
    df.insert(1, "y_scaled", y_scaled)
    df.insert(2, "z_scaled", z_scaled)
    return df

def path_transformation(df: list,
                        a_coeffs: list,
                        b_coeffs: list,
                        modeltype_path: str,
                        coord_basis: str,
                        bounds: list,
                        tol: float = 1e-7,
                        xatol: float = 1e-8):
    """
    - verwendet Funktionen aus qe_model_pathmodels.py

    - Funktion tranformiert das Gitter im Zentrum {x,y,z} oder {x_scaled,y_scaled,z_scaled} auf die Koordinaten {t,rho,phi} entlang des Pfades r(t)
    - gilt nicht für den Pfad 2B. Das Koordinatensystem bezieht sich immer auf Punkt 2A

    Args:
        df:                 Pandas Dataframe
        a_coeffs, b_coeffs: Koeffizienten der quadratischen Raumkurve
        modeltype_path:     Modell des Pfades der Schnittpunktumgebung
        coord_basis:        Koordinatensystem im Zentrum, das transformiert wird. Bislang:
                            "xyz": das nicht-skalierte Koordinatensystem im Zentrum
                            "xyz_scaled": das skalierte Koordniatensystem im Zentrum 
        bounds:             Intervall für t, in dem minimize_scalar nach dem Minmum sucht: (t_min, t_max)
        tol:                Toleranz für Nichtorthogonalität von Versatz- und Tangentenvektor
        xatol:              Toleranz in der minimize_scalar Funktion
    Return:
        df:                 das um die neuen Koordinaten erweiterte Dataframe   
    """
    # Lade Koordinatenachsen, auf dem der Pfad angefittet wurde
    if coord_basis == "xyz":
        axes = ("x", "y", "z")
    elif coord_basis == "xyz_scaled":
        axes = ("x_scaled", "y_scaled", "z_scaled")
    else:
        raise ValueError(f"coord_basis={coord_basis}; Falsches Basis-Koordinatensystem für Pfad-Transformation! Verfügbar:\n xyz\n xyz_scaled")
    
    x_ax, y_ax, z_ax = df[f"{axes[0]}"], df[f"{axes[1]}"], df[f"{axes[2]}"]

    # Berechne neue Koordinaten und füge sie dem Dataframe hinzu
    if modeltype_path=="path_point1":
        t = pathmodels.find_t_for_xyz(x_ax, y_ax, z_ax, pathmodels.r_point1, bounds, xatol, a=a_coeffs, b=b_coeffs)
        r, T, B, N, kappa = load_path(modeltype_path, t, a_coeffs, b_coeffs)
        V = pathmodels.v_vector(x_ax, y_ax, z_ax, r)
    elif modeltype_path=="path_point2A":
        t = pathmodels.find_t_for_xyz(x_ax, y_ax, z_ax, pathmodels.r_point2A, bounds, xatol)
        r, T, B, N, kappa = load_path(modeltype_path, t)
        V = pathmodels.v_vector(x_ax, y_ax, z_ax, r)
    elif modeltype_path=="path_point3":
        t = pathmodels.find_t_for_xyz(x_ax, y_ax, z_ax, pathmodels.r_point3, bounds, xatol)     
        r, T, B, N, kappa = load_path(modeltype_path, t)
        V = pathmodels.v_vector(x_ax, y_ax, z_ax, r)
    elif modeltype_path=="path_point1_center":
        t = pathmodels.find_t_for_xyz(x_ax, y_ax, z_ax, pathmodels.r_point1_center, bounds, xatol)
        r, T, B, N, kappa = load_path(modeltype_path, t)
        V = pathmodels.v_vector(x_ax, y_ax, z_ax, r)
    else:
        raise ValueError(f"Falscher Parameter: modeltype_path={modeltype_path}; verfügbar:\n path_point1 \n path_point2A \n path_point3 \n path_point1_center")

    t, rho, phi = pathmodels.new_coordinates(t, T, N, B, V, kappa, tol)

    # 1. Bestehende Spalten umbenennen und neue hinzufügen
    df = df.rename(columns={"t": "t_def", "rho": "rho_def", "phi": "phi_def"})

    df.insert(0, "t", t)
    df.insert(1, "rho", rho)
    df.insert(2, "phi", phi)
    return df

# ######################################################################################
# Analyse und Anpassung des pandas-Dataframes
# ######################################################################################

# --------------------------------------------------------------------------------------
# Auslesen der Ausgabedateien von QE
# --------------------------------------------------------------------------------------

def model_xml_to_df(k0: list,
                    p_str: str,
                    n_str: str,
                    k_grid_center: list,
                    datlabel: str,
                    bandnumbers: list = None,
                    t_grid: list = None,
                    v_grid: list = None):
    """
    - lädt Daten aus der xml-Datei von QE und die Vektoren des k-Gitters im Koordinatenursprung
    - Funktion vergleicht fermi-Energien zwischen scf-Rechnung und nscf-Rechnung
    - falls Fermi-Energien unterschiedlich, wird die Fermi-Energie der scf-Rechnung übernommen

    Args:
        k0:             Verschiebungsvektor auf Schnittpunkt der Bänder
        p_str:          halbe Kantenlängen (p1, p2, p2) des Gitters als string (für Dateienpfad)
        n_str:          Anzahl der Datenpunkte (n1, n2, n3) als string (für Dateienpfad)
        k_grid_center:  Vektoren des Gitters im Koordinatenursprung {x,y,z}
        datlabel:       (str) datlabel des ersten Dataframes
        bandnumners:    Auswahl der Bänder.
                        Werden genau zwei Bänder gewählt, wird die Differenz berechnet.
        t_grid:         Vektoren des Gitters im Pfad-Koordinatensystem {t,rho,phi}
        v_grid:         Vektoren der Komponenten {t, vN, vB}
    Return:
        df:             unveränderte Daten der xml-Datei als Dataframe, inklusive der Gitter im Zentrum und k0
        new:            Dataframe nach Auswahl bestimmter Bänder und Umrechnung in eV
    """
    path_scf_xml = config.path_scf_xml_copy(datlabel, p_str, n_str)
    path_nscf_xml = config.path_nscf_xml_copy(datlabel, p_str, n_str)
    
    tree = ET.parse(path_nscf_xml)
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
    #print(df.shape[0])
    
    # Füge kx0-Vektoren hinzu
    df["kx0"] = [k0[0]] * df.shape[0]
    df["ky0"] = [k0[1]] * df.shape[0]
    df["kz0"] = [k0[2]] * df.shape[0]

    # Füge Fermi-Energie hinzu
    nscf_fermi_node = root.find("output/band_structure/fermi_energy")
    nscf_fermi_energy = float(nscf_fermi_node.text)

    tree2 = ET.parse(path_scf_xml)
    root2 = tree2.getroot()
    scf_fermi_node = root2.find("output/band_structure/fermi_energy")
    scf_fermi_energy = float(scf_fermi_node.text)

    if not nscf_fermi_energy == scf_fermi_energy:
        print("----> ACHTUNG: Fermi-Energien von scf-Rechnung und nscf-Rechnung sind nicht identisch:")
        print(f"----> scf:  {scf_fermi_energy}")
        print(f"----> nscf: {nscf_fermi_energy}")
        print("----> übernehme Fermi-Energie der scf-Rechnung")
        fermi_energy = scf_fermi_energy
    else:
        fermi_energy = nscf_fermi_energy

    df["fermi_energy"] = [fermi_energy] * df.shape[0]

    # Füge Vektoren des k-Gitters im Koordinatenursprung hinzu
    df["x"] = k_grid_center[:, 0]
    df["y"] = k_grid_center[:, 1]
    df["z"] = k_grid_center[:, 2]

    # Füge Pfad-Koordinatensystem hinzu
    if t_grid is not None:
        df["t"] = t_grid[:, 0]
        df["rho"] = t_grid[:, 1]
        df["phi"] = t_grid[:, 2]
    else:
        df["t"] = np.ones_like(df["x"])
        df["rho"] = np.ones_like(df["x"])
        df["phi"] = np.ones_like(df["x"])
    
    # Füge V-Vektoren des Pfad-Koordinatensystems hinzu falls vorhanden
    if v_grid is not None:
        df["vN"] = v_grid[:, 1]
        df["vB"] = v_grid[:, 2]
    else:
        df["vN"] = np.ones_like(df["x"])
        df["vB"] = np.ones_like(df["x"])

    # -------------------------------------------------------------------

    # Erzeuge Dataframe
    if bandnumbers is not None:
        new = df[["x", "y", "z", "kx", "ky", "kz", "kx0", "ky0", "kz0", "t", "rho", "phi", "vN", "vB","fermi_energy"]].copy()
        for i in range(len(bandnumbers)):
                new[f"band{i}"] = (df[f"band{bandnumbers[i]}"] - df["fermi_energy"])/units.eV
        
        new["fermi_energy"] = new["fermi_energy"]/units.eV

    if bandnumbers is not None and len(bandnumbers) == 2:
        new["diff"] = abs(new["band0"] - new["band1"])
    
    pd.options.mode.chained_assignment = None # Deaktiviert Index Warnung von Pandas
    new['index1'] = new.index # füge Indizes der Peaks als Spalte hinzu
    return df, new

def mme_to_df(p_str: str,
              n_str: str,
              datlabel: str):
    """
    - Funktion liest bestimmte Betragsquadrate der Impuls-Matrix Elemente(PME) aus der filp-Datei von bands.x aus und gibt sie zusammen mit den k-Koordinaten als Pandas-Dataframe zurück
    - die Betragsquadrate der Impuls-Matrix-Elemente sind:
        - |<n|p|m>|**2, wobei n=vorletztes Band, m=letztes Band
        - d.h. nur die k-Punkte werden berücksichtigt, bei denen En unterhalb der Fermi-Energie und Em oberhalb der Fermi-Energie liegt
    - die Vorraussetzung dieser Funktion ist also, dass die interessanten Bänder nahe der Fermi-Energie die beiden höchsten Bänder in den Daten von QE sind
    
    Args: 
        p_str:          halbe Kantenlängen (p1, p2, p2) des Gitters als string (für Dateienpfad)
        n_str:          Anzahl der Datenpunkte (n1, n2, n3) als string (für Dateienpfad)
        datlabel:       Label in Dateienname
    Return:
        df:     Pandas Dataframe (siehe oben)
    """
    # Laden der Ordner-Struktur
    path_p_avg = config.path_p_avg_copy(datlabel, p_str, n_str) # main_directory/prefix_out/suffix/prefix_p_avg.dat

    print(f"Pfad der p_avg-Datei: {path_p_avg}")
    print()
    data = []
    # Extrahieren der Zahlen für jede Zeile des Datafiles
    with open(path_p_avg, 'r') as txt_file:
        for line in txt_file:
            # ersetze Zeichen, dient dazu die erste Zeile richtig einzulesen
            line = line.replace("=", " ").replace(",", " ")
            parts = line.split()
            numbers = []
            for p in parts:
                # alles außer Zahlen wird ignoriert.
                try:
                    numbers.append(float(p))
                except ValueError:
                    continue
            data.append(numbers)

    nbnd = int(data[0][0])
    print(f"Anzahl der Bänder: {nbnd}")

    k_points = [] # k-Punkte
    v_bands = [] # Nummern der äußeren Valenzbänder
    indis_1 = [] # Zeilennummern mit 1er-Zeilen
    indis_2 = [] # Zeilennummern mit 2er-Zeilen
    indis_3 = [] # Zeilennummern mit 3er-Zeilen
    for i, line in enumerate(data):
        # prüft, ob mindestens ein Elemet der Zeile > 1 ist
        if any(n>=1 for n in line):
            # prüft, ob Länge der Liste genau 4 ist
            if len(line) == 4:
                k_points.append(line[0:3])
                v_bands.append(line[3])
            elif line[0] == 1.0:
                indis_1.append(i)
            elif line[0] == 2.0:
                indis_2.append(i)
            elif line[0] == 3.0:
                indis_3.append(i)

    nks = len(k_points)
    print(f"Anzahl der k-Punkte: {nks}")

    # Prüfe ob die Länge der Listen genauso lange wie die Anzahl der k-Punkte ist
    if not (len(k_points) == len(v_bands) == len(indis_1) == len(indis_2) == len(indis_3)):
        raise ValueError("Nicht alle k-Punkte extrahiert. Irgendwo ist ein Fehler.")

    # Extrahiere alle interessanten Matrix-Elemte
    px_list = []
    py_list = []
    pz_list = []
    kx_list = []
    ky_list = []
    kz_list = []
    for i in range(nks):
        # nehme nur Einträge mit einem Leitungsband
        if v_bands[i] == nbnd-1:
            # Zeilen der Blöcke "1","2","3"
            px_data = data[indis_1[i]+1: indis_2[i]]
            py_data = data[indis_2[i]+1: indis_3[i]]
            if i == nks: # Beim letzten Block bis zum letzten Eintrag
                pz_data = data[indis_3[i]+1: len(data)]
            else:
                pz_data = data[indis_3[i]+1: indis_1[i+1]-1]
            # alle Zahlen in eine Liste
            px_numbers = np.concatenate(px_data)
            py_numbers = np.concatenate(py_data)
            pz_numbers = np.concatenate(pz_data)
            # Wähle letzten Eintrag
            px_list.append(px_numbers[-1])
            py_list.append(py_numbers[-1])
            pz_list.append(pz_numbers[-1])
            # k-Punkte in Listen
            k_point = k_points[i]
            kx_list.append(k_point[0])
            ky_list.append(k_point[1])
            kz_list.append(k_point[2])

    print(f"Anzahl der k-Punkte mit einem einzigen Leitungsband: {len(kx_list)}")

    # Erstelle pandas-Dataframe
    df = pd.DataFrame({
        "kx": kx_list,
        "ky": ky_list,
        "kz": kz_list,
        "px": px_list,
        "py": py_list,
        "pz": pz_list,
    })

    return df

# --------------------------------------------------------------------------------------
# Berechnung statistischer Größen für die Matrix-Impuls-Elemente
# --------------------------------------------------------------------------------------

def mme_statistics(df: list,
                   df_mme: list,
                   merge_decimals: int=None):
    """
    - Funktion berechnet statische Werte der Matrix-Impuls-Elemente von QE
        - Standardabweichung
        - Erwartungswert
        - Variationskoeffizient
        - Spannweite
        - relativer maximaler Fehler
    - Wenn merge_decimals nicht None, werden die Koordinaten kx,ky,kz beider Dataframes miteinander verglichen und die Energiewerte den Matrix-Impuls-Elementen zugeordnet. Dann werden die statistischen Werte nur für jede Punkte berechnet, bei denen die Zuordnung erfolgreich war. Dies dient dazu, die statischen Werte nur für den THz-aktiven Bereich zu bestimmen, wenn df vorher darauf zugeschnitten wird.
    Args:
        df:                 pandas Dataframe der Energie-Berechnung
        df_mme:             pandas Dataframe der Matrix-Impuls-Elemente
        merge_decimals:     Anzahl der Nachkommastellen, auf denen die Dataframes miteinander verglichen werden
    """
    px = df_mme["px"]
    py = df_mme["py"]
    pz = df_mme["pz"]

    # Standardabweichung
    px_std = np.std(px)
    py_std = np.std(py)
    pz_std = np.std(pz)

    print(f"----> Standardabweichung (px,py,pz)")
    print(px_std)
    print(py_std)
    print(pz_std)
    print()

    # Erwartungswert
    px_mean = np.mean(px)
    py_mean = np.mean(py)
    pz_mean = np.mean(pz)

    print("----> Erwartungswert (px,py,pz)")
    print(px_mean)
    print(py_mean)
    print(pz_mean)
    print()

    # Variationskoeffizient
    px_var = px_std/px_mean
    py_var = py_std/py_mean
    pz_var = pz_std/pz_mean

    print("----> Variationskoeffizient (px,py,pz)")
    print(px_var)
    print(py_var)
    print(pz_var)
    print()

    # Spannweite
    px_spann = np.max(px)-np.min(px)
    py_spann = np.max(py)-np.min(py)
    pz_spann = np.max(pz)-np.min(pz)

    print("----> Spannweite (px,py,pz)")
    print(px_spann)
    print(py_spann)
    print(pz_spann)
    print()

    # relativer maximaler Fehler
    px_rel = np.max([ np.abs(np.max(px)-px_mean) , np.abs(np.min(px)-px_mean) ]) / px_mean
    py_rel = np.max([ np.abs(np.max(py)-py_mean) , np.abs(np.min(py)-py_mean) ]) / py_mean
    pz_rel = np.max([ np.abs(np.max(pz)-pz_mean) , np.abs(np.min(pz)-pz_mean) ]) / pz_mean

    print("----> relativer Maximalfehler (px,py,pz)")
    print(px_rel)
    print(py_rel)
    print(pz_rel)
    print()

    if merge_decimals is not None:
        print("")
        print("---->  Zusammenfügen beider Dataframes df, df_mme")
        decimals = merge_decimals
        cols = ["kx", "ky", "kz"]
        df1 = df.copy()
        df2 = df_mme.copy()

        for col in cols:
            df1[f"{col}_tmp"] = df1[col].round(decimals)
            df2[f"{col}_tmp"] = df2[col].round(decimals)
        
        df_merged = pd.merge(df1, df2, on=["kx_tmp", "ky_tmp", "kz_tmp"])
        df_merged = df_merged.drop(columns=["kx_tmp", "ky_tmp", "kz_tmp"])
        print(f"---->  Zusammenfügen erfolgreich für {len(df_merged)} von {len(df_mme)} Zeilen.")

        px = df_merged["px"]
        py = df_merged["py"]
        pz = df_merged["pz"]

        # Standardabweichung
        px_std = np.std(px)
        py_std = np.std(py)
        pz_std = np.std(pz)

        print(f"----> Standardabweichung (px,py,pz)")
        print(px_std)
        print(py_std)
        print(pz_std)
        print()

        # Erwartungswert
        px_mean = np.mean(px)
        py_mean = np.mean(py)
        pz_mean = np.mean(pz)

        print("----> Erwartungswert (px,py,pz)")
        print(px_mean)
        print(py_mean)
        print(pz_mean)
        print()

        # Variationskoeffizient
        px_var = px_std/px_mean
        py_var = py_std/py_mean
        pz_var = pz_std/pz_mean

        print("----> Variationskoeffizient (px,py,pz)")
        print(px_var)
        print(py_var)
        print(pz_var)
        print()

        # Spannweite
        px_spann = np.max(px)-np.min(px)
        py_spann = np.max(py)-np.min(py)
        pz_spann = np.max(pz)-np.min(pz)

        print("----> Spannweite (px,py,pz)")
        print(px_spann)
        print(py_spann)
        print(pz_spann)
        print()

        # Maximaler relativer Fehler
        px_rel = np.max([ np.abs(np.max(px)-px_mean) , np.abs(np.min(px)-px_mean) ]) / px_mean
        py_rel = np.max([ np.abs(np.max(py)-py_mean) , np.abs(np.min(py)-py_mean) ]) / py_mean
        pz_rel = np.max([ np.abs(np.max(pz)-pz_mean) , np.abs(np.min(pz)-pz_mean) ]) / pz_mean

        print("----> Maximaler relativer Fehler (px,py,pz)")
        print(px_rel)
        print(py_rel)
        print(pz_rel)   
        print()

# --------------------------------------------------------------------------------------
# Berechnung des Schnittpunktes
# --------------------------------------------------------------------------------------

def model_find_intersect(df: list,
                         point: str):
    """
    - Funktion findet den Schnittpunkt der Bänder in der Nähe der Fermi-Energie
    - die Summe der Energien und der Differenz wird summiert und der kleinste Eintrag wird zurückgegeben

    Args:
        df:     pandas Dataframe der Energie-Berechnung
        point:  Um welchen Schnittpunkt handelt es sich?
    """
    df_copy = df.copy()

    if point == "point_1":
        df_copy = df_copy.loc[(df_copy["ky"] == df_copy["kz"])] # punkt 1
    elif point == "point_2A":
        df_copy = df_copy.loc[(df_copy["ky"] == df_copy["kz"]) & (df_copy["kx"] == df_copy["ky"])] # punkt 2A
    elif point == "point_2B":
        df_copy = df_copy.loc[(df_copy["kx"] == df_copy["ky"])] # punkt 2B
    elif point == "point_3":
        df_copy = df_copy.loc[(df_copy["ky"] == 0.5) & (df_copy["ky"] == 0.5)] # punkt 3
    else:
        raise ValueError(f"point={point}; Verfügbar:\n point_1\n point_2A\n point_2B\n point_3")

    df_energy = df_copy[["band0", "band1", "diff"]].copy()
    #df_energy = df_energy.loc[(df_energy["band0"] < 0) & (df_energy["band1"] > 0)]
    
    # finde Index, bei dem die Summe der Energien am kleinsten ist
    index_min = df_energy.abs().sum(axis=1).idxmin()

    print("Schnittpunkt:")
    print(df.iloc[index_min].to_string(float_format='{:.15f}'.format))

# --------------------------------------------------------------------------------------
# Hauptkomponentenanalyse
# --------------------------------------------------------------------------------------

def model_gradient(df: list,
                   energy: str):
    """
    - Funktion generiert ein 3D-Gitter aus der gewählten Spalte energy des Dataframes
    - dann wird mithilfe von numpy der Gradient berechnet und dem Dataframe als Spalten dEdx_energy, dEdy_energy und dEdz_energy hinzugefügt
    - außerdem wird die Gradienlänge berechnet und hinzugefügt: grad_energy

    Args:
        df:         Pandas Dataframe aus der xml-Datei
        energy:     Spalten-Label der Energie z.B. "band0" oder "diff"
    Return:
        df_neu:  das mit den Gradientbeiträgen erweiterte Pandas Dataframe
    """

    x_vals = np.sort(df["x"].unique())
    y_vals = np.sort(df["y"].unique())
    z_vals = np.sort(df["z"].unique())

    # Sortiere Dataframe
    df_neu = df.sort_values(["x", "y", "z"])
    
    # Erzeuge Energie-Grid von band
    E_grid = df_neu[f"{energy}"].to_numpy().reshape(len(x_vals),len(y_vals),len(z_vals))

    # Berechnung des Gradienten (gleichmäßiger Punkteabstand)
    dEdx, dEdy, dEdz = np.gradient(E_grid, x_vals, y_vals, z_vals)

    # füge Gradientenbeiträge dem Dataframe hinzu
    df_neu[f"dEdx_{energy}"] = dEdx.ravel()
    df_neu[f"dEdy_{energy}"] = dEdy.ravel()
    df_neu[f"dEdz_{energy}"] = dEdz.ravel()

    # Berechnung der Gradientenlängen und hinzufügen zum Dataframe
    df_neu[f"grad_{energy}"] = np.sqrt(df_neu[f"dEdx_{energy}"]**2 + df_neu[f"dEdy_{energy}"]**2 + df_neu[f"dEdz_{energy}"]**2)
    return df_neu

def model_mean_curv(df: list,
                    energy: str,
                    limit: float = 100):
    """
    - Funktion berechnet den Mittelwert der Krümmung für alle Werte mit Krümmung kleiner als limit
    
    Args:
        df:         Pandas Dataframe mit den Krümmungen
        energy:     Spalten-Label der Energie z.B. "band0" oder "diff"
        limit:      Dataframe wird auf Krümmung >= limit zugeschnitten
    """
    df_limit = df.loc[df[f"grad_grad_{energy}"] >= limit]
    x_std = np.mean(df_limit[f"dEdx_grad_{energy}"].to_numpy())
    y_std = np.mean(df_limit[f"dEdy_grad_{energy}"].to_numpy())
    z_std = np.mean(df_limit[f"dEdz_grad_{energy}"].to_numpy())
    vector = np.array((x_std, y_std, z_std))
    normalized_vector = vector/np.linalg.norm(vector)
    print(f"----> normierter Mittelwert der Krümmungsvektoren für {energy}:\n{normalized_vector}")

def model_PCA(df: list,
              energy: str):
    """
    - Funktion bestimmt die Hauptachsen der Energie-Variation durch Hauptkomponentenanalyse (PCA)
    - soll dazu dienen, die beste Drehung für das Gitter zu ermitteln, sodass der Fit die Symmetrie der Energie-Werte besser ausnutzen kann
    
    Args:
        df:         Pandas Dataframe mit den Gradienten
        energy:     Spalten-Label der Energie z.B. "band0" oder "diff"
    """
    dEdx = df[f"dEdx_{energy}"]
    dEdy = df[f"dEdy_{energy}"]
    dEdz = df[f"dEdz_{energy}"]
    gradients = np.array([[dgx, dgy, dgz] for dgx, dgy, dgz in zip(dEdx, dEdy, dEdz)])
    pca = PCA(n_components=3)
    pca.fit(gradients)
    principal_axes = pca.components_
    print(f"----> Ergebnis der PCA-Analyse für {energy}:\n{principal_axes}")

# --------------------------------------------------------------------------------------
# Zuschnitt des Dataframes vor der Modellierung
# --------------------------------------------------------------------------------------

def model_cut_000(df: list,
                  coord_system: str):
    """
    - wenn coord_system="xyz" oder "xyz_scaled": entfernt x=y=z=0 aus den Daten (vor der Modellierung)
    - wenn coord_system="path": entfernt rho=0 aus den Daten (vor der Modellierung)
    
    Args:
        df:             Pandas Dataframe
        coord_system:   Koordinatensystem "xyz", "xyz_scaled" oder "path"
    Return:
        df:     Pandas Dataframe mit den entfernten Koordinaten
    """
    print(f"----> Alte Rho-Verteilung:\n {df["rho"].unique()}")
    if (coord_system=="xyz") or (coord_system=="xyz_scaled"):
        df = df[~((df["x"] == 0) & (df["y"] == 0) & (df["z"] == 0))] 
        # ~ negiert die Bedingung
    elif coord_system=="path":
        df = df[~((df["rho"] == 0))]
    print(f"----> Neue Rho-Verteilung:\n {df["rho"].unique()}")
    print()
    return df

def model_cut_df_to_thz_range(df: list,
                              cut_value_diff: float,
                              cut_value_bands: float,
                              coord_system: list,
                              complete_cut: bool = True):
    """
    - Funktion schneidet das Dataframe auf den thz-aktiven Bereich zu
    - complete_cut = True: Die Bänder werden direkt über das Dataframe exakt auf die Thz-Bedingungen zugeschnitten. Das Dataframe wird schlicht gefiltert.
    - complete_cut = False: Der Zuschnitt erfolgt über die vorkommenden Achsenwerte nach Anwendung der Thz-Bedinungen. Wenn das Koordinatensystem zylindrisch ist, und alle Werte phi von 0 bis 2pi vorkommen, dann werden die Bänder über den gesamten Kreis zurückgegeben, auch wenn die Thz-aktive Zone eine Fläche im Kreis bildet.

    Args:
        df:                 Pandas Dataframe
        cut_value_diff:     Energie in eV, auf der die Differenz der Bänder zugeschnitten wird
        cut_value_bands:    Energie in eV, auf der die Bänder zugeschnitten werden
        coord_system:       Koordinatensystem der Berechnungen
        complete_cut:       siehe oben
    Return:
        df_neu oder df_area: das auf dem thz-aktiven Bereich zugeschnittene Dataframe
    """
    print("====> Definition des THz-aktiven Bereichs:")
    print(f"----> Differenz der Bänder < {cut_value_diff}")
    print(f"----> unteres Band > -{cut_value_bands}")
    print(f"----> oberes Band < {cut_value_bands}")

    # Wahl des Koordinatensystems
    if coord_system == "kxyz":
        axes = ("kx", "ky", "kz")
    elif coord_system == "xyz":
        axes = ("x", "y", "z")
    elif coord_system == "xyz_scaled":
        axes = ("x_scaled", "y_scaled", "z_scaled")
    elif coord_system == "path":
        axes = ("t", "rho", "phi")
    else:
        raise ValueError(f"coord_system={coord_system}; Dieses Koordinatensystem existiert nicht! Verfügbar:\n xyz\n xyz_scaled\n path")
    
    # Koordinatenachsen des Koordinatensystems
    x_vals = np.sort(df[axes[0]].unique())
    y_vals = np.sort(df[axes[1]].unique())
    z_vals = np.sort(df[axes[2]].unique())
        
    # Minimal- und Maximalwerte
    x_min_old, x_max_old = float(min(x_vals)), float(max(x_vals))
    y_min_old, y_max_old = float(min(y_vals)), float(max(y_vals))
    z_min_old, z_max_old = float(min(z_vals)), float(max(z_vals))

    # Zuschnittbedingungen
    df_area = df.copy()
    df_area = df_area.loc[(df_area["diff"] < cut_value_diff) & (df_area["band1"] < cut_value_bands) & (df_area["band0"] > -cut_value_bands)]
    
    # Print der neuen Grenzen
    x_min, x_max = float(min(df_area[axes[0]])), float(max(df_area[axes[0]]))
    y_min, y_max = float(min(df_area[axes[1]])), float(max(df_area[axes[1]]))
    z_min, z_max = float(min(df_area[axes[2]])), float(max(df_area[axes[2]]))

    print("====> Bereich des thz-aktiven Bereichs:")
    print(f"----> {axes[0]}: [{x_min} , {x_max}]")
    print(f"----> {axes[1]}: [{y_min} , {y_max}]")
    print(f"----> {axes[2]}: [{z_min} , {z_max}]")
    
    # Grenzen für das Koordinatensystem (x,y,z)
    if coord_system != "xyz": 
        xx_min, xx_max = float(min(df_area["x"])), float(max(df_area["x"]))
        yy_min, yy_max = float(min(df_area["y"])), float(max(df_area["y"]))
        zz_min, zz_max = float(min(df_area["z"])), float(max(df_area["z"]))
        print("====> Im Koordinatensystem (x,y,z):")
        print(f"----> {"x"}: [{xx_min} , {xx_max}]")
        print(f"----> {"y"}: [{yy_min} , {yy_max}]")
        print(f"----> {"z"}: [{zz_min} , {zz_max}]")
    # Grenzen für Komponenten des V-Vektors
    if coord_system == "path":
        vB = df_area["rho"]*np.cos(df_area["phi"])
        vN = df_area["rho"]*np.sin(df_area["phi"])
        vB_min, vB_max = float(np.min(vB)), float(np.max(vB))
        vN_min, vN_max = float(np.min(vN)), float(np.max(vN))
        print("====> Ebenen-Komponenten im Koordinatensystem (r,rho,phi):")
        print(f"----> {"vB"}: [{vB_min} , {vB_max}]")
        print(f"----> {"vN"}: [{vN_min} , {vN_max}]")

    if complete_cut:
        print("Zuschnitt auf diesen Bereich.")
        print()
        return df_area
    
    else:
        print("Zuschnitt Minima und Maxima unter Berücksichtigung, dass Koordinatenachse mehrere Punkte enthält.")
        x_min_indize, x_max_indize = np.where(x_vals == x_min)[0][0], np.where(x_vals == x_max)[0][0]
        y_min_indize, y_max_indize = np.where(y_vals == y_min)[0][0], np.where(y_vals == y_max)[0][0]
        z_min_indize, z_max_indize = np.where(z_vals == z_min)[0][0], np.where(z_vals == z_max)[0][0]

        if x_min_indize == x_max_indize: # keine Ausdehnung
            x_range = x_vals[x_min_indize-1: x_max_indize+2]
        else:
            x_range = x_vals[x_min_indize: x_max_indize+1]

        if y_min_indize == y_max_indize: # keine Ausdehnung
            y_range = y_vals[y_min_indize-1: y_max_indize+2]
        else:
            y_range = y_vals[y_min_indize: y_max_indize+1]

        if z_min_indize == z_max_indize: # keine Ausdehnung
            z_range = z_vals[z_min_indize-1: z_max_indize+2]
        else:
            z_range = z_vals[z_min_indize: z_max_indize+1]

        df_neu = df.loc[df[axes[0]].isin(x_range) & df[axes[1]].isin(y_range) & df[axes[2]].isin(z_range)]
        x_min_neu, x_max_neu = float(min(df_neu[axes[0]].unique())), float(max(df_neu[axes[0]].unique()))
        y_min_neu, y_max_neu = float(min(df_neu[axes[1]].unique())), float(max(df_neu[axes[1]].unique()))
        z_min_neu, z_max_neu = float(min(df_neu[axes[2]].unique())), float(max(df_neu[axes[2]].unique()))

        print("====> Zuschnitt: vorher -> nacher")
        print(f"----> {axes[0]}: [{x_min_old} , {x_max_old}] -> [{x_min_neu} , {x_max_neu}]")
        print(f"----> {axes[1]}: [{y_min_old} , {y_max_old}] -> [{y_min_neu} , {y_max_neu}]")
        print(f"----> {axes[2]}: [{z_min_old} , {z_max_old}] -> [{z_min_neu} , {z_max_neu}]")
        print()
        return df_neu

# ######################################################################################
# Modellierung
# ######################################################################################

# --------------------------------------------------------------------------------------
# Design_Matrix des Modells laden
# --------------------------------------------------------------------------------------

def load_model(modeltype: str,
               orders: list,
               x, y, z,
               symmetry=None,
               coeffs=None,
               no_a0=False,
               a_coeffs=None,
               b_coeffs=None):
    """
    - verwendet Funktionen aus qe_model_models.py

    - lädt die Designmatrix (oder Modell-Werte) für verschiedene Funktionen
    
    Args:
        modeltype:      Parametername des Modells
        orders:         Liste der Ordnungen für das Modell Bsp: [p_order, f_order, l_order, ...]
                        p_order:            p-Ordnung des Modells
                        f_order:            f-Ordnung des Modells
                        l_order:            l-Ordnung des Modells
                        ...
        x, y, z:        Koordinaten, float oder array
        symmetry:       Grad der Symmetrie
        coeffs:         Modellkoeffizienten
        no_a0:          Soll der erste Koeffizient (konstanter Term) entfernt werden?
        a_coeffs, b_coeffs:  Koeffizienten des Pfades
    Return:
        Design-Matrix, falls coeffs=None
        Modell-Werte, falls coeffs vorhanden
    """
    if modeltype == "regular_1":
        A = models.model_regular_1(orders[0], x, y, z, coeffs=coeffs, no_a0=no_a0)
    elif modeltype == "regular_2":
        A = models.model_regular_2(orders[0], x, y, z, coeffs=coeffs, no_a0=no_a0)
    elif modeltype == "regular_3":
        A = models.model_regular_3(orders[0], x, y, z, coeffs=coeffs, no_a0=no_a0)
    # --------------------------------------------------------------------------------------------
    elif modeltype == "regular_4":
        print(f"WARNUNG: Nur für Skalierung auf [-1,1]. Falls nicht, muss der Parameter L im Modell manuell angepasst werden!")
        A = models.model_regular_4(orders[0], orders[1], x, y, z, symmetry=symmetry, coeffs=coeffs, no_a0=no_a0)
    elif modeltype == "regular_5":
        print(f"WARNUNG: Nur für Skalierung auf [-1,1]. Falls nicht, muss der Parameter L im Modell manuell angepasst werden!")
        A = models.model_regular_5(orders[0], orders[1], x, y, z, symmetry=symmetry, coeffs=coeffs, no_a0=no_a0)
    elif modeltype == "regular_6":
        print(f"WARNUNG: Nur für Skalierung auf [-1,1]. Falls nicht, muss der Parameter L im Modell manuell angepasst werden!")
        A = models.model_regular_6(orders[0], orders[1], orders[2], x, y, z, symmetry=symmetry, coeffs=coeffs, no_a0=no_a0)
    elif modeltype == "regular_7":
        print(f"WARNUNG: Nur für Skalierung auf [-1,1]. Falls nicht, muss der Parameter L im Modell manuell angepasst werden!")
        A = models.model_regular_7(orders[0], orders[1], orders[2], x, y, z, symmetry=symmetry, coeffs=coeffs, no_a0=no_a0)
    # --------------------------------------------------------------------------------------------
    elif modeltype == "cylindrical_1":
        A = models.model_cylindrical_1(orders[0], orders[1], x, y, z, symmetry=symmetry, coeffs=coeffs, no_a0=no_a0)
    elif modeltype == "cylindrical_2":
        A = models.model_cylindrical_2(orders[0], orders[1], x, y, z, symmetry=symmetry, coeffs=coeffs, no_a0=no_a0)
    elif modeltype == "cylindrical_3":
        A = models.model_cylindrical_3(orders[0], orders[1], x, y, z, symmetry=symmetry, coeffs=coeffs, no_a0=no_a0)
    elif modeltype == "cylindrical_4":
        A = models.model_cylindrical_4(orders[0], orders[1], orders[2], x, y, z, symmetry=symmetry, coeffs=coeffs, no_a0=no_a0)
    # --------------------------------------------------------------------------------------------
    elif modeltype == "spherical_1":
        A = models.model_spherical_1(orders[0], orders[1], x, y, z, symmetry=symmetry, coeffs=coeffs, no_a0=no_a0)
    elif modeltype == "spherical_2":
        A = models.model_spherical_2(orders[0], orders[1], orders[2], x, y, z, symmetry=symmetry, coeffs=coeffs, no_a0=no_a0)
    elif modeltype == "spherical_3":
        A = models.model_spherical_3(orders[0], orders[1], x, y, z, coeffs=coeffs, no_a0=no_a0)
    elif modeltype == "spherical_4":
        A = models.model_spherical_4(orders[0], orders[1], x, y, z, coeffs=coeffs, no_a0=no_a0)
    # --------------------------------------------------------------------------------------------
    elif modeltype == "point1_xyz_1":
        A = models.model_point1_xyz_1(x, y, z, orders[0], orders[1], orders[2], a_coeffs, b_coeffs, coeffs=coeffs)
    elif modeltype == "point1_xyz_2":
        A = models.model_point1_xyz_2(x, y, z, a_coeffs, b_coeffs, coeffs=coeffs)
    # --------------------------------------------------------------------------------------------
    elif modeltype == "path_1":
        A = models.model_path_1(orders[0], orders[1], x, y, z, symmetry=symmetry, coeffs=coeffs, no_a0=no_a0)
    elif modeltype == "path_2":
        A = models.model_path_2(orders[0], orders[1], orders[2], x, y, z, symmetry=symmetry, coeffs=coeffs, no_a0=no_a0)
    elif modeltype == "path_3":
        A = models.model_path_3(orders[0], orders[1], orders[2], x, y, z, symmetry=symmetry, coeffs=coeffs, no_a0=no_a0)
    elif modeltype == "path_4":
        A = models.model_path_4(orders[0], orders[1], orders[2], orders[3], x, y, z, symmetry=symmetry, coeffs=coeffs)
    elif modeltype == "path_5":
        A = models.model_path_5(orders[0], orders[1], orders[2], x, y, z, symmetry=symmetry, coeffs=coeffs)
    elif modeltype == "path_6":
        A = models.model_path_6(orders[0], orders[1], orders[2], x, y, z, symmetry=symmetry, coeffs=coeffs)
    # --------------------------------------------------------------------------------------------
    elif modeltype == "model_path_abs_1":
        A = models.model_path_abs_1(orders[0], orders[1], orders[2], orders[3], x, y, z, symmetry=symmetry, coeffs=coeffs)
    elif modeltype == "model_path_abs_2":
        A = models.model_path_abs_2(orders[0], orders[1], orders[2], orders[3], x, y, z, symmetry=symmetry, coeffs=coeffs)
    elif modeltype == "model_path_abs_3":
        A = models.model_path_abs_3(orders[0], orders[1], orders[2], orders[3], x, y, z, symmetry=symmetry, coeffs=coeffs)
    elif modeltype == "model_path_abs_4": # Banddifferenz Punkt 1
        A = models.model_path_abs_4(orders[0], orders[1], orders[2], orders[3], x, y, z, symmetry=symmetry, coeffs=coeffs) # Epsilon
    elif modeltype == "model_path_abs_5": # Bänder Punkt 1
        A = models.model_path_abs_5(orders[0], orders[1], orders[2], orders[3], x, y, z, symmetry=symmetry, coeffs=coeffs) # Epsilon
    # --------------------------------------------------------------------------------------------
    elif modeltype == "model_path_point2_1":
        A = models.model_path_point2_1(orders[0], orders[3], orders[4], orders[5], orders[6], x, y, z, a_coeffs, coeffs=coeffs)
    elif modeltype == "model_path_point2_2": # Banddifferenz Punkt 2
        A = models.model_path_point2_2(orders[0], orders[3], orders[4], x, y, z, a_coeffs, symmetry=symmetry, coeffs=coeffs) # Epsilon
    elif modeltype == "model_path_point2_3": # Bänder Punkt 2
        A = models.model_path_point2_3(orders[0], orders[3], orders[4], x, y, z, a_coeffs, symmetry=symmetry, coeffs=coeffs) # Epsilon
    # --------------------------------------------------------------------------------------------
    elif modeltype == "model_path_point3_1":
        A = models.model_path_point3_1(orders[0], orders[2], orders[3], x, y, z, symmetry=symmetry, coeffs=coeffs) # Epsilon
    elif modeltype == "model_path_point3_2": # Banddifferenz Punkt 3
        A = models.model_path_point3_2(orders[0], orders[2], orders[3], x, y, z, symmetry=symmetry, coeffs=coeffs)
    elif modeltype == "model_path_point3_3": # änder Punkt 3
        A = models.model_path_point3_3(orders[0], orders[2], orders[3], x, y, z, symmetry=symmetry, coeffs=coeffs)
    else:
        raise ValueError(f"modeltype={modeltype} existiert nicht!")
    return A

# --------------------------------------------------------------------------------------
# Berechnung des Modells (FIT)
# --------------------------------------------------------------------------------------

def model_solve_LS(df: list,
                   modeltype: str,
                   energy: str,
                   orders: list,
                   symmetry: int = None,
                   coord_system: str = None,
                   no_a0: bool = False,
                   max_coeffs: int = 1000,
                   ridgeCV: bool = False,
                   ridge_alphas: list = np.logspace(-6, 2, 9),
                   col_weighting: bool = True,
                   a_coeffs: list = None,
                   b_coeffs: list = None):
    """
    - verwendet Funktion load_model

    - Hintergrund: The Full-Rank Least Squares Problem (LS)
      S.260 in Matrix Computations 4.th Edition Gene H. Golub
    - Löse: min ||Ax - b||_2

    Args:
        df:             das Pandas Dataframe
        modeltype:      Parametername des Modells
        energy:         Werte, an denen das Modell gefittet wird
        orders:         Liste der Ordnungen für das Modell Bsp: [p_order, f_order, l_order, ...]
                        p_order:            p-Ordnung des Modells
                        f_order:            f-Ordnung des Modells
                        l_order:            l-Ordnung des Modells
                        ...
        symmetry:       Grad der Symmetrie
        coord_system:   Koordinatensystem der Daten aus dem Dataframe
        no_a0:          Soll der erste Koeffizient (konstanter Term) entfernt werden?
        max_coeffs:     Modell wird nicht berechnet, wenn Anzahl der Koeffizieten > max_coeffs
        ridgeCV:        aktiviert Ridge-Lösungsverfahren anstatt lineare Regression
        ridge_alphas:   Liste von alphas im Ridge-Verfahren zum testen
        col_weighting:  aktiviert Spaltenskalierung der Design-Matrix nach GOLUB & VAN LOAN
        a_coeffs, b_coeffs:  Koeffizienten des Pfades
    Return:
        coeffs:         Modellkoeffizienten
        bool:           Bool, um Schleife über Ordnungen abzubrechen
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
        raise ValueError(f"coord_system={coord_system}; Dieses Koordinatensystem existiert nicht! Verfügbar:\n xyz\n xyz_scaled\n path")
    
    # Laden der Design-Matrix
    A = load_model(modeltype, orders, x, y, z, symmetry=symmetry, no_a0=no_a0, a_coeffs=a_coeffs, b_coeffs=b_coeffs)

    if col_weighting: # Siehe Matrix Computations GOLUB & VAN LOAN S.306
        # Spaltennormen berechnen (als Vektor)
        norm_vec = np.linalg.norm(A, axis=0)
        # Die Matrix muss nicht-singulär sein. Sonst wird durch 0 geteilt. Teilen durch 1 lässt die Spalte wie sie ist. 
        norm_vec = np.where(norm_vec == 0, 1.0, norm_vec)

        A = A / norm_vec # Dies entspricht dem Folgenden: 
        """
        G_0_inv = np.diag(1.0 / norm_vec) # Inverse der quadratischen Diagonalmatrix
        A = A @ G_0_inv # Skalierung der Design-Matrix
        """

    b = np.array(df[f"{energy}"])

    print_str_0 = f"----> Anzahl der Koeffizienten: {np.shape(A)[1]}"
    print_str_1 = f"----> Konditionszahl: {np.round(np.linalg.cond(A),2):.2e}"

    # Stop bei maximaler Anzahl an Koeffizienten
    if np.shape(A)[1] > max_coeffs:
        print(f"----> Zu viele Koeffizienten. Abbruch der Schleife.")
        return None, True

    # Lösung des linearen Gleichungssystems
    if ridgeCV:
        print(f"----> Lösungsverfahren: Ridge Regression")
        model = RidgeCV(alphas=ridge_alphas, fit_intercept=False)
        model.fit(A,b)
        coeffs = model.coef_
    else:
        print(f"----> Lösungsverfahren: Lineare Regression")
        coeffs, _, _, _ = np.linalg.lstsq(A, b, rcond=1e-10)
    
    # Rücktransformation der Skalierung:
    if col_weighting:
        coeffs = coeffs / norm_vec # Dies entspricht dem Folgenden: 
        """
        coeffs = G_0_inv @ coeffs
        """

    print(print_str_0)
    print(print_str_1)

    return coeffs, False

def model_a0_correction(df: list,
                        modeltype: str,
                        energy: str,
                        coeffs: list,
                        orders: list,
                        symmetry: int = None,
                        no_a0: bool = False,
                        a_coeffs: list = None,
                        b_coeffs: list = None):
    """
    - verwendet Funktion load.model

    - Funktion funktioniert nur, wenn a0 = einziger Koeffizient der konstanten Ordnung
    - Funktion passt a0 so an, dass die Energie von Modell und Daten bei 
      (0,0,0) übereinstimmen (Verschiebung der Energien)
    - Achtung funktioniert nur im auf den Ursprung verschobenen Gittern !
    
    Args:
        df:             das Pandas Datenframe, in dem band enthalten ist
        modeltype:      Parametername des Modells
        energy:         Werte, an denen das Modell gefittet wurde
        coeffs:         Modellkoeffizienten
        orders:         Liste der Ordnungen für das Modell Bsp: [p_order, f_order, l_order, k_order]
                        p_order:            p-Ordnung des Modells
                        f_order:            f-Ordnung des Modells
                        l_order:            l-Ordnung des Modells
                        k_order:            k-Ordnung des Modells
        symmetry:       Grad der Symmetrie
        no_a0:          Soll der erste Koeffizient (konstanter Term) entfernt werden?
        a_coeffs, b_coeffs:  Koeffizienten des Pfades
    Return:
        coeffs:         verbesserte Modellkoeffizienten für E0
    """
    print(f"----> a0-Korrektur")
    print(f"----> ACHTUNG: Funktioniert nur in auf den Ursprung verschobenen Gittern und wenn der erste Koeffizient jener der einzigen konstanten Ordnung ist!")
    
    # Funktionswert bei k0=[0,0,0] laden
    f = load_model(modeltype, orders, 0, 0, 0, symmetry=symmetry, coeffs=coeffs, no_a0=no_a0, a_coeffs=a_coeffs, b_coeffs=b_coeffs)
    # Energie bei k0=[0,0,0] laden
    df = df[(df["x"] == 0) & (df["y"] == 0)& (df["z"] == 0)]
    E = df[f"{energy}"].iloc[0]

    dE = abs(f - E)

    print("----> Fehler in a0 vor der Verschiebung:")
    print(f"----> |f - band| = {dE}")
    print(f"alter Koeffizient: {coeffs[0]}")
    if f > E:
        coeffs[0] = coeffs[0] - dE
    elif f < E:
        coeffs[0] = coeffs[0] + dE
    else:
        coeffs[0] = coeffs[0]
    print(f"neuer Koeffizient: {coeffs[0]}")
    
    return coeffs

# --------------------------------------------------------------------------------------
# Speichern der Modell-Energien im pandas Dataframe
# --------------------------------------------------------------------------------------

def model_use_on_grid(df: list,
                      energy: str,
                      modeltype: str,
                      orders: list,
                      coeffs: list,
                      coord_system: str,
                      symmetry: int = None,
                      no_a0: bool = False,
                      a_coeffs: list = None,
                      b_coeffs: list = None):
    """
    - verwendet Funktion load_model

    - Funktion berechnet mithilfe der Koeffizienten das Modell und speichert die Modellenergien im Dataframe
    - außerdem wird der Fehler an jedem Datenpunkt berechnet und dem Dataframe hinzugefügt
        
    Args:
        df:                 Pandas Dataframe
        energy:             Werte, an denen das Modell gefittet wurde
        modeltype:          Parametername des Modells
        orders:             Liste der Ordnungen für das Modell Bsp: [p_order, f_order, l_order, ...]
                            p_order:            p-Ordnung des Modells
                            f_order:            f-Ordnung des Modells
                            l_order:            l-Ordnung des Modells
                            ...
        coeffs:             Modellkoeffizienten der Energie
        coord_system:       Koordinatensystem der Daten aus dem Dataframe
        symmetry:           Grad der Symmetrie
        no_a0:              Wurde der erste Koeffizient a0 entfernt?
        a_coeffs, b_coeffs:  Koeffizienten des Pfades
    Return:
        df:                 das mit den Ergebnissen erweiterte Dataframe
    """
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
        raise ValueError(f"coord_system={coord_system}; Dieses Koordinatensystem existiert nicht! Verfügbar:\n xyz\n xyz_scaled\n path")

    energy_model = load_model(modeltype, orders, x, y, z, symmetry=symmetry, coeffs=coeffs, no_a0=no_a0, a_coeffs=a_coeffs, b_coeffs=b_coeffs)
    # Füge Modell-Energien dem Dataframe hinzu
    df[f"{energy}_model"] = energy_model
    # Fehler berechnen und dem Dataframe hinzufügen
    df[f"error_{energy}"] = abs(df[f"{energy}"]-df[f"{energy}_model"])
    return df

# ######################################################################################
# Speichern und Laden von Dateien
# ######################################################################################

def model_save_array(array: list,
                     p_str: str,
                     n_str: str,
                     datlabel: str,
                     txt_suffix: str,
                     modeltype: str):
    """
    - speichert numpy-array als txt-file im Unterordner:
        main_directory/prefix_out/suffix/modeltype
    Args:
        array:          numpy-array, der zeilenweise als txt-File gespeichert wird
        p_str:          halbe Kantenlängen (p1, p2, p2) des Gitters als string (für Dateienpfad)
        n_str:          Anzahl der Datenpunkte (n1, n2, n3) als string (für Dateienpfad)
        datlabel:       Label in Dateienname
        txt_suffix:     Suffix der txt-Datei
        modeltype:      Name des Modells
    """
    prefix = config.prefix
    path_result_directory = config.path_result_directory(modeltype, datlabel, p_str, n_str)
    path_data = os.path.join(path_result_directory, f"{prefix}_{txt_suffix}.txt")
    with open(path_data, "w") as txt_file:
        for line in array:
            txt_file.write(f"{line}"+ "\n")

def model_save_csv(df: list,
                   p_str: str,
                   n_str: str,
                   datlabel: str,
                   csv_suffix: str,
                   modeltype: str,
                   index: bool = False):
    """
    - speichert ein pandas-Dataframe als csv-Datei im Unterordner:
        main_directory/prefix_out/suffix/modeltype
    Args:
        df:             pandas-Dataframe
        p_str:          halbe Kantenlängen (p1, p2, p2) des Gitters als string (für Dateienpfad)
        n_str:          Anzahl der Datenpunkte (n1, n2, n3) als string (für Dateienpfad)
        datlabel:       Label in Dateienname
        csv_suffix:     Suffix der csv-Datei
        modeltype:      Name des Modells
        index:          Soll der Index des Dataframes gespeichert werden?
    """
    prefix = config.prefix
    path_result_directory = config.path_result_directory(modeltype, datlabel, p_str, n_str)
    path_csv = os.path.join(path_result_directory, f"{prefix}_{csv_suffix}.csv")
    print(f"Speichere Dataframe der Modell-Energien an folgendem Ort:\n{path_csv}")
    df.to_csv(path_csv, index=index)

def model_load_df(p_str: str,
                  n_str: str,
                  datlabel: str,
                  csv_suffix: str,
                  modeltype: str):
    """
    - lädt csv-Datei aus Unterordner und gibt es als pandas-Dataframe zurück
    Unterordner: main_directory/prefix_out/suffix/modeltype

    Args:
        p_str:          halbe Kantenlängen (p1, p2, p2) des Gitters als string (für Dateienpfad)
        n_str:          Anzahl der Datenpunkte (n1, n2, n3) als string (für Dateienpfad)
        datlabel:       Label in Dateienname
        csv_suffix:     Suffix der csv-Datei: 
                        Beispiel:   nitiB2_thz_all_mins.csv, 
                                    suffix = all_mins
        modeltype:      Name des Modells
    Return:
        df              pandas-Dataframe                            
    """
    prefix = config.prefix
    path_result_directory = config.path_result_directory(modeltype, datlabel, p_str, n_str)
    path_data = os.path.join(path_result_directory, f"{prefix}_{csv_suffix}.csv")
    df = pd.read_csv(path_data)
    return df

def model_load_txt(p_str: str,
                   n_str: str,
                   datlabel: str,
                   txt_suffix: str,
                   modeltype: str):
    """
    - Funktion lödt txt-file im Modell-Unterordner als Liste
    Args:
        p_str:          halbe Kantenlängen (p1, p2, p2) des Gitters als string (für Dateienpfad)
        n_str:          Anzahl der Datenpunkte (n1, n2, n3) als string (für Dateienpfad)
        datlabel:       Label in Dateienname
        txt_suffix:     Suffix der txt-Datei:
                        Beispiel:   nitiB2_thz_coeffs.txt,
                                    txt_suffix = coeffs 
        modeltype:      Name des Modells
    Return:
        lines           Liste aus Zeilen des txt-Files
    """
    prefix = config.prefix
    path_result_directory = config.path_result_directory(modeltype, datlabel, p_str, n_str)
    path_data = os.path.join(path_result_directory, f"{prefix}_{txt_suffix}.txt")
    with open(path_data, 'r') as txt_file:
        lines = [float(line.rstrip('\n')) for line in txt_file]
    lines = np.array(lines)
    return lines
