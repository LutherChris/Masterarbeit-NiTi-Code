import numpy as np
from scipy.optimize import minimize_scalar

import lib.qe_model_models as models_models

# ######################################################################################
# Modelle zur Berechnung des Pfades
# ######################################################################################

def path_point1(y_order, z_order, x_model, coeffs=None, no_a0=False):
    """
    - Modell für Punkt 1 der Form:
    [None, [1, x, x**2, ...], [1, x, x**2, ...]]
    """
    A_y = models_models.terms_x_vec(y_order, x_model, no_a0=no_a0)
    A_z = models_models.terms_x_vec(z_order, x_model, no_a0=no_a0)

    # Auswertung:
    if coeffs is None:
        return [None, A_y, A_z]
    else:
        if np.isscalar(x_model):
            y = A_y@coeffs[1].item()
            z = A_z@coeffs[2].item()
            return [x_model, y, z]
        else:
            y = A_y@coeffs[1]
            z = A_z@coeffs[2]
            return [x_model, y, z]
        
def path_point2(x_order, y_order, z_order, x_model, coeffs=None, no_a0=False):
    """
    - x = t der (ttt)-Achse
    - Modell für Punkt 2 der Form:
    [[1, x, x**2, ...], [1, x, x**2, ...], [1, x, x**2, ...]]
    """
    A_x = models_models.terms_x_vec(x_order, x_model, no_a0=no_a0)
    A_y = models_models.terms_x_vec(y_order, x_model, no_a0=no_a0)
    A_z = models_models.terms_x_vec(z_order, x_model, no_a0=no_a0)

    # Auswertung:
    if coeffs is None:
        return [A_x, A_y, A_z]
    else:
        if np.isscalar(x_model):
            x_ = A_x@coeffs[0].item()
            y_ = A_y@coeffs[1].item()
            z_ = A_z@coeffs[2].item()
            return [x_, y_, z_]
        else:
            x_ = A_x@coeffs[0]
            y_ = A_y@coeffs[1]
            z_ = A_z@coeffs[2]
            return [x_, y_, z_]

# ######################################################################################
# Koordinatentransformationen
# ######################################################################################

# --------------------------------------------------------------------------------------
# Punkt 1
# --------------------------------------------------------------------------------------

def r_point1(t, a, b):
    """
    - Funktion der Raumkurve (t, Ordnung 4, Ordnung 4)
    """
    a1, a2, a3, a4 = a[0], a[1], a[2], a[3]
    b1, b2, b3, b4 = b[0], b[1], b[2], b[3]
    t = np.atleast_1d(t).astype(float)
    rx = t
    ry = a1*t + a2*t**2 + a3*t**3 + a4*t**4
    rz = b1*t + b2*t**2 + b3*t**3 + b4*t**4
    r = np.stack([rx, ry, rz], axis=-1)
    return r

def dr_point1(t, a, b):
    """
    - erste Ableitung der Raumkurve (t, Ordnung 4, Ordnung 4)
    """
    a1, a2, a3, a4 = a[0], a[1], a[2], a[3]
    b1, b2, b3, b4 = b[0], b[1], b[2], b[3]
    t = np.atleast_1d(t).astype(float)
    drx = np.ones_like(t).astype(float)
    dry = a1 + 2*a2*t + 3*a3*t**2 + 4*a4*t**3
    drz = b1 + 2*b2*t + 3*b3*t**2 + 4*b4*t**3
    dr = np.stack([drx, dry, drz], axis=-1)
    return dr

def ddr_point1(t, a, b):
    """
    - zweite Ableitung der Raumkurve (t, Ordnung 4, Ordnung 4)
    """
    a1, a2, a3, a4 = a[0], a[1], a[2], a[3]
    b1, b2, b3, b4 = b[0], b[1], b[2], b[3]
    t = np.atleast_1d(t).astype(float)
    ddrx = np.zeros_like(t).astype(float)
    ddry = 2*a2 + 6*a3*t + 12*a4*t**2
    ddrz = 2*b2 + 6*b3*t + 12*b4*t**2
    ddr = np.stack([ddrx, ddry, ddrz], axis=-1)
    return ddr

def dddr_point1(t, a, b):
    """
    - dritte Ableitung der Raumkurve (t, Ordnung 4, Ordnung 4)
    """
    a1, a2, a3, a4 = a[0], a[1], a[2], a[3]
    b1, b2, b3, b4 = b[0], b[1], b[2], b[3]
    t = np.atleast_1d(t).astype(float)
    dddrx = np.zeros_like(t).astype(float)
    dddry = 6*a3 + 24*a4*t
    dddrz = 6*b3 + 24*b4*t
    dddr = np.stack([dddrx, dddry, dddrz], axis=-1)
    return dddr

# --------------------------------------------------------------------------------------
# Punkt 1 Center (Zentrum der Schale)
# --------------------------------------------------------------------------------------

def r_point1_center(t):
    """
    - Funktion der Raumkurve entlang der 100-Richtung für Punkt1 (Zentrum der Schale)
    """
    t = np.atleast_1d(t).astype(float)
    zeros = np.zeros_like(t).astype(float)
    r = np.stack([t, zeros, zeros], axis=-1)
    return r

# --------------------------------------------------------------------------------------
# Punkt 2A
# --------------------------------------------------------------------------------------

def r_point2A(t):
    """
    - Funktion der Raumkurve entlang der 111-Richtung für Punkt 2A
    """
    t = np.atleast_1d(t).astype(float)
    r = np.stack([t, t, t], axis=-1)
    return r

# --------------------------------------------------------------------------------------
# Punkt 2B
# --------------------------------------------------------------------------------------

def r_point2B(t, a, phi):
    """
    - Funktion der Raumkurve entlang des Punktes 2B(t,phi)
    - phi der bekannte Winkel der Raumkurve 2B
    """
    t = np.atleast_1d(t).astype(float)
    phi = np.atleast_1d(phi).astype(float)
    a0, a1, a2, a3, a4 = a[0], a[1], a[2], a[3], a[4]

    r = r_point2A(t).T # shape (3, n)
    d = a0 + (a1-1)*t + a2*t**2 + a3*t**3 + a4*t**4
    rho = np.sqrt(6)*d

    # Koordinatentransformation {t,rho,phi}->{x,y,z}
    B = np.array([1.0, 1.0, -2.0])
    B = B / np.linalg.norm(B) # Normierung
    B = np.tile(B, (len(t), 1)).T   # shape (3, n)
    # Tangentenvekor liegt in 111-Richtung; Normalenvektor N=BxT:
    N = np.array([1.0, -1.0, 0.0])
    N = N / np.linalg.norm(N)
    N = np.tile(N, (len(t), 1)).T   # shape (3, n)

    rx = r[0] + rho*np.sin(phi)*N[0] + rho*np.cos(phi)*B[0]
    ry = r[1] + rho*np.sin(phi)*N[1] + rho*np.cos(phi)*B[1]
    rz = r[2] + rho*np.sin(phi)*N[2] + rho*np.cos(phi)*B[2]
    r = np.stack([rx, ry, rz], axis=-1)
    phi_vec = np.full(len(t), phi)
    return r, rho, phi_vec

# --------------------------------------------------------------------------------------
# Punkt 3
# --------------------------------------------------------------------------------------

def r_point3(t):
    """
    - Funktion der Raumkurve entlang der 001-Richtung für Punkt 3
    """
    t = np.atleast_1d(t).astype(float)
    zeros = np.zeros_like(t).astype(float)
    r = np.stack([zeros, zeros, t], axis=-1)
    return r

# --------------------------------------------------------------------------------------

def v_vector(x, y, z, r):
    """
    - Versatzvektor (x,y,z)-r(t)
    """
    x = np.atleast_1d(x)
    y = np.atleast_1d(y)
    z = np.atleast_1d(z)
    points = np.stack([x, y, z], axis=-1) # Punkte als array shape(n,3)
    V = points - r
    return V

def frenet(dr, ddr, dddr):
    """
    - berechnet Frenetsches Dreibein und dazugehörige skalare Kurvenparameter
    Schutz vor Division durch 0 bei Normierung:
    - erstelle für B und N jeweils Nullarrays und fülle nur an Stellen auf, wo |(cross(dr, ddr)| > 1e-12

    Args:
        dr:     erste Ableitungen des Pfad-Vektors (vektorisiert)   #shape(n,3)
        ddr:    zweite Ableitungen des Pfad-Vektors                 #shape(n,3)
        dddr:   dritte Ableitung des Pfad-Vektors                   #shape(n,3)
    Return:
        T:      Tangentenvektor     #shape(n,3)
        N:      Normalenvektor      #shape(n,3)
        B:      Binormalenvektor    #shape(n,3)
        v:      Geschwindigkeit     #shape(n,)
        kappa:  Krümmung            #shape(n,)
        tau:    Torsion             #shape(n,)
    """
    # Geschwindigkeit
    v = np.linalg.norm(dr, axis=1)

    # Tangentenvektor
    T = dr / v[:, None]             #shape(n,3)/shape(n,1)=shape(n,3)
    
    # Kreuzprodukt dr,ddr
    cross_dr_ddr = np.cross(dr, ddr)
    norm_cross = np.linalg.norm(cross_dr_ddr, axis=1)
    mask = norm_cross > 1e-12  #Schutz vor Division durch 0
    if not all(mask):
        print("WARNUNG: Division durch 0 bei Pfadvektoren (norm_cross > 1e-12)!")

    # Binormalenvektor
    B = np.zeros_like(dr, dtype=float)
    B[mask] = cross_dr_ddr[mask] / norm_cross[mask, None]

    # Normalenvektor (B x T)
    N = np.zeros_like(dr, dtype=float)
    N[mask] = np.cross(B[mask], T[mask])

    # nach: N[mask] = np.cross(B[mask], T[mask])
    N_tmp = np.cross(B[mask], T[mask])
    N_norm = np.linalg.norm(N_tmp, axis=1)
    ok = N_norm > 1e-12
    N_tmp[ok] /= N_norm[ok, None]
    N[mask] = N_tmp

    # Krümmung
    kappa = np.zeros_like(v, dtype=float)
    kappa[mask] = norm_cross[mask] / (v[mask]**3)

    # Torsion
    tau = np.zeros_like(v, dtype=float)
    numerator = np.einsum('ij,ij->i', cross_dr_ddr, dddr)  # Skalarprodukt
    tau[mask] = numerator[mask] / (norm_cross[mask]**2)
    
    # Orthonormalität überprüfen
    norm_T = np.linalg.norm(T, axis=1)  # Norm
    norm_B = np.linalg.norm(B, axis=1)
    norm_N = np.linalg.norm(N, axis=1)
    dot_TN = np.einsum('ij,ij->i', T, N) # Skalarprodukt
    dot_TB = np.einsum('ij,ij->i', T, B)
    dot_NB = np.einsum('ij,ij->i', N, B)
    max_dev_norms = np.max(np.abs(np.array([norm_T - 1, norm_N - 1, norm_B - 1])))
    max_dev_orth  = np.max(np.abs(np.array([dot_TN, dot_TB, dot_NB])))
    print(f"----> Maximale Abweichung von |T|=|N|=|B|=1 : {max_dev_norms:.2e}")
    print(f"----> Maximale Abweichung von Orthogonalität: {max_dev_orth:.2e}")
    
    return T, N, B, v, kappa, tau
    
def find_t_for_xyz(x, y, z, r_func, bounds=(-2,2), xatol=1e-8, **kwargs):
    """
    - findet das t, für das der Punkt r(t) am nächsten zum Punkt (x,y,z) liegt
    Args:
        x,y,z:              Werte des kartesischen Koordinatensystems
        r_func:             Funktion, welche die Raumkurve r(t) definiert
        bounds:             Intervall für t, in dem minimize_scalar nach dem Minmum sucht
        xatol:              Toleranz in der minimize_scalar Funktion
        **kwargs:           Koeffizienten der Raumkurve (z.B. a_coeffs, b_coeffs)
    Return:
        t:                  Koordinate t
    """
    def distance(t, point):
        r = r_func(t, **kwargs)[0] #shape(1,3)
        Vx = point[0] - r[0]
        Vy = point[1] - r[1]
        Vz = point[2] - r[2]
        V_vec = np.array([Vx, Vy, Vz])
        return np.sum(V_vec**2) # float
    
    x = np.atleast_1d(x)
    y = np.atleast_1d(y)
    z = np.atleast_1d(z)
    points = np.stack([x, y, z], axis=-1) # Punkte als array shape(n,3)
    t_vals = np.empty_like(x, dtype=float)

    for i, point in enumerate(points):
        res = minimize_scalar(distance, bounds=bounds, method="bounded", args=(point,), options={"xatol": xatol})
        t_vals[i] = res.x
    t = t_vals if x.ndim > 0 else t_vals.item()
    print(f"----> Anzahl der (x,t) = ({len(x)}, {len(t)})")
    return t

# -------------------------------------------------------------------------------------------------

def new_coordinates(t, T, N, B, V, kappa, tol=1e-7):
    """
    - transformiert (x,y,z) in lokale Polarkoordinaten (t, rho, phi) entlang der Raumkurve r(t)
    - nutzt minimize_scalar von scipy.optimize

    Args:
        t:      Koordinate t aus find_t_for_xyz()
        T:      Tangentenvektor aus frenet()
        N:      Normalenvektor aus frenet()
        B:      Binormalenvektor aus frenet()
        V:      Versatzvektor aus v_vector()
        kappa:  Krümmung  aus frenet()
        tol:    Toleranz zur Prüfung, ob V othogonal zu T ist
    Return:
        t, rho, phi:        Neue Koordinaten
    """
    # Polarkoordinaten
    """
    Skalarprodukte: np.einsum("ik,kj->ij", A, B) heißt: Cij = sum_k Aik Bkj
    """
    Vt = np.einsum("ij,ij->i", V, T)
    Vn = np.einsum("ij,ij->i", V, N)
    Vb = np.einsum("ij,ij->i", V, B)
    rho = np.sqrt(Vn**2 + Vb**2)
    phi = np.arctan2(Vn, Vb) # arctan2(y,x)

    # Prüfe ob notwendige Bedingung erfüllt ist
    kappa_max = np.max(kappa)
    if kappa_max == 0:
        print("----> Notwendige Bedingung erfüllt. kappa_max=0")
    else:
        condition = np.all(rho < 1/kappa_max)
        if condition:
            print("----> Notwendige Bedingung erfüllt. rho < 1/kappa_max")
        else:
            print("----> WARNUNG: notwendige Bedingung rho < 1/kappa_max nicht erfüllt!")
            print(f"----> 1/kappa_max={1/kappa_max}, rho_min={np.min(rho)}")

    # Prüfen, ob V wirklich orthogonal zu T ist
    mask = np.abs(Vt) < tol
    if len(t[mask]) == len(t):
        print(f"----> Achsentransformation mit Abweichung der Orthogonalität < {tol} erfolgreich")
        print(f"----> Anzahl der (t,rho,phi): ({len(t)}, {len(rho)}, {len(phi)})")
    else:
        print(f"----> WARNUNG: Abweichung der Orthogonalität < {tol} nicht erfüllt!")
        print(f"----> Maximale Abweichung: {np.max(np.abs(Vt)):.2e}")
    return t, rho, phi
