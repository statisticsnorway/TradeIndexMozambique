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
index_chained_export = f'../data/index_export_chained.parquet'
index_chained_import = f'../data/index_import_chained.parquet'

index_chained_export = pd.read_parquet(index_chained_export)
index_chained_import = pd.read_parquet(index_chained_import)

# Append (concatenate) them
index_chained_all = pd.concat([index_chained_export, index_chained_import], ignore_index=True)

# -

# #### Calculate changes (%)
#
# - **Quarterly change**
# - **Year on year change**

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
# Calculate changes
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

df_base = df_base.drop(columns=['index_unchained'])


# +
import pandas as pd

# Correct flow selection with multiple selections per flow
flow_selection = for_publication

# Initialize empty DataFrame
df_filtered = pd.DataFrame(columns=df_base.columns)

# Loop over flows and selections
for flow, selections in flow_selection.items():
    for sel in selections:
        df_flow = df_base[
            (df_base['flow'] == flow) &
            (df_base['level'].isin(sel['levels'])) &
            (df_base['series'].isin(sel['series']))
        ].copy()
        df_filtered = pd.concat([df_filtered, df_flow], ignore_index=True)


df_filtered['flow'] = df_filtered['flow'].map({'1': 'Import', '2': 'Export'})

# 
SITC_labels = SITC_labels = {
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

df_filtered['series_name'] = df_filtered['series'].map(SITC_labels)

# Optionally combine with level for clarity
df_filtered['series_name'] = df_filtered['series_name'].fillna(df_filtered['series'])

# Preview
df_filtered



# +
XMPI = df_filtered.copy()

# Pivot multiple measures
XMPI_wide = XMPI.pivot_table(
    index=['flow', 'level', 'series', 'series_name'],   # rows
    columns='time',                       # columns
    values=['index']
)

# Swap levels so that time is the top level
XMPI_wide = XMPI_wide.swaplevel(axis=1)

# Sort columns by time
XMPI_publication = XMPI_wide.sort_index(axis=1, level=0)

XMPI_publication = XMPI_publication.round(2)

# Preview
XMPI_publication


# +
XMPI = df_filtered.copy()

# Pivot multiple measures
XMPI_wide = XMPI.pivot_table(
    index=['flow', 'level', 'series', 'series_name'],   # rows
    columns='time',                       # columns
    values=['quarterly_change']
)

# Swap levels so that time is the top level
XMPI_wide = XMPI_wide.swaplevel(axis=1)

# Sort columns by time
XMPI_quarterly_change = XMPI_wide.sort_index(axis=1, level=0)

XMPI_quarterly_change = XMPI_quarterly_change.round(2)

# Preview
XMPI_quarterly_change

# +
XMPI = df_filtered.copy()

# Pivot multiple measures
XMPI_wide = XMPI.pivot_table(
    index=['flow', 'level', 'series', 'series_name'],   # rows
    columns='time',                       # columns
    values=['year_on_year_change']
)

# Swap levels so that time is the top level
XMPI_wide = XMPI_wide.swaplevel(axis=1)

# Sort columns by time
XMPI_year_on_year_change = XMPI_wide.sort_index(axis=1, level=0)

XMPI_year_on_year_change = XMPI_year_on_year_change.round(2)

# Preview
XMPI_year_on_year_change

# +
import pandas as pd
import matplotlib.pyplot as plt

# Make sure directory exists
import os
os.makedirs('../publication', exist_ok=True)

# Suppose your wide DataFrame is df_wide
XMPI_publication = XMPI_publication.copy()  # your pivoted MultiIndex DF

# --------------------------
# Export to Excel
# --------------------------
excel_path = '../publication/XMPI_publication.xlsx'
XMPI_publication.to_excel(excel_path, merge_cells=True)
print(f"Saved Excel to: {excel_path}")

# --------------------------
# Export to PDF (table)
# --------------------------
pdf_path = '../publication/XMPI_publication.pdf'

# Create figure based on number of rows
fig_height = max(4, len(XMPI_publication) * 0.5)
fig, ax = plt.subplots(figsize=(16, fig_height))
ax.axis('off')

# Convert MultiIndex columns to strings for matplotlib table
columns_for_table = [" ".join(map(str, col)).strip() if isinstance(col, tuple) else col
                     for col in XMPI_publication.columns.values]

# Create table
table = ax.table(
    cellText=XMPI_publication.values,
    colLabels=columns_for_table,
    cellLoc='center',
    loc='center'
)

table.auto_set_font_size(False)
table.set_fontsize(9)
table.auto_set_column_width(col=list(range(len(XMPI_publication.columns))))

plt.tight_layout()
plt.savefig(pdf_path, bbox_inches='tight')
plt.close()
print(f"Saved PDF to: {pdf_path}")

# +
import pandas as pd
import matplotlib.pyplot as plt

# Make sure directory exists
import os
os.makedirs('../publication', exist_ok=True)

# Suppose your wide DataFrame is df_wide
XMPI_quarterly_change = XMPI_quarterly_change.copy()  # your pivoted MultiIndex DF

# --------------------------
# Export to Excel
# --------------------------
excel_path = '../publication/XMPI_quarterly_change.xlsx'
XMPI_quarterly_change.to_excel(excel_path, merge_cells=True)
print(f"Saved Excel to: {excel_path}")

# --------------------------
# Export to PDF (table)
# --------------------------
pdf_path = '../publication/XMPI_quarterly_change.pdf'

# Create figure based on number of rows
fig_height = max(4, len(XMPI_quarterly_change) * 0.5)
fig, ax = plt.subplots(figsize=(16, fig_height))
ax.axis('off')

# Convert MultiIndex columns to strings for matplotlib table
columns_for_table = [" ".join(map(str, col)).strip() if isinstance(col, tuple) else col
                     for col in XMPI_quarterly_change.columns.values]

# Create table
table = ax.table(
    cellText=XMPI_quarterly_change.values,
    colLabels=columns_for_table,
    cellLoc='center',
    loc='center'
)

table.auto_set_font_size(False)
table.set_fontsize(9)
table.auto_set_column_width(col=list(range(len(XMPI_quarterly_change.columns))))

plt.tight_layout()
plt.savefig(pdf_path, bbox_inches='tight')
plt.close()
print(f"Saved PDF to: {pdf_path}")


# +
import pandas as pd
import matplotlib.pyplot as plt

# Make sure directory exists
import os
os.makedirs('../publication', exist_ok=True)

# Suppose your wide DataFrame is df_wide
XMPI_year_on_year_change = XMPI_year_on_year_change.copy()  # your pivoted MultiIndex DF

# --------------------------
# Export to Excel
# --------------------------
excel_path = '../publication/XMPI_year_on_year_change.xlsx'
XMPI_year_on_year_change.to_excel(excel_path, merge_cells=True)
print(f"Saved Excel to: {excel_path}")

# --------------------------
# Export to PDF (table)
# --------------------------
pdf_path = '../publication/XMPI_year_on_year_change.pdf'

# Create figure based on number of rows
fig_height = max(4, len(XMPI_year_on_year_change) * 0.5)
fig, ax = plt.subplots(figsize=(16, fig_height))
ax.axis('off')

# Convert MultiIndex columns to strings for matplotlib table
columns_for_table = [" ".join(map(str, col)).strip() if isinstance(col, tuple) else col
                     for col in XMPI_year_on_year_change.columns.values]

# Create table
table = ax.table(
    cellText=XMPI_year_on_year_change.values,
    colLabels=columns_for_table,
    cellLoc='center',
    loc='center'
)

table.auto_set_font_size(False)
table.set_fontsize(9)
table.auto_set_column_width(col=list(range(len(XMPI_year_on_year_change.columns))))

plt.tight_layout()
plt.savefig(pdf_path, bbox_inches='tight')
plt.close()
print(f"Saved PDF to: {pdf_path}")


