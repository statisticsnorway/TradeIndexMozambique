# ### Import donors

# +
import os
import pandas as pd

# Parquet file path for donors
correspondance_file = '../cat/donors.parquet'


# Check if the parquet file exists
if os.path.exists(correspondance_file):
    answer = input(f"File {correspondance_file} already exists. Do you want to import it again? (yes/no): ").strip().lower()
    if answer == 'yes':
        # Read Excel and save parquet
        donors = pd.read_csv(
            '../cat/donors.csv', sep=';')
       
        print(f"\nNOTE: Parquet file {correspondance_file} overwritten with {donors.shape[0]} rows and {donors.shape[1]} columns.\n")
    else:
        print(f"File {correspondance_file} not replaced.")
else:
    # File does not exist → create it
    donors = pd.read_csv(
            '../cat/donors.csv', sep=';')

    donors.to_parquet(correspondance_file, engine='pyarrow', index=False)

    print(f"\nNOTE: Parquet file {correspondance_file} created with {donors.shape[0]} rows and {donors.shape[1]} columns.\n")

# -


