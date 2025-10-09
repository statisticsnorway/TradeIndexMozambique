# +
import pandas as pd
import numpy as np
import json
from pathlib import Path
from itables import init_notebook_mode, show
import matplotlib.pyplot as plt
import seaborn as sns
#pd.set_option('display.float_format',  '{:18,.0}'.format)
pd.set_option('display.float_format', lambda x: f'{x:15,.0f}' if abs(x)>1e5 else f'{x:15.2f}')
import ipywidgets as widgets
from IPython.display import display


year = 2021
quarter = 1
flow = 'Export'
selected_outlier= 'outlier_sd'

import itables

# Initialize interactive display mode
itables.init_notebook_mode(all_interactive=True)
# -

data_dir = Path('../check')
external_source = pd.concat(
    pd.read_parquet(parquet_file)
    for parquet_file in data_dir.glob(f'external_source_{flow}*.parquet')
)
#tradedata.to_parquet(f'../data/{flow}_{year}.parquet')
print(f'{external_source.shape[0]} rows read from parquet files for {flow}\n')

data_dir = Path('../check')
external_source1 = pd.concat(
    pd.read_parquet(parquet_file)
    for parquet_file in data_dir.glob(f'check_{flow}*.parquet')
)
#tradedata.to_parquet(f'../data/{flow}_{year}.parquet')
print(f'{external_source.shape[0]} rows read from parquet files for {flow}\n')

aggregate_df = external_source1.groupby('comno', as_index=False)['value'].sum()
aggregate_df.rename(columns={'value': 'total_value'}, inplace=True)


aggregate_df

show(external_source, maxBytes=0)

external_source = external_source[
    external_source['ref'].notna()]

merged_df = external_source.merge(aggregate_df, on='comno', how='left')

t_section = merged_df.copy()

# +
# COMPUTE PRICE PER TRANSACTION
t_section['price'] = t_section['value'] / t_section['weight']

# COMPUTE mean, median and standard deviation per HS per quarter
df_agg = t_section.groupby(['flow', 'year', 'comno', 'quarter'], as_index=False).agg({
    'price': ['mean', 'median', 'std']
})

# Rename the resulting columns for clarity
df_agg.columns = ['flow', 'year', 'comno', 'quarter', 'price_mean', 'price_median', 'price_std']

# Round all price-related columns to 2 decimals
df_agg = df_agg.round({'price_mean': 2, 'price_median': 2, 'price_std': 2})

# Merge the results back into the original DataFrame
t_section = pd.merge(t_section, df_agg, on=['flow', 'year', 'comno', 'quarter'], how='left')

# Also round the transaction-level price if needed
t_section['price'] = t_section['price'].round(2)

t_section

# -

outlier_sd = 2

# +
t_section['z_score'] = (t_section['price'] - t_section['price_mean']) / t_section['price_std']

def classify_outlier_SD(row):
    return abs(row['z_score']) > outlier_sd

# Apply the function to each row in the DataFrame t_section
t_section['outlier_sd'] = t_section.apply(classify_outlier_SD, axis=1)

# +

# Check if column exists in t_section
if selected_outlier not in t_section.columns:
    raise ValueError(f"Column '{selected_outlier}' not found in t_section")

# Crosstab of frequencies
crosstab2 = pd.crosstab(index=t_section[selected_outlier], columns='Count', margins=True)

# Calculate relative percentages
crosstab2['Percentage (%)'] = ((crosstab2['Count'] / crosstab2.loc['All', 'Count']) * 100).map('{:.1f}'.format)

# Keep only 'Count' and 'Percentage (%)' columns
crosstab2 = crosstab2[['Count', 'Percentage (%)']]

# Print formatted output
print(f'{flow.capitalize()}. Frequencies of transactions tagged as outlier with {selected_outlier} above the limit for {year} quarter {quarter}')
display(crosstab2)

# -

show(t_section, maxBytes=0)

# + active=""
# t_section = t_section.loc[t_section['comno'] == '27160000'].copy()

# +
# Round the numeric columns you care about
t_section = t_section.round({
    'price': 2,
    'price_mean': 2,
    'price_median': 2,
    'price_std': 2,
    'z_score': 2
})

# Export to CSV: semicolon as separator, comma as decimal, Excel-friendly encoding
t_section.to_csv(
    '../check/external_source_new.csv',
    sep=';', 
    index=False,
    decimal=',',         # use comma for decimals
    encoding='utf-8-sig' # makes Excel interpret characters correctly
)

# -

aggvars = ['year', 'flow', 'comno', 'quarter', 'month']
tradedata_month = t_section.groupby(aggvars, as_index=False).agg(
    weight=('weight', 'sum'),
    value=('value', 'sum')
)
tradedata_month['price'] = tradedata_month['value'] / tradedata_month['weight']

tradedata_month

tradedata_month['no_of_months'] = tradedata_month.groupby(['flow', 'year', 'comno'])['month'].transform('count')
for stat in ['max', 'min', 'median', 'mean']:
    tradedata_month[f'price_{stat}'] = tradedata_month.groupby(['flow', 'year', 'comno'])['price'].transform(stat)
tradedata_month['price_sd'] = tradedata_month.groupby(['flow', 'year', 'comno'])['price'].transform('std')
tradedata_month['price_cv'] = tradedata_month['price_sd'] / tradedata_month['price_mean']

tradedata_month = tradedata_month.merge(aggregate_df, on='comno', how='left')

# +
# Round the numeric columns you care about
tradedata_month = tradedata_month.round({
    'price': 2,
    'price_mean': 2,
    'price_median': 2,
    'price_std': 2,
    'z_score': 2
})

# Export to CSV: semicolon as separator, comma as decimal, Excel-friendly encoding
tradedata_month.to_csv(
    '../check/external_source_month.csv',
    sep=';', 
    index=False,
    decimal=',',         # use comma for decimals
    encoding='utf-8-sig' # makes Excel interpret characters correctly
)

# -


