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

# ## Create weight base data and delete outliers for 2018

year = 2018
outlier_limit = 2.0
exec(open("A10M CreateWeightBasePopulation.py").read())

# ## Create weight base population 2018
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

# ## Calculate the base prices 2018

exec(open("A30M Base_price.py").read())
baseprice

# ## Tradedata 2019 quarter 1

year = 2019
quarter  = 1
exec(open("T010 Read trade quarter.py").read())

# ### Price control quarter
# Check the data for extreme prices

price_limit_low = 0.3
price_limit_high = 2.5
exec(open("T40M Price_control.py").read())

# ### Impute prices quarter

exec(open("T50M Impute_prices.py").read())
prices

# ### Calculate unchained index quarter

exec(open("T60M Index_unchained.py").read())

# ## Tradedata 2019 quarter 2

quarter  = 2
exec(open("T010 Read trade quarter.py").read())

# ### Price control quarter
# Check the data for extreme prices

price_limit_low = 0.3
price_limit_high = 2.5
exec(open("T40M Price_control.py").read())

# ### Impute prices quarter

exec(open("T50M Impute_prices.py").read())
prices

# ### Calculate unchained index quarter

exec(open("T60M Index_unchained.py").read())

# ## Tradedata 2019 quarter 3

quarter  = 3
exec(open("T010 Read trade quarter.py").read())

# ### Price control quarter
# Check the data for extreme prices

price_limit_low = 0.3
price_limit_high = 2.5
exec(open("T40M Price_control.py").read())

# ### Impute prices quarter

exec(open("T50M Impute_prices.py").read())

# ### Calculate unchained index quarter

exec(open("T60M Index_unchained.py").read())

# ## Tradedata 2019 quarter 4

quarter  = 4
exec(open("T010 Read trade quarter.py").read())

# ### Price control quarter
# Check the data for extreme prices

price_limit_low = 0.3
price_limit_high = 2.5
exec(open("T40M Price_control.py").read())

# ### Impute prices quarter

exec(open("T50M Impute_prices.py").read())

# ### Calculate unchained index quarter

exec(open("T60M Index_unchained.py").read())

# ## Calculate chained index for the first year

year = 2019
exec(open("T71M Chain_first_year.py").read())

# ## Create weight base data and delete outliers for 2019

year = 2019
outlier_limit = 2.0
exec(open("A10M CreateWeightBasePopulation.py").read())

# ## Create weight base population 2019
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

# ## Calculate the base prices 2019

exec(open("A30M Base_price.py").read())
baseprice

# ## Tradedata 2020 quarter 1

year = 2020
quarter  = 1
exec(open("T010 Read trade quarter.py").read())

# ### Price control quarter
# Check the data for extreme prices

price_limit_low = 0.3
price_limit_high = 2.5
exec(open("T40M Price_control.py").read())

# ### Impute prices quarter

exec(open("T50M Impute_prices.py").read())
prices

# ### Calculate unchained index quarter

exec(open("T60M Index_unchained.py").read())

# ### Chained index

exec(open("T72M Chain_next_years.py").read())

# ## Tradedata 2020 quarter 2

year = 2020
quarter  = 2
exec(open("T010 Read trade quarter.py").read())

# ### Price control quarter
# Check the data for extreme prices

price_limit_low = 0.3
price_limit_high = 2.5
exec(open("T40M Price_control.py").read())

# ### Impute prices quarter

exec(open("T50M Impute_prices.py").read())

# ### Calculate unchained index quarter

exec(open("T60M Index_unchained.py").read())

# ### Chained index

exec(open("T72M Chain_next_years.py").read())

# ## Tradedata 2020 quarter 3

year = 2020
quarter  = 3
exec(open("T010 Read trade quarter.py").read())

# ### Price control quarter
# Check the data for extreme prices

price_limit_low = 0.3
price_limit_high = 2.5
exec(open("T40M Price_control.py").read())

# ### Impute prices quarter

exec(open("T50M Impute_prices.py").read())
prices

# ### Calculate unchained index quarter

exec(open("T60M Index_unchained.py").read())

# ### Chained index

exec(open("T72M Chain_next_years.py").read())

# ## Tradedata 2020 quarter 4

year = 2020
quarter  = 4
exec(open("T010 Read trade quarter.py").read())

# ### Price control quarter
# Check the data for extreme prices

price_limit_low = 0.3
price_limit_high = 2.5
exec(open("T40M Price_control.py").read())

# ### Impute prices quarter

exec(open("T50M Impute_prices.py").read())
prices

# ### Calculate unchained index quarter

exec(open("T60M Index_unchained.py").read())

# ## Chained index

year = 2020
exec(open("T72M Chain_next_years.py").read())
index_chained_detailed

# ## Create weight base data and delete outliers for 2020

year = 2020
outlier_limit = 2.0
exec(open("A10M CreateWeightBasePopulation.py").read())

# ## Create weight base population 2020
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

# ## Calculate the base prices 2020

exec(open("A30M Base_price.py").read())
baseprice

# ## Tradedata 2021 quarter 1

year = 2021
quarter  = 1
exec(open("T010 Read trade quarter.py").read())

# ### Price control quarter
# Check the data for extreme prices

price_limit_low = 0.3
price_limit_high = 2.5
exec(open("T40M Price_control.py").read())

# ### Impute prices quarter

exec(open("T50M Impute_prices.py").read())
prices

# ### Calculate unchained index quarter

exec(open("T60M Index_unchained.py").read())

# ### Chained index

exec(open("T72M Chain_next_years.py").read())

# ## Tradedata 2021 quarter 2

year = 2021
quarter  = 2
exec(open("T010 Read trade quarter.py").read())

# ### Price control quarter
# Check the data for extreme prices

price_limit_low = 0.3
price_limit_high = 2.5
exec(open("T40M Price_control.py").read())

# ### Impute prices quarter

exec(open("T50M Impute_prices.py").read())

# ### Calculate unchained index quarter

exec(open("T60M Index_unchained.py").read())

# ### Chained index

exec(open("T72M Chain_next_years.py").read())

# ## Tradedata 2021 quarter 3

year = 2021
quarter  = 3
exec(open("T010 Read trade quarter.py").read())

# ### Price control quarter
# Check the data for extreme prices

price_limit_low = 0.3
price_limit_high = 2.5
exec(open("T40M Price_control.py").read())

# ### Impute prices quarter

exec(open("T50M Impute_prices.py").read())
prices

# ### Calculate unchained index quarter

exec(open("T60M Index_unchained.py").read())

# ### Chained index

exec(open("T72M Chain_next_years.py").read())

# ## Tradedata 2021 quarter 4

year = 2021
quarter  = 4
exec(open("T010 Read trade quarter.py").read())

# ### Price control quarter
# Check the data for extreme prices

price_limit_low = 0.3
price_limit_high = 2.5
exec(open("T40M Price_control.py").read())

# ### Impute prices quarter

exec(open("T50M Impute_prices.py").read())
prices

# ### Calculate unchained index quarter

exec(open("T60M Index_unchained.py").read())

# ## Chained index

year = 2021
exec(open("T72M Chain_next_years.py").read())
index_chained_detailed

#



# ## aggregate with lambda function and when calculations are done

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
sitccat.loc[sitccat['comno'] == '27160000']

commlist = pd.read_parquet('../data/commodity_sitc.parquet')
commlist.loc[commlist['comno'] == '27160000']


t_section.loc[t_section['comno'] == '27160000']

t_sitc = pd.merge(tradedata, sitccat, on='comno', how='left', indicator=True)
print(f'Result of merge with sitc catalog for {flow}, for {year}q{quarter}:')
display(pd.crosstab(t_sitc['_merge'], columns='Frequency', margins=True))
print(f'List of commodity numbers that do not have sitc code for {flow}, for {year}q{quarter}:')
display(pd.crosstab(t_sitc.loc[t_sitc['_merge'] == 'left_only', 'comno'], columns='Frequency', margins=True))


pd.crosstab(t_sitc.loc[t_sitc['comno'] == '27160000', 'comno'], columns=t_sitc['_merge'], margins=True)

pd.crosstab(t_sitc.loc[t_sitc['_merge'] == 'left_only', 'comno'], columns='_merge', margins=True)

# +
 if len(t_sitc.loc[t_sitc['_merge'] == 'left_only']) > 0:
    print(f'List of commodity numbers that do not have sitc code for {flow}, for {year}q{quarter}:')
    display(pd.crosstab(t_sitc.loc[t_sitc['_merge'] == 'left_only', 'comno'], columns='Frequency', margins=True))

    
        
# -

data = pd.DataFrame({'bruk2': ['123', 'abc', 'a2d', 'dd3']})
data['nummer'] = data['bruk2'].str[1].str.isdigit()
data

tradedata.loc[np.isinf(tradedata['price'])]

len(tradedata.loc[np.isinf(tradedata['price'])]) > 0

trade_quarter.loc[trade_quarter['comno'] > '87000000']

if len(trade_without_outliers_r.loc[trade_without_outliers_r['base_price'].isna()]) > 0:
    display(pd.crosstab(trade_without_outliers_r.loc[trade_without_outliers_r['base_price'].isna(), 'base_price'], columns='Frequency'))

trade_without_outliers_r

trade_without_outliers_r



year_base = year - 1

data_dir = Path('../data')
trade = pd.concat(
    pd.read_parquet(parquet_file)
    for parquet_file in data_dir.glob(f'{flow}_{year}q*.parquet')
)
print(f'{trade.shape[0]} rows read from parquet files for {year}\n')
trade

# ## Open the weight base for previous year and aggregate to section

year = 2019
weight_base = pd.read_parquet(f'../data/weight_base_{flow}_{year}.parquet')
print(f'{weight_base.shape[0]} rows read from parquet file ../data/weight_base_{flow}_{year}.parquet\n')
weight_base

# ## Extract weight at commodity level

commodity_weights = (weight_base[weight_base.duplicated(['year', 'flow', 'comno'], keep='first') == False]
            .sort_values(['year', 'flow', 'comno'])                 
)
commodity_weights = commodity_weights[['year', 'flow', 'comno', 'Weight_HS']]
commodity_weights

# ## Match the weight to the tradedata
# We use inner join because we only want to include those who are in the weight base

trade_with_weights = pd.merge(trade, commodity_weights, on=['year', 'flow', 'comno'], how='inner')
trade_with_weights

# ## Calculate the price
# We also calculate the median price by commodity

trade_with_weights['price'] = trade_with_weights['value'] / trade_with_weights['weight']
trade_with_weights['price_median'] = trade_with_weights.groupby(['flow', 'comno'])['price'].transform('median')
trade_with_weights

# ## Mark outliers

trade_with_weights['outlier'] = np.select([trade_with_weights['price'] / trade_with_weights['price_median'] < 0.3,
                                           trade_with_weights['price'] / trade_with_weights['price_median'] > 2.5,
                                           ],
                                          [1, 2],
                                          default=0
                                         )
display(pd.crosstab(trade_with_weights['outlier'], columns=trade_with_weights['flow'], margins=True))
trade_with_weights

# ## Extract those who are not outliers

# +
trade_without_outliers = trade_with_weights.loc[trade_with_weights['outlier'] == 0]

trade_without_outliers = trade_without_outliers.groupby(['year', 'quarter', 'flow', 'comno', 'section', 'Weight_HS'], 
                                                        as_index=False).agg(
    value_quarter=('value', 'sum'),
    weight_quarter=('weight', 'sum')
    )
trade_without_outliers['price'] = trade_without_outliers['value_quarter'] / trade_without_outliers['weight_quarter']
trade_without_outliers
# -

# ## Transpose the data so it will be easier to impute missing prices

trade_without_outliers_r = trade_without_outliers.pivot(index=['year', 'flow', 'comno', 'section', 'Weight_HS'], 
                                                        columns='quarter', 
                                                        values= ['price']
                                                       )
trade_without_outliers_r.columns = trade_without_outliers_r.columns.get_level_values(0) + '_' + trade_without_outliers_r.columns.get_level_values(1).astype('str')
trade_without_outliers_r.reset_index(inplace=True)
trade_without_outliers_r

# ## Compute values for price relatives and product

trade_without_outliers_r['price_rel_1'] = trade_without_outliers_r['price_4.0'] / trade_without_outliers_r['price_3.0']
trade_without_outliers_r['price_rel_2'] = trade_without_outliers_r['price_4.0'] / trade_without_outliers_r['price_2.0']
trade_without_outliers_r['product_1'] = trade_without_outliers_r['price_rel_1'] * trade_without_outliers_r['Weight_HS']
trade_without_outliers_r['product_2'] = trade_without_outliers_r['price_rel_2'] * trade_without_outliers_r['Weight_HS']

# ## Compute products aggregated to section

trade_without_outliers_r['prod_sum_1'] = trade_without_outliers_r.groupby(['year', 'flow', 'section'])['product_1'].transform('sum')
trade_without_outliers_r['prod_sum_2'] = trade_without_outliers_r.groupby(['year', 'flow', 'section'])['product_2'].transform('sum')

# ## Create weights by section for those who have value for product_1

trade_without_outliers_r['weight_section'] = trade_without_outliers_r['Weight_HS'] * trade_without_outliers_r['product_1'].notna()
trade_without_outliers_r['weight_section'] = trade_without_outliers_r.groupby(['year', 'flow', 'section'])['weight_section'].transform('sum')

# ## Impute prices for those who are missing
# Not all will necessarily get prices in this round

trade_without_outliers_r['impute_base'] = trade_without_outliers_r['price_4.0'].isna().astype('int') 
trade_without_outliers_r['price_4.0'] = np.where((~trade_without_outliers_r['price_3.0'].isna()) &
                                                 (trade_without_outliers_r['impute_base'] == 1),
                                                 trade_without_outliers_r['price_3.0']*
                                                 trade_without_outliers_r['prod_sum_1']/
                                                 trade_without_outliers_r['weight_section'],
                                                 trade_without_outliers_r['price_4.0']
                                                )
trade_without_outliers_r['price_4.0'] = np.where((trade_without_outliers_r['price_3.0'].isna()) &
                                                 (trade_without_outliers_r['impute_base'] == 1),
                                                  trade_without_outliers_r['price_2.0']*
                                                  trade_without_outliers_r['prod_sum_2']/
                                                  trade_without_outliers_r['weight_section'],
                                                  trade_without_outliers_r['price_4.0']
                                                 )
display(pd.crosstab(trade_without_outliers_r['impute_base'], columns='Frequency', margins=True))

# ## Compute products aggregated flow

trade_without_outliers_r['prod_sum_1'] = trade_without_outliers_r.groupby(['year', 'flow'])['product_1'].transform('sum')
trade_without_outliers_r['prod_sum_2'] = trade_without_outliers_r.groupby(['year', 'flow'])['product_2'].transform('sum')

# ## Create weights by flow for those who have value for product_1

trade_without_outliers_r['weight_flow'] = trade_without_outliers_r['Weight_HS'] * trade_without_outliers_r['product_1'].notna()
trade_without_outliers_r['weight_flow'] = trade_without_outliers_r.groupby(['year', 'flow'])['weight_flow'].transform('sum')

# ## Impute prices for those who are still missing
# All rows should have prices after these operations. It is checked with a table.

trade_without_outliers_r['impute_base'] = np.where(trade_without_outliers_r['impute_base'] == 1,
                                                  trade_without_outliers_r['price_4.0'].isin([np.nan, np.inf]).astype('int') + 1,
                                                  trade_without_outliers_r['impute_base'])
trade_without_outliers_r['price_4.0'] = np.where((trade_without_outliers_r['price_3.0'].notna()) &
                                                  (trade_without_outliers_r['impute_base'] == 2),
                                                  trade_without_outliers_r['price_3.0']*
                                                  trade_without_outliers_r['prod_sum_1']/
                                                  trade_without_outliers_r['weight_flow'],
                                                  trade_without_outliers_r['price_4.0']
                                                 )
trade_without_outliers_r['price_4.0'] = np.where((trade_without_outliers_r['price_3.0'].isna()) &
                                                  (trade_without_outliers_r['impute_base'] == 2),
                                                  trade_without_outliers_r['price_2.0']*
                                                  trade_without_outliers_r['prod_sum_2']/
                                                  trade_without_outliers_r['weight_flow'],
                                                  trade_without_outliers_r['price_4.0']
                                                 )
display(pd.crosstab(trade_without_outliers_r['impute_base'], columns='Frequency', margins=True))
trade_without_outliers_r.rename(columns = {'price_4.0': 'base_price'}, inplace = True)
# Check if all have got prices
if len(trade_without_outliers_r.loc[trade_without_outliers_r['base_price'].isin([np.nan, np.inf])]) > 0:
    display(pd.crosstab(trade_without_outliers_r.loc[trade_without_outliers_r['base_price'].isin([np.nan, np.inf]), 'base_price'], columns='Frequency'))

