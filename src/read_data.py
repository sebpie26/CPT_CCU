import pandas as pd
import yaml



def read_emission_flows_xlsx(filepath_xlsx, filepath_yaml):
    """Read in of emission excel file and model parameter yaml

    Args:
        filepath_xlsx (str): location of emission excel file
        filepath_yaml (str): model parameter yaml

    Returns:
        tuple:
        - model_params (dict): Dictionary with parameters of the Bern model. model_params['Bern-model][...]
        - g_construction (dict): Dictionary with GHGs as keys and arrays of annual emission as values.
        - g_operation (dict): Dictionary with GHGs as keys and arrays of annual emission as values.
        - g_raw_material_acquisition (dict): Dictionary with GHGs as keys and arrays of annual emission as values.
        - g_decommissioning (dict): Dictionary with GHGs as keys and arrays of annual emission as values.
        - g_prod_use_phase (dict): Dictionary with GHGs as keys and arrays of annual emission as values.
        - g_prod_EOL (dict): Dictionary with GHGs as keys and arrays of annual emission as values.
        - g_stored (dict): Dictionary with GHGs as keys and arrays of annual emission as values.
        - g_released (dict): Dictionary with GHGs as keys and arrays of annual emission as values.
        - g_net (dict): Dictionary with GHGs as keys and arrays of annual emission as values.
    """


    with open(filepath_yaml, 'r') as file:
        model_params = yaml.safe_load(file)

    df = pd.read_excel(filepath_xlsx)

    GHG_list = ['CO2', 'CH4', 'N2O']

    g_construction, g_operation, g_raw_material_acquisition, g_decommissioning, g_prod_use_phase, g_prod_EOL, g_stored, g_released, g_net = {}, {}, {}, {}, {}, {}, {}, {}, {}

    for GHG in GHG_list:
        g_construction.update({f'{GHG}': df[f'{GHG}_construction']})
        g_operation.update({f'{GHG}': df[f'{GHG}_operation']})
        g_raw_material_acquisition.update({f'{GHG}': df[f'{GHG}_raw_material_acquisition']})
        g_decommissioning.update({f'{GHG}': df[f'{GHG}_decommissioning']})
        g_prod_use_phase.update({f'{GHG}': df[f'{GHG}_prod_use_phase']})
        g_prod_EOL.update({f'{GHG}': df[f'{GHG}_prod_EOL']})
        g_stored.update({f'{GHG}': df[f'{GHG}_stored']})
        g_released.update({f'{GHG}': [sum(values) for values in zip(g_construction[f'{GHG}'], g_operation[f'{GHG}'],g_raw_material_acquisition[f'{GHG}'],
                                                               g_decommissioning[f'{GHG}'], g_prod_use_phase[f'{GHG}'], g_prod_EOL[f'{GHG}'])]})
        g_net.update({f'{GHG}': [sum(values) for values in zip(g_released[f'{GHG}'], g_stored[f'{GHG}'])]})


    return model_params, g_construction, g_operation, g_raw_material_acquisition, g_decommissioning, g_prod_use_phase, g_prod_EOL, g_stored, g_released, g_net



if __name__ == "__main__":
    
    filepath_xlsx = 'C:/Users/Sebastian/Documents/VSC Workspace/Individual project Industrial ecology/data/emission_flows_2.xlsx'
    filepath_yaml = 'C:/Users/Sebastian/Documents/VSC Workspace/Individual project Industrial ecology/data/model_parameters.yaml'

    model_params, g_construction, g_operation, g_raw_material_acquisition, g_decommissioning, g_prod_use_phase, \
        g_prod_EOL, g_stored, g_released, g_net = read_emission_flows_xlsx(filepath_xlsx, filepath_yaml)

    g_list = [g_construction, g_operation, g_raw_material_acquisition, g_decommissioning, g_prod_use_phase, g_prod_EOL, g_stored, g_released, g_net]

    print(model_params)
    for key in ["CO2", "CH4", "N2O"]:
        for g_flow in g_list:
            print(len(g_flow[key]))