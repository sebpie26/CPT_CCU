"""import math as m
import numpy as np

def atmo_load_SARF(ghg, model_params):
    param = model_params["SARF-model"]

    if ghg == "CO2":
        C_alpha_max = param["CO2_C0"]
        alpha_N2O = param["CO2_c1"]*m.sqrt(param["N2O_C"])

        if param["CO2_C"] >= C_alpha_max:
            alpha_prime = param["CO2_d1"] - param["CO2_b1"]^2 /4 /param["CO2_a1"]

        elif param["CO2_C0"] < param["CO2_C"] and param["CO2_C"] < C_alpha_max:
            alpha_prime = param["CO2_d1"]+param["CO2_a1"]*(param["CO2_C"]-param["CO2_C0"])^2 +param["CO2_b1"](param["CO2_C"]-param["CO2_C0"])

        else:
            alpha_prime = param["CO2_d1"]

        return (alpha_prime+alpha_N2O)*m.log(param["CO2_C"] / param["CO2_C0"])

    elif ghg == "CH4":
        return (param["N2O_a2"]*m.sqrt(param["CO2_C"]) + param["N2O_b2"]*m.sqrt(param["N2O_C"]) + param["N2O_c2"]*m.sqrt(param["CH4_C"]) + param["N2O_d2"]) * (m.sqrt(param["N2O_C"])-param["N2O_C0"])

    elif ghg == "N2O":
        return (param["CH4_a3"]*m.sqrt(param["CH4_C"]) + param["CH4_b3"]*m.sqrt(param["N2O_C"] + param["CH4_d3"])) * (m.sqrt(param["CH4_C"])-param["CH4_C0"])
    else:
        raise ValueError(f"Greenhouse gas {ghg} is not implemented in SARF-model. Available GHG are CO2, CH4, N2O.")

liste2 = ['a','b','c']
liste1 = liste2 + [1]

dicty = {"eins":2, "zwei":3, "drei":5}

bla = dicty.keys()
bla.remove("eins")
bla.remove("zwei")
"""

import matplotlib.pyplot as plt
import numpy as np

def plot_CGWI_ghg_shares(GWI_data_dict, TH_list, save_path, show_or_save, sdr=0.0):

    def autopct_filter(pct): return f'{pct:.1f}%' if pct > 3 else ''

    fig, axs = plt.subplots(1, len(TH_list), figsize=(12, 4.5), squeeze=False)

    for i, th in enumerate(TH_list):
        ax = axs[0, i]
        data = [abs(sum(sum(GWI_data_dict[key][f"TH_{th}"][f"SDR_{sdr}"]["GWI_inst"][ghg]) for key in GWI_data_dict.keys())) for ghg in GHG_LIST]
        labels = [GHG_LABELS[ghg] for ghg in GHG_LIST]
        colors = [COLORS[ghg] for ghg in GHG_LIST]

        wedges, texts, autotexts = ax.pie(
            data, autopct=autopct_filter, pctdistance=0.8, colors=colors,
            wedgeprops=dict(width=0.4, edgecolor="w"), startangle=90)
        kw = dict(arrowprops=dict(arrowstyle="-"), zorder=0, va="center")

        # --- compute wedge angles/anchor points ---
        angles = []
        for w in wedges:
            ang = (w.theta2 - w.theta1) / 2. + w.theta1
            angles.append(ang)

        # split wedges into left/right side based on x-position
        left_idx = [j for j, a in enumerate(angles) if np.cos(np.deg2rad(a)) < 0]
        right_idx = [j for j, a in enumerate(angles) if np.cos(np.deg2rad(a)) >= 0]

        # sort each side top-to-bottom by their natural y position
        left_idx.sort(key=lambda j: -np.sin(np.deg2rad(angles[j])))
        right_idx.sort(key=lambda j: -np.sin(np.deg2rad(angles[j])))

        def assign_label_y(idx_list, min_gap=0.22):
            """Evenly space y-positions only enough to avoid overlap."""
            n = len(idx_list)
            if n == 0:
                return {}
            ys = [np.sin(np.deg2rad(angles[j])) for j in idx_list]
            # enforce a minimum gap between consecutive (sorted descending) ys
            for k in range(1, n):
                if ys[k-1] - ys[k] < min_gap:
                    ys[k] = ys[k-1] - min_gap
            return dict(zip(idx_list, ys))

        label_y = {}
        label_y.update(assign_label_y(left_idx))
        label_y.update(assign_label_y(right_idx))

        for j, w in enumerate(wedges):
            ang = angles[j]
            x = np.cos(np.deg2rad(ang))
            y = np.sin(np.deg2rad(ang))
            ty = label_y[j]
            tx = 1.3 * np.sign(x)

            horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
            connectionstyle = f"angle,angleA=0,angleB={ang}"
            kw["arrowprops"].update({"connectionstyle": connectionstyle})

            ax.annotate(
                labels[j],
                xy=(x, y),
                xytext=(tx, ty),
                horizontalalignment=horizontalalignment,
                **kw)

        ax.set_title(f"TH: {th} years")

    fig.tight_layout()
    _show_or_save(fig, "plot_CGWI_ghg_shares.png", save_path, show_or_save)