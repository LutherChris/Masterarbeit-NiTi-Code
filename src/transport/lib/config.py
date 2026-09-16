import os
import os.path

# Hier werden die Pfade der Ordner definiert.
# ##################################################################

prefix = "nitiB2_transport"

# ##################################################################

# PBEsol_precision - ultra-soft-pseudo-potential uspp
main_directory = f"/home/chris/nitiB2_uspp"

# PBEsol_nc - non-conserving nc
#main_directory = f"/home/chris/nitiB2_nc"

####################################################################
qe_working_directory = main_directory + f"/{prefix}"
bt2_working_directory = main_directory + f"/tmp_{prefix}"

# ------------------------------------------------------------------
# Ordner und Dateien für BoltzTrap2-Rechnungen in bt2.py
# ------------------------------------------------------------------

def path_bt2_dft_directory():
    # main_directory/bt2_working_directory/prefix.save
    path_bt2_dft_directory_ = os.path.join(bt2_working_directory , f"{prefix}.save")
    return path_bt2_dft_directory_

def path_bt2_bt2file(m, fermipm):
    # main_directory/bt2_working_directory/interpolation_..._bt2
    bt2file_filename_ = f"interpolation_m{m}_fermipm{f"{fermipm:.4f}"}_bt2"
    path_bt2_bt2file_ = os.path.join(bt2_working_directory, bt2file_filename_)
    return path_bt2_bt2file_

def path_bt2_resultdata(m, fermipm, erange, margin, temp, bins):
    # main_directory/bt2_working_directory/results_..._btj
    resultdata_filename_ = f"results_m{m}_fermipm{f"{fermipm:.4f}"}_erange{f"{erange:.4f}"}_margin{f"{margin:.4f}"}_T{temp.min()}-{temp.max()}_bins{bins}_btj"
    path_bt2_resultdata_ = os.path.join(bt2_working_directory, resultdata_filename_)
    return path_bt2_resultdata_

# Log-Files
def path_log_interpolation(m, fermipm, erange, margin, temp, bins):
    # main_directory/bt2_working_directory/log_int__...
    logdata_directory_ = os.path.join(bt2_working_directory, "logs")
    if not os.path.exists(logdata_directory_):
        os.makedirs(logdata_directory_)
    log_int_filename_ = f"log_int__m{m}_fermipm{f"{fermipm:.4f}"}_erange{f"{erange:.4f}"}_margin{f"{margin:.4f}"}_T{temp.min()}-{temp.max()}_bins{bins}"
    path_log_interpolation_ = os.path.join(logdata_directory_, log_int_filename_)
    return path_log_interpolation_

def path_log_calculation(m, fermipm, erange, margin, temp, bins):
    # main_directory/bt2_working_directory/log_calc__...
    logdata_directory_ = os.path.join(bt2_working_directory, "logs")
    if not os.path.exists(logdata_directory_):
        os.makedirs(logdata_directory_)
    log_calc_filename_ = f"log_calc__m{m}_fermipm{f"{fermipm:.4f}"}_erange{f"{erange:.4f}"}_margin{f"{margin:.4f}"}_T{temp.min()}-{temp.max()}_bins{bins}"
    path_log_calculation_ = os.path.join(logdata_directory_, log_calc_filename_)
    return path_log_calculation_
