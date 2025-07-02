# # Price control
# Checking for extreme values

year_1 = year - 1

# ## Read parquet files
# Parquet file for current quarter

trade_quarter = pd.read_parquet(f'../data/{flow}_{year}q{quarter}.parquet')
print(f'{trade_quarter.shape[0]} rows read from parquet file ../data/{flow}_{year}q{quarter}.parquet\n')
base_price = pd.read_parquet(f'../data/base_price{flow}_{year-1}.parquet')
print(f'{base_price.shape[0]} rows read from parquet file ../data/base_price{flow}_{year-1}.parquet\n')
base_price.drop(columns='year', inplace=True)

# ## Match with base price file
# We will only keep those who are in both the quarter data and base price data

trade_quarter = pd.merge(trade_quarter, base_price, on=['flow', 'comno'], how='left', indicator=True)
print(f'Result of merge with base price for {flow}, for {year}q{quarter}:')
display(pd.crosstab(trade_quarter['_merge'], columns='Frequency', margins=True))
trade_quarter = trade_quarter.loc[trade_quarter['_merge'] == 'both']
trade_quarter.drop(columns='_merge', inplace=True)
trade_quarter['price'] = trade_quarter['value'] / trade_quarter['weight']
trade_quarter['price_chg'] = trade_quarter['price'] / trade_quarter['base_price']

# ## Check for outlier prices
# The limits are objects which values can be changed

trade_quarter['outlier'] = np.select([(trade_quarter['price'] / trade_quarter['base_price'] < price_limit_low),
                                     (trade_quarter['price'] / trade_quarter['base_price'] > price_limit_high),
                                     ],
                                     ['1', '2'],
                                   default='0')
display(pd.crosstab(trade_quarter['outlier'], columns='Frequency', margins=True))


# List outliers

print(f'Outliers for {flow}, {year}q{quarter}\n')
display(trade_quarter.loc[trade_quarter['outlier'].isin(['1','2'])])

# ## Delete outliers

tradedata_no_outlier = trade_quarter.loc[trade_quarter['outlier'] == '0']

#  ## Store the data as parquet file

tradedata_no_outlier.drop(columns='price_chg', inplace=True)
tradedata_no_outlier.to_parquet(f'../data/tradedata_no_outlier_{flow}_{year}q{quarter}.parquet')
print(f'\nNOTE: Parquet file ../data/tradedata_no_outlier_{flow}_{year}q{quarter}.parquet written with {tradedata_no_outlier.shape[0]} rows and {tradedata_no_outlier.shape[1]} columns\n')
