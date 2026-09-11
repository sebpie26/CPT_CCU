import numpy as np
import scipy.integrate as integrate
import pandas as pd
import matplotlib.pyplot as plt


### Parameters
# Should be moved to a yaml file at one point
# Radiative forcing per unit mass (W/m² per kg GHG)
r_CO2 = 1.704871e-15
r_CH4 = 1.364641e-13
r_N2O = 4.101665e-13

# Atmospheric lifetimes (years)
tau_CO2_1, tau_CO2_2, tau_CO2_3 = 394.4, 36.54, 4.304
tau_CH4 = 11.8
tau_N2O = 109

# Bern model weights for CO2 (dimensionless)
a_CO2_0, a_CO2_1, a_CO2_2, a_CO2_3 = 0.2173, 0.2240, 0.2824, 0.2763


def atmo_load_CO2(T):
    return a_CO2_0 + a_CO2_1*np.exp(-T/tau_CO2_1) + a_CO2_2*np.exp(-T/tau_CO2_2) + a_CO2_3*np.exp(-T/tau_CO2_3)

def atmo_load_CH4(T):
    return np.exp(-T/tau_CH4)

def atmo_load_N2O(T):
    return np.exp(-T/tau_N2O)

def GWP(gas, T):
        """
        This function returns the global warming potential for a given gas over a specified analytical horizon.

        Args:
            gas (str): The greenhouse gas ('CO2', 'CH4', or 'N2O')
            T (float): The analytical horizon in years
        """

        if gas == 'CH4':
            return r_CH4 * integrate.quad(atmo_load_CH4, 0, T)[0] / (r_CO2 * integrate.quad(atmo_load_CO2, 0, T)[0])
        elif gas == 'N2O':
            return r_N2O * integrate.quad(atmo_load_N2O, 0, T)[0] / (r_CO2 * integrate.quad(atmo_load_CO2, 0, T)[0])
        else:
            raise ValueError("Invalid gas type. Choose from 'CH4' or 'N2O'.")


def moura_costa_method(AH, CO2_flows, CH4_flows, N2O_flows, CO2_storage, plot=False):
    
    """
    Calculates the CO2 equivalent emissions using the Moura-Costa method.

    Args:
        AH (int): Analytical horizon in years
        CO2_flows (array): CO2 emitted in year 0, 1, 2, ...
        CH4_flows (array): CH4 emitted in year 0, 1, 2, ...
        N2O_flows (array): N2O emitted in year 0, 1, 2, ...
        CO2_storage (dict): Dictionary with keys as storage duration (years) and values as CO2 stored
    
    Returns:
        tuple:
            - CO2e_sum (float): Total CO2 equivalent emissions
            - CO2_storage_impact (list): List of CO2 storage impacts for each storage duration
            - t_eq (float): Equivalence time for CO2 at the given analytical horizon
    """

    def equivalence_time_factor(T):
        """
        This function calculates the equivalence time for storing one 

        Args:
            T (float): Analytical horizon (years)
        Returns:
            tuple:
            - t_eq (float): Equivalence time for CO2 (years)
            - f_eq (float): Equivalence factor (impact on climate change of one unit of mass CO2 per year stored)
        """
        t_eq = integrate.quad(atmo_load_CO2, 0, T)[0]

        return t_eq, -1/t_eq
    

    t_eq, f_eq = equivalence_time_factor(AH)
    CO2_storage_impact = np.sum([CO2_storage[i] * i * f_eq for i in CO2_storage.keys()])
    CO2e_sum = np.sum(CO2_flows) + np.sum(CH4_flows)*GWP('CH4', AH) + np.sum(N2O_flows)*GWP('N2O', AH) + CO2_storage_impact

    return CO2e_sum, CO2_storage_impact, t_eq

def lashof_method(AH, CO2_flows, CH4_flows, N2O_flows, CO2_storage, plot=False):
    """
    Calculates the CO2 equivalent emissions using the Lashof method.

    Args:
        AH (int): Analytical horizon in years
        CO2_flows (array): CO2 emitted in year 0, 1, 2, ...
        CH4_flows (array): CH4 emitted in year 0, 1, 2, ...
        N2O_flows (array): N2O emitted in year 0, 1, 2, ...
        CO2_storage (dict): Dictionary with keys as storage duration (years) and values as CO2 stored
    
    Returns:
        tuple:
            - CO2e_sum (float): Total CO2 equivalent emissions
            - CO2_storage_impact (list): List of CO2 storage impacts for each storage duration
            - t_eq (float): Equivalence time for CO2 at the given analytical horizon
    """

    reference_RF = integrate.quad(atmo_load_CO2, 0, AH)[0]
    params = [integrate.quad(atmo_load_CO2, 0, AH-i)[0] /reference_RF for i in CO2_storage.keys()]
    CO2_storage_impact = np.sum([CO2_storage[i] * integrate.quad(atmo_load_CO2, 0, AH-i)[0] /reference_RF for i in CO2_storage.keys()])
    CO2e_sum = np.sum(CO2_flows) + np.sum(CH4_flows)*GWP('CH4', AH) + np.sum(N2O_flows)*GWP('N2O', AH) + CO2_storage_impact

    return CO2e_sum, CO2_storage_impact




if __name__ == "__main__":
    # Example usage
    AH = 100  # Analytical horizon in years
    CO2_flows = np.array([1000, 2000, 1500])  # Example CO2 emissions
    CH4_flows = np.array([5, 7, 6])      # Example CH4 emissions
    N2O_flows = np.array([2, 3, 2])      # Example N2O emissions
    CO2_storage = {10: 1000, 20: 2000, 30: 1500}  # Example CO2 storage for different durations

    CO2e_sum_moura, CO2_storage_impact_moura, t_eq = moura_costa_method(AH, CO2_flows, CH4_flows, N2O_flows, CO2_storage)
    CO2e_sum_lashof, CO2_storage_impact_lashof = lashof_method(AH, CO2_flows, CH4_flows, N2O_flows, CO2_storage)

    print(f"Total CO2e sum: {CO2e_sum_moura, CO2e_sum_lashof}")
    print(f"CO2 storage impact: {CO2_storage_impact_moura, CO2_storage_impact_lashof}")
    print(f"Equivalence time for CO2 at {AH} years: {t_eq}")

