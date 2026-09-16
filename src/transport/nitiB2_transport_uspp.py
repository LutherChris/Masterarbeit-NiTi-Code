import numpy as np
# -----------------------------------------------------------------------------------
from lib.run_transport import run

# Standartwerte
plot_T_list, plot_mu_list = None, None
xlim_values, ylim_values = None, None
trace = True
plot_T, plot_mu = None, None
plot_m, cv_perT_vs_T = None, False

# -----------------------------------------------------------------------------------
# Interpolation(en) durch BoltzTrap2
fermipm, erange, margin = None, None, None
calc = False
# -----------------------------------------------------------------------------------

m_values = [1, 5, 10, 20, 30, 40, 50, 60, 70, 80] # Abbruch m=90, fitde3D
bins_values = [3000]
T_list = np.arange(10, 430, 10)

# -----------------------------------------------------------------------------------
# Plots der Transportgrößen
plot = True
# -----------------------------------------------------------------------------------
bins = 3000

# Seebeck-Koeffizient vs. chemisches Potential
Y_name="seebeck"; X_name="mu"; plot_m_list=[80]; plot_T_list=[50, 100, 200, 330, 400]
#Y_name="seebeck"; X_name="mu"; plot_m_list=[10, 20, 30, 40, 50, 60, 70, 80]; plot_T_list=[200]

# Seebeck-Koeffizient vs. Temperatur
#Y_name="seebeck"; X_name="T"; plot_m_list=[80]
#Y_name="seebeck"; X_name="T"; plot_m_list=m_values

# Seebeck-Koeffizient vs. m 
#Y_name="seebeck"; X_name="m"; plot_m_list=m_values
#Y_name="seebeck"; X_name="m"; plot_m_list=m_values; plot_T=400
#Y_name="seebeck"; X_name="m"; plot_m_list=m_values; plot_T=50

# -----------------------------------------------------------------------------------
# Wärmekapazität vs. chemisches Potential
#Y_name="cv"; X_name="mu"; plot_m_list=[80]; plot_T_list=[10, 50, 100, 200, 330, 400]
#Y_name="cv"; X_name="mu"; plot_m_list=m_values

# Wärmekapazität vs. Temperatur
#Y_name="cv"; X_name="T"; plot_m_list=[80]
#Y_name="cv"; X_name="T"; plot_m_list=m_values

# Wärmekapazität/Tempertatur vs. Temperatur
#cv_perT_vs_T = True; plot_m=80

# Wärmekapazität vs. m 
#Y_name="cv"; X_name="m"; plot_m_list=m_values
#Y_name="cv"; X_name="m"; plot_m_list=m_values; plot_T=400

#--------------------------------------------------------------------
# Leitfähigkeit pro Streurate vs. chemisches Potential
#Y_name="sigma"; X_name="mu"; plot_m_list=[80]; plot_T_list=[10, 50, 100, 200, 330, 400]
#Y_name="sigma"; X_name="mu"; plot_m_list=m_values

# Leitfähigkeit pro Streurate vs. Temperatur
#Y_name="sigma"; X_name="T"; plot_m_list=[80]
#Y_name="sigma"; X_name="T"; plot_m_list=[5, 10, 20, 30, 40, 50, 60, 70, 80]

# Leitfähigkeit pro Streurate vs m 
#Y_name="sigma"; X_name="m"; plot_m_list=m_values
#Y_name="sigma"; X_name="m"; plot_m_list=m_values; plot_T=400

#--------------------------------------------------------------------
# Wärmeleitfähigkeit pro Streurate vs. chemisches Potential
#Y_name="kappa"; X_name="mu"; plot_m_list=[80]; plot_T_list=[10, 50, 100, 200, 330, 400]
#Y_name="kappa"; X_name="mu"; plot_m_list=m_values

# Wärmeleitfähigkeit pro Streurate vs. Temperatur
#Y_name="kappa"; X_name="T"; plot_m_list=[80]
#Y_name="kappa"; X_name="T"; plot_m_list=m_values

# Wärmeleitfähigkeit pro Streurate vs m 
#Y_name="kappa"; X_name="m"; plot_m_list=m_values
#Y_name="kappa"; X_name="m"; plot_m_list=m_values; plot_T=400

#--------------------------------------------------------------------
# Hall-Koeffizient vs. chemisches Potential
#Y_name="hall"; X_name="mu"; plot_m_list=[80]; plot_T_list=[10, 50, 100, 200, 330, 400]
#Y_name="hall"; X_name="mu"; plot_m_list=m_values

# Hall-Koeffizient pro Streurate vs. Temperatur
#Y_name="hall"; X_name="T"; plot_m_list=[80]
#Y_name="hall"; X_name="T"; plot_m_list=[5, 10, 20, 30, 40, 50, 60, 70, 80]

# Hall-Koeffizient pro Streurate vs m 
#Y_name="hall"; X_name="m"; plot_m_list=m_values
Y_name="hall"; X_name="m"; plot_m_list=m_values; plot_T=400

if __name__ == "__main__":
    run(cfg=__import__(__name__))