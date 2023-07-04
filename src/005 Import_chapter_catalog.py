# # Import the chapter catalog from Excel

import pandas as pd

chapter_section = pd.read_excel(
    '../data/Chapter_Section.xlsx',
    header=None,
    names=['chapter', 'section'],
    dtype=str,
    na_values={'.', ' .'}
)
chapter_section.to_parquet('../data/chapter_section.parquet')


