# # Create weight base population

# ## Add parquet files for the whole year together

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
# import ipywidgets as widgets
# from IPython.display import display
#
#
# year = 2024
# quarter = 3
# flow = 'export'
# selected_outlier= 'outlier_sd'
#
# import itables
#
# # Initialize interactive display mode
# itables.init_notebook_mode(all_interactive=True)
# -

data_dir = Path('../data')
tradedata = pd.concat(
    pd.read_parquet(parquet_file)
    for parquet_file in data_dir.glob(f'{flow}_{year}_q*.parquet')
)
#tradedata.to_parquet(f'../data/{flow}_{year}.parquet')
print()
print(f"\n===Tradedata for {flow} {year}===")
print()
print(f'{tradedata.shape[0]} rows read from parquet files for {year}\n')

tradedata['price'] = tradedata['value'] / tradedata['weight']

# ### List rows where price is set to Infinity

if len(tradedata.loc[np.isinf(tradedata['price'])]) > 0:
    print(f'{flow.capitalize()} {year}. Rows where price could not be calculated.\n')
    display(tradedata.loc[np.isinf(tradedata['price'])])

# ## Population weights - Add sums for aggregated levels

tradedata['T_sum'] = tradedata.groupby(['flow'])['value'].transform('sum')
tradedata['HS_sum'] = tradedata.groupby(['flow', 'comno'])['value'].transform('sum')
tradedata['S_sum'] = tradedata.groupby(['flow', 'section'])['value'].transform('sum')
tradedata['C_sum'] = tradedata.groupby(['flow', 'chapter'])['value'].transform('sum')
tradedata['S1_sum'] = tradedata.groupby(['flow', 'sitc1'])['value'].transform('sum')
tradedata['S2_sum'] = tradedata.groupby(['flow', 'sitc2'])['value'].transform('sum')
#tradedata['isic_section_sum'] = tradedata.groupby(['flow', 'isic_section'])['value'].transform('sum')
#tradedata['isic_division_sum'] = tradedata.groupby(['flow', 'isic_division'])['value'].transform('sum')
#tradedata['isic_group_sum'] = tradedata.groupby(['flow', 'isic_group'])['value'].transform('sum')
#tradedata['isic_class_sum'] = tradedata.groupby(['flow', 'isic_class'])['value'].transform('sum')
tradedata['hs6_sum'] = tradedata.groupby(['flow', 'hs6'])['value'].transform('sum')


tradedata.groupby(['flow', 'section'])['value'].agg('sum')

pd.crosstab(tradedata['section'], columns='Freq', margins=True)

tradedata['comno'].loc[tradedata['section'].isna()].value_counts()

tradedata.to_parquet(f'../data/tradedata_{flow}_{year}.parquet')
print(f'\nNOTE: Parquet file ../data/tradedata_{flow}_{year}.parquet written with {tradedata.shape[0]} rows and {tradedata.shape[1]} columns\n')
print("\n" + "="*80)

# ## Delete outliers based on low number of transactions in month and low value

# +
outlier_n_test = pd.crosstab(index=tradedata['outlier_n_test'], columns='Count', margins=True)
# Calculate relative percentages
outlier_n_test['Percentage (%)'] = ((outlier_n_test['Count'] / outlier_n_test.loc['All', 'Count']) * 100).map('{:.1f}'.format)

print("The table below shows how many transactions were tagged as outliers based on low number of transactions and value.")

display(outlier_n_test)
# -

# Remove outliers
tradedata = tradedata.loc[
    (tradedata['outlier_n_test'] == 0)
].copy()

# #### Create datasets for analysis of removal of outliers 

# Filter the DataFrame to keep only transactions where all specified conditions are False
tradedata_no_MAD = tradedata.loc[
    (tradedata['outlier_MAD'] == False)
].copy()

# Filter the DataFrame to keep only transactions where all specified conditions are False
tradedata_no_sd = tradedata.loc[
    (tradedata['outlier_sd'] == False)
].copy()

# Filter the DataFrame to keep only transactions where all specified conditions are False
tradedata_no_sd2 = tradedata.loc[
    (tradedata['outlier_sd'] == False) &
    (tradedata['outlier_sd2'] == False)
].copy()

# Create dataframe with all outliers
tradedata_with_outlier = tradedata.copy()

# ## Delete outliers based on selected outlier test
# The limit is set before we run this syntax. We use axis=0 to avoid a lot of messages

# +
print("\n" + "="*80)
print(f"Descriptive Statistics for {flow.capitalize()} in {year}")
print(f"The table below shows how many transactions were tagged as outliers")
print(f"Grouped by outlier flag ('{selected_outlier}')")


# Compute group stats
summary_table = (
    tradedata.groupby(selected_outlier)
    .agg(
        value_count=('value', 'count'),
        value_mean=('value', 'mean'),
        value_sum=('value', 'sum'),
        value_std=('value', 'std')
    )
)

# Compute overall ("All") row
overall = pd.DataFrame({
    'value_count': [tradedata['value'].count()],
    'value_mean': [tradedata['value'].mean()],
    'value_sum': [tradedata['value'].sum()],
    'value_std': [tradedata['value'].std()]
}, index=['All'])

# Append the "All" row
summary_table = pd.concat([summary_table, overall])

display(summary_table)

print("\n" + "="*80)
print(f"Top 100 Outliers for {flow.capitalize()} in {year}")
print(f"Based on highest 'value' where '{selected_outlier} = True'")


# Filter for outliers, sort by 'value' in descending order, and display the top 100
top_outliers = (
    tradedata.loc[tradedata[selected_outlier] == 1]
    .sort_values(by='value', ascending=False)
    .head(100)
)

display(top_outliers)
print("\n" + "="*80)

# -



# Remove outliers
tradedata = tradedata.loc[
    (tradedata[selected_outlier] == 0)
].copy()

# #### Count transactions within each comno after removal of outliers

tradedata['n_transactions'] = tradedata.groupby(['flow', 'comno', 'quarter', 'month'])['value'].transform('count')

# ## Aggregate to months as there are often more transactions for the same commodity within the same month

# +
#put in aggvars to calculate isic
#'isic_section', 'isic_division', 'isic_group', 'isic_class',
#'isic_section_sum', 'isic_division_sum', 'isic_group_sum', 'isic_class_sum',
# -

aggvars = ['year', 'flow', 'comno', 'quarter', 'month', 'section', 'chapter', 'hs6',
           'sitc1', 'sitc2', 'T_sum', 'S_sum', 'C_sum', 'S1_sum', 'S2_sum', 'hs6_sum', 'HS_sum']
tradedata_month = tradedata.groupby(aggvars, dropna=False, as_index=False).agg(
    weight=('weight', 'sum'),
    value=('value', 'sum'),
    n_transactions_month = ('n_transactions', 'mean')
)
tradedata_month['price'] = tradedata_month['value'] / tradedata_month['weight']

# ## Add columns for to check for homogenity in the data
# These columns will be checked against the edge values that we choose

tradedata_month['no_of_months'] = tradedata_month.groupby(['flow', 'comno'])['month'].transform('count')
for stat in ['max', 'min', 'median', 'mean']:
    tradedata_month[f'price_{stat}'] = tradedata_month.groupby(['flow', 'comno'])['price'].transform(stat)
tradedata_month['price_sd'] = tradedata_month.groupby(['flow', 'comno'])['price'].transform('std')
tradedata_month['n_transactions_year'] = tradedata_month.groupby(['flow', 'comno'])['n_transactions_month'].transform('sum')
tradedata_month['price_cv'] = tradedata_month['price_sd'] / tradedata_month['price_mean']

# ## Save as parquet file

tradedata_month.to_parquet(f'../data/{flow}_{year}.parquet')
print()
print('Final output:')
print(f'\nNOTE: Parquet file ../data/{flow}_{year}.parquet written with {tradedata_month.shape[0]} rows and {tradedata_month.shape[1]} columns\n')
print("\n" + "="*80)

# +
import pandas as pd
import plotly.express as px
import ipywidgets as widgets
from IPython.display import display

def price_cv_ui(datasets, dataset_names, flow, year):
    """
    Interactive visualization of Price Coefficient of Variation (CV)
    with selectable X-axis (transactions or value) and nicer annotation for CV < 0.5.
    """

    # Aggregate to monthly data and count transactions per month
    def aggregate_to_monthly(df):
        df_month = df.groupby(['year', 'flow', 'comno', 'quarter', 'month'], as_index=False).agg(
            weight=('weight', 'sum'),
            value=('value', 'sum'),
            n_transactions_month=('comno', 'count')  # count rows per month
        )
        df_month['price'] = df_month['value'] / df_month['weight']
        return df_month

    # Calculate price CV
    def calculate_price_cv(df_month):
        df_month['price_mean'] = df_month.groupby(['flow', 'comno'])['price'].transform('mean')
        df_month['price_sd'] = df_month.groupby(['flow', 'comno'])['price'].transform('std')
        df_month['price_cv'] = (df_month['price_sd'] / df_month['price_mean']).fillna(0)
        return df_month

    # Final aggregation including summing transactions per year
    def aggregate_final(df_month):
        df_month['n_transactions_year'] = df_month.groupby(['flow', 'year', 'comno'])['n_transactions_month'].transform('sum')
        return df_month.groupby(['flow', 'year', 'comno'], as_index=False).agg(
            price=('price', 'mean'),
            value=('value', 'sum'),
            n_transactions_year=('n_transactions_year', 'first'),
            price_cv=('price_cv', 'first')
        )[['comno', 'price', 'value', 'n_transactions_year', 'price_cv']]

    # Consolidate all datasets
    consolidated = pd.DataFrame()
    for i, dataset in enumerate(datasets):
        df_month = aggregate_to_monthly(dataset)
        df_month = calculate_price_cv(df_month)
        final_df = aggregate_final(df_month)
        final_df['Dataset'] = dataset_names[i]
        consolidated = pd.concat([consolidated, final_df], ignore_index=True)

    # Plot function
    def plot_dynamic_xaxis(dataset_name, x_variable):
        data = consolidated[consolidated['Dataset'] == dataset_name]
    
        # Number of commodities with CV < 0.5
        below_cv_count = data.loc[data['price_cv'] < 0.5, 'comno'].nunique()
    
        # Share of value for those commodities
        total_value = data['value'].sum()
        below_cv_value = data.loc[data['price_cv'] < 0.5, 'value'].sum()
        below_cv_pct = below_cv_value / total_value * 100 if total_value > 0 else 0
    
        x_labels = {
            'n_transactions_year': 'Number of Transactions (Year)',
            'value': 'Total Value'
        }
    
        title = f"{flow.capitalize()} {year} - Price CV"
    
        fig = px.scatter(
            data,
            x=x_variable,
            y='price_cv',
            hover_data={'comno': True, 'price_cv': ':.3f', x_variable: ':.0f'},
            labels={
                x_variable: x_labels[x_variable],
                'price_cv': 'Price CV'
            },
            title=title
        )
        fig.update_traces(
            marker=dict(size=7, color='blue', opacity=0.7, line=dict(width=0.5, color='black'))
        )
        fig.update_layout(
            height=600,
            title_font_size=18,
            template='plotly_white',
            annotations=[
                dict(
                    x=1, y=1, xref='paper', yref='paper',
                    text=(
                        f"<b>CV < 0.5</b><br>"
                        f"Commodities: {below_cv_count}<br>"
                        f"Share of total value: {below_cv_pct:.1f}%"
                    ),
                    showarrow=False,
                    xanchor='right',
                    yanchor='top',
                    font=dict(size=14, color='darkblue'),
                    bgcolor='rgba(255,255,255,0.7)',
                    bordercolor='darkblue',
                    borderwidth=1,
                    borderpad=5
                )
            ]
        )
        fig.show()


    # UI widgets
    dataset_dropdown = widgets.Dropdown(
        options=dataset_names,
        value=dataset_names[0],
        description='Dataset:',
        layout=widgets.Layout(width='300px')
    )

    x_axis_dropdown = widgets.Dropdown(
        options=[
            ('Number of Transactions', 'n_transactions_year'),
            ('Total Value', 'value')
        ],
        value='n_transactions_year',
        description='X-axis:',
        layout=widgets.Layout(width='300px')
    )

    output = widgets.interactive_output(
        plot_dynamic_xaxis,
        {'dataset_name': dataset_dropdown, 'x_variable': x_axis_dropdown}
    )

    display(widgets.HBox([dataset_dropdown, x_axis_dropdown]), output)


# Example usage
datasets = [tradedata_with_outlier, tradedata_no_sd, tradedata_no_sd2]
dataset_names = ['With outliers', 'outlier_sd removed', 'outlier_sd2 removed']
price_cv_ui(datasets, dataset_names, flow, year)
print("\n" + "="*80)
print()
# -

# #### Histogram - Price Distribution for comno

# +
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.patches as mpatches
import ipywidgets as widgets
from IPython.display import display, clear_output

def price_distribution_ui(tradedata_no_sd, tradedata_with_outlier):
    # Ensure quarter is numeric for filtering
    tradedata_no_sd['quarter'] = pd.to_numeric(tradedata_no_sd['quarter'], errors='coerce')
    tradedata_with_outlier['quarter'] = pd.to_numeric(tradedata_with_outlier['quarter'], errors='coerce')

    # Get comno values that exist in both datasets
    comno_values = sorted(
        set(tradedata_no_sd['comno'].dropna().unique()) &
        set(tradedata_with_outlier['comno'].dropna().unique())
    )
    
    comno_combobox = widgets.Combobox(
        placeholder='Type or select HS code',
        options=comno_values,
        value=comno_values[0] if comno_values else None,
        description='HS code:',
        ensure_option=True,
        layout=widgets.Layout(width='300px')
    )
    
    dataset_dropdown = widgets.Dropdown(
        options=[('With outliers', 'tradedata_with_outlier'), ('Without outliers', 'tradedata_no_sd')],
        value='tradedata_with_outlier',
        description='Dataset:',
        layout=widgets.Layout(width='200px')
    )
    
    unique_quarters = sorted(tradedata_no_sd['quarter'].dropna().unique().tolist())
    quarter_checkboxes = [widgets.Checkbox(value=(i == 0), description=str(int(q)), indent=False) for i, q in enumerate(unique_quarters)]
    quarter_box = widgets.VBox(quarter_checkboxes)
    
    plot_output = widgets.Output()
    
    def get_selected_quarters():
        return [int(cb.description) for cb in quarter_checkboxes if cb.value]
    
    def plot_price_distribution(ax, dataset, comno_value, selected_quarters):
        filtered_data = dataset[
            (dataset['comno'] == comno_value) &
            (dataset['quarter'].isin(selected_quarters))
        ]
        if filtered_data.empty:
            ax.text(0.5, 0.5, 'No data for selected filters', ha='center', va='center', fontsize=14)
            ax.set_axis_off()
            return

        if 'outlier_sd' in filtered_data.columns:
            counts = filtered_data['outlier_sd'].value_counts()
            enable_kde = counts.min() >= 2 if len(counts) > 1 else False

            sns.histplot(
                data=filtered_data,
                x='price',
                hue='outlier_sd',
                kde=enable_kde,
                bins=30,
                alpha=0.7,
                ax=ax,
                multiple='stack',
                palette={False: 'tab:blue', True: 'tab:orange'}
            )

            handles = [
                mpatches.Patch(color='tab:blue', label='No Outlier'),
                mpatches.Patch(color='tab:orange', label='Outlier')
            ]
            ax.legend(title='Outlier Status', handles=handles)
        else:
            sns.histplot(
                data=filtered_data,
                x='price',
                kde=True,
                bins=30,
                alpha=0.7,
                ax=ax
            )

        ax.set_title(f'HS {comno_value} | Quarters: {", ".join(map(str, selected_quarters))}')
        ax.set_xlabel('Price')
        ax.set_ylabel('Frequency')
    
    def update_plot(_):
        with plot_output:
            clear_output(wait=True)
            comno = comno_combobox.value
            dataset_name = dataset_dropdown.value
            selected_quarters = get_selected_quarters()
            
            if not comno:
                print("Please select a valid HS code.")
                return
            if not selected_quarters:
                print("Please select at least one quarter.")
                return
            
            dataset = {
                'tradedata_with_outlier': tradedata_with_outlier,
                'tradedata_no_sd': tradedata_no_sd
            }[dataset_name]
            
            fig, ax = plt.subplots(figsize=(10, 6))
            plot_price_distribution(ax, dataset, comno, selected_quarters)
            plt.tight_layout()
            plt.show()
    
    update_button = widgets.Button(description="Update Plot", button_style='primary', icon='refresh')
    update_button.on_click(update_plot)
    
    display(
        widgets.HBox([comno_combobox, dataset_dropdown]),
        widgets.Label("Select Quarters:"),
        quarter_box,
        update_button,
        plot_output
    )



# -

# 1. Histogram Plot UI
price_distribution_ui(tradedata_no_sd, tradedata_with_outlier)
print("\n" + "="*80)
print()


# +
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.lines as mlines
import ipywidgets as widgets
from IPython.display import display, clear_output

def price_lineplot_ui(tradedata_month):
    """
    Interactive line plot of price over time per HS code (comno) with optional
    right-hand axis for value, weight, or both, plus stats annotation.
    """
    # Ensure numeric for calculations
    for col in ['year', 'month', 'price', 'value', 'weight']:
        tradedata_month[col] = pd.to_numeric(tradedata_month[col], errors='coerce')

    # Compute date column
    tradedata_month['date'] = pd.to_datetime(
        tradedata_month[['year', 'month']].assign(day=1),
        errors='coerce'
    )
    tradedata_month = tradedata_month.dropna(subset=['date'])

    comno_values = sorted(tradedata_month['comno'].dropna().unique())
    
    comno_combobox = widgets.Combobox(
        placeholder='Type or select HS code',
        options=comno_values,
        value=comno_values[0] if comno_values else None,
        description='HS code:',
        ensure_option=False,
        layout=widgets.Layout(width='300px')
    )

    right_axis_dropdown = widgets.Dropdown(
        options=[('None', 'none'), ('Value', 'value'), ('Weight', 'weight'), ('Both', 'both')],
        value='none',
        description='Show:',
        layout=widgets.Layout(width='200px')
    )

    plot_output = widgets.Output()

    def plot_line(ax_left, dataset, comno, right_selection):
        filtered = dataset[dataset['comno'] == comno]
        if filtered.empty:
            ax_left.text(0.5, 0.5, 'No data for selected HS code', ha='center', va='center')
            ax_left.set_axis_off()
            return

        filtered = filtered.sort_values('date')

        # Left axis: Price
        sns.lineplot(data=filtered, x='date', y='price', color='tab:blue', marker='o', ax=ax_left, label='Price')
        ax_left.set_ylabel('Price', color='tab:blue')
        ax_left.tick_params(axis='y', labelcolor='tab:blue')
        ax_left.set_xlabel('Date')
        ax_left.set_title(f'HS {comno} - Price vs. Value & Weight')
        ax_left.grid(True)

        legend_handles = [mlines.Line2D([], [], color='tab:blue', marker='o', label='Price')]

        # Right axis: Value / Weight
        if right_selection != 'none':
            ax_right = ax_left.twinx()
            if right_selection in ['value', 'both']:
                sns.lineplot(data=filtered, x='date', y='value', color='gray', linestyle='--', marker='s', ax=ax_right)
                legend_handles.append(mlines.Line2D([], [], color='gray', linestyle='--', marker='s', label='Value'))
            if right_selection in ['weight', 'both']:
                sns.lineplot(data=filtered, x='date', y='weight', color='darkgray', linestyle=':', marker='^', ax=ax_right)
                legend_handles.append(mlines.Line2D([], [], color='darkgray', linestyle=':', marker='^', label='Weight'))
            ax_right.set_ylabel('Value / Weight', color='gray')
            ax_right.tick_params(axis='y', labelcolor='gray')

        # Stats annotation (last row)
        latest = filtered.iloc[-1]
        stats_text = (
            f"Months: {latest.get('month', '')}\n"
            f"Max: {latest.get('price_max', latest['price']):,.2f}\n"
            f"Min: {latest.get('price_min', latest['price']):,.2f}\n"
            f"Median: {latest.get('price_median', latest['price']):,.2f}\n"
            f"Mean: {latest.get('price_mean', latest['price']):,.2f}\n"
            f"SD: {latest.get('price_sd', 0):,.2f}\n"
            f"Transactions: {latest.get('n_transactions_year', 0)}\n"
            f"CV: {latest.get('price_cv', 0):.2f}"
        )
        ax_left.text(
            0.98, 0.95, stats_text,
            transform=ax_left.transAxes,
            fontsize=9,
            verticalalignment='top',
            horizontalalignment='right',
            bbox=dict(facecolor='white', edgecolor='gray', boxstyle='round,pad=0.3')
        )
        ax_left.legend(handles=legend_handles, loc='upper left')

    def update_plot(_):
        with plot_output:
            clear_output(wait=True)
            comno = comno_combobox.value
            right_selection = right_axis_dropdown.value

            if not comno:
                print("Please select or enter a valid HS code.")
                return

            fig, ax = plt.subplots(figsize=(10, 6))
            plot_line(ax, tradedata_month, comno, right_selection)
            plt.tight_layout()
            plt.show()

    update_button = widgets.Button(description="Update Plot", button_style='primary', icon='refresh')
    update_button.on_click(update_plot)

    display(
        widgets.HBox([comno_combobox, right_axis_dropdown]),
        update_button,
        plot_output
    )



# -

# 2. Lineplot UI
price_lineplot_ui(tradedata_month)
print("\n" + "="*80)
print()


# #### Piechart for trade flow

# +
print('')
print('')
print(f'Piechart of weightbase for {flow} in {year}')
print('')
print('')


# Load SITC1 label data
sitc1_label = pd.read_csv("../cat/labels.csv")
sitc1_label = sitc1_label[sitc1_label["category"] == 'sitc1'][["code", "label"]]  # Keep relevant columns

# Remove duplicates for each SITC1
df_pie = tradedata_month.drop_duplicates(subset="sitc1").sort_values("sitc1").dropna(subset=["sitc1"])

# Ensure `sitc1` and `code` are the same type
df_pie["sitc1"] = df_pie["sitc1"].astype(str)
sitc1_label["code"] = sitc1_label["code"].astype(str)

# Merge with labels
df_pie = df_pie.merge(sitc1_label, left_on="sitc1", right_on="code", how="left")

# Create a combined label with both code and name
df_pie["label"] = df_pie["label"]

# Define colors
colors = plt.cm.Paired.colors  

# Create figure
fig, ax = plt.subplots(figsize=(8, 8))

# Generate pie chart
wedges, texts, autotexts = ax.pie(
    df_pie["S1_sum"], 
    labels=None,  # Remove default labels to avoid stacking
    autopct="%1.1f%%", 
    startangle=140, 
    colors=colors, 
    pctdistance=0.85  
)

# Adjust percentage label styling
for autotext in autotexts:
    autotext.set_color("black")
    autotext.set_fontweight("bold")

# Add labels outside the pie with fixed offsets
for wedge, label in zip(wedges, df_pie["label"]):
    angle = (wedge.theta2 + wedge.theta1) / 2  # Get middle angle of each slice
    x = 1.2 * wedge.r * np.cos(np.radians(angle))  # Fixed position offset
    y = 1.2 * wedge.r * np.sin(np.radians(angle))  # Fixed position offset
    ax.annotate(
        label, 
        xy=(wedge.r * np.cos(np.radians(angle)), wedge.r * np.sin(np.radians(angle))),
        xytext=(x, y),  # Label position outside pie
        ha="center", fontsize=10, 
        bbox=dict(boxstyle="round,pad=0.3", edgecolor="gray", facecolor="white"),
        arrowprops=dict(arrowstyle="-", connectionstyle="arc3,rad=0.2")
    )

# Title
plt.title(f"Pie chart of weightbase for SITC1 for {flow} in {year}", fontsize=14)

plt.show()
print("\n" + "="*80)
print()
# -



