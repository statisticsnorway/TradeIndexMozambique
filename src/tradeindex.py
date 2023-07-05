# # The price index for external trade for Mozambique
# This program runs all the needed programs for creating the index. Most of the other programs are made as functions which will be called here. The rest will be executed from here

import pandas as pd
import numpy as np
import json
from pathlib import Path
from itables import init_notebook_mode
#from trade_index_functions import *
#pd.set_option('display.float_format',  '{:18,.0}'.format)
#pd.set_option('display.float_format', lambda x: f'{x:15.0f}' if abs(x)>1e12 else f'{x:15.1f}')
pd.set_option('display.float_format', lambda x: f'{x:15,.0f}' if abs(x)>1e5 else f'{x:15.2f}')

display(pd.get_option('display.precision'))
display(pd.get_option('display.float_format'))

# Set the option for interactive browsing of dataframes

init_notebook_mode(all_interactive=True)

# ## Import chapter and section correspondance

exec(open("005 Import_chapter_catalog.py").read())

# ## Import commodity and sitc correspondance

exec(open("007 Import_commodities_catalog.py", encoding="utf-8").read())
commodity_sitc = pd.read_parquet('../data/commodity_sitc.parquet')
commodity_sitc

# ## Import export files for 2018

year = 2018
flow = 'Export'
quarter = 1
exec(open("T010 Read trade quarter.py").read())
quarter = 2
exec(open("T010 Read trade quarter.py").read())
quarter = 3
exec(open("T010 Read trade quarter.py").read())
quarter = 4
exec(open("T010 Read trade quarter.py").read())

# ## Create weight base data and delete outliers

outlier_limit = 2.0
exec(open("A10M CreateWeightBasePopulation.py").read())
tradedata

# ## Create weight base population
# This syntax will select the commodities to use for the index for the next year. It will be the base for that index. We set the parameters for selecting the commodities here

share_total=0.05
no_of_months=5
no_of_months_seasons=3
section_seasons='II'
price_cv=0.5
max_by_min=10
max_by_median=5
median_by_min=5
share_small=0.0001
exec(open("A20M CreateWeightBase.py").read())


# ## Base prices

def coverage(df: pd.DataFrame, groupcol, aggcol1, aggcol2) -> pd.DataFrame:
    result = df.groupby(['year', 'flow', groupcol]).agg(
        Ssample_sum=(aggcol1, 'sum'),
        Spop_sum=('S1_sum', 'mean'),
        Sno_of_comm=('S1_sum', 'size')
        )
    result['Tsample_sum'] = result.groupby(['year', 'flow'])['Ssample_sum'].transform('sum')
    result['Tpop_sum'] = result.groupby(['year', 'flow'])['Spop_sum'].transform('sum')
    result['Tno_of_comm'] = result.groupby(['year', 'flow'])['Sno_of_comm'].transform('sum')
    result['Scoverage'] = result['Ssample_sum'] * 100 / result['Spop_sum']
    return result


coverage(basedata, 'sitc1', 'HS_sum', 'S1_sum')

data_dir = Path('../data')
tradedata = pd.concat(
    pd.read_parquet(parquet_file)
    for parquet_file in data_dir.glob(f'{flow}_{year}q*.parquet')
)
tradedata


def coverage(df: pd.DataFrame, groupcol, aggcol) -> pd.DataFrame:
    result = df.groupby(['year', 'flow', groupcol]).agg(
        Ssample_sum=('HS_sum', 'sum'),
        Spop_sum=('S1_sum', 'mean'),
        Sno_of_comm=('S1_sum', 'size')
        )
    result['Tsample_sum'] = result.groupby(['year', 'flow'])['Ssample_sum'].transform('sum')
    result['Tpop_sum'] = result.groupby(['year', 'flow'])['Spop_sum'].transform('sum')
    result['Tno_of_comm'] = result.groupby(['year', 'flow'])['Sno_of_comm'].transform('sum')
    result['Scoverage'] = result['Ssample_sum'] * 100 / result['Spop_sum']
#    result[groupcol] = result[groupcol].map(labels[groupcol])
    return result


c1 = coverage(basedata, 'sitc2', 'S2_sum')
labels


def class_from_comm(df: pd.DataFrame, code:str, text:str, label:str):
    df1 = df[[code, text]].rename(columns={text: label})
    df1 = df1[df1.duplicated([code], keep='first') == False].sort_values([code])
    df1[label] = df1[code] + ' ' + df1[label]
    label_dict = df1[[code, label]].set_index(code).to_dict()
    return label_dict


chapter_dict = class_from_comm(commodity_sitc, 'hs2', 'hs2_text', 'chapter')
sitc1_dict = class_from_comm(commodity_sitc, 'sitcr4_1', 'sitc1_text', 'sitc1')
sitc2_dict = class_from_comm(commodity_sitc, 'sitcr4_2', 'sitc2_text', 'sitc2')
labels = chapter_dict | sitc1_dict | sitc2_dict
labels

chapter = commodity_sitc[['hs2', 'hs2_text']].rename(columns={'hs2_text': 'chapter'})
chapter = chapter[chapter.duplicated(['hs2'], keep='first') == False].sort_values(['hs2'])
chapter['chapter'] = chapter['hs2'] + ' ' + chapter['chapter']
chapter_dict = chapter[['hs2', 'chapter']].set_index('hs2').to_dict()
chapter_dict

commodity_sitc.info()

# +
labels.to_parquet('../data/labels.parquet')

#.to_pydict()
# -



with open('../data/labels.json') as json_file:
    data = json.load(json_file)
data    


