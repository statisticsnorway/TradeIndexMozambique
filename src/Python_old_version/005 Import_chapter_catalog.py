# # Import the chapter catalog from Excel

import pandas as pd

chapter_section = pd.read_excel(
    '../data/Chapter_Section.xlsx',
    header=None,
    names=['chapter', 'section'],
    dtype=str,
    na_values={'.', ' .'}
)

# ## Save as parquet file

print(f'\nNOTE: Parquet file ../data/chapter_section.parquet written with {chapter_section.shape[0]} rows and {chapter_section.shape[1]} columns\n')
chapter_section.to_parquet('../data/chapter_section.parquet')
