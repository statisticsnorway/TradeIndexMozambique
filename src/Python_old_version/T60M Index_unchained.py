# # Create unchained index

# ## Read parquet file with unchained indexes for previous quarter(s)
# This is done from quarter 2 every year

if quarter > 1:
    indexunchainedfile = f'../data/index_unchained_{year}.parquet'
    index_unchained_previous = pd.read_parquet(indexcommodityfile)
    print(print(f'{index_unchained_previous.shape[0]} rows read from parquet file {indexunchainedfile}\n'))

# Calculate base year as the previous year

year_base = year - 1

# ## Read parquet files

# +
imputefile = f'../data/price_impute_{flow}_{year}q{quarter}.parquet'
price_impute = pd.read_parquet(imputefile)
print(f'{price_impute.shape[0]} rows read from parquet file {imputefile}\n')

basepricefile = f'../data/base_price{flow}_{year_1}.parquet'
baseprice = pd.read_parquet(basepricefile)
print(f'{baseprice.shape[0]} rows read from parquet file {basepricefile}\n')
baseprice.drop(columns='year', inplace=True)
# -

# ## Merge prices with base prices

prices = pd.merge(price_impute, baseprice, on=['flow', 'comno'], how='left', indicator=True)
display(pd.crosstab(prices['_merge'], columns='Frequency', margins=True))
prices.drop(columns='_merge', inplace=True)

# ## Calculate unchained index and index weight for commodities

prices['index_unchained'] = prices['price'] / prices['base_price'] * 100
prices['index_weight'] = prices['index_unchained'] * prices['Weight_HS']
prices['level'] = 'Commodity'
prices['series'] = prices['comno']


# ## Function for creating unchained index for a series

def unchained(dataframe, groupvars:list, level, series):
    index_agg = dataframe.groupby(groupvars, as_index=False).agg(
        Weight_HS=('Weight_HS', 'sum'),
    index_weight=('index_weight', 'sum')
    )
    index_agg['index_unchained'] = index_agg['index_weight'] / index_agg['Weight_HS']
    index_agg['level'] = level
    index_agg['series'] = index_agg[series]
    return index_agg


# ## Unchained index for section

# +
#index_agg = prices.groupby(['year', 'quarter', 'flow', 'section'], as_index=False).agg(
#    Weight_HS=('Weight_HS', 'sum'),
#    index_weight=('index_weight', 'sum')
#)
#index_agg['index_unchained'] = index_agg['index_weight'] / index_agg['Weight_HS']
#index_agg['level'] = 'Section'
#index_agg['series'] = 'section'

index_section = unchained(prices, groupvars=['year', 'quarter', 'flow', 'section'], level='Section', series='section')
# -

# ## Unchained index for total

index_total = unchained(prices, groupvars=['year', 'quarter', 'flow'], level='Total', series='flow')

# ## Unchained index for sitc1 and sitc2

index_sitc1 = unchained(prices, groupvars=['year', 'quarter', 'flow', 'sitc1'], level='Sitc1', series='sitc1')
index_sitc2 = unchained(prices, groupvars=['year', 'quarter', 'flow', 'sitc2'], level='Sitc2', series='sitc2')

# ## Add index files together

indexes = [prices, index_section, index_sitc1, index_sitc2, index_total]
index_unchained = pd.concat(indexes)
varlist = ['flow', 'year', 'quarter', 'index_unchained', 'level', 'series']
index_unchained = index_unchained[varlist]

# ## Add indexes to previous quarters
# We will also delete previous version if a quarter is executed again

if quarter > 1:
    index_unchained = pd.concat([index_unchained, index_unchained_previous])
    groupvars = ['flow', 'level', 'series', 'year', 'quarter']
    index_unchained = index_unchained[index_unchained.duplicated(groupvars, keep='last') == False].sort_values(groupvars)

display(pd.crosstab([index_unchained['level'], index_unchained['series']], 
                    columns=[index_unchained['year'], index_unchained['quarter']],
                             values=index_unchained['index_unchained'],
                             aggfunc='mean'))

# ## Save result as parquet file

indexcommodityfile = f'../data/index_unchained_{year}.parquet'
index_unchained.to_parquet(indexcommodityfile)
print(f'\nNOTE: Parquet file {indexcommodityfile} written with {index_unchained.shape[0]} rows and {index_unchained.shape[1]} columns\n')
