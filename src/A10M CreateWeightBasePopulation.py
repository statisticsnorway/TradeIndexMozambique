# # Create weight base population

# ## Add parquet files for the whole year together

data_dir = Path('../data')
tradedata = pd.concat(
    pd.read_parquet(parquet_file)
    for parquet_file in data_dir.glob(f'{flow}_{year}q*.parquet')
)
print(f'{tradedata.shape[0]} rows read from parquet files for {year}\n')
tradedata['price'] = tradedata['value'] / tradedata['weight']

# ## List rows where price is set to Infinity

print(f'This list shows rows where price could not be calculated. It should be empty.\n')
display(tradedata.loc[np.isinf(tradedata['price'])])

# ## Add std and mean at commodity level
# We actually don't need these to, except for control

tradedata['sd_comno'] = tradedata.groupby(['flow', 'comno'])['price'].transform('std')
tradedata['mean_comno'] = tradedata.groupby(['flow', 'comno'])['price'].transform('mean')

# ## Delete outliers
# The limit is set before we run this syntax. We use axis=0 to avoid a lot of messages

# This calculates the 2*std inncorrect
#tradedata['outlier_price'] = (
#    tradedata.groupby(['flow', 'comno'], as_index=False)['price']
#    .transform(lambda x: abs(x - np.mean(x, axis=0) > outlier_limit * np.std(x))).astype(int)
#)
tradedata['outlier_price'] = np.where((abs(tradedata['price'] - tradedata['mean_comno']) > (2 * tradedata['sd_comno'])), 1, 0)
print(f'Value of price outliers for {flow} in {year} for comno price with limit {outlier_limit}')
display(
    (pd.crosstab(tradedata['outlier_price'], 
                 columns='Sum', 
                 values=tradedata['valUSD'], 
                 margins=True, 
                 aggfunc='sum')
    .style.format('{:.0f}')
    )
)
display(tradedata.groupby('outlier_price').agg(
    valUSD_count=('valUSD', 'count'),
    valUSD_mean=('valUSD', 'mean'),
    valUSD_sum=('valUSD', 'sum'),
    valUSD_std=('valUSD', 'std')
    )
)        
print(f'List of price outliers for {flow} in {year} for comno price with limit {outlier_limit}')
display(tradedata.loc[tradedata['outlier_price'] == 1])
tradedata = tradedata.loc[tradedata['outlier_price'] == 0]
#tradedata.drop(columns=['outlier_price', 'sd_comno', 'mean_comno'], inplace=True)

# ## Add columns for to check for homogenity in the data
# These columns will be checked against the edge values that we choose

tradedata['no_of_months'] = tradedata.groupby(['flow', 'comno'])['month'].transform('count')
tradedata['price_max'] = tradedata.groupby(['flow', 'comno'])['price'].transform('max')
tradedata['price_min'] = tradedata.groupby(['flow', 'comno'])['price'].transform('min')
tradedata['price_median'] = tradedata.groupby(['flow', 'comno'])['price'].transform('median')
tradedata['price_mean'] = tradedata.groupby(['flow', 'comno'])['price'].transform('mean')
tradedata['price_sd'] = tradedata.groupby(['flow', 'comno'])['price'].transform('std')
tradedata['price_cv'] = tradedata['price_sd'] / tradedata['price_mean']
tradedata['T_sum'] = tradedata.groupby(['flow'])['value'].transform('sum')
tradedata['HS_sum'] = tradedata.groupby(['flow', 'comno'])['value'].transform('sum')
tradedata['S_sum'] = tradedata.groupby(['flow', 'section'])['value'].transform('sum')
tradedata['C_sum'] = tradedata.groupby(['flow', 'chapter'])['value'].transform('sum')
tradedata['S1_sum'] = tradedata.groupby(['flow', 'sitc1'])['value'].transform('sum')
tradedata['S2_sum'] = tradedata.groupby(['flow', 'sitc2'])['value'].transform('sum')

# ## Save as parquet file

tradedata.to_parquet(f'../data/{flow}_{year}.parquet')
print(f'\nNOTE: Parquet file ../data/{flow}_{year}.parquet written with {tradedata.shape[0]} rows and {tradedata.shape[1]} columns\n')
