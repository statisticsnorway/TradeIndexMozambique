# # The price index for external trade for Mozambique
# This program runs all the needed programs for creating the index. Most of the other programs are made as functions which will be called here. The rest will be executed from here

import pandas as pd
import numpy as np
from pathlib import Path
#from trade_index_functions import *
#pd.set_option('display.float_format',  '{:18,.0}'.format)
#pd.set_option('display.float_format', lambda x: f'{x:15.0f}' if abs(x)>1e12 else f'{x:15.1f}')
pd.set_option('display.float_format', lambda x: f'{x:15,.0f}')

display(pd.get_option('display.precision'))
display(pd.get_option('display.float_format'))

# ## Import chapter and section correspondance

exec(open("005 Import_chapter_catalog.py").read())

# ## Import commodity and sitc correspondance

exec(open("007 Import_commodities_catalog.py").read())
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
basedata

# ## Base prices




