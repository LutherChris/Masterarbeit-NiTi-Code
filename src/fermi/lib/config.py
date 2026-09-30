import os
import os.path

# ##################################################################
prefix = "B2_fermi"
main_directory = f"/home/chris/VS_code/Masterarbeit-NiTi-Code/examples/B2_uspp"

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
