# # Impute missing prices

# Calculate base year and previous quarter

# year= 2019
# quarter=1
# flow='export'

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
# import itables
# # Initialize interactive display mode
# itables.init_notebook_mode(all_interactive=True)
# init_notebook_mode(all_interactive=True)
#
# year = 2022
# quarter = 1
# flow = 'import'
# price_limit_low = 0.5
# price_limit_high = 1.5
#
# -

year_base = year - 1
quarter_1 = 4 if quarter == 1 else quarter - 1
#year_1 = year - 1

# ## Read parquet files

print()
print(f"\n===Tradedata for {flow} {year}-Q{quarter}, baseprices and weights for sample===")
print()

# +
if quarter == 1:
    basepricefile = f'../data/base_price{flow}_{year_base}.parquet'
else:
    basepricefile = f'../data/price_impute_{flow}_{year}q{quarter_1}.parquet'

baseprice = pd.read_parquet(basepricefile)
print(f'{baseprice.shape[0]} rows read from parquet file {basepricefile}\n')

if quarter == 1:
    baseprice.rename(columns={'base_price': 'price'}, inplace=True)
    baseprice.drop(columns='impute_base', inplace=True)

baseprice['qrt'] = 0    

weightbasefile = f'../data/weight_base_{flow}_{year_base}.parquet'
weight_base = pd.read_parquet(weightbasefile)
print(f'{weight_base.shape[0]} rows read from parquet file {weightbasefile}\n')

tradedatafile = f'../data/tradedata_no_outlier_{flow}_{year}_q{quarter}.parquet'
tradedata_no_outlier = pd.read_parquet(tradedatafile)
print(f'{tradedata_no_outlier.shape[0]} rows read from parquet file {tradedatafile}\n')
print("\n" + "="*80)
print()
# -

# ## Calculate the price per quarter per HS

# +
tradedata_no_outlier['qrt'] = 1
tradedata_qrt = tradedata_no_outlier.groupby(['year', 'flow', 'comno', 'qrt'], as_index=False).agg(
    value=('value', 'sum'),
    weight=('weight', 'sum')
)

tradedata_qrt['price'] = tradedata_qrt['value'] / tradedata_qrt['weight']
# -

tradedata_qrt

# ## Add files together

# +
tradedata_qrts = pd.concat([baseprice, tradedata_qrt])

print(f'Add current period prices with baseprices')
print("     0 = Prices for Commodities in baseprice data")
print(f"     1 = Prices for Commodities in current period")
print("If fewer prices in current period, they will be imputed")
display(pd.crosstab(tradedata_qrts['qrt'], columns='Frequency', margins=True))
print("\n" + "="*80)
print()
# -

# ## Restructure file

qrt_r = tradedata_qrts.pivot(index=['flow', 'comno', 'source_base'], columns='qrt', values= ['price'])
qrt_r.columns = [f'{x}_{y}' for x, y in qrt_r.columns]
qrt_r = qrt_r.reset_index()

qrt_r

# ## Add donor prices

# +
import pandas as pd

def merge_donor_prices(qrt_r: pd.DataFrame, donor: pd.DataFrame, year: int, quarter: int, debug: bool = True) -> pd.DataFrame:
    """
    Merge donor prices into qrt_r, replacing price_1 when:
      - donor price exists
      - donor source matches qrt_r['source_base']
    
    Parameters
    ----------
    qrt_r : pd.DataFrame
        Quarterly dataset with 'comno', 'source_base', 'price_1'.
    donor : pd.DataFrame
        Donor dataset in wide format (to be melted).
    year : int
        Year to filter donor prices on.
    quarter : int
        Quarter to filter donor prices on.
    debug : bool, default=True
        If True, prints which comnos had donor prices applied.
    
    Returns
    -------
    pd.DataFrame
        Updated qrt_r with donor prices merged into 'price_1'.
    """

    if not donor.empty:
        df_long = donor.melt(
            id_vars=["source", "comno", "flow"],
            var_name="Period",
            value_name="price"
        )

        df_long["year"] = df_long["Period"].str[:4]
        df_long["quarter"] = df_long["Period"].str[-1:].str.zfill(1)
        df_long["comno"] = df_long["comno"].astype(str)

        # Safe numeric conversion
        df_long["price"] = pd.to_numeric(
            df_long["price"].astype(str).str.replace(",", ".", regex=False),
            errors="coerce"
        )

        donor_pivot = df_long[["source", "comno", "year", "quarter", "price"]].copy()
    else:
        donor_pivot = pd.DataFrame({
            "source": pd.Series(dtype="object"),
            "comno": pd.Series(dtype="object"),
            "year": pd.Series(dtype="object"),
            "quarter": pd.Series(dtype="object"),
            "price": pd.Series(dtype="float64")
        })

    # Convert to numeric safely
    donor_pivot = donor_pivot.copy()
    donor_pivot["year"] = pd.to_numeric(donor_pivot["year"], errors="coerce")
    donor_pivot["quarter"] = pd.to_numeric(donor_pivot["quarter"], errors="coerce")

    # Filter for the given year/quarter
    donor_pivot_filtered = donor_pivot[
        (donor_pivot["year"] == year) &
        (donor_pivot["quarter"] == quarter)
    ].copy()

    # Ensure float64
    donor_pivot_filtered["price"] = donor_pivot_filtered["price"].astype("float64")

    # Merge donor prices into qrt_r
    merged = qrt_r.merge(
        donor_pivot_filtered[["comno", "price", "source"]],
        on="comno",
        how="left",
        suffixes=("", "_donor")
    )

    # Condition: donor price exists & matches source_base
    mask_replaced = merged["price"].notna() & (merged["source"] == merged["source_base"])

    # Replace price_1 where condition holds
    merged.loc[mask_replaced, "price_1"] = merged.loc[mask_replaced, "price"]

    if debug:
        print(f"Commodities with donor selected in base year.")
        print(f"The donor source is used for the whole year of {year}.")
        print(f'Price replaced for {year}Q{quarter}:')
        display(merged.loc[mask_replaced, ["comno","price_0", "price", "source"]])
        print("\n" + "="*80 + "\n")

    # Drop helper column and return updated df
    return merged.drop(columns=["price"])



# -

donor = pd.read_parquet('../cat/donors.parquet')
qrt_r = merge_donor_prices(qrt_r, donor, year=year, quarter=quarter, debug=True)


# +
#show(donor, maxBytes=0)
# -

# ## Merge with weight_base

# +
prices = pd.merge(weight_base, qrt_r, on=['flow', 'comno'], how='left')

prices.drop(columns=['year'], inplace=True)

# +
### Tag commodities that will be imputed

# +

# Step 1: initial flag — 1 if missing, 0 otherwise
prices['impute'] = prices['price_1'].isna().astype(int)

# Step 2: count valid price_1 per (flow, section)
section_counts = prices.groupby(['flow','section'])['price_1'].transform(lambda x: x.notna().sum())

# Step 3: set impute=2 if price_1 is missing but section has < 2 valid commodities
prices['impute'] = np.where(
    (prices['impute'] == 1) & (section_counts < 2),
    2,
    prices['impute']
)


# Calculate the relative price ratio 'price_rel' by dividing 'price_1' by 'price_0'
# This represents the change in price between the two time periods represented by price_1 and price_0
prices['price_rel'] = prices['price_1'] / prices['price_0']

# Calculate the 'product' column, which is a weighted value of the price ratio ('price_rel')
# This is done by multiplying 'price_rel' by 'Weight_HS' to reflect the influence of each product
prices['product'] = prices['price_rel'] * prices['Weight_HS']

# Calculate the sum of 'product' for each group of 'flow' and 'section' using 'transform'
# The result is stored in 'prod_sum' and repeated for each row within the group
prices['prod_sum_section'] = prices.groupby(['flow', 'section'])['product'].transform('sum')

# Set prod_sum = 0 for rows with impute == 2
prices.loc[prices['impute'] == 2, 'prod_sum_section'] = 0


# Calculate 'Weight_section' by setting it to 'Weight_HS' where 'product' is not NaN
# This effectively considers only rows with valid 'product' values when computing section weights
prices['Weight_section'] = prices['Weight_HS'] * (prices['product'].notna())

# Aggregate 'Weight_section' by summing it within each 'flow' and 'section' group using 'transform'
# The result gives a total weight per section and flow, repeated for each row in the group
prices['Weight_section'] = prices.groupby(['flow', 'section'])['Weight_section'].transform('sum')

# -

prices

# ## Impute missing values on section level

# +
#prices['impute'] = prices['price_1'].isna().astype(int)
prices['price_1'] =  np.where(prices['impute'] == 1,
                              prices['price_0'] * prices['prod_sum_section'] /  prices['Weight_section'],
                              prices['price_1']
                             )

prices['price_rel'] =  np.where(prices['impute'] == 1,
                                prices['price_1'] / prices['price_0'],
                                prices['price_rel']
                               )  

print(f'{flow.capitalize()}, {year}. Number of imputations in current period using price change from either section or total')
print("Imputation flag (`impute_base`) explanation:")
print("    0 = price in current period already exists, no imputation needed")
print("    1 = price in current period was missing, imputation applied on section level.")
print(f"    2 = price in current period was missing, imputation applied on total level - {flow}.")

# -

# ## Impute missing values on flow level

# +
prices['prod_sum_flow'] = prices.groupby(['flow'])['product'].transform('sum')

prices['Weight_flow'] = prices['Weight_HS'] * prices['product'].notna()
prices['Weight_flow'] = prices.groupby(['flow'])['Weight_flow'].transform('sum')




prices['price_1'] =  np.where(prices['impute'] == 2,
                              prices['price_0'] * prices['prod_sum_flow'] /  prices['Weight_flow'],
                              prices['price_1']
                             )

prices['price_rel'] =  np.where(prices['impute'] == 2,
                                prices['price_1'] / prices['price_0'],
                                prices['price_rel']
                               )


display(pd.crosstab(prices['impute'], columns='Frequency', margins=True))
print("\n" + "="*80)
print()

# -

prices

# ## Save result as parquet file

# +
prices.drop(columns=['Weight_flow', 'price_0'], inplace=True)
prices.rename(columns={'price_1': 'price'}, inplace=True)
prices['year'] = year
prices['quarter'] = quarter

imputefile = f'../data/price_impute_{flow}_{year}q{quarter}.parquet'
prices.to_parquet(imputefile)
print()
print("Final output")
print(f"Prices for selected sample for current period {year}q{quarter}")
print()
print(f'\nNOTE: Parquet file {imputefile} written with {prices.shape[0]} rows and {prices.shape[1]} columns\n')
show(prices, maxBytes=0)
# -










