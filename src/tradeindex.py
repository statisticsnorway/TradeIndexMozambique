# # The price index for external trade for Mozambique
# This program runs all the needed programs for creating the index. Most of the other programs are included and executerd from here. The parameteres will change for each period

# ## Import the necessary Python packages
# If the packages are not installed, use `pip install` from a terminal window to install, for instance `pip install pyarrow` and `pip install jupytext --upgrade`

import pandas as pd
import numpy as np
import json
from pathlib import Path
from itables import init_notebook_mode
#pd.set_option('display.float_format',  '{:18,.0}'.format)
#pd.set_option('display.float_format', lambda x: f'{x:15.0f}' if abs(x)>1e12 else f'{x:15.1f}')
pd.set_option('display.float_format', lambda x: f'{x:15,.0f}' if abs(x)>1e5 else f'{x:15.2f}')

# Set the option for interactive browsing of dataframes. This will show the output dataframes in a more flexible way than the default view.

init_notebook_mode(all_interactive=True)

# ## Import chapter and section correspondance

exec(open("005 Import_chapter_catalog.py").read())

# ## Import commodity and sitc correspondance

exec(open("007 Import_commodities_catalog.py", encoding="utf-8").read())

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



tradedata.loc[(tradedata['exporterNUIT'] == '400027145') & (tradedata['sitc1'] == '3')]

tradedata.loc[np.isinf(tradedata['price'])]

data_dir = Path('../data')
tradedata = pd.concat(
    pd.read_parquet(parquet_file)
    for parquet_file in data_dir.glob(f'{flow}_{year}q*.parquet')
)
tradedata.info()


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
c1


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
tradedata.info()



with open('../data/labels.json') as json_file:
    data = json.load(json_file)
data    

tr = tradedata.replace(labels)
tr

tradedata['sitc1t'] = tradedata['sitc1'].map(labels['sitc1'])
tradedata.info()

# +
labs = pd.read_json('../data/labels.json')
labs


# -

x

# +
np.random.seed(44291)

n = 25000
outliser_limit = 2.0
flow = ['E', 'I'] 
comno = ['44190000', '44201000', '44209000'] 
value = abs(np.random.normal(1000000000,100000000000, size=n))
weight = abs(np.random.normal(1,10, size=n))

# Opprett en Pandas dataframe
data = {'flow': np.random.choice(flow, n),
        'comno': np.random.choice(comno, n),
        'value': value,
        'weight': weight}
tradedata = pd.DataFrame(data)
tradedata['price'] = tradedata['value'] / tradedata['weight']
tradedata['sd_comno'] = tradedata.groupby(['flow', 'comno'])['price'].transform('std')
tradedata['mean_comno'] = tradedata.groupby(['flow', 'comno'])['price'].transform('mean')

tradedata['ul'] = tradedata['mean_comno'] + (2 * tradedata['sd_comno'])
tradedata['ll'] = tradedata['mean_comno'] - (2 * tradedata['sd_comno'])
tradedata['outl'] = np.where((tradedata['price'] < tradedata['ll']) | (tradedata['price'] > tradedata['ul']), 1, 0)
tradedata['outl2'] = np.where((abs(tradedata['price'] - tradedata['mean_comno']) > (2 * tradedata['sd_comno'])), 1, 0)

tradedata['ul2'] = (
    tradedata.groupby(['flow', 'comno'], as_index=False)['price']
    .transform(lambda x: np.mean(x, axis=0)  + (outlier_limit * np.std(x, axis=0)))
)
tradedata['ll2'] = (
    tradedata.groupby(['flow', 'comno'], as_index=False)['price']
    .transform(lambda x: np.mean(x, axis=0)  - (outlier_limit * np.std(x, axis=0)))
)
tradedata['outlier_price'] = (
    tradedata.groupby(['flow', 'comno'], as_index=False)['price']
    .transform(lambda x: abs(x - np.mean(x, axis=0) > outlier_limit * np.std(x))).astype(int)
)
tradedata['dist_std'] = (
    tradedata.groupby(['flow', 'comno'], as_index=False)['price']
    .transform(lambda x: outlier_limit * np.std(x, axis=0))
)
display(tradedata)
pd.crosstab(tradedata['outl2'], columns=tradedata['outlier_price'])

# -

tradedata.info()




