# # Read csv file from external trade and add some new columns

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
# year = 2021
# quarter = 1
# flow = 'import'

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

print()
print(f"\n===Input data for {flow} {year}-Q{quarter}===")
print()


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
    trade_data['flow'] = trade_data['flow'].map({'I': '1', 'E': '2'})  # or keep 'E'/'I' if preferred

    # Convert month to numeric safely
    trade_data['month'] = pd.to_numeric(trade_data['month'], errors='coerce')

    # Compute quarter
    trade_data['quarter'] = np.where(
        trade_data['month'].notna(),
        (((trade_data['month'] - 1) // 3) + 1).astype('Int64').astype(str),
        np.nan
    )

    print(f"{trade_data.shape[0]} rows read from: {full_path}")
    #print("Sample rows:\n", trade_data.head())
    print("Unique quarters:", trade_data['quarter'].dropna().unique())

    return trade_data


tradedata = read_trade_data(path='../data/',
            prefix='',
            flow=flow,
            year=year,
            quarter=quarter,
            suffix='csv' )
tradedata

# +
# Remove rows where all columns are NaN
tradedata = tradedata.dropna(how='all')

# Optional: reset index after dropping
tradedata.reset_index(drop=True, inplace=True)

# Check how many rows remain
print(f"Number of rows after removing all-NaN rows: {len(tradedata)}")

# -

# ## Read parquet files
# Parquet files with correspondances to sitc and section

sitccat = pd.read_parquet('../cat/commodity_sitc.parquet')
print(f'{sitccat.shape[0]} rows read from parquet file ../cat/commodity_sitc.parquet\n')
isiccat = pd.read_parquet('../cat/commodity_isic.parquet')
print(f'{sitccat.shape[0]} rows read from parquet file ../cat/commodity_isic.parquet\n')
sectioncat = pd.read_parquet('../cat/chapter_section.parquet')
print(f'{sectioncat.shape[0]} rows read from parquet file ../cat/sectioncat.parquet\n')
print("\n" + "="*80)
print()

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
    print("\n" + "="*80)

# Clean up by dropping the '_merge' column
t_sitc.drop(columns='_merge', inplace=True)

# -

# ## Merge trade data with ISIC catalog
# We add ISIC levels from the correspondance table

# + active=""
# # Perform the merge with section catalog
# t_isic = pd.merge(t_sitc, isiccat, on='comno', how='left', indicator=True)
#
# # Display the result of the merge with chapter catalog
# print()
# print(f'Result of merge with ISIC catalog for {flow}, for {year}q{quarter}:')
# display(pd.crosstab(t_isic['_merge'], columns='Frequency', margins=True))
#
# # Check if there are any "left_only" entries
# left_only_isic = t_isic.loc[t_isic['_merge'] == 'left_only']
# if not left_only_isic.empty:
#     print(f'List of  commodity numbers that do not have ISIC code for {flow}, for {year}q{quarter}:')
#     
#     # Crosstab for the 'left_only' entries
#     display(pd.crosstab(left_only_isic['comno'], columns='Frequency'))
# else:
#     print(f"No missing ISIC codes for {flow}, for {year}q{quarter}.")
#     print("\n" + "="*80)
# # Clean up by dropping the '_merge' column
# t_isic.drop(columns='_merge', inplace=True)
#
# -

# ## Merge trade data with chapter catalog
# We add section from the correspondance table

# +
# Extract 'chapter' from the first two characters of 'comno'
t_sitc['chapter'] = t_sitc['comno'].str[0:2]

# Extract 'HS6' from the first two characters of 'comno'
t_sitc['hs6'] = t_sitc['comno'].str[0:6]

# Perform the merge with section catalog
t_section = pd.merge(t_sitc, sectioncat, on='chapter', how='left', indicator=True)

# Display the result of the merge with chapter catalog
print()
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
    print("\n" + "="*80)
# Clean up by dropping the '_merge' column
t_section.drop(columns='_merge', inplace=True)

# -

# ## Check if month is missing

# +
# Count rows with NaN in the 'month' column
num_nan_month = t_section['month'].isna().sum()

# Print nicely
print("\n" + "="*80)
print("\n=== Missing month values ===")
print(f"Number of rows with NaN in the 'month' column: {num_nan_month}")
print("============================\n")
print()


# -


# ## Choose whether to use weight or quantity for the UV-weight

use_quantity = pd.read_excel('../cat/Commodities_use_quantity.xlsx', dtype=str)
use_quantity_list = use_quantity['comno'].tolist()

# ### Check if chosen commodities to use quantity instead of weight is consistent.

# +
# Condition to check if quantity is 0 or unit is NaN (kg)
mask = (
    t_section['comno'].isin(use_quantity_list)
) & (
    (t_section['unit'].isna()) | (t_section['quantity'] == 0)
)

# Get rows with issue
rows_with_issue = t_section.loc[mask]

# Get unique comno where condition occurs
commodities_with_issue = rows_with_issue['comno'].unique()

# Count number of rows per comno, sorted by descending count
counts_per_comno = (
    rows_with_issue.groupby('comno')
    .size()
    .reset_index(name='rows_quantity_0')
    .sort_values(by='rows_quantity_0', ascending=False)
)

# Print with spacing for readability
print("\n=== Commodities with issue ===")
print("Commodities (comno) where we use quantity instead of weight but quantity is zero or unit is NaN:\n")
print(commodities_with_issue)
print("\nTotal number of commodities with issue:", len(commodities_with_issue))
print(f"\nNumber of rows per comno with issue can be found in csv : ../data/commodities_issue_quantity_{year}Q{quarter}.csv")
counts_per_comno.to_csv(f'../data/commodities_issue_quantity_{year}Q{quarter}.csv', index=False)
print('\nEvaluate commodities in use_quantity: ../cat/use_quantity.xlsx')
print("\n" + "="*80)
print()
# -


t_section['weight'] = np.where(t_section['comno'].isin(use_quantity_list), t_section['quantity'], t_section['weight'])

# ### Print number of rows that have 0 in weight or value

# +
# Select rows where weight or value is 0
rows_with_zero = t_section[(t_section['weight'] == 0)]

# Print with spacing for readability
print("\n=== Transactions with zero in weight) ===")
print("Transactions where weight (after using quantity for some commodities) is 0:\n")
print("\nTotal number of such transactions:", len(rows_with_zero))
print("\n" + "="*80)
print()


# +
# Select rows where weight or value is 0
rows_with_zero = t_section[(t_section['value'] == 0)]

# Print with spacing for readability
print("\n=== Transactions with zero values ===")
print("Transactions where value is 0:\n")
print("\nTotal number of such transactions:", len(rows_with_zero))
print("\n" + "="*80)
print()

# +
import pandas as pd

# --- Clean ref ---
ref_orig = t_section['ref']
ref_str = ref_orig.fillna('').astype(str).str.strip()

# --- Define external criteria ---
is_missing = ref_orig.isna()
starts_99 = ref_str.str.startswith('99', na=False)
contains_x = ref_str.str.contains('x', case=False, na=False)

external_mask = is_missing | starts_99 | contains_x

# --- Define exceptions ---
exceptions = {'27160000', '27111100'}
comno_str = t_section['comno'].astype(str)

# --- Build keep mask ---
keep_mask = (
    # Flow 2
    ((t_section['flow'] == '2') & (
        (~external_mask & ~comno_str.isin(exceptions)) |  # normal rows
        (starts_99 & comno_str.isin(exceptions))         # exceptions starting with 99
    )) |
    # Flow != 2 -> apply external filter to all rows
    ((t_section['flow'] != '2') & (~external_mask))
)

# --- Apply filter ---
t_section_filtered = t_section[keep_mask].copy()

# --- Reporting ---
before = t_section.groupby('comno').size().rename('rows_before')
after = t_section_filtered.groupby('comno').size().rename('rows_after')

report = before.to_frame().join(after, how='left').fillna(0)
report['rows_after'] = report['rows_after'].astype(int)
report['rows_removed'] = report['rows_before'] - report['rows_after']


print("\n=== Transactions with external source removed===")
# Show only comno where rows were removed (top 20)
report_external = report[report['rows_removed'] > 0].sort_values('rows_removed', ascending=False)
print(report_external.head(20))

print(f"\nTotal rows before: {len(t_section)}")
print(f"Total rows after : {len(t_section_filtered)}")
print("Exceptions: Where external source used instead of customs data\n", 
      t_section_filtered[t_section_filtered['comno'].astype(str).isin(exceptions)]['comno'].value_counts())

# --- Replace original df if needed ---
t_section = t_section_filtered
# -


t_section['unit'] = t_section['unit'].replace('KHW', 'KWH')

# ## Save as parquet
# The quarter file is save as a parquet file

t_section.to_parquet(f'../data/{flow}_{year}q{quarter}.parquet')
print()
print('Final output:')
print(f'\nNOTE: Parquet file ../data/{flow}_{year}q{quarter}.parquet written with {t_section.shape[0]} rows and {t_section.shape[1]} columns\n')
print("\n" + "="*80)


