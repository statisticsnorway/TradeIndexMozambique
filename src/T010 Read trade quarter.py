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
    na_values={'.',' .'}
)

# ## Read parquet files
# Parquet files with correspondances to sitc and section

sitccat = pd.read_parquet('../data/commodity_sitc.parquet')
sectioncat = pd.read_parquet('../data/chapter_section.parquet')

# ## Merge trade data with sitc catalog
# We add sitc and sitc2 from the correspondance table

t_sitc = pd.merge(tradedata, sitccat, on='comno', how='left', indicator=True)
print(f'Result of merge with sitc catalog for {flow}, for {year}q{quarter}:')
display(pd.crosstab(t_sitc['_merge'], columns='Frequency', margins=True))
t_sitc.drop(columns='_merge', inplace=True)

# ## Merge trade data with sitc catalog
# We add sitc and sitc2 from the correspondance table

t_sitc['chapter'] = t_sitc['comno'].str[0:2]
t_section = pd.merge(t_sitc, sectioncat, on='chapter', how='left', indicator=True)
print(f'Result of merge with chapter catalog for {flow}, for {year}q{quarter}:')
display(pd.crosstab(t_section['_merge'], columns='Frequency', margins=True))
t_section.drop(columns='_merge', inplace=True)

# ## Add a quarter column 

t_section['quarter'] = t_section['month'].astype(int) / 3
t_section['quarter'] = np.trunc(t_section['quarter']) + (t_section['quarter'] > np.trunc(t_section['quarter']))

# ## Save as parquet
# The quarter file is save as a parquet file

t_section.to_parquet(f'../data/{flow}_{year}q{quarter}.parquet')
print(f'\nNOTE: Parquet file ../data/{flow}_{year}q{quarter}.parquet written\n')
