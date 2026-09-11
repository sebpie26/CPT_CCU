import pandas as pd
import numpy as np



def read_emission_flows_csv(filepath):
    """
    Reads g_emit and g_stored from a CSV file.

    Parameters
    ----------
    filepath : str
        Path to the CSV file.

    Returns
    -------
    g_emit : np.ndarray
    g_stored : np.ndarray
    """

    df = pd.read_csv(filepath)

    GHG_list = ['CO2', 'CH4', 'N2O']
    """
    g_construction = {"CO2": df["CO2_construction"].to_numpy(), "CH4": df["CH4_construction"].to_numpy(), "N2O": df["N2O_construction"].to_numpy()}
    g_operation = {"CO2": df["CO2_operation"].to_numpy(), "CH4": df["CH4_operation"].to_numpy(), "N2O": df["N2O_operation"].to_numpy()}
    g_raw_material_acquisition = {"CO2": df["CO2_raw_material_acquisition"].to_numpy(), "CH4": df["CH4_raw_material_acquisition"].to_numpy(), "N2O": df["N2O_raw_material_acquisition"].to_numpy()}
    g_decommissioning = {"CO2": df["CO2_decommissioning"].to_numpy(), "CH4": df["CH4_decommissioning"].to_numpy(), "N2O": df["N2O_decommissioning"].to_numpy()}
    g_prod_use_phase = {"CO2": df["CO2_prod_use_phase"].to_numpy(), "CH4": df["CH4_prod_use_phase"].to_numpy(), "N2O": df["N2O_prod_use_phase"].to_numpy()}
    g_prod_EOL = {"CO2": df["CO2_prod_EOL"].to_numpy(), "CH4": df["CH4_prod_EOL"].to_numpy(), "N2O": df["N2O_prod_EOL"].to_numpy()}
    g_stored = {"CO2": df["CO2_stored"].to_numpy(), "CH4": df["CH4_stored"].to_numpy(), "N2O": df["N2O_stored"].to_numpy()}

    g_list = [g_construction, g_operation, g_raw_material_acquisition, g_decommissioning, g_prod_use_phase, g_prod_EOL, g_stored]
    
    g_net = {GHG : None for GHG in GHG_list}
    for GHG in GHG_list:
        g_net[GHG] = [sum(values) for values in zip(*g_list)]"""


    g_emit = {"CO2": df["CO2_emit"].to_numpy(), "CH4": df["CH4_emit"].to_numpy(), "N2O": df["N2O_emit"].to_numpy()}
    g_stored = {"CO2": df["CO2_stored"].to_numpy(), "CH4": np.zeros(len(df["CO2_stored"])), "N2O": np.zeros(len(df["CO2_stored"]))}
    g_net = {GHG: [g_emit[GHG][i]+g_stored[GHG][i] for i in range(len(g_emit[GHG]))] for GHG in GHG_list}



    return g_emit, g_stored, g_net


if __name__ == "__main__":
    
    filepath = "C:/Users/Sebastian/Documents/VSC Workspace/Individual project Industrial ecology/data/emission_flows.csv"

    g_emit, g_stored, g_net = read_emission_flows_csv(filepath)

    for key in ["CO2", "CH4", "N2O"]:
        print(len(g_emit[key]))
        print(len(g_stored[key]))
        print(len(g_net[key]))