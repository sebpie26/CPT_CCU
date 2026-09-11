import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import math as m

def conceptual_cGWI_trajectory(y_values, no_points, CPT, iCPT):

    x = np.arange(no_points)

    fig, ax = plt.subplots(figsize=(8, 4))

    ax.spines['top'].set_color('none')
    ax.spines['right'].set_color('none')
    ax.spines['left'].set_position('zero')
    ax.spines['bottom'].set_position('zero')
    ax.plot(1, 0, ">k", transform=ax.get_yaxis_transform(), clip_on=False)
    ax.plot(0, 1, "^k", transform=ax.get_xaxis_transform(), clip_on=False)


    ax.grid(True, linestyle='--', linewidth=0.5, color='gray')
    ax.set_xlim(0, 49)
    ax.set_ylim(-60, 110)


    labels = ax.get_xticklabels()
    for label in labels:
        if label.get_text() == '0':
            label.set_visible(False)


    ax.plot(x, y_values, color='red', linewidth=2)
    ax.plot(CPT, 0, '*', label='CPT', color='blue')
    if iCPT:
        ax.plot(iCPT, 0, '*', label='inverted CPT', color='blue')


    ax.set_xlabel('Time [years]', loc='right')
    ax.set_ylabel('GWI [ton CO2e]', loc='top', rotation=0)


    plt.legend()
    plt.tight_layout()
    plt.show()


def ton_year_theory():

    fig, ax = plt.subplots(2,1,figsize=(8, 4))
    
    ax[0].spines['top'].set_color('none')
    ax[0].spines['right'].set_color('none')
    ax[0].spines['left'].set_position('zero')
    ax[0].spines['bottom'].set_position('zero')
    ax[0].plot(1, 0, ">k", transform=ax[0].get_yaxis_transform(), clip_on=False)
    ax[0].plot(0, 1, "^k", transform=ax[0].get_xaxis_transform(), clip_on=False)


    ax[0].grid(True, linestyle='--', linewidth=0.5, color='gray')
    ax[0].set_xlim(0, 150)
    ax[0].set_ylim(-1.05, 1.05)


    labels = ax[0].get_xticklabels()
    for label in labels:
        if label.get_text() == '0':
            label.set_visible(False)


    def atmo_load_CO2(t):
        ### Parameters
        # Should be moved to a yaml file at one point
        # Radiative forcing per unit mass (W/m²/ton GHG)
        r_CO2 = 1.704871e-12
        r_CH4 = 1.364641e-10
        r_N2O = 4.101665e-10

        # Atmospheric lifetimes (years)
        tau_CO2_1, tau_CO2_2, tau_CO2_3 = 394.4, 36.54, 4.304
        tau_CH4 = 11.8
        tau_N2O = 109

        # Bern model weights for CO2 (dimensionless)
        a_CO2_0, a_CO2_1, a_CO2_2, a_CO2_3 = 0.2173, 0.2240, 0.2824, 0.2763
        return a_CO2_0 + a_CO2_1*np.exp(-t/tau_CO2_1) + a_CO2_2*np.exp(-t/tau_CO2_2) + a_CO2_3*np.exp(-t/tau_CO2_3)

    no_points = 100
    y_atmo_load = np.concatenate(([1],[atmo_load_CO2(t) for t in range(1, no_points+1)]))
    x_atmo_load = np.arange(no_points+1)

    ax[0].plot(x_atmo_load, y_atmo_load, color='red', linewidth=2)
    ax[0].fill_between(x_atmo_load, y_atmo_load, color='salmon')

    equivalence_time = sum(y_atmo_load)
    ax[0].hlines(-1, 0, 60, color='blue', linewidth=2)
    ax[0].fill_between([0,60],[-1,-1],color='lightblue',label='Benefit of storing')

    ax[0].vlines(0,0,y_atmo_load[0], color='red')
    ax[0].vlines(100,0,y_atmo_load[-1], color='red')
    ax[0].vlines(0,0,-1,color='blue')
    ax[0].vlines(equivalence_time,0,-1,color='black',label='Equivalence time',linestyles='dashed')
    ax[0].vlines(60,0,-1,color='blue')

    ax[0].set_xlabel('Time [years]', loc='right')
    ax[0].set_ylabel('Moura Costa method', loc='top', rotation=0)
    ax[0].legend()


    ax[1].spines['top'].set_color('none')
    ax[1].spines['right'].set_color('none')
    ax[1].spines['left'].set_position('zero')
    ax[1].spines['bottom'].set_position('zero')
    ax[1].plot(1, 0, ">k", transform=ax[1].get_yaxis_transform(), clip_on=False)
    ax[1].plot(0, 1, "^k", transform=ax[1].get_xaxis_transform(), clip_on=False)


    ax[1].grid(True, linestyle='--', linewidth=0.5, color='gray')
    ax[1].set_xlim(0, 150)
    ax[1].set_ylim(0, 1.05)

    ax[1].plot(x_atmo_load, y_atmo_load, color='red', linewidth=2)
    ax[1].fill_between(x_atmo_load, y_atmo_load, color='salmon')
    year_stored = 30
    x_atmo_load_stored  = np.arange(year_stored,no_points+year_stored+1)
    ax[1].plot(x_atmo_load_stored, y_atmo_load, color='blue', linewidth=2)
    x_stored_fill = np.arange(no_points,no_points+year_stored+1)
    ax[1].fill_between(x_stored_fill, y_atmo_load[-year_stored-1:], color='lightblue',label='Benefit of storing')

    ax[1].vlines(0,0,y_atmo_load[0], color='red')
    ax[1].vlines(100,0,y_atmo_load[-1], color='red')
    ax[1].vlines(year_stored,0,y_atmo_load[0],color='blue')
    ax[1].vlines(100,0,y_atmo_load[-year_stored-1],color='black',linestyles='dashed',label='Cutting off the impact')
    ax[1].vlines(100+year_stored,0,y_atmo_load[100],color='blue')

    ax[1].set_xlabel('Time [years]', loc='right')
    ax[1].set_ylabel('Lashof method', loc='top', rotation=0)
    ax[1].legend()



    plt.tight_layout()
    plt.show()


if __name__ == "__main__":

    no_points = 50
    y_values1 = [-0.1*(i-0.1)**(2)+100 for i in range(no_points)]
    CPT1 = m.sqrt(1000)+0.1

    #conceptual_cGWI_trajectory(y_values=y_values1, no_points=no_points, CPT=CPT1, iCPT=None)


    y_values2 = [(x-15)*(x-40)*(11*x+120)/(1440) for x in range(no_points)]
    CPT2 = 15
    iCPT = 40

    #conceptual_cGWI_trajectory(y_values=y_values2, no_points=no_points, CPT=CPT2, iCPT=iCPT)

    ton_year_theory()
