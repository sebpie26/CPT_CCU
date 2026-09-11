import math as m
from collections import defaultdict
import time
import os
import pickle

import calc_CPT
import read_data
import dynamic_lca
from excel_export import write_results_to_excel
import plot_report_figures

def nested_dict():
    return defaultdict(nested_dict)


def SA_CPT(model_params, g_construction, g_operation, g_raw_material_acquisition, g_decommissioning, g_prod_use_phase, \
        g_prod_EOL, g_stored, g_released, g_net, lifetime, TH_list, SDR_list, save_path, show_or_save):

        
    gCPT_dict, aCPT_dict, GWI_data_dict, extm_vals_dict = defaultdict(dict), defaultdict(dict), nested_dict(), nested_dict()
    g_dict = {'construction': g_construction, 'operation': g_operation, 'raw_material_acquisition': g_raw_material_acquisition, \
              'decommissioning': g_decommissioning, 'prod_use_phase': g_prod_use_phase, 'prod_EOL': g_prod_EOL, 'stored': g_stored, \
                'released': g_released, 'net': g_net}


    for th in TH_list:
        print(f"\nImpact modelling period of {th} years.")

        for sdr in SDR_list:
            print(f"\nSocial Discount Rate of {sdr*100}%.")


            #Determine gCPT and aCPT and write them into return dict
            gCPT, GWI_inst_net, GWI_cum_net, disc_params_net = calc_CPT.graphical_CPT(g_net=g_net, model_params=model_params, TH=th, SDR=sdr)
            aCPT, GWI_inst_released, GWI_cum_released, disc_params_released, GWI_inst_stored, GWI_cum_stored, disc_params_stored = \
                calc_CPT.analytical_CPT(g_released=g_released, g_stored=g_stored, model_params=model_params, lifetime=lifetime, TH=th, SDR=sdr)

            gCPT_dict[f'TH_{th}'].update({f'SDR_{sdr}': {'gCPT': gCPT, 'lb_GWI': GWI_cum_net[m.floor(gCPT)], 'ub_GWI': GWI_cum_net[m.ceil(gCPT)]}})
            aCPT_dict[f'TH_{th}'].update({f'SDR_{sdr}': {'aCPT': aCPT, 'E_lifetime': GWI_cum_released[-1], 'S_lifetime': GWI_cum_stored[-1]}})


            #Helpers for the writing of data in return dicts through loops
            g_names = ['net', 'released', 'stored']
            ghg_list = ['CO2', 'CH4', 'N2O']
            disc_params_list = [disc_params_net, disc_params_released, disc_params_stored]
            GWI_pair_list = [[GWI_inst_net, GWI_cum_net], [GWI_inst_released, GWI_cum_released], [GWI_inst_stored, GWI_cum_stored]]


            # Writing of 'net', 'released', 'stored' separately as they are already calculated
            for i, j, k in zip(g_names, disc_params_list, GWI_pair_list):
                GWI_data_dict[i][f'TH_{th}'][f'SDR_{sdr}'] = {'GWI_inst': k[0], 'GWI_cum': k[1]}
                extm_vals_dict[i][f'TH_{th}'][f'SDR_{sdr}'] = j[f'TH_{th}'][f'SDR_{sdr}']

            GWI_pair_list_non_zero = [[{ghg: [x for x in GWI_inst_net[ghg] if x!= 0] for ghg in ghg_list}, GWI_cum_net], \
                                          [{ghg: [x for x in GWI_inst_released[ghg] if x!= 0] for ghg in ghg_list}, GWI_cum_released], \
                                           [{ghg: [x for x in GWI_inst_stored[ghg] if x!= 0] for ghg in ghg_list}, GWI_cum_stored]]
            
            for i, j in zip(g_names, GWI_pair_list_non_zero):
                for ghg in ghg_list:
                    if len(j[0][ghg]) > 0:
                        extm_vals_dict[i][f'TH_{th}'][f'SDR_{sdr}'][ghg].update({'min_inst_GWI': min(j[0][ghg]), 'max_inst_GWI': max(j[0][ghg])})
                    else:
                        extm_vals_dict[i][f'TH_{th}'][f'SDR_{sdr}'][ghg].update({'min_inst_GWI': 0, 'max_inst_GWI': 0})
                extm_vals_dict[i][f'TH_{th}'][f'SDR_{sdr}']['cum_GWI'] = {'min_cum_GWI': min(j[1]), 'max_cum_GWI': max(j[1]), 'final_cum_GWI': j[1][-1]}


            # Calculation and writing of flow and GWI data of 'construction', 'operation', 'raw_material_acquisition', 'decommissioning', 'prod_use_phase', 'prod_EOL'
            for i, g_flows in g_dict.items():
                if not GWI_data_dict[i][f'TH_{th}'][f'SDR_{sdr}']:
                    GWI_inst_return, GWI_cum_return, disc_params = dynamic_lca.dynamic_GWI(g_flows=g_flows, model_params=model_params, TH=th, SDR=sdr)
                    GWI_data_dict[i][f'TH_{th}'][f'SDR_{sdr}'] = {'GWI_inst': GWI_inst_return, 'GWI_cum': GWI_cum_return}
                    extm_vals_dict[i][f'TH_{th}'][f'SDR_{sdr}'] = disc_params[f'TH_{th}'][f'SDR_{sdr}']

                    for ghg in ghg_list:
                        GWI_inst_non_0 = [x for x in GWI_inst_return[ghg] if x!= 0]
                        if len(GWI_inst_non_0) > 0:
                            extm_vals_dict[i][f'TH_{th}'][f'SDR_{sdr}'][ghg].update({'min_inst_GWI': min(GWI_inst_non_0), 'max_inst_GWI': max(GWI_inst_non_0)})
                        else:
                            extm_vals_dict[i][f'TH_{th}'][f'SDR_{sdr}'][ghg].update({'min_inst_GWI': 0, 'max_inst_GWI': 0})
                    extm_vals_dict[i][f'TH_{th}'][f'SDR_{sdr}']['cum_GWI'] = {'min_cum_GWI': min(GWI_cum_return), 'max_cum_GWI': max(GWI_cum_return), 'final_cum_GWI': GWI_cum_return[-1]}


    return gCPT_dict, aCPT_dict, GWI_data_dict, extm_vals_dict, g_dict


def save_and_plot_resutls(g_dict, gCPT_dict, aCPT_dict, GWI_data_dict, extm_vals_dict, SDR_list, TH_list, save_path, show_or_save):

    ### comment out from here if a pickle file is read for testing of plots and excel
    pkl_data = (g_dict, gCPT_dict, aCPT_dict, GWI_data_dict, extm_vals_dict, SDR_list, TH_list, save_path, show_or_save)
    pkl_save_path = save_path+'SA_CPT.pkl'
    
    with open(pkl_save_path, 'wb') as file:
        pickle.dump(pkl_data, file)

    
    xlsx_path = write_results_to_excel(gCPT_dict=gCPT_dict, aCPT_dict=aCPT_dict, GWI_data_dict=GWI_data_dict, extm_vals_dict=extm_vals_dict, g_dict=g_dict, 
                                       TH_list=TH_list, SDR_list=SDR_list, save_path=save_path)


    if show_or_save != None:
        plot_report_figures.plot_all_for_main(g_dict, gCPT_dict, aCPT_dict, GWI_data_dict, extm_vals_dict, SDR_list, TH_list, save_path, show_or_save)
        for data_flag in ['net', 'released', 'stored']:
            plot_report_figures.plot_SA_CPT_results(GWI_data_dict[data_flag], data_flag, SDR_list, TH_list, save_path, show_or_save)


if __name__ == "__main__":

    filepath_xlsx = 'C:/Users/Sebastian/Documents/Coding projects/CPT_CCU/data/emission_flows_3.xlsx'
    filepath_yaml = 'C:/Users/Sebastian/Documents/Coding projects/CPT_CCU/data/model_parameters.yaml'

    model_params, g_construction, g_operation, g_raw_material_acquisition, g_decommissioning, g_prod_use_phase, \
        g_prod_EOL, g_stored, g_released, g_net = read_data.read_emission_flows_xlsx(filepath_xlsx, filepath_yaml)


    lifetime = 50 #Lifetime of plant
    TH_list = [100, 500] #List of impact modelling periods
    SDR_list = [-0.03, -0.01, 0.0, 0.01, 0.03, 0.09] #List of social discount rates

    show_or_save = 'save' # None, 'show', 'save'; Flag for not creating, showing, or saving plots. 
    save_path = f"C:/Users/Sebastian/Documents/Coding projects/CPT_CCU/results/{int(time.time())}/"
    os.makedirs(save_path)


    gCPT_dict, aCPT_dict, GWI_data_dict, extm_vals_dict, g_dict = \
        SA_CPT(model_params=model_params, g_construction=g_construction, g_operation=g_operation, g_raw_material_acquisition=g_raw_material_acquisition, \
               g_decommissioning=g_decommissioning, g_prod_use_phase=g_prod_use_phase, g_prod_EOL=g_prod_EOL, g_stored=g_stored, g_released=g_released, \
                g_net=g_net, lifetime=lifetime, TH_list=TH_list, SDR_list=SDR_list, save_path=save_path, show_or_save=show_or_save)


    # Remove commenting for testing of plots and excel. Therefore, comment out from lifetime = 50 to the line above this comment. 
    """g_dict = {'construction': g_construction, 'operation': g_operation, 'raw_material_acquisition': g_raw_material_acquisition, \
              'decommissioning': g_decommissioning, 'prod_use_phase': g_prod_use_phase, 'prod_EOL': g_prod_EOL, 'stored': g_stored, \
                'released': g_released, 'net': g_net}
    
    pkl_save_path = 'C:/Users/Sebastian/Documents/Coding projects/CPT_CCU/results/1787236990/SA_CPT.pkl'
    with open(pkl_save_path, 'rb') as file:
        (g_dict, gCPT_dict, aCPT_dict, GWI_data_dict, extm_vals_dict, SDR_list, TH_list, save_path, show_or_save) = pickle.load(file) #New: (g_dict, gCPT_dict, aCPT_dict, GWI_data_dict, extm_vals_dict, SDR_list, TH_list, save_path, show_or_save) #Old: (g_released, g_stored, g_net, SDR_list, TH_list, extm_vals_dict, GWI_data_dict, gCPT_dict, aCPT_dict)

    save_path = 'C:/Users/Sebastian/Documents/Coding projects/CPT_CCU/results/1787236990/'
    show_or_save = 'save'"""

    save_and_plot_resutls(g_dict, gCPT_dict, aCPT_dict, GWI_data_dict, extm_vals_dict, SDR_list, TH_list, save_path, show_or_save)