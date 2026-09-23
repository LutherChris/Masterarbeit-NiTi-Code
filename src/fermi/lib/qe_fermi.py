import matplotlib.pyplot as plt
import pandas as pd
from itertools import cycle

# --------------------------------------------------------------------------------------
# Liste von pandas Dataframes der Bänder
# --------------------------------------------------------------------------------------

def open_bands_and_split(path):
    """
    Args:
        path:       Pfad der dat.gnu Datei
    return;
        df_list:    Liste der Bänder als pandas Dataframes
    """
    f = open(path, "r")
    f_lines = f.readlines()
    f.close

    j = []
    for i in range(len(f_lines)):
        if f_lines[i] == '\n':
            j.append(i)
    df = pd.read_csv(path, sep='\\s+', header=None, skip_blank_lines=False)
    df_list = [df[:j[0]]]
    for i in range(len(j)-1):
        df_list.append(df[j[i]+1 : j[i+1]])
    return df_list

# --------------------------------------------------------------------------------------
# Plot der Energiebänder
# --------------------------------------------------------------------------------------

def plot_bands(df_list,
               fermi_energy: int,
               fermi: bool=True):
    """
    - plottet die Energiebänder
    Args:
        df_list:        Liste der Bänder als pandas Dataframes
        fermi_energy:   Fermi-Energie aus QE
        fermi:          Soll die Energieskala anhand der Fermi-Energie verschoben werden?
    """
    colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
    colors_cycle = cycle(colors)

    def next_color():
        return next(colors_cycle)
    
    for i in range(len(df_list)):
        color = next_color()
        if fermi:
            plt.plot(df_list[i][0], df_list[i][1]-fermi_energy, ".", color=color)
            plt.plot(df_list[i][0], df_list[i][1]-fermi_energy, "-", color=color)
        else:
            plt.plot(df_list[i][0], df_list[i][1], ".", color=color)
            plt.plot(df_list[i][0], df_list[i][1], "-", color=color)
