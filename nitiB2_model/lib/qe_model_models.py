import numpy as np
import pandas as pd
from itertools import product
from scipy.special import sph_harm_y as sph_harm
from numpy.polynomial import legendre
from numpy.polynomial import chebyshev
from scipy.special import genlaguerre

import lib.qe_model_pathmodels as pathmodels

"""
# ######################################################################################
- Die Funktionen in diesem Dokument definieren die Modelle, die von load_model in qe_model_calc geladen werden. Beim Hinzufügen neuer Modelle muss auch load_model angepasst werden.

load_model(modeltype, orders, x, y, z, symmetry=None, coeffs=None, no_a0=False)

Args:
    p_order = orders[0]:        p-Ordnung des Modells
    f_order = orders[1]:        f-Ordnung des Modells
    l_order = orders[2]:        l-Ordnung des Modells
    k_order = orders[3]:        k-Ordnung des Modells
    p1_order = orders[4]:       p1-Ordnung des Modells
    p2_order = orders[5]:       p2-Ordnung des Modells
    p3_order = orders[6]:       p3-Ordnung des Modells
    
    x,y,z:          Koordinaten, float oder array
    symmetry:       Grad der Symmetrie: haben die Daten eine 4-Fach-Symmetrie, damm symmetry=4
    coeffs:         Modellkoeffizienten
    no_a0:          Soll der erste Koeffizient in den Polynom_Ordnungen entfernt werden?
Return:
    Design-Matrix, falls coeffs=None
    Modell-Werte, falls coeffs vorhanden

- Die Eigenschaften der Modellfunktionen werden im Dokument [PLATZHALTER] genauer erläutert.
# ######################################################################################
"""

# ######################################################################################
# Modelle in kartesischen Koordinaten
# ######################################################################################

# ======================================================================================
# Einfache Polynome
# ======================================================================================

def powers(order, dim=3):
    """
    - generiert eine Liste von Exponenten-Kombinationen für beliebige Polynom-Ordnungen
    - Liefert alle Exponenten-Tuples (i,j,k) für Polynome <= order
    - Beispiel: order=1, dim=3:
        
          x⁰y⁰z⁰   x¹y⁰z⁰   x⁰y¹z⁰   x⁰y⁰z¹
    """
    powers_ = []
    for total_degree in range(order+1):
        for exps in product(range(total_degree+1), repeat=dim):
            if sum(exps) == total_degree:
                powers_.append(exps)
    return powers_

def terms_xyz_vec(order, x, y, z, no_a0=False):
    """
    - Funkion ist eine vektorisierte Version und nutzt numpy anstatt von For-Schleifen, um eine komplette Design-Matrix A aus Polynomen für ein lineares Gleichungssystem bzw. Regression zu erstellen.
    - jede Spalte entspricht einem Polynom-Term (1, z, y, x, z², ...)
    - jede Zeile entspricht einem Datenpunkt
    - Beispiel: order=1, no_a0=False:
        A: [[x1⁰y1⁰z1⁰, x1⁰y1⁰z1¹, x1⁰y1¹z1⁰, x1¹y1⁰z⁰ ]
            [x2⁰y2⁰z2⁰, x2⁰y2⁰z2¹, x2⁰y2¹z2⁰, x2¹y2⁰z2⁰]
            [x3⁰y3⁰z3⁰, x3⁰y3⁰z3¹, x3⁰y3¹z3⁰, x3¹y3⁰z3⁰]
            [x4⁰y4⁰z4⁰, x4⁰y4⁰z4¹, x4⁰y4¹z4⁰, x4¹y4⁰z4⁰]
            [ ...                                      ]]
    """
    x = np.atleast_1d(x) # falls x float -> [x]
    y = np.atleast_1d(y)
    z = np.atleast_1d(z)

    exp = powers(order, dim=3) # [(0, 0, 0), (0, 0, 1), (0, 1, 0), (1, 0, 0),...]
    if no_a0:
        exp.remove((0, 0, 0)) # entfernt Term (0,0,0)
    exp = np.array(exp) # exp als Matrix mit shape: (Ordnungen, spalte)
    """
    exp = [[0 0 0]
           [0 0 1]
           [0 1 0]
           [1 0 0]
           [...  ]]
    """
    A = (x[:, None] ** exp[:, 0]) * (y[:, None] ** exp[:, 1]) * (z[:, None] ** exp[:, 2]) # Design-Matrix, shape: (len(x), Ordnungen)
    """
    x[:,None]: macht aus Zeilenvektor x = [x1, x2, .. ] einen Spaltenvektor
    exp[:, 0]: erste Spalte von exp als Zeilenvektor
    A: [[x1⁰y1⁰z1⁰, x1⁰y1⁰z1¹, x1⁰y1¹z1⁰, ...]
        [x2⁰y2⁰z2⁰, x2⁰y2⁰z2¹, x2⁰y2¹z2⁰, ...]
        [ ...                                ]]
    """ 
    return A

def terms_xy_vec(order, x, y, no_a0=False):
    """
    - gleiche Logik wie Funktion terms_xyz_vec, nur für zwei Dimensionen
    """
    x = np.atleast_1d(x) # falls x float -> [x]
    y = np.atleast_1d(y)

    exp = powers(order, dim=2) # [(0, 0), (0, 1), (1, 0), (0, 2), (1, 1), ...]
    if no_a0:
        exp.remove((0, 0))
    exp = np.array(exp)
    A = (x[:, None] ** exp[:, 0]) * (y[:, None] ** exp[:, 1])
    return A

def terms_x_vec(order, x, no_a0=False):
    """
    - gleiche Logik wie Funktion terms_xyz_vec, nur für eine Dimension
    """
    x = np.atleast_1d(x) # falls x float -> [x]
    exp = powers(order, dim=1)
    if no_a0:
        exp.remove((0,))
    exp = np.array(exp)
    A = (x[:, None] ** exp[:, 0])
    return A

# --------------------------------------------------------------------------------------

def model_regular_1(p_order, x, y, z, coeffs=None, no_a0=False):
    """
    - Modell für einfache Polynome in x,y,z der Ordnung p_order
    - coeffs = None:
        -> lädt Design-Matrix A
    - coeffs = Liste von Koeffizienten:
        -> führt die Matrix-Vektor-Multiplikation aus. Das Ergebnis ist der berechnete Wert des Polynoms an den Stellen (x,y,z)
    - Wenn x ein Skalar ist, wird auch der resultierende Wert als Skalar anstatt eines 1-Element-Arrays ausgegeben.
    """
    A = terms_xyz_vec(p_order, x, y, z, no_a0)
    if coeffs is None:
        return A
    else:
        if np.isscalar(x):
            return (A @ coeffs).item()
        else:
            return A@coeffs

# ======================================================================================
# chebyshev - Polynome
# ======================================================================================

def chebyshev_terms(order, x, no_a0=False):
    """
    - berechnet die Polynom-Basis-Polynome für eine Dimension
    - Das Ergebnis ist eine Matrix, in der jede Spalte ein Chebyshev-Polynom T(x) ist.
        Beispiel Order=2
        [[T0(x1), T1(x1), T2(x1)]
         [T0(x2), T1(x2), T2(x2)]
         [T0(x3), T1(x3), T2(x3)]
         [T0(x4), T1(x4), T2(x4)]
         [ ...                  ]]
    - Shape: (len(x), order+1)
    """
    one_mat = np.eye(order+1) # Einheitsmatrix
    terms = chebyshev.chebval(x, one_mat.T).T
    if no_a0:
        terms = terms[:, 1:] # Entferne T0
    return terms

def chebyshev_xyz(order, x, y, z, no_a0=False):
    """
    - diese Funktion kombiniert die 1D-Chebyshev-Polynome zu einem Tensorprodukt in 3D
        T_i(x)*T_j(y)*T_k(z)
    - Shape: (len(x), (order+1)**3)
    - Bei order=2 sind es 3³=27 Terme.
        Die Design-Matrix enthält nun alle Kombinationen T_i(x)*T_j(y)*T_k(z) für i,j,k in {1,2,3}
        [[T0(x1)*T0(y1)*T0(z1), T0(x1)*T0(y1)*T1(z1), T0(x1)*T0(y1)*T2(z1), T0(x1)*T1(y1)*T0(z1), ...]
         [T0(x2)*T0(y2)*T0(z2), T0(x2)*T0(y2)*T1(z2), T0(x2)*T0(y2)*T2(z2), T0(x2)*T1(y2)*T0(z2), ...]
         [T0(x3)*T0(y3)*T0(z3), T0(x3)*T0(y3)*T1(z3), T0(x3)*T0(y3)*T2(z3), T0(x3)*T1(y3)*T0(z3), ...]
         [ ...                                                                                       ]]
    """
    x = np.atleast_1d(x) # falls x float -> [x]
    y = np.atleast_1d(y)
    z = np.atleast_1d(z)
    Tx = chebyshev_terms(order, x, no_a0=no_a0)
    Ty = chebyshev_terms(order, y, no_a0=no_a0)
    Tz = chebyshev_terms(order, z, no_a0=no_a0)
    # Tensorprodukt
    terms = (Tx[:, :, None, None] * Ty[:, None, :, None] * Tz[:, None, None, :])
    return terms.reshape(len(x), -1)

def model_regular_2(p_order, x, y, z, coeffs=None, no_a0=False):
    """
    - Produktansatz mit Chebychev-Polynome
    - Skalierung auf [-1,1] notwendig
    """
    A = chebyshev_xyz(p_order, x, y, z, no_a0=no_a0)

    if coeffs is None:
        return A
    else:
        if np.isscalar(x):
            return (A @ coeffs).item()
        else:
            return A@coeffs

# ======================================================================================
# Legendre - Polynome
# ======================================================================================

def legendre_terms(order, x, no_a0=False):
    """
    - Logik ist das gleiche wie chebyshev_terms, nur für Legendre-Polynome
    """
    one_mat = np.eye(order+1) # Einheitsmatrix
    terms = legendre.legval(x, one_mat.T).T
    if no_a0:
        terms = terms[:, 1:] # Entferne T0
    return terms

def legendre_xyz(order, x, y, z, no_a0=False):
    """
    - Logik ist das gleiche wie chebyshev_xyz, nur für Legendre-Polynome
    """
    x = np.atleast_1d(x) # falls x float -> [x]
    y = np.atleast_1d(y)
    z = np.atleast_1d(z)
    Lx = legendre_terms(order, x, no_a0=no_a0)
    Ly = legendre_terms(order, y, no_a0=no_a0)
    Lz = legendre_terms(order, z, no_a0=no_a0)
    # Tensorprodukt
    terms = (Lx[:, :, None, None] * Ly[:, None, :, None] * Lz[:, None, None, :])
    return terms.reshape(len(x), -1)

def model_regular_3(order, x, y, z, coeffs=None, no_a0=False):
    """
    - Produktansatz mit Legendre-Polynome
    - Skalierung auf [-1,1] notwendig
    """
    A = legendre_xyz(order, x, y, z, no_a0=no_a0)
    
    if coeffs is None:
        return A
    
    else:
        if np.isscalar(x):
            return (A @ coeffs).item()
        else:
            return A@coeffs

# ======================================================================================
# Funktionen mit Trigonometrischen Reihen
# ======================================================================================

def model_regular_4(p_order, f_order, x, y, z, symmetry=None, coeffs=None, no_a0=False, L=2):
    """
    - Mischung aus einfachen Polynomen und Winkelterm-Produkten
    - für Skalierung auf [-1,1] gilt L=2, falls nicht, muss L hier manuell angepasst werden
    """
    k = 2*np.pi/L
    s = 1 if symmetry is None else symmetry
    
    # Polynom-Designmatrix
    A_poly = terms_xyz_vec(p_order, x, y, z, no_a0=no_a0) # shape: (len(x), Ordnungen)

    # Fourier-Terme
    fourier_terms = []
    for n in range(1, f_order+1):
        ax, ay, az = s*k*n*x, s*k*n*y, s*k*n*z
        cx, cy, cz = np.cos(ax), np.cos(ay), np.cos(az)
        sx, sy, sz = np.sin(ax), np.sin(ay), np.sin(az)
        # 8 Kombinationen der Sinus und Cosinus-Terme
        fourier_terms.extend([cx * cy * cz, 
                              cx * cy * sz,
                              cx * sy * cz,
                              sx * cy * cz,
                              cx * sy * sz,
                              sx * cy * sz,
                              sx * sy * cz,
                              sx * sy * sz])
    A_fourier = np.column_stack(fourier_terms) # shape: (len(x), 8*f_order)
    
    # Kombination
    A = np.concatenate([A_poly, A_fourier], axis=1) # shape: (len(x), Ordnungen+8*f_order)

    if coeffs is None:
        return A
    else:
        if np.isscalar(x):
            return (A @ coeffs).item()
        else:
            return A@coeffs

def model_regular_5(p_order, f_order, x, y, z, symmetry=None, coeffs=None, no_a0=False, L=2):
    """
    - Mischung aus einfachen Polynomen und Winkeltermen
    - für Skalierung auf [-1,1] gilt L=2, falls nicht, muss L hier manuell angepasst werden
    """
    k = 2*np.pi/L
    s = 1 if symmetry is None else symmetry

    # Polynom-Designmatrix
    A_poly = terms_xyz_vec(p_order, x, y, z, no_a0=no_a0) # shape: (len(x), Ordnungen)
    
    # Fourier-Terme
    fourier_terms = []
    for n in range(1, f_order+1):
        an = s*k*n*(x+y+z)
        fourier_terms.extend([np.cos(an), np.sin(an)])
    A_fourier = np.column_stack(fourier_terms) # shape: (len(x), 2*f_order)
    
    # Kombination
    A = np.concatenate([A_poly, A_fourier], axis=1) # shape: (len(x), Ordnungen+2*f_order)

    if coeffs is None:
        return A
    else:
        if np.isscalar(x):
            return (A @ coeffs).item()
        else:
            return A@coeffs

def model_regular_6(p_order, f_order, l_order, x, y, z, symmetry=None, coeffs=None, no_a0=False, L=2):
    """
    - Mischung aus einfachen Polynomen und Winkelterm-Produkten multipliziert mit Polynomen 
    - für Skalierung auf [-1,1] gilt L=2, falls nicht, muss L hier manuell angepasst werden
    """
    k = 2*np.pi/L
    s = 1 if symmetry is None else symmetry
    
    # Polynom-Designmatrix
    A_poly = terms_xyz_vec(p_order, x, y, z, no_a0=no_a0) # shape: (len(x), p-Ordnungen)
    R_poly = terms_xyz_vec(l_order, x, y, z, no_a0=no_a0) # shape: (len(x), l-Ordnungen)

    # Fourier-Terme
    fourier_terms = []
    for n in range(1, f_order+1):
        ax, ay, az = s*k*n*x, s*k*n*y, s*k*n*z
        cx, cy, cz = np.cos(ax), np.cos(ay), np.cos(az)
        sx, sy, sz = np.sin(ax), np.sin(ay), np.sin(az)
        # 8 Kombinationen der Sinus und Cosinus-Terme
        fourier_terms.extend([cx * cy * cz, 
                              cx * cy * sz,
                              cx * sy * cz,
                              sx * cy * cz,
                              cx * sy * sz,
                              sx * cy * sz,
                              sx * sy * cz,
                              sx * sy * sz])
    F_fourier = np.column_stack(fourier_terms) # shape: (len(x), 8*f_order)
    
    # Kombination R_poly*F_fourier
    A_fourier = R_poly[:,:,None]*F_fourier[:,None,:]
    A_fourier = A_fourier.reshape(np.atleast_1d(x).shape[0], -1) # wenn x scalar, wird es zum Vektor, sonst hat es keinen shape
    """
    np.shape(R_poly[:,:,None])  -> (len(x), l-Ordnungen, 1)
    print(np.shape(A_fourier))  -> (len(X), 1, 8*f_order)
    Multiplikation              -> (len(x), l-Ordnungen, 8*f_order), jeder Eintrag in poly wird mit allen Fouriertermen multipliziert
    np.shape(A_fourier.reshape(x.shape[0], -1)) -> (len(x), l-Ordnungen x 8*f_order)
    """

    # Kombination aus A_fourier und A_poly
    A = np.concatenate([A_poly, A_fourier], axis=1)

    if coeffs is None:
        return A
    else:
        if np.isscalar(x):
            return (A @ coeffs).item()
        else:
            return A@coeffs

def model_regular_7(p_order, f_order, l_order, x, y, z, symmetry=None, coeffs=None, no_a0=False, L=2):
    """
    - Mischung aus einfachen Polynomen und Winkeltermen multipliziert mit Polynomen
    - für Skalierung auf [-1,1] gilt L=2, falls nicht, muss L hier manuell angepasst werden
    """
    k = 2*np.pi/L
    s = 1 if symmetry is None else symmetry
    
    # Polynom-Designmatrix
    A_poly = terms_xyz_vec(p_order, x, y, z, no_a0=no_a0) # shape: (len(x), p-Ordnungen)
    R_poly = terms_xyz_vec(l_order, x, y, z, no_a0=no_a0) # shape: (len(x), l-Ordnungen)

    # Fourier-Terme
    fourier_terms = []
    for n in range(1, f_order+1):
        an = s*k*n*(x+y+z)
        fourier_terms.extend([np.cos(an), np.sin(an)])
    F_fourier = np.column_stack(fourier_terms) # shape: (len(x), 8*f_order)
    
    # Kombination R_poly*F_fourier
    A_fourier = R_poly[:,:,None]*F_fourier[:,None,:]
    A_fourier = A_fourier.reshape(np.atleast_1d(x).shape[0], -1) # wenn x scalar, wird es zum Vektor, sonst hat es keinen shape

    # Kombination aus A_fourier und A_poly
    A = np.concatenate([A_poly, A_fourier], axis=1)

    if coeffs is None:
        return A
    else:
        if np.isscalar(x):
            return (A @ coeffs).item()
        else:
            return A@coeffs
 
# --------------------------------------------------------------------------------------
# Modelle in Zylinderkoordinaten
# --------------------------------------------------------------------------------------

def model_cylindrical_1(p_order, f_order, x, y, z, symmetry=None, coeffs=None, no_a0=False):
    """
    - Mischung aus einfachen Polynomen und Fouriertermen
    """
    r = np.sqrt(x**2 + y**2)
    phi = np.arctan2(y, x)
    s = 1 if symmetry is None else symmetry
    
    # Polynom-Designmatrix
    A_poly = terms_xy_vec(p_order, r, z, no_a0=no_a0) # shape: (len(x), p-Ordnungen)

    # Fourier-Terme
    fourier_terms = []
    for n in range(1, f_order+1):
        an = s*n*phi
        fourier_terms.extend([np.cos(an), np.sin(an)])
    A_fourier = np.column_stack(fourier_terms) # shape: (len(x), 2*f_order)
    
    # Kombination aus A_fourier und A_poly
    A = np.concatenate([A_poly, A_fourier], axis=1)

    if coeffs is None:
        return A
    else:
        if np.isscalar(x):
            return (A @ coeffs).item()
        else:
            return A@coeffs

def model_cylindrical_2(p_order, f_order, x, y, z, symmetry=None, coeffs=None, no_a0=False):
    """
    - Mischung aus einfachen Polynomen und mit r multiplizierte Fourierterme
    """
    r = np.sqrt(x**2 + y**2)
    phi = np.arctan2(y, x)
    s = 1 if symmetry is None else symmetry

    # Polynom-Designmatrix
    A_poly = terms_xy_vec(p_order, r, z, no_a0=no_a0) # shape: (len(x), p-Ordnungen)

    # Fourier-Terme
    fourier_terms = []
    for n in range(1, f_order+1):
        an = s*n*phi
        fourier_terms.extend([r**(2*n)*np.cos(an)])
    A_fourier = np.column_stack(fourier_terms) # shape: (len(x), 2*f_order)
   
    # Kombination aus A_fourier und A_poly
    A = np.concatenate([A_poly, A_fourier], axis=1)

    if coeffs is None:
        return A
    else:
        if np.isscalar(x):
            return (A @ coeffs).item()
        else:
            return A@coeffs

def model_cylindrical_3(p_order, f_order, x, y, z, symmetry=None, coeffs=None, no_a0=False):
    """
    - Mischung aus einfachen Polynomen und mit r und z multiplizierte Fourierterme
    """
    r = np.sqrt(x**2 + y**2)
    phi = np.arctan2(y, x)
    s = 1 if symmetry is None else symmetry

    # Polynom-Designmatrix
    A_poly = terms_xy_vec(p_order, r, z, no_a0=no_a0) # shape: (len(x), p-Ordnungen)

    # Fourier-Terme
    fourier_terms = []
    for n in range(1, f_order+1):
        an = s*n*phi
        fourier_terms.extend([r**(n)*np.cos(an), r**(n)*np.sin(an), z**(n)*np.cos(an), z**(n)*np.sin(an)])
    A_fourier = np.column_stack(fourier_terms) # shape: (len(x), 4*f_order)
   
    # Kombination aus A_fourier und A_poly
    A = np.concatenate([A_poly, A_fourier], axis=1)

    if coeffs is None:
        return A
    else:
        if np.isscalar(x):
            return (A @ coeffs).item()
        else:
            return A@coeffs

def model_cylindrical_4(p_order, f_order, l_order, x, y, z, symmetry=None, coeffs=None, no_a0=False):
    """
    - Mischung aus einfachen Polynomen und Fourierterme multipliziert mit Polynomen (Verallgemeinerung von cylindrical_3)
    """
    r = np.sqrt(x**2 + y**2)
    phi = np.arctan2(y, x)
    s = 1 if symmetry is None else symmetry

    # Polynom-Designmatrix
    A_poly = terms_xy_vec(p_order, r, z, no_a0=no_a0) # shape: (len(x), p-Ordnungen)
    R_poly = terms_xy_vec(l_order, r, z, no_a0=no_a0) # shape: (len(x), l-Ordnungen)

    # Fourier-Terme
    fourier_terms = []
    for n in range(1, f_order+1):
        an = s*n*phi
        fourier_terms.extend([np.cos(an), np.sin(an)])
    F_fourier = np.column_stack(fourier_terms) # shape: (len(x), 2*f_order)

    # Kombination R_poly*F_fourier
    A_fourier = R_poly[:,:,None]*F_fourier[:,None,:]
    A_fourier = A_fourier.reshape(np.atleast_1d(x).shape[0], -1) 

    # Kombination aus A_fourier und A_poly
    A = np.concatenate([A_poly, A_fourier], axis=1)

    if coeffs is None:
        return A
    else:
        if np.isscalar(x):
            return (A @ coeffs).item()
        else:
            return A@coeffs

# --------------------------------------------------------------------------------------
# Modelle in Kugelkoordinaten
# --------------------------------------------------------------------------------------

def model_spherical_1(p_order, f_order, x, y, z, symmetry=None, coeffs=None, no_a0=False):
    """
    - Mischung aus einfachen Polynomen und Fourierterme
    """
    r = np.sqrt(x**2 + y**2 + z**2)
    theta = np.arccos(np.clip(z / np.maximum(r, 1e-15), -1, 1))
    phi = np.arctan2(y, x)
    s = 1 if symmetry is None else symmetry

    # Polynom-Designmatrix
    A_poly = terms_x_vec(p_order, r, no_a0=no_a0) # shape: (len(x), p-Ordnungen)

    # Fourier-Terme
    fourier_terms = []
    for n in range(1, f_order+1):
        an = s*n*theta
        bn = s*n*phi
        fourier_terms.extend([np.cos(an), np.sin(an), np.cos(bn), np.sin(bn)])
    A_fourier = np.column_stack(fourier_terms) # shape: (len(x), 2*f_order)

    # Kombination aus A_fourier und A_poly
    A = np.concatenate([A_poly, A_fourier], axis=1)

    if coeffs is None:
        return A
    else:
        if np.isscalar(x):
            return (A @ coeffs).item()
        else:
            return A@coeffs

def model_spherical_2(p_order, f_order, l_order, x, y, z, symmetry=None, coeffs=None, no_a0=False):
    """
    - Mischung aus einfachen Polynomen und Fourierterme multipliziert in Polynomen
    """
    r = np.sqrt(x**2 + y**2 + z**2)
    theta = np.arccos(np.clip(z / np.maximum(r, 1e-15), -1, 1))
    phi = np.arctan2(y, x)
    s = 1 if symmetry is None else symmetry

    # Polynom-Designmatrix
    A_poly = terms_x_vec(p_order, r, no_a0=no_a0) # shape: (len(x), p-Ordnungen)
    R_poly = terms_x_vec(l_order, r, no_a0=no_a0) # shape: (len(x), l-Ordnungen)

    # Fourier-Terme
    fourier_terms = []
    for n in range(1, f_order+1):
        an = s*n*theta
        bn = s*n*phi
        fourier_terms.extend([np.cos(an), np.sin(an), np.cos(bn), np.sin(bn)])
    F_fourier = np.column_stack(fourier_terms) # shape: (len(x), 2*f_order)

    # Kombination R_poly*F_fourier
    A_fourier = R_poly[:,:,None]*F_fourier[:,None,:]
    A_fourier = A_fourier.reshape(np.atleast_1d(x).shape[0], -1) 

    # Kombination aus A_fourier und A_poly
    A = np.concatenate([A_poly, A_fourier], axis=1)

    if coeffs is None:
        return A
    else:
        if np.isscalar(x):
            return (A @ coeffs).item()
        else:
            return A@coeffs

# Kugelfächenfunktionen mit einefachen Polynomen

def spherical_harmonics_vec(order, theta, phi, real=True):
    """
    - Hilfsfuntkion: berechnet sphärische Harmonische bis zur Odnung order
    - wandelt zudem komplexe Harmonische in eine reelle Basis um
    """
    theta = np.atleast_1d(theta)
    phi = np.atleast_1d(phi)

    # alle (l,m)-Kombinationen
    l_vals = np.arange(order+1)
    """
    erzeugt eine Liste aller möglichen l-Werte; für order=2:
    l_vals = [0 1 2]
    """
    m_vals = np.concatenate([np.arange(-l, l + 1) for l in l_vals])
    """
    für jedes l werden m-Werte erzeugt (-l bis l) und dann wird alles zu einem Vektor zusammengefasst; für order=2:
    l=0 -> m=[0]
    l=1 -> m=[-1 0 1]
    l=2 -> m=[-2 -1  0  1  2]
    m_vals = [ 0 -1  0  1 -2 -1  0  1  2]
    """
    l_for_m = np.concatenate([[l] * (2 * l + 1) for l in l_vals])
    """
    für jedes m brauchen wir ein l, deshalb muss l_vals auf die m erweitert werden; für order=2:
    l=0 -> [0]*1=[0]
    l=1 -> [1]*3=[1, 1, 1]
    l=2 -> [2]*5=[2, 2, 2, 2, 2]
    l_for_m = [0 1 1 1 2 2 2 2 2]
    """

    # Alle Y_lm
    Y = sph_harm(m_vals[:, None], l_for_m[:, None], theta[None, :], phi[None, :])  # (n_lm, N)
    Y = Y.T  # (N, n_lm)

    if real:
        terms = []
        for i, (m,l) in enumerate(zip(m_vals, l_for_m)):
            if m > 0:
                # Reelle Version: √2 * Re(Y_l^m) = √2 * cos(m φ) * ...
                terms.append(np.sqrt(2) * Y[:, i].real)
            elif m < 0:
                # Reelle Version: √2 * Im(Y_l^{|m|}) = √2 * sin(|m| φ) * ...
                # -> sph_harm liefert Y_l^m, daher -m für positives m
                idx_pos = np.where((l_for_m == l) & (m_vals == -m))[0][0]
                terms.append(np.sqrt(2) * Y[:, idx_pos].imag)
            else:
                # m == 0
                terms.append(Y[:, i].real)
        A = np.column_stack(terms)
        return A
    else:
        return Y
    
def model_spherical_3(p_order, f_order, x, y, z, coeffs=None, no_a0=False):
    """
    - "reelle" Kugelflächenfunktionen multipliziert mit einfachen Polynomen in r
    """
    r = np.sqrt(x**2 + y**2 + z**2)
    theta = np.arccos(np.clip(z / np.maximum(r, 1e-15), -1, 1))
    phi = np.arctan2(y, x)

    S_harm = spherical_harmonics_vec(f_order, theta, phi, real=True)
    R_poly = terms_x_vec(p_order, r, no_a0=no_a0)

    # Kombination aus R_poly*S_harm
    A = R_poly[:,:,None]*S_harm[:,None,:]
    A = A.reshape(np.atleast_1d(x).shape[0], -1) 

    if coeffs is None:
        return A
    else:
        if np.isscalar(x):
            return (A @ coeffs).item()
        else:
            return A@coeffs

# Kugelflächenfunktionen mit Laquerre Polynomen

def laguerre_terms(order, x, alpha=0, no_a0=False):
    """
    - Hilfsfunktion, berechnet 1D Laguerre-Polynome (vektorisiert) für ein Array x
    - Shape: (len(x), order+1)
    - apha: assoziierte Languerre Polynome in physikalischen Anwendungen
    alpha=0 : Standard Laguerre
    alpha>0 : Polynom wird stärker gegen 0 bei x≈0 gedrückt
    alpha<0 : Polynom hat eine „mehr flache“ Form am Ursprung
    """
    x = np.atleast_1d(x)
    terms = np.column_stack([genlaguerre(n, alpha)(x) for n in range(order+1)])
    if no_a0:
        terms = terms[:, 1:] # Entferne T0
    return terms

def model_spherical_4(p_order, f_order, x, y, z, coeffs=None, no_a0=False):
    """
    - "reale" Kugelflächenfunktionen multipliziert mit einfachen Polynomen in r
    """
    r = np.sqrt(x**2 + y**2 + z**2)
    theta = np.arccos(np.clip(z / np.maximum(r, 1e-15), -1, 1))
    phi = np.arctan2(y, x)

    S_harm = spherical_harmonics_vec(f_order, theta, phi, real=True)
    R_poly = laguerre_terms(p_order, r, no_a0=no_a0)

    # Kombination aus R_poly*S_harm
    A = R_poly[:,:,None]*S_harm[:,None,:]
    A = A.reshape(np.atleast_1d(x).shape[0], -1) 

    if coeffs is None:
        return A
    else:
        if np.isscalar(x):
            return (A @ coeffs).item()
        else:
            return A@coeffs
    
# --------------------------------------------------------------------------------------
# Spezielle Modelle mit Koordinatentransformation für Punkt 1
# --------------------------------------------------------------------------------------

def model_point1_xyz_1(x, y, z, p_order,f_order, l_order, a_coeffs, b_coeffs, coeffs=None):
    """
    - MODELL NUR IM KOORDINATENSYSTEM (x,y,z)
    """
    x = np.atleast_1d(x)
    y = np.atleast_1d(y)
    z = np.atleast_1d(z)

    # Koordinatentransformation
    if len(a_coeffs) == 4:
        a1, a2, a3, a4 = a_coeffs[0], a_coeffs[1], a_coeffs[2], a_coeffs[3]
    else:
        raise ValueError(f"Das Modell 'model_point1_xyz_1' funktioniert nur mit einem Polynom-Modell 4. Ordnung ohne konstanten Term! len(a_coeffs)={len(a_coeffs)}")
    if len(b_coeffs) == 4:
        b1, b2, b3, b4 = b_coeffs[0], b_coeffs[1], b_coeffs[2], b_coeffs[3]
    else:
        raise ValueError(f"Das Modell 'model_point1_xyz_1' funktioniert nur mit einem Polynom-Modell 4. Ordnung ohne konstanten Term! len(b_coeffs)={len(b_coeffs)}")
    
    x0 = x
    y0 = a1*x+a2*x**2+a3**2+a4**2
    z0 = b1*x+b2*x**2+b3**2+b4**2

    #r = np.sqrt((x)**2 + (y)**2 + (z)**2)
    r_prime = np.sqrt((x-x0)**2 + (y-y0)**2 + (z-z0)**2)
    #z_prime = (z-z0)
    z_abs_prime = np.abs(z-z0)
    z_abs = np.abs(z)

    # Design-Matrix

    P_terms = terms_x_vec(p_order, r_prime, no_a0=False)
    F_terms = terms_x_vec(f_order, z_abs_prime, no_a0=False)
    Z_terms = terms_x_vec(l_order, z_abs, no_a0=False)

    # Kombination aus P_terms * F_terms
    PF = P_terms[:,:,None]*F_terms[:,None,:]
    PF = PF.reshape(np.atleast_1d(x).shape[0], -1)

    # Kombination aus Pf und Z_terms
    A = np.concatenate([PF, Z_terms], axis=1)

    if coeffs is None:
        return A
    else:
        if np.isscalar(x):
            return (A @ coeffs).item()
        else:
            return A@coeffs
        
def model_point1_xyz_2(x, y, z, a_coeffs, b_coeffs, coeffs=None):
    """
    - ACHTUNG: MODELL NUR IM KOORDINATENSYSTEM (x,y,z)
    - speziell für Punkt 1 erstelltes Modell mit Betragsfunktionen und Koordinatentransformation durch den Pfad-Fit
    """

    x = np.atleast_1d(x)
    y = np.atleast_1d(y)
    z = np.atleast_1d(z)

    # Koordinatentransformation
    if len(a_coeffs) == 4:
        a1, a2, a3, a4 = a_coeffs[0], a_coeffs[1], a_coeffs[2], a_coeffs[3]
    else:
        raise ValueError(f"Das Modell 'model_point1_xyz_2' funktioniert nur mit einem Polynom-Modell 4. Ordnung ohne konstanten Term! len(a_coeffs)={len(a_coeffs)}")
    if len(b_coeffs) == 4:
        b1, b2, b3, b4 = b_coeffs[0], b_coeffs[1], b_coeffs[2], b_coeffs[3]
    else:
        raise ValueError(f"Das Modell 'model_point1_xyz_2' funktioniert nur mit einem Polynom-Modell 4. Ordnung ohne konstanten Term! len(b_coeffs)={len(b_coeffs)}")
    
    x0 = x
    y0 = a1*x+a2*x**2+a3**2+a4**2
    z0 = b1*x+b2*x**2+b3**2+b4**2

    #r = np.sqrt((x)**2 + (y)**2 + (z)**2)
    r_prime = np.sqrt((x-x0)**2 + (y-y0)**2 + (z-z0)**2)
    #z_prime = (z-z0)
    #z_abs_prime = np.abs(z-z0)
    z_abs = np.abs(z)

    # Design-Matrix

    A = [r_prime,
         r_prime*z_abs, 
         r_prime*z_abs**2,
         r_prime*z_abs**3,
         r_prime*z_abs**4,
         r_prime*z_abs**5,
         z,
         z_abs]
    A = np.column_stack(A)

    if coeffs is None:
        return A
    else:
        if np.isscalar(x):
            return (A @ coeffs).item()
        else:
            return A@coeffs

# --------------------------------------------------------------------------------------
# Pfadfunktionen
# --------------------------------------------------------------------------------------

def model_path_1(p_order, f_order, t, rho, phi, symmetry=None, coeffs=None, no_a0=False):
    """
    - keine explizite t-Abhängigkeit
    - Polynomansatz für rho - p_order
    - Fourieransatz für phi - f_order
    """
    t = np.atleast_1d(t)
    rho = np.atleast_1d(rho)
    phi = np.atleast_1d(phi)
    s = 1 if symmetry is None else symmetry

    # Polynom-Designmatrix in rho
    A_poly = terms_x_vec(p_order, rho, no_a0=no_a0)

    # Fourier-Terme
    fourier_terms = []
    for n in range(1, f_order+1):
        an = s*n*phi
        fourier_terms.extend([np.sin(an), np.cos(an)])
    A_fourier = np.column_stack(fourier_terms)

    # Kombination A_poly*A_fourier
    A = A_poly[:,:,None]*A_fourier[:,None,:]
    A = A.reshape(np.atleast_1d(t).shape[0], -1) 

    if coeffs is None:
        return A
    else:
        if np.isscalar(t):
            return (A @ coeffs).item()
        else:
            return A@coeffs

def model_path_2(p_order, f_order, l_order, t, rho, phi, symmetry=None, coeffs=None, no_a0=False):
    """
    - Polynomansatz für rho - p_order
    - Fourieransatz für phi - f_order
    - Polynomansatz für t - l_order
    """
    t = np.atleast_1d(t)
    rho = np.atleast_1d(rho)
    phi = np.atleast_1d(phi)
    s = 1 if symmetry is None else symmetry

    # Polynom-Designmatrix in rho
    L_poly = terms_x_vec(l_order, t, no_a0=no_a0)
    P_poly = terms_x_vec(p_order, rho, no_a0=no_a0)
    
    # Fourier-Terme
    fourier_terms = []
    for n in range(1, f_order+1):
        an = s*n*phi
        fourier_terms.extend([np.sin(an), np.cos(an)])
    F_fourier = np.column_stack(fourier_terms)

    # Kombination P_poly*F_fourier*L_poly
    A1 = P_poly[:,:,None, None]*F_fourier[:,None,:, None]*L_poly[:, None, None, :]
    A1 = A1.reshape(np.atleast_1d(t).shape[0], -1) 

    # Kombination aus A_fourier und A_poly
    A = np.concatenate([L_poly, A1], axis=1)

    if coeffs is None:
        return A
    else:
        if np.isscalar(t):
            return (A @ coeffs).item()
        else:
            return A@coeffs
        
# --------------------------------------------------------------------------------------

def model_path_3(p_order, f_order, l_order, t, rho, phi, symmetry=None, coeffs=None, no_a0=False):
    """
    - keine explizite t-Abhängigkeit
    - Polynomansatz für rho - p_order
    - Fourieransatz für phi sin-Terme f_order
    - Fourieransatz für phi cos-Terme l_order
    """
    t = np.atleast_1d(t)
    rho = np.atleast_1d(rho)
    phi = np.atleast_1d(phi)

    s = 1 if symmetry is None else symmetry

    # Polynome in rho
    A_rho = terms_x_vec(p_order, rho, no_a0=no_a0) #shape(N, p_order)

    # Fourier-Terme
    m_vals = np.arange(1, f_order+1)
    A_sin = np.sin(s*phi[:,None]*m_vals[None,:]) #shape(N, f_order)

    k_vals = np.arange(1, l_order+1)
    A_cos = np.cos(s*phi[:,None]*k_vals[None,:]) #shape(N, l_order)

    # Tensorprodukte: Kombination zu a_{nmk}
    A_sin_full = A_rho[:, :, None] * A_sin[:, None, :]
    A_cos_full = A_rho[:, :, None] * A_cos[:, None, :]
    A = np.concatenate([A_sin_full.reshape(len(rho), -1), A_cos_full.reshape(len(rho), -1) ], axis=1) # flach machen

    if coeffs is None:
        return A
    else:
        if np.isscalar(t):
            return (A @ coeffs).item()
        else:
            return A@coeffs

def model_path_4(p_order, f_order, l_order, k_order, t, rho, phi, symmetry=None, coeffs=None):
    """
    - Polynomansatz für rho - p_order ab 1. Ordnung
    - Fourieransatz für phi sin-Terme f_order
    - Fourieransatz für phi cos-Terme l_order
    - Polynomansatz für t - k_order inkl. 0-te Ordnung
    """
    t = np.atleast_1d(t)
    rho = np.atleast_1d(rho)
    phi = np.atleast_1d(phi)
    N = len(t)

    s = 1 if symmetry is None else symmetry

    # Polynome in rho
    p_vals = np.arange(1, p_order+1)
    A_rho = rho[:, None] ** p_vals[None, :] #shape(N, p_order)

    # Polynome in t
    k_vals = np.arange(0, k_order+1)
    A_t   = t[:, None] ** k_vals[None, :] #shape(N, k_order+1)

    # Fourier-Terme
    f_vals = np.arange(1, f_order+1)
    A_sin = np.sin(s*phi[:,None]*f_vals[None,:]) #shape(N, f_order)

    l_vals = np.arange(1, l_order+1)
    A_cos = np.cos(s*phi[:,None]*l_vals[None,:]) #shape(N, l_order)

    # Tensorprodukte
    A_tr = A_t[:, :, None] * A_rho[:, None, :] # shape(N, p_order, k_order+1)
    A_tr = A_tr.reshape(N, -1) # shape(N, p_order * (k_order+1))

    A_sin_full = A_tr[:, :, None] * A_sin[:, None, :] # shape(N, p_order * (k_order+1), f_order)
    A_sin_full = A_sin_full.reshape(N, -1) # shape(N, p_order * (k_order+1) *f_order)

    A_cos_full = A_tr[:, :, None] * A_cos[:, None, :] # shape(N, p_order * (k_order+1), l_order)
    A_cos_full = A_cos_full.reshape(N, -1) # shape(N, p_order * (k_order+1) *l_order)

    A = np.concatenate([A_sin_full, A_cos_full], axis=1) # shape(N, p_order * (k_order+1) *f_order + p_order * (k_order+1) *l_order)

    if coeffs is None:
        return A
    else:
        if np.isscalar(t):
            return (A @ coeffs).item()
        else:
            return A@coeffs

def model_path_5(p_order, l_order, k_order, t, rho, phi, symmetry=None, coeffs=None):
    """
    - Polynomansatz für rho - p_order ab 1. Ordnung
    - keine Sinus-Terme
    - Fourieransatz für phi cos-Terme l_order
    - Polynomansatz für t - k_order inkl. 0-te Ordnung
    """
    t = np.atleast_1d(t)
    rho = np.atleast_1d(rho)
    phi = np.atleast_1d(phi)

    s = 1 if symmetry is None else symmetry

    # Polynome in rho
    p_vals = np.arange(1, p_order+1)
    A_rho = rho[:, None] ** p_vals[None, :] #shape(N, p_order)

    # Polynome in t
    k_vals = np.arange(0, k_order+1)
    A_t   = t[:, None] ** k_vals[None, :] #shape(N, k_order)

    # Fourier-Terme
    l_vals = np.arange(1, l_order+1)
    A_cos = np.cos(s*phi[:,None]*l_vals[None,:]) #shape(N, l_order)

    # Tensorprodukte: Kombination zu a_{nmk}
    A_tr = A_t[:, :, None] * A_rho[:, None, :]
    A_full = A_tr[:, :, :, None] * A_cos[:, None, None, :]
    A = A_full.reshape(len(t), -1)  # flach machen

    if coeffs is None:
        return A
    else:
        if np.isscalar(t):
            return (A @ coeffs).item()
        else:
            return A@coeffs
        
def model_path_6(p_order, f_order, l_order, t, rho, phi, symmetry=None, coeffs=None):
    """
    - Polynomansatz für rho - p_order ab 1. Ordnung
    - Fourieransatz für phi sin-Terme f_order
    - Fourieransatz für phi cos-Terme l_order
    - keine Ordnung in t
    """
    rho = np.atleast_1d(rho)
    phi = np.atleast_1d(phi)

    s = 1 if symmetry is None else symmetry

    # Polynome in rho
    p_vals = np.arange(1, p_order+1)
    A_rho = rho[:, None] ** p_vals[None, :] #shape(N, p_order)

    # Fourier-Terme
    f_vals = np.arange(1, f_order+1)
    A_sin = np.sin(s*phi[:,None]*f_vals[None,:]) #shape(N, f_order)

    l_vals = np.arange(1, l_order+1)
    A_cos = np.cos(s*phi[:,None]*l_vals[None,:]) #shape(N, l_order)

    # Tensorprodukte: Kombination zu a_{nmk}
    A_sin_full = A_rho[:, :, None] * A_sin[:, None, :]   # shape (N, p_order, f_order)
    A_cos_full = A_rho[:, :, None] * A_cos[:, None, :]   # shape (N, p_order, l_order)

    A = np.concatenate([A_sin_full.reshape(len(t), -1), A_cos_full.reshape(len(t), -1) ], axis=1) # flach machen

    if coeffs is None:
        return A
    else:
        if np.isscalar(t):
            return (A @ coeffs).item()
        else:
            return A@coeffs
        
# --------------------------------------------------------------------------------------
# Modelle für Punkt 1

def model_path_abs_1(p_order, f_order, l_order, k_order, t, rho, phi, symmetry=None, coeffs=None):
    """
    - Funktion mit t^j rho^p |sin(a phi)| Terme
    """
    t = np.atleast_1d(t)
    rho = np.atleast_1d(rho)
    phi = np.atleast_1d(phi)

    s = 1 if symmetry is None else symmetry
    N = len(t)

    # Polynome in rho
    p_vals = np.arange(1, p_order+1)
    A_rho = rho[:, None] ** p_vals[None, :] #shape(N, p_order)

    # Polynome in t
    k_vals = np.arange(0, k_order+1)
    A_t   = t[:, None] ** k_vals[None, :] #shape(N, k_order)

    # |sin(s phi)| - Term
    A_abs_sin = np.abs(np.sin(s * phi))[:, None, None]  # (N,1,1)

    # Fourier-Terme
    f_vals = np.arange(1, f_order+1)
    A_sin = np.sin(s*phi[:,None]*f_vals[None,:]) #shape(N, f_order)

    l_vals = np.arange(1, l_order+1)
    A_cos = np.cos(s*phi[:,None]*l_vals[None,:]) #shape(N, l_order)

    # Tensorprodukte: Kombination zu a_{nmk}
    A_tr = A_t[:, :, None] * A_rho[:, None, :] # shape(N, T, R)
    A_abs_full = A_tr * A_abs_sin # shape(N, T,R )
    A1 = A_abs_full.reshape(N, -1) 

    A_sin_full = A_tr[:, :, :, None] * A_sin[:, None, None, :] # shape(N, T, R, M)
    A2 = A_sin_full.reshape(N, -1)

    A_cos_full = A_tr[:, :, :, None] * A_cos[:, None, None, :] # shape(N, T, R, K)
    A3 = A_cos_full.reshape(N, -1)

    # Gesamtmatrix
    A = np.concatenate([A1, A2, A3], axis=1)

    if coeffs is None:
        return A
    else:
        if np.isscalar(t):
            return (A @ coeffs).item()
        else:
            return A@coeffs
        
def model_path_abs_2(p_order, f_order, l_order, k_order, t, rho, phi, symmetry=None, coeffs=None):
    """
    - Funktion mit t^j rho^p |sin(a phi)| Terme
    """
    t = np.atleast_1d(t)
    rho = np.atleast_1d(rho)
    phi = np.atleast_1d(phi)

    s = 1 if symmetry is None else symmetry
    N = len(t)

    # Polynome in rho
    p_vals = np.arange(1, p_order+1)
    A_rho = rho[:, None] ** p_vals[None, :] #shape(N, p_order)

    # Polynome in t
    k_vals = np.arange(0, k_order+1)
    A_t   = t[:, None] ** k_vals[None, :] #shape(N, k_order)

    # |sin(a phi)| - Term
    A_abs_sin = np.abs(np.sin(phi))[:, None, None]  # (N,1,1)

    # |cos(a phi)| - Term
    A_abs_cos = np.abs(np.cos(phi))[:, None, None]  # (N,1,1)

    # Fourier-Terme
    f_vals = np.arange(1, f_order+1)
    A_sin = np.sin(s*phi[:,None]*f_vals[None,:]) #shape(N, f_order)

    l_vals = np.arange(1, l_order+1)
    A_cos = np.cos(s*phi[:,None]*l_vals[None,:]) #shape(N, l_order)

    # Tensorprodukte: Kombination zu a_{nmk}
    A_tr = A_t[:, :, None] * A_rho[:, None, :] # shape(N, T, R)
    A_abs_full = A_tr * A_abs_sin # shape(N, T,R )
    A1s = A_abs_full.reshape(N, -1) 

    A_abs_cos_full = A_tr * A_abs_cos
    A1c = A_abs_cos_full.reshape(N, -1)

    A_sin_full = A_tr[:, :, :, None] * A_sin[:, None, None, :] # shape(N, T, R, M)
    A2 = A_sin_full.reshape(N, -1)

    A_cos_full = A_tr[:, :, :, None] * A_cos[:, None, None, :] # shape(N, T, R, K)
    A3 = A_cos_full.reshape(N, -1)

    # Gesamtmatrix
    A = np.concatenate([A1s, A1c, A2, A3], axis=1)

    if coeffs is None:
        return A
    else:
        if np.isscalar(t):
            return (A @ coeffs).item()
        else:
            return A@coeffs
        
def model_path_abs_3(p_order, f_order, l_order, k_order, t, rho, phi, symmetry=None, coeffs=None):
    """
    - Funktion mit t^j rho^p |sin(a phi)| Terme
    - wie model_path_abs_2, nur dass alle Terme für rho erlaubt sind! np.arange(0, p_order+1) anstatt np.arange(1, p_order+1)
    """
    t = np.atleast_1d(t)
    rho = np.atleast_1d(rho)
    phi = np.atleast_1d(phi)

    s = 1 if symmetry is None else symmetry
    N = len(t)

    # Polynome in rho
    p_vals = np.arange(0, p_order+1)
    A_rho = rho[:, None] ** p_vals[None, :] #shape(N, p_order)
    
    # Polynome in t
    k_vals = np.arange(0, k_order+1)
    A_t   = t[:, None] ** k_vals[None, :] #shape(N, k_order)

    # |sin(a phi)| - Term
    A_abs_sin = np.abs(np.sin(phi))[:, None, None]  # (N,1,1)

    # |cos(a phi)| - Term
    A_abs_cos = np.abs(np.cos(phi))[:, None, None]  # (N,1,1)

    # Fourier-Terme
    f_vals = np.arange(1, f_order+1)
    A_sin = np.sin(s*phi[:,None]*f_vals[None,:]) #shape(N, f_order)

    l_vals = np.arange(1, l_order+1)
    A_cos = np.cos(s*phi[:,None]*l_vals[None,:]) #shape(N, l_order)

    # Tensorprodukte: Kombination zu a_{nmk}
    A_tr = A_t[:, :, None] * A_rho[:, None, :] # shape(N, T, R)
    A_abs_full = A_tr * A_abs_sin # shape(N, T,R )
    A1s = A_abs_full.reshape(N, -1) 

    A_abs_cos_full = A_tr * A_abs_cos
    A1c = A_abs_cos_full.reshape(N, -1)

    A_sin_full = A_tr[:, :, :, None] * A_sin[:, None, None, :] # shape(N, T, R, M)
    A2 = A_sin_full.reshape(N, -1)

    A_cos_full = A_tr[:, :, :, None] * A_cos[:, None, None, :] # shape(N, T, R, K)
    A3 = A_cos_full.reshape(N, -1)

    # Gesamtmatrix
    A = np.concatenate([A1s, A1c, A2, A3], axis=1)

    if coeffs is None:
        return A
    else:
        if np.isscalar(t):
            return (A @ coeffs).item()
        else:
            return A@coeffs
        
# Finales Modell für Banddifferenz
def model_path_abs_4(p_order, f_order, l_order, k_order, t, rho, phi, symmetry=None, coeffs=None, eps=1e-1):
    """
    Glatt gemachte Version von model_path_abs_3:
    |sin(phi)| -> sqrt(sin^2(phi) + eps)
    |cos(phi)| -> sqrt(cos^2(phi) + eps)

    eps steuert die Glattheit der Knickstellen.
    - bei rho=0 wird phi=0 gesetzt
    - Ordnung in rho ab 1
    """

    t   = np.atleast_1d(t)
    rho = np.atleast_1d(rho)
    phi = np.atleast_1d(phi)

    phi = np.where(rho == 0, 0.0, phi)

    s = 1 if symmetry is None else symmetry
    N = len(t)

    # Polynome 
    p_vals = np.arange(1, p_order + 1)
    k_vals = np.arange(0, k_order + 1)

    A_rho = rho[:, None] ** p_vals[None, :]
    A_t   = t[:, None]   ** k_vals[None, :]

    # Tensorprodukt t,rho 
    A_tr = A_t[:, :, None] * A_rho[:, None, :]   # (N, K, P)

    # Glatte Winkelfunktionen
    A_abs_sin = np.sqrt(np.sin(s * phi)**2 + eps)[:, None, None]
    A_abs_cos = np.sqrt(np.cos(s * phi)**2 + eps)[:, None, None]

    A1s = (A_tr * A_abs_sin).reshape(N, -1)
    A1c = (A_tr * A_abs_cos).reshape(N, -1)

    # Fourier-Terme
    f_vals = np.arange(1, f_order + 1)
    l_vals = np.arange(1, l_order + 1)

    A_sin = np.sin(s * phi[:, None] * f_vals[None, :])
    A_cos = np.cos(s * phi[:, None] * l_vals[None, :])

    A2 = (A_tr[:, :, :, None] * A_sin[:, None, None, :]).reshape(N, -1)
    A3 = (A_tr[:, :, :, None] * A_cos[:, None, None, :]).reshape(N, -1)

    A = np.concatenate([A1s, A1c, A2, A3], axis=1)

    if coeffs is None:
        return A
    else:
        return (A @ coeffs).item() if np.isscalar(t) else A @ coeffs

# Finales Modell für Bänder
def model_path_abs_5(p_order, f_order, l_order, k_order, t, rho, phi, symmetry=None, coeffs=None, eps=1e-1):
    """
    Glatt gemachte Version von model_path_abs_3:
    |sin(phi)| -> sqrt(sin^2(phi) + eps)
    |cos(phi)| -> sqrt(cos^2(phi) + eps)

    eps steuert die Glattheit der Knickstellen.
    - bei rho=0 wird phi=0 gesetzt
    - Ordnung in rho ab 0
    """

    t   = np.atleast_1d(t)
    rho = np.atleast_1d(rho)
    phi = np.atleast_1d(phi)

    phi = np.where(rho == 0, 0.0, phi)

    s = 1 if symmetry is None else symmetry
    N = len(t)

    # Polynome 
    p_vals = np.arange(0, p_order + 1)
    k_vals = np.arange(0, k_order + 1)

    A_rho = rho[:, None] ** p_vals[None, :]
    A_t   = t[:, None]   ** k_vals[None, :]

    # Tensorprodukt t,rho 
    A_tr = A_t[:, :, None] * A_rho[:, None, :]   # (N, K, P)

    # Glatte Winkelfunktionen
    A_abs_sin = np.sqrt(np.sin(s * phi)**2 + eps)[:, None, None]
    A_abs_cos = np.sqrt(np.cos(s * phi)**2 + eps)[:, None, None]

    A1s = (A_tr * A_abs_sin).reshape(N, -1)
    A1c = (A_tr * A_abs_cos).reshape(N, -1)

    # Fourier-Terme
    f_vals = np.arange(1, f_order + 1)
    l_vals = np.arange(1, l_order + 1)

    A_sin = np.sin(s * phi[:, None] * f_vals[None, :])
    A_cos = np.cos(s * phi[:, None] * l_vals[None, :])

    A2 = (A_tr[:, :, :, None] * A_sin[:, None, None, :]).reshape(N, -1)
    A3 = (A_tr[:, :, :, None] * A_cos[:, None, None, :]).reshape(N, -1)

    A = np.concatenate([A1s, A1c, A2, A3], axis=1)

    if coeffs is None:
        return A
    else:
        return (A @ coeffs).item() if np.isscalar(t) else A @ coeffs

# --------------------------------------------------------------------------------------
# Modelle für Punkt 2

def model_path_point2_1(p_order, k_order, p1_order, p2_order, p3_order, t, rho, phi, a_coeffs, coeffs=None):

    scalar_input = np.isscalar(t)
    t   = np.atleast_1d(t)
    rho = np.atleast_1d(rho)
    phi = np.atleast_1d(phi)

    N_t = len(t)

    # Pfade laden und chi(t) berechnen

    if len(a_coeffs) != 5:
        raise ValueError(f"Das Modell 'model_path_point2_1' funktioniert nur mit einem Polynom-Modell 4. Ordnung mit konstanten Term! len(a_coeffs)={len(a_coeffs)}")

    B = np.array([1.0, 1.0, -2.0])
    B = B / np.linalg.norm(B) # Normierung
    B = np.tile(B, (len(t), 1))   # shape (t,3)
    N = np.array([1.0, -1.0, 0.0])
    N = N / np.linalg.norm(N)
    N = np.tile(N, (len(t), 1))   # shape (t,3)

    rA = pathmodels.r_point2A(t)                                     # shape: (t, 3)
    rB1, _, _ = pathmodels.r_point2B(t, a_coeffs, 0)                # shape: (t, 3)
    rB2, _ , _ = pathmodels.r_point2B(t, a_coeffs, (2/3)*np.pi)     # shape: (t, 3)
    rB3, _ , _ = pathmodels.r_point2B(t, a_coeffs, (4/3)*np.pi)     # shape: (t, 3)

    rx = rA[:, 0] + rho*np.sin(phi)*N[:, 0] + rho*np.cos(phi)*B[:, 0]
    ry = rA[:, 1] + rho*np.sin(phi)*N[:, 1] + rho*np.cos(phi)*B[:, 1]
    rz = rA[:, 2] + rho*np.sin(phi)*N[:, 2] + rho*np.cos(phi)*B[:, 2]

    chi1 = np.sqrt( (rx-rB1[:, 0])**2 + (ry-rB1[:, 1])**2 + (rz-rB1[:, 2])**2 )
    chi2 = np.sqrt( (rx-rB2[:, 0])**2 + (ry-rB2[:, 1])**2 + (rz-rB2[:, 2])**2 )
    chi3 = np.sqrt( (rx-rB3[:, 0])**2 + (ry-rB3[:, 1])**2 + (rz-rB3[:, 2])**2 )

    # Modell in t, rho, phi, chiB1, chiB2, chiB3

    # Polynome
    p_vals = np.arange(1, p_order + 1)
    k_vals = np.arange(0, k_order + 1)
    p1_vals = np.arange(1, p1_order + 1)
    p2_vals = np.arange(1, p2_order + 1)
    p3_vals = np.arange(1, p3_order + 1)

    A_rho = rho[:, None] ** p_vals[None, :]
    A_t   = t[:, None] ** k_vals[None, :]
    A_chi1 = chi1[:, None] ** p1_vals[None, :]
    A_chi2 = chi2[:, None] ** p2_vals[None, :]
    A_chi3 = chi3[:, None] ** p3_vals[None, :]

    # Tensorprodukt
    A_poly = A_t[:, :, None, None, None, None] * A_rho[:, None, :, None, None, None] * A_chi1[:, None, None, :, None, None] * A_chi2[:, None, None, None, :, None] * A_chi3[:, None, None, None, None, :]

    # Gesamtmatrix
    A = A_poly.reshape(N_t, -1)

    if coeffs is None:
        return A
    else:
        return (A @ coeffs).item() if scalar_input else A @ coeffs

# Finales Modell für Banddifferenz
def model_path_point2_2(p_order, k_order, p1_order, t, rho, phi, a_coeffs, symmetry=None, coeffs=None, eps=1e-8):

    scalar_input = np.isscalar(t)
    t   = np.atleast_1d(t)
    rho = np.atleast_1d(rho)
    phi = np.atleast_1d(phi)

    s = 1 if symmetry is None else symmetry
    N_t = len(t)

    # Pfade laden und chi(t) berechnen

    if len(a_coeffs) != 5:
        raise ValueError(f"Das Modell 'model_path_point2_2' funktioniert nur mit einem Polynom-Modell 4. Ordnung mit konstanten Term! len(a_coeffs)={len(a_coeffs)}")

    rB1, rhoB1, _ = pathmodels.r_point2B(t, a_coeffs, 0)                # shape: (t, 3)
    chi1 = np.sqrt( rho**2 + rhoB1**2 - 2*rho*rhoB1*np.cos(s*phi)+eps)
    # Modell in t, rho, phi, chiB1, chiB2, chiB3

    # Polynome
    p_vals = np.arange(1, p_order + 1)
    k_vals = np.arange(0, k_order + 1)
    p1_vals = np.arange(0, p1_order + 1)

    A_rho = rho[:, None] ** p_vals[None, :]
    A_t   = t[:, None] ** k_vals[None, :]
    A_chi1 = chi1[:, None] ** p1_vals[None, :]

    # Tensorprodukt
    A_poly = A_t[:, :, None, None] * A_rho[:, None, :, None] * A_chi1[:, None, None, :]

    # Gesamtmatrix
    A = A_poly.reshape(N_t, -1)

    if coeffs is None:
        return A
    else:
        return (A @ coeffs).item() if scalar_input else A @ coeffs 

# Finales Modell für Bänder
def model_path_point2_3(p_order, k_order, p1_order, t, rho, phi, a_coeffs, symmetry=None, coeffs=None, eps=1e-8):

    scalar_input = np.isscalar(t)
    t   = np.atleast_1d(t)
    rho = np.atleast_1d(rho)
    phi = np.atleast_1d(phi)

    s = 1 if symmetry is None else symmetry
    N_t = len(t)

    # Pfade laden und chi(t) berechnen

    if len(a_coeffs) != 5:
        raise ValueError(f"Das Modell 'model_path_point2_3' funktioniert nur mit einem Polynom-Modell 4. Ordnung mit konstanten Term! len(a_coeffs)={len(a_coeffs)}")

    rB1, rhoB1, _ = pathmodels.r_point2B(t, a_coeffs, 0)                # shape: (t, 3)
    chi1 = np.sqrt( rho**2 + rhoB1**2 - 2*rho*rhoB1*np.cos(s*phi)+eps)
    # Modell in t, rho, phi, chiB1, chiB2, chiB3

    # Polynome
    p_vals = np.arange(0, p_order + 1)
    k_vals = np.arange(0, k_order + 1)
    p1_vals = np.arange(0, p1_order + 1)

    A_rho = rho[:, None] ** p_vals[None, :]
    A_t   = t[:, None] ** k_vals[None, :]
    A_chi1 = chi1[:, None] ** p1_vals[None, :]

    # Tensorprodukt
    A_poly = A_t[:, :, None, None] * A_rho[:, None, :, None] * A_chi1[:, None, None, :]

    # Gesamtmatrix
    A = A_poly.reshape(N_t, -1)

    if coeffs is None:
        return A
    else:
        return (A @ coeffs).item() if scalar_input else A @ coeffs 
    
# --------------------------------------------------------------------------------------
# Modelle für Punkt 3

def model_path_point3_1(p_order, l_order, k_order, t, rho, phi, symmetry=None, coeffs=None, eps=1e-1):
    """
    |cos(phi)| -> sqrt(cos^2(phi) + eps)

    eps steuert die Glattheit der Knickstellen.
    - bei rho=0 wird phi=0 gesetzt
    - Ordnung in rho ab 1
    """

    t   = np.atleast_1d(t)
    rho = np.atleast_1d(rho)
    phi = np.atleast_1d(phi)

    phi = np.where(rho == 0, 0.0, phi)

    s = 1 if symmetry is None else symmetry
    N = len(t)

    # Polynome 
    p_vals = np.arange(1, p_order + 1)
    k_vals = np.arange(0, k_order + 1)

    A_rho = rho[:, None] ** p_vals[None, :]
    A_t   = t[:, None]   ** k_vals[None, :]

    # Tensorprodukt t,rho 
    A_tr = A_t[:, :, None] * A_rho[:, None, :]   # (N, K, P)
    # Glatte Winkelfunktionen
    A_abs_cos = np.sqrt(np.cos(s * phi)**2 + eps)[:, None, None]

    A1c = (A_tr * A_abs_cos).reshape(N, -1)

    # Fourier-Terme
    l_vals = np.arange(1, l_order + 1)

    A_cos = np.cos(s * phi[:, None] * l_vals[None, :])
    A3 = (A_tr[:, :, :, None] * A_cos[:, None, None, :]).reshape(N, -1)
    A = np.concatenate([A1c, A3], axis=1)

    if coeffs is None:
        return A
    else:
        return (A @ coeffs).item() if np.isscalar(t) else A @ coeffs

# Finales Modell für Banddifferenz
def model_path_point3_2(p_order, l_order, k_order, t, rho, phi, symmetry=None, coeffs=None):
    """
    - bei rho=0 wird phi=0 gesetzt
    - Ordnung in rho ab 1
    """
    t   = np.atleast_1d(t)
    rho = np.atleast_1d(rho)
    phi = np.atleast_1d(phi)
    phi = np.where(rho == 0, 0.0, phi)

    s = 1 if symmetry is None else symmetry
    N = len(t)

    # Polynome 
    p_vals = np.arange(1, p_order + 1)
    k_vals = np.arange(0, k_order + 1)

    A_rho = rho[:, None] ** p_vals[None, :]
    A_t   = t[:, None]   ** k_vals[None, :]

    # Tensorprodukt t,rho 
    A_tr = A_t[:, :, None] * A_rho[:, None, :]   # (N, K, P)

    # Fourier-Terme
    l_vals = np.arange(0, l_order + 1)
    A_cos = np.cos(s * phi[:, None] * l_vals[None, :])

    A = (A_tr[:, :, :, None] * A_cos[:, None, None, :]).reshape(N, -1)

    if coeffs is None:
        return A
    else:
        return (A @ coeffs).item() if np.isscalar(t) else A @ coeffs
    
# Finales Modell für Bänder
def model_path_point3_3(p_order, l_order, k_order, t, rho, phi, symmetry=None, coeffs=None):
    """
    - bei rho=0 wird phi=0 gesetzt
    - Ordnung in rho ab 0
    """

    t   = np.atleast_1d(t)
    rho = np.atleast_1d(rho)
    phi = np.atleast_1d(phi)

    phi = np.where(rho == 0, 0.0, phi)

    s = 1 if symmetry is None else symmetry
    N = len(t)

    # Polynome 
    p_vals = np.arange(0, p_order + 1)
    k_vals = np.arange(0, k_order + 1)

    A_rho = rho[:, None] ** p_vals[None, :]
    A_t   = t[:, None]   ** k_vals[None, :]

    # Tensorprodukt t,rho 
    A_tr = A_t[:, :, None] * A_rho[:, None, :]   # (N, K, P)

    # Fourier-Terme
    l_vals = np.arange(0, l_order + 1)
    A_cos = np.cos(s * phi[:, None] * l_vals[None, :])

    A = (A_tr[:, :, :, None] * A_cos[:, None, None, :]).reshape(N, -1)

    if coeffs is None:
        return A
    else:
        return (A @ coeffs).item() if np.isscalar(t) else A @ coeffs