import os
import os.path

# ##################################################################
prefix = "B2_conv"
main_directory = f"/home/chris/VS_code/Masterarbeit-NiTi-Code/examples/B2_uspp"
num_cores = 6 
num_pool = 3

####################################################################
qe_working_directory = main_directory + f"/{prefix}"
bt2_working_directory = main_directory + f"/tmp_{prefix}"

# ------------------------------------------------------------------
# Dateien:
# scf.in, scf.out, nscf.in, nscf.out im Konfigurationsordner von QE
# ------------------------------------------------------------------
def path_scf_in():
    # main_directory/qe_working_directory/prefix.scf.in
    filename_scf_in = f"{prefix}.scf.in"
    path_scf_in_ = os.path.join(qe_working_directory, filename_scf_in)
    return path_scf_in_

def path_scf_out():
    # main_directory/qe_working_directory/prefix.scf.out
    filename_scf_out = f"{prefix}.scf.out"
    path_scf_out_ = os.path.join(qe_working_directory, filename_scf_out)
    return path_scf_out_

# ------------------------------------------------------------------
# Sicherheitskopie der in-Datei 
# ------------------------------------------------------------------

def path_scf_in_copy():
    # main_directory/qe_working_directory/copy/prefix.scf.in
    # Ort der Sicherheitskopie der in-Datei
    copysave_directory_ = os.path.join(qe_working_directory ,"copy")
    if not os.path.exists(copysave_directory_):
        os.makedirs(copysave_directory_)
    filename_scf_in_ = f"{prefix}.scf.in"
    path_scf_in_copy_ = os.path.join(copysave_directory_ , filename_scf_in_)
    return path_scf_in_copy_

# ------------------------------------------------------------------
# Result-Dateien der Konvergenz-Rechnung
# ------------------------------------------------------------------

def path_result_key(key):
    # main_directory/qe_working_directory/conv_results/prefix.key
    result_directory_ = os.path.join(qe_working_directory, "conv_results")
    if not os.path.exists(result_directory_):
        os.makedirs(result_directory_)
    resultname_ = f"{prefix}.{key}"
    path_result_key_ = os.path.join(result_directory_, resultname_)
    return path_result_key_

# ------------------------------------------------------------------
# Temporäre Dateien
# ------------------------------------------------------------------

def path_tmp():
    path_temp_ = os.path.join(qe_working_directory, "tmp")
    if not os.path.exists(path_temp_):
        os.makedirs(path_temp_)
    return path_temp_