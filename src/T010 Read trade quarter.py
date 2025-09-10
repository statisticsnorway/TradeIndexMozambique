# +
# Read csv file from external trade and add some new columns
# -

# ## Read csv file
# We use the pandas read_csv to import the file to a Python pandas dataframe. With the dtype parameter we decide the column types.

# + active=""
# import pandas as pd
# import numpy as np
# import json
# from pathlib import Path
# from itables import init_notebook_mode, show
# import matplotlib.pyplot as plt
# import seaborn as sns
# #pd.set_option('display.float_format',  '{:18,.0}'.format)
# pd.set_option('display.float_format', lambda x: f'{x:15,.0f}' if abs(x)>1e5 else f'{x:15.2f}')
# import itables
# # Initialize interactive display mode
# itables.init_notebook_mode(all_interactive=True)
#
#
# year = 2025
# quarter = 2
# flow = 'Import'

# +
dtyp = {
    'flow': 'object',
    'year': 'object',
    'month': 'object',
    'comno': 'object',
    'country': 'object',
    'weight': 'float64',
    'quantity': 'float64',
    'unit': 'object',
    'value': 'float64',
    'valUSD': 'float64',
    'itemid': 'object',
    'exporterNUIT': 'object',
    'ref': 'object',
    'ItemID': 'object'
}

xmpi_names = ['flow', 
              'year',
              'month',
              'comno',
              'country',
              'weight',
              'quantity',
              'unit',
              'value',
              'valUSD',
              'itemid',
              'exporterNUIT',
              'ref',
              'ItemID'
]


# -

def read_trade_data(path, prefix, flow, year, quarter, suffix):
    full_path = f'{path}{prefix}{flow} - {year}_XPMI_Q{quarter}.{suffix}'

    # Read tab-delimited file with headers from file
    trade_data = pd.read_csv(
        full_path,
        sep=',',
        dtype=dtyp,
        na_values={'.', ' .'},
        encoding='latin1',
        low_memory=False
    )

    # Convert 'flow' to numeric representation
    trade_data['flow'] = trade_data['flow'].map({'E': '1', 'I': '2'})  # or keep 'E'/'I' if preferred

    # Convert month to numeric safely
    trade_data['month'] = pd.to_numeric(trade_data['month'], errors='coerce')

    # Compute quarter
    trade_data['quarter'] = np.where(
        trade_data['month'].notna(),
        (((trade_data['month'] - 1) // 3) + 1).astype('Int64').astype(str),
        np.nan
    )

    print(f"{trade_data.shape[0]} rows read from: {full_path}")
    print("Sample rows:\n", trade_data.head())
    print("Unique quarters:", trade_data['quarter'].dropna().unique())

    return trade_data


tradedata = read_trade_data(path='../data/',
            prefix='',
            flow=flow,
            year=year,
            quarter=quarter,
            suffix='csv' )
tradedata


# ## Read parquet files
# Parquet files with correspondances to sitc and section

sitccat = pd.read_parquet('../cat/commodity_sitc.parquet')
print(f'{sitccat.shape[0]} rows read from parquet file ../cat/commodity_sitc.parquet\n')
sectioncat = pd.read_parquet('../cat/chapter_section.parquet')
print(f'{sectioncat.shape[0]} rows read from parquet file ../cat/sectioncat.parquet\n')

# ## Merge trade data with sitc catalog
# We add sitc and sitc2 from the correspondance table

# +
# Perform the merge
t_sitc = pd.merge(tradedata, sitccat, on='comno', how='left', indicator=True)

# Display the result of the merge
print(f'Result of merge with SITC catalog for {flow}, for {year}q{quarter}:')
display(pd.crosstab(t_sitc['_merge'], columns='Frequency', margins=True))

# Check if there are any "left_only" entries
left_only_data = t_sitc.loc[t_sitc['_merge'] == 'left_only']
if not left_only_data.empty:
    print(f'List of commodity numbers that do not have SITC codes for {flow}, for {year}q{quarter}:')
    
    # Crosstab for the 'left_only' entries
    display(pd.crosstab(left_only_data['comno'], columns='Frequency'))
else:
    print(f"No missing SITC codes for {flow}, for {year}q{quarter}.")

# Clean up by dropping the '_merge' column
t_sitc.drop(columns='_merge', inplace=True)

# -

# ## Merge trade data with chapter catalog
# We add section from the correspondance table

# + active=""
# t_sitc['chapter'] = t_sitc['comno'].str[0:2]
# t_section = pd.merge(t_sitc, sectioncat, on='chapter', how='left', indicator=True)
# print(f'Result of merge with chapter catalog for {flow}, for {year}q{quarter}:')
# display(pd.crosstab(t_section['_merge'], columns='Frequency', margins=True))
# if len(t_section.loc[t_section['_merge'] == 'left_only']) > 0:
#     print(f'List of chapters that do not have section code for {flow}, for {year}q{quarter}:')
#     display(pd.crosstab(t_section.loc[t_section['_merge'] == 'left_only', 'chapter'], columns='Frequency', margins=True))
# t_section.drop(columns='_merge', inplace=True)

# +
# Extract 'chapter' from the first two characters of 'comno'
t_sitc['chapter'] = t_sitc['comno'].str[0:2]

# Perform the merge with section catalog
t_section = pd.merge(t_sitc, sectioncat, on='chapter', how='left', indicator=True)

# Display the result of the merge with chapter catalog
print(f'Result of merge with chapter catalog for {flow}, for {year}q{quarter}:')
display(pd.crosstab(t_section['_merge'], columns='Frequency', margins=True))

# Check if there are any "left_only" entries
left_only_chapters = t_section.loc[t_section['_merge'] == 'left_only']
if not left_only_chapters.empty:
    print(f'List of chapters that do not have section code for {flow}, for {year}q{quarter}:')
    
    # Crosstab for the 'left_only' chapters
    display(pd.crosstab(left_only_chapters['chapter'], columns='Frequency'))
else:
    print(f"No missing section codes for {flow}, for {year}q{quarter}.")

# Clean up by dropping the '_merge' column
t_section.drop(columns='_merge', inplace=True)

t_section.columns = t_section.columns.str.lower()
# -

# ## Check if month is missing

print('rows with NaN in month column: ',t_section['month'].isna().sum())  # This will show how many NaN values are present


# ## print number of rows that have 0 in weight or value

# +
rows_with_zero = t_section[(t_section['weight'] == 0) | (t_section['value'] == 0)]
print("Number of rows with 0 in weight or value:", len(rows_with_zero))

#t_section['weight'] = np.where(t_section['weight'] == 0, 1, t_section['weight'])
# -

# ## Choose whether to use weight or quantity for the UV-weight

use_quantity = pd.read_excel('../cat/use_quantity.xlsx', dtype=str)
use_quantity_list = use_quantity['use_quantity'].tolist()

t_section['weight'] = np.where(t_section['comno'].isin(use_quantity_list), t_section['quantity'], t_section['weight'])

# Count how many rows in t_section['some_column'] are in use_quantity_list
match_count = t_section['comno'].isin(use_quantity_list).sum()
print(f"Number of matching rows: {match_count}")


# ## Save as parquet
# The quarter file is save as a parquet file

t_section.to_parquet(f'../data/{flow}_{year}q{quarter}.parquet')
print(f'\nNOTE: Parquet file ../data/{flow}_{year}q{quarter}.parquet written with {t_section.shape[0]} rows and {t_section.shape[1]} columns\n')




