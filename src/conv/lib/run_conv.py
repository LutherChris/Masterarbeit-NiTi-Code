import numpy as np
import matplotlib.pyplot as plt
import shutil
# -----------------------------------------------------------------------------------
import lib.qe_conv as qe
import lib.config as config
from lib.plot_config import FIGWIDTH, HFACTOR, DATEIENNAME, SHOW, SAVE, TITEL, PLOT_SETTINGS

"""
Diese Datei lädt cfg.-Parameter aus z.B. nitiB2_conv_uspp.py und aktiviert verschiedene Abschnitte:
- Konvergenz bzgl. "celldm"
- Konvergenz bzgl. "ecutwfc"
- Konvergenz bzgl. "K_POINTS automatic"
- Konvergenz bzgl. smearing
- Plotten

# ===================================================================================
# Übersicht aller Parameter
# ===================================================================================

cfg.diff_value              (float) Parameter des Konvergenzkriteriums in meV
    Konvergenzkriterium :
        max( |E_n-2 - E_n-1| , |E_n   - E_n-1| ) < cfg.diff_value 
        max( |E_n-1 - E_n  | , |E_n+1 - E_n  | ) < cfg.diff_value 
        max( |E_n   - E_n+1| , |E_n+2 - E_n+1| ) < cfg.diff_value 
    - Diese Formel gilt für den Fall dass die Parameter eine Schrittweite von genau 1 haben.
    - Die Schrittweite wird im Code berücksichtigt, indem durch |n_2 - n_1| usw... geteilt wird.

# -----------------------------------------------------------------------------------
# Konvergenz bzgl. "ecutwfc"
# -----------------------------------------------------------------------------------
cfg.ecutwfc:                (bool) Aktiviert die Konvergenz bzgl. "ecutwfc"
cfg.cutoff_list:            (list) Liste verschiedener ecutwfc-Werte

# -----------------------------------------------------------------------------------
# Konvergenz bzgl. "nk" in K_POINTS automatic"
# -----------------------------------------------------------------------------------
cfg.k_points:               (bool) Aktiviert die Konvergenz bzgl. "K_POINTS automatic"
cfg.nk_list_K_POINTS:       (list) Liste verschiedener nk-Werte

# -----------------------------------------------------------------------------------
# Konvergenz bzgl. "celldm"
# -----------------------------------------------------------------------------------
cfg.celldm:                 (bool) Aktiviert die Konvergenz bzgl. "celldm"
cfg.celldm_list:            (list) Liste verschiedener celldm-Werte

# -----------------------------------------------------------------------------------
# Konvergenz bzgl. smearing
# -----------------------------------------------------------------------------------
cfg.smearing:               (bool) Aktiviert die Konvergenz bzgl. smearing
cfg.key_smearing:           (str) Smearing-Typ
                                möglich: "gauss", "marzari-vanderbilt", "methfessel-paxton"
cfg.degauss_list:           (list) Liste verschiedener degauss-Werte
cfg.nk_list_smearing:       (list) Liste verschiedener nk-Werte

# -----------------------------------------------------------------------------------
# Plots
# -----------------------------------------------------------------------------------
cfg.plot:                   (bool) Aktiviert Plots
cfg.key_plot:               (str) Welche Konvergenz-Kurve soll geplottet werden?
                               möglich: "celldm", "ecutwfc", "k_points", "smearing"
cfg.nk_list_smearing_plot:  (list) Falls key_plot="smearing", welche nk-Werte sollen geplottet werden?
"""

def run(cfg):
    # Laden der Plot-Einstellungen aus plot_config.py
    plt.rcParams.update(PLOT_SETTINGS)
    # Pfade der .in und .out Dateien
    path_in = config.path_scf_in()
    path_out = config.path_scf_out()

    # Erstelle Sicherheitskopie der in-Datei
    path_scf_in_copy = config.path_scf_in_copy()
    shutil.copyfile(path_in, path_scf_in_copy)      

    # -----------------------------------------------------------------------------------
    # Konvergenz bzgl. "celldm"
    # -----------------------------------------------------------------------------------

    if cfg.celldm:

        key_ = "celldm"
        key_save = key_
        key_list = cfg.celldm_list

        # Konvergenz bzgl. celldm
        E_list = []
        for celldm in key_list:
            # Namelist-Parameter celldm ändern
            qe.change_config_namelist(path_in, key_, celldm)
            # QE-Rechnung und Rückgabe der konvergierten Gesamtenergie
            etot = qe.energy(path_in, path_out)
            E_list.append(float(etot))
        print(f"Liste der konvergierten Gesamtenergie:\n {E_list}")

        # Speichern der Ergebnisse
        path_results = config.path_result_key(key_save)
        with open(path_results, 'w') as f:
            f.write(f"# {key_save} [a.u.], Gesamtenergie [Ry]\n")
            for i in range(len(E_list)):
                f.write(f"{key_list[i]}, {E_list[i]}\n")
        
    # -----------------------------------------------------------------------------------
    # Konvergenz bzgl. "ecutwfc"
    # -----------------------------------------------------------------------------------

    if cfg.ecutwfc:

        key_ = "ecutwfc"
        key_save = key_
        cutoff_list = cfg.cutoff_list

        # Konvergenz bzgl. ecutwfc
        E_list = []
        for cutoff in cutoff_list:
            # Namelist-Parameter ecutwfc ändern
            qe.change_config_namelist(path_in, key_, cutoff)
            # QE-Rechnung und Rückgabe der konvergierten Gesamtenergie
            etot = qe.energy(path_in, path_out)
            E_list.append(float(etot))
        print(f"Liste der konvergierten Gesamtenergie:\n {E_list}")

        # Speichern der Ergebnisse
        path_results = config.path_result_key(key_save)
        with open(path_results, 'w') as f:
            f.write(f"# {key_save} [Ry], Gesamtenergie [Ry]\n")
            for i in range(len(E_list)):
                f.write(f"{cutoff_list[i]}, {E_list[i]}\n")
    
    # -----------------------------------------------------------------------------------
    # Konvergenz bzgl. "K_POINTS automatic"
    # -----------------------------------------------------------------------------------

    if cfg.kpoints:

        key_ = "K_POINTS automatic"
        key_save = "kpoints"
        nk_list = cfg.nk_list_K_POINTS

        # erstelle Liste für K_POINTS automatic
        k_list = []
        for nk in nk_list:
            k_list.append(f"{nk} {nk} {nk} 1 1 1")
        print(f"Liste der kpoints:\n {k_list}")

        # Konvergenz bzgl nk in K_POINTS automatic
        E_list = []
        for k in k_list:
            # Card-Parameter K_POINTS automatic ändern
            qe.change_config_card(path_in, key_, k)
            # QE-Rechnung und Rückgabe der konvergierten Gesamtenergie
            etot= qe.energy(path_in, path_out)
            E_list.append(float(etot))
        print(f"Liste der konvergierten Gesamtenergie:\n {E_list}")

        # Speichern der Ergebnisse
        path_results = config.path_result_key(key_save)
        with open(path_results, 'w') as f:
            f.write(f"# {key_save} [nk nk nk 1 1 1], Gesamtenergie [Ry]\n")
            for i in range(len(E_list)):
                f.write(f"{nk_list[i]}, {E_list[i]}\n")
            
    # -----------------------------------------------------------------------------------
    # Konvergenz bzgl. smearing
    # -----------------------------------------------------------------------------------
    
    if cfg.smearing:

        smearings = ["gauss", "marzari-vanderbilt", "methfessel-paxton"]
        if cfg.key_smearing in smearings:
            key_smearing = cfg.key_smearing
        else:
            raise ValueError(f"Falsches key_smearing: {key_smearing}")

        degauss_list = cfg.degauss_list
        key_smearing = cfg.key_smearing
        nk_list = cfg.nk_list_smearing
        key1_ = "degauss"
        key2_ = "K_POINTS automatic"

        # Teste, ob richtiges smearing manuell eingestellt wurde
        qe.test_smearing(path_in, key_smearing)

        # erstelle Liste für K_POINTS automatic
        k_list = []
        for nk in nk_list:
            k_list.append(f"{nk} {nk} {nk} 1 1 1")
        print(f"Liste der K_POINTS automatic:\n {k_list}")

        # Konvergenz bzgl smearing
        for j in range(len(k_list)):
            # Card-Parameter K_POINTS automatic ändern
            qe.change_config_card(path_in, key2_, k_list[j])

            E_list = []
            for i in degauss_list:
                # Namelist-Parameter degauss ändern
                qe.change_config_namelist(path_in, key1_, i)
                # QE-Rechnung und Rückgabe der konvergierten Gesamtenergie
                etot = qe.energy(path_in, path_out)
                E_list.append(float(etot))
            print(E_list)

            # Speichern der Ergebnisse
            key_ = f"{key_smearing}.{nk_list[j]}"
            path_results = config.path_result_key(key_)
            with open(path_results, 'w') as f:
                f.write(f"# {key1_}, Gesamtenergie [Ry]\n")
                for i in range(len(E_list)):
                    f.write(f"{degauss_list[i]}, {E_list[i]}\n")
    
    # -----------------------------------------------------------------------------------
    # Plotten und Analysieren
    # -----------------------------------------------------------------------------------
    
    def difference(key_list, energy, value):
        """
        - Hilfsfunktion zur Berechnung des Konvergenzkriteriums
        """
        # Umrechnung der Energie in meV
        ry_to_ev = 13.605703976
        energy_mev = energy*ry_to_ev*1e3
 
        # Maximum der linksseitigen und rechtsseitigen Energiedifferenz
        # Randwerte haben nur linksseiten bzw. nur rechtsseitige Energiedifferenz
        # besser als Gradient, da der Gradient die Steigung herausmitteln kann
        dE = [np.abs(energy_mev[1] - energy_mev[0])]
        for i in range(1, len(energy_mev)-1):
            left = np.abs(energy_mev[i-1] - energy_mev[i])/np.abs(key_list[i-1] - key_list[i])
            right = np.abs(energy_mev[i+1] - energy_mev[i])/np.abs(key_list[i+1] - key_list[i])
            dE.append(max(left, right))
        dE.append(np.abs(energy_mev[-1] - energy_mev[-2]))
        dE = np.array(dE)
        print()
        print(f"maximale Energiedifferenz zu den Nachbarn in meV:\n {dE}")

        # Indize finden, an denen dE an zwei aufeinanderfolgenden Stellen kleiner als der Schwellenwert ist
        idx = None
        for i in range(1, len(energy_mev)-1):
            if (dE[i-1] < value) and (dE[i] < value) and (dE[i+1] < value): #!!! Anwendung des Konvergenzkriteriums
                idx = i
                break

        if idx is not None:
            print()
            print(f"Konvergenzkriterium mit value={value} meV erfüllt für:")
            print(f"key_list-Wert: {key_list[idx]}")
            print(f"Wert der Energie: {energy_mev[idx]}")
            print(f"maximale Energiedifferenz zum Nachbarn für (i-1), (i), (i+1):\n {float(dE[idx-1]), float(dE[idx]), float(dE[idx+1])}")
        else:
            print(f"Konvergenzkriterium ist nicht erfüllt. value={value}.")

    if cfg.plot:

        key_ = cfg.key_plot

        # ------------------------------------------------------------------------------
        # Plot von "celldm", "ecutwfc", "k_points"
        # ------------------------------------------------------------------------------
        if key_ in ["celldm", "ecutwfc", "kpoints"]:
            if key_ == "celldm":
                units = "[a.u.]"
            elif key_ == "ecutwfc":
                units = "[Ry]"
            elif key_ == "kpoints":
                units = "[nk nk nk 1 1 1]"

            key = key_
            # Daten laden
            path_results = config.path_result_key(key)
            key_list, etot_list = np.loadtxt(path_results, delimiter=",", unpack=True, skiprows=1)
            print()
            print(f"key_list:\n {key_list}")
            print()
            print(f"etot_list:\n {etot_list}")

            # Differenz und Konvergenzkriterium
            difference(key_list, etot_list, cfg.diff_value)

            # Abbildung erstellen
            plt.figure(figsize=(FIGWIDTH,FIGWIDTH*HFACTOR))
            plt.plot(key_list, etot_list, ".")
            plt.plot(key_list, etot_list, "-", color="grey")
            plt.ylabel("Gesamtenergie [Ry]")
            plt.xlabel(f"{key} {units}")       

            if TITEL:
                plt.title(f"{config.prefix}: Konvergenz bzgl. {key}")
            if SAVE:
                plt.savefig(f"{DATEIENNAME}.jpg")
                plt.savefig(f"{DATEIENNAME}.png")
                plt.savefig(f"{DATEIENNAME}.pdf")
            if SHOW:
                plt.show() 
        
        # ------------------------------------------------------------------------------
        # Plot von smearing
        # ------------------------------------------------------------------------------
    
        if key_ == "smearing":
            colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
            nk_list = cfg.nk_list_smearing_plot

            plt.figure(figsize=(FIGWIDTH,FIGWIDTH*HFACTOR))
            smearing = ["gauss", "marzari-vanderbilt", "methfessel-paxton"]
            for j in range(len(smearing)):
                for i in range(len(nk_list)):
                    path_key = f"{smearing[j]}.{nk_list[i]}"
                    path_results = config.path_result_key(path_key)
                    # Daten laden
                    degauss, etot = np.loadtxt(path_results, delimiter=",", unpack=True, skiprows=1)
                    if j == 0:
                        plt.plot(degauss, etot, "-", label=f"{smearing[j]} nk={nk_list[i]}", color=colors[i])
                    elif j == 1:
                        plt.plot(degauss, etot, "--", label=f"{smearing[j]} nk={nk_list[i]}", color=colors[i])
                    else:
                        plt.plot(degauss, etot, "-.", label=f"{smearing[j]} nk={nk_list[i]}", color=colors[i])

            plt.ylabel("Gesamtenergie [Ry]")
            plt.xlabel(f"degauss")
            plt.legend(loc="center left", bbox_to_anchor=(1, 0.5))
            
            # -------------------------------------------------

            if TITEL:
                plt.title(f"{config.prefix}: Konvergenz bzgl. smearing")  
            if SAVE:
                plt.savefig(f"{DATEIENNAME}.jpg")
                plt.savefig(f"{DATEIENNAME}.png")
                plt.savefig(f"{DATEIENNAME}.pdf")
            if SHOW:
                plt.show() 