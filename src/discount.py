import numpy as np
import scipy.integrate as integrate
import pandas as pd
import matplotlib.pyplot as plt
import os
import time
import csv

import read_in

"""This module is not relevant to run main.py"""

def discount_ts(g_flows, SDR_list):

    disc_GHG_flows = {0.0: g_flows}
    GHG_NPV = {0.0: {key: sum(g_flows[key]) for key in g_flows.keys()}}

    for SDR in SDR_list:
        disc_GHG_flows.update({SDR: {}})
        GHG_NPV.update({SDR: {}})
        for GHG in g_flows.keys():
            years = np.arange(len(g_flows[GHG]))
            disc_factors = 1 / ((1 + SDR) ** years)
            disc_flow = np.array(g_flows[GHG])*disc_factors
            disc_GHG_flows[SDR].update({GHG: disc_flow})
            GHG_NPV[SDR].update({GHG: sum(disc_flow)})

    return disc_GHG_flows, GHG_NPV

def save_disc_flows_in_csv(res_dict, save_path):


    """# 1. Flatten the dictionary structure using a list comprehension
    flat_list = []
    for status, inner_dict in res_dict.items(): #status: released, stored, net
        for SDR, gases in inner_dict.items():
            # Create a single flat dictionary per row
            row = {'Status': status, 'Value': SDR}
            row.update(gases)  # Adds CO2, CH4, N2O to the row dict
            flat_list.append(row)

    # 2. Convert to DataFrame and sort nicely
    df = pd.DataFrame(flat_list)
    df = df.sort_values(by=['Status', 'Value']).reset_index(drop=True)

    # 3. Export to CSV
    df.to_csv(save_path+'gas_data_flattened.csv', index=False)"""

    filename = save_path+'GHG_disc_data.csv'

    with open(filename, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["category", "SDR", "GHG", "index", "value"])

        for category, depths in res_dict.items():          # stored, released, net
            for SDR, gases in depths.items():         # 0.0, -0.03, ...
                for GHG, values in gases.items():        # CO2, CH4, N2O
                    for i, value in enumerate(values, start=1):
                        writer.writerow([category, SDR, GHG, i, value])


def print_min_max_values(disc_GHG_flows):

    print_dict = {}
    GHG_list = disc_GHG_flows[0.0].keys()
    SDR_list = disc_GHG_flows.keys()

    for SDR in SDR_list:
        print_dict.update({SDR: {}})
        for GHG in GHG_list:
            for i, j in enumerate(disc_GHG_flows[SDR][GHG]):
                if i == 0:
                    print_dict[SDR].update({GHG: [[i+1,j], [i+1,j]]})
                else:
                    if j != 0:
                        if j < print_dict[SDR][GHG][0][1]: print_dict[SDR][GHG][0] = [i+1,j]
                        if j > print_dict[SDR][GHG][1][1]: print_dict[SDR][GHG][1] = [i+1,j]

    for SDR in SDR_list:
            for GHG in GHG_list:
                print(f"{SDR}; {GHG}; Min: {print_dict[SDR][GHG][0]}; Max: {print_dict[SDR][GHG][1]}")



if __name__ == "__main__":
    save_path = f"C:/Users/Sebastian/Documents/Coding projects/CPT_CCU/results/{int(time.time())}/"
    os.makedirs(save_path)

    filepath_emission_data = "C:/Users/Sebastian/Documents/Coding projects/CPT_CCU/data/emission_flows.csv"
    g_emit, g_stored, g_net = read_in.read_emission_flows_csv(filepath_emission_data)
    
    SDR_list = [-0.03, -0.01, 0.0, 0.01, 0.03, 0.09]

    disc_GHG_flows, GHG_NPV = discount_ts(g_net, SDR_list)

    #res_dict = {"released": discount_ts(g_emit, SDR_list)[0], "stored": discount_ts(g_stored, SDR_list)[0], "net": discount_ts(g_net, SDR_list)[0]}

    #save_disc_flows_in_csv(res_dict, save_path)

    print_min_max_values(disc_GHG_flows)
    