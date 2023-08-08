# # Create base population

# ## Open parquet file

basedata = pd.read_parquet(f'../data/{flow}_{year}.parquet')
print(f'{basedata.shape[0]} rows read from parquet file ../data/{flow}_{year}.parquet\n')

# ## Compute share of total

basedata['share_total'] = basedata['HS_sum'] / basedata['T_sum'] 
smaller = basedata.loc[basedata['share_total'] <= share_total]
valsum_ex_big = smaller.groupby('flow', as_index=False).agg(T_sum_small = ('value', 'sum'))

# ## Table of big commodities

print(f'Coomodities with share of total more than {share_total} for {flow} {year}')
big = basedata.loc[basedata['share_total'] > share_total]
display(pd.crosstab(big['comno'], 
                    columns='Sum',
                    values=big['value'],
                    aggfunc='sum', margins=True))

# ## Add sum of small commodities to the trade data

basedata = pd.merge(basedata, valsum_ex_big, on='flow', how='left')

# ## Drop all the rows but the first within each comno to get data for the whole year

# +
basedata = (basedata[basedata.duplicated(['flow', 'comno'], keep='first') == False]
            .sort_values(['flow', 'comno'])
)

basedata.drop(columns=['price', 
                       'month', 
                       'ref', 
                       'ItemID', 
                       'country', 
                       'unit', 
                       'weight', 
                       'quantity',
                       'value',
                       'valUSD',
                       'itemno',
                       'exporterNUIT'
                      ], inplace=True)
# -

# ## Calculate new columns
# the share the small have of the total within the commodities and more

basedata['share_small'] = basedata['HS_sum'] / basedata['T_sum_small']
basedata['max_by_min'] = basedata['price_max'] / basedata['price_min']
basedata['max_by_median'] = basedata['price_max'] / basedata['price_median']
basedata['median_by_min'] = basedata['price_median'] / basedata['price_min']

# ## Select the sample for the index
# We start with an overview of the original number of comodities

print(f'Number of commodities before selection')
display(pd.crosstab(basedata['flow'], columns='Frequency', margins=True))

# ### Extract those with enough months and Seasonal commodities

basedata = basedata.loc[(basedata['no_of_months'] >= no_of_months) | ((basedata['no_of_months'] >= no_of_months_seasons) &
                        (basedata['section'] == section_seasons))]
print(f'Number of commodities after selection of at least {no_of_months} months or seasonal commodities in section {section_seasons} with {no_of_months_seasons} or more months')
display(pd.crosstab(basedata['flow'], columns='Frequency', margins=True))

# ### price_cv

basedata = basedata.loc[(basedata['price_cv'] < price_cv)]
print(f'Number of commodities after selection of those with price co-variance less than {price_cv}')
display(pd.crosstab(basedata['flow'], columns='Frequency', margins=True))

# ### max by min

basedata = basedata.loc[(basedata['max_by_min'] < max_by_min)]
print(f'Number of commodities after selection of those with maximum by minimum less than {max_by_min}')
display(pd.crosstab(basedata['flow'], columns='Frequency', margins=True))

# ### max by median

basedata = basedata.loc[(basedata['max_by_median'] < max_by_median)]
print(f'Number of commodities after selection of those with maximum by median less than {max_by_median}')
display(pd.crosstab(basedata['flow'], columns='Frequency', margins=True))

# ### median by min

basedata = basedata.loc[(basedata['median_by_min'] < median_by_min)]
print(f'Number of commodities after selection of those with median by minimum less than {median_by_min}')
display(pd.crosstab(basedata['flow'], columns='Frequency', margins=True))

# ### share small

basedata = basedata.loc[(basedata['share_small'] > share_small)]
print(f'Number of commodities after selection of those with share of small {share_small} or more')
display(pd.crosstab(basedata['flow'], columns='Frequency', margins=True))

# ## Import labels from json file

with open('../data/labels.json') as json_file:
    labels = json.load(json_file)
labels


# ## Function to calculate the coverage
# As we calculate the coverage for different aggregation levels, we make a function for it

def coverage(df: pd.DataFrame, groupcol, aggcol) -> pd.DataFrame:
    result = df.groupby(['year', 'flow', groupcol], as_index=False).agg(
        Ssample_sum=('HS_sum', 'sum'),
        spop_sum=(aggcol, 'mean'),
        Sno_of_comm=(aggcol, 'size')
        )
    result['Tsample_sum'] = result.groupby(['year', 'flow'])['Ssample_sum'].transform('sum')
    result['Tpop_sum'] = result.groupby(['year', 'flow'])['spop_sum'].transform('sum')
    result['Tno_of_comm'] = result.groupby(['year', 'flow'])['Sno_of_comm'].transform('sum')
    result['Scoverage'] = result['Ssample_sum'] * 100 / result['spop_sum']
    result['Tcoverage'] = result['Tsample_sum'] * 100 / result['Tpop_sum']
    result = result.replace(labels)
    return result


# ## Coverage on different aggregation levels

print('Coverage of section')
display(coverage(basedata, 'section', 'S_sum'))
print('Coverage of sitc 1')
display(coverage(basedata, 'sitc1', 'S1_sum'))
print('Coverage of sitc 2')
display(coverage(basedata, 'sitc2', 'S2_sum'))

# ## Keep only columns that will be used later

keepcol = ['flow',
           'year',
           'comno',
           'sitc1',
           'sitc2',
           'chapter',
           'section',
           'quarter',
           'T_sum',
           'HS_sum',
           'S_sum',
           'C_sum',
           'S1_sum',
           'S2_sum'
           ]
basedata = basedata[keepcol]


# ## Function to calculate weights

def calculate_weights(df:pd.DataFrame, level, aggcol, mult1, mult2, weight) -> pd.DataFrame:
    result = (df[df.duplicated(['year', 'flow', level], keep='first') == False]
            .sort_values(['year', 'flow', level])
    )
    if level == 'section':
        result[aggcol] = result.groupby(['year', 'flow'])[mult2].transform('sum')
    else:
        result[aggcol] = result.groupby(['year', 'flow', 'section'])[mult2].transform('sum')
    result[weight] = result[mult1] * result[mult2] / result[aggcol]
    result = result[['year', 'flow', level, aggcol, weight]]
    return result


# ## Calculate weights for section

section_weights = calculate_weights(basedata, 
                                    level='section', 
                                    aggcol='Tsample_sum', 
                                    mult1='T_sum', 
                                    mult2='S_sum',
                                    weight='Weight_S'
                                   )

# ## Add section weights to weight data

basedata = pd.merge(basedata, section_weights, on=(['year', 'flow', 'section']), how='left')

# ## Calculate weights for chapter

chapter_weights = calculate_weights(basedata, 
                                    level='chapter', 
                                    aggcol='Ssample_sum', 
                                    mult1='Weight_S', 
                                    mult2='C_sum',
                                    weight='Weight_C'
                                   )                                 

# ## Add chapter weights to weight data

basedata = pd.merge(basedata, chapter_weights, on=(['year', 'flow', 'chapter']), how='left')

# ## Calculate weight_HS
# This is the weight for commodities

basedata['Csample_sum'] = basedata.groupby(['year', 'flow', 'chapter'])['HS_sum'].transform('sum')
basedata['Weight_HS'] = basedata['Weight_C'] * basedata['HS_sum'] / basedata['Csample_sum']

# ## Save as parquet file

basedata.to_parquet(f'../data/weight_base_{flow}_{year}.parquet')
print(f'\nNOTE: Parquet file ../data/weight_base_data/{flow}_{year}.parquet written with {basedata.shape[0]} rows and {basedata.shape[1]} columns\n')
