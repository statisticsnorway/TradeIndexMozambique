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
pd.set_option('display.float_format', lambda x: f'{x:15,.0f}' if abs(x)>1e5 else f'{x:15.2f}')

# Set the option for interactive browsing of dataframes. This will show the output dataframes in a more flexible way than the default view.

init_notebook_mode(all_interactive=True)

# ## Import chapter and section correspondance

exec(open("005 Import_chapter_catalog.py").read())

# ## Import commodity and sitc correspondance

exec(open("007 Import_commodities_catalog.py", encoding="utf-8").read())

# ## Parameters for 2018

year = 2018
flow = 'Export'

# ## Import export files for 2018

quarter = 1
exec(open("T010 Read trade quarter.py").read())
quarter = 2
exec(open("T010 Read trade quarter.py").read())
quarter = 3
exec(open("T010 Read trade quarter.py").read())
quarter = 4
exec(open("T010 Read trade quarter.py").read())

t_section

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
basedata

# ## Base prices 2018

# Parameters

year = 2018

# ## Calculate the base prices

exec(open("A30M Base_price.py").read())
trade_without_outliers_r

# ## Read tradedata 2019 quarter 1

year = 2019
quarter  = 1

# +
np.random.seed(44291)

n = 10
outliser_limit = 2.0
flow = ['E', 'I'] 
comno = ['44190000', '44201000', '44209000'] 
value = abs(np.random.normal(100,1000, size=n))
weight = abs(np.random.normal(1,10, size=n))

# Opprett en Pandas dataframe
data = {'flow': np.random.choice(flow, n),
        'comno': np.random.choice(comno, n),
        'value': value,
        'weight': weight}
tradedata = pd.DataFrame(data)
tradedata['price'] = tradedata['value'] / tradedata['weight']
tradedata['sd_comno'] = tradedata.groupby(['flow', 'comno'])['price'].transform('std')
tradedata['sd_comno2'] = tradedata.groupby(['flow', 'comno'])['price'].transform('std')*2
tradedata['price2'] = tradedata['price'] * 2

tradedata['sd_comno_lambda2'] = tradedata.groupby(['flow', 'comno'], as_index=False)['price'].transform(lambda x: (outlier_limit * (np.std(x))))
tradedata['sd_comno_lambda2p2'] = tradedata.groupby(['flow', 'comno'], as_index=False)['price2'].transform(lambda x: np.std(x))

tradedata['mean_comno'] = tradedata.groupby(['flow', 'comno'])['price'].transform('mean')

tradedata['ul'] = tradedata['mean_comno'] + (2 * tradedata['sd_comno'])
tradedata['ll'] = tradedata['mean_comno'] - (2 * tradedata['sd_comno'])
tradedata['outl'] = np.where((tradedata['price'] < tradedata['ll']) | (tradedata['price'] > tradedata['ul']), 1, 0)
tradedata['outl2'] = np.where((abs(tradedata['price'] - tradedata['mean_comno']) > (2 * tradedata['sd_comno'])), 1, 0)

tradedata['ul2'] = (
    tradedata.groupby(['flow', 'comno'], as_index=False)['price']
    .transform(lambda x: np.mean(x, axis=0)  + (outlier_limit * (np.std(x, axis=0))))
)
tradedata['ll2'] = (
    tradedata.groupby(['flow', 'comno'], as_index=False)['price']
    .transform(lambda x: np.mean(x, axis=0)  - (outlier_limit * (np.std(x, axis=0))))
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




