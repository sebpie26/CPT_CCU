import numpy as np
import math as m

import dynamic_lca
import read_data



def graphical_CPT(g_net, model_params, TH, SDR):
    """Graphical determination of the CPT.

    Args:
        g_net (dict): Dictionary with GHGs as keys and yearly net emission flows (array) as values.
        TH (int): Impact modelling period in years.
        SDR (float): Social discount rate as decimal.

    Returns:
        tuple:
            - gCPT (float): Carbon payback time in years.
            - GWI_inst_net: Dictionary with GHGs and 'total' as keys and yearly instantaneous GWI values (array) as values.
            - GWI_cum_net: Array with cumulative GWI values.
    """

    GWI_inst_net, GWI_cum_net, disc_params_net = dynamic_lca.dynamic_GWI(g_flows=g_net, model_params=model_params, TH=TH, SDR=SDR)

    for i in range(len(GWI_cum_net)):
         
        if i == len(GWI_cum_net)-1:
            print("There's no graphical CPT.")
            return None, GWI_inst_net, GWI_cum_net, disc_params_net

        elif GWI_cum_net[0] < 0:
            print(f"The graphically determined CPT is in year 1. \nThe GWI in year 1 is {GWI_cum_net[0]} ton CO2e.")
            return 1, GWI_inst_net, GWI_cum_net, disc_params_net
        
        elif GWI_cum_net[i] == 0:
            gCPT = i+1
            print(f"The graphically determined CPT is in year {gCPT}. \nThe GWI in year {gCPT} is {GWI_cum_net[i]}ton CO2e.")
            return gCPT, GWI_inst_net, GWI_cum_net, disc_params_net

        elif GWI_cum_net[i] > 0 and GWI_cum_net[i+1] < 0:
            gCPT = np.interp(0, [GWI_cum_net[i+1], GWI_cum_net[i]], [i+1,i]) +1
            print(f"The graphically determined CPT is in year {gCPT}. \nThe GWI in year {m.floor(gCPT)} is {GWI_cum_net[i]}ton CO2e and in year {m.ceil(gCPT)}: {GWI_cum_net[i+1]} ton CO2e.")
            return gCPT, GWI_inst_net, GWI_cum_net, disc_params_net


def analytical_CPT(g_released, g_stored, model_params, lifetime, TH, SDR):
    """Analytical determination of the CPT.

    Args:
        g_released (dict): Dictionary with GHGs as keys and yearly released emission flows (array) as values.
        g_stored (dict): Dictionary with GHGs as keys and yearly stored emission flows (array) as values.
        L (int): Lifetime of the CCU plant.
        TH (int): Impact modelling period in years.
        SDR (float): Social discount rate as decimal.

    Raises:
        ValueError: If there is no graphical CPT.

    Returns:
        tuple:
        - aCPT (float): Analytical carbon payback time.
        - GWI_inst_released (dict): Dictionary with GHGs and 'total' as keys and yearly instantaneous GWI values (array) as values.
        - GWI_cum_released (dict): Array with cumulative GWI values.
        - GWI_inst_stored (dict): Dictionary with GHGs and 'total' as keys and yearly instantaneous GWI values (array) as values.
        - GWI_cum_stored (dict): Array with cumulative GWI values.
    """

    #show_or_save = show_or_save+"_aCPT_emit"
    GWI_inst_released, GWI_cum_released, disc_params_released = dynamic_lca.dynamic_GWI(g_flows=g_released, model_params=model_params, TH=TH, SDR=SDR)
    
    #show_or_save = show_or_save.replace("emit","stored")
    GWI_inst_stored, GWI_cum_stored, disc_params_stored = dynamic_lca.dynamic_GWI(g_flows=g_stored, model_params=model_params, TH=TH, SDR=SDR)


    if abs(GWI_cum_released[-1]) < abs(GWI_cum_stored[-1]):
        aCPT = lifetime * abs(GWI_cum_released)[-1] / abs(GWI_cum_stored)[-1]

        print(f"The analytically determined CPT is in year {aCPT}. \nLifetime emissions: {round(GWI_cum_released[-1],1)} ton CO2e. Lifetime storage: {round(GWI_cum_stored[-1],1)} ton CO2e.")

        return aCPT, GWI_inst_released, GWI_cum_released, disc_params_released, GWI_inst_stored, GWI_cum_stored, disc_params_stored
    
    else:
        raise ValueError("There is no analytical CPT.")



if __name__ == "__main__":

    filepath_xlsx = 'C:/Users/Sebastian/Documents/Coding projects/CPT_CCU/data/emission_flows_3.xlsx'
    filepath_yaml = 'C:/Users/Sebastian/Documents/Coding projects/CPT_CCU/data/model_parameters.yaml'

    model_params, g_construction, g_operation, g_raw_material_acquisition, g_decommissioning, g_prod_use_phase, \
        g_prod_EOL, g_stored, g_released, g_net = read_data.read_emission_flows_xlsx(filepath_xlsx, filepath_yaml)

    L = 50 #lifetime of plant
    TH = 100 #Impact modelling period
    SDR = 0.0 #Social discount rate

    gCPT, GWI_inst_net, GWI_cum_net, disc_params_net = graphical_CPT(g_flows=g_net, model_params=model_params, TH=TH, SDR=SDR)
    aCPT, GWI_inst_released, GWI_cum_released, disc_params_released, GWI_inst_stored, GWI_cum_stored, disc_params_stored = \
        analytical_CPT(g_released=g_released, g_stored=g_stored, model_params=model_params, L=L, TH=TH, SDR=SDR)