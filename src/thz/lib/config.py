import os
import os.path
import shutil
import pandas as pd

# Hier werden die Pfade der Ordner definiert.
# ##################################################################

prefix = "nitiB2_thz"

####################################################################

# PBEsol_precision - ultra-soft-pseudo-potential uspp
main_directory = f"/home/chris/nitiB2_uspp"

# PBEsol_nc - non-conserving nc
#main_directory = f"/home/chris/nitiB2_nc"

####################################################################
# Parallele Berechnung
# mpirun -np {num_cores} pw.x -npool {num_pool} -in ... > ...

num_cores = 6   #-np    : Anzahl der physischen Prozessorkerne
num_pool = 3       #-npool : Anzahl der verknüpften Prozessorkerne

####################################################################

qe_working_directory = main_directory + f"/{prefix}"
bt2_working_directory = main_directory + f"/tmp_{prefix}"

def suffix(datlabel, nks, phi_steps, R, r):
    suffix = f"{datlabel}_nks{nks}_phisteps{phi_steps}_R{R:.6f}_r{r:.6f}"
    return suffix

def path_scf_in():
    # main_directory/prefix/prefix.scf.in
    filename_scf_in = f"{prefix}.scf.in"
    path_scf_in_ = os.path.join(qe_working_directory, filename_scf_in)
    return path_scf_in_

def path_scf_out():
    # main_directory/prefix/prefix.scf.out
    filename_scf_out = f"{prefix}.scf.out"
    path_scf_out_ = os.path.join(qe_working_directory, filename_scf_out)
    return path_scf_out_

def path_bands_in():
    # main_directory/prefix/prefix.bands.in
    filename_bands_in = f"{prefix}.bands.in"
    path_bands_in_ = os.path.join(qe_working_directory, filename_bands_in)
    return path_bands_in_

def path_bands_out():
    # main_directory/prefix/prefix.bands.out
    filename_bands_out = f"{prefix}.bands.out"
    path_bands_out_ = os.path.join(qe_working_directory, filename_bands_out)
    return path_bands_out_

def path_tmp_directory(datlabel, nks, phi_steps, R, r):
    # main_directory/prefix_tmp/suffix
    suffix_ = suffix(datlabel, nks, phi_steps, R, r)
    path_tmp_ = os.path.join(main_directory, f"{prefix}_tmp")
    if not os.path.exists(path_tmp_):
        os.makedirs(path_tmp_)
    path_tmp_directory_ = os.path.join(path_tmp_, f"{suffix_}")
    if not os.path.exists(path_tmp_directory_):
        os.makedirs(path_tmp_directory_)
    return path_tmp_directory_

def path_tmp_directory_i(datlabel, nks, phi_steps, R, r, i):
    # main_directory/prefix_tmp/suffix/i
    path_tmp_directory_ = path_tmp_directory(datlabel, nks, phi_steps, R, r)
    path_tmp_directory_i_ = os.path.join(path_tmp_directory_, f"{i}")
    if not os.path.exists(path_tmp_directory_i_):
            os.makedirs(path_tmp_directory_i_)
    return path_tmp_directory_i_

def path_out_directory(datlabel, nks, phi_steps, R, r):
    # main_directory/prefix_out/suffix
    suffix_ = suffix(datlabel, nks, phi_steps, R, r)
    path_out = os.path.join(main_directory, f"{prefix}_out")
    if not os.path.exists(path_out):
        os.makedirs(path_out)
    path_out_directory_ = os.path.join(path_out, f"{suffix_}")
    if not os.path.exists(path_out_directory_):
        os.makedirs(path_out_directory_)
    return path_out_directory_

def path_out_directory_i(datlabel, nks, phi_steps, R, r, i):
    # main_directory/prefix_out/suffix/i
    path_out_directory_ = path_out_directory(datlabel, nks, phi_steps, R, r)
    path_out_directory_i_ = os.path.join(path_out_directory_, f"{i}")
    if not os.path.exists(path_out_directory_i_):
        os.makedirs(path_out_directory_i_)
    return path_out_directory_i_

def path_COPY_directory():
    # main_directory/tmp_prefix_COPY
    path_COPY_directory_ = os.path.join(main_directory, f"tmp_{prefix}_COPY")
    if not os.path.exists(path_COPY_directory_):
        os.makedirs(path_COPY_directory_)
    return path_COPY_directory_

def path_xml(datlabel, nks, phi_steps, R, r, i):
    xml_filename = f"{prefix}.xml"
    path_tmp_directory_i_ = path_tmp_directory_i(datlabel, nks, phi_steps, R, r, i)
    path_xml_ = os.path.join(path_tmp_directory_i_, xml_filename)
    return path_xml_

def path_log():
    # main_directory/prefix/log
    path_log_ = os.path.join(qe_working_directory, "log")
    return path_log_

 
# ##################################################################
# Hilfsfunktionen zum kopieren und Löschen von Ordnern
# ##################################################################

def copy_folder(source_folder, copy_folder):
    """
    - Hilfsfunktion kopiert alle Daten von einen Ordner in einen anderen
    """
    for element in os.listdir(source_folder):
        source_path = os.path.join(source_folder, element)
        copy_path = os.path.join(copy_folder, element)
        if os.path.isdir(source_path):
            shutil.copytree(source_path, copy_path, dirs_exist_ok=True)
        else:
            shutil.copy2(source_path, copy_path)

def delete_folder(path):
    """
    - Hilfsfunktion zum löschen aller Daten in einem Ordner
    """
    for element in os.listdir(path):
        element_path = os.path.join(path, element)
        if os.path.isfile(element_path) or os.path.islink(element_path):
            os.unlink(element_path)  # Datei oder Symlink löschen
        elif os.path.isdir(element_path):
            shutil.rmtree(element_path)

# ######################################################################################
# Speichern und Laden von Dateien
# ######################################################################################

def save_csv(df, path, suffix, index: bool = False):
    """
    - Hilfsfunktion zum Speichern von Dataframes als csv-Datei
    """
    filename = f"{prefix}_{suffix}.csv"
    path_data = os.path.join(path, filename)
    df.to_csv(path_data, index=index)

def load_csv(path, suffix):
    """
    - Hilfsfunktion zum Laden von csv-Dateien
    """
    filename = f"{prefix}_{suffix}.csv"
    path_data = os.path.join(path, filename)
    df = pd.read_csv(path_data)
    return df

# ------------------------------------------------------------------
# Temporäre Dateien
# ------------------------------------------------------------------

def path_tmp():
    path_temp_ = os.path.join(qe_working_directory, "tmp")
    if not os.path.exists(path_temp_):
        os.makedirs(path_temp_)
    return path_temp_