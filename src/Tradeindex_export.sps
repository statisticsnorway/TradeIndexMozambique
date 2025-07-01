* Encoding: UTF-8.
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
read_quarter flow=Export year=2020 quarter=1 outlier_sd_limit=2.0.
read_quarter flow=Export year=2020 quarter=2 outlier_sd_limit=2.0.
read_quarter flow=Export year=2020 quarter=3 outlier_sd_limit=2.0.
read_quarter flow=Export year=2020 quarter=4 outlier_sd_limit=2.0.


**********************************Year 2021****************************************************

**Yearly (1. quarter) - Selection of HS, Calculation of weights and base price**
**This program runs all the programs that shall be executed yearly. Most of the other programs are included and executed from here**

* Yearly (2021, base 2020).
create_weight_base_population flow=Export year_1=2020.

**Select parameteres for sample selection - What is acceptable price variation for each commodity. Stricter parameter --> less heterogeniety**
**Check coverage - How much of the population does the sample cover.**.
create_weight_base flow=Export
                   year_1=2020 
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
base_prices flow=Export year=2021 year_1 = 2020
                    outlier_median_year_limit_upper=2.5 
                    outlier_median_year_limit_lower=0.3
                    .

************************ Quarterly (2021)*******************************************************
  
*****1st quarter*************
** Select limits for outliers - standard deviation from mean**.
read_quarter flow=Export year=2021 quarter=1  
                    outlier_sd_limit=2.0
                    .

**'Check the data for extreme prices**
** Select limit for extreme price changes - price change from bace price (Q4 Y-1)**.
price_control flow=Export year_base=2020 year=2021 quarter=1 
                    outlier_time_limit_upper=2 
                    outlier_time_limit_lower=0.3 
                    .

**Impute missing prices in quarter**.
impute_price flow=Export year_base=2020 quarter_1=4 year=2021 quarter=1.

**Calculate unchained index quarter**.
indices_unchained flow=Export year_base=2020 year=2021 quarter=1.


*****2nd quarter*************.
** Select limits for outliers - standard deviation from mean**.
read_quarter flow=Export year=2021 quarter=2  
                    outlier_sd_limit=2.0
                    .

**'Check the data for extreme prices**
** Select limit for extreme price changes - price change from bace price (Q4 Y-1)**.
price_control flow=Export year_base=2020 year=2021 quarter=2 
                    outlier_time_limit_upper=2 
                    outlier_time_limit_lower=0.3 
                    .

**Impute missing prices in quarter**.
impute_price flow=Export year_base=2020 quarter_1=1 year=2021 quarter=2.

**Calculate unchained index quarter**.
indices_unchained flow=Export year_base=2020 year=2021 quarter=2.

*****3th quarter*************.
** Select limits for outliers - standard deviation from mean**.
read_quarter flow=Export year=2021 quarter=3  
                    outlier_sd_limit=2.0
                    .

**'Check the data for extreme prices**
** Select limit for extreme price changes - price change from bace price (Q4 Y-1)**.
price_control flow=Export year_base=2020 year=2021 quarter=3 
                    outlier_time_limit_upper=2 
                    outlier_time_limit_lower=0.3 
                    .

**Impute missing prices in quarter**.
impute_price flow=Export year_base=2020 quarter_1=2 year=2021 quarter=3.

**Calculate unchained index quarter**.
indices_unchained flow=Export year_base=2020 year=2021 quarter=3.

*****4th quarter*************.
** Select limits for outliers - standard deviation from mean**.
read_quarter flow=Export year=2021 quarter=4  
                    outlier_sd_limit=2.0
                    .

**'Check the data for extreme prices**
** Select limit for extreme price changes - price change from bace price (Q4 Y-1)**.
price_control flow=Export year_base=2020 year=2021 quarter=4 
                    outlier_time_limit_upper=2 
                    outlier_time_limit_lower=0.3 
                    .

**Impute missing prices in quarter**.
impute_price flow=Export year_base=2020 quarter_1=3 year=2021 quarter=4.

**Calculate unchained index quarter**.
indices_unchained flow=Export year_base=2020 year=2021 quarter=4.


**Calculate chained index**
**This will start when all quarters of the first index year have been processed. There is ine syntax for chaining the first year and one for further chaining.**
**Attention! only change first_index_year, when updating reference year (not the same as base year)**.
chain_first_year flow=Export year=2021.


**********************************Year 2022****************************************************

**Yearly (1. quarter) - Selection of HS, Calculation of weights and base price**
**This program runs all the programs that shall be executed yearly. Most of the other programs are included and executed from here**

* Yearly (2022, base 2021).
create_weight_base_population flow=Export year_1=2021.

**Select parameteres for sample selection - What is acceptable price variation for each commodity. Stricter parameter --> less heterogeniety**
**Check coverage - How much of the population does the sample cover.**.
create_weight_base flow=Export
                   year_1=2021 
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
base_prices flow=Export year=2022 year_1 = 2021
                    outlier_median_year_limit_upper=2.5 
                    outlier_median_year_limit_lower=0.3
                    .

************************ Quarterly (2022)*******************************************************
  
*****1st quarter*************
** Select limits for outliers - standard deviation from mean**.
read_quarter flow=Export year=2022 quarter=1  
                    outlier_sd_limit=2.0
                    .

**'Check the data for extreme prices**
** Select limit for extreme price changes - price change from bace price (Q4 Y-1)**.
price_control flow=Export year_base=2021 year=2022 quarter=1 
                    outlier_time_limit_upper=2 
                    outlier_time_limit_lower=0.3 
                    .

**Impute missing prices in quarter**.
impute_price flow=Export year_base=2021 quarter_1=4 year=2022 quarter=1.

**Calculate unchained index quarter**.
indices_unchained flow=Export year_base=2021 year=2022 quarter=1.

*****2nd quarter*************.
** Select limits for outliers - standard deviation from mean**.
read_quarter flow=Export year=2022 quarter=2  
                    outlier_sd_limit=2.0
                    .

**'Check the data for extreme prices**
** Select limit for extreme price changes - price change from bace price (Q4 Y-1)**.
price_control flow=Export year_base=2021 year=2022 quarter=2 
                    outlier_time_limit_upper=2 
                    outlier_time_limit_lower=0.3 
                    .

**Impute missing prices in quarter**.
impute_price flow=Export year_base=2021 quarter_1=1 year=2022 quarter=2.

**Calculate unchained index quarter**.
indices_unchained flow=Export year_base=2021 year=2022 quarter=2.

*****3th quarter*************.
** Select limits for outliers - standard deviation from mean**.
read_quarter flow=Export year=2022 quarter=3  
                    outlier_sd_limit=2.0
                    .

**'Check the data for extreme prices**
** Select limit for extreme price changes - price change from bace price (Q4 Y-1)**.
price_control flow=Export year_base=2021 year=2022 quarter=3 
                    outlier_time_limit_upper=2 
                    outlier_time_limit_lower=0.3 
                    .

**Impute missing prices in quarter**.
impute_price flow=Export year_base=2021 quarter_1=2 year=2022 quarter=3.

**Calculate unchained index quarter**.
indices_unchained flow=Export year_base=2021 year=2022 quarter=3.

*****4th quarter*************.
** Select limits for outliers - standard deviation from mean**.
read_quarter flow=Export year=2022 quarter=4  
                    outlier_sd_limit=2.0
                    .

**'Check the data for extreme prices**
** Select limit for extreme price changes - price change from bace price (Q4 Y-1)**.
price_control flow=Export year_base=2021 year=2022 quarter=4 
                    outlier_time_limit_upper=2 
                    outlier_time_limit_lower=0.3 
                    .

**Impute missing prices in quarter**.
impute_price flow=Export year_base=2021 quarter_1=3 year=2022 quarter=4.

**Calculate unchained index quarter**.
indices_unchained flow=Export year_base=2021 year=2022 quarter=4.



chain_year flow=Export year_base=2021 year=2022 .


**********************************Year 2023****************************************************

**Yearly (1. quarter) - Selection of HS, Calculation of weights and base price**
**This program runs all the programs that shall be executed yearly. Most of the other programs are included and executed from here**

* Yearly (2023, base 2022).
create_weight_base_population flow=Export year_1=2022.

**Select parameteres for sample selection - What is acceptable price variation for each commodity. Stricter parameter --> less heterogeniety**
**Check coverage - How much of the population does the sample cover.**.
create_weight_base flow=Export
                   year_1=2022 
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
base_prices flow=Export year=2023 year_1 = 2022
                    outlier_median_year_limit_upper=2.5 
                    outlier_median_year_limit_lower=0.3
                    .

************************ Quarterly (2023)*******************************************************
  
*****1st quarter*************
** Select limits for outliers - standard deviation from mean**.
read_quarter flow=Export year=2023 quarter=1  
                    outlier_sd_limit=2.0
                    .

**'Check the data for extreme prices**
** Select limit for extreme price changes - price change from bace price (Q4 Y-1)**.
price_control flow=Export year_base=2022 year=2023 quarter=1 
                    outlier_time_limit_upper=2 
                    outlier_time_limit_lower=0.3 
                    .

**Impute missing prices in quarter**.
impute_price flow=Export year_base=2022 quarter_1=4 year=2023 quarter=1.

**Calculate unchained index quarter**.
indices_unchained flow=Export year_base=2022 year=2023 quarter=1.

*****2nd quarter*************.
** Select limits for outliers - standard deviation from mean**.
read_quarter flow=Export year=2023 quarter=2  
                    outlier_sd_limit=2.0
                    .

**'Check the data for extreme prices**
** Select limit for extreme price changes - price change from bace price (Q4 Y-1)**.
price_control flow=Export year_base=2022 year=2023 quarter=2 
                    outlier_time_limit_upper=2 
                    outlier_time_limit_lower=0.3 
                    .

**Impute missing prices in quarter**.
impute_price flow=Export year_base=2022 quarter_1=1 year=2023 quarter=2.

**Calculate unchained index quarter**.
indices_unchained flow=Export year_base=2022 year=2023 quarter=2.

*****3th quarter*************.
** Select limits for outliers - standard deviation from mean**.
read_quarter flow=Export year=2023 quarter=3  
                    outlier_sd_limit=2.0
                    .

**'Check the data for extreme prices**
** Select limit for extreme price changes - price change from bace price (Q4 Y-1)**.
price_control flow=Export year_base=2022 year=2023 quarter=3 
                    outlier_time_limit_upper=2 
                    outlier_time_limit_lower=0.3 
                    .

**Impute missing prices in quarter**.
impute_price flow=Export year_base=2022 quarter_1=2 year=2023 quarter=3.

**Calculate unchained index quarter**.
indices_unchained flow=Export year_base=2022 year=2023 quarter=3.

*****4th quarter*************.
** Select limits for outliers - standard deviation from mean**.
read_quarter flow=Export year=2023 quarter=4  
                    outlier_sd_limit=2.0
                    .

**'Check the data for extreme prices**
** Select limit for extreme price changes - price change from bace price (Q4 Y-1)**.
price_control flow=Export year_base=2022 year=2023 quarter=4 
                    outlier_time_limit_upper=2 
                    outlier_time_limit_lower=0.3 
                    .

**Impute missing prices in quarter**.
impute_price flow=Export year_base=2022 quarter_1=3 year=2023 quarter=4.

**Calculate unchained index quarter**.
indices_unchained flow=Export year_base=2022 year=2023 quarter=4.



chain_year flow=Export year_base=2022 year=2023 .


coverage flow=Export first_year=2020 last_year=2023 level=sitc1. 
coverage flow=Export first_year=2020 last_year=2023 level=sitc2. 
coverage flow=Export first_year=2020 last_year=2023 level=section. 


