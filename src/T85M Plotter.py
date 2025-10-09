# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.4
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

year = 2024
first_index_year = 2021

import pandas as pd
import numpy as np
import json
import os
from pathlib import Path
import itables
import matplotlib.pyplot as plt
from itables import init_notebook_mode, show
itables.init_notebook_mode(all_interactive=True)
import seaborn as sns
import ipywidgets as widgets
from IPython.display import display
#pd.set_option('display.float_format',  '{:18,.0}'.format)
pd.set_option('display.float_format', lambda x: f'{x:15,.0f}' if abs(x)>1e5 else f'{x:15.2f}')
# Initialize interactive display mode
itables.init_notebook_mode(all_interactive=True)

# # Datasets

# +
index_chained_export = f'../data/index_export_chained.parquet'
index_chained_import = f'../data/index_import_chained.parquet'

index_chained_export = pd.read_parquet(index_chained_export)
index_chained_import = pd.read_parquet(index_chained_import)

# Append (concatenate) them
#index_chained_all = index_chained_export.copy()
index_chained_all = pd.concat([index_chained_export, index_chained_import], ignore_index=True)
#index_chained_all = index_chained_all[index_chained_all['year'] <= year].copy()

# -

# #### Calculate metrics

# +
df_base = index_chained_all.copy()
df_base["series"] = df_base["series"].astype(str)   # ensure series is string
df_base["flow"] = df_base["flow"].astype(str)       # ensure flow is string

df_base["time"] = df_base["year"].astype(str) + "-Q" + df_base["quarter"].astype(str)
df_base = df_base.sort_values(by=["year", "quarter"])
df_base["time"] = pd.Categorical(
    df_base["time"],
    ordered=True,
    categories=sorted(df_base["time"].unique(), key=lambda x: (int(x[:4]), int(x[-1])))
)

# ----------------------------
# Calculate transformations
# ----------------------------
df_base = df_base.sort_values(by=["level", "series", "flow", "year", "quarter"])

df_base["index"] = df_base["index_chained"]

df_base["quarterly_change"] = (
    df_base.groupby(["level", "series", "flow"])["index_chained"]
    .pct_change() * 100
)

df_base["year_on_year_change"] = (
    df_base.groupby(["level", "series", "flow"])["index_chained"]
    .pct_change(4) * 100
)

df_base["rolling_var"] = (
    df_base.groupby(["level", "series", "flow"])["index_chained"]
    .rolling(4).var()
    .reset_index(level=[0,1,2], drop=True)
)

# Ensure level column is lowercase
df_base['level'] = df_base['level'].str.lower()

df_base = df_base.reset_index(drop=True)
# -

# #### Filter dataset --> look only at total and sitc



df_base = df_base[df_base["level"] != 'commodity']
df_base = df_base[df_base["level"] != 'special_serie']
df_base

# # Plot

# +
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import ipywidgets as widgets
from IPython.display import display, clear_output

# ---------------------------
# Labels
# ---------------------------
SITC_labels = {
    "0": "0 - Food and live animals",
    "1": "1 - Beverages and tobacco",
    "2": "2 - Crude materials, inedible, except fuels",
    "3": "3 - Mineral fuels, lubricants and related materials",
    "4": "4 - Animal and vegetable oils, fats and waxes",
    "5": "5 - Chemicals and related products n.e.s.",
    "6": "6 - Manufactured goods classified chiefly by material",
    "7": "7 - Machinery and transport equipment",
    "8": "8 - Miscellaneous manufactured articles",
    "9": "9 - Commodities and transactions",
    "00": "00 - Live animals",
    "01": "01 - Meat and meat preparations",
    "02": "02 - Dairy products and birds' eggs",
    "03": "03 - Fish, crustaceans, mollusks, and preparations",
    "04": "04 - Cereals and cereal preparations",
    "05": "05 - Vegetables and fruit",
    "06": "06 - Sugars, sugar preparations, and honey",
    "07": "07 - Coffee, tea, cocoa, spices, and manufactures thereof",
    "08": "08 - Feeding stuff for animals (not including unmilled cereals)",
    "09": "09 - Miscellaneous edible products and preparations",
    "11": "11 - Beverages",
    "12": "12 - Tobacco and tobacco manufactures",
    "21": "21 - Hides, skins, and furskins, raw",
    "22": "22 - Oil seeds and oleaginous fruits",
    "23": "23 - Crude rubber (including synthetic and reclaimed)",
    "24": "24 - Cork and wood",
    "25": "25 - Pulp and waste paper",
    "26": "26 - Textile fibers (other than wool tops and other combed wool)",
    "27": "27 - Crude fertilizers and crude minerals",
    "28": "28 - Metalliferous ores and metal scrap",
    "29": "29 - Crude animal and vegetable materials, n.e.s.",
    "32": "32 - Coal, coke, and briquettes",
    "33": "33 - Petroleum, petroleum products, and related materials",
    "34": "34 - Gas, natural and manufactured",
    "35": "35 - Electric current",
    "41": "41 - Animal oils and fats",
    "42": "42 - Fixed vegetable fats and oils",
    "43": "43 - Animal and vegetable oils and fats, processed",
    "51": "51 - Organic chemicals",
    "52": "52 - Inorganic chemicals",
    "53": "53 - Dyeing, tanning, and coloring materials",
    "54": "54 - Medicinal and pharmaceutical products",
    "55": "55 - Essential oils and perfume materials",
    "56": "56 - Fertilizers (other than crude)",
    "57": "57 - Plastics in primary forms",
    "58": "58 - Plastics in non-primary forms",
    "59": "59 - Chemical materials and products, n.e.s.",
    "61": "61 - Leather, leather manufactures, and dressed furskins",
    "62": "62 - Rubber manufactures, n.e.s.",
    "63": "63 - Cork and wood manufactures",
    "64": "64 - Paper, paperboard, and articles thereof",
    "65": "65 - Textile yarn, fabrics, and related products",
    "66": "66 - Non-metallic mineral manufactures",
    "67": "67 - Iron and steel",
    "68": "68 - Non-ferrous metals",
    "69": "69 - Manufactures of metal, n.e.s.",
    "71": "71 - Power generating machinery and equipment",
    "72": "72 - Machinery specialized for industries",
    "73": "73 - Metalworking machinery",
    "74": "74 - General industrial machinery",
    "75": "75 - Office machines and computers",
    "76": "76 - Telecommunications and sound recording equipment",
    "77": "77 - Electrical machinery and apparatus",
    "78": "78 - Road vehicles",
    "79": "79 - Other transport equipment",
    "81": "81 - Prefabricated buildings and materials",
    "82": "82 - Furniture and parts thereof",
    "83": "83 - Travel goods, handbags, and similar containers",
    "84": "84 - Articles of apparel and clothing accessories",
    "85": "85 - Footwear",
    "87": "87 - Professional, scientific, and controlling instruments",
    "88": "88 - Photographic apparatus, optical goods, watches, and clocks",
    "89": "89 - Miscellaneous manufactured articles",
    "91": "91 - Postal packages not classified",
    "93": "93 - Special transactions and commodities not classified",
    "94": "94 - Animals and birds, live, not for food",
    "95": "95 - Coin (other than gold coin), not legal tender",
    "96": "96 - Coins and monetary gold",
    'I': 'Live animals; animal products (Chapters 01-05)',
     'II': 'Vegetable products (Chapters 06-14)',
     'III': 'Animal or vegetable fats and oils and their cleavage products; prepared edible fats; animal or vegetable waxes (Chapter 15)',
     'IV': 'Prepared foodstuffs; beverages, spirits and vinegar; tobacco and manufactured tobacco substitutes (Chapters 16-24)',
     'V': 'Mineral products (Chapters 25-27)',
     'VI': 'Products of the chemical or allied industries (Chapters 28-38)',
     'VII': 'Plastics and articles thereof; rubber and articles thereof (Chapters 39-40)',
     'VIII': 'Raw hides and skins, leather, furskins and articles thereof; saddlery and harness; travel goods, handbags and similar containers; articles of animal gut (other than silkworm gut) (Chapters 41-43)',
     'IX': 'Wood and articles of wood; wood charcoal; cork and articles of cork; manufactures of straw, of esparto or of other plaiting materials; basketware and wickerwork (Chapters 44-46)',
     'X': 'Pulp of wood or other fibrous cellulosic material; recovered (waste and scrap) paper or paperboard; paper and paperboard and articles thereof (Chapters 47-49)',
     'XI': 'Textiles and textile articles (Chapters 50-63)',
     'XII': 'Footwear, headgear, umbrellas, sun umbrellas, walking sticks, seat-sticks, whips, riding-crops and parts thereof; prepared feathers and down and articles made of feathers or of down; artificial flowers; articles of human hair (Chapters 64-67)',
     'XIII': 'Articles of stone, plaster, cement, asbestos, mica or similar materials; ceramic products; glass and glassware (Chapters 68-70)',
     'XIV': 'Natural or cultured pearls, precious or semi-precious stones, precious metals, metals clad with precious metal and articles thereof; imitation jewellery; coin (Chapter 71)',
     'XV': 'Base metals and articles of base metal (Chapters 72-83)',
     'XVI': 'Machinery and mechanical appliances; electrical equipment; parts thereof; sound recorders and reproducers, television image and sound recorders and reproducers, and parts and accessories of such articles (Chapters 84-85)',
     'XVII': 'Vehicles, aircraft, vessels and associated transport equipment (Chapters 86-89)',
     'XVIII': 'Optical, photographic, cinematographic, measuring, checking, precision, medical or surgical instruments and apparatus; clocks and watches; musical instruments; parts and accessories thereof (Chapters 90-92)',
     'XIX': 'Arms and ammunition; parts and accessories thereof (Chapter 93)',
     'XX': 'Miscellaneous manufactured articles (Chapters 94-96)',
     'XXI': 'Works of art, collectors’ pieces and antiques (Chapter 97)'
}


flow_labels = {
    "1": "Import",
    "2": "Export"
}

# ---------------------------
# Prepare base DataFrame
# ---------------------------
# Filter out 'commodity'
df_base = df_base[df_base['series'] != 'commodity'].copy()

# Prepare time column
df_base["time"] = df_base["year"].astype(str) + "-Q" + df_base["quarter"].astype(str)
df_base = df_base.sort_values(by=["year", "quarter"])
df_base["time"] = pd.Categorical(
    df_base["time"],
    ordered=True,
    categories=sorted(df_base["time"].unique(), key=lambda x: (int(x[:4]), int(x[-1])))
)

# ---------------------------
# Widgets
# ---------------------------
# Level dropdown (single selection)
level_dropdown = widgets.Dropdown(
    options=sorted(df_base['level'].unique()),
    value=sorted(df_base['level'].unique())[0],
    description='Level:'
)

# Series dropdown (multiple selection)
series_dropdown = widgets.SelectMultiple(
    options=[],  # will be populated dynamically
    description='Series:',
    rows=6
)

# Flow selection
flow_select = widgets.SelectMultiple(
    options=sorted(df_base['flow'].unique()),
    value=tuple(['2']),
    description='Flows:',
    rows=4
)

# Metrics selection
all_metrics = ['index', 'quarterly_change', 'year_on_year_change', 'share_total']
metrics_select = widgets.SelectMultiple(
    options=all_metrics,
    value=tuple(['index']),
    description='Metrics:',
    rows=len(all_metrics)
)

# Update series options based on selected level
def update_series_options(*args):
    selected_level = level_dropdown.value
    series_values = sorted(df_base[df_base['level'] == selected_level]['series'].unique())
    series_dropdown.options = series_values
    if series_values:
        series_dropdown.value = tuple(series_values[:1])  # default to first series

# Connect observer
level_dropdown.observe(update_series_options, names='value')
update_series_options()  # initialize series options

# ---------------------------
# Plotting function
# ---------------------------
def update_plot(level, series, flows, metrics):
    if not series or not flows or not metrics:
        print("Please select at least one series, flow, and metric.")
        return

    plt.figure(figsize=(16, 7))
    sns.set_theme(style="whitegrid")

    # Unique colors per series
    series_palette = sns.color_palette("tab10", n_colors=len(series))
    series_color_map = dict(zip(series, series_palette))
    styles = ['-', '--', '-.', ':']  # line styles per metric

    for i, metric in enumerate(metrics):
        style = styles[i % len(styles)]
        for s in series:
            for flow in flows:
                df_plot = df_base[
                    (df_base['level'] == level) &
                    (df_base['series'] == s) &
                    (df_base['flow'] == flow)
                ]
                if not df_plot.empty:
                    plt.plot(
                        df_plot['time'],
                        df_plot[metric],
                        label=f"{metric} ({SITC_labels.get(s, s)} - {flow_labels.get(flow, flow)})",
                        color=series_color_map[s],
                        linestyle=style,
                        marker='o'
                    )
                    # Highlight last point
                    last_point = df_plot.iloc[-1]
                    plt.text(
                        last_point['time'],
                        last_point[metric],
                        f"{metric} ({flow_labels.get(flow, flow)})",
                        fontsize=9,
                        horizontalalignment='left'
                    )

    plt.xticks(rotation=45)
    plt.xlabel("Time")
    plt.ylabel("Value")
    plt.title(f"Import and Export Price Index (XMPI) - Mozambique ({first_index_year}=100)")
    plt.legend(title="Metric (Series - Flow)", fontsize=9, title_fontsize=10)
    plt.tight_layout()
    plt.show()

# ---------------------------
# Interactive UI
# ---------------------------
widgets.interact(
    update_plot,
    level=level_dropdown,
    series=series_dropdown,
    flows=flow_select,
    metrics=metrics_select
)

# -





