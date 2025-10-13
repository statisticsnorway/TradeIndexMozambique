# # Base prices

# ## Add parquet files for the whole year together
# This will be all the data, including the outliers

# + active=""
# import pandas as pd
# import numpy as np
# import json
# from pathlib import Path
# from itables import init_notebook_mode, show
# import matplotlib.pyplot as plt
# import seaborn as sns
# #pd.set_option('display.float_format',  '{:18,.0}'.format)
# pd.set_option('display.float_format', lambda x: f'{x:15,.0f}' if abs(x)>1e5 else f'{x:15.2f}')
# import itables
# # Initialize interactive display mode
# itables.init_notebook_mode(all_interactive=True)
#
# selected_outlier = 'outlier_sd'
# year = 2021
# flow = 'export'
# quarter = 4
# -

data_dir = Path('../data')
trade = pd.concat(
    pd.read_parquet(parquet_file)
    for parquet_file in data_dir.glob(f'{flow}_{year}_q*.parquet')
)
print()
print(f"\n===Tradedata for {flow} {year}===")
print()
print(f'{trade.shape[0]} rows read from parquet files for {year}\n')

# ### Check for more than one unique unit of measurement per comno

# +
import pandas as pd
import numpy as np

# Step 1: Count unique 'unit' per 'comno'
unit_counts = trade.groupby('comno')['unit'].nunique(dropna=False)

# Step 2: Identify comno with more than one unique unit
comno_multiple_units = unit_counts[unit_counts > 1].index.tolist()

if not comno_multiple_units:
    print("\n" + "="*80)
    print(f'Check if transaction data for each commodity have same unit of measurement in year {year}:')
    print("All commodities have a single unit of measurement.")
    print("\n" + "="*80)
else:
    print("\n" + "="*80)
    print("Commodities with more than one unit of measurement detected!")
    print("Can only have one unit of measurement. Keeping transactions with unit that have the highest total value.\n")

    # Step 3: Aggregate total value per comno and unit
    agg_value = trade.groupby(['comno', 'unit'], dropna=False)['value'].sum().reset_index()

    # Step 4: Tie-breaking — sort by value desc, then prefer non-NA
    agg_value['unit_is_na'] = agg_value['unit'].isna()
    agg_value = agg_value.sort_values(['comno', 'value', 'unit_is_na'], ascending=[True, False, True])

    # Step 5: Pick unit to keep for each comno
    max_unit = agg_value.drop_duplicates(subset='comno', keep='first')

    # Step 6: Filter both tables to only include comno with multiple units
    agg_value_multi = agg_value[agg_value['comno'].isin(comno_multiple_units)]
    max_unit_multi = max_unit[max_unit['comno'].isin(comno_multiple_units)]

    # Step 7: Identify removed units (everything except max_unit for multi-unit comno)
    removed_units = pd.merge(
        agg_value_multi,
        max_unit_multi[['comno', 'unit']],
        on=['comno', 'unit'],
        how='outer',
        indicator=True
    ).query('_merge == "left_only"').drop(columns=['_merge', 'unit_is_na'])

    # Step 8: Filter trade to keep only selected unit
    trade = trade.merge(max_unit[['comno', 'unit']], on=['comno', 'unit'], how='inner')

    # Step 9: Reporting — only comno with multiple units
    print("Transactions for comno with unit kept:")
    for _, row in max_unit_multi.iterrows():
        unit_display = 'NA' if pd.isna(row['unit']) else row['unit']
        print(f"Comno {row['comno']}: kept transactions with unit = {unit_display} (total value = {row['value']:.2f})")

    if not removed_units.empty:
        print("\nTransactions for comno with unit removed:")
        print("Take action to ensure comparisons are consistent between periods")
        for _, row in removed_units.iterrows():
            unit_display = 'NA' if pd.isna(row['unit']) else row['unit']
            print(f"Comno {row['comno']}: removed transactions with unit = {unit_display} (total value = {row['value']:.2f})")
    else:
        print("\nNo units removed (unexpected).")

    print("\n" + "="*80)


# +
# Extract unique comno-unit combinations
trade_unique = trade[['comno', 'unit']].drop_duplicates()

# Rename the column
trade_unique = trade_unique.rename(columns={'unit': 'unit_baseyear'})

# Save as Parquet file
trade_unique.to_parquet(f'../data/comno_unit_unique_{flow}_{year}.parquet', engine='pyarrow', index=False)
# -

# ## Open the weight base for previous year and aggregate to section

weight_base = pd.read_parquet(f'../data/weight_base_{flow}_{year}.parquet')
print()
print(f"\n===Weight data for {flow} {year}===")
print()
print(f'{weight_base.shape[0]} rows read from parquet file ../data/weight_base_{flow}_{year}.parquet\n')

# ## Extract weight at commodity level

commodity_weights = (weight_base[weight_base.duplicated(['year', 'flow', 'comno'], keep='first') == False]
            .sort_values(['year', 'flow', 'comno'])                 
)
commodity_weights = commodity_weights[['year', 'flow', 'comno', 'Weight_HS']]

# ## Match the weight to the tradedata
# We use inner join because we only want to include those who are in the weight base

trade_with_weights = pd.merge(trade, commodity_weights, on=['year', 'flow', 'comno'], how='inner')

# ## Delete outliers based on low number of transactions in month and low value

# +
print("\n" + "="*80)
print()
print(f'{flow.capitalize()}, {year}. Remove outliers in sample')

# Crosstab of frequencies
crosstab3 = pd.crosstab(index=trade_with_weights['outlier_n_test'], columns='Count', margins=True)

# Calculate relative percentages
crosstab3['Percentage (%)'] = ((crosstab3['Count'] / crosstab3.loc['All', 'Count']) * 100).map('{:.1f}'.format)

# Keep only 'Count' and 'Percentage (%)' columns
crosstab3 = crosstab3[['Count', 'Percentage (%)']]

# Print formatted output


print("The table below shows how many transactions were tagged as outliers based on number of transactions in month and value.")
print(f"According to conditions where number of transactions in month is below: {n_t_month} and transasction value below: {value_limit}, and n transactions in quarter below: {n_t_quarter}")
display(crosstab3)

# +
# Filter the DataFrame to keep only transactions where all specified conditions are False
trade_with_weights = trade_with_weights.loc[
    (trade_with_weights['outlier_n_test'] == False)

].copy()
# -

# ### Remvoe outliers based on selected test

# +
# Crosstab of frequencies outlier
crosstab = pd.crosstab(trade_with_weights[selected_outlier], columns='Frequency', margins=True)
# Calculate relative percentages
crosstab['Percentage (%)'] = ((crosstab['Frequency'] / crosstab.loc['All', 'Frequency']) * 100).map('{:.1f}'.format)
# Keep only 'Frequency' and 'Percentage (%)' columns
crosstab = crosstab[['Frequency', 'Percentage (%)']]
print("\n" + "="*80)
print()
print(f'{flow.capitalize()}, {year}. Frequencies of transactions tagged as outlier in sample and removed based on {selected_outlier} in sample')

display(crosstab)
# -

trade_with_weights_no_outliers = trade_with_weights.copy()

# +
# Filter the DataFrame to keep only transactions where all specified conditions are False
trade_with_weights_no_outliers = trade_with_weights_no_outliers.loc[
    (trade_with_weights_no_outliers[selected_outlier] == False)

].copy()
# -

# #### Aggregate up to month per HS

# +
#put in aggvars to compute isic
#'isic_section', 'isic_division', 'isic_group', 'isic_class',
# -

aggvars = ['year', 'flow', 'comno', 'quarter', 'month', 'section', 'chapter', 
           'sitc1', 'sitc2',  'hs6', 'Weight_HS']
tradedata_month_base = trade_with_weights_no_outliers.groupby(aggvars, dropna=False, as_index=False).agg(
    weight=('weight', 'sum'),
    value=('value', 'sum'),
    n_transactions = ('n_transactions', 'first')
)


print("\n" + "="*80)
print()
print(f'{flow.capitalize()}, {year}. Aggregated transaction data to month for sample')

# ## Calculate the price per month per HS and other measures
#

# +
tradedata_month_base['price'] = tradedata_month_base['value'] / tradedata_month_base['weight']

tradedata_month_base['price_median'] = tradedata_month_base.groupby(['flow', 'comno'])['price'].transform('median')
tradedata_month_base['price_sd'] = tradedata_month_base.groupby(['flow', 'comno'])['price'].transform('std')
tradedata_month_base['price_mean'] = tradedata_month_base.groupby(['flow', 'comno'])['price'].transform('mean')
# extra step: Calculate the standard deviation to mean ratio for each transaction
tradedata_month_base['price_mean_ratio'] = tradedata_month_base['price']/tradedata_month_base['price_mean']
tradedata_month_base['price_median_ratio'] = tradedata_month_base['price']/tradedata_month_base['price_median']
tradedata_month_base['price_sd_ratio'] = tradedata_month_base['price']/tradedata_month_base['price_sd']
tradedata_month_base['price_cv'] = tradedata_month_base['price_sd']/tradedata_month_base['price_mean']
show(tradedata_month_base, maxBytes=0)
# -

# ## Extreme price difference from median price per HS per month - Tag outliers

price_limit_median_low = 0.4
price_limit_median_high = 1.7

# +
tradedata_month_base['outlier_time'] = np.select(
    [
        tradedata_month_base['price'] / tradedata_month_base['price_median'] < price_limit_median_low,
        tradedata_month_base['price'] / tradedata_month_base['price_median'] > price_limit_median_high,
    ],
    [1, 2],
    default=0
)

print("\n" + "="*80)
print(f'Price control on monthly prices in baseyear for Flow: {flow.capitalize()}')
print(f'Monthly price change from median price in {year} per HS')
print("     0 = normal (within acceptable range of median)")
print(f"     1 = price < {price_limit_median_low} of median (too low)")
print(f"     2 = price > {price_limit_median_high} of median (too high)")

display(pd.crosstab(
    tradedata_month_base['outlier_time'],
    columns=tradedata_month_base['flow'],
    margins=True
))

# -

tradedata_month_base['outlier_time'] = tradedata_month_base['outlier_time'].apply(lambda x: True if x in [1, 2] else False)


# +
count_true_outliers = tradedata_month_base.groupby('comno')[['outlier_time']].sum()

print(f'Monthly prices per month tagged as outlier per commoditiy for year {year}:')
print(f'{flow.capitalize()}, {year}. Outliers')
display(count_true_outliers.loc[count_true_outliers['outlier_time'] == True])
print("\n" + "="*80)
# -

# ## Extract those who are not outliers

# ### Used in further calculation:

# +
# Filter the DataFrame to keep only transactions where all specified conditions are False
trade_without_outliers = tradedata_month_base.loc[
    (tradedata_month_base['outlier_time'] == False)

].copy()
# -

# ## Calculate the price per quarter per HS

# +
# Grouping trade_without_outliers by specified variables and aggregating value and weight
trade_without_outliers_r = trade_without_outliers.groupby(
    ['year', 'quarter', 'flow', 'comno', 'section', 'Weight_HS'], 
    as_index=False
).agg(
    value_quarter=('value', 'sum'),     # Sum the value for each group
    weight_quarter=('weight', 'sum')     # Sum the weight for each group
)

trade_without_outliers_r['price'] = trade_without_outliers_r['value_quarter'] / trade_without_outliers_r['weight_quarter']
# -

use_donor = 'no'

# ## Add donors

# +
import pandas as pd

# Load donor data or create empty DataFrame
if use_donor == 'yes':
    donor = pd.read_parquet('../cat/donors.parquet')
else:
    donor = pd.DataFrame(columns=["source", "comno", "flow"])  # 'flow' needed for melt

if not donor.empty:
    # Melt the data into long format
    df_long = donor.melt(
        id_vars=["source", "comno", "flow"],
        var_name="Period",
        value_name="price"
    ).copy()  # avoid SettingWithCopyWarning

    # Extract year and quarter
    df_long["year"] = df_long["Period"].str[:4]
    df_long["quarter"] = df_long["Period"].str[-1:].str.zfill(1)
    df_long["comno"] = df_long["comno"].astype(str)

    # Convert price to numeric safely and enforce float64
    df_long["price"] = pd.to_numeric(
        df_long["price"].astype(str).str.replace(",", ".", regex=False),
        errors='coerce'
    )

    # Select relevant columns and take a copy
    donor_pivot = df_long[["source", "comno", "year", "quarter", "price"]].copy()

else:
    # Empty DataFrame with correct dtypes
    donor_pivot = pd.DataFrame({
        "source": pd.Series(dtype='object'),
        "comno": pd.Series(dtype='object'),
        "year": pd.Series(dtype='object'),
        "quarter": pd.Series(dtype='object'),
        "price": pd.Series(dtype='float64')
    })

# ✅ Forward-compatible float64 enforcement
donor_pivot["price"] = donor_pivot["price"].astype('float64')



# +
# Merge to bring donor prices
merged = trade_without_outliers_r.merge(
    donor_pivot, 
    on=["comno", "year", "quarter"], 
    how="left", 
    suffixes=("", "_donor")
)

# Identify rows where price will be replaced
mask_replaced = merged["price_donor"].notna()

# Replace price with donor price where available
merged.loc[mask_replaced, "price"] = merged.loc[mask_replaced, "price_donor"]

# Print comno, source, and new price where replacement happened
print(f"Use price information from other sources - {use_donor}")
print("If yes, replace trade data with donor prices for selected commodities.")
print("\nRows where price was replaced with donor:")
print(merged.loc[mask_replaced, ["comno", "source", 'quarter']])
print()
print()
print("\n" + "="*80)
# Drop helper column
trade_without_outliers_r = merged.drop(columns=["price_donor"])
trade_without_outliers_r.rename(columns={'source': 'source_base'}, inplace=True)



# -

# ## Transpose the data so it will be easier to impute missing prices

# +
trade_without_outliers_r = trade_without_outliers_r.pivot(index=['year', 'flow', 'comno', 'section', 'Weight_HS', 'source_base'], 
                                                        columns='quarter', 
                                                        values= ['price']
                                                       )
trade_without_outliers_r.columns = trade_without_outliers_r.columns.get_level_values(0) + '_' + trade_without_outliers_r.columns.get_level_values(1).astype('str')
trade_without_outliers_r.reset_index(inplace=True)
print()
# Identify only the price columns
price_cols = [col for col in trade_without_outliers_r.columns if col.startswith("price_")]

# Filter rows with missing values in price columns only
missing_prices = trade_without_outliers_r.loc[trade_without_outliers_r[price_cols].isna().any(axis=1)]

print(f"{flow.capitalize()}, {year} - Commodities with missing quarterly prices in the base year:")
display(missing_prices)
print("\n" + "="*80)
# -

# ### Impute by section
# We calculate two price relatives:
#
# **price_rel_1** = Price change 3rd to 4th quarter
#
# **price_rel_2** = Price change 2rd to 4th quarter
#
# This we do to be able to impute 4th quarter prices for commodities that are also missing 3rd quarter price. We then use the price_rel_2 to impute the change from 2nd quarter.

# ## Compute values for price relatives and product

trade_without_outliers_r['price_rel_1'] = trade_without_outliers_r['price_4'] / trade_without_outliers_r['price_3']
trade_without_outliers_r['price_rel_2'] = trade_without_outliers_r['price_4'] / trade_without_outliers_r['price_2']
trade_without_outliers_r['product_1'] = trade_without_outliers_r['price_rel_1'] * trade_without_outliers_r['Weight_HS']
trade_without_outliers_r['product_2'] = trade_without_outliers_r['price_rel_2'] * trade_without_outliers_r['Weight_HS']

# ## Compute products aggregated to section

trade_without_outliers_r['prod_sum_1_section'] = trade_without_outliers_r.groupby(['year', 'flow', 'section'])['product_1'].transform('sum')
trade_without_outliers_r['prod_sum_2_section'] = trade_without_outliers_r.groupby(['year', 'flow', 'section'])['product_2'].transform('sum')

# ## Create weights by section for those who have value for product_1

trade_without_outliers_r['weight_section'] = trade_without_outliers_r['Weight_HS'] * trade_without_outliers_r['product_1'].notna()
trade_without_outliers_r['weight_section'] = trade_without_outliers_r.groupby(['year', 'flow', 'section'])['weight_section'].transform('sum')

# ## Impute prices for those who are missing
# Not all will necessarily get prices in this round

# +
# Step 1: initial flag — 1 if price_4 is missing, 0 otherwise
trade_without_outliers_r['impute_base'] = trade_without_outliers_r['price_4'].isna().astype(int)

# Step 2: count valid price_4 per (flow, section)
section_counts = trade_without_outliers_r.groupby(['flow','section'])['price_4'].transform(lambda x: x.notna().sum())

# Step 3: set impute=2 if price_4 is missing but section has < 2 valid commodities
trade_without_outliers_r['impute_base'] = np.where(
    (trade_without_outliers_r['impute_base'] == 1) & (section_counts < 2),
    2,
    trade_without_outliers_r['impute_base']
)

# Set prod_sum = 0 for rows with impute == 2 --> to avvoid imputing by section when number of commodities is below set limit.
trade_without_outliers_r.loc[trade_without_outliers_r['impute_base'] == 2, 'prod_sum_1_section'] = 0
trade_without_outliers_r.loc[trade_without_outliers_r['impute_base'] == 2, 'prod_sum_2_section'] = 0

# +
trade_without_outliers_r['price_4'] = np.where((trade_without_outliers_r['price_3'].notna()) &
                                               (trade_without_outliers_r['impute_base'] == 1),
                                               trade_without_outliers_r['price_3']*
                                               trade_without_outliers_r['prod_sum_1_section']/
                                               trade_without_outliers_r['weight_section'],
                                               trade_without_outliers_r['price_4']
                                              )
trade_without_outliers_r['price_4'] = np.where((trade_without_outliers_r['price_3'].isna()) &
                                               (trade_without_outliers_r['impute_base'] == 1),
                                                trade_without_outliers_r['price_2']*
                                                trade_without_outliers_r['prod_sum_2_section']/
                                                trade_without_outliers_r['weight_section'],
                                                trade_without_outliers_r['price_4']
                                              )

trade_without_outliers_r['price_rel_1'] =  np.where(trade_without_outliers_r['impute_base'] == 1,
                                trade_without_outliers_r['price_4'] / trade_without_outliers_r['price_3'],
                                trade_without_outliers_r['price_rel_1']
                               )  

trade_without_outliers_r['price_rel_2'] =  np.where(trade_without_outliers_r['impute_base'] == 1,
                                trade_without_outliers_r['price_4'] / trade_without_outliers_r['price_2'],
                                trade_without_outliers_r['price_rel_2']
                               )  



print("\n" + "="*80)
# -

# ### Impute by Total

# ## Compute products aggregated flow

trade_without_outliers_r['prod_sum_1_flow'] = trade_without_outliers_r.groupby(['year', 'flow'])['product_1'].transform('sum')
trade_without_outliers_r['prod_sum_2_flow'] = trade_without_outliers_r.groupby(['year', 'flow'])['product_2'].transform('sum')

# ## Create weights by flow for those who have value for product_1

trade_without_outliers_r['weight_flow'] = trade_without_outliers_r['Weight_HS'] * trade_without_outliers_r['product_1'].notna()
trade_without_outliers_r['weight_flow'] = trade_without_outliers_r.groupby(['year', 'flow'])['weight_flow'].transform('sum')

# ## Impute prices for those who are still missing
# All rows should have prices after these operations. It is checked with a table.

# +

trade_without_outliers_r['price_4'] = np.where((trade_without_outliers_r['price_3'].notna()) &
                                               (trade_without_outliers_r['impute_base'] == 2),
                                               trade_without_outliers_r['price_3']*
                                               trade_without_outliers_r['prod_sum_1_flow']/
                                               trade_without_outliers_r['weight_flow'],
                                               trade_without_outliers_r['price_4']
                                              )
trade_without_outliers_r['price_4'] = np.where((trade_without_outliers_r['price_3'].isna()) &
                                               (trade_without_outliers_r['impute_base'] == 2),
                                               trade_without_outliers_r['price_2']*
                                               trade_without_outliers_r['prod_sum_2_flow']/
                                               trade_without_outliers_r['weight_flow'],
                                               trade_without_outliers_r['price_4']
                                              )


trade_without_outliers_r['price_rel_1'] =  np.where(trade_without_outliers_r['impute_base'] == 2,
                                trade_without_outliers_r['price_4'] / trade_without_outliers_r['price_3'],
                                trade_without_outliers_r['price_rel_1']
                               )  

trade_without_outliers_r['price_rel_2'] =  np.where(trade_without_outliers_r['impute_base'] == 2,
                                trade_without_outliers_r['price_4'] / trade_without_outliers_r['price_2'],
                                trade_without_outliers_r['price_rel_2']
                               )  


print(f'{flow.capitalize()}, {year}. Number of imputations in base year using price change for section or flow')
print("Imputation flag (`impute_base`) explanation:")
print("    0 = price_4 already exists, no imputation needed")
print("    1 = price_4 was missing, imputation applied at section level.")
print("    2 = price_4 was missing, imputation applied at flow level.")
display(pd.crosstab(trade_without_outliers_r['impute_base'], columns='Frequency', margins=True))
trade_without_outliers_r.rename(columns = {'price_4': 'base_price'}, inplace = True)


# Show commodities where imputation was applied (price_4 missing originally)
print("\nCommodities with imputed prices in baseperiod, 4th quarter, by section or flow level:")
# Show commodities where imputation was applied (price_4 missing originally or section had <2 valid prices)
imputed_prices = trade_without_outliers_r.loc[
    (trade_without_outliers_r['impute_base'] == 1) | (trade_without_outliers_r['impute_base'] == 2)
]
display(imputed_prices)
print("\n" + "="*80)

# Check if all have prices
if len(trade_without_outliers_r.loc[trade_without_outliers_r['base_price'].isna() | np.isinf(trade_without_outliers_r['base_price'])]) > 0:
    # Display the frequency of NaN and inf values in 'base_price'
    problematic_prices = trade_without_outliers_r.loc[trade_without_outliers_r['base_price'].isna() | np.isinf(trade_without_outliers_r['base_price']), ['comno', 'base_price']]
    print('Could not impute --> missing baseprice')
    display(problematic_prices)
else:
    print(f'\n{flow.capitalize()}, {year}. After imputation: No missing base prices.\n')

print("\n" + "="*80)
# -

# # Save prices for whole baseyear

trade_without_outliers_r = trade_without_outliers_r.merge(trade_unique, on='comno', how='left')

trade_without_outliers_r.to_parquet(f'../data/prices_baseyear_{flow}_{year}.parquet')
print(f'\nNOTE: Parquet file ../data/prices_baseyear_{flow}_{year}.parquet written with {trade_without_outliers_r.shape[0]} rows and {trade_without_outliers_r.shape[1]} columns\n')

# ## Save as parquet file

baseprice = trade_without_outliers_r[['year', 'flow', 'comno', 'base_price', 'unit_baseyear', 'source_base', 'impute_base']]
baseprice.to_parquet(f'../data/base_price{flow}_{year}.parquet')
print(f'\nNOTE: Parquet file ../data/base_price{flow}_{year}.parquet written with {baseprice.shape[0]} rows and {baseprice.shape[1]} columns\n')
print("\n" + "="*80)

# ### Visualization of transactions per hs and monthly prices and outlier control time

# +
import matplotlib.pyplot as plt
import seaborn as sns
import ipywidgets as widgets
from IPython.display import display

# Ensure month is sorted numerically
def preprocess_dataset(dataset):
    dataset = dataset.sort_values(by='month')  # Sort by month (numeric)
    return dataset

# Preprocess datasets
trade_with_weights_no_outliers = preprocess_dataset(trade_with_weights_no_outliers)
tradedata_month_base = preprocess_dataset(tradedata_month_base)

# Function to filter data for a specific comno and plot it on given axes
def plot_transactions_for_comno(ax, dataset, comno_value, x_var, y_var, hue):
    filtered_data = dataset[dataset['comno'] == comno_value]
    sns.scatterplot(data=filtered_data, x=x_var, y=y_var, 
                    hue=hue, ax=ax, palette='muted', legend='full')
    ax.set_title(f'{flow.capitalize()}, {year}. Transactions for comno {comno_value} - Detection_method: {hue}')
    ax.set_xlabel(x_var)
    ax.set_ylabel(y_var)

# Function to update plots based on selected comno, dataset, and axes
def update_plot(comno_value, dataset_name, x_var, y_var):
    dataset = {
        'trade_with_weights': trade_with_weights,
        'trade_with_weights_no_outliers': trade_with_weights_no_outliers
    }[dataset_name]
    
    fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(14, 6))  # Only two plots now


    # Second plot
    plot_transactions_for_comno(axs[0], dataset, comno_value, x_var, y_var, selected_outlier)
    axs[0].set_title(f'{flow.capitalize()}, {year}. Transaction data - prices for comno {comno_value}')
    
    # Third plot
    plot_transactions_for_comno(axs[1], tradedata_month_base, comno_value, x_var, y_var, 'outlier_time')
    axs[1].set_title(f'{flow.capitalize()}, {year}. Monthly data - Unit values per month for comno {comno_value}')
    
    plt.tight_layout()
    plt.show()

# Specify the comno values and sort them
comno_values = sorted(trade_with_weights_no_outliers['comno'].unique().tolist())

# Define list of axis variables
axis_variables = ['price', 'trans_n', 'value', 'weight', 'month', 'quarter']

# Create widgets
comno_dropdown = widgets.Combobox(
    options=comno_values,
    value=str(comno_values[0]),
    description='Search comno:',
    layout=widgets.Layout(width='300px'),
    placeholder='Type or select a comno'
)

dataset_dropdown = widgets.Dropdown(
    options=['trade_with_weights', 'trade_with_weights_no_outliers'],
    value='trade_with_weights',
    description='Select dataset:',
    layout=widgets.Layout(width='300px')
)

x_dropdown = widgets.Dropdown(
    options=axis_variables,
    value='value',
    description='Select X:',
    layout=widgets.Layout(width='300px')
)

y_dropdown = widgets.Dropdown(
    options=axis_variables,
    value='price',
    description='Select Y:',
    layout=widgets.Layout(width='300px')
)

output = widgets.interactive_output(update_plot, {
    'comno_value': comno_dropdown,
    'dataset_name': dataset_dropdown,
    'x_var': x_dropdown,
    'y_var': y_dropdown
})

display(dataset_dropdown, comno_dropdown, x_dropdown, y_dropdown, output)

print("\n" + "="*80)
# -
print()
print("Final output")
print(f"Base prices for selected sample for year {year}")
print()
show(baseprice, maxBytes=0)





