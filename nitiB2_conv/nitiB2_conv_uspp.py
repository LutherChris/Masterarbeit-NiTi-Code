import numpy as np
from lib.run_conv import run

# ###################################################################################
# Parameter der Konvergenz
# ###################################################################################

diff_value = 2 # in meV

# -----------------------------------------------------------------------------------
# Konvergenz bzgl. "ecutwfc"
# -----------------------------------------------------------------------------------
ecutwfc = False
cutoff_list = np.arange(20,51,1)
#print(cutoff_list)

# -----------------------------------------------------------------------------------
# Konvergenz bzgl. "K_POINTS automatic"
# -----------------------------------------------------------------------------------
kpoints = False
nk_list_K_POINTS = np.arange(2, 23, 1)
#print(nk_list_K_POINTS)

# -----------------------------------------------------------------------------------
# Konvergenz bzgl. "celldm"
# -----------------------------------------------------------------------------------
celldm = False
celldm_list = np.arange(5.5627, 5.6628, 0.1)
#print(celldm_list)

# -----------------------------------------------------------------------------------
# Konvergenz bzgl. Smearing
# -----------------------------------------------------------------------------------
smearing = False
#key_smearing = "gauss"
#key_smearing = "marzari-vanderbilt"
key_smearing = "methfessel-paxton"
degauss_list = np.arange(0.01, 0.105, 0.01)
nk_list_smearing = [18, 19, 20]
#print(degauss_list)

# ###################################################################################
# Plotten und Analysieren
# ###################################################################################

plot = False
key_plot = "ecutwfc"
#key_plot = "kpoints"
#key_plot = "celldm"
#key_plot = "smearing"
nk_list_smearing_plot = nk_list_smearing

if __name__ == "__main__":
    run(cfg=__import__(__name__))