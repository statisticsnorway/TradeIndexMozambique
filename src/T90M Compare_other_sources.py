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
index_chained_export = f'../data/index_Export_chained.parquet'
index_chained_import = f'../data/index_Import_chained.parquet'

index_chained_export = pd.read_parquet(index_chained_export)
index_chained_import = pd.read_parquet(index_chained_import)

# Append (concatenate) them
index_chained_all = pd.concat([index_chained_export, index_chained_import], ignore_index=True)

# -

index_chained_all = index_chained_all[index_chained_all['year'] <= year]


donor = pd.read_csv(f'../cat/compare_other_source.csv', sep=';')

# +
# Assuming df is your dataframe
df_long = donor.melt(id_vars=["flow", "source", "comno"], 
                  var_name="Period", 
                  value_name="price")  # rename the values column

# Extract year and quarter
df_long["year"] = df_long["Period"].str[:4].astype(int)
df_long["quarter"] = df_long["Period"].str[4:6].astype(int)  # last 2 digits

# Ensure comno is string and price is float
df_long["comno"] = df_long["comno"].astype(str)
df_long["price"] = df_long["price"].str.replace(",", ".").astype(float)

df_long['level'] = 'donor'
df_long['series'] = df_long['comno']
df_long['index_unchained'] = df_long['price']

# Drop  columns
donor = df_long.drop(columns=['price', 'comno', 'source', 'Period'])

# +
# Create a temporary dataframe with only 2022 for mean calculation
donor_2022 = donor[donor['year'] == first_index_year]

# Compute the mean per group based on 2022 only
index_mean = donor_2022.groupby(['flow', 'series', 'level'])['index_unchained'].mean().reset_index()
index_mean.rename(columns={'index_unchained': 'index_mean'}, inplace=True)

# Merge the 2022 mean back to the full donor dataset
donor_chained = donor.merge(index_mean, on=['flow', 'series', 'level'], how='left')

# Compute the chained index
donor_chained['index_chained'] = donor_chained['index_unchained'] * 100 / donor_chained['index_mean']

# Optional cleanup
donor_chained.drop(columns='index_mean', inplace=True)
donor_chained['year'] = donor_chained['year'].astype(int)
donor_chained['quarter'] = donor_chained['quarter'].astype(int)

donor_chained = donor_chained.sort_values(
    by=["series", "year", "quarter"]
).reset_index(drop=True)
# -
index_chained_all = pd.concat([index_chained_all, donor_chained], ignore_index=True)

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
# -

# #### Filter dataset --> look only at total and sitc

# +
#df_base = df_base[df_base["level"] != 'Commodity']
#df_base = df_base[df_base["level"] != 'special_serie']
# -

# # Plot

# +
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
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
    "96": "96 - Coins and monetary gold"
}

flow_labels = {
    "1": "Import",
    "2": "Export"
}


# ---------------------------
# Clean and prepare dataset
# ---------------------------
# Drop unwanted series
#df_base = df_base[df_base['series'] != 'commodity'].copy()

# Drop exact duplicates on series/flow/year/quarter
df_base = df_base.drop_duplicates(subset=['series','flow','year','quarter'])

# Keep only rows with valid year and quarter
mask = df_base['year'].notna() & df_base['quarter'].notna()
df_base = df_base[mask].copy()

# Build period column
df_base['period'] = pd.PeriodIndex(
    year=df_base['year'].astype(int),
    quarter=df_base['quarter'].astype(int),
    freq='Q'
)

# Ensure full period coverage for each series-flow combination
full_periods = pd.period_range(df_base['period'].min(), df_base['period'].max(), freq='Q')
series_flow = df_base[['series','flow']].drop_duplicates()
full_index = series_flow.assign(key=1).merge(
    pd.DataFrame({'period': full_periods, 'key':1}),
    on='key'
).drop('key', axis=1)

# Merge back to fill missing periods
df_base = full_index.merge(df_base, on=['series','flow','period'], how='left')

# Rebuild year and quarter from period
df_base['year'] = df_base['period'].dt.year
df_base['quarter'] = df_base['period'].dt.quarter

# Rebuild time label for plotting
df_base = df_base.sort_values(['series','flow','period']).reset_index(drop=True)
df_base['time'] = df_base['period'].astype(str).str.replace("Q","-Q")
df_base['time'] = pd.Categorical(
    df_base['time'],
    ordered=True,
    categories=[str(p).replace("Q","-Q") for p in full_periods]
)

# ---------------------------
# Widgets
# ---------------------------
series_select = widgets.SelectMultiple(
    options=sorted(df_base['series'].unique()),
    value=(sorted(df_base['series'].unique())[0],),
    description='Series:',
    rows=10
)

flow_select = widgets.SelectMultiple(
    options=sorted(df_base['flow'].unique()),
    value=(),
    description='Flows:',
    rows=6
)

all_metrics = ['index', 'quarterly_change', 'year_on_year_change', 'share_total']
metrics_select = widgets.SelectMultiple(
    options=all_metrics,
    value=('index',),
    description='Metrics:',
    rows=len(all_metrics)
)

# ---------------------------
# Plotting function
# ---------------------------
def update_plot(series, flows, metrics):
    if not series or not flows or not metrics:
        print("Please select at least one series, flow, and metric.")
        return

    plt.figure(figsize=(16, 7))
    sns.set_theme(style="whitegrid")

    # Color palette per series
    series_palette = sns.color_palette("tab10", n_colors=len(series))
    series_color_map = dict(zip(series, series_palette))

    # Line styles per metric
    styles = ['-', '--', '-.', ':']

    for i, metric in enumerate(metrics):
        style = styles[i % len(styles)]
        for s in series:
            for flow in flows:
                df_plot = df_base[
                    (df_base['series'] == s) &
                    (df_base['flow'] == flow)
                ]
                if not df_plot.empty:
                    plt.plot(
                        df_plot['time'],
                        df_plot[metric],
                        label=f"{metric} ({SITC_labels.get(str(s), s)} - {flow_labels.get(str(flow), flow)})",
                        color=series_color_map[s],
                        linestyle=style,
                        marker='o'
                    )
                    # Highlight last non-NaN point
                    last_point = df_plot.dropna(subset=[metric]).iloc[-1]
                    plt.text(
                        last_point['time'],
                        last_point[metric],
                        f"{metric} ({flow_labels.get(str(flow), flow)})",
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
    series=series_select,
    flows=flow_select,
    metrics=metrics_select
)
# -




