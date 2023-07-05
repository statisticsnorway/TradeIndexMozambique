# # Create base population

# ## Open parquet file

basedata = pd.read_parquet(f'../data/{flow}_{year}.parquet')

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

# ### Seasonal commodities

basedata = basedata.loc[(basedata['no_of_months'] >= no_of_months) | ((basedata['no_of_months'] >= no_of_months) &
                        (basedata['section'] == section_seasons))]
print(f'Number of commodities after selection of at least {no_of_months} months or seasonal commodities in section {section_seasons} with {no_of_months_seasons} or more months')
display(pd.crosstab(basedata['flow'], columns='Frequency', margins=True))

# ### price_cv

basedata = basedata.loc[(basedata['price_cv'] < price_cv)]
print(f'Number of commodities after selection of at those with price co-variance less than {price_cv}')
display(pd.crosstab(basedata['flow'], columns='Frequency', margins=True))

# ### max by min

basedata = basedata.loc[(basedata['max_by_min'] < max_by_min)]
print(f'Number of commodities after selection of at those with maximum by minimum less than {max_by_min}')
display(pd.crosstab(basedata['flow'], columns='Frequency', margins=True))

# ### max by median

basedata = basedata.loc[(basedata['max_by_median'] < max_by_median)]
print(f'Number of commodities after selection of at those with maximum by median less than {max_by_median}')
display(pd.crosstab(basedata['flow'], columns='Frequency', margins=True))

# ### median by min

basedata = basedata.loc[(basedata['median_by_min'] < median_by_min)]
print(f'Number of commodities after selection of at those with median by minimum less than {median_by_min}')
display(pd.crosstab(basedata['flow'], columns='Frequency', margins=True))

# ### share small

basedata = basedata.loc[(basedata['share_small'] < share_small)]
print(f'Number of commodities after selection of at those with share of small {share_small} or more')
display(pd.crosstab(basedata['flow'], columns='Frequency', margins=True))

# ## Import labels from json file

with open('../data/labels.json') as json_file:
    labels = json.load(json_file)
print(labels)


# ## Function to calculate the coverage
# As we calculate the coverage for different aggregation levels, we make a function for it

def coverage(df: pd.DataFrame, groupcol, aggcol) -> pd.DataFrame:
    result = df.groupby(['year', 'flow', groupcol]).agg(
        Ssample_sum=('HS_sum', 'sum'),
        Spop_sum=('S1_sum', 'mean'),
        Sno_of_comm=('S1_sum', 'size')
        )
    result['Tsample_sum'] = result.groupby(['year', 'flow'])['Ssample_sum'].transform('sum')
    result['Tpop_sum'] = result.groupby(['year', 'flow'])['Spop_sum'].transform('sum')
    result['Tno_of_comm'] = result.groupby(['year', 'flow'])['Sno_of_comm'].transform('sum')
    result['Scoverage'] = result['Ssample_sum'] * 100 / result['Spop_sum']
    result = result.replace(labels)
    return result


# ## Coverage on different aggregation levels

print('Coverage of section')
display(coverage(basedata, 'section', 'S_sum'))
print('Coverage of sitc 1')
display(coverage(basedata, 'sitc1', 'S1_sum'))
print('Coverage of sitc 2')
display(coverage(basedata, 'sitc2', 'S2_sum'))
