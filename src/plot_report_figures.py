import numpy as np
from collections import defaultdict
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
from matplotlib.legend_handler import HandlerTuple
import math as m
import time
import os

import read_data
import dynamic_lca

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": "Calibri",
    "font.size": 11,
    "axes.titlesize": 12,
    "axes.titleweight": "bold",
    "axes.labelsize": 11,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "axes.grid": True,
    "grid.linestyle": "--",
    "grid.linewidth": 0.5,
    "grid.color": "gray",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
})

GHG_LIST = ["CO2", "CH4", "N2O"]
COLORS = {"CO2": "blue", "CH4": "purple", "N2O": "green", "cum": "red", "gCPT": "orange", "TH_100": "orangered", "TH_500": "red",
          "aCPT_100": "khaki", "aCPT_500": "darkkhaki", "E_lifetime_100": "orangered", "E_lifetime_500": "red", "S_lifetime_100": "yellowgreen", "S_lifetime_500": "olivedrab"}
COLORMAPS = {"CO2": cm.Blues, "CH4": cm.Purples, "N2O": cm.Greens, "cum": cm.Reds}
GHG_LABELS = {"CO2": "CO$_2$", "CH4": "CH$_4$", "N2O": "N$_2$O"}
#GRID_KW = dict(linestyle="--", linewidth=0.5, color="gray")


def _show_or_save(fig, filename, save_path=None, show_or_save=None):
    """Show, save or drop a figure - mirrors the existing plotting functions."""
    if 'show' in show_or_save:
        plt.show()
    elif 'save' in show_or_save:
        if not save_path:
            raise ValueError(f"save_path is required to save '{filename}'.")
        fig.savefig(save_path + filename)
    plt.close(fig)


def _colormap_coloring(colorkey, colorval=None, colorscale=[0,1]):
    if colorval == None or abs(colorval) > max(colorscale) + 0.4*(max(colorscale)-min(colorscale)):
        colorval = np.average(colorscale)
    norm = mcolors.Normalize(vmin=min(colorscale) - 0.4*(max(colorscale)-min(colorscale)), vmax=max(colorscale) + 0.4*(max(colorscale)-min(colorscale)))
    colourmap = COLORMAPS[f"{colorkey}"]
    return colourmap(norm(colorval))


def plot_all_for_main(g_dict, gCPT_dict, aCPT_dict, GWI_data_dict, extm_vals_dict, SDR_list, TH_list, save_path, show_or_save):

    #plot_ghg_flows(g_released=g_dict["released"], g_stored=g_dict["stored"], g_net=g_dict["net"], SDR_list=SDR_list, save_path=save_path, show_or_save=show_or_save)
    ##plot_ghg_shares(g_dict, SDR_list=SDR_list, save_path=save_path, show_or_save=show_or_save)
    plot_CGWI_stage_shares(GWI_data_dict, SDR_list, TH_list, save_path, show_or_save)
    #plot_CGWI_ghg_shares(GWI_data_dict, TH_list, save_path, show_or_save, sdr=0.0)
    #plot_distribution_g_flows(g_flows=g_dict["net"], SDR_list=SDR_list, save_path=save_path, show_or_save=show_or_save)
    #plot_npv(extm_vals_dict, SDR_list=SDR_list, save_path=save_path, show_or_save=show_or_save, TH=TH_list[-1], flow="net")
    #plot_distribution_GWI(GWI_data_dict, TH_list, SDR_list=SDR_list, save_path=save_path, show_or_save=show_or_save, flow='net')
    #plot_GWI_cum_final(extm_vals_dict, TH_list, SDR_list=SDR_list, save_path=save_path, show_or_save=show_or_save, flow='net')
    #plot_graphical_CPT(gCPT_dict=gCPT_dict, TH_list=TH_list, SDR_list=SDR_list, save_path=save_path, show_or_save=show_or_save)
    #plot_analytical_CPT(aCPT_dict, TH_list, SDR_list=SDR_list, save_path=save_path, show_or_save=show_or_save)
    #plot_distribution_of_CPTs(gCPT_dict, aCPT_dict, TH_list, SDR_list=SDR_list, save_path=save_path, show_or_save=show_or_save)


def plot_ghg_flows(g_released, g_stored, g_net, SDR_list, save_path, show_or_save):


    fig, axs = plt.subplots(3, 3, figsize=(15,9), squeeze=False)

    lenght = max([len(g_released[key]) for key in g_released.keys()]+[len(g_stored[key]) for key in g_stored.keys()]+[len(g_net[key]) for key in g_net.keys()])
    x_axs = range(1, lenght+1)
    grouped_handles = {i: [] for i in range(len(SDR_list))}
    
    g_flows = defaultdict(dict)
    g_flows.update({"released": {"0.0": g_released}, "stored": {"0.0": g_stored}, "net": {"0.0": g_net}})
    SDR_list_non_zero = [i for i in SDR_list if i != 0.0]
    title_addon = ["released", "stored", "net"]

    for i in title_addon:
        for sdr in SDR_list_non_zero:
            g_flows[i].update({f"{sdr}": {}})
            for ghg in GHG_LIST:
                emit_GHG = [g_flows[i]["0.0"][f"{ghg}"][j] / ((1 + sdr)**j) for j in range(len(g_flows[i]["0.0"][f"{ghg}"]))]
                g_flows[i][f"{sdr}"].update({f"{ghg}": emit_GHG})
                

    for i, ghg in enumerate(GHG_LIST):
        for j, dataset in enumerate(title_addon):
            ax = axs[i, j]
            for k, sdr in enumerate(SDR_list):
                colour = "black" if sdr==0.0 else _colormap_coloring(ghg, sdr, SDR_list) #colourmap(norm(sdr))
                line, = ax.plot(x_axs, g_flows[dataset][f"{sdr}"][f"{ghg}"], label=f"{sdr:.1%}", color=colour)

                if len(grouped_handles[k]) > 0:
                    if line.get_color() not in [grouped_handles[k][l].get_color() for l in range(len(grouped_handles[k]))]: 
                        grouped_handles[k].append(line)
                else:
                    grouped_handles[k].append(line)
            ax.ticklabel_format(axis='y', style='sci', scilimits=(-2,3))
            ax.yaxis.get_offset_text().set_fontsize(9)
            ax.set_xlabel('Time [years]')
            ax.set_ylabel('Flow [ton/year]')
            ax.set_title(f'Annual flow of {title_addon[j]} {GHG_LABELS[ghg]}')

    #fig.suptitle("Greenhouse gas flows", fontsize=16)
    fig.tight_layout()
    fig.subplots_adjust(bottom=0.15)

    fig.legend(
        [tuple(grouped_handles[i]) for i in range(len(SDR_list))], 
        [f"{sdr:.1%}" for sdr in SDR_list],
        loc='lower left', bbox_to_anchor=(0.03, 0.02),
        ncols=len(SDR_list),
        handler_map={tuple: HandlerTuple(ndivide=None)},
        handlelength=10.0,
        title="Social Discount Rates", title_fontsize=10)
    
    _show_or_save(fig, 'ghg_flows.png', save_path, show_or_save)


def plot_ghg_shares(g_dict, SDR_list, save_path, show_or_save):

    SDR_set = sorted(set([min(SDR_list), 0.0, max(SDR_list)]))
    rel_g_dict_keys = list(g_dict.keys())
    rel_g_dict_keys.remove("net")
    rel_g_dict_keys.remove("stored")

    fig, axs = plt.subplots(len(rel_g_dict_keys), len(SDR_set), figsize=(12,4.5*len(rel_g_dict_keys)), squeeze=False)

    for i, key in enumerate(rel_g_dict_keys):
        for j, ghg in enumerate(GHG_LIST):
            ax = axs[i,j]
            data = [sum(g_dict[key][ghg]) for ghg in GHG_LIST] #Undiscounted flows
            if set(data) == {0}:
                continue
            labels = [GHG_LABELS[ghg] for ghg in GHG_LIST]
            colors = [COLORS[ghg] for ghg in GHG_LIST]
            title_dict = {'construction': "Construction stage, ", 'operation':'Operation stage, ', 'raw_material_acquisition':"Raw material acquisition, ", \
                          'decommissioning': "Decommissioning stage, ", 'prod_use_phase': "Product use-phase, ", 'prod_EOL':"Product EOL, ", 'released':"Released "}
            ax.pie(data, labels=labels, colors=colors)
            ax.set_title(f"{title_dict[key]}{GHG_LABELS[ghg]}")

    fig.tight_layout()
    _show_or_save(fig, "plot_ghg_shares.png", save_path, show_or_save)


def plot_SA_CPT_results(GWI_results, data_flag, SDR_list, TH_list, save_path, show_or_save):
    

    fig, axs = plt.subplots(3, len(TH_list)+1, figsize=(15,9), squeeze=False)

    grouped_handles = {i: [] for i in range(len(SDR_list))}

    for i, ghg in enumerate(GHG_LIST):
        for j, th in enumerate(TH_list):
            x_axs = np.arange(1, th+1)
            ax = axs[i,j]
            for k, sdr in enumerate(SDR_list):
                colour = "black" if sdr==0.0 else _colormap_coloring(ghg, sdr, SDR_list) #colourmap(norm(sdr))
                line, = ax.plot(x_axs, GWI_results[f"TH_{th}"][f"SDR_{sdr}"]["GWI_inst"][f'{ghg}'], label=f'{sdr:.1%}', color=colour)
                if len(grouped_handles[k]) > 0:
                    if line.get_color() not in [grouped_handles[k][l].get_color() for l in range(len(grouped_handles[k]))]:
                        grouped_handles[k].append(line)
                else:
                    grouped_handles[k].append(line)

            ax.ticklabel_format(axis='y', style='sci', scilimits=(-2,3))
            ax.yaxis.get_offset_text().set_fontsize(9)
            ax.set_xlabel('Time [years]')
            ax.set_ylabel('GWI [ton CO2e]')
            ax.set_title(f'Inst GWI of {GHG_LABELS[ghg]}, TH: {th} years')
    
    for j, th in enumerate(TH_list):
        x_axs = np.arange(1, th+1)
        ax = axs[j, len(TH_list)]
        for k, sdr in enumerate(SDR_list):
            color = "black" if sdr==0.0 else _colormap_coloring("cum", sdr, SDR_list) #colourmap(norm(sdr))
            line, = ax.plot(x_axs, GWI_results[f"TH_{th}"][f"SDR_{sdr}"]["GWI_cum"], label=f'{sdr:.1%}', color=color)
            if line.get_color() not in [grouped_handles[k][l].get_color() for l in range(len(grouped_handles[k]))]:
                grouped_handles[k].append(line)

        ax.ticklabel_format(axis='y', style='sci', scilimits=(-2,3))
        ax.yaxis.get_offset_text().set_fontsize(9)
        ax.set_xlabel('Time [years]')
        ax.set_ylabel('GWI [ton CO2e]')
        ax.set_title(f'Cum GWI, TH: {th} years')

    axs[2,2].axis("off")
    axs[2,2].legend(
        [tuple(grouped_handles[i]) for i in range(len(SDR_list))], 
        [f"{SDR:.1%}" for SDR in SDR_list], 
        loc='upper left', 
        handler_map={tuple: HandlerTuple(ndivide=None)},
        handlelength=10.0,
        title="Social Discount Rates", title_fontsize=10)

    #fig.suptitle(f"Dynamic LCA results of {data_flag} emissions", fontsize=16)
    plt.tight_layout()

    _show_or_save(fig, f'dLCA_results_of_{data_flag}_emissions.png', save_path, show_or_save)


def plot_CGWI_stage_shares(GWI_data_dict, SDR_list, TH_list, save_path, show_or_save, sdr=0.0):

    rel_g_dict_keys = list(GWI_data_dict.keys())
    for i in ["net", "stored", "released", "raw_material_acquisition"]:
        rel_g_dict_keys.remove(i)
    label_dict = {'construction': "Construction phase", 'operation':'Operation phase', 'decommissioning': "Decommissioning phase",\
                        'prod_use_phase': "Product use-phase", 'prod_EOL':"Product EOL"}
    axs_labels = []
    for i in rel_g_dict_keys:
        axs_labels.append(label_dict[i])

    fig, axs = plt.subplots(1, len(TH_list), figsize=(12,4.5), squeeze=False)

    for i, th in enumerate(TH_list):
        ax = axs[0,i]
        data = [GWI_data_dict[key][f"TH_{th}"][f"SDR_{sdr}"]["GWI_cum"][-1] for key in rel_g_dict_keys]
        colors = ["blue", "green", "black", "red", "orange"]
         #'raw_material_acquisition':"Raw material acquisition, ", 
        ax.pie(data, labels=axs_labels, colors=colors, autopct='%1.2f%%')
        ax.set_title(f"TH: {th} years")

    fig.tight_layout()
    _show_or_save(fig, f"plot_CGWI_stage_shares_TH_{th}.png", save_path, show_or_save)


def plot_CGWI_ghg_shares(GWI_data_dict, TH_list, save_path, show_or_save, sdr=0.0):

    def autopct_filter(pct): return f'{pct:.1f}%' if pct > 3 else ''
    def label_position(x,y,label): 
        if label=="CH$_4$":
            return (1.2*np.sign(x), 1.5*y)
        else:
            return (1.2*np.sign(x), 1.2*y)

    fig, axs = plt.subplots(1, len(TH_list), figsize=(12,4.5), squeeze=False)

    for i, th in enumerate(TH_list):
        ax = axs[0,i]
        data = [abs(sum(sum(GWI_data_dict[key][f"TH_{th}"][f"SDR_{sdr}"]["GWI_inst"][ghg]) for key in GWI_data_dict.keys())) for ghg in GHG_LIST]
        labels = [GHG_LABELS[ghg] for ghg in GHG_LIST]
        colors = [COLORS[ghg] for ghg in GHG_LIST]

        wedges, texts, autotexts = ax.pie(data, autopct=autopct_filter, pctdistance=0.8, colors=colors, wedgeprops=dict(width=0.4)) # labels=labels, colors=colors, autopct=autopct_filter)

        for i, w in enumerate(wedges):
            ang = (w.theta2 - w.theta1)/2. + w.theta1
            y = np.sin(np.deg2rad(ang))
            x = np.cos(np.deg2rad(ang))
            ax.annotate(labels[i], xy=(x, y), xytext=label_position(x,y,labels[i]), arrowprops=dict(arrowstyle="-"), ha='center')


        ax.set_title(f"TH: {th} years")

    fig.tight_layout()
    _show_or_save(fig, "plot_CGWI_ghg_shares.png", save_path, show_or_save)


def plot_distribution_g_flows(g_flows, SDR_list, save_path, show_or_save):
    """Three panels (CO2 / CH4 / N2O), each with one violin per social discount rate.

    Args:
        g_net (dict): Dictionary with GHGs as keys and yearly net emission flows (array) as values.
        SDR_list (list): List of social discount rates in decimal numbers. Default: [0.09, 0.0, -0.03]
        save_path (str): Location to save the plot.
        show_or_save (str): Flag whether 'show' or 'save' graph.
    """

    def discount(flow, SDR):
        """Exopenential discounting: g_j / (1 + SDR)**j"""
        return flow / (1.0 + SDR) ** np.arange(len(flow))

    SDR_set = sorted(set([min(SDR_list), 0.0, max(SDR_list)]))
    fig, axs = plt.subplots(1, len(g_flows.keys()), figsize=(12,4.5), squeeze=False)

    for i, ghg in enumerate(g_flows.keys()):
        ax = axs[0,i]
        for k, sdr in enumerate(SDR_set):
            ax.violinplot(discount(g_flows[ghg], sdr), positions=[k+1], facecolor=_colormap_coloring(ghg, sdr, SDR_list), linecolor='black', widths=0.7, showmedians=True, showextrema=True)
            
        ax.ticklabel_format(axis='y', style='sci', scilimits=(-2,3))
        ax.yaxis.get_offset_text().set_fontsize(9)
        #ax.axhline(0.0, color="black", linewidth=0.8)
        ax.set_xticks(range(1, len(SDR_set) + 1))
        ax.set_xticklabels([f"{sdr:.1%}" for sdr in SDR_set])
        ax.set_xlabel("Social discount rate")
        ax.set_ylabel(f"Annual net flow of {GHG_LABELS[ghg]} [ton]")
        ax.set_title(f"Net {GHG_LABELS[ghg]} flow")

    #fig.suptitle("Distribution of discounted net GHG flows", fontsize=15)
    fig.tight_layout()
    _show_or_save(fig, "distribution_of_ghg_flows.png", save_path, show_or_save)


def plot_npv(extm_vals_dict, SDR_list, save_path, show_or_save, TH, flow="net"):
    """ Three panels (CO2 / CH4 / N2O) with the net present value of the flows per social discount rate."""

    fig, axs = plt.subplots(1, len(GHG_LIST), figsize=(12,4.5), squeeze=False)
    x = np.arange(len(SDR_list))

    for i, ghg in enumerate(['CO2', 'CH4', 'N2O']):

        ax = axs[0,i]
        data = [extm_vals_dict[flow][f'TH_{TH}'][f'SDR_{sdr}'][ghg]['NPV_flow'] for sdr in SDR_list]
        ax.bar(x, data, width=0.65, color=COLORS[ghg], edgecolor="black", linewidth=0.6)

        if ghg == 'CO2':
            ax.yaxis.set_inverted(True)
        ax.ticklabel_format(axis='y', style='sci', scilimits=(-2,3))
        ax.yaxis.get_offset_text().set_fontsize(9)
        #ax.axhline(0.0, color="black", linewidth=0.8)
        ax.set_xticks(x)
        ax.set_xticklabels([f"{SDR:.1%}" for SDR in SDR_list])
        ax.set_xlabel("Social discount rate")
        ax.set_ylabel(f"NPV of {GHG_LABELS[ghg]} [ton]")
        ax.set_title(f"NPV of {flow} {GHG_LABELS[ghg]} flow")

    #fig.suptitle("Net present value of greenhouse gas flows", fontsize=15)
    fig.tight_layout()
    _show_or_save(fig, "npv_of_ghgs.png", save_path, show_or_save)


def plot_distribution_GWI(GWI_data_dict, TH_list, SDR_list, save_path, show_or_save, flow='net'):
    """Four panels (CO2 / CH4 / N2O / cum) in two rows, each with one violin per social discount rate for two TH.
        
    Args:
        GWI_data_dict (dict): Instantaneous and cumulative GWI values in each timestop for every TH and SDR. 
        TH (int): List of social discount rates in decimal numbers.
        SDR_list (list): Location to save the plot.
    """

    SDR_set = sorted(set([min(SDR_list), 0.0, max(SDR_list)]))
    columns = GHG_LIST + ["cum"]
    fig, axs = plt.subplots(len(TH_list), len(GHG_LIST)+1, figsize=(16,9))

    for i, th in enumerate(TH_list):
        for j, ghg in enumerate(columns):
            ax = axs[i,j]

            for k, sdr in enumerate(SDR_set):
                if ghg=="cum":
                    data = GWI_data_dict[flow][f'TH_{th}'][f'SDR_{sdr}']['GWI_cum']
                else:
                    data = GWI_data_dict[flow][f'TH_{th}'][f'SDR_{sdr}']['GWI_inst'][ghg]

                ax.violinplot(data, positions=[k+1], facecolor=_colormap_coloring(ghg, sdr, SDR_list), linecolor='black', widths=0.7, showmedians=True, showextrema=True)

            ax.ticklabel_format(axis='y', style='sci', scilimits=(-2,3))
            ax.yaxis.get_offset_text().set_fontsize(9)
            #ax.axhline(0.0, color="black", linewidth=0.8)
            ax.set_xticks(range(1, len(SDR_set) + 1))
            ax.set_xticklabels([f"{sdr:.1%}" for sdr in SDR_set])
            ax.set_xlabel("Social discount rate")
            ax.set_ylabel(f"GWI [ton CO$_2$e]")
            if ghg=="cum":
                ax.set_title(f"Cumulative GWI, TH={th}")
            else:
                ax.set_title(f"Instantaneous GWI, {GHG_LABELS[ghg]}, TH={th}")

    #fig.suptitle(f"Distribution of net instantaneous GWI", fontsize=15)
    fig.tight_layout()

    _show_or_save(fig, "distribution_of_GWI.png", save_path, show_or_save)


def plot_GWI_cum_final(extm_vals_dict, TH_list, SDR_list, save_path, show_or_save, flow='net'):
    """ One panel: the last value of the cumulative net GWI per social discount rate, with one bar per time horizon in TH_list."""

    fig, ax = plt.subplots(figsize=(4.5,4.5))
    x = np.arange(len(SDR_list))
    width = 0.8 / max(len(TH_list), 1)

    for t, th in enumerate(TH_list):

        data = [extm_vals_dict[flow][f'TH_{th}'][f'SDR_{SDR}']['cum_GWI']['final_cum_GWI'] for SDR in SDR_list]
        offset = (t - (len(TH_list) - 1) / 2) * width
        ax.bar(x+offset, data, width=width * 0.92, label=f"TH = {th} years", color=COLORS[f"TH_{th}"], edgecolor="black", linewidth=0.6)

    ax.ticklabel_format(axis='y', style='sci', scilimits=(-2,3))
    ax.yaxis.get_offset_text().set_fontsize(9)
    ax.yaxis.set_inverted(True)
    #ax.axhline(0.0, color="black", linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{sdr:.1%}" for sdr in SDR_list])
    ax.set_xlabel("Social discount rate")
    ax.set_ylabel("Cumulative GWI [ton CO$_2$e]")
    #ax.set_title(f"Final cumulative {flow} GWI")
    ax.legend(title="Time horizon")

    fig.tight_layout()
    _show_or_save(fig, "final_cum_GWI.png", save_path, show_or_save)


def plot_graphical_CPT(gCPT_dict, TH_list, SDR_list, save_path, show_or_save):
    """Two panels (graphical CPT, cum GWI of that year) each with one bar per SDR.
        Data from ``gCPT[f'TH_{TH}'][f'SDR_{SDR}'][key]``.
    """
    panels = [('gCPT', 'Graphical CPT [years]', 'Graphical carbon payback time'),
                ('cum', 'Cumulative GWI [ton CO$_2$e]', 'Cumulative GWI in year of payback')]

    fig, axs = plt.subplots(1, 2, figsize=(12,4.5), squeeze=False)
    x = np.arange(len(SDR_list))

   
    for i, (key, ylabel, title) in enumerate(panels):
        ax = axs[0,i]
        if key == 'gCPT':
            data = [gCPT_dict[f'TH_{TH_list[0]}'][f'SDR_{sdr}']['gCPT'] for sdr in SDR_list]
        else:
            data = [gCPT_dict[f'TH_{TH_list[0]}'][f'SDR_{sdr}']['lb_GWI'] for sdr in SDR_list]

        ax.bar(x, data, width=0.65, color=COLORS[key], edgecolor="black", linewidth=0.6)


        delta = (max(data)-min(data))*0.5
        ax.set_ylim(min(data)-delta, max(data)+delta)
        if key == 'cum':
            ax.yaxis.set_inverted(True)
        #ax.axhline(0.0, color="black", linewidth=0.8)
        ax.set_xticks(x)
        ax.set_xticklabels([f"{SDR:.1%}" for SDR in SDR_list])
        ax.set_xlabel("Social discount rate")
        ax.set_ylabel(ylabel)
        ax.set_title(title)

    #fig.suptitle("Graphical CPT results", fontsize=15)
    fig.tight_layout()
    _show_or_save(fig, "gCPT.png", save_path, show_or_save)


def plot_analytical_CPT(aCPT_dict, TH_list, SDR_list, save_path, show_or_save):
    """Three panels (analytical CPT, lifetime released emissions and lifetime stored emissions) each with one bar per TH and SDR.
     Data from ``aCPT[f'TH_{TH}'][f'SDR_{SDR}'][key]``.
    """
    panels = [('aCPT', 'Analytical CPT [years]', 'Analytical carbon payback time'),
              ('E_lifetime', 'Released emissions [ton CO$_2$e]', 'Cumulative GWI of released GHGs'),
              ('S_lifetime', 'Stored emissions [ton CO$_2$e]', f'Cumulative GWI of stored {GHG_LABELS["CO2"]}')]

    fig, axs = plt.subplots(1, 3, figsize=(12,4.5), squeeze=False)
    x = np.arange(len(SDR_list))
    width = 0.8 / max(len(TH_list), 1)
    grouped_handles = {t: [] for t in range(len(TH_list))}

    for i, (key, ylabel, title) in enumerate(panels):
        ax = axs[0, i]
        for t, th in enumerate(TH_list):
            offset = (t - (len(TH_list) - 1) / 2) * width
            data = [aCPT_dict[f'TH_{th}'][f'SDR_{sdr}'][key] for sdr in SDR_list]
            color = COLORS[f"aCPT_{th}"] if key == 'aCPT' else COLORS[f"{key}_{th}"]
            bar = ax.bar(x+offset, data, width=width*0.92, label=f"TH = {th} years", color=color, edgecolor="black", linewidth=0.6)
            if len(grouped_handles[t]) > 0:
                if bar.patches[0].get_facecolor() not in [grouped_handles[t][j].patches[0].get_facecolor() for j in range(len(grouped_handles[t]))]: 
                    grouped_handles[t].append(bar)
            else:
                grouped_handles[t].append(bar)

        if key == 'S_lifetime':
            ax.yaxis.set_inverted(True)
        if key == 'E_lifetime' or 'S_lifetime':
                ax.ticklabel_format(axis='y', style='sci', scilimits=(-2,3))
                ax.yaxis.get_offset_text().set_fontsize(9)
        #ax.axhline(0.0, color="black", linewidth=0.8)
        ax.set_xticks(x)
        ax.set_xticklabels([f"{SDR:.1%}" for SDR in SDR_list])
        ax.set_xlabel("Social discount rate")
        ax.set_ylabel(ylabel)
        ax.set_title(title)

    handles = [tuple(grouped_handles[t]) for t in range(len(TH_list))]
    labels = [f"TH = {th} years" for th in TH_list]
    fig.legend(handles, labels, loc="lower center", ncols=len(TH_list),
               title="Time horizon", handler_map={tuple: HandlerTuple(ndivide=None)}, handlelength=10.0)
    #fig.suptitle("Analytical CPT results", fontsize=15)
    fig.tight_layout()
    fig.subplots_adjust(bottom=0.22)
    _show_or_save(fig, "aCPT.png", save_path, show_or_save)


def plot_distribution_of_CPTs(gCPT_dict, aCPT_dict, TH_list, SDR_list, save_path, show_or_save):

    aCPT_100, aCPT_500, gCPT_list = [], [], []

    for SDR in SDR_list:

        aCPT_100.append(aCPT_dict[f"TH_100"][f"SDR_{SDR}"]["aCPT"])
        aCPT_500.append(aCPT_dict[f"TH_500"][f"SDR_{SDR}"]["aCPT"])
        gCPT_list.append(gCPT_dict[f"TH_{TH_list[0]}"][f"SDR_{SDR}"]["gCPT"])


    CPT_list = [aCPT_100, aCPT_500, gCPT_list]
    xticklabels = ['Analytical CPT\n100 years', 'Analytical CPT\n500 years', 'Graphical CPT']

    fig, ax = plt.subplots(figsize=(4.5,4.5))

    for k, (violin, colorkey) in enumerate(zip(CPT_list, GHG_LIST)):
        ax.violinplot(violin, positions=[k+1], facecolor=_colormap_coloring(colorkey, colorscale=SDR_list), linecolor='black',  widths=0.62, showmedians=True, showextrema=True)

    #ax.axhline(0.0, color="black", linewidth=0.8)
    ax.set_xticks(range(1, len(xticklabels) + 1))
    ax.set_xticklabels(xticklabels)
    #ax.set_title("Distribution of carbon payback times")
    ax.set_ylabel('CPT [years]')
    plt.tight_layout()

    _show_or_save(fig, 'distribution_of_CPTs.png', save_path, show_or_save)


def plot_GWP_GHG(GWI_inst, GWI_cum, AGWP_ref, g_flows, TH, SDR, save_path, show_or_save):
    """Plots the results of the dynamic LCA function.

    Args:
        GWI_inst (array): Dictionary containing instantaneous GWI for each GHG and total GWI. [W/m²]
        GWP_cum (array): Cumulative GWI over time. [W/m²]
        AGWP_ref (array): AGWP of 1 ton CO2 over time. [W/m²/ton CO2e]
        CO2_flows (array): tonnes of CO2 emitted in year 0, 1, 2, ...
        CH4_flows (array): kg of CH4 emitted in year 0, 1, 2, ...
        N2O_flows (array): kg of N2O emitted in year 0, 1, 2, ...
        TH (int): Analytical horizon (years)
    """

    fig, axs = plt.subplots(2, 3, figsize=(12,9))
    for row in range(2):
        for col in range(3):
            axs[row, col].set_xlabel('Time [years]')
            axs[row, col].grid(True, linestyle='--', linewidth=0.5, color='gray')

    x = np.arange(1, TH+1)

    axs[0, 0].plot(x, GWI_inst['CO2'], label='CO2', color='blue')
    axs[0, 0].set_ylabel('GWI [ton CO2e]')
    axs[0, 0].set_title('Instantaneous GWI of CO2')
    axs[0, 0].legend(loc='upper right')

    axs[1, 0].plot(x, GWI_inst['CH4'], label='CH4', color='orange')
    axs[1, 0].plot(x, GWI_inst['N2O'], label='N2O', color='green')
    axs[1, 0].set_ylabel('GWI [ton CO2e]')
    axs[1, 0].set_title('Instantaneous GWI of CH4 and N2O')


    axs[0, 1].plot(x, GWI_cum, color='red')
    axs[0, 1].hlines(GWI_cum[-1], x[0], x[-1], label=f"{round(GWI_cum[-1], 1)} ton CO2e", color='0.5', linestyles="dotted")
    axs[0, 1].set_ylabel('Cumulative GWI [ton CO2e]')
    axs[0, 1].set_title('Cumulative GWI')
    axs[0, 1].legend(loc='upper right')

    axs[1, 1].plot(x, AGWP_ref, label='CO2', color='blue')
    axs[1, 1].set_ylabel('AGWP [W/m²/ton CO2]')
    axs[1, 1].set_title('AGWP of CO2 (reference)')


    axs[0, 2].plot(x, g_flows["CO2"], label='CO2', color='blue')
    axs[0, 2].set_ylabel('Flow [ton/year]')
    axs[0, 2].set_title('Annual flow of CO2')
    axs[0, 2].legend(loc='upper right')

    axs[1, 2].plot(x, g_flows["CH4"], label='CH4', color='orange')
    axs[1, 2].plot(x, g_flows["N2O"], label='N2O', color='green')
    axs[1, 2].set_ylabel('Flow [ton/year]')
    axs[1, 2].set_title('Annual flows of CH4 and N2O')


    #fig.suptitle(f"Dynamic LCA Results, TH: {TH}years, SDR: {SDR:.1%}%", fontsize=16)
    plt.legend()
    plt.tight_layout()

    _show_or_save(fig, f'TH_{TH}_SDR_{SDR}_dLCA_results.png', save_path, show_or_save)


def conceptual_cGWI_trajectory(y_values, x_values, CPT, iCPT, save_path, show_or_save):


    fig, ax = plt.subplots(figsize=(9, 4.5))

    ax.spines['top'].set_color('none')
    ax.spines['right'].set_color('none')
    ax.spines['left'].set_position('zero')
    ax.spines['bottom'].set_position('zero')
    ax.plot(1, 0, ">k", transform=ax.get_yaxis_transform(), clip_on=False)
    ax.plot(0, 1, "^k", transform=ax.get_xaxis_transform(), clip_on=False)


    ax.set_xlim(0, 13)
    ax.set_ylim(-10, 14)


    labels = ax.get_xticklabels()
    for label in labels:
        if label.get_text() == '0':
            label.set_visible(False)


    ax.plot(x_values, y_values, color=COLORS["cum"], linewidth=2)
    ax.plot(CPT, 0, '*', label='CPT', color='olive')
    if iCPT:
        ax.plot(iCPT, 0, '*', label='Inverted CPT', color='navy')


    ax.set_xlabel('Time [years]', loc='right')
    ax.set_ylabel('GWI [ton CO2e]')
    ax.grid(True, linestyle="--", linewidth=0.5, color="grey")


    plt.legend()
    plt.tight_layout()
    addon = 'perm_stor' if iCPT==None else 'temp_stor'
    _show_or_save(fig, f'gCPT_trajectory_{addon}', save_path, show_or_save)


def ton_year_theory(model_params, save_path, show_or_save):

    fig, ax = plt.subplots(2,1,figsize=(9, 4.5))
    
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


    no_points = 100
    y_atmo_load = np.concatenate(([1],[dynamic_lca.atmo_load_BM(t, "CO2", model_params) for t in range(1, no_points+1)]))
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
    ax[0].set_ylabel('Moura Costa method')
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
    ax[1].set_ylabel('Lashof method')
    ax[1].legend()

    _show_or_save(fig, 'ton_year_approaches.png', save_path, show_or_save)



if __name__ == "__main__":

    plt.rcdefaults()

    filepath_xlsx = 'C:/Users/Sebastian/Documents/Coding projects/CPT_CCU/data/emission_flows_3.xlsx'
    filepath_yaml = 'C:/Users/Sebastian/Documents/Coding projects/CPT_CCU/data/model_parameters.yaml'

    model_params, g_construction, g_operation, g_raw_material_acquisition, g_decommissioning, g_prod_use_phase, \
        g_prod_EOL, g_stored, g_released, g_net = read_data.read_emission_flows_xlsx(filepath_xlsx, filepath_yaml)


    # Input parameters
    show_or_save = 'save'
    if show_or_save == 'save':
        save_path = f"C:/Users/Sebastian/Documents/Coding projects/CPT_CCU/results/1787227814/"
        #os.makedirs(save_path)
    else:
        save_path = None


    # Theoretical CPT trajectory with negative emissions
    x_values = np.linspace(0, 13, 100)
    y_values1 = [10-0.1*i**2 for i in x_values] # [-0.1*(i-0.1)**(2)+10 for i in range(no_points)]
    CPT1 = 10
    conceptual_cGWI_trajectory(y_values=y_values1, x_values=x_values, CPT=CPT1, iCPT=None, save_path=save_path, show_or_save=show_or_save)


    # Theoretical CPT trajectory with temporally stored emissions
    y_values2 = [(x-3)*(x-10)*(x+5)/20 for x in x_values] # [(x-15)*(x-40)*(11*x+120)/(1440) for x in range(no_points)]
    CPT2 = 3
    iCPT = 10   #inverted carbon payback time
    conceptual_cGWI_trajectory(y_values=y_values2, x_values=x_values, CPT=CPT2, iCPT=iCPT, save_path=save_path, show_or_save=show_or_save)


    # Comparison between Moura-Costa and Lashof method
    ton_year_theory(model_params=model_params, save_path=save_path, show_or_save=show_or_save)