#Bloc d'importation
import pandas as pd
import numpy as np
import math
import os

##### Constantes #####
rho = 6.371E6
phi_0 = 48.764246

# Chargement véhicules
data_vehicles = pd.read_csv("vehicles.csv")

# Chargement instances
instances = []
for k in range(1, 11):
    file_path = f"instance_{k:02d}.csv"
    df = pd.read_csv(file_path)
    instances.append(df.to_dict(orient="records"))

# Coordonnees
def yj_yi(phij, phii): #yj - yi
    return rho * 2 * np.pi * (phij - phii) / 360

def xj_xi(lambdaj, lambdai): #xj - xi
    return rho * math.cos(2 * np.pi * phi_0 / 360) * 2 * np.pi * (lambdaj - lambdai) / 360

def distM(i, j, instance_idx): #distance de manhattan entre i et j du fichier A
    deltax = xj_xi(instances[instance_idx][j]["longitude"], instances[instance_idx][i]["longitude"])
    deltay = yj_yi(instances[instance_idx][j]["latitude"], instances[instance_idx][i]["latitude"])
    return abs(deltax) + abs(deltay)

def gamma_f_max(row_f):
    # majorant simple
    return sum(
        np.sqrt(row_f[f"fourier_cos_{n}"]**2 + row_f[f"fourier_sin_{n}"]**2)
        for n in range(4)
    )

def temps_max(i, j, family, instance_idx):    
    """
    Returns the maximum travel time for a given family and instance index from i to j.
    tau_f(i,j|max) = (distM(i,j)/s_f + p_f) * gamma_f_max
    Args:
        family (str): The family of vehicles
        i (int): The starting node index.
        j (int): The ending node index.
        instance_idx (int): The index of the instance file.
    """
    row_f = data_vehicles.loc[data_vehicles["family"] == family].iloc[0]
    speed_f = row_f["speed"]
    p_f = row_f["service_time"]
    gamma_f = gamma_f_max(row_f)
    distance = distM(i, j, instance_idx)
    return (distance / speed_f + p_f) * gamma_f




def is_route_possible(family, sequence, instance_idx):
    """
    Determines if a given sequence of nodes can form a valid route
    for the specified instance index and family vehicle.

    Args:
        family (str): The family of vehicles
        sequence (list): A list of node indices representing the route.
        instance_idx (int): The index of the instance file.
    """
    # Contraine de temps => on veut que les fenetre de temps soient dans l'ordre croissant  et le tjmax -lj - timax >= tauij(tmax)
    
