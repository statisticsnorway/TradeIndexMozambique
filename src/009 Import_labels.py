# # Import the chapter catalog from Excel

import pandas as pd

commodity_sitc = pd.read_excel(
    '../cat/HS_SITC.xlsx',
    header=0,
    dtype=str,
    na_values={'.', ' .'}
).rename(columns={'Code': 'comno'})
commodity_sitc['sitc1'] = commodity_sitc['SITC'].str[0]
commodity_sitc['sitc2'] = commodity_sitc['SITC'].str[0:2]
commodity_sitc

# ## Keep only the columns for match with commodities

commodity_sitc = commodity_sitc[['comno', 'sitc1', 'sitc2']]

# ## Save as parquet file

commodity_sitc.to_parquet('../cat/commodity_sitc.parquet')
print(f'\nNOTE: Parquet file ../cat/commodity_sitc.parquet written with {commodity_sitc.shape[0]} rows and {commodity_sitc.shape[1]} columns\n')

# ## Sitc labels import

sitc_label = pd.read_csv('../cat/SITC_labels.txt', dtype=str, sep=';')
sitc_label

sitc_label.to_parquet('../cat/SITC_label.parquet')
print(f'\nNOTE: Parquet file ../cat/SITC_label.parquet written with {sitc_label.shape[0]} rows and {sitc_label.shape[1]} columns\n')
