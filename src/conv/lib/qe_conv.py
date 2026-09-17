import re
import os
import shutil
import subprocess
import sys
# --------------------------------------------------------------------------------------
import lib.config as config

# --------------------------------------------------------------------------------------
# Funktionen zum Ändern der Quantum Espresso config-Dateien
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

def change_config_card(path_in: str,
                       card: str,
                       new_value: int):
    """
    - verändert den Wert eines card-Parameters auf einen neuen Wert und speichert die neue in-Datei

    Args:
        path_in:    Pfad der in-Datei von QE
        card:       card-Parameter
                    z.B. "K_POINTS automatic"
        new_value:  neuer Wert des Namelist-Parameters
                    z.B. "2 2 2 1 1 1"
    """
    filename = path_in.split("/")[-1]
    file = open(path_in, "r")
    file_lines = file.readlines()
    file.close()

    new_lines = []
    continue_again = False
    for i in range(len(file_lines)):
        if re.search(card, file_lines[i]):
            new_line = " "+str(new_value)+"\n"
            print(f"{file_lines[i+1]} > {new_line}")
            new_lines.append(file_lines[i])
            new_lines.append(new_line) 
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
# QE-Rechnung und Rückgabe der konvergierten Gesamtenergie
# --------------------------------------------------------------------------------------

def energy(path_in: str,
           path_out: str):
    """
    - führt QE mit der in-Datei aus
    - öffnet die out-Datei von QE und gibt die kovergierte Gesamtenergie zurück 

    Args:
        path_in:    Pfad der in-Datei von QE
        path_out:   Pfad der out-Datei von QE
    Return:
        energy:     konvergierte Gesamtenergie der out-Datei von QE
    """
    qe_working_directory = config.qe_working_directory
    num_cores = config.num_cores

    if num_cores > 1:
        print(f"- Parallele Berechnung mit {num_cores} Kernen")
        process = subprocess.Popen(f"cd {qe_working_directory} && mpirun -np {num_cores} pw.x -in {path_in} > {path_out}", shell=True, stdout=subprocess.DEVNULL)
    else:
        process = subprocess.Popen(f"cd {qe_working_directory} && pw.x -in {path_in} > {path_out}", shell=True, stdout=subprocess.DEVNULL)

    process.wait()
    file = open(path_out, "r")
    file_lines = file.readlines()
    file.close()
    
    for line in file_lines:
        if re.search("!", line):
            part = re.findall(r"[-+]?(?:\d*\.*\d+)", line)
            energy = part[0]
            print(f"total energy = {energy}\n")
    return energy

# --------------------------------------------------------------------------------------
# Überprüfung der smearing-Einstellung
# --------------------------------------------------------------------------------------

def test_smearing(path_in: str,
                  key: str):
    """
    Warum? Da die Zeichenfolge smearing in der In-Datei doppelt vorkommt, funktioniert change_config_namelist hier nicht.
    Deshalb muss das smearing manuell geändert werden.
    Diese Funktion dient dazu, zu testen, ob das gewünschte smearing in der in-Datei festgelegt wurde.

    Args:
        path_in:    Pfad der in-Datei von QE
        key:        smearing
                        "gauss"
                        "marzari-vanderbilt"
                        "methfessel-paxton"
    """
    file = open(path_in, "r")
    file_lines = file.readlines()
    file.close()
    if key == "gauss":
        n = []
        for line in file_lines:
            if re.search(key, line):
                n.append(1)
        if not len(n) == 2:
            sys.exit(f"! Ändere manuell in Datei zu smearing = {key} !")
    elif key == "marzari-vanderbilt":
        n = []
        for line in file_lines:
            if re.search(key, line):
                n.append(1)
        if not len(n) == 1:
            sys.exit(f"! Ändere manuell in Datei zu smearing = {key} !")
    elif key == "methfessel-paxton":
        n = []
        for line in file_lines:
            if re.search(key, line):
                n.append(1)
        if not len(n) == 1:
            sys.exit(f"! Ändere manuell in Datei zu smearing = {key} !")
    else:
        raise ValueError(f"Unbekanntes smearing: {key}")