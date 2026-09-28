import numpy as np
from lib.run_conv import run

# ###################################################################################
# Parameters of convergence
# ###################################################################################

diff_value = 2 # in meV

# -----------------------------------------------------------------------------------
# Convergence regarding "ecutwfc"
# -----------------------------------------------------------------------------------
ecutwfc = False
cutoff_list = np.arange(20,51,1)
#print(cutoff_list)

# -----------------------------------------------------------------------------------
# Convergence regarding "K_POINTS automatic"
# -----------------------------------------------------------------------------------
kpoints = False
nk_list_K_POINTS = np.arange(2, 23, 1)
#print(nk_list_K_POINTS)

# -----------------------------------------------------------------------------------
# Convergence regarding "celldm"
# -----------------------------------------------------------------------------------
celldm = False
celldm_list = np.arange(5.5627, 5.6628, 0.1)
#print(celldm_list)

# -----------------------------------------------------------------------------------
# Convergence regarding Smearing
# -----------------------------------------------------------------------------------
smearing = False
#key_smearing = "gauss"
#key_smearing = "marzari-vanderbilt"
key_smearing = "methfessel-paxton"
degauss_list = np.arange(0.01, 0.105, 0.01)
nk_list_smearing = [18, 19, 20]
#print(degauss_list)

# ###################################################################################
# Plotting and analyzing
# ###################################################################################

plot = False
key_plot = "ecutwfc"
#key_plot = "kpoints"
#key_plot = "celldm"
#key_plot = "smearing"
nk_list_smearing_plot = nk_list_smearing

if __name__ == "__main__":
    run(cfg=__import__(__name__))