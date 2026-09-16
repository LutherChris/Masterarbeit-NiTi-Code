import os
import os.path
import shutil

# Hier werden die Pfade der Ordner definiert.
# ##################################################################

#prefix = "nitiB2_model"
#prefix = "nitiB2_modelMME"
prefix = "nitiB2_point2A"

# ##################################################################

# PBEsol_precision - ultra-soft-pseudo-potential uspp
#main_directory = f"/home/chris/nitiB2_uspp"
main_directory = f"/home/chris/nitiB2_uspp_pbesol2.0"

# PBEsol_nc - non-conserving nc
#main_directory = f"/home/chris/nitiB2_nc"

# ##################################################################

qe_working_directory = main_directory + f"/{prefix}"
bt2_working_directory = main_directory + f"/tmp_{prefix}"

def suffix(datlabel, p, n):
    suffix_ = f"{datlabel}_p{str(p).replace('.','')}_n{str(n).replace('.','')}"
    return suffix_

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

def path_nscf_in():
    # main_directory/qe_working_directory/prefix.nscf.in
    filename_nscf_in = f"{prefix}.nscf.in"
    path_nscf_in_ = os.path.join(qe_working_directory, filename_nscf_in)
    return path_nscf_in_

def path_nscf_out():
    # main_directory/qe_working_directory/.nscf.out
    filename_nscf_out = f"{prefix}.nscf.out"
    path_nscf_out_ = os.path.join(qe_working_directory, filename_nscf_out)
    return path_nscf_out_

# ------------------------------------------------------------------
# Ordner:
# prefix_out und prefix_tmp
# ------------------------------------------------------------------
def path_tmp_directory(datlabel, p, n):
    # main_directory/prefix_tmp/suffix
    suffix_ = suffix(datlabel, p, n)
    path_tmp_ = os.path.join(main_directory, f"{prefix}_tmp")
    if not os.path.exists(path_tmp_):
        os.makedirs(path_tmp_)
    path_tmp_directory_ = os.path.join(path_tmp_, f"{suffix_}")
    if not os.path.exists(path_tmp_directory_):
        os.makedirs(path_tmp_directory_)
    return path_tmp_directory_

def path_out_directory(datlabel, p, n):
    # main_directory/prefix_out/suffix
    suffix_ = suffix(datlabel, p, n)
    path_out = os.path.join(main_directory, f"{prefix}_out")
    if not os.path.exists(path_out):
        os.makedirs(path_out)
    path_out_directory_ = os.path.join(path_out, f"{suffix_}")
    if not os.path.exists(path_out_directory_):
        os.makedirs(path_out_directory_)
    return path_out_directory_

# ------------------------------------------------------------------
# Dateien:
# scf und nscf-Rechnung in main_directory/prefix_out/suffix
# ------------------------------------------------------------------

def path_scf_in_out_directory(datlabel, p, n):
    # main_directory/prefix_out/suffix/prefix.nscf.in
    path_out_directory_ = path_out_directory(datlabel, p, n)
    filename_scf_in = f"{prefix}.scf.in"
    path_scf_in_out_directory_ = os.path.join(path_out_directory_, filename_scf_in)
    return path_scf_in_out_directory_

def path_nscf_in_out_directory(datlabel, p, n):
    # main_directory/prefix_out/suffix/prefix.nscf.in
    path_out_directory_ = path_out_directory(datlabel, p, n)
    filename_nscf_in = f"{prefix}.nscf.in"
    path_nscf_in_out_directory_ = os.path.join(path_out_directory_, filename_nscf_in)
    return path_nscf_in_out_directory_

# ------------------------------------------------------------------
# Ordner:
# Ergebnisse in Form von csv-Dateien (im Modell-Unterordner)
# ------------------------------------------------------------------
def path_result_directory(modeltype, datlabel, p, n):
    # main_directory/prefix_out/suffix/modeltype
    path_out_directory_ = path_out_directory(datlabel, p, n)
    path_result_directory_ = os.path.join(path_out_directory_, f"{modeltype}")
    if not os.path.exists(path_result_directory_):
        os.makedirs(path_result_directory_)
    return path_result_directory_

# ------------------------------------------------------------------
# Ordner:
# für Kopie des tmp_prefix-Ordners der scf-Rechnung
# ------------------------------------------------------------------

def path_COPY_directory():
    # main_directory/tmp_prefix_COPY
    path_COPY_directory_ = os.path.join(main_directory, f"tmp_{prefix}_COPY")
    if not os.path.exists(path_COPY_directory_):
        os.makedirs(path_COPY_directory_)
    return path_COPY_directory_

# ------------------------------------------------------------------
# Dateien:
# xml-Dateien der scf und nscf-Rechnung
# ------------------------------------------------------------------

def path_xml(datlabel, p, n):
    # main_directory/prefix_tmp/suffix/prefix.xml
    xml_filename = f"{prefix}.xml"
    path_tmp_directory_ = path_tmp_directory(datlabel, p, n)
    path_xml_ = os.path.join(path_tmp_directory_, xml_filename)
    return path_xml_

def path_scf_xml_():
    # main_directory/tmp_prefix_COPY/prefix.xml
    scf_xml_filename = f"{prefix}.xml"
    path_copy_ = path_COPY_directory()
    path_scf_xml_ = os.path.join(path_copy_, scf_xml_filename)
    return path_scf_xml_

# ------------------------------------------------------------------
# Ordner und Dateien:
# für Kopien der xml-Dateien im _out Ordner
# ------------------------------------------------------------------

def path_scf_xml_COPY_directory(datlabel, p, n):
    # main_directory/prefix_out/suffix/scf
    path_out_directory_ = path_out_directory(datlabel, p, n)
    path_scf_xml_COPY_directory_ = os.path.join(path_out_directory_, "scf")
    if not os.path.exists(path_scf_xml_COPY_directory_):
        os.makedirs(path_scf_xml_COPY_directory_)
    return path_scf_xml_COPY_directory_

def path_scf_xml_copy(datlabel, p, n):
    # main_directory/prefix_out/suffix/scf/prefix.mxl
    xml_filename = f"{prefix}.xml"
    path_scf_xml_COPY_directory_ = path_scf_xml_COPY_directory(datlabel, p, n)
    path_xml_= os.path.join(path_scf_xml_COPY_directory_, xml_filename)
    return path_xml_

def path_nscf_xml_COPY_directory(datlabel, p, n):
    # main_directory/prefix_out/suffix/nscf
    path_out_directory_ = path_out_directory(datlabel, p, n)
    path_nscf_xml_COPY_directory_ = os.path.join(path_out_directory_, "nscf")
    if not os.path.exists(path_nscf_xml_COPY_directory_):
        os.makedirs(path_nscf_xml_COPY_directory_)
    return path_nscf_xml_COPY_directory_

def path_nscf_xml_copy(datlabel, p, n):
    # main_directory/prefix_out/suffix/nscf/prefix.xml
    xml_filename = f"{prefix}.xml"
    path_nscf_xml_COPY_directory_ = path_nscf_xml_COPY_directory(datlabel, p, n)
    path_xml_= os.path.join(path_nscf_xml_COPY_directory_, xml_filename)
    return path_xml_

# ------------------------------------------------------------------
# Datei:
# log-Datei der QE-Rechnung mit den Rechenzeiten
# ------------------------------------------------------------------

def path_log():
    # main_directory/qe_working_directory/log/log
    path_log_directory_ = os.path.join(qe_working_directory, "log")
    if not os.path.exists(path_log_directory_):
        os.makedirs(path_log_directory_)
    path_log_ = os.path.join(path_log_directory_, "log")
    return path_log_
 
# ------------------------------------------------------------------
# Dateien:
# für die Berechnung der Matrix-Elemente
# bands_x.in, bands_x.out, p_avg.dat
# ------------------------------------------------------------------

def path_bands_x_in():
    # main_directory/qe_working_directory/prefix.bands_x.in
    filename_bands_x_in = f"{prefix}.bands_x.in"
    path_bands_x_in_ = os.path.join(qe_working_directory, filename_bands_x_in)
    return path_bands_x_in_

def path_bands_x_out():
    # main_directory/qe_working_directory/prefix.bands_x.out
    filename_bands_x_out = f"{prefix}.bands_x.out"
    path_bands_x_out_ = os.path.join(qe_working_directory, filename_bands_x_out)
    return path_bands_x_out_

def path_p_avg_copy(datlabel, p, n):
    # main_directory/prefix_out/suffix/prefix_p_avg.dat
    filename_p_avg = f"{prefix}_p_avg.dat"
    path_out_directory_ = path_out_directory(datlabel, p, n)
    path_filename_p_avg_ = os.path.join(path_out_directory_, filename_p_avg)
    return path_filename_p_avg_
 
# ##################################################################
# Hilfsfunktionen zum kopieren und Löschen von Ordnern
# ##################################################################

def copy_folder(source_folder, copy_folder):
    """
    Hilfsfunktion kopiert alle Daten von einen Ordner in einen anderen
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
    Hilfsfunktion zum löschen aller Daten in einem Ordner
    """
    for element in os.listdir(path):
        element_path = os.path.join(path, element)
        if os.path.isfile(element_path) or os.path.islink(element_path):
            os.unlink(element_path)  # Datei oder Symlink löschen
        elif os.path.isdir(element_path):
            shutil.rmtree(element_path)
