﻿* Encoding: UTF-8.
* Execute only once.
INSERT file='src\002 ValueLabelFromDataset.sps'.
INSERT file='src\005 Import_chapter_catalog.sps'.
INSERT file='src\007 Import_commodities_catalog.sps'.
INSERT file='src\008 Import_special_series_list.sps'.

* Execute every time we run the index.
INSERT file='src\T10M Read_trade_quarter.sps'.
INSERT file='src\A10M CreateWightBasePopulation.sps'.
INSERT file='src\A20M CreateWeightBase.sps'.
INSERT file='src\A30M Base_price.sps'.
INSERT file='src\T40M Price_control.sps'.
INSERT file='src\T50M Impute_prices.sps'.
INSERT file='src\T60M Index_unchained.sps'.
INSERT file='src\T71M Chain_first_year.sps'.
INSERT file='src\T72M Chain_next_years.sps'.
INSERT file='src\T80M Coverage.sps'.


* Quarterly first year.
** Select limits for outliers - standard deviation from mean**.
read_quarter flow=Import year=2023 quarter=1 outlier_sd_limit=2.0.
read_quarter flow=Import year=2023 quarter=2 outlier_sd_limit=2.0.
read_quarter flow=Import year=2023 quarter=3 outlier_sd_limit=2.0.
read_quarter flow=Import year=2023 quarter=4 outlier_sd_limit=2.0.


**********************************Year 2023****************************************************

**Yearly (1. quarter) - Selection of HS, Calculation of weights and base price**
**This program runs all the programs that shall be executed yearly. Most of the other programs are included and executed from here**

* Yearly (2024, base 2023).
create_weight_base_population flow=Import year_1=2023.

**Select parameteres for sample selection - What is acceptable price variation for each commodity. Stricter parameter --> less heterogeniety**
**Check coverage - How much of the population does the sample cover.**.
create_weight_base flow=Import
                   year_1=2023 
                   share_total=0.05
                   no_of_months=5
                   no_of_months_seasons=3
                   section_seasons='II'
                   price_cv=0.5
                   max_by_min=10
                   max_by_median=5
                   median_by_min=5
                   share_small=0.0001
                   no_of_transactions=10
                   .

** Select limit for extreme price changes - price change from median price in base year**.
**Check imputation of base prices**.
base_prices flow=Import year=2024 year_1 = 2023
                    outlier_median_year_limit_upper=2.0 
                    outlier_median_year_limit_lower=0.5
                    .

************************ Quarterly (2024)*******************************************************
  
*****1st quarter*************
** Select limits for outliers - standard deviation from mean**.
read_quarter flow=Import year=2024 quarter=1  
                    outlier_sd_limit=2.0
                    .

**'Check the data for extreme prices**
** Select limit for extreme price changes - price change from bace price (Q4 Y-1)**.
price_control flow=Import year_base=2023 year=2024 quarter=1 
                    outlier_time_limit_upper=2 
                    outlier_time_limit_lower=0.5 
                    .

**Impute missing prices in quarter**.
impute_price flow=Import year_base=2023 quarter_1=4 year=2024 quarter=1.

**Calculate unchained index quarter**.
indices_unchained flow=Import year_base=2023 year=2024 quarter=1.


*****2nd quarter*************.
** Select limits for outliers - standard deviation from mean**.
read_quarter flow=Import year=2024 quarter=2  
                    outlier_sd_limit=2.0
                    .

**'Check the data for extreme prices**
** Select limit for extreme price changes - price change from bace price (Q4 Y-1)**.
price_control flow=Import year_base=2023 year=2024 quarter=2 
                    outlier_time_limit_upper=2 
                    outlier_time_limit_lower=0.5 
                    .

**Impute missing prices in quarter**.
impute_price flow=Import year_base=2023 quarter_1=1 year=2024 quarter=2.

**Calculate unchained index quarter**.
indices_unchained flow=Import year_base=2023 year=2024 quarter=2.

*****3th quarter*************.
** Select limits for outliers - standard deviation from mean**.
read_quarter flow=Import year=2024 quarter=3  
                    outlier_sd_limit=2.0
                    .

**'Check the data for extreme prices**
** Select limit for extreme price changes - price change from bace price (Q4 Y-1)**.
price_control flow=Import year_base=2023 year=2024 quarter=3 
                    outlier_time_limit_upper=2 
                    outlier_time_limit_lower=0.5 
                    .

**Impute missing prices in quarter**.
impute_price flow=Import year_base=2023 quarter_1=2 year=2024 quarter=3.

**Calculate unchained index quarter**.
indices_unchained flow=Import year_base=2023 year=2024 quarter=3.

*****4th quarter*************.
** Select limits for outliers - standard deviation from mean**.
read_quarter flow=Import year=2024 quarter=4  
                    outlier_sd_limit=2.0
                    .

**'Check the data for extreme prices**
** Select limit for extreme price changes - price change from bace price (Q4 Y-1)**.
price_control flow=Import year_base=2023 year=2024 quarter=4 
                    outlier_time_limit_upper=2 
                    outlier_time_limit_lower=0.5 
                    .

**Impute missing prices in quarter**.
impute_price flow=Import year_base=2023 quarter_1=3 year=2024 quarter=4.

**Calculate unchained index quarter**.
indices_unchained flow=Import year_base=2023 year=2024 quarter=4.


**Calculate chained index**
**This will start when all quarters of the first index year have been processed. There is ine syntax for chaining the first year and one for further chaining.**
**Attention! only change first_index_year, when updating reference year (not the same as base year)**.
chain_first_year flow=Import year=2024.


**********************************Year 2025****************************************************

**Yearly (1. quarter) - Selection of HS, Calculation of weights and base price**
**This program runs all the programs that shall be executed yearly. Most of the other programs are included and executed from here**

* Yearly (2025, base 2024).
create_weight_base_population flow=Import year_1=2024.

**Select parameteres for sample selection - What is acceptable price variation for each commodity. Stricter parameter --> less heterogeniety**
**Check coverage - How much of the population does the sample cover.**.
create_weight_base flow=Import
                   year_1=2024 
                   share_total=0.05
                   no_of_months=5
                   no_of_months_seasons=3
                   section_seasons='II'
                   price_cv=0.5
                   max_by_min=10
                   max_by_median=5
                   median_by_min=5
                   share_small=0.0001
                   no_of_transactions=10
                   .

** Select limit for extreme price changes - price change from median price in base year**.
**Check imputation of base prices**.
base_prices flow=Import year=2025 year_1 = 2024
                    outlier_median_year_limit_upper=2.0 
                    outlier_median_year_limit_lower=0.5
                    .

************************ Quarterly (2025)*******************************************************
  
*****1st quarter*************
** Select limits for outliers - standard deviation from mean**.
read_quarter flow=Import year=2025 quarter=1  
                    outlier_sd_limit=2.0
                    .

**'Check the data for extreme prices**
** Select limit for extreme price changes - price change from bace price (Q4 Y-1)**.
price_control flow=Import year_base=2024 year=2025 quarter=1 
                    outlier_time_limit_upper=2 
                    outlier_time_limit_lower=0.5 
                    .

**Impute missing prices in quarter**.
impute_price flow=Import year_base=2024 quarter_1=4 year=2025 quarter=1.

**Calculate unchained index quarter**.
indices_unchained flow=Import year_base=2024 year=2025 quarter=1.

*****2nd quarter*************.
** Select limits for outliers - standard deviation from mean**.
read_quarter flow=Import year=2025 quarter=2  
                    outlier_sd_limit=2.0
                    .

**'Check the data for extreme prices**
** Select limit for extreme price changes - price change from bace price (Q4 Y-1)**.
price_control flow=Import year_base=2024 year=2025 quarter=2 
                    outlier_time_limit_upper=2 
                    outlier_time_limit_lower=0.5 
                    .

**Impute missing prices in quarter**.
impute_price flow=Import year_base=2024 quarter_1=1 year=2025 quarter=2.

**Calculate unchained index quarter**.
indices_unchained flow=Import year_base=2024 year=2025 quarter=2.

*****3th quarter*************.
** Select limits for outliers - standard deviation from mean**.
read_quarter flow=Import year=2025 quarter=3  
                    outlier_sd_limit=2.0
                    .

**'Check the data for extreme prices**
** Select limit for extreme price changes - price change from bace price (Q4 Y-1)**.
price_control flow=Import year_base=2024 year=2025 quarter=3 
                    outlier_time_limit_upper=2 
                    outlier_time_limit_lower=0.5 
                    .

**Impute missing prices in quarter**.
impute_price flow=Import year_base=2024 quarter_1=2 year=2025 quarter=3.

**Calculate unchained index quarter**.
indices_unchained flow=Import year_base=2024 year=2025 quarter=3.

*****4th quarter*************.
** Select limits for outliers - standard deviation from mean**.
read_quarter flow=Import year=2025 quarter=4  
                    outlier_sd_limit=2.0
                    .

**'Check the data for extreme prices**
** Select limit for extreme price changes - price change from bace price (Q4 Y-1)**.
price_control flow=Import year_base=2024 year=2025 quarter=4 
                    outlier_time_limit_upper=2 
                    outlier_time_limit_lower=0.5 
                    .

**Impute missing prices in quarter**.
impute_price flow=Import year_base=2024 quarter_1=3 year=2025 quarter=4.

**Calculate unchained index quarter**.
indices_unchained flow=Import year_base=2024 year=2025 quarter=4.



chain_year flow=Import year_base=2024 year=2025 .




coverage flow=Import first_year=2023 last_year=2024 level=sitc1. 
coverage flow=Import first_year=2023 last_year=2024 level=sitc2. 
coverage flow=Import first_year=2023 last_year=2024 level=section. 


