# # Import and Export Price Index – XMPI
#
# **Yearly (Before running of 1st quarter routines): Selection of sample (HS8), Calculation of Weights, and Base Prices**
#
# This program executes all routines that need to run on a yearly basis.  
# Most other programs are included and executed from here.
#
# ---
#
# **Key Steps**
#
# - **Import data for base year**
# - **Unit values (Transaction data) - Outlier control per commodity**  
# - **Unit values (month) - Control of price changes from the base period**  
# - **Unit values (quarter) - Imputation of missing prices**
# - **Add donors**
# - **Define parameters for sample selection and select sample**  
#   - Determines acceptable price variation for each commodity  
#   - Stricter parameters → less heterogeneity  
# - **Check coverage**  
#   - How much of the population is covered by the sample  
# - **Calculate base prices**
#
# ---
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

# **Data transformation from transaction data up until base price calculation:**
#
# $$
# \begin{array}{c}
# \boxed{\textbf{Transaction Unit Values}} \\[0.6em]
# UnitValue_i^{\text{transaction}} = 
# \frac{Value_i^{\text{transaction}}}{Weight_i^{\text{transaction}}} \\[1.2em]
# \downarrow \\[0.6em]
# \boxed{\textbf{Outlier Control (2σ from quarterly mean)}} \\[0.6em]
# \text{Outlier Detection: } 
# z_i = \frac{p_i - \bar{p}}{\sigma_p}, \quad
# \text{outlier if } |z_i| > 2 \\[1.2em]
# \downarrow \\[0.6em]
# \boxed{\textbf{Monthly Unit Values}} \\[0.6em]
# UnitValue_i^{\text{month}} = 
# \frac{\sum\limits_{t \in \text{month}} Value_{i,t}^{\text{transaction}}}
# {\sum\limits_{t \in \text{month}} Weight_{i,t}^{\text{transaction}}} \\[1.2em]
# \downarrow \\[0.6em]
# \boxed{\textbf{Sample Selection (check against parameters: value > parameter)}} \\[0.6em]
# \text{Accepted if:} \\[0.3em]
# \text{Months with transactions} \ge \text{no\_of\_months} 
# \;\; \text{or} \;\;
# (\text{Months with transactions} \ge \text{no\_of\_months\_seasons} 
# \;\text{and}\; \text{section} = \text{section\_seasons}) \\[0.3em]
# \text{Actual transactions in year} \ge \text{n\_transactions\_year} \\[0.3em]
# \text{Actual } price\_cv < \text{price\_cv} \\[0.3em]
# \text{Monthly prices in year: } 
# \frac{\max}{\min} < \text{max\_by\_min} \\[0.3em]
# \text{Monthly prices in year: } 
# \frac{\max}{\text{median}} < \text{max\_by\_median} \\[0.3em]
# \text{Monthly prices in year: } 
# \frac{\text{median}}{\min} < \text{median\_by\_min} \\[0.3em]
# \text{Actual share of total value} > \text{share\_small} \\[1.2em]
# \downarrow \\[0.6em]
# \boxed{\textbf{Quarterly Unit Values}} \\[0.6em]
# UnitValue_i^{\text{quarter}} = 
# \frac{\sum\limits_{t \in \text{quarter}} Value_{i,t}^{\text{transaction}}}
# {\sum\limits_{t \in \text{quarter}} Weight_{i,t}^{\text{transaction}}} \\[1.2em]
# \downarrow \\[0.6em]
# \boxed{\textbf{Imputation of missing 4th quarter Unit Values}} \\[1.2em]
# \downarrow \\[0.6em]
# \boxed{\textbf{4th Quarter Base Prices}}
# \end{array}
# $$
#

# ## Import the necessary Python packages
#
# If some packages are missing, they can be installed with `pip install` in a terminal window.   

# +
# #!pip install pyarrow itables dash plotly ipywidgets jupytext itables pyarrow
# -

# ---
# ⚠️ For **ipywidgets** and JupyterLab widgets, installation might need to be done specifically for your user account:  
#
# If you get an error when vizualising the data try to install the following packages in the terminal:
#
# - `pip install ipywidgets --upgrade --user`  
# - `pip install jupyterlab_widgets --user`
#   
# **Afterwards close the browser and reopen the jupyterlab or notebook**
#
# Most packages can also be installed directly by activating the cell below.
#

# ## Documentation of data structure and catalouges
# remove # to read the documentation in the cell below

# +
#exec(open("01 Documentation.py").read())
# -

import pandas as pd
import numpy as np
import json
import os
from pathlib import Path
import itables
import matplotlib.pyplot as plt
from itables import init_notebook_mode, show
import seaborn as sns
import ipywidgets as widgets
from IPython.display import display
#pd.set_option('display.float_format',  '{:18,.0}'.format)
pd.set_option('display.float_format', lambda x: f'{x:15,.0f}' if abs(x)>1e5 else f'{x:15.2f}')
# Initialize interactive display mode
itables.init_notebook_mode(all_interactive=True)

# ## Select year and flow for sample selection and base price calculation
#
# Choose the **year** and **flow** to define the dataset for sample selection and the calculation of base prices.
#

year = 2023
flow = 'export'

# ## 005 Import_chapter_catalog - Import chapter and section correspondance
# This correspondance is used in the aggregation of the index

exec(open("005 Import_chapter_catalog.py").read())

# ## 007 Import_commodities_catalog - Import commodity sitc and ISIC correspondance
# This correspondance is used in the aggregation of the index

exec(open("007 Import_commodities_catalog.py").read())

# ## 008 Import_donors_catalog - Import donors that are used instead of trade data for some commoditites

exec(open("008 Import_donors_catalog.py").read())

# ## T010 Read trade quarter - Import tradedata for all 4 quarters
# Load all necessary data files corresponding to the base year.
#
# Add correspondance with different classification.

quarter = 1
exec(open("T010 Read trade quarter.py").read())
quarter = 2
exec(open("T010 Read trade quarter.py").read())
quarter = 3
exec(open("T010 Read trade quarter.py").read())
quarter = 4
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

# Accepted treshold for standard deviation from mean (default=2)
outlier_sd = 2

# Deviation from median (default=3)
outlier_dev_median = 3
# -

quarter = 1
exec(open("T015 Outlier control quarter.py").read())
quarter = 2
exec(open("T015 Outlier control quarter.py").read())
quarter = 3
exec(open("T015 Outlier control quarter.py").read())
quarter = 4
exec(open("T015 Outlier control quarter.py").read())

# ## A10M CreateWeightBasePopulation - Create population weights
#
# Generate the dataset used for weighting and simultaneously remove any outliers according to the defined thresholds.  

exec(open("A10M CreateWeightBasePopulation.py").read())

# ## Add Donors
#
# For certain commodities, price information from sources **other than foreign trade data** is available.  
# This information is stored in:
#
# `../cat/donors.csv`.
#
#
# **Note:** Be aware of change in the reference period for the donor source.  
# Any misalignment must be addressed **before** adding the data.
#
# **Option:**  
# - `"yes"` → Replace trade data with donor prices for selected commodities.  
# - `"no"` → Exclude donor data and keep the original trade prices.
#

use_donor = 'no'

# ## A20M CreateWeightBase - Select sample and create sample weights
#
# This step selects the commodities (the i's) that will be used for the index in the upcoming year.  
# It establishes the base population for the index, and here you define the parameters for commodity selection.
#
# After this step the sample weights have been created:
#
# $$
# \displaystyle {w_i^b}
# $$
#

share_total=0.05
no_of_months=5
no_of_months_seasons=3
section_seasons='II'
price_cv=0.5
max_by_min=10
max_by_median=5
median_by_min=5
share_small=0.0001
n_transactions_year = 20
exec(open("A20M CreateWeightBase.py").read())
basedata

# ## A30M Base_price - Calculate the base prices for the sample (4th quarter)
#
#
# Compute the 4th quarter base prices for each commodity in the selected sample:
# $$p_i^0$$
# Price of item \(i\) in the base period \(0\)
#
# Impute missing prices in the 4th quarter.
#
# These base prices serve as the reference point for price index calculations.
#

exec(open("A30M Base_price.py").read())
print("\n" + "="*80)
print()


# ## Updating HS Numbers (HS Revision)
#
# **Cases**
#
# - **1:1**  
#   Update Excel sheet
#
# - **1:Many**  
#   Identify if most of the trade is moved to a single commodity  
#   → If yes, update Excel sheet
#
# - **Many:1**  
#   if possible make expert judgement, and update Excel sheet
#
# - **Many:Many**  
#   if possible make expert judgement, and update Excel sheet
#

# ***UPDATE HS? (yes/no)*** 

update = 'no'

if update == "yes":
    exec(open("A40M HS Update.py").read())
    print("\n" + "-" * 40)
    print("\n\033[1mHS update script executed.\033[0m")
else:
    print("\033[1mHS update script skipped.\033[0m")
