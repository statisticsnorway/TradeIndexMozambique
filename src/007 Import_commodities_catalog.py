# # Import the chapter catalog from Excel

import pandas as pd

# +
commodity_sitc = pd.read_excel(
    '../data/Commodities_Catalogue_XPMI.xlsx',
    sheet_name='Pauta Grupos_2023_',
    header=0,
    dtype=str,
    na_values={'.', ' .'}
)

commodity_sitc.rename(columns={'SH2': 'hs2', 
                               'Descrição SH2': 'hs2_text',
                               'Description sitcr4_1': 'sitc1_text',
                               'Description sitcr4_2': 'sitc2_text'
                               }, 
                       inplace=True)


# -

# ## Function for extracting classifications from the imported spreadsheet

def class_from_comm(df: pd.DataFrame, code:str, text:str, label:str):
    df1 = df[[code, text]].rename(columns={text: label})
    df1 = df1[df1.duplicated([code], keep='first') == False].sort_values([code])
    df1[label] = df1[code] + ' ' + df1[label]
    label_dict = df1[[code, label]].set_index(code).to_dict()
    return label_dict


# ## Create labels dictionary from imported spreadsheet

chapter_dict = class_from_comm(commodity_sitc, 'hs2', 'hs2_text', 'chapter')
sitc1_dict = class_from_comm(commodity_sitc, 'sitcr4_1', 'sitc1_text', 'sitc1')
sitc2_dict = class_from_comm(commodity_sitc, 'sitcr4_2', 'sitc2_text', 'sitc2')
labels = chapter_dict | sitc1_dict | sitc2_dict

# ## Save labels dictionary as json file

with open("../data/labels.json", "w") as outfile:
    json.dump(labels, outfile)

# ## Keep only the columns for match with commodities

commodity_sitc = commodity_sitc[['comno', 'sitcr4_1', 'sitcr4_2']].rename(columns={'sitcr4_1': 'sitc1', 
                                                                                   'sitcr4_2': 'sitc2'})

# ## Save as parquet file

commodity_sitc.to_parquet('../data/commodity_sitc.parquet')
