# # Impute missing prices

# Calculate base year and previous quarter

year_base = year - 1
if quarter == 1:
    quarter_1 = 4
else:
    quarter_1 = quarter - 1

# ## Read parquet files

# +
if quarter == 1:
    basepricefile = f'../data/base_price{flow}_{year_1}.parquet'
else:
    basepricefile = f'../data/price_impute_{flow}_{year}Q{quarter_1}.parquet'

baseprice = pd.read_parquet(basepricefile)
print(f'{baseprice.shape[0]} rows read from parquet file {basepricefile}\n')

if quarter == 1:
    baseprice.rename(columns={'base_price': 'price'}, inplace=True)
    baseprice.drop(columns='impute_base', inplace=True)

baseprice['qrt'] = 0    

weightbasefile = f'../data/weight_base_{flow}_{year_base}.parquet'
weight_base = pd.read_parquet(weightbasefile)
print(f'{weight_base.shape[0]} rows read from parquet file {weightbasefile}\n')

tradedatafile = f'../data/tradedata_no_outlier_{flow}_{year}q{quarter}.parquet'
tradedata_no_outlier = pd.read_parquet(tradedatafile)
print(f'{tradedata_no_outlier.shape[0]} rows read from parquet file {tradedatafile}\n')
# -

# ## Aggregate

tradedata_no_outlier['qrt'] = 1
tradedata_qrt = tradedata_no_outlier.groupby(['year', 'flow', 'comno', 'qrt'], as_index=False).agg(
    value=('value', 'sum'),
    weight=('weight', 'sum')
)

# ## Add files together

tradedata_qrt['price'] = tradedata_qrt['value'] / tradedata_qrt['weight']
tradedata_qrts = pd.concat([baseprice, tradedata_qrt])
display(pd.crosstab(tradedata_qrts['qrt'], columns='Frequency', margins=True))

# ## Restructure file

qrt_r = tradedata_qrts.pivot(index=['flow', 'comno'], columns='qrt', values= ['price'])
qrt_r.columns = [f'{x}_{y}' for x, y in qrt_r.columns]
qrt_r = qrt_r.reset_index()

# ## Merge with weight_base

prices = pd.merge(weight_base, qrt_r, on=['flow', 'comno'], how='left')
prices.drop(columns=['year', 'quarter'], inplace=True)
prices['price_rel'] = prices['price_1'] / prices['price_0']
prices['product'] = prices['price_rel'] * prices['Weight_HS']
prices['prod_sum'] = prices.groupby(['flow', 'section'])['product'].transform('sum')
prices['Weight_section'] = prices['Weight_HS'] * (prices['product'].notna())
prices['Weight_section'] = prices.groupby(['flow', 'section'])['Weight_section'].transform('sum')

# ## Impute missing values on section level

# +
prices['impute'] = prices['price_1'].isna().astype(int)
prices['price_1'] =  np.where(prices['impute'] == 1,
                              prices['price_0'] * prices['prod_sum'] /  prices['Weight_section'],
                              prices['price_1']
                             )

prices['price_rel'] =  np.where(prices['impute'] == 1,
                                prices['price_1'] / prices['price_0'],
                                prices['price_rel']
                               )  
# -

# ## Impute missing values on flow level

# +
prices['prod_sum'] = prices.groupby(['flow'])['product'].transform('sum')

prices['Weight_flow'] = prices['Weight_HS'] * prices['product'].notna()
prices['Weight_flow'] = prices.groupby(['flow'])['Weight_flow'].transform('sum')

prices['impute'] = np.where(prices['impute'] == 1,
                            prices['price_1'].isna().astype(int) + 1,
                            prices['impute']
                           )

prices['price_1'] =  np.where(prices['impute'] == 2,
                              prices['price_0'] * prices['prod_sum'] /  prices['Weight_flow'],
                              prices['price_1']
                             )

prices['price_rel'] =  np.where(prices['impute'] == 2,
                                prices['price_1'] / prices['price_0'],
                                prices['price_rel']
                               )

display(pd.crosstab(prices['impute'], columns='Frequency', margins=True))
display(prices['price_1'].describe())
# -

# ## Save result as parquet file

# +
prices.drop(columns=['Weight_flow', 'price_0'], inplace=True)
prices.rename(columns={'price_1': 'price'}, inplace=True)
prices['year'] = year
prices['quarter'] = quarter

imputefile = f'../data/price_impute_{flow}_{year}q{quarter}.parquet'
prices.to_parquet(imputefile)
print(f'\nNOTE: Parquet file {imputefile} written with {prices.shape[0]} rows and {prices.shape[1]} columns\n')
