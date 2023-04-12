# # Read csv file from external trade

import pandas as pd
import numpy as np

# ## Read csv file
# We use the pandas read_csv to import the file to a Python pandas dataframe. With the dtype parameter we decide the column types.

year = 2018
export = pd.read_csv(
    f'../data/Export - {year}_XPMI.csv',
    header=0,
    sep=';',
    decimal=',',
    dtype={
        'flow': 'object',
        'year': 'object',
        'month': 'object',
        'ref': 'object',
        'ItemID': 'object',
        'comno': 'object',
        'country': 'object',
        'unit': 'object',
        'weight': 'float',
        'quantity': 'float',
        'value': 'float',
        'valUSD': 'float',
        'itemno': 'object',
        'exporterNUIT': 'object'
    },
    na_values={'.',' .'}
)
export

pd.crosstab(export['unit'], columns='Frequency', margins=True)

export.info()


