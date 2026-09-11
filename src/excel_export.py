"""
excel_export.py
===============

Writes the results of ``SA_CPT`` (graphical_CPT, analytical_CPT, GWI_data,
extreme_vals and the raw g-flows) into a single, formatted .xlsx workbook.

Sheets produced
---------------
CPT           : one row per (TH, SDR) with gCPT / aCPT and their companion values
GWI_inst      : instantaneous GWI, columns = (flow, horizon, SDR, GHG), rows = year
GWI_cum       : cumulative GWI,    columns = (flow, horizon, SDR),      rows = year
g_flows       : raw emission/removal flows, columns = (flow, GHG),      rows = year
extm_GWI_vals    : min/max/final GWI per (flow, TH, SDR, GHG)  [extreme_vals['GWI']]
extm_flow_vals   : min/max/NPV per (flow, TH, SDR, GHG)        [extreme_vals['flows']]

Only pandas and openpyxl are required.

Usage (at the end of SA_CPT, after the TH/SDR loops):

    from excel_export import write_results_to_excel

    xlsx_path = write_results_to_excel(
        graphical_CPT=graphical_CPT,
        analytical_CPT=analytical_CPT,
        GWI_data=GWI_data,
        extreme_vals=extreme_vals,
        g_dict=g_dict,
        TH_list=TH_list,
        SDR_list=SDR_list,
        save_path=save_path,
    )
"""

from __future__ import annotations

import os

import numpy as np
import pandas as pd
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

# --------------------------------------------------------------------------- #
# constants / styles
# --------------------------------------------------------------------------- #

GHG_ORDER = ("CO2", "CH4", "N2O", "total")

# Units used in the column headings. Change them here and every sheet follows.
UNIT_GWI = "ton CO2e"    # GWI_inst / GWI_cum / extm_GWI_vals
UNIT_FLOW = "ton"        # g_flows / extm_flow_vals

SCI_FMT = "0.000E+00"   # radiative-forcing style numbers
FIX_FMT = "0.000"       # years
PCT_FMT = "0.0%"        # SDR stored as a fraction (0.09 -> 9.0%)
PCT_LIT_FMT = '0.0"%"'  # SDR already multiplied by 100 (9.0 -> 9.0%)

HEADER_FONT = Font(bold=True, color="FFFFFF")
HEADER_FILL = PatternFill("solid", fgColor="1F4E79")
SUBHEAD_FILL = PatternFill("solid", fgColor="2E75B6")
TITLE_FONT = Font(bold=True, size=12, color="1F4E79")
INDEX_FONT = Font(bold=True)
CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)


# --------------------------------------------------------------------------- #
# small helpers
# --------------------------------------------------------------------------- #

def _resolve_path(save_path, filename="SA_CPT_results.xlsx"):
    """Accept either a directory or a full *.xlsx path."""
    save_path = str(save_path)
    if save_path.lower().endswith((".xlsx", ".xlsm")):
        folder = os.path.dirname(save_path)
        if folder:
            os.makedirs(folder, exist_ok=True)
        return save_path
    os.makedirs(save_path, exist_ok=True)
    return os.path.join(save_path, filename)


def _get(d, *keys):
    """Nested lookup that never creates keys (important: defaultdicts!)."""
    cur = d
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return None
        cur = cur[k]
    return cur


def _th_label(TH):
    return f"TH {TH}"


def _sdr_label(SDR):
    return f"{SDR * 100:.1f}%"


def _ghg_label(ghg, unit):
    """'CO2' -> 'CO2\\n[ton CO2e]' (used in the wide sheets' headers)."""
    return f"{ghg}\n[{unit}]"


def _series(arr):
    return pd.Series(np.asarray(arr, dtype=float))


def _multiindex(cols_dict, names):
    """Build a DataFrame from {tuple: Series} with a named column MultiIndex."""
    if not cols_dict:
        return pd.DataFrame()
    df = pd.DataFrame(cols_dict)
    df.columns = pd.MultiIndex.from_tuples(list(df.columns), names=names)
    df.index.name = "year"
    return df


# --------------------------------------------------------------------------- #
# frame builders
# --------------------------------------------------------------------------- #

def _cpt_frame(graphical_CPT, analytical_CPT, TH_list, SDR_list):
    cols = ["Time horizon [a]", "SDR [%]", "graphical\nCPT [a]", "Cum GWI before\ngCPT [ton CO2e]", "Cum GWI after\ngCPT [ton CO2e]",
            "analytical\nCPT [a]", "Lifetime released\n[ton CO2e]", "Lifetime stored\n[ton CO2e]", "aCPT - gCPT [a]"]
    rows = []
    for TH in TH_list:
        for SDR in SDR_list:
            g = _get(graphical_CPT, f"TH_{TH}", f"SDR_{SDR}") or {}
            a = _get(analytical_CPT, f"TH_{TH}", f"SDR_{SDR}") or {}
            if not g and not a:
                continue
            gcpt, acpt = g.get("gCPT"), a.get("aCPT")
            rows.append({
                "Time horizon [a]": TH,
                "SDR [%]": SDR * 100,
                "graphical\nCPT [a]": gcpt,
                "Cum GWI before\ngCPT [ton CO2e]": g.get("lb_GWI"),
                "Cum GWI after\ngCPT [ton CO2e]": g.get("ub_GWI"),
                "analytical\nCPT [a]": acpt,
                "Lifetime released\n[ton CO2e]": a.get("E_lifetime"),
                "Lifetime stored\n[ton CO2e]": a.get("S_lifetime"),
                "aCPT - gCPT [a]": (acpt - gcpt) if (gcpt is not None and acpt is not None) else None,
            })
    return pd.DataFrame(rows, columns=cols)


def _inst_frame(GWI_data, flows, TH_list, SDR_list):
    cols = {}
    for flow in flows:
        for TH in TH_list:
            for SDR in SDR_list:
                entry = _get(GWI_data, flow, f"TH_{TH}", f"SDR_{SDR}")
                if not entry or entry.get("GWI_inst") is None:
                    continue
                inst = entry["GWI_inst"]
                keys = [k for k in GHG_ORDER if k in inst] + \
                       [k for k in inst if k not in GHG_ORDER]
                for ghg in keys:
                    cols[(flow, _th_label(TH), _sdr_label(SDR),
                          _ghg_label(ghg, UNIT_GWI))] = _series(inst[ghg])
    return _multiindex(cols, ["flow", "TH", "SDR", "GHG"])


def _cum_frame(GWI_data, flows, TH_list, SDR_list):
    cols = {}
    for flow in flows:
        for TH in TH_list:
            for SDR in SDR_list:
                entry = _get(GWI_data, flow, f"TH_{TH}", f"SDR_{SDR}")
                if not entry or entry.get("GWI_cum") is None:
                    continue
                cols[(flow, _th_label(TH), _sdr_label(SDR))] = _series(entry["GWI_cum"])
    return _multiindex(cols, ["flow", "TH", "SDR"])


def _g_flows_frame(g_list):
    cols = {}
    for flow, ghg_dict in g_list.items():
        if not isinstance(ghg_dict, dict):
            continue
        keys = [k for k in GHG_ORDER if k in ghg_dict] + \
               [k for k in ghg_dict if k not in GHG_ORDER]
        for ghg in keys:
            cols[(flow, _ghg_label(ghg, UNIT_FLOW))] = _series(ghg_dict[ghg])
    return _multiindex(cols, ["flow", "GHG"])


def _extreme_gwi_frame(extreme_vals, flows, TH_list, SDR_list):
    """
    Pivot the GWI-related extremes into a tidy table.

    Expected nesting (current schema):
        extreme_vals[flow]['TH_x']['SDR_y'][GHG] -> {'min_inst_GWI', 'max_inst_GWI', ...}
        extreme_vals[flow]['TH_x']['SDR_y']['cum_GWI'] -> {'min_cum_GWI', 'max_cum_GWI', 'final_cum_GWI'}

    Returns (DataFrame, header_spec) where header_spec is [(top, bottom), ...].
    """
    ghgs = ("CO2", "CH4", "N2O")
    rows = []
    for flow in flows:
        for TH in TH_list:
            for SDR in SDR_list:
                entry = _get(extreme_vals, flow, f"TH_{TH}", f"SDR_{SDR}")
                if not entry:
                    continue
                row = {"flow": flow, "Time horizon [a]": TH, "SDR": SDR}
                for ghg in ghgs:
                    sub = entry.get(ghg, {}) or {}
                    row[f"{ghg} min_inst"] = sub.get("min_inst_GWI")
                    row[f"{ghg} max_inst"] = sub.get("max_inst_GWI")
                cum = entry.get("cum_GWI", {}) or {}
                row["min_cum"] = cum.get("min_cum_GWI")
                row["max_cum"] = cum.get("max_cum_GWI")
                row["final_cum"] = cum.get("final_cum_GWI")
                rows.append(row)

    cols = ["flow", "Time horizon [a]", "SDR"]
    header = [("", "flow"), ("", "Time horizon\n[a]"), ("", "SDR")]
    for ghg in ghgs:
        cols += [f"{ghg} min_inst", f"{ghg} max_inst"]
        header += [(ghg, f"min inst GWI\n[{UNIT_GWI}]"),
                   (ghg, f"max inst GWI\n[{UNIT_GWI}]")]
    cols += ["min_cum", "max_cum", "final_cum"]
    header += [("", f"min cum GWI\n[{UNIT_GWI}]"),
               ("", f"max cum GWI\n[{UNIT_GWI}]"),
               ("", f"final cum GWI\n[{UNIT_GWI}]")]
    return pd.DataFrame(rows, columns=cols), header


def _extreme_flow_frame(extreme_vals, flows, TH_list, SDR_list):
    """
    Pivot the flow-related extremes (min / max / NPV of the raw, non-discounted
    and discounted flows) into a tidy table.

    Expected nesting (current schema):
        extreme_vals[flow]['TH_x']['SDR_y'][GHG] -> {'min_flow', 'max_flow', 'NPV_flow', ...}

    Returns (DataFrame, header_spec) where header_spec is [(top, bottom), ...].
    """
    ghgs = ("CO2", "CH4", "N2O")
    rows = []
    for flow in flows:
        for TH in TH_list:
            for SDR in SDR_list:
                entry = _get(extreme_vals, flow, f"TH_{TH}", f"SDR_{SDR}")
                if not entry:
                    continue
                row = {"flow": flow, "Time horizon [a]": TH, "SDR": SDR}
                for ghg in ghgs:
                    sub = entry.get(ghg, {}) or {}
                    row[f"{ghg} min_flow"] = sub.get("min_flow")
                    row[f"{ghg} max_flow"] = sub.get("max_flow")
                    row[f"{ghg} NPV_flow"] = sub.get("NPV_flow")
                rows.append(row)

    cols = ["flow", "Time horizon [a]", "SDR"]
    header = [("", "flow"), ("", "Time horizon\n[a]"), ("", "SDR")]
    for ghg in ghgs:
        cols += [f"{ghg} min_flow", f"{ghg} max_flow", f"{ghg} NPV_flow"]
        header += [(ghg, f"min flow\n[{UNIT_FLOW}]"),
                   (ghg, f"max flow\n[{UNIT_FLOW}]"),
                   (ghg, f"NPV flow\n[{UNIT_FLOW}]")]
    return pd.DataFrame(rows, columns=cols), header


# --------------------------------------------------------------------------- #
# formatting helpers
# --------------------------------------------------------------------------- #

def _safe_style(cell, font=None, fill=None, alignment=None, number_format=None):
    """Merged cells can refuse some assignments -> fail silently."""
    try:
        if font is not None:
            cell.font = font
        if fill is not None:
            cell.fill = fill
        if alignment is not None:
            cell.alignment = alignment
        if number_format is not None:
            cell.number_format = number_format
    except AttributeError:
        pass


def _format_block(ws, n_header_rows, n_index_cols, n_cols,
                  data_number_format=SCI_FMT, index_width=22, data_width=14,
                  header_row_offset=0, freeze=True):
    """Header styling, column widths, number formats and freeze panes."""
    for r in range(header_row_offset + 1, header_row_offset + n_header_rows + 1):
        for c in range(1, n_cols + 1):
            _safe_style(ws.cell(row=r, column=c),
                        font=HEADER_FONT, fill=HEADER_FILL, alignment=CENTER)
        _auto_row_height(ws, r, n_cols)

    for c in range(1, n_cols + 1):
        ws.column_dimensions[get_column_letter(c)].width = (
            index_width if c <= n_index_cols else data_width
        )

    first_data_row = header_row_offset + n_header_rows + 1
    for row in ws.iter_rows(min_row=first_data_row, max_row=ws.max_row,
                            min_col=1, max_col=n_cols):
        for cell in row:
            if cell.column <= n_index_cols:
                _safe_style(cell, font=INDEX_FONT,
                            alignment=Alignment(horizontal="center"))
            else:
                _safe_style(cell, number_format=data_number_format,
                            alignment=Alignment(horizontal="right"))

    if freeze:
        ws.freeze_panes = ws.cell(row=first_data_row, column=n_index_cols + 1)


def _check_fmt_keys(sheet, df, special_fmts):
    """Warn if a special_fmts key no longer matches a column (renamed heading)."""
    unknown = [k for k in (special_fmts or {}) if k not in list(df.columns)]
    if unknown:
        print(f"  [excel_export] warning: sheet '{sheet}' has number formats for "
              f"unknown column(s) {unknown} - heading renamed? Format not applied.")


def _format_flat_table(ws, df, n_index_cols, default_fmt=SCI_FMT,
                       index_width=24, data_width=16, special_fmts=None):
    """Format a sheet written with ``to_excel(index=False)`` (header in row 1)."""
    n_cols = df.shape[1]
    special = special_fmts or {}
    _check_fmt_keys(ws.title, df, special)

    for c in range(1, n_cols + 1):
        _safe_style(ws.cell(row=1, column=c),
                    font=HEADER_FONT, fill=HEADER_FILL, alignment=CENTER)
        ws.column_dimensions[get_column_letter(c)].width = (
            index_width if c <= n_index_cols else data_width
        )
    _auto_row_height(ws, 1, n_cols)

    for j, col in enumerate(df.columns, start=1):
        is_index = j <= n_index_cols
        fmt = special.get(col, None if is_index else default_fmt)
        align = Alignment(horizontal="center" if is_index else "right")
        font = INDEX_FONT if is_index else None
        for r in range(2, len(df) + 2):
            _safe_style(ws.cell(row=r, column=j),
                        font=font, alignment=align, number_format=fmt)

    ws.freeze_panes = ws.cell(row=2, column=n_index_cols + 1)
    if len(df):
        ws.auto_filter.ref = ws.dimensions


def _auto_row_height(ws, row, n_cols, base=15):
    """Make a header row tall enough for its multi-line labels."""
    lines = 1
    for c in range(1, n_cols + 1):
        val = ws.cell(row=row, column=c).value
        if isinstance(val, str):
            lines = max(lines, val.count("\n") + 1)
    ws.row_dimensions[row].height = base * lines + 4


def _write_grouped_table(writer, sheet, df, header, n_index_cols,
                         default_fmt=SCI_FMT, index_width=22, data_width=17,
                         special_fmts=None):
    """
    Write ``df`` with a two-row header.

    ``header`` is one ``(top, bottom)`` pair per column. Consecutive identical
    non-empty ``top`` values are merged into a group heading in row 1 (e.g. CO2
    spanning its min/max columns); an empty ``top`` leaves row 1 blank so the
    label in row 2 stands alone.
    """
    df.to_excel(writer, sheet_name=sheet, index=False, header=False, startrow=2)
    ws = writer.sheets[sheet]
    n_cols = df.shape[1]
    special = special_fmts or {}
    _check_fmt_keys(sheet, df, special)

    # row 1: group headings (merged), row 2: column headings
    tops = [h[0] for h in header]
    j = 0
    while j < len(tops):
        k = j
        while k + 1 < len(tops) and tops[k + 1] == tops[j]:
            k += 1
        if tops[j]:
            ws.cell(row=1, column=j + 1, value=tops[j])
            if k > j:
                ws.merge_cells(start_row=1, start_column=j + 1,
                               end_row=1, end_column=k + 1)
        j = k + 1
    for j, (_, bottom) in enumerate(header, start=1):
        ws.cell(row=2, column=j, value=bottom)

    for r in (1, 2):
        for c in range(1, n_cols + 1):
            _safe_style(ws.cell(row=r, column=c),
                        font=HEADER_FONT, fill=HEADER_FILL, alignment=CENTER)
    ws.row_dimensions[1].height = 19
    _auto_row_height(ws, 2, n_cols)

    for c in range(1, n_cols + 1):
        ws.column_dimensions[get_column_letter(c)].width = (
            index_width if c <= n_index_cols else data_width
        )

    for j, col in enumerate(df.columns, start=1):
        is_index = j <= n_index_cols
        fmt = special.get(col, None if is_index else default_fmt)
        align = Alignment(horizontal="center" if is_index else "right")
        font = INDEX_FONT if is_index else None
        for r in range(3, len(df) + 3):
            _safe_style(ws.cell(row=r, column=j),
                        font=font, alignment=align, number_format=fmt)

    ws.freeze_panes = ws.cell(row=3, column=n_index_cols + 1)
    if len(df):
        ws.auto_filter.ref = f"A2:{get_column_letter(n_cols)}{len(df) + 2}"


def _header_rows_of(df):
    """Rows pandas writes above the data (MultiIndex columns add an index-name row)."""
    extra = 1 if (df.columns.nlevels > 1 and df.index.name) else 0
    return df.columns.nlevels + extra


# --------------------------------------------------------------------------- #
# main entry point
# --------------------------------------------------------------------------- #

def write_results_to_excel(gCPT_dict, aCPT_dict, GWI_data_dict, extm_vals_dict,
                           g_dict, TH_list, SDR_list, save_path,
                           filename="SA_CPT_results.xlsx"):
    """
    Write all CPT / GWI results into one formatted workbook and return its path.

    Parameters
    ----------
    graphical_CPT, analytical_CPT : dict
        ``{'TH_100': {'SDR_-0.03': {...}}}``
    GWI_data : nested dict
        ``[flow]['TH_x']['SDR_y'] -> {'GWI_inst': {GHG: array}, 'GWI_cum': array}``
    extreme_vals : nested dict
        ``[flow]['TH_x']['SDR_y'][GHG] -> {'min_flow', 'max_flow', 'NPV_flow',
        'min_inst_GWI', 'max_inst_GWI'}`` plus a sibling
        ``[flow]['TH_x']['SDR_y']['cum_GWI'] -> {'min_cum_GWI', 'max_cum_GWI', 'final_cum_GWI'}``
    g_list : dict
        ``{flow: {'CO2': array, 'CH4': array, 'N2O': array}}``
    save_path : str
        Directory or full ``*.xlsx`` path.
    """
    path = _resolve_path(save_path, filename)

    # flow ordering: g_list first (it holds all nine names), then any extras
    # found in GWI_data or extreme_vals (e.g. an aggregate 'net' flow that
    # only shows up in extreme_vals).
    flows = list(g_dict.keys())
    flows += [f for f in GWI_data_dict.keys() if f not in flows]
    flows += [f for f in extm_vals_dict.keys() if f not in flows]

    cpt_df = _cpt_frame(gCPT_dict, aCPT_dict, TH_list, SDR_list)
    inst_df = _inst_frame(GWI_data_dict, flows, TH_list, SDR_list)
    cum_df = _cum_frame(GWI_data_dict, flows, TH_list, SDR_list)
    gflow_df = _g_flows_frame(g_dict)
    ev_gwi_df, ev_gwi_header = _extreme_gwi_frame(extm_vals_dict, flows, TH_list, SDR_list)
    ev_flow_df, ev_flow_header = _extreme_flow_frame(extm_vals_dict, flows, TH_list, SDR_list)

    with pd.ExcelWriter(path, engine="openpyxl") as writer:

        # ---------------------------------------------------------------- CPT
        cpt_df.to_excel(writer, sheet_name="CPT", index=False)
        _format_flat_table(
            writer.sheets["CPT"], cpt_df, n_index_cols=2,
            index_width=14, data_width=22,
            special_fmts={"Time horizon [a]": "0",
                          "SDR [%]": PCT_LIT_FMT,
                          "graphical\nCPT [a]": FIX_FMT,
                          "analytical\nCPT [a]": FIX_FMT,
                          "aCPT - gCPT [a]": FIX_FMT},
        )

        # ----------------------------------------------------------- GWI_inst
        inst_df.to_excel(writer, sheet_name="GWI_inst")
        _format_block(writer.sheets["GWI_inst"],
                      n_header_rows=_header_rows_of(inst_df),
                      n_index_cols=1, n_cols=inst_df.shape[1] + 1,
                      index_width=8, data_width=15)

        # ------------------------------------------------------------ GWI_cum
        cum_df.to_excel(writer, sheet_name="GWI_cum")
        ws = writer.sheets["GWI_cum"]
        _format_block(ws, n_header_rows=_header_rows_of(cum_df),
                      n_index_cols=1, n_cols=cum_df.shape[1] + 1,
                      index_width=8, data_width=15)
        # GWI_cum has no GHG level, so the unit goes in the index-name row
        note = ws.cell(row=_header_rows_of(cum_df), column=2,
                       value=f"*All values in [{UNIT_GWI}]")
        _safe_style(note, font=Font(bold=False, italic=True, color="FFFFFF"),
                    alignment=Alignment(horizontal="left", vertical="center"))

        # ------------------------------------------------------------ g_flows
        gflow_df.to_excel(writer, sheet_name="g_flows")
        ws = writer.sheets["g_flows"]
        _format_block(ws, n_header_rows=_header_rows_of(gflow_df),
                      n_index_cols=1, n_cols=gflow_df.shape[1] + 1,
                      index_width=8, data_width=16)
        # note in the (otherwise empty) index-name row of the header block
        note = ws.cell(row=_header_rows_of(gflow_df), column=2,
                       value="*Non-discounted flows (input data)")
        _safe_style(note, font=Font(bold=False, italic=True, color="FFFFFF"),
                    alignment=Alignment(horizontal="left", vertical="center"))

        # --------------------------------------------------------- extm_GWI_vals
        if not ev_gwi_df.empty:
            _write_grouped_table(
                writer, "extm_GWI_vals", ev_gwi_df, ev_gwi_header, n_index_cols=3,
                index_width=24, data_width=17,
                special_fmts={"Time horizon [a]": "0", "SDR": PCT_FMT},
            )

        # -------------------------------------------------------- extm_flow_vals
        if not ev_flow_df.empty:
            _write_grouped_table(
                writer, "extm_flow_vals", ev_flow_df, ev_flow_header, n_index_cols=3,
                index_width=24, data_width=17,
                special_fmts={"Time horizon [a]": "0", "SDR": PCT_FMT},
            )
            # the flow-name column needs more room than the rest
            writer.sheets["extm_flow_vals"].column_dimensions["A"].width = 28

    return path