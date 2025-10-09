# # Import the chapter catalog from Excel

import pandas as pd

# ### Import SITC_HS correspondance

# +
import os
import pandas as pd

# Parquet file path for commodity-SITC
correspondance_file = '../cat/commodity_sitc.parquet'

# Check if the parquet file exists
if os.path.exists(correspondance_file):
    answer = input(f"File {correspondance_file} already exists. Do you want to import it again? (yes/no): ").strip().lower()
    if answer == 'yes':
        # Read Excel and save parquet
        commodity_sitc = pd.read_excel(
            '../cat/HS_SITC.xlsx',
            header=0,
            dtype=str,
            na_values={'.', ' .'}
        ).rename(columns={'Code': 'comno'})

        commodity_sitc['sitc1'] = commodity_sitc['SITC'].str[0]
        commodity_sitc['sitc2'] = commodity_sitc['SITC'].str[0:2]

        commodity_sitc = commodity_sitc[['comno', 'sitc1', 'sitc2']]
        commodity_sitc.to_parquet(correspondance_file, index=False)

        print(f"\nNOTE: Parquet file {correspondance_file} overwritten with {commodity_sitc.shape[0]} rows and {commodity_sitc.shape[1]} columns.\n")
    else:
        print(f"File {correspondance_file} not replaced.")
else:
    # File does not exist → create it
    commodity_sitc = pd.read_excel(
        '../cat/HS_SITC.xlsx',
        header=0,
        dtype=str,
        na_values={'.', ' .'}
    ).rename(columns={'Code': 'comno'})

    commodity_sitc['sitc1'] = commodity_sitc['SITC'].str[0]
    commodity_sitc['sitc2'] = commodity_sitc['SITC'].str[0:2]

    commodity_sitc = commodity_sitc[['comno', 'sitc1', 'sitc2']]
    commodity_sitc.to_parquet(correspondance_file, index=False)

    print(f"\nNOTE: Parquet file {correspondance_file} created with {commodity_sitc.shape[0]} rows and {commodity_sitc.shape[1]} columns.\n")

# -

# ### Import ISIC_HS correspondance

# +
import os
import pandas as pd

# Parquet file path for commodity-SITC
correspondance_file = '../cat/commodity_isic.parquet'

# Check if the parquet file exists
if os.path.exists(correspondance_file):
    answer = input(f"File {correspondance_file} already exists. Do you want to import it again? (yes/no): ").strip().lower()
    if answer == 'yes':
        # Read Excel and save parquet
        commodity_isic = pd.read_excel(
            '../cat/HS_ISIC.xlsx',
            header=0,
            dtype=str,
            na_values={'.', ' .'}
        ).rename(columns={'Code': 'comno'})

        # Extract ISIC hierarchy
        commodity_isic['isic_section']  = commodity_isic['ISIC'].str[0]
        commodity_isic['isic_division'] = commodity_isic['ISIC'].str[0:3]
        commodity_isic['isic_group']    = commodity_isic['ISIC'].str[0:4]
        commodity_isic['isic_class']    = commodity_isic['ISIC'].str[0:5]
        
        # Keep only relevant columns (add 'comno' if you have it)
        commodity_isic = commodity_isic[['comno', 'isic_section', 'isic_division', 'isic_group', 'isic_class']]
        
        # Save to parquet
        commodity_isic.to_parquet(correspondance_file, index=False)


        print(f"\nNOTE: Parquet file {correspondance_file} overwritten with {commodity_isic.shape[0]} rows and {commodity_isic.shape[1]} columns.\n")
    else:
        print(f"File {correspondance_file} not replaced.")
else:
    # File does not exist → create it
    commodity_isic = pd.read_excel(
        '../cat/HS_ISIC.xlsx',
        header=0,
        dtype=str,
        na_values={'.', ' .'}
    ).rename(columns={'Code': 'comno'})


    # Extract ISIC hierarchy
    commodity_isic['isic_section']  = commodity_isic['ISIC'].str[0]
    commodity_isic['isic_division'] = commodity_isic['ISIC'].str[0:3]
    commodity_isic['isic_group']    = commodity_isic['ISIC'].str[0:4]
    commodity_isic['isic_class']    = commodity_isic['ISIC'].str[0:5]
    
    # Keep only relevant columns (add 'comno' if you have it)
    commodity_isic = commodity_isic[['comno', 'isic_section', 'isic_division', 'isic_group', 'isic_class']]
    
    # Save to parquet
    commodity_isic.to_parquet(correspondance_file, index=False)



    print(f"\nNOTE: Parquet file {correspondance_file} created with {commodity_isic.shape[0]} rows and {commodity_isic.shape[1]} columns.\n")

