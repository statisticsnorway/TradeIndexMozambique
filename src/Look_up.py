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

year = 2024
year_1 = year-1
quarter  = 4
flow = 'Export'

# # Datasets

# +
# Define file paths
file_paths = {
    "tradedata_year": f'../data/tradedata_{flow}_{year}.parquet',
    "tradedata_quarter": f'../data/{flow}_{year}_q{quarter}.parquet',
    "baseprice": f'../data/base_price{flow}_{year}.parquet',
    "index_chained": f'../data/index_{flow}_chained.parquet',
    "prices_baseyear": (f'../data/prices_baseyear_{flow}_{year_1}.parquet'),
    "labels": (f'../cat/SITC_label.parquet'),
    "index_unchained": (f'../data/index_unchained_{flow}_{year}.parquet'),
    "tradedata_month": (f'../data/tradedata_{flow}_{year}.parquet')
}

# Load each file if it exists
dataframes = {}

for key, path in file_paths.items():
    if os.path.exists(path):
        dataframes[key] = pd.read_parquet(path)
    else:
        print(f"File not found: {path}")

# Access the DataFrames like this:
tradedata_year = dataframes.get("tradedata_year")
tradedata_quarter = dataframes.get("tradedata_quarter")
baseprice = dataframes.get("baseprice")
index_chained = dataframes.get("index_chained")
prices_baseyear = dataframes.get("prices_baseyear")
label = dataframes.get("labels")
index_unchained = dataframes.get("index_unchained")
tradedata_month = dataframes.get("tradedata_month")
# -

# # Select dataset

df = tradedata_year

df2 = tradedata_quarter

df1 = index_unchained

sitccat = pd.read_parquet('../cat/commodity_sitc.parquet')
print(f'{sitccat.shape[0]} rows read from parquet file ../cat/commodity_sitc.parquet\n')
sitccat = sitccat.rename(columns={'comno': 'series'})
# Perform the merge
df1 = pd.merge(df1, sitccat, on='series', how='left', indicator=True)


# # Select commodity to look at:

comno = '76020000'
sitc1 = '0'

# # Look at Dataset for selected commoditity, year and quarter

look_at = df.loc[df['comno'] == comno]
show(look_at, maxBytes=0)

look_at = df2.loc[df2['comno'] == comno]
show(look_at, maxBytes=0)

look_at = df1.loc[df1['sitc1'] == sitc1]
show(look_at, maxBytes=0)

# # Look at Dataset for selected group, year and quarter

# +
sitc2 = '00'

section = 'V'
# -

look_at = df.loc[df['sitc2'] == sitc2]
show(look_at, maxBytes=0)

look_at = df.loc[df['section'] == section]
show(look_at, maxBytes=0)

# # Discriptiv statistics

# +
# Compute descriptive statistics for each column
stats_dict = {
    "value": look_at["value"].describe(),
    "weight": look_at["weight"].describe(),
    "price": look_at["price"].describe()
}

# Convert to DataFrame for a cleaner table format
stats_df = pd.DataFrame(stats_dict)

# Display the table
print(stats_df)

# -

# # Calculating price and price_cv with and without outliers 

# +
# Assuming the original dataframe is named 'df'
tradedata_with_outlier = look_at.copy()
tradedata_no_MAD = look_at[look_at['outlier_MAD'] == False].copy()
tradedata_no_sd = look_at[look_at['outlier_sd'] == False].copy()
tradedata_no_sd2 = look_at[look_at['outlier_sd2'] == False].copy()

# Define the aggregation variables
aggvars = ['year', 'flow', 'comno', 'quarter', 'month', 'section', 'chapter', 
           'sitc1', 'sitc2']

# Count total number of rows before aggregation
tradedata_with_outlier['n_transactions'] = len(tradedata_with_outlier)
tradedata_no_MAD['n_transactions'] = len(tradedata_no_MAD)
tradedata_no_sd['n_transactions'] = len(tradedata_no_sd)
tradedata_no_sd2['n_transactions'] = len(tradedata_no_sd2)

# Aggregation function
def aggregate_data(df):
    aggregated_df = df.groupby(aggvars, as_index=False).agg(
        weight=('weight', 'sum'),
        value=('value', 'sum'),
        n_transactions=('n_transactions', 'first')
    )
    aggregated_df['price'] = aggregated_df['value'] / aggregated_df['weight']
    return aggregated_df

# Apply aggregation to all datasets
tradedata_with_outlier_agg = aggregate_data(tradedata_with_outlier)
tradedata_no_MAD_agg = aggregate_data(tradedata_no_MAD)
tradedata_no_sd_agg = aggregate_data(tradedata_no_sd)
tradedata_no_sd2_agg = aggregate_data(tradedata_no_sd2)


# Helper function to calculate price_mean, price_sd, and price_cv within each dataset
def calculate_price_cv(df):
    df['price_mean3'] = df.groupby(['flow', 'comno'])['price'].transform('mean')
    df['price_sd3'] = df.groupby(['flow', 'comno'])['price'].transform('std')
    df['price_cv'] = (df['price_sd3'] / df['price_mean3']).fillna(0)  # Handle NaNs by filling with 0
    return df

# Function to aggregate data after calculating price_cv
def aggregate_and_calculate_price(df):
    #df['qrt'] = 1  # Assign a constant quarter value for simplicity
    
    aggregated_df = df.groupby(['year', 'flow', 'comno'], as_index=False).agg(
        value=('value', 'sum'),
        weight=('weight', 'sum')
        #n_transactions=('n_transactions', 'first')  # Assuming n_transactions does not vary
    )
    
    aggregated_df['price'] = aggregated_df['value'] / aggregated_df['weight']
    return aggregated_df[['comno', 'price']]

# List of datasets to process
datasets = [tradedata_with_outlier_agg, tradedata_no_MAD_agg, tradedata_no_sd_agg, tradedata_no_sd2_agg]
dataset_names = ['With outliers', 'No MAD', 'No SD', 'NO SD2']

consolidated_data = pd.DataFrame()
for i, dataset in enumerate(datasets):
    dataset = calculate_price_cv(dataset)
    aggregated_data = aggregate_and_calculate_price(dataset)
    
    # Merge the aggregated data with the calculated price_cv from the original dataset
    aggregated_data = aggregated_data.merge(
        dataset[['comno', 'price_cv']].drop_duplicates(), on='comno', how='left'
    )
    
    aggregated_data['Dataset'] = dataset_names[i]
    consolidated_data = pd.concat([consolidated_data, aggregated_data], ignore_index=True)

# Pivot the consolidated data and keep base_price and n_transactions without tags
price_comparison = consolidated_data.pivot_table(
    index='comno', 
    columns='Dataset', 
    values=['price', 'price_cv'],
    aggfunc='first'  # Ensures we only keep one instance of the value
)

# Flatten the MultiIndex columns for clarity
price_comparison.columns = [f'{col[0]}_{col[1]}' for col in price_comparison.columns]

# Aggregate base_price and n_transactions separately, keeping just one instance of each
base_data = consolidated_data[['comno']].drop_duplicates()

# Merge base data to include base_price and n_transactions in the comparison
price_comparison = price_comparison.merge(base_data, on='comno', how='left')

# Display the consolidated table
print(f"{flow.capitalize()} {year}. Comparison of Prices and Price CV with different outlier removal method:")
show(price_comparison, maxBytes=0)
# -

# # Index chained for selected commodity

last4 = index_chained.loc[(index_chained['year'] >= (year - 3)) & (index_chained['series'] == comno)]
display(pd.crosstab([last4['level'], last4['series']], 
                    columns=[last4['year'], last4['quarter']], 
                    values=last4['index_chained'], 
                    aggfunc='mean'))

# +
data = index_chained.loc[index_chained['series'] == comno]

data
# -

# # Vizualization for selected commodity

comno = '02071400'

# +
# Create DataFrame
data = index_chained.loc[index_chained['series'] == comno]


df = pd.DataFrame(data)

df = df.reset_index(drop=True)

# Create a unique time variable combining year and quarter
df["time"] = df["year"].astype(str) + "-Q" + df["quarter"].astype(str)

# Compute the quarterly percentage change
df["quarterly_change"] = df["index_chained"].pct_change(fill_method=None) * 100  # Convert to percentage

# Set figure size
plt.figure(figsize=(12, 5))

# Line plot for index_chained over time
plt.subplot(1, 2, 1)
sns.lineplot(x="time", y="index_chained", data=df, marker="o", linestyle="-", color="#3498DB")  # Modern blue
plt.xticks(rotation=45)
plt.title(f'HS {comno} - Index chained  - {flow}')
plt.xlabel("Time (Year-Quarter)")
plt.ylabel("Index Chained")

# Modern color palette for positive/negative bars
modern_green = "#4CAF50"  # Soft green
modern_red = "#E74C3C"  # Vibrant red

colors = [modern_green if change > 0 else modern_red for change in df["quarterly_change"]]

# Bar plot for quarterly change with modern colors
plt.subplot(1, 2, 2)
sns.barplot(x="time", y="quarterly_change", data=df, hue="time", palette=colors)
plt.legend().remove()
plt.axhline(0, color="gray", linestyle="--")  # Reference line at 0
plt.xticks(rotation=45)
plt.title(f'Quarterly Change for HS {comno} - {flow}')
plt.xlabel("Time (Year-Quarter)")
plt.ylabel("Quarterly % Change")

# Show plots
plt.tight_layout()
plt.show()
# -

# # Vizualization for selected series and level

# +
level = 'Sitc2'
# select Sitc1, Sitc2, Section, Total, Commoditiy

series = '00'

# +
# Filter data based on level and series
data = index_chained.loc[(index_chained['level'] == level) & (index_chained['series'] == series)]
df = pd.DataFrame(data).reset_index(drop=True)

# Create a unique time variable combining year and quarter
df["time"] = df["year"].astype(str) + "-Q" + df["quarter"].astype(str)

# Compute the quarterly percentage change
df["quarterly_change"] = df["index_chained"].pct_change(fill_method=None) * 100  # Convert to percentage

# Compute the quarterly percentage change
df["Y/Y_change"] = df["index_chained"].pct_change(4, fill_method=None) * 100  # Convert to percentage


# SITC2 series labels mapping
series_labels = {
    "0": "0 - Food and live animals",
    "1": "1 - Beverages and tobacco",
    "2": "2 - Crude materials, inedible, except fuels",
    "3": "3 - Mineral fuels, lubricants and related materials",
    "4": "4 - Animal and vegetable oils, fats and waxes",
    "5": "5 - Chemicals and related products n.e.s.",
    "6": "6 - Manufactured goods classified chiefly by material",
    "7": "7 - Machinery and transport equipment",
    "8": "8 - Miscellaneous manufactured articles",
    "9": "9 - Commodities and transactions","00": "00 - Live animals",
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

# Get the label for the selected series
series_label = series_labels.get(series, f"SITC {series}")  # Default to series if not found

# Set figure size
plt.figure(figsize=(12, 5))

# First plot: Index Chained over time
plt.subplot(1, 2, 1)
sns.lineplot(x="time", y="index_chained", data=df, marker="o", linestyle="-", color="#3498DB")  # Blue color
plt.xticks(rotation=45)
plt.xlabel("Time (Year-Quarter)")
plt.ylabel("Index Chained")
plt.title(f'{series_label}\nIndex Chained - {flow}')  # Title split for readability

# Modern color palette for positive/negative bars
modern_green = "#4CAF50"  # Soft green
modern_red = "#E74C3C"  # Vibrant red

colors = [modern_green if change > 0 else modern_red for change in df["quarterly_change"]]

# Second plot: Quarterly percentage change
plt.subplot(1, 2, 2)
sns.barplot(x="time", y="quarterly_change", data=df, hue="time", palette=colors)
plt.legend().remove()
plt.axhline(0, color="gray", linestyle="--")  # Reference line at 0
plt.xticks(rotation=45)
plt.xlabel("Time (Year-Quarter)")
plt.ylabel("Quarterly % Change")
plt.title(f'{series_label}\nQuarterly Change - {flow}')


# Show plots
plt.tight_layout()
plt.show()

# -

index_chained

# +
index_chained_export = f'../data/index_export_chained.parquet'
index_chained_import = f'../data/index_import_chained.parquet'

index_chained_export = pd.read_parquet(index_chained_export)
index_chained_import = pd.read_parquet(index_chained_import)

# Append (concatenate) them
index_chained_all = pd.concat([index_chained_export, index_chained_import], ignore_index=True)
index_chained_all.dtypes

# -

sitccat = pd.read_parquet('../cat/commodity_sitc.parquet')
print(f'{sitccat.shape[0]} rows read from parquet file ../cat/commodity_sitc.parquet\n')
sitccat = sitccat.rename(columns={'comno': 'series'})


# +

# Perform the merge
index_chained_all = pd.merge(index_chained_all, sitccat, on='series', how='left', indicator=True)

index_chained_all
# -


# Option 1: Replace the flow column with text labels
index_chained_all['flow'] = index_chained_all['flow'].replace({"1": 'Export', "2": 'Import'})

index_chained_all

# +
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import ipywidgets as widgets
from IPython.display import display, clear_output

# Prepare base DataFrame
df_base = index_chained_all.copy()
df_base["time"] = df_base["year"].astype(str) + "-Q" + df_base["quarter"].astype(str)

# Sorter og sett riktig kategorirekkefølge på 'time'
df_base = df_base.sort_values(by=["year", "quarter"])
df_base["time"] = pd.Categorical(
    df_base["time"],
    ordered=True,
    categories=sorted(df_base["time"].unique(), key=lambda x: (int(x[:4]), int(x[-1])))
)

# Widgets
level_dropdown = widgets.Dropdown(
    options=sorted(df_base['level'].unique()),
    description='Level:'
)

# Use Combobox for searchable dropdown
series_dropdown = widgets.Combobox(
    options=[],  # Will be populated based on selected level
    description='Series:',
    ensure_option=True,
    placeholder='Type to search...'
)

flow_select = widgets.SelectMultiple(
    options=sorted(df_base['flow'].unique()),
    value=['Export'],
    description='Flows:',
    rows=4
)

# SITC2 series labels mapping (truncated for brevity in example)
series_labels = {
    "0": "0 - Food and live animals",
    "1": "1 - Beverages and tobacco",
    "2": "2 - Crude materials, inedible, except fuels",
    "3": "3 - Mineral fuels, lubricants and related materials",
    "4": "4 - Animal and vegetable oils, fats and waxes",
    "5": "5 - Chemicals and related products n.e.s.",
    "6": "6 - Manufactured goods classified chiefly by material",
    "7": "7 - Machinery and transport equipment",
    "8": "8 - Miscellaneous manufactured articles",
    "9": "9 - Commodities and transactions","00": "00 - Live animals",
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

# Update series options based on level
def update_series_options(*args):
    selected_level = level_dropdown.value
    series_values = sorted(df_base[df_base['level'] == selected_level]['series'].unique())
    series_dropdown.options = series_values
    if series_values:
        series_dropdown.value = series_values[0]

# Trigger update on level change
level_dropdown.observe(update_series_options, names='value')
update_series_options()  # Initial trigger

# Plotting function
def update_plot(level, series, flows):
    df = df_base[
        (df_base['level'] == level) &
        (df_base['series'] == series) &
        (df_base['flow'].isin(flows))
    ]

    plt.figure(figsize=(16, 7))

    if df.empty:
        plt.text(0.5, 0.5, 'No data for this combination.', ha='center', va='center')
        plt.axis('off')
        plt.show()
        return

    ax = sns.lineplot(
        data=df,
        x="time",
        y="index_chained",
        hue="flow",
        style="series",
        markers=True,
        dashes=True,
        errorbar=None
    )

    for (series, flow), group in df.groupby(['series', 'flow']):
        if not group.empty:
            last_point = group.iloc[-1]
            label = f"{series_labels.get(series, series)} ({flow})"
            plt.text(
                last_point["time"],
                last_point["index_chained"],
                label,
                horizontalalignment='left',
                size='medium',
                color='black',
                weight='semibold'
            )

    # Custom legend
    series_unique = df['series'].unique()
    flow_unique = df['flow'].unique()

    palette = sns.color_palette(n_colors=len(flow_unique))
    flow_color_map = dict(zip(sorted(flow_unique), palette))
    series_styles = ['-', '--', '-.', ':']
    series_style_map = dict(zip(sorted(series_unique), series_styles))

    legend_handles = []
    for flow in sorted(flow_unique):
        for series in sorted(series_unique):
            color = flow_color_map[flow]
            linestyle = series_style_map.get(series, '-')
            line = mlines.Line2D(
                [], [], color=color, marker='o', markersize=6,
                linestyle=linestyle,
                label=f"{series_labels.get(series, series)} ({flow})"
            )
            legend_handles.append(line)

    plt.legend(handles=legend_handles, title="Series (Flow)", loc='upper left')
    plt.title("Export and Import Price Index - Mozambique")
    plt.xlabel("Time")
    plt.ylabel("Index (Chained)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# Interactive UI
widgets.interact(
    update_plot,
    level=level_dropdown,
    series=series_dropdown,
    flows=flow_select
)

# -










