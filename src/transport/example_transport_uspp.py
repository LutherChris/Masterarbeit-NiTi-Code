import numpy as np
# -----------------------------------------------------------------------------------
from lib.run_transport import run

# -----------------------------------------------------------------------------------
# Interpolation(s) by BoltzTraP2
fermipm, erange, margin = None, None, None
calc = False
# -----------------------------------------------------------------------------------

m_values = [1, 5, 10, 20, 30, 40, 50, 60, 70, 80] # Abbruch m=90, fitde3D
bins_values = [3000]
T_list = np.arange(10, 430, 10)

# -----------------------------------------------------------------------------------
# Plots of transport quantities
plot = True
# -----------------------------------------------------------------------------------
bins = 3000

# Seebeck coefficient vs. chemical potential
Y_name="seebeck"; X_name="mu"; plot_m_list=[80]; plot_T_list=[50, 100, 200, 330, 400]
#Y_name="seebeck"; X_name="mu"; plot_m_list=[10, 20, 30, 40, 50, 60, 70, 80]; plot_T_list=[200]

# Seebeck coefficient vs. temperature
#Y_name="seebeck"; X_name="T"; plot_m_list=[80]
#Y_name="seebeck"; X_name="T"; plot_m_list=m_values

# Seebeck coefficient vs. m 
#Y_name="seebeck"; X_name="m"; plot_m_list=m_values
#Y_name="seebeck"; X_name="m"; plot_m_list=m_values; plot_T=400
#Y_name="seebeck"; X_name="m"; plot_m_list=m_values; plot_T=50

# -----------------------------------------------------------------------------------
# Heat capacity vs. chemical potential
#Y_name="cv"; X_name="mu"; plot_m_list=[80]; plot_T_list=[10, 50, 100, 200, 330, 400]
#Y_name="cv"; X_name="mu"; plot_m_list=m_values

# Heat capacity vs. temperature
#Y_name="cv"; X_name="T"; plot_m_list=[80]
#Y_name="cv"; X_name="T"; plot_m_list=m_values

# Heat capacity/temperature vs. temperature
#cv_perT_vs_T = True; plot_m=80

# Heat capacity vs. m 
#Y_name="cv"; X_name="m"; plot_m_list=m_values
#Y_name="cv"; X_name="m"; plot_m_list=m_values; plot_T=400

#--------------------------------------------------------------------
# Conductivity per scattering rate vs. chemical potential
#Y_name="sigma"; X_name="mu"; plot_m_list=[80]; plot_T_list=[10, 50, 100, 200, 330, 400]
#Y_name="sigma"; X_name="mu"; plot_m_list=m_values

# Conductivity per scattering rate vs. temperature
#Y_name="sigma"; X_name="T"; plot_m_list=[80]
#Y_name="sigma"; X_name="T"; plot_m_list=[5, 10, 20, 30, 40, 50, 60, 70, 80]

# Conductivity per scattering rate vs m
#Y_name="sigma"; X_name="m"; plot_m_list=m_values
#Y_name="sigma"; X_name="m"; plot_m_list=m_values; plot_T=400

#--------------------------------------------------------------------
# Thermal conductivity per scattering rate vs. chemical potential
#Y_name="kappa"; X_name="mu"; plot_m_list=[80]; plot_T_list=[10, 50, 100, 200, 330, 400]
#Y_name="kappa"; X_name="mu"; plot_m_list=m_values

# Thermal conductivity per scattering rate vs. temperature
#Y_name="kappa"; X_name="T"; plot_m_list=[80]
#Y_name="kappa"; X_name="T"; plot_m_list=m_values

# Thermal conductivity per scattering rate vs m
#Y_name="kappa"; X_name="m"; plot_m_list=m_values
#Y_name="kappa"; X_name="m"; plot_m_list=m_values; plot_T=400

#--------------------------------------------------------------------
# Hall coefficient vs. chemical potential
#Y_name="hall"; X_name="mu"; plot_m_list=[80]; plot_T_list=[10, 50, 100, 200, 330, 400]
#Y_name="hall"; X_name="mu"; plot_m_list=m_values

# Hall coefficient per scattering rate vs. temperature
#Y_name="hall"; X_name="T"; plot_m_list=[80]
#Y_name="hall"; X_name="T"; plot_m_list=[5, 10, 20, 30, 40, 50, 60, 70, 80]

# Hall coefficient per scattering rate vs m
#Y_name="hall"; X_name="m"; plot_m_list=m_values
Y_name="hall"; X_name="m"; plot_m_list=m_values; plot_T=400

if __name__ == "__main__":
    run(cfg=__import__(__name__))