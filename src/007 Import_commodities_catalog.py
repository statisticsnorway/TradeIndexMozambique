# # Import the chapter catalog from Excel

import pandas as pd

commodity_sitc = pd.read_excel(
    '../data/Commodities_Catalogue_XPMI.xlsx',
    sheet_name='Pauta Grupos_2023_',
    header=0,
    dtype=str,
    na_values={'.', ' .'}
)
commodity_sitc = commodity_sitc[['comno', 'sitcr4_1', 'sitcr4_2']].rename(columns={'sitcr4_1': 'sitc1', 
                                                                                   'sitcr4_2': 'sitc2'})
commodity_sitc.to_parquet('../data/commodity_sitc.parquet')


