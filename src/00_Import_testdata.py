# ---
# jupyter:
#   jupytext:
#     formats: py:hydrogen
#     text_representation:
#       extension: .py
#       format_name: hydrogen
#       format_version: '1.3'
#       jupytext_version: 1.16.4
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Trade examples

# %%
import pandas as pd
import numpy as np

# %%
import os
print(os.getcwd())


# %%
import pandas as pd
import os

# Base path and file prefix
base_path = '../data'
fileprefix = 'Import - '  # Replace with your actual prefix

for year in range(2023, 2024):
    for quarter in range(1, 5):
        input_filename = f'{fileprefix}{year}_XPMI_Q{quarter}.csv'
        input_path = os.path.join(base_path, input_filename)
        output_filename = input_filename.replace('.csv', '.txt')
        output_path = os.path.join(base_path, output_filename)

        try:
            # Read the CSV file
            df = pd.read_csv(input_path, encoding='latin1', dtype=str)

            # Example structure/format adjustments
            df.columns = df.columns.str.lower().str.strip()
            df['year'] = year
            df['quarter'] = quarter

            # Add any custom adjustments here
            # e.g., df['new_column'] = df['existing_column'] * 2

            # Save the modified dataframe as a tab-separated .txt file
            df.to_csv(output_path, sep='\t', index=False)

            print(f'Saved: {output_path}')

        except FileNotFoundError:
            print(f'File not found: {input_path}')
        except Exception as e:
            print(f'Error processing {input_path}: {e}')

