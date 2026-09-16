import os
import os.path
import numpy as np
import time
import matplotlib.pylab as plt
from BoltzTraP2 import fite, serialization, sphere, units
from BoltzTraP2 import dft as BTP
from BoltzTraP2 import bandlib as BL
# --------------------------------------------------------------------------------------
import lib.config as config

# --------------------------------------------------------------------------------------
# Interpolation durch BoltzTrap2
# --------------------------------------------------------------------------------------

def bt2calculations(m: int,
                    T_list: list,
                    bins: int,
                    fermipm: float = None,
                    erange: float = None,
                    margin: float = None,
                    curv: bool = True,
                    enable_logging: bool = True):
    """
    - berechnet Interpolation und Integration mit BoltzTraP2
    - speichert Daten in einer JSON-Datei im Arbeitsverzeichnis

    Args:
        m:                  Interpolationsdichte des k-Punkte-Rasters
        T_list:             Liste von Temperaturwerten
        bins:               Anzahl der zur Bestimmung der Zustandsdichte(DOS) verwendeten Bins
        fermipm:            wählt Bänder für die Interpolation in der Nähe des Fermi-Niveaus aus
                            None: fermipm = 15 * units.BOLTZMANN * T_list.max()
        erange:             Energiebereich für das DOS. Falls nicht angegeben, wird er automatisch von der DOS-Funktion ermittelt.
                            None: erange = 15 * units.BOLTZMANN * T_list.max()
        margin:             Bereich der chemischen Potentiale für mur
                            None: margin = 10 * units.BOLTZMANN * temp.max()
        curv:               Soll die Bandkrümmung berechnet werden?
        enable_logging:     Sollen das log und die print-Ausgabe für die Rechenzeiten aktiv sein?

    Bemerkungen:
        - Interpolation: fermipm wählt die Bänder im gewählten Intervall +-fermipm um das Fermi-Niveau aus, schneidet sie aber nicht auf einen bestimmten Energiebereich zu!
        - nur das Intervall der Bänder [-erange,+erange] wird für die Berechnung der Zustandsdichte verwendet
        - margin schneidet die Ränder des Energiebereichs für das DOS um den Wert margin ab
    """
    # Standartwerte laden
    temp = np.array(T_list)
    if fermipm == None:
        fermipm = 15 * units.BOLTZMANN * temp.max()
        print(f"fermipm:{fermipm}")
    if erange == None:
        erange = 15 * units.BOLTZMANN * temp.max()
        print(f"erange:{erange}")
    if margin == None:
        margin = 10 * units.BOLTZMANN * temp.max()
        print(f"margin:{margin}")
    
    # Pfade definieren
    dftdata = config.path_bt2_dft_directory()
    bt2file = config.path_bt2_bt2file(m, fermipm)
    resultdata = config.path_bt2_resultdata(m, fermipm, erange, margin, temp, bins)
    logdata_filename_int = config.path_log_interpolation(m, fermipm, erange, margin, temp, bins)
    logdata_filename_calc = config.path_log_calculation(m, fermipm, erange, margin, temp, bins)
    
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

    # -----------------------------------------------------------------------------------
    # Interpolation, wenn bt2file nicht existiert 
    # -----------------------------------------------------------------------------------

    if not os.path.exists(bt2file):
        print("Interpolation: bt2file does not exist, new interpolation")

        # Starte Zeitmessung und Log
        if enable_logging:
            start_time_0 = time.time()
            start_time = time.time()
            log_file = open(logdata_filename_int, "w")
            print(f"--- m={m}, bins={bins}, Tlen={len(temp)}", file=log_file)

        # Laden der Roh-DFT-Daten
        data = BTP.DFTData(os.path.join(dftdata))
        log("DFTData DONE", log_file)

        # Auswahl der interessanten Bänder
        data.bandana(emin=data.fermi - fermipm, emax=data.fermi + fermipm)
        log("bandana DONE", log_file)

        # Einrichtung des k-Punkt-Gitters mit etwa der m-fachen Dichte der Eingabe
        equivalences = sphere.get_equivalences(data.atoms, data.magmom, len(data.kpoints)*m)
        log("get_equivalences DONE", log_file)

        # Interpolation der Bandstruktur
        coeffs = fite.fitde3D(data, equivalences)
        log("fitde3D DONE", log_file)

        # Speichern der Ergebnisse
        serialization.save_calculation(bt2file, data, equivalences, coeffs, serialization.gen_bt2_metadata(data, data.mommat is not None))
        log("save_calculation DONE", log_file)

        if enable_logging and log_file:
            print("--- %.2f s --- Interpolation DONE" % (time.time() - start_time_0))
            print("--- %.2f s --- Interpolation DONE" % (time.time() - start_time_0), file=log_file)
            log_file.close()

    # Laden der Interpolationsergebnisse aus der Datei
    data, equivalences, coeffs, metadata = serialization.load_calculation(bt2file)

    #print(f"--- data.fermi: {data.fermi}")
    #print(f"--- data.atoms: {data.atoms}")
    #print(f"--- data.magmom: {data.magmom}")
    print(f"--- data.kpoints: {len(data.kpoints)}")
    print(f"--- new number of kpoints: {len(data.kpoints)*m}")
    #print(f"--- data.mommat: {data.mommat}")
    #print(f"--- ata.get_lattvec() : {data.get_lattvec()}")
    #print(f"--- data.get_volume(): {data.get_volume()}")

    # -----------------------------------------------------------------------------------
    # Berechnung, wenn resultdata nicht existiert 
    # -----------------------------------------------------------------------------------

    if not os.path.exists(resultdata):
        print("Integration: resultdata does not exist, new calculation")

        # Starte Zeitmessung und Log
        if enable_logging:
            start_time_0 = time.time()
            start_time = time.time()
            log_file = open(logdata_filename_calc, "w")
            print(f"--- m={m}, bins={bins}, Tlen={len(temp)}", file=log_file)

        # Erstellung der vollständigen neuen Energiebänder aus den Interpolationskoeffizienten
        """
        getBTPbands() erstellt die vollständigen Energiebänder aus den Interpolationskoeffizienten
        Args:
            equivalences:   Liste der k-Punkt-Äquivalenzklassen
            coeffs:         Interpolationskoeffizienten
            lattvec:        Gittervektoren des Systems
            curvature:      Soll die Bandkrümmung berechnet werden?
            nWorker:        Anzahl der zu Arbeitsprozesse = 1
        Returns:
            eband:          Liste mit den Bandenergien
            vvband:         Liste mit dem äußeren Produkt jeder Gruppengeschwindigkeit
            cband:          Liste mit den Krümmungen
        """
        lattvec = data.get_lattvec()
        eband, vvband, cband = fite.getBTPbands(equivalences, coeffs, lattvec, curvature=curv)
        log("getBTPbands DONE", log_file)

        # Neuberechnung der Fermi-Energie und der intrinsischen chemischen Potentiale
        """
        BL.solve_for_mu()
        - BTPDOS() ändert die Anzahl der Valenzelektronen, wenn die Bänder angeschnitten werden
            -> deshalb muss hier mit epsilon mit den vollständigen Bändern berechnet werden
        Args:
            epsilon:        Energiebereich, bei dem die DOS verfügbar ist
            data.nelect:    Anzahl der Valenzelektronen
            temp[i]:        einzelner Wert der Temperatur
            refine:         wenn True, beschränke mu nicht auf die Werte in epsilon
            try_center:     Wenn True, wird der Wert von mu in die Mitte großer Lücken ausgerichtet
        """
        epsilon, dos, vvdos, cdos = BL.BTPDOS(eband, vvband, cband, npts=bins, scattering_model="uniform_tau")
        mu0 = []
        for i in range(len(temp)):
            mu0.append(BL.solve_for_mu(epsilon, dos, data.nelect, temp[i], data.dosweight, refine=False, try_center=False))
        mu0 = np.array(mu0)
        fermi = BL.solve_for_mu(epsilon, dos, data.nelect, 0.0, data.dosweight, refine=False, try_center=False)
        print(f"--- old fermi-level: {data.fermi}")
        print(f"--- new fermi-level: {fermi}")
        log("Calculation mu0 DONE", log_file)

        # Berechnung der Zustandsdichte (DOS), Transport-DOS und Krümmungs-DOS
        """
        Args:
            eband:              Liste mit den Bandenergien
            vvband:             Liste mit dem äußeren Produkt jeder Gruppengeschwindigkeit
            cband:              Liste mit den Krümmungen
            eragne:             Bereich der Energie
            npts:               Anzahl der bins
            scattering model:   Modell für Elektronenlebensdauern, oder Liste mit Streurate
            Tmin:               Mindesttemperatur
        Returns:
            epsilon:    Energiebereich, bei dem die DOS verfügbar ist
            vvdos:      Transport-DOS
            cdos:       Krümmung-DOS
        """
        temp = np.array(T_list)
        emin = fermi - erange
        emax = fermi + erange
        
        epsilon, dos, vvdos, cdos = BL.BTPDOS(eband, vvband, cband, erange=(emin, emax), npts=bins, scattering_model="uniform_tau")
        log("BTPDOS DONE", log_file)

        # Smoothen DOS ist möglich !

        # Definition der Werte für das chemische Potential
        murmin = epsilon.min() + margin
        murmax = epsilon.max() - margin
        mur_indices = np.logical_and(epsilon > murmin, epsilon < murmax)
        mur = epsilon[mur_indices]
        log("mur DONE", log_file)

        # Berechnung der Momente der FD Verteilung über die Bandstruktur
        """
        BL.fermiintegrals()
        Args:
            epsilon:    Energiebereich, bei dem die DOS verfügbar ist
            vvdos:      Transport-DOS
            mur:        Liste der chemischen Potenziale
            temp:       Liste der Temperaturwerte
            dosweight:  maximale Besetzung eines Elektronenmodus
            cdos:       Krümmung-DOS, falls verfügbar
        Returns:        (T=temperature, µ=chemical potential)
            N:          Liste mit den Elektronenzahlen für jedes T und µ   
            L0:         N mit Integralen des Transport-DOS
            L1:         N mit den ersten Momenten des Transport-DOS
            L2:         N mit den zweiten Momenten des Transport-DOS
            Lm11:       N mit den Integrale der Krümmung-DOS
        """
        N, L0, L1, L2, L11 = BL.fermiintegrals(epsilon, dos, vvdos, mur, temp, dosweight=data.dosweight, cdos=cdos)
        log("fermiintegrals DONE", log_file)

        # Berechnung der Transportgrößen basierend auf Fermi-Dirac-Integrale
        UCvol = data.get_volume() # Volumen der Elementarzelle
        """
        BL.calc_Onsager_coefficients()
        Args:
            N:          Liste mit den Elektronenzahlen für jedes T und µ   
            L0:         N mit Integralen des Transport-DOS
            L1:         N mit den ersten Momenten des Transport-DOS
            L2:         N mit den zweiten Momenten des Transport-DOS
            Lm11:       N mit den Integrale der Krümmung-DOS
            mur:        Liste der chemischen Potenziale
            temp:       Liste der Temperaturwerte
            UCvol:      Volumen der Elementarzelle
        Returns: 
            sigma:      Leitfähigkeitstensor für jede Kombination von T und µ
            seebeck:    Seebeck-Koeffiziententensor für jede Kombination von T und µ
            kappa:      Ladungsträgerbeitrag zur Wärmeleitfähigkeit für jede Kombination von T und µ
            hall:       wenn Lm11 vorhanden ist, Hall-Tensor für jede Kombination von T und µ
        """
        sigma, seebeck, kappa, hall = BL.calc_Onsager_coefficients(L0, L1, L2, mur, temp, UCvol, Lm11=L11)
        log("calc_Onsager_coefficients DONE", log_file)
        
        # Berechnen Sie den elektronischen Beitrag zur Wärmekapazität
        """
        Args:
            epsilon:    Energiebereich, bei dem die DOS verfügbar ist
            mur:        Liste der chemischen Potenziale
            temp:       Liste der Temperaturwerte
            dosweight:  maximale Besetzung eines Elektronenmodus
        Returns:
            cv:         elektronischer Beitrag zur Wärmekapazität für jede Temperatur und jedes chemische Potenzial, in SI-Einheiten
        """
        cv = BL.calc_cv(epsilon, dos, mur, temp, data.dosweight)
        log("calc_cv DONE", log_file)

        # Speichern der Resultate
        """
        Args:
            filename:   Pfad zur Datei
            data:       DFT-Daten
            fermi:      Fermi-Level
            Tr:         Liste der Temperaturwerte
            mu0:        Liste der intrinsischen chemischen Potentiale bei jeder Temperatur
            mur:        Liste der chemischen Potentiale
            N:          Ergebnis der Anzahl der Elektronen
            sdos:       Ergebnis des smoothed DOS
            cv:         Ergebnis der Wärmekapazität
            sigma:      Ergebnis der elektrische Leitfähigkeit
            seebeck:    Ergebnis des Seebeck-Koeffizieten
            kappa:      Ergebnis des Trägerbeitrags zur Wärmeleitfähigkeit
            hall:       Ergebnis des Hall-Koeffizienten
            metadata:   Metadaten
        """
        serialization.save_results(resultdata, data, fermi, temp, mu0, mur, N, None, cv, sigma, seebeck, kappa, hall, metadata)
        log("save_results DONE", log_file)

        if enable_logging and log_file:
            print("--- %.2f s --- Calculation DONE" % (time.time() - start_time_0))
            print("--- %.2f s --- Calculation DONE" % (time.time() - start_time_0), file=log_file)       
            log_file.close()

# --------------------------------------------------------------------------------------
# Plots
# --------------------------------------------------------------------------------------

# Plottet Größe [Y_name] in Abhängigkeit der Größe [X_name]

def plot_Y_X(Y_name: str,
             X_name: str,
             m_values: list,
             bins: int,
             T_list: list,
             T_plot: list = None,
             mu_plot: list = None,
             fermipm: float = None,
             erange: float = None,
             margin: float = None,
             xlim_values: tuple = None,
             ylim_values: tuple = None,
             trace: bool = True):
    """
    Plottet Größe [Y_name] in Abhängigkeit der Größe [X_name]
    Args:
        Y_name:     "cv", "seebeck", "kappa", "sigma", "hall"
        X_name:     "mu", "T"
        m_values:   Liste der zu plottenden m-Werte; 
                    m:Interpolationsdichte des k-Punkte-Rasters
        bins:       Anzahl der zur Bestimmung des DOS verwendeten Bins
        T_list:     Liste von Temperaturwerten - verwendet, um den Dateienpfad zu finden
        T_plot:     optional
                    wenn X_name=mu: Liste der zu plottenden T-Kurven
                    if None: Raumtemperatur
        mu_plot:    optional
                    wenn X_name=T: Liste der zu plottenden mu-Kurven
                    if None: Fermi-Energie
        fermipm:    verwendet, um den Dateienpfad zu finden
        erange:     verwendet, um den Dateienpfad zu finden
        margin:     verwendet, um den Dateienpfad zu finden 
        xlim_values:(float,float) Einschränkung der Plots auf einen Bereich der X-Achse
        ylim_values:(float,float) Einschränkung der Plots auf einen Bereich der y-Achse
        trace:      Soll die Spur des Tensors bepolottet werden?

    Einheiten:
        Y_name      physikalische Größe                     Einheit             Richtung, wenn trace=True,                  else
        --------------------------------------------------------------------------------------------------------------------------
        cv          Wärmekapazität:                         [J/(mol*K)]         -
        seebeck     Seebeck-Koeffizient:                    [V/K]               (xx + yy + zz)/3                            xx
        kappa       Wärmeleitfähigkeit/Streurate:           [W/(m*K*s)]         (xx + yy + zz)/3                            xx
        sigma       Elektrische Leitfähigkeit/Streurate:    [1/(ohm*m*s)]       (xx + yy + zz)/3                            xx
        hall        Hall-Koeffizient:                       [m³/C]              (xyz + yzx + zxy - xzy - zyx - yxz)/6       xyz

        X_name      physikalische Größe                     Einheit             Richtung bei Tensor
        --------------------------------------------------------------------------------------------------------------------------
        mu          chemisches Potential                    [Ha]                -
        T           Temperatur                              [K]                 -
    """
  
    # Wähle die passenden Datenarrays aus
    # Fallunterscheidung für verschiedene Achse, Titel, Ordner usw.
    fermi = [0]
    cv = [0,0]
    seebeck = sigma = kappa = [0,0,0,0]
    hall = [0,0,0,0,0]
    if X_name == "mu":
        def xdata():
            return (mur - fermi)
        xlabel = r"$\mu$-$E_f$ [Ha]"
        X_title_name = "des chemischen Potentials für verschiedene Temperaturen"

        if Y_name == "cv":
            def ydata(t):
                return cv[t, :]
            ylabel = r"$C_v$ [J/K]"
            Y_title_name = "Elektronischer Beitrag zur Wärmekapazität"

        elif Y_name == "seebeck":
            if trace:
                def ydata(t):
                    return np.trace(seebeck[t, :, ...], axis1=1, axis2=2)/3.0
                ylabel = r"$S$ [V/K]"
            else:
                def ydata(t):
                    return seebeck[t, :, 0, 0] # xx-Richtung
                ylabel = r"$S^{xx}$ [V/K]"
            Y_title_name = "Seebeck-Koeffizient"

        elif Y_name == "sigma":
            if trace:
                def ydata(t):
                    return np.trace(sigma[t, :, ...], axis1=1, axis2=2)/3.0
                ylabel = r"$\sigma$/$\tau_0$ [1/($\Omega$ m s)]"
            else:
                def ydata(t):
                    return sigma[t, :, 0, 0] # xx-Richtung
                ylabel = r"$\sigma^{xx}$/ $\tau_0$ [1/($\Omega$ m s)]"
            Y_title_name = "Elektrische Leitfähigkeit pro Streurate"

        elif Y_name == "kappa":
            if trace:
                def ydata(t):
                    return np.trace(kappa[t, :, ...], axis1=1, axis2=2)/3.0
                ylabel = r"$\kappa$/$\tau_0$ [W/(m K s)]"
            else:
                def ydata(t):
                    return kappa[t, :, 0, 0] # xx-Richtung
                ylabel = r"$\kappa^{xx}$/ $\tau_0$ [W/(m K s)]"
            Y_title_name = "Wärmeleitfähigkeit pro Streurate"

        elif Y_name == "hall":
            if trace:
                def ydata(t):
                    trace = (hall[t, :, 0, 1, 2]+hall[t, :, 1, 2, 0]+hall[t, :, 2, 0, 1]-hall[t, :, 0, 2, 1]-hall[t, :, 2, 1, 0]-hall[t, :, 1, 0, 2])/6.0
                    return trace
                ylabel = r"$R_H$ [$m^3$/C]"
            else:
                def ydata(t):
                    return hall[t, :, 0, 1, 2] # xyz-Richtung
                ylabel = r"$R_H^{xyz}$ [$m^3$/C]"
            Y_title_name = "Hall-Koeffizient"

        else:
            raise ValueError(f"Unbekannter Y-Parametername: {Y_name}")
    
    elif X_name == "T":
        def xdata():
            return temp
        xlabel = r"$T$ [K]"
        X_title_name = "der Temperatur für verschiedene chemischen Potentiale"

        if Y_name == "cv":
            def ydata(j):
                return cv[:, j]
            ylabel = r"$C_v$ [J/K]"
            Y_title_name = "Elektronischer Beitrag zur Wärmekapazität"

        elif Y_name == "seebeck":
            if trace:
                def ydata(j):
                    return np.trace(seebeck[:, j, ...], axis1=1, axis2=2)/3.0
                ylabel = r"$S$ [V/K]"
            else:
                def ydata(j):
                    return seebeck[:, j, 0, 0] # xx-Richtung
                ylabel = r"$S^{xx}$ [V/K]"
            Y_title_name = "Seebeck-Koeffizient"

        elif Y_name == "sigma":
            if trace:
                def ydata(j):
                    return np.trace(sigma[:, j, ...], axis1=1, axis2=2)/3.0
                ylabel = r"$\sigma$/$\tau_0$ [1/($\Omega$ m s)]"
            else:
                def ydata(j):
                    return sigma[:, j, 0, 0] # xx-Richtung
                ylabel = r"$\sigma^{xx}$/ $\tau_0$ [1/($\Omega$ m s)]"
            Y_title_name = "Elektrische Leitfähigkeit pro Streurate"

        elif Y_name == "kappa":
            if trace:
                def ydata(j):
                    return np.trace(kappa[:, j, ...], axis1=1, axis2=2)/3.0
                ylabel = r"$\kappa$/$\tau_0$ [W/(m K s)]"
            else:
                def ydata(j):
                    return kappa[:, j, 0, 0] # xx-Richtung
                ylabel = r"$\kappa^{xx}$/ $\tau_0$ [W/(m K s)]"
            Y_title_name = "Wärmeleitfähigkeit pro Streurate"

        elif Y_name == "hall":
            if trace:
                def ydata(j):
                    trace = (hall[:, j, 0, 1, 2]+hall[:, j, 1, 2, 0]+hall[:, j, 2, 0, 1]-hall[:, j, 0, 2, 1]-hall[:, j, 2, 1, 0]-hall[:, j, 1, 0, 2])/6
                    return trace
                ylabel = r"$R_H$ [$m^3$/C]"
            else:
                def ydata(j):
                    return hall[:, j, 0, 1, 2] # xyz-Richtung
                ylabel = r"$R_H^{xyz}$ [$m^3$/C]"
            Y_title_name = "Hall-Koeffizient"

        else:
            raise ValueError(f"Unbekannter Y-Parametername: {Y_name}")
    
    else:
        raise ValueError(f"Unbekannter X-Parametername: {X_name}")

    plt.figure(figsize=(14,5))

    for m in m_values:

        # Lade resultsfile
        temp = np.array(T_list)
        if fermipm == None:
            fermipm = 15 * units.BOLTZMANN * temp.max()
        if erange == None:
            erange = 15 * units.BOLTZMANN * temp.max()
        if margin == None:
            margin = 10 * units.BOLTZMANN * temp.max()

        # Dateien und Ordner-Namen
        resultfile = config.path_bt2_resultdata(m, fermipm, erange, margin, temp, bins)

        # Lade bt2-Daten
        data, fermi, temp, mu0, mur, N, smoothedDOS, cv, sigma, seebeck, kappa, hall, metadata = serialization.load_results(resultfile)
                
        # Erstelle Plots
        if X_name == "mu":

            # erstelle T_index - Liste der zu plottenden Temperaturen
            roomT_index = np.abs(temp - 300).argmin() # approximiere Index der Raumtemperatur

            if T_plot == None:
                T_index = [roomT_index]
            else:
                T_index = [roomT_index]
                for t in T_plot:
                    T_i = np.abs(temp - t).argmin()
                    T_index.append(T_i)

            # plot
            for t in T_index:
                y_data = ydata(t)
                x_data = xdata()
                if t == roomT_index:
                    #plt.plot(x_data, y_data, ".", color="grey", alpha=0.5)
                    plt.plot(x_data, y_data, "-", label=f"m={m}, T={temp[t]}K, bins={bins}")
                else:
                    #plt.plot(x_data, y_data, ".", color="grey", alpha=0.5)
                    plt.plot(x_data, y_data, "--", label=f"m={m}, T={temp[t]}K, bins={bins}")
        
        elif X_name == "T":

            # erstelle mu_index - Liste der zu plottenden chemischen Potenitale
            fermi_index = np.abs(mur - fermi).argmin() # approximiere Index der Fermi-Energie

            if mu_plot == None:
                mu_index = [fermi_index]
            else:
                mu_index = [fermi_index]
                for mu in mu_plot:
                    mu_i = np.abs( (mur - fermi) - mu ).argmin()
                    mu_index.append(mu_i)
        
            # plot
            for j in mu_index:
                y_data = ydata(j)
                x_data = xdata()
                if j == fermi_index:
                    plt.plot(x_data, y_data, ".", color="grey", alpha=0.5)
                    plt.plot(x_data, y_data, "-", label=f"m={m}, (µ-$E_f$)={f"{(mur[j]-fermi):.4f}"}, bins={bins}")
                else:
                    plt.plot(x_data, y_data, ".", color="grey", alpha=0.5)
                    plt.plot(x_data, y_data, "--", label=f"m={m}, (µ-$E_f$)={f"{(mur[j]-fermi):.4f}"}, bins={bins}")
        
        else:
            raise ValueError(f"Unbekannter X-Parametername: {X_name}")

    plt.xlabel(xlabel, fontsize="14")
    plt.ylabel(ylabel, fontsize="14")
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.title(f"{Y_title_name} in Abhängigkeit\n{X_title_name}", fontsize="14")
    if xlim_values is not None:
        plt.xlim(xlim_values)
    if ylim_values is not None:
        plt.ylim(ylim_values)
    plt.grid()
    plt.tight_layout()
    plt.show()

# Plottet Größe [Y_name] in Abhängigkeit der Größe [input_name]

def plot_Y_input(Y_name: str,
                 input_name: str,
                 m_values: list,
                 bins: int,
                 T_list: list,
                 T: int = None,
                 mu: int = None,
                 fermipm: float = None,
                 erange: float = None,
                 margin: float = None,
                 xlim_values: tuple = None,
                 ylim_values: tuple = None,
                 trace: bool = True):
    """
    Plottet Größe [Y_name] in Abhängigkeit der Größe [input_name]
    Args:
        Y_name:     "cv", "seebeck", "kappa", "sigma", "hall"
        input_name: "m"
        m_values:   Liste der zu plottenden m-Werte; 
                    m:Interpolationsdichte des k-Punkte-Rasters
        bins:       Anzahl der zur Bestimmung des DOS verwendeten Bins
        T_list:     verwendet, um den Dateienpfad zu finden
        T:          optional, Temperaturwert von Y_name
                    if None: Raumtemperatur
        mu:         optional, Wert des chemischen Potentials von Y_name
                    if None: Fermi-Energie
        fermipm:    verwendet, um den Dateienpfad zu finden
        erange:     verwendet, um den Dateienpfad zu finden
        margin:     verwendet, um den Dateienpfad zu finden 
        xlim_values (float,float) Einschränkung des Plots auf einen Bereich der X-Achse
        ylim_values (float,float) Einschränkung des Plots auf einen Bereich der y-Achse
        trace:      Soll die Spur des Tensors bepolottet werden?

    Einheiten:
        Y_name      physikalische Größe                     Einheit             Richtung, wenn trace=True,                  else
        --------------------------------------------------------------------------------------------------------------------------
        cv          Wärmekapazität:                         [J/(mol*K)]         -
        seebeck     Seebeck-Koeffizient:                    [V/K]               (xx + yy + zz)/3                            xx
        kappa       Wärmeleitfähigkeit/Streurate:           [W/(m*K*s)]         (xx + yy + zz)/3                            xx
        sigma       Elektrische Leitfähigkeit/Streurate:    [1/(ohm*m*s)]       (xx + yy + zz)/3                            xx
        hall        Hall-Koeffizient:                       [m³/C]              (xyz + yzx + zxy - xzy - zyx - yxz)/6       xyz

        input_name  Größe                                       Einheit         Richtung bei Tensor
        ------------------------------------------------------------------------------------------
        m           Interpolationsdichte des k-Punkte-Rasters   -                -
    """

    # Wähle die passenden Datenarrays aus
    cv = [0,0]
    seebeck = sigma = kappa = [0,0,0,0]
    hall = [0,0,0,0,0]
    if Y_name == "cv":
        def ydata(t, j):
            return cv[t, j]
        ylabel = r"$C_v$ [J/K]"
        Y_title_name = "Elektronischer Beitrag zur Wärmekapazität"

    elif Y_name == "seebeck":
        if trace:
            def ydata(t, j):
                return (seebeck[t, j, 0, 0] + seebeck[t, j, 1, 1] + seebeck[t, j, 2, 2])/3.0
            ylabel = r"$S$ [V/K]"
        else:
            def ydata(t, j):
                return seebeck[t, j, 0, 0] # xx-Richtung
            ylabel = r"$S^{xx}$ [V/K]"
        Y_title_name = "Seebeck-Koeffizient"

    elif Y_name == "sigma":
        if trace:
            def ydata(t, j):
                return (sigma[t, j, 0, 0] + sigma[t, j, 1, 1] + sigma[t, j, 2, 2])/3.0
            ylabel = r"$\sigma$/$\tau_0$ [1/($\Omega$ m s)]"
        else:
            def ydata(t, j):
                return sigma[t, j, 0, 0] # xx-Richtung
            ylabel = r"$\sigma^{xx}$/ $\tau_0$ [1/($\Omega$ m s)]"
        Y_title_name = "Elektrische Leitfähigkeit pro Streurate"

    elif Y_name == "kappa":
        if trace:
            def ydata(t, j):
                return (kappa[t, j, 0, 0] + kappa[t, j, 1, 1] + kappa[t, j, 2, 2])/3.0
            ylabel = r"$\kappa$/$\tau_0$ [W/(m K s)]"
        else:
            def ydata(t, j):
                return kappa[t, j, 0, 0] # xx-Richtung
            ylabel = r"$\kappa^{xx}$/ $\tau_0$ [W/(m K s)]"
        Y_title_name = "Wärmeleitfähigkeit pro Streurate"

    elif Y_name == "hall":
        if trace:
            def ydata(t, j):
                return (hall[t, j, 0, 1, 2]+hall[t, j, 1, 2, 0]+hall[t, j, 2, 0, 1]-hall[t, j, 0, 2, 1]-hall[t, j, 2, 1, 0]-hall[t, j, 1, 0, 2])/6
            ylabel = r"$R_H$ [$m^3$/C]"
        else:
            def ydata(t, j):
                return hall[t, j, 0, 1, 2] # xyz-Richtung
            ylabel = r"$R_H^{xyz}$ [$m^3$/C]"
        Y_title_name = "Hall-Koeffizient"

    else:
        raise ValueError(f"Unbekannter Parametername: {Y_name}")   

    # Erstelle Plots
    plt.figure(figsize=(10,3))

    if input_name == "m":
        xlabel = "Parameter m"
        X_title_name = "des Parameters m"
        temp = np.array(T_list)
        
        if fermipm == None:
            fermipm = 15 * units.BOLTZMANN * temp.max()
        if erange == None:
            erange = 15 * units.BOLTZMANN * temp.max()
        if margin == None:
            margin = 10 * units.BOLTZMANN * temp.max()
        
        # Erstelle x und y-Daten
        # t verändert sich nicht
        if T == None:
                t = np.abs(temp - 293.15).argmin() # approximiere Index der Raumtemperatur
        else:
            t = np.abs(temp - T).argmin()

        x_data = []
        y_data = []
        for m in m_values:
            
            # Dateien und Ordner-Namen
            resultfile = config.path_bt2_resultdata(m, fermipm, erange, margin, temp, bins)
            
            # Lade bt2-Daten
            data, fermi, temp, mu0, mur, N, smoothedDOS, cv, sigma, seebeck, kappa, hall, metadata = serialization.load_results(resultfile)          

            # fermi kann je nach m leicht unterschiedlich sein
            if mu == None:
                j = np.abs(mur - fermi).argmin() # approximiere Index der Fermi-Energie
            x_data.append(m)
            y_data.append(ydata(t,j))

        plt.plot(x_data, y_data, "o", color="black", alpha=0.5)
        plt.plot(x_data, y_data, "-", label=f"T={temp[t]}, (µ-$E_f$)={0 if mu is None else mu}")

    plt.xlabel(xlabel, fontsize="14")
    plt.ylabel(ylabel, fontsize="14")
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.title(f"{Y_title_name} in Abhängigkeit\n{X_title_name}", fontsize="14")
    if xlim_values is not None:
        plt.xlim(xlim_values)
    if ylim_values is not None:
        plt.ylim(ylim_values)
    plt.grid()
    plt.tight_layout()
    plt.show()

# Wärmekapazität/Tempertatur vs. Temperatur

def cv_perT_vs_T(m: int,
                 bins: int,
                 T_list: list,
                 fermipm: float=None,
                 erange: float=None,
                 margin: float=None):
    """
    - plottet Wärmekapazität/Tempertatur vs. Temperatur
    Args:
        m:          m-Werts
        bins:       Anzahl der zur Bestimmung des DOS verwendeten Bins
        T_list:     verwendet, um den Dateienpfad zu findenur
        fermipm:    verwendet, um den Dateienpfad zu finden
        erange:     verwendet, um den Dateienpfad zu finden
        margin:     verwendet, um den Dateienpfad zu finden 
    """
    plt.figure(figsize=(14,5))
    cv = [0,0]
    def ydata(j):
        return cv[:, j]
    ylabel = r"$\gamma = C_v/T$ [J/$K^2$]"
    xlabel = r"$T$ [K]"
    temp = np.array(T_list)
    X_title_name = "der Temperatur für verschiedene chemischen Potentiale"
    Y_title_name = "Elektronischer Beitrag zur Wärmekapazität/Temperatur"

    if fermipm == None:
        fermipm = 15 * units.BOLTZMANN * temp.max()
    if erange == None:
        erange = 15 * units.BOLTZMANN * temp.max()
    if margin == None:
        margin = 10 * units.BOLTZMANN * temp.max()
    
    resultfile = config.path_bt2_resultdata(m, fermipm, erange, margin, temp, bins)

    data, fermi, temp, mu0, mur, N, smoothedDOS, cv, sigma, seebeck, kappa, hall, metadata = serialization.load_results(resultfile)

    fermi_index = np.abs(mur - fermi).argmin() # approximiere Index der Fermi-Energie
    mu_index = [fermi_index]
    for j in mu_index:
        y_data = ydata(j)/temp
        x_data = temp
        if j == fermi_index:
            plt.plot(x_data, y_data, ".", color="grey", alpha=0.5)
            plt.plot(x_data, y_data, "-", label=f"m={m}, (µ-$E_f$)={f"{(mur[j]-fermi):.4f}"}, bins={bins}")
        else:
            plt.plot(x_data, y_data, ".", color="grey", alpha=0.5)
            plt.plot(x_data, y_data, "--", label=f"m={m}, (µ-$E_f$)={f"{(mur[j]-fermi):.4f}"}, bins={bins}")
    plt.xlabel(xlabel, fontsize="14")
    plt.ylabel(ylabel, fontsize="14")
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.title(f"{Y_title_name} in Abhängigkeit\n{X_title_name}", fontsize="14")
    plt.grid()
    plt.tight_layout()
    plt.show()
