# # Read csv file from external trade and add some new columns

# ## Read csv file
# We use the pandas read_csv to import the file to a Python pandas dataframe. With the dtype parameter we decide the column types.

# + active=""
# !pip install upsetplot
# !pip install matplotlib-venn

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
#
# year = 2021
# quarter = 3
# flow = 'Export'
# outlier_dev_median = 3.5
# selected_outlier = 'outlier_sd'
#
# # Accepted treshold for standard deviation from mean (default=2)
# outlier_sd = 2
#
# import itables
#
# # Initialize interactive display mode
# itables.init_notebook_mode(all_interactive=True)
# -
# ## Read parquet files
# Parquet files with correspondances to sitc and section

t_section = pd.read_parquet(f'../data/{flow}_{year}q{quarter}.parquet')
print()
print(f"\n===Input data for {flow} {year}-Q{quarter}===")
print()
print(f'{t_section.shape[0]} rows read from parquet file ../data/{flow}_{year}q{quarter}.parquet\n')
print("\n" + "="*80)
print()

# ### Removal of obvious errors

#When the weight is 0 we delete the whole case.
t_section = t_section.loc[t_section['weight'] != 0]
#When the value is 0, we delete the whole case.
t_section = t_section.loc[t_section['value'] != 0]

# ### Count transactions per group

# +
# Count the number of transactions per HS (flow, comno, quarter)
t_section['n_transactions'] = t_section.groupby(['flow', 'comno', 'quarter'])['value'].transform('count')

# Count the number of transactions per HS (flow, comno, quarter)
t_section['n_transactions_month'] = t_section.groupby(['flow', 'comno', 'quarter', 'month'])['value'].transform('count')


# Step 2: Directly categorize the transaction counts within each comno
transaction_count_per_comno = t_section[['comno', 'n_transactions']].drop_duplicates()

# Define the categorization function
def categorize_transactions(count):
    if count < 3:
        return 'Less than 3 transactions in quarter'
    elif 3 <= count <= 10:
        return 'Between 3-10 transactions in quarter'
    elif 10 <= count <= 30:
        return 'Between 11-30 transactions in quarter'
    else:
        return 'Above 30 transactions in quarter'

# Apply the function to categorize transaction counts
transaction_count_per_comno['category'] = transaction_count_per_comno['n_transactions'].apply(categorize_transactions)

# Step 3: Create a frequency table for each category
frequency_table = transaction_count_per_comno.groupby('category').size().reset_index(name='frequency')

# Display the frequency table

print(f"{flow.capitalize()}. {year}-Q{quarter} - Distribution of HS codes by number of transactions")
print("Number of commodities - Categorized by number of transaction")


display(frequency_table)
print("="*80 + "\n")
# -

# ### Tag transactions where number of transactions in month is low or value below set target
# What we identify are transactions that have low value, and also where they are the only transaction in that month, and among a small number of transactions in the quarter. All conditions must apply for it to be removed.

# +
n_t_month = 2
n_t_quarter = 10
value_limit = 4000


t_section['outlier_n_test'] = False

#Reactivate if you want to aplly conditions
#t_section['outlier_n_test'] = (t_section['n_transactions_month'] < n_t_month) & (t_section['value'] < value_limit) & (t_section['n_transactions'] < n_t_quarter)

# +
# Crosstab of frequencies
crosstab3 = pd.crosstab(index=t_section['outlier_n_test'], columns='Count', margins=True)

# Calculate relative percentages
crosstab3['Percentage (%)'] = ((crosstab3['Count'] / crosstab3.loc['All', 'Count']) * 100).map('{:.1f}'.format)

# Keep only 'Count' and 'Percentage (%)' columns
crosstab3 = crosstab3[['Count', 'Percentage (%)']]

# Print formatted output

print(f"{flow.capitalize()}. {year}-Q{quarter}")
print("The table below shows how many transactions were tagged as outliers based on conditions: number of transactions and value.")
print(f"According to conditions where number of transactions in month is below: {n_t_month} and transaction value below: {value_limit}, and number transactions in quarter below: {n_t_quarter}")
display(crosstab3)


# -

# ### OUTLIER DETECTION - calculate mean, median and standard deviation per quarter
# by flow, HS, Quarter
# calculate standard deviation
# calculate deviation from the median
# Tag transactions 

# +
#COMPUTE PRICE PER TRANSACTION.
t_section['price'] = t_section['value']/t_section['weight']

#COMPUTE mean, median and standard deviation per HS per quarter.
df_agg = t_section.groupby(['flow', 'comno', 'quarter'], as_index=False).agg({
    'price': ['mean', 'median', 'std']
})

# Rename the resulting columns for clarity
df_agg.columns = ['flow', 'comno', 'quarter', 'price_mean', 'price_median', 'price_std']

# merge the results back into the original DataFrame
t_section = pd.merge(t_section, df_agg, on=['flow', 'comno', 'quarter'], how='left')
t_section
# -

# # Detection of outliers

# #### Standard deviations from the mean:
# Description: This method assesses how far each data point is from the mean (average) value of the dataset. It uses the concept of standard deviation, which measures the spread or variability of the data around the mean.
#
# The mean and standard deviation are both sensitive to extreme values. If the dataset already includes outliers, these values can distort the mean and increase the standard deviation, making the method less effective at detecting outliers. Sometimes it might be neccesary to do several rounds of cleaning the data whith this method.
#
# Bias Risk: Iterative cleaning can sometimes lead to over-cleaning. If the data has natural variability, repeated removal of outliers can distort the dataset, eliminating data points that may actually be valid.

# +
t_section['z_score'] = (t_section['price'] - t_section['price_mean']) / t_section['price_std']

def classify_outlier_SD(row):
    return abs(row['z_score']) > outlier_sd

# Apply the function to each row in the DataFrame t_section
t_section['outlier_sd'] = t_section.apply(classify_outlier_SD, axis=1)
# -


# #### Second round of removal outlier standard deviation

# #### Display result

# Remove outliers based on test standard deviation from mean
t_section2 = t_section.loc[
    (t_section['outlier_sd'] == False)
].copy()

# +
df_agg2 = t_section2.groupby(['flow', 'comno', 'quarter'], as_index=False).agg({
    'price': ['mean', 'median', 'std']
})

# Rename the resulting columns for clarity
df_agg2.columns = ['flow', 'comno', 'quarter', 'price_mean2', 'price_median2', 'price_std2']

# merge the results back into the original DataFrame
t_section = pd.merge(t_section, df_agg2, on=['flow', 'comno', 'quarter'], how='left')

# +
t_section['z_score2'] = (t_section['price'] - t_section['price_mean2']) / t_section['price_std2']

def classify_outlier_SD(row):
    return abs(row['z_score2']) > outlier_sd

# Apply the function to each row in the DataFrame t_section
t_section['outlier_sd2'] = t_section.apply(classify_outlier_SD, axis=1)
# -

#
#
#

# ### Absolute Deviation from Median (MAD)
# Description: The Median Absolute Deviation (MAD) measures the distance between each data point and the median of the dataset. It’s robust against outliers and skewed data because the median is less affected by extreme values than the mean.
#
# Skewed Data Impact: While MAD works well with skewed data, applying a strict threshold might disproportionately affect one tail of the distribution if the data is heavily skewed. This could result in an asymmetrical bias, where one side of the distribution is more affected than the other.

# +
# Calculate the deviation from median for for each transaction
t_section['deviation_from_median'] = (t_section['price'] - t_section['price_median'])

# Calculate the absolute deviation
t_section['abs_deviation'] = t_section['deviation_from_median'].abs()

# Calculate MAD (Median Absolute Deviation) for each group
df_agg2 = t_section.groupby(['flow', 'comno', 'quarter'], as_index=False).agg({
    'abs_deviation': ['median']
})

# Rename the resulting columns for clarity
df_agg2.columns = ['flow', 'comno', 'quarter', 'MAD']

# Merge the results back into the original DataFrame
t_section = pd.merge(t_section, df_agg2, on=['flow', 'comno', 'quarter'], how='left') 

# Calculate the modified Z-score using the deviation from median
t_section['modified_z'] = 0.6745 * t_section['deviation_from_median'] / t_section['MAD']


# +
def classify_outlier_MAD(row):
    return abs(row['modified_z']) > outlier_dev_median

# Apply the function to each row in the DataFrame t_section
t_section['outlier_MAD'] = t_section.apply(classify_outlier_MAD, axis=1)
# -


# #### Display result

# +

# Check if column exists in t_section
if selected_outlier not in t_section.columns:
    raise ValueError(f"Column '{selected_outlier}' not found in t_section")

# Crosstab of frequencies
crosstab2 = pd.crosstab(index=t_section[selected_outlier], columns='Count', margins=True)

# Calculate relative percentages
crosstab2['Percentage (%)'] = ((crosstab2['Count'] / crosstab2.loc['All', 'Count']) * 100).map('{:.1f}'.format)

# Keep only 'Count' and 'Percentage (%)' columns
crosstab2 = crosstab2[['Count', 'Percentage (%)']]

# Print formatted output

print(f"{flow.capitalize()}. {year}-Q{quarter}")
print("The table below shows how many transactions were tagged as outliers")
print(f"according to '{selected_outlier}', along with their relative share (%).")
display(crosstab2)

# -


# ### Plot of number of outliers for each detection method
# (not in use at the moment)

# + active=""
# import matplotlib.pyplot as plt
#
# # Count outliers for each method
# outlier_counts = {
#     'MAD': t_section['outlier_MAD'].sum(),
#     'SD': t_section['outlier_sd'].sum(),
#     'SD2': t_section['outlier_sd2'].sum()
# }
#
# # Create a bar plot
# plt.figure(figsize=(8, 6))
# plt.bar(outlier_counts.keys(), outlier_counts.values())
# plt.title(f'{flow.capitalize()}, {year} quarter {quarter}: Number of Outliers Detected by Each Method')
# plt.xlabel('Outlier Detection Method')
# plt.ylabel('Number of Outliers')
# plt.show()
# -

# #### Remove columns not in use

# +
# Define the columns to be removed
columns_to_remove = [
    'price_mean', 'price_median', 'price_std', 
    'deviation_from_median', 'abs_deviation', 
    'MAD', 'modified_z', 'z_score', 
    'price_mean2', 'price_median2', 
    'price_std2', 'z_score2', 'n_transactions_month'
]

# Remove the specified columns from t_section
t_section = t_section.drop(columns=columns_to_remove)
# -

# ## Save as parquet
# The quarter file is save as a parquet file

t_section.to_parquet(f'../data/{flow}_{year}_q{quarter}.parquet')
print()
print('Final output:')
print(f'\nNOTE: Parquet file ../data/{flow}_{year}q{quarter}.parquet written with {t_section.shape[0]} rows and {t_section.shape[1]} columns\n')
print("\n" + "="*80)
