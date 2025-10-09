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
# import itables
# # Initialize interactive display mode
# itables.init_notebook_mode(all_interactive=True)
# init_notebook_mode(all_interactive=True)
#
# year = 2023
# quarter = 1
# flow = 'export'
# -

# ### Updating HS Numbers (HS Revision)
#
# **Cases**
#
# - **1:1**  
#   Update Excel sheet
#
# - **1:Many**  
#   Identify if most of the trade is moved to a single commodity  
#   → If yes, update Excel sheet
#
# - **Many:1**  
#   if possible make expert judgement, and update Excel sheet
#
# - **Many:Many**  
#   if possible make expert judgement, and update Excel sheet
#

# +
# Read CSV
new_hs = pd.read_csv('../cat/HS_revision_replacement.csv', sep=';', dtype=str)

# Optional: set display options for nicer output
pd.set_option('display.max_rows', 20)       # show up to 20 rows
pd.set_option('display.max_columns', None)  # show all columns
pd.set_option('display.width', 100)         # adjust width
pd.set_option('display.colheader_justify', 'center')

# Print
print("\n" + "-"*40)
print()
print("### HS Revision Replacement Table ###\n")
print("The following table shows the mapping of old HS numbers to the new HS numbers, including the year the change is valid from:\n")
print(new_hs.to_string(index=False))
print()
# -

base_price = pd.read_parquet(f'../data/base_price{flow}_{year}.parquet')

weightbasefile = f'../data/weight_base_{flow}_{year}.parquet'
weight_base = pd.read_parquet(weightbasefile)

# # HS Number Update in Base Price Dataset
#
# The following Python code updates HS numbers in the `base_price` dataset based on a revision table (`new_hs`). Only HS numbers with `year + 1 == valid_from` are updated, and duplicate `comno`s are avoided.
#

# +
# Convert year to integer if needed
base_price["year"] = base_price["year"].astype(int)
new_hs["valid_from"] = new_hs["valid_from"].astype(int)

# Ensure comno columns are strings with leading zeros
base_price["comno"] = base_price["comno"].astype(str).str.zfill(8)
new_hs["comno"] = new_hs["comno"].astype(str).str.zfill(8)
new_hs["comno_new"] = new_hs["comno_new"].astype(str).str.zfill(8)

# Keep old codes
base_price["comno_old"] = base_price["comno"]

# Merge on comno
merged = base_price.merge(new_hs, how="left", on="comno")

# Create mask: year + 1 == valid_from AND comno_new not in base_price
existing_codes = set(base_price["comno"])
mask = (merged["year"] + 1 == merged["valid_from"]) & (~merged["comno_new"].isin(existing_codes))

# Apply update only where mask is True
merged.loc[mask, "comno"] = merged.loc[mask, "comno_new"]

# Drop helper columns
base_price = merged.drop(columns=["comno_new", "valid_from"])

# Rows that were updated
updated_rows = base_price[base_price["comno"] != base_price["comno_old"]]

# Print
print("\n" + "-"*40)
print("### HS Number Updates in Base Price Dataset ###\n")
if not updated_rows.empty:
    print("The following rows have been updated with new HS numbers:\n")
    print(updated_rows[["year", "comno", "comno_old"]].to_string(index=False))
else:
    print("No HS numbers were updated based on the current HS revision table.")
# -

# # HS Number Update in weight_base Dataset
#
# The following Python code updates HS numbers in the `weight_base` dataset based on a revision table (`new_hs`). Only HS numbers with `year + 1 == valid_from` are updated, and duplicate `comno`s are avoided.
#

# +
# Convert year to integer if needed
weight_base["year"] = weight_base["year"].astype(int)
new_hs["valid_from"] = new_hs["valid_from"].astype(int)

# Ensure comno columns are strings with leading zeros
weight_base["comno"] = weight_base["comno"].astype(str).str.zfill(8)
new_hs["comno"] = new_hs["comno"].astype(str).str.zfill(8)
new_hs["comno_new"] = new_hs["comno_new"].astype(str).str.zfill(8)

# Keep old codes
weight_base["comno_old"] = weight_base["comno"]

# Merge on comno
merged = weight_base.merge(new_hs, how="left", on="comno")

# Create mask: year + 1 == valid_from AND comno_new not in weight_base
existing_codes = set(weight_base["comno"])
mask = (merged["year"] + 1 == merged["valid_from"]) & (~merged["comno_new"].isin(existing_codes))

# Apply update only where mask is True
merged.loc[mask, "comno"] = merged.loc[mask, "comno_new"]

# Drop helper columns
weight_base = merged.drop(columns=["comno_new", "valid_from"])

# Rows that were updated
updated_rows = weight_base[weight_base["comno"] != weight_base["comno_old"]]

# Print
print("\n" + "-"*40)
print("### HS Number Updates in Base Price Dataset ###\n")
if not updated_rows.empty:
    print("The following rows have been updated with new HS numbers:\n")
    print(updated_rows[["year", "comno", "comno_old"]].to_string(index=False))
else:
    print("No HS numbers were updated based on the current HS revision table.")


# +
# Ensure comno columns are strings with leading zeros
weight_base["comno"] = weight_base["comno"].astype(str).str.zfill(8)
base_price["comno"] = base_price["comno"].astype(str).str.zfill(8)

# Sets of comno values
comno_weight = set(weight_base["comno"])
comno_base = set(base_price["comno"])

# Intersection: present in both datasets
comno_both = comno_weight & comno_base
print("\n" + "-"*40)
print("### Check to se that comno in both base_price and weight_base is updated ###\n")
print(f"Number of comno present in both datasets: {len(comno_both)}\n")

# Only in weight_base
only_in_weight = comno_weight - comno_base
if len(only_in_weight) > 0:
    print(f"\033[1mNumber of comno only in weight_base: {len(only_in_weight)}\033[0m")
    print(", ".join(sorted(only_in_weight)))
    print()  # extra line for spacing

# Only in base_price
only_in_base = comno_base - comno_weight
if len(only_in_base) > 0:
    print(f"\033[1mNumber of comno only in base_price: {len(only_in_base)}\033[0m")
    print(", ".join(sorted(only_in_base)))
    print()
# -

# ### Save to original file --> comno is now updated

# # NOT ACTIVATED YET

# + active=""
# base_price.to_parquet(f'../data/base_price{flow}_{year}.parquet')

# + active=""
# weight_base.to_parquet(f'../data/weight_base_{flow}_{year}.parquet')
# -




