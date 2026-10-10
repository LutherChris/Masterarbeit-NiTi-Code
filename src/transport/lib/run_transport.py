from multiprocessing import Process
# -----------------------------------------------------------------------------------
import lib.bt2_transport as bt2

# --------------------------------------------------------------------------------------

######################################################################################

def run_single(m, bins, T_list, fermipm, erange, margin):
    bt2.bt2calculations(m, T_list, bins, fermipm=fermipm, erange=erange, margin=margin, curv=True, enable_logging=True)


def run(cfg):

    # ###################################################################################
    # Standard-Parameter, wenn nicht vorhanden
    plot_T_list = cfg.plot_T_list if hasattr(cfg, "plot_T_list") else (print("Achtung: 'plot_T_list' fehlt - setze Standard: None"), None)[1]
    plot_mu_list = cfg.plot_mu_list if hasattr(cfg, "plot_mu_list") else (print("Achtung: 'plot_mu_list' fehlt - setze Standard: None"), None)[1]      
    xlim_values = cfg.xlim_values if hasattr(cfg, "xlim_values") else (print("Achtung: 'xlim_values' fehlt - setze Standard: None"), None)[1]
    ylim_values = cfg.ylim_values if hasattr(cfg, "ylim_values") else (print("Achtung: 'ylim_values' fehlt - setze Standard: None"), None)[1]
    trace = cfg.trace if hasattr(cfg, "trace") else (print("Achtung: 'trace' fehlt - setze Standard: None"), None)[1]
    plot_T = cfg.plot_T if hasattr(cfg, "plot_T") else (print("Achtung: 'plot_T' fehlt - setze Standard: None"), None)[1]
    plot_mu = cfg.plot_mu if hasattr(cfg, "plot_mu") else (print("Achtung: 'plot_mu' fehlt - setze Standard: None"), None)[1]
    plot_m = cfg.plot_m if hasattr(cfg, "plot_m") else (print("Achtung: 'plot_m' fehlt - setze Standard: None"), None)[1]
    cv_perT_vs_T = cfg.cv_perT_vs_T if hasattr(cfg, "cv_perT_vs_T") else (print("Achtung: 'cv_perT_vs_T' fehlt - setze Standard: False"), False)[1]
    
    # ###################################################################################
    
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
        if cv_perT_vs_T:
            bt2.cv_perT_vs_T(plot_m, cfg.bins, cfg.T_list, cfg.fermipm, cfg.erange, cfg.margin)

        else:
            # Transportgrößen vs mu oder T
            if cfg.X_name in ["mu", "T"]:
                bt2.plot_Y_X(cfg.Y_name, cfg.X_name, cfg.plot_m_list, cfg.bins, cfg.T_list, plot_T_list, plot_mu_list, cfg.fermipm, cfg.erange, cfg.margin, xlim_values, ylim_values, trace)
            
            # Transportgrößen vs m
            elif cfg.X_name in ["m"]:
                bt2.plot_Y_input(cfg.Y_name, cfg.X_name, cfg.plot_m_list, cfg.bins, cfg.T_list, plot_T, plot_mu, cfg.fermipm, cfg.erange, cfg.margin, xlim_values, ylim_values)


