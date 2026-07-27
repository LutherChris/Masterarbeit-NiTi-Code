import os
import os.path

# Hier werden die Pfade der Ordner definiert.
# ##################################################################

prefix = "nitiB2_fermi"
#prefix = "nitiB2_fermi_2"

# ##################################################################

# PBEsol_precision - ultra-soft-pseudo-potential uspp
main_directory = f"/home/chris/nitiB2_uspp"

# PBEsol_nc - non-conserving nc
#main_directory = f"/home/chris/nitiB2_nc"

####################################################################
qe_working_directory = main_directory + f"/{prefix}"
bt2_working_directory = main_directory + f"/tmp_{prefix}"

# ------------------------------------------------------------------
# Ordner und Dateien für plotbands.py
# ------------------------------------------------------------------

def path_gnufile(datname):
    # main_directory/qe_working_directory/datname
    path_gnufile_ = os.path.join(qe_working_directory, datname)
    return path_gnufile_
