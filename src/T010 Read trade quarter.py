# # Read csv file from external trade and add some new columns

# ## Read csv file
# We use the pandas read_csv to import the file to a Python pandas dataframe. With the dtype parameter we decide the column types.

tradedata = pd.read_csv(
    f'../data/{flow} - {year}_XPMI_Q{quarter}.csv',
    header=0,
    sep=',',
    decimal='.',
    dtype={
        'flow': 'object',
        'year': 'object',
        'month': 'object',
        'ref': 'object',
        'ItemID': 'object',
        'comno': 'object',
        'country': 'object',
        'unit': 'object',
        'weight': 'float',
        'quantity': 'float',
        'value': 'float',
        'valUSD': 'float',
        'itemno': 'object',
        'exporterNUIT': 'object'
        },
    na_values={'.',' .'},
    encoding= 'unicode_escape'
)
tradedata['comno'] = tradedata['comno'].str.strip()
print(f'{tradedata.shape[0]} rows read from parquet csv ../data/{flow} - {year}_XPMI_Q{quarter}.csv\n')

# ## Read parquet files
# Parquet files with correspondances to sitc and section

sitccat = pd.read_parquet('../data/commodity_sitc.parquet')
print(f'{sitccat.shape[0]} rows read from parquet file ../data/commodity_sitc.parquet\n')
sectioncat = pd.read_parquet('../data/chapter_section.parquet')
print(f'{sectioncat.shape[0]} rows read from parquet file ../data/sectioncat.parquet\n')

# ## Merge trade data with sitc catalog
# We add sitc and sitc2 from the correspondance table

t_sitc = pd.merge(tradedata, sitccat, on='comno', how='left', indicator=True)
print(f'Result of merge with sitc catalog for {flow}, for {year}q{quarter}:')
display(pd.crosstab(t_sitc['_merge'], columns='Frequency', margins=True))
if len(t_sitc.loc[t_sitc['_merge'] == 'left_only']) > 0:
    print(f'List of commodity numbers that do not have sitc code for {flow}, for {year}q{quarter}:')
    display(pd.crosstab(t_sitc.loc[t_sitc['_merge'] == 'left_only', 'comno'], columns='Frequency', margins=True))
t_sitc.drop(columns='_merge', inplace=True)

# ## Merge trade data with chapter catalog
# We add section from the correspondance table

t_sitc['chapter'] = t_sitc['comno'].str[0:2]
t_section = pd.merge(t_sitc, sectioncat, on='chapter', how='left', indicator=True)
print(f'Result of merge with chapter catalog for {flow}, for {year}q{quarter}:')
display(pd.crosstab(t_section['_merge'], columns='Frequency', margins=True))
if len(t_section.loc[t_section['_merge'] == 'left_only']) > 0:
    print(f'List of chapters that do not have section code for {flow}, for {year}q{quarter}:')
    display(pd.crosstab(t_section.loc[t_section['_merge'] == 'left_only', 'chapter'], columns='Frequency', margins=True))
t_section.drop(columns='_merge', inplace=True)

# ## Add a quarter column 

t_section['quarter'] = t_section['month'].astype(int) / 3
t_section['quarter'] = (np.trunc(t_section['quarter']) + (t_section['quarter'] > np.trunc(t_section['quarter']))).astype('str')

# ## Set weight to at least 1
# When the weight is 0 we set it to 1 as suggested by INE.

t_section['weight'] = np.where(t_section['weight'] == 0, 1, t_section['weight'])

# ## Choose whether to use weight or quantity for the amount
# For 27160000 we choose quantity

quant_vars = ['27160000']
t_section['weight'] = np.where(t_section['comno'].isin(quant_vars), t_section['quantity'], t_section['weight'])

# ## Save as parquet
# The quarter file is save as a parquet file

t_section.to_parquet(f'../data/{flow}_{year}q{quarter}.parquet')
print(f'\nNOTE: Parquet file ../data/{flow}_{year}q{quarter}.parquet written with {t_section.shape[0]} rows and {t_section.shape[1]} columns\n')
