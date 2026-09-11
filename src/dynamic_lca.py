import numpy as np
import scipy.integrate as integrate
import time
import os


import read_data
import plot_report_figures



def atmo_load_BM(t, ghg, model_params):
    param = model_params["Bern-model"]
    if ghg == "CO2":
        return param['a_0_CO2'] + param['a_1_CO2']*np.exp(-t/param['tau_1_CO2']) \
            + param['a_2_CO2']*np.exp(-t/param['tau_2_CO2']) + param['a_3_CO2']*np.exp(-t/param['tau_3_CO2'])

    elif ghg == "CH4":
        return np.exp(-t/param['tau_CH4'])

    elif ghg == "N2O":
        return np.exp(-t/param['tau_N2O'])

    else:
        raise ValueError(f"Greenhouse gas {ghg} is not implemented in Bern-model. Available GHGs are CO2, CH4, N2O.")


def AGWP_CO2(T, model_params):
    return model_params['Bern-model']['r_CO2'] * integrate.quad(atmo_load_BM, 0, T, args=("CO2", model_params))[0]


def dynamic_GWI(g_flows, model_params, TH, SDR, save_path=None, show_or_save=None):
    """Function calculates the instantaneous and cumulative GWI with the dynamic LCA approach. Results can be plotted through a flag.

    Args:
        g_flows (dict): Dictionary with GHGs as keys and arrays of yearly emission as values.
        model_params (dict): Dictionary with parameters of the Bern model. model_params['Bern-model][...]
        TH (int): Impact modelling period in years.
        SDR (float): Social discount rate as decimal.
        save_path (str): Location to save the plot.
        show_or_save (str): Flag whether 'show' or 'save' graph. Default None means no plot.

    Returns:
        tuple:
            - GWI_inst_return (dict): Dictionary with GHGs and 'total as keys and arrays of yearly instantaneous GWI (ton CO2e) as values.
            - GWI_cum_return (dict): Dictionary with GHGs and 'total as keys and arrays of yearly cumulative GWI (ton CO2e) as values.
    """


    
    CO2_flows = g_flows["CO2"]
    CH4_flows = g_flows["CH4"]
    N2O_flows = g_flows["N2O"]


    # TH can exceed the emission period and GHG flows are therefore extended with zeros
    # The TH (impact modeling period) can currently be not shorter than the analytical horizon.
    if TH < any([len(CO2_flows), len(CH4_flows), len(N2O_flows)]):
        raise ValueError("The TH (impact modeling period) must be longer than or equal to the the analytical horizon (years of emission).")
    CO2_flows = np.concatenate([CO2_flows, np.zeros(TH - len(CO2_flows))])
    CH4_flows = np.concatenate([CH4_flows, np.zeros(TH - len(CH4_flows))])
    N2O_flows = np.concatenate([N2O_flows, np.zeros(TH - len(N2O_flows))])

    # Social discounting of emission flows
    disc_params = {f'TH_{TH}': {f'SDR_{SDR}': {}}}
    for i in range(TH):
        temp_weight = 1/(1+SDR)**i
        CO2_flows[i] = CO2_flows[i]*temp_weight
        CH4_flows[i] = CH4_flows[i]*temp_weight
        N2O_flows[i] = N2O_flows[i]*temp_weight

    GHG_non_0 = [[x for x in CO2_flows if x != 0], [x for x in CH4_flows if x != 0], [x for x in N2O_flows if x != 0]]
    for GHG, j in zip(['CO2', 'CH4', 'N2O'], GHG_non_0):
        if len(j) > 0:
            disc_params[f'TH_{TH}'][f'SDR_{SDR}'].update({f'{GHG}': {'min_flow': min(j), 'max_flow': max(j), 'NPV_flow': sum(j)}})
        else:
            disc_params[f'TH_{TH}'][f'SDR_{SDR}'].update({f'{GHG}': {'min_flow': 0, 'max_flow': 0, 'NPV_flow': 0}})

    # Calculation of the instantaneous GWI for each year t = 1..TH, summing the contributions of all previous years tau = 0..t-1
    GWI_inst = {'CO2': [], 'CH4': [], 'N2O': [], 'total': []}
    for t in range(1, TH + 1):
        total_CO2 = 0.0
        total_CH4 = 0.0
        total_N2O = 0.0
        for tau in range(t):
            total_CO2 += CO2_flows[tau] * model_params['Bern-model']['r_CO2'] * integrate.quad(atmo_load_BM, t-tau-1, t-tau, args=("CO2", model_params))[0]
            total_CH4 += CH4_flows[tau] * model_params['Bern-model']['r_CH4'] * integrate.quad(atmo_load_BM, t-tau-1, t-tau, args=("CH4", model_params))[0]
            total_N2O += N2O_flows[tau] * model_params['Bern-model']['r_N2O'] * integrate.quad(atmo_load_BM, t-tau-1, t-tau, args=("N2O", model_params))[0]
        
        GWI_inst['CO2'].append(total_CO2)
        GWI_inst['CH4'].append(total_CH4)
        GWI_inst['N2O'].append(total_N2O)
        GWI_inst['total'].append(total_CO2 + total_CH4 + total_N2O)


    # Cumulative global warming impact is the running sum of the instantaneous GWI contributions. [W/m²]
    GWI_cum = np.cumsum(GWI_inst['total'])

    # Calculate the reference AGWP of 1 kg CO2 at each horizon T = 1..TH. [W/m²/ton CO2e]
    AGWP_ref = np.array([AGWP_CO2(T, model_params) for T in range(1, TH + 1)])

    GWI_inst_return = {i : GWI_inst[i]/AGWP_ref for i in GWI_inst.keys()}   #Unit: ton CO2e
    GWI_cum_return = GWI_cum / AGWP_ref                                     #Unit: ton CO2e


    if show_or_save != None:
        g_flows = {"CO2": CO2_flows, "CH4": CH4_flows, "N2O": N2O_flows}
        plot_report_figures.plot_GWP_GHG(GWI_inst_return, GWI_cum_return, AGWP_ref, g_flows, TH, SDR, save_path, show_or_save)


    return GWI_inst_return, GWI_cum_return, disc_params


def print_min_max_values(GWI_inst_return, GWI_cum_return, SDR):


    GWI_inst_return.update({'cum': GWI_cum_return})

    print_dict = {}
    GHG_list = ['CO2', 'CH4', 'N2O', 'cum']


    print_dict.update({SDR: {}})
    for GHG in GHG_list:
        for i, j in enumerate(GWI_inst_return[GHG]):
            if i == 0:
                print_dict[SDR].update({GHG: [[i+1,j], [i+1,j]]})
            else:
                if j != 0:
                    if j < print_dict[SDR][GHG][0][1]: print_dict[SDR][GHG][0] = [i+1,j]
                    if j > print_dict[SDR][GHG][1][1]: print_dict[SDR][GHG][1] = [i+1,j]


    for GHG in GHG_list:
        print(f"{SDR}; {GHG}; Min: {print_dict[SDR][GHG][0]}; Max: {print_dict[SDR][GHG][1]}")


if __name__ == "__main__":

    filepath_xlsx = 'C:/Users/Sebastian/Documents/Coding projects/CPT_CCU/data/emission_flows_3.xlsx'
    filepath_yaml = 'C:/Users/Sebastian/Documents/Coding projects/CPT_CCU/data/model_parameters.yaml'

    model_params, g_construction, g_operation, g_raw_material_acquisition, g_decommissioning, g_prod_use_phase, \
        g_prod_EOL, g_stored, g_released, g_net = read_data.read_emission_flows_xlsx(filepath_xlsx, filepath_yaml)

    TH = 100
    SDR = 0
    show_or_save = None #show, save, None
    if show_or_save == 'save':
        save_path = f"C:/Users/Sebastian/Documents/Coding projects/CPT_CCU/results/{int(time.time())}/"
        os.makedirs(save_path)
    else:
        save_path = None

    GWI_inst_return, GWI_cum_return, disc_params = dynamic_GWI(g_flows=g_net, model_params=model_params, TH=TH, SDR=SDR, save_path=save_path, show_or_save=show_or_save)

    #print_min_max_values(GWI_inst_return, GWI_cum_return, SDR)

    #print(f"\nFinal result at the {TH}-year analytical horizon: {GWI_cum_return[-1]}ton CO2e")