# # Import and Export Price Index – XMPI
#
# **Quarterly production**  
#
# This section covers the processing of quarterly production data for the XMPI, including import and export price calculations.
#
# **Key steps**
#
# - **Import quarterly data**  
# - **Unit values (Transaction data) - Outlier control per commodity**  
# - **Unit values (month) - Control of price changes from the base period**  
# - **Unit values (quarter) - Imputation of missing prices**  
# - **Index calculation and aggregation**
#

# ### The formula
#
#
# $$
# \displaystyle I_g^t = \sum_{i \in g} \frac{p_i^t}{p_i^0} \cdot \frac{w_i^b}{\sum_{i \in g} w_i^b}
# $$
#
# represents a **weighted price index** for a group of items \(g\) at time \(t\). It is widely used in economics and statistics to measure **price changes over time** while accounting for the relative importance of each item.
#
# - **Laspeyres Index:** This formula is essentially a Laspeyres-type index, sometimes referred to as the **Young index**  
# - **Trade Statistics:** Often applied in **import/export price indices** to track changes in prices of goods over time  
#
# ---
#
# ### Components
#
# - $p_i^t$ : Price of item \(i\) at time \(t\)  
# - $p_i^0$ : Price of item \(i\) in the base period \(0\)  
# - $w_i^b$ : Weight of item \(i\) based on its share in total expenditure in the base period  
# - $sum_{i \in g} w_i^b$ : Total weight of all items in group \(g\), used to normalize contributions  
#
# ---
#
# ### Interpretation:
# - The ratio ${p_i^t}/{p_i^0}$ is the **price relative** of item \(i\)  
# - Each price relative is **weighted** by its importance in the base period, ensuring that more significant items contribute proportionally more to the group index  
# - The sum gives the **group-level index**, which can be interpreted as the **average price change for the group**, adjusted for weights  
#
# ---
#

# **Data transformation from transaction data up until index calculation**
#
# $$
# \begin{array}{c}
# \boxed{\text{Transaction Unit Values}} \\[0.5em]
# UnitValue_i^{transaction} = \frac{Value_i^{transaction}}{Weight_i^{transaction}} \\[1em]
# \downarrow \\[0.5em]
# \boxed{\text{Outlier Control (2σ from quarterly mean)}} \\[0.5em]
# \text{Outlier Detection: } z_i = \frac{p_i - \bar{p}}{\sigma_p}, \quad
# \text{outlier if } |z_i| > 2 \\[1em]
# \downarrow \\[0.5em]
# \boxed{\text{Monthly Unit Values}} \\[0.5em]
# UnitValue_i^{month} = \frac{\sum\limits_{t \in month} Value_{i,t}^{transaction}}{\sum\limits_{t \in month} Weight_{i,t}^{transaction}} \\[1em]
# \downarrow \\[0.5em]
# \boxed{\text{Price Control (deviation from base)}} \\[0.5em]
# \text{Accepted if } \text{price\_limit\_low} \le \frac{p_i^\text{month}}{p_i^\text{base}} \le \text{price\_limit\_high} \\[1em]
# \downarrow \\[0.5em]
# \boxed{\text{Quarterly Unit Values}} \\[0.5em]
# UnitValue_i^{quarter} = \frac{\sum\limits_{t \in quarter} Value_{i,t}^{transaction}}{\sum\limits_{t \in quarter} Weight_{i,t}^{transaction}} \\[1em]
# \downarrow \\[0.5em]
# \boxed{\text{Imputation of Missing Values}} \\[1em]
# \downarrow \\[0.5em]
# \boxed{\text{Quarterly Index Calculation}}
# \end{array}
# $$
#

# ## Import the necessary Python packages
#
# If any packages are not installed, you can install them using `pip install` from a terminal window.  
# For example:

# +
# #!pip install pyarrow itables dash plotly ipywidgets jupytext itables pyarrow
# -

# ⚠️ For **ipywidgets** and JupyterLab widgets, installation might need to be done specifically for your user account:  
#
# If you get an error when vizualising the data try to install the following packages in the terminal:
#
# - `pip install ipywidgets --upgrade --user`  
# - `pip install jupyterlab_widgets --user`
#   
# **Afterwards restart kernel, close the browser and reopen the jupyterlab or notebook**
#
# Most packages can also be installed directly by activating the cell below.
#

import pandas as pd
import numpy as np
import json
import os
from pathlib import Path
from itables import init_notebook_mode, show
import matplotlib.pyplot as plt
import seaborn as sns
import itables
#pd.set_option('display.float_format',  '{:18,.0}'.format)
pd.set_option('display.float_format', lambda x: f'{x:15,.0f}' if abs(x)>1e5 else f'{x:15.2f}')
# Initialize interactive display mode
itables.init_notebook_mode(all_interactive=True)

# ## Select year, quarter and flow
# The parameters can be adjusted for each period as needed.

year = 2024
quarter  = 3
flow = 'export'

# ## T010 Read trade quarter - Import tradedata for a quarter
# This section processes the trade data for a given quarter.  

exec(open("T010 Read trade quarter.py").read())

# ## T015 Outlier control quarter - Outlier control
# **Control is done on transaction-level data per commoditiy per quarter**  

# **Outlier detection methods**
#
# **1. Standard deviations from the mean**  
# This method measures how far each data point is from the dataset’s mean (average).  
# It relies on the standard deviation, which captures the spread or variability of values around the mean.  
#
# **2. Median Absolute Deviation (MAD)**  
# This method measures the distance between each data point and the dataset’s median.  
# Because it is based on the median, MAD is more robust against outliers and skewed data than methods using the mean.  
#
# **Choose which outliers to remove**
#
# You can select different methods for detecting and removing outliers:
#
# - **outlier_sd**: 1 iteration tagging outlier with set limit for standard deviation from the mean (recommended)  
# - **outlier_sd2**: 2 iteration tagging outlier with set limit for standard deviations from the mean  
# - **outlier_MAD**: 1 iteration tagging outlier with set limit for absolute deviation from the median  
#
# ➡️ **Recommended:** `outlier_sd`
#
# **Set threshold for acceptable price dispersion at the transaction level for each HS code**
#
# Define the maximum allowed variation in prices for individual transactions within each HS code.  
# This ensures that extreme price differences do not distort the analysis and selection.

# +
selected_outlier = 'outlier_sd'

# Deviation from mean
outlier_sd = 2

#Deviation from median
outlier_dev_median = 5
# -

exec(open("T015 Outlier control quarter.py").read())

# ## T40M Price_control - Price control
# **Control is done on aggregatet monthly prices for each commodity in the sample (i)**  
# Check the trade data for extreme monthly prices by comparing the current period with the baseprice.
#
# Accepted:  
# $$
# \text{price\_limit\_low} \le \frac{p_i^\text{month}}{p_i^\text{base}} \le \text{price\_limit\_high}
# $$

#Treshold price change
price_limit_low = 0.4
price_limit_high = 1.7

exec(open("T40M Price_control.py").read())

# ## T50M Impute_prices - Impute prices and add donors
# **Imputation is done on aggregatet quarterly prices for each commodity in the sample (i)**  
# Estimate missing or invalid prices for the current quarter using available data and defined imputation rules.
#
# **Donor**
#
# For certain commodities, price information from sources **other than foreign trade data** is available.  
# This information is stored in:
#
# `../cat/donors.csv`.
#
# **Note:** Be aware of change in the reference period for the donor source.  
# Any misalignment must be addressed **before** adding the data.

exec(open("T50M Impute_prices.py").read())

# ## T60M Index_unchained - Calculate unchained index
#
# Compute the unchained price index for the current quarter using the selected sample and base prices.
#
# Create a short index for the current year at elementary level (HS8) and all aggregates.
#
# $$
# \displaystyle I_g^t = \sum_{i \in g} \frac{p_i^t}{p_i^0} \cdot \frac{w_i^b}{\sum_{i \in g} w_i^b}
# $$
#
# ---

exec(open("T60M Index_unchained.py").read())

# ## T71M / T72M - Calculate chained index
#
# Calculate a chained index by linking the current year's short index to the existing chained index (long index).  
# This step starts once all quarters of the first index year have been processed.  
# A specific syntax is used for chaining the first year, and a separate syntax is applied for subsequent years.
#

first_index_year = 2022 # This should not be changed unless we start the index again
if (year == first_index_year) & (quarter == 4):
    exec(open("T71M Chain_first_year.py").read())
elif year > first_index_year:
    exec(open("T72M Chain_next_years.py").read())
else:
    print("Not executed because we are executing one of the first 3 quarters of the first year. The chained index starts when all quarters of the first index year are executed.")

# ## Visualization of index
#
# Display and analyze the calculated index.
#

# + active=""
# exec(open("T80M_Graph.py").read())
# -

# ## Visualization of index for both import and export
#
# Examine the calculated index for both import and export data to compare trends and assess overall price movements.
#

exec(open("T85M Plotter.py").read())

# ## Compare XMPI to other sources
#
# Compare the XMPI results with other data sources to validate the index and identify any discrepancies or differences in trends.
#

exec(open("T90M Compare_other_sources.py").read())

# ## Publication

# ### Selected series for publication

for_publication = {
    '1': [  # Import
        {'levels': ['Sitc1'], 'series': ['0', '1','2','3','4','5','6','7','8','9']}, #Sitc1
        {'levels': ['Sitc2'], 'series': ['']},                                       #Sitc2
        {'levels': ['special_serie'], 'series': ['']}                                #Special series
    ],
    '2': [  # Export
        {'levels': ['Sitc1'], 'series': ['0', '1','2','3','4','5','6','7','8','9']}, #Sitc1
        {'levels': ['Sitc2'], 'series': ['']},                                       #Sitc2
        {'levels': ['special_serie'], 'series': ['']}                                #Special series
    ]
}

# ### Create publication material?

answer = input("Do you want to run T95M Publication.py? (yes/no): ").strip().lower()
if answer == "yes":
    exec(open("T95M Publication.py").read())
else:
    print("Publication material not updated.")
