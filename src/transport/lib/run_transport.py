from multiprocessing import Process
# -----------------------------------------------------------------------------------
import lib.bt2_transport as bt2

"""
- Diese Datei lädt cfg.-Parameter aus z.B. nitiB2_transport_uspp.py zum berechnen der Transportgrößen durch BoltzTrap2.

# ===================================================================================
# Übersicht aller Parameter
# ===================================================================================

# -----------------------------------------------------------------------------------
# Interpolation durch BoltzTrap2
# -----------------------------------------------------------------------------------
cfg.calc        (bool) Aktivierung der Berechnungen durch BoltzTrap2
cfg.m_values    (list) Liste der m-Input-Parameter
                        m = Interpolationsdichte des k-Punkte-Rasters
cfg.T_list      (list) Liste von Temperaturwerten 
cfg.bins_values (list) Liste mit der Anzahl der zur Bestimmung der Zustandsdichte (DOS) verwendeten Bins
                        Bins = Unterteilung der DOS in gleich große Abschnitte - die Bins
cfg.fermipm     (float),(None) wählt Bänder für die Interpolation in der Nähe des Fermi-Niveaus aus
                                - fermipm wählt die Bänder im Intervall $\pm$ (fermipm) um das Fermi-Niveau aus, schneidet sie aber nicht auf einen bestimmten Energiebereich zu
                                None: fermipm = 15 * units.BOLTZMANN * temp.max()
cfg.erange      (float),(None) Energiebereich für die Zustandsdichte DOS
                                - nur das Intervall der Bänder $\pm$ (erange) wird für die Berechnung der Zustandsdichte verwendet
                                None: erange = 15 * units.BOLTZMANN * temp.max()
cfg.margin      (float),(None) margin schneidet die Ränder des Energiebereichs für das DOS um den Wert margin ab
                                - dient als Definitionsbereich für die chemischen Potentiale (mur)
                                - der Wert margin muss also stets kleiner als erange sein, sonst ist mur leer
                                - margin sollte nicht 0 sein, da am Rand Berechnungsfehler auftreten 
                                None: margin = 10 * units.BOLTZMANN * temp.max()

# -----------------------------------------------------------------------------------
# Plots der Transportgrößen mit BoltzTrap2
# -----------------------------------------------------------------------------------
cfg.plot            (bool) Aktiviert Plot der Transportgrößen
cfg.bins            (list) Liste der bins für die Plots
cfg.Y_name          (str) Größe der Y-Achse:
                          "cv", "seebeck", "kappa", "sigma", "hall"
cfg.X_name          (str) Größe der X-Achse:
                          "mu", "T", "m"
cfg.xlim_values     (float,float),(None) Einschränkung der Plots auf einen Bereich der X-Achse
                                            None: keine Einschränkung
cfg.ylim_values     (float,float),(None) Einschränkung der Plots auf einen Bereich der y-Achse
                                            None: keine Einschränkung

Wenn cfg.X_name == "mu" oder "T":
    cfg.plot_m_list     (list) Liste der m-Werte für die Plots
    cfg.plot_T_list     (list),(None) wenn X_name=mu: Liste der zu plottenden T-Kurven
                                        None: Raumtemperatur
    cfg.plot_mu_list    (list),(None) wenn X_name=T: Liste der zu plottenden mu-Kurven
                                        None: Fermi-Energie
    cfg.trace           (bool) Soll die Spur des Tensors gepolottet werden?
                                        False: xx-Richtung bei 2dimensionalen Größen, xyz-Richtung bei Hall-Koeffizient

Wenn cfg.X_name == "m":
    cfg.plot_m_list     (list) X-Achse des Plots
    cfg.plot_T          (float),(None) zu plottende T-Kurve
                                        None: Raumtemperatur
    cfg.plot_mu         (float),(None) zu plottende mu-Kurve
                                        None: Fermi-Energie

cfg.cv_perT_vs_T    (bool) Spezieller Plot: Wärmekapazität/Tempertatur vs. Temperatur                 
    plot_m              (int) m-Werte der Kurve
"""

######################################################################################

def run_single(m, bins, T_list, fermipm, erange, margin):
    bt2.bt2calculations(m, T_list, bins, fermipm=fermipm, erange=erange, margin=margin, curv=True, enable_logging=True)


def run(cfg):
    
    # -----------------------------------------------------------------------------------
    # Interpolation(en) durch BoltzTrap2
    # -----------------------------------------------------------------------------------

    if cfg.calc:
        print()
        print("Interpolation(en) mit BoltzTrap2")
        print(f"T_list:\n{cfg.T_list}")

        # Gesamtzahl der Kombinationen:
        total = len(cfg.m_values) * len(cfg.bins_values)
        count = 1 # Startwert für Fortschrittszähler

        for m in cfg.m_values:
            for bins in cfg.bins_values:
                print(f"[{count}/{total}] m={m}, bins={bins}, Tmax={cfg.T_list.max()}")
                p = Process(target=run_single, args=(m, bins, cfg.T_list, cfg.fermipm, cfg.erange, cfg.margin))
                p.start()
                p.join()   # wartet → weiterhin seriell
                print(f"[{count}/{total}] Berechnung abgeschlossen.")
                count += 1

    # -----------------------------------------------------------------------------------
    # Plot der Transportgrößen
    # -----------------------------------------------------------------------------------
    
    if cfg.plot:

        # Wärmekapazität/Tempertatur vs. Temperatur
        if cfg.cv_perT_vs_T:
            bt2.cv_perT_vs_T(cfg.plot_m, cfg.bins, cfg.T_list, cfg.fermipm, cfg.erange, cfg.margin)

        else:
            # Transportgrößen vs mu oder T
            if cfg.X_name in ["mu", "T"]:
                bt2.plot_Y_X(cfg.Y_name, cfg.X_name, cfg.plot_m_list, cfg.bins, cfg.T_list, cfg.plot_T_list, cfg.plot_mu_list, cfg.fermipm, cfg.erange, cfg.margin, cfg.xlim_values, cfg.ylim_values, cfg.trace)
            
            # Transportgrößen vs m
            elif cfg.X_name in ["m"]:
                bt2.plot_Y_input(cfg.Y_name, cfg.X_name, cfg.plot_m_list, cfg.bins, cfg.T_list, cfg.plot_T, cfg.plot_mu, cfg.fermipm, cfg.erange, cfg.margin, cfg.xlim_values, cfg.ylim_values)


