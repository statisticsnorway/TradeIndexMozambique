# # Import the chapter catalog from Excel

import os
import pandas as pd

# +

# Parquet file path
correspondance_file = '../cat/chapter_section.parquet'

# Check if the parquet file exists
if os.path.exists(correspondance_file):
    answer = input(f"File {correspondance_file} already exists. Do you want to import it again? (yes/no): ").strip().lower()
    if answer == 'yes':
        # Read Excel and save parquet
        chapter_section = pd.read_excel(
            '../cat/Chapter_Section.xlsx',
            header=None,
            names=['chapter', 'section'],
            dtype=str,
            na_values={'.', ' .'}
        )
        chapter_section.to_parquet(correspondance_file, index=False)
        print(f"\nNOTE: Parquet file {correspondance_file} overwritten with {chapter_section.shape[0]} rows and {chapter_section.shape[1]} columns.\n")
    else:
        print(f"File {correspondance_file} not replaced.")
else:
    # File does not exist → create it
    chapter_section = pd.read_excel(
        '../cat/Chapter_Section.xlsx',
        header=None,
        names=['chapter', 'section'],
        dtype=str,
        na_values={'.', ' .'}
    )
    chapter_section.to_parquet(correspondance_file, index=False)
    print(f"\nNOTE: Parquet file {correspondance_file} created with {chapter_section.shape[0]} rows and {chapter_section.shape[1]} columns.\n")

