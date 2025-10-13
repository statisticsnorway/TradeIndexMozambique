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
#
# import itables
# # Initialize interactive display mode
# itables.init_notebook_mode(all_interactive=True)
# init_notebook_mode(all_interactive=True)
#
# year = 2025
# quarter = 1
# flow = 'import'
# price_limit_low = 0.5
# price_limit_high = 1.5
# selected_outlier = 'outlier_sd'
#
# -
# # Price control
# Checking for extreme values

year_1 = year - 1

# ## Read parquet files
# Parquet file for current quarter

print()
print(f"\n===Tradedata and baseprices for {flow} {year}-Q{quarter}===")
print()
trade_quarter = pd.read_parquet(f'../data/{flow}_{year}_q{quarter}.parquet')
print(f'{trade_quarter.shape[0]} rows read from parquet file ../data/{flow}_{year}_q{quarter}.parquet\n')
base_price = pd.read_parquet(f'../data/base_price{flow}_{year-1}.parquet')
print(f'{base_price.shape[0]} rows read from parquet file ../data/base_price{flow}_{year-1}.parquet\n')
base_price.drop(columns='year', inplace=True)

# ## Match with base price file
# We will only keep those who are in both the quarter data and base price data

# +

trade_quarter = pd.merge(trade_quarter, base_price, on=['flow', 'comno'], how='left', indicator=True)
print("\n" + "="*80)
print()
print(f'Result of merge with base price for {flow}, for {year}q{quarter}:')
display(pd.crosstab(trade_quarter['_merge'], columns='Frequency', margins=True))

trade_quarter = trade_quarter.loc[trade_quarter['_merge'] == 'both']
trade_quarter.drop(columns='_merge', inplace=True)

trade_quarter['price'] = trade_quarter['value'] / trade_quarter['weight']
trade_quarter['price_chg'] = trade_quarter['price'] / trade_quarter['base_price']
# -

# ### Check if unit of measurement is different from baseyear
# Remove commodities due to unit mismatch with base year.
#
# Take action if possible to reconcile different units of measurement:

# +
import pandas as pd

# Step 1: Fill missing values with placeholder for comparison
trade_quarter['unit_filled'] = trade_quarter['unit'].fillna('NA')
trade_quarter['unit_base_filled'] = trade_quarter['unit_baseyear'].fillna('NA')
trade_quarter['unit_match'] = trade_quarter['unit_filled'] == trade_quarter['unit_base_filled']

# Step 2: Identify comno with mismatches
mismatched_comno = trade_quarter.loc[~trade_quarter['unit_match'], 'comno'].unique()

if len(mismatched_comno) == 0:
    print("\n" + "="*80)
    print()
    print('Check if unit of measurement is different from baseyear')
    print("No transactions for commodities removed. All units match the base year.")
    print("\n" + "="*80)
    print()
else:
    # Step 3: Summarize removed transactions
    removed_summary = (
        trade_quarter.loc[~trade_quarter['unit_match']]
        .groupby(['comno', 'unit_filled', 'unit_base_filled'], dropna=False)
        .agg(
            total_value=('value', 'sum'),
            transactions=('value', 'count')
        )
        .reset_index()
        .sort_values('total_value', ascending=False)
    )

    # Step 4: Remove mismatched transactions from dataset
    trade_quarter = trade_quarter[trade_quarter['unit_match']]

    # Step 5: Print report
    print("\n" + "="*80)
    print()
    print('Check if unit of measurement is different from baseyear')
    print("Commodities where transactions were removed due to unit mismatch with base year:\n")
    for _, row in removed_summary.iterrows():
        unit_current = row['unit_filled']
        unit_base = row['unit_base_filled']
        print(f" - Comno {row['comno']}: {row['transactions']} transactions removed")
        print(f"   Unit in quarter: {unit_current}  |  Unit in base year: {unit_base}")
        print(f"   Total value removed: {row['total_value']:.2f}\n")

    print("\033[1mTake action if possible to reconcile different units of measurement.\033[0m")
    print("\n" + "="*80)
    print()

# -

# ### Count transactions per group for HS in current quarter and base

# +
# Step 1: Count the number of transactions within each comno
transaction_count_per_comno = trade_quarter.groupby('comno')['n_transactions'].count().reset_index()
transaction_count_per_comno.columns = ['comno', 'transaction_count']

# Step 2: Create categories for the transaction counts
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
transaction_count_per_comno['category'] = transaction_count_per_comno['transaction_count'].apply(categorize_transactions)

# Step 3: Create a frequency table for each category
frequency_table = transaction_count_per_comno.groupby('category').size().reset_index(name='frequency')

# Display the frequency table
print(f"{flow.capitalize()}. {year}-Q{quarter} - Distribution of HS codes in sample by number of transactions")
print("Number of commodities - Categorized by number of transaction")

display(frequency_table)
# -

# ## Delete outliers based on low number of transactions in month and low value

# +

print(f'{flow.capitalize()}, {year}-Q{quarter}. Remove outliers in sample')



# Crosstab of frequencies
crosstab3 = pd.crosstab(index=trade_quarter['outlier_n_test'], columns='Count', margins=True)

# Calculate relative percentages
crosstab3['Percentage (%)'] = ((crosstab3['Count'] / crosstab3.loc['All', 'Count']) * 100).map('{:.1f}'.format)

# Keep only 'Count' and 'Percentage (%)' columns
crosstab3 = crosstab3[['Count', 'Percentage (%)']]

# Print formatted output


print("The table below shows how many transactions were tagged as outliers based on number of transactions in month and value.")
print(f"According to conditions where number of transactions in month is below: {n_t_month} and transasction value below: {value_limit}, and n transactions in quarter below: {n_t_quarter}")
display(crosstab3)

print("\n" + "="*80)

# -

trade_quarter = trade_quarter.loc[ 
    (trade_quarter['outlier_n_test'] == False)     
].copy()

# +
if selected_outlier not in trade_quarter.columns:
    raise ValueError(f"Column '{selected_outlier}' not found in trade_quarter")

# Crosstab of frequencies
crosstab2 = pd.crosstab(index=trade_quarter[selected_outlier], columns=['Count'], margins=True)

# Calculate relative percentages
crosstab2['Percentage (%)'] = ((crosstab2['Count'] / crosstab2.loc['All', 'Count']) * 100).map('{:.1f}'.format)

# Keep only 'Count' and 'Percentage (%)' columns
crosstab2 = crosstab2[['Count', 'Percentage (%)']]

# Print formatted output
print(f'{flow.capitalize()} {year}, Q{quarter}. Removed transactions tagged as outlier with a {selected_outlier} above the limit')
display(crosstab2)
# -


# ### Remove outliers

# +
# Filter the DataFrame to keep only transactions where all specified conditions are False
tradedata_no_outlier = trade_quarter.loc[ 
    (trade_quarter[selected_outlier] == False) 
    
].copy()

# +
#put in aggvars below to calculate isic
# isic_section', 'isic_division', 'isic_group', 'isic_class',
# -

aggvars = ['year', 'flow', 'comno', 'quarter', 'month', 'section', 'chapter', 
           'sitc1', 'sitc2', 'hs6']
tradedata_month_quarter = tradedata_no_outlier.groupby(aggvars, dropna=False, as_index=False).agg(
    weight=('weight', 'sum'),
    value=('value', 'sum'),
    n_transactions = ('n_transactions', 'mean'),
    base_price = ('base_price', 'first')
)


tradedata_month_quarter

# ## Calculate the price per month per HS and other measures

# +
tradedata_month_quarter['price'] = tradedata_month_quarter['value'] / tradedata_month_quarter['weight']

tradedata_month_quarter['price_chg'] = tradedata_month_quarter['price'] / tradedata_month_quarter['base_price']

tradedata_month_quarter['price_median'] = tradedata_month_quarter.groupby(['flow', 'comno'])['price'].transform('median')
tradedata_month_quarter['price_sd'] = tradedata_month_quarter.groupby(['flow', 'comno'])['price'].transform('std')
tradedata_month_quarter['price_mean'] = tradedata_month_quarter.groupby(['flow', 'comno'])['price'].transform('mean')
# extra step: Calculate the standard deviation to mean ratio for each transaction
tradedata_month_quarter['price_mean_ratio'] = tradedata_month_quarter['price']/tradedata_month_quarter['price_mean']
tradedata_month_quarter['price_median_ratio'] = tradedata_month_quarter['price']/tradedata_month_quarter['price_median']
tradedata_month_quarter['price_sd_ratio'] = tradedata_month_quarter['price']/tradedata_month_quarter['price_sd']
tradedata_month_quarter['price_cv'] = tradedata_month_quarter['price_sd']/tradedata_month_quarter['price_mean']
# -

# ## Extreme price difference from baseprice (4 quarter of previous year) price per HS per month - Tag outliers

# +
tradedata_month_quarter['outlier_time_q'] = np.select([(tradedata_month_quarter['price'] / tradedata_month_quarter['base_price'] < price_limit_low),
                                     (tradedata_month_quarter['price'] / tradedata_month_quarter['base_price'] > price_limit_high),
                                     ],
                                     ['1', '2'],
                                   default='0')

print("\n" + "="*80)
print(f'Price control on monthly prices in current quarter for Flow: {flow.capitalize()}')
print(f'Monthly price change from baseprice in {year} per HS')
print("     0 = normal (within acceptable range of median)")
print(f"     1 = price < {price_limit_low} of baseprice (too low)")
print(f"     2 = price > {price_limit_high} of baseprice (too high)")
display(pd.crosstab(tradedata_month_quarter['outlier_time_q'], columns='Frequency', margins=True))
# -


# List outliers

print("\n" + "="*80)
print()
print(f'Monthly prices tagged as outlier per commoditiy for current period {year}Q{quarter}:')
print(f'{flow.capitalize()}, {year}. Outliers')
display(tradedata_month_quarter.loc[tradedata_month_quarter['outlier_time_q'].isin(['1','2'])])
print("\n" + "="*80)

# Convert the 'outlier_time_q' column to boolean
tradedata_month_quarter['outlier_time_q'] = tradedata_month_quarter['outlier_time_q'].isin(['1', '2'])


# ## Delete outliers

# Filter the DataFrame to keep only transactions where all specified conditions are False
tradedata_no_outlier_time = tradedata_month_quarter.loc[
    (tradedata_month_quarter['outlier_time_q'] == False)
].copy()

tradedata_no_outlier1 = tradedata_no_outlier_time.copy()

count_true_outliers = tradedata_month_quarter.groupby('comno')[['outlier_time_q']].sum()
count_true_outliers_sorted = count_true_outliers.sort_values('outlier_time_q', ascending=False)
print(f'Commoditiy for current period {year}Q{quarter} and number of months with outliers:')
display(count_true_outliers_sorted)
print("\n" + "="*80)

#  ## Store the data as parquet file

#tradedata_no_outlier1.drop(columns='price_chg', inplace=True)
print()
print("Final output")
print(f"Prices for current period {year}Q{quarter} for sample")
print()
tradedata_no_outlier1.to_parquet(f'../data/tradedata_no_outlier_{flow}_{year}_q{quarter}.parquet')
print(f'\nNOTE: Parquet file ../data/tradedata_no_outlier_{flow}_{year}q{quarter}.parquet written with {tradedata_no_outlier.shape[0]} rows and {tradedata_no_outlier.shape[1]} columns\n')
show(tradedata_no_outlier1, maxBytes=0)
print("\n" + "="*80)

# ### Visualization of transactions per hs and outlier control (sd)

# +
import matplotlib.pyplot as plt
import seaborn as sns
import ipywidgets as widgets
from IPython.display import display

# Function to filter data for a specific comno and plot it on given axes
def plot_transactions_for_comno(ax, dataset, comno_value, x_var, y_var, hue1):
    # Filter data for the given comno
    filtered_data = dataset[dataset['comno'] == comno_value]

    # Plot transactions, color-coding based on the hue1 variable
    sns.scatterplot(data=filtered_data, x=x_var, y=y_var, 
                    hue=hue1, ax=ax, palette={True: 'red', False: 'blue'}, legend='full')

    # Add plot labels and title
    ax.set_title(f'Transactions for comno {comno_value} - Detection method: {hue1}')
    ax.set_xlabel(x_var)
    ax.set_ylabel(y_var)

# Function to update plots based on selected comno, dataset, and axes
def update_plot(comno_value, dataset_name, x_var, y_var):
    # Select the appropriate dataset
    if dataset_name == 'trade_quarter':
        dataset = trade_quarter
    else:
        dataset = tradedata_no_outlier

    # Clear the current figure
    plt.clf()

    # Create a grid of subplots
    num_hues = len(hue1_variables)
    fig, axs = plt.subplots(nrows=(num_hues + 1) // 2, ncols=2, figsize=(14, 6 * ((num_hues + 1) // 2)))
    axs = axs.flatten()  # Flatten the 2D array of axes for easier indexing

    # Loop through each hue1 variable and create a plot in the corresponding subplot
    for i, hue1 in enumerate(hue1_variables):
        plot_transactions_for_comno(axs[i], dataset, comno_value, x_var, y_var, hue1)

    # If there are any empty subplots, remove them
    for j in range(i + 1, len(axs)):
        fig.delaxes(axs[j])

    # Adjust layout
    plt.tight_layout()
    plt.show()

# Specify the comno values you want to visualize and sort them
comno_values = sorted(trade_quarter['comno'].unique().tolist())  # Sort unique comno values

# Define the hue1 variables you want to visualize
hue1_variables = [selected_outlier]  # Example hue1 variables

# Define the list of variables for the x- and y-axes
axis_variables = ['price', 'base_price', 'n_transactions', 'month', 'value', 'weight', 'country', 'price_chg']

# Create a dropdown menu for comno selection
comno_dropdown = widgets.Combobox(
    options=comno_values,
    value=str(comno_values[0]),
    description='Search comno:',
    layout=widgets.Layout(width='300px'),
    placeholder='Type or select a comno'
)

# Create a dropdown menu for dataset selection
dataset_dropdown = widgets.Dropdown(
    options=['trade_quarter', 'tradedata_no_outlier'],
    value='trade_quarter',  # Default dataset
    description='Select dataset:',
    layout=widgets.Layout(width='300px')
)

# Create dropdowns for selecting x- and y-axis variables
x_dropdown = widgets.Dropdown(
    options=axis_variables,
    value='value',  # Default x-axis
    description='Select X:',
    layout=widgets.Layout(width='300px')
)

y_dropdown = widgets.Dropdown(
    options=axis_variables,
    value='price_chg',  # Default y-axis
    description='Select Y:',
    layout=widgets.Layout(width='300px')
)

# Create an interactive output for the plot
output = widgets.interactive_output(update_plot, {
    'comno_value': comno_dropdown, 
    'dataset_name': dataset_dropdown,
    'x_var': x_dropdown,
    'y_var': y_dropdown
})

# Display the dropdowns and output
display(dataset_dropdown, comno_dropdown, x_dropdown, y_dropdown, output)
# -


# ### Visualization of transactions per hs and monthly prices and outlier control time

# +
import matplotlib.pyplot as plt
import seaborn as sns
import ipywidgets as widgets
from IPython.display import display

# Ensure month is sorted numerically
def preprocess_dataset(dataset):
    return dataset.sort_values(by='month')  # Sort by month (numeric)

# Function to filter data for a specific comno and plot it on given axes
def plot_transactions_for_comno(ax, dataset, comno_value, x_var, y_var, hue):
    # Filter data for the given comno
    filtered_data = dataset[dataset['comno'] == comno_value]

    # Plot transactions, color-coding based on the hue variable
    sns.scatterplot(data=filtered_data, x=x_var, y=y_var, 
                    hue=hue, ax=ax, palette={True: 'red', False: 'blue'}, legend='full')

    # Add plot labels and title
    ax.set_title(f'Transactions for comno {comno_value} - Detection method: {hue}')
    ax.set_xlabel(x_var)
    ax.set_ylabel(y_var)

# Function to update plots for both datasets based on selected comno, dataset, and axes
def update_plot(comno_value, x_var, y_var):
    # Clear the current figure
    plt.clf()

    # Create a grid of subplots (2 rows, 1 column to compare two datasets)
    fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(16, 6))

    # Preprocess both datasets (keeping original variables unchanged)
    preprocessed_trade_quarter = preprocess_dataset(trade_quarter)
    preprocessed_tradedata_month_quarter = preprocess_dataset(tradedata_month_quarter)
    
    # Plot for `trade_quarter` dataset
    plot_transactions_for_comno(axs[0], preprocessed_trade_quarter, comno_value, x_var, y_var, selected_outlier)
    axs[0].set_title(f'Transactiondata - prices for comno {comno_value}')
    
    # Plot for `tradedata_month_quarter` dataset
    plot_transactions_for_comno(axs[1], preprocessed_tradedata_month_quarter, comno_value, x_var, y_var, 'outlier_time_q')
    axs[1].set_title(f'Monthly data - Unit values per month for comno {comno_value}')
    
    # Adjust layout
    plt.tight_layout()
    plt.show()

# Specify the comno values you want to visualize and sort them
comno_values = sorted(trade_quarter['comno'].unique().tolist())  # Sort unique comno values

# Define the list of variables for the x- and y-axes
axis_variables = ['price', 'base_price', 'n_transactions', 'month', 'value', 'weight', 'country', 'price_chg']

# Create a dropdown menu for comno selection with search functionality using Combobox
comno_dropdown = widgets.Combobox(
    options=comno_values,
    value=str(comno_values[0]),  # Default value
    description='Search comno:',
    layout=widgets.Layout(width='300px'),
    ensure_option=True,  # Only allow valid options from the list
    placeholder='Type or select a comno'
)

# Create dropdowns for selecting x- and y-axis variables
x_dropdown = widgets.Dropdown(
    options=axis_variables,
    value='value',  # Default x-axis
    description='Select X:',
    layout=widgets.Layout(width='300px')
)

y_dropdown = widgets.Dropdown(
    options=axis_variables,
    value='price_chg',  # Default y-axis
    description='Select Y:',
    layout=widgets.Layout(width='300px')
)

# Create an interactive output for the plot
output = widgets.interactive_output(update_plot, {
    'comno_value': comno_dropdown, 
    'x_var': x_dropdown,
    'y_var': y_dropdown
})

# Display the dropdowns and output
display(comno_dropdown, x_dropdown, y_dropdown, output)
# -



