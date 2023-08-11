# # Base prices

# ## Add parquet files for the whole year together
# This will be all the data, including the outliers

data_dir = Path('../data')
trade = pd.concat(
    pd.read_parquet(parquet_file)
    for parquet_file in data_dir.glob(f'{flow}_{year}q*.parquet')
)
print(f'{trade.shape[0]} rows read from parquet files for {year}\n')

# ## Open the weight base for previous year and aggregate to section

weight_base = pd.read_parquet(f'../data/weight_base_{flow}_{year}.parquet')
print(f'{weight_base.shape[0]} rows read from parquet file ../data/weight_base_{flow}_{year}.parquet\n')

# ## Extract weight at commodity level

commodity_weights = (weight_base[weight_base.duplicated(['year', 'flow', 'comno'], keep='first') == False]
            .sort_values(['year', 'flow', 'comno'])                 
)
commodity_weights = commodity_weights[['year', 'flow', 'comno', 'Weight_HS']]

# ## Match the weight to the tradedata
# We use inner join because we only want to include those who are in the weight base

trade_with_weights = pd.merge(trade, commodity_weights, on=['year', 'flow', 'comno'], how='inner')

# ## Calculate the price
# We also calculate the median price by commodity

trade_with_weights['price'] = trade_with_weights['value'] / trade_with_weights['weight']
trade_with_weights['price_median'] = trade_with_weights.groupby(['flow', 'comno'])['price'].transform('median')

# ## Mark outliers

trade_with_weights['outlier'] = np.select([trade_with_weights['price'] / trade_with_weights['price_median'] < 0.3,
                                           trade_with_weights['price'] / trade_with_weights['price_median'] > 2.5,
                                           ],
                                          [1, 2],
                                          default=0
                                         )
display(pd.crosstab(trade_with_weights['outlier'], columns=trade_with_weights['flow'], margins=True))

# ## Extract those who are not outliers

# +
trade_without_outliers = trade_with_weights.loc[trade_with_weights['outlier'] == 0]

trade_without_outliers = trade_without_outliers.groupby(['year', 'quarter', 'flow', 'comno', 'section', 'Weight_HS'], 
                                                        as_index=False).agg(
    value_quarter=('value', 'sum'),
    weight_quarter=('weight', 'sum')
    )
trade_without_outliers['price'] = trade_without_outliers['value_quarter'] / trade_without_outliers['weight_quarter']
# -

# ## Transpose the data so it will be easier to impute missing prices

trade_without_outliers_r = trade_without_outliers.pivot(index=['year', 'flow', 'comno', 'section', 'Weight_HS'], 
                                                        columns='quarter', 
                                                        values= ['price']
                                                       )
trade_without_outliers_r.columns = trade_without_outliers_r.columns.get_level_values(0) + '_' + trade_without_outliers_r.columns.get_level_values(1).astype('str')
trade_without_outliers_r.reset_index(inplace=True)

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
                                                  trade_without_outliers_r['price_4.0'].isna().astype('int') + 1,
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
if len(trade_without_outliers_r.loc[trade_without_outliers_r['base_price'].isna()]) > 0:
    display(pd.crosstab(trade_without_outliers_r.loc[trade_without_outliers_r['base_price'].isna(), 'base_price'], columns='Frequency'))


# ## Save as parquet file

baseprice = trade_without_outliers_r[['year', 'flow', 'comno', 'base_price', 'impute_base']]
baseprice.to_parquet(f'../data/base_price{flow}_{year}.parquet')
print(f'\nNOTE: Parquet file ../data/base_price{flow}_{year}.parquet written with {baseprice.shape[0]} rows and {baseprice.shape[1]} columns\n')


