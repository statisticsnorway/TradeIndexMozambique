# # Create base population

# ## Open parquet file

basedata = pd.read_parquet(f'../data/{flow}_{year}.parquet')
basedata.info()

# ## Compute share of total

basedata['share_total'] = basedata['HS_sum'] / basedata['T_sum'] 
smaller = basedata.loc[basedata['share_total'] <= share_total]
valsum_ex_big = smaller.groupby('flow', as_index=False).agg(T_sum_small = ('value', 'sum'))

# ## Table of big commodities

print(f'Coomodities with share of total more than {share_total} for {flow} {year}')
display(pd.crosstab(basedata.loc[basedata['share_total'] > share_total, 'comno'], 
                    columns='Sum',
                    values=basedata['value'],
                    aggfunc='sum', margins=True))

# ## Add sum of small commodities to the trade data

basedata = pd.merge(basedata, valsum_ex_big, on='flow', how='left')

# ## Drop all the rows but the first within each comno to get data for the whole year

# +
basedata = (basedata[basedata.duplicated(['flow', 'comno'], keep='first') == False]
            .sort_values(['flow', 'comno'])
            .reset_index()
)

basedata.drop(columns=['price', 'month'], inplace=True)
