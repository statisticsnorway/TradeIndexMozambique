* Encoding: UTF-8.
* Execute only once.
INSERT file='src\002 ValueLabelFromDataset.sps'.
INSERT file='src\005 Import_chapter_catalog.sps'.
INSERT file='src\007 Import_commodities_catalog.sps'.

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
read_quarter flow=Import year=2020 quarter=1 outlier_limit_upper=2.0 outlier_limit_lower=2.0.
read_quarter flow=Import year=2020 quarter=2 outlier_limit_upper=2.0 outlier_limit_lower=2.0.
read_quarter flow=Import year=2020 quarter=3 outlier_limit_upper=2.0 outlier_limit_lower=2.0.
read_quarter flow=Import year=2020 quarter=4 outlier_limit_upper=2.0 outlier_limit_lower=2.0.

* Yearly (2021, base 2020).
create_weight_base_population flow=Import year_1=2020.
create_weight_base flow=Import
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
                   .
base_prices flow=Import year=2021 year_1 = 2020 outlier_median_limit_upper=1.9 outlier_median_limit_lower=0.4 outlier_limit_upper=2.0 outlier_limit_lower=2.0.

* Quarterly (2021).
read_quarter flow=Import year=2021 quarter=1 outlier_limit_upper=2.0 outlier_limit_lower=2.0.
price_control flow=Import year_base=2020 year=2021 quarter=1 outlier_time_limit_upper=1.9 outlier_time_limit_lower=0.4 outlier_limit_upper=2.0 outlier_limit_lower=2.0.
impute_price flow=Import year_base=2020 quarter_1=4 year=2021 quarter=1.
indices_unchained flow=Import year_base=2020 year=2021 quarter=1.


read_quarter flow=Import year=2021 quarter=2 outlier_limit_upper=2.0 outlier_limit_lower=2.0.
price_control flow=Import year_base=2020 year=2021 quarter=2 outlier_time_limit_upper=1.9 outlier_time_limit_lower=0.4 outlier_limit_upper=2.0 outlier_limit_lower=2.0.
impute_price flow=Import year_base=2020 quarter_1=1 year=2021 quarter=2.
indices_unchained flow=Import year_base=2020 year=2021 quarter=2.


read_quarter flow=Import year=2021 quarter=3 outlier_limit_upper=2.0 outlier_limit_lower=2.0.
price_control flow=Import year_base=2020 year=2021 quarter=3 outlier_time_limit_upper=1.9 outlier_time_limit_lower=0.4 outlier_limit_upper=2.0 outlier_limit_lower=2.0.
impute_price flow=Import year_base=2020 quarter_1=2 year=2021 quarter=3.
indices_unchained flow=Import year_base=2020 year=2021 quarter=3.


read_quarter flow=Import year=2021 quarter=4 outlier_limit_upper=2.0 outlier_limit_lower=2.0.
price_control flow=Import year_base=2020 year=2021 quarter=4 outlier_time_limit_upper=1.9 outlier_time_limit_lower=0.4 outlier_limit_upper=2.0 outlier_limit_lower=2.0.
impute_price flow=Import year_base=2020 quarter_1=3 year=2021 quarter=4.
indices_unchained flow=Import year_base=2020 year=2021 quarter=4.


* After the first year (2021).
chain_first_year flow=Import year=2021.

* Yearly (2022, base 2021).
create_weight_base_population flow=Import year_1=2021.
create_weight_base flow=Import
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
                   .
base_prices flow=Import year=2022 year_1 = 2021 outlier_median_limit_upper=1.9 outlier_median_limit_lower=0.4 outlier_limit_upper=2.0 outlier_limit_lower=2.0.

* Quarterly (2022).
read_quarter flow=Import year=2022 quarter=1 outlier_limit_upper=2.0 outlier_limit_lower=2.0.
price_control flow=Import year_base=2021 year=2022 quarter=1 outlier_time_limit_upper=1.9 outlier_time_limit_lower=0.4 outlier_limit_upper=2.0 outlier_limit_lower=2.0.
impute_price flow=Import year_base=2021 quarter_1=4 year=2022 quarter=1.
indices_unchained flow=Import year_base=2021 year=2022 quarter=1.
chain_year flow=Import year_base=2021 year=2022 .

read_quarter flow=Import year=2022 quarter=2 outlier_limit_upper=2.0 outlier_limit_lower=2.0.
price_control flow=Import year_base=2021 year=2022 quarter=2 outlier_time_limit_upper=1.9 outlier_time_limit_lower=0.4 outlier_limit_upper=2.0 outlier_limit_lower=2.0.
impute_price flow=Import year_base=2021 quarter_1=1 year=2022 quarter=2.
indices_unchained flow=Import year_base=2021 year=2022 quarter=2.
chain_year flow=Import year_base=2021 year=2022 .

read_quarter flow=Import year=2022 quarter=3 outlier_limit_upper=2.0 outlier_limit_lower=2.0.
price_control flow=Import year_base=2021 year=2022 quarter=3 outlier_time_limit_upper=1.9 outlier_time_limit_lower=0.4 outlier_limit_upper=2.0 outlier_limit_lower=2.0.
impute_price flow=Import year_base=2021 quarter_1=2 year=2022 quarter=3.
indices_unchained flow=Import year_base=2021 year=2022 quarter=3.
chain_year flow=Import year_base=2021 year=2022 .

read_quarter flow=Import year=2022 quarter=4 outlier_limit_upper=2.0 outlier_limit_lower=2.0.
price_control flow=Import year_base=2021 year=2022 quarter=4 outlier_time_limit_upper=1.9 outlier_time_limit_lower=0.4 outlier_limit_upper=2.0 outlier_limit_lower=2.0.
impute_price flow=Import year_base=2021 quarter_1=3 year=2022 quarter=4.
indices_unchained flow=Import year_base=2021 year=2022 quarter=4.
chain_year flow=Import year_base=2021 year=2022 .

* Yearly (2023, base 2022).
create_weight_base_population flow=Import year_1=2022.
create_weight_base flow=Import
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


coverage flow=Import first_year=2020 last_year=2022 level=sitc1. 
coverage flow=Import first_year=2020 last_year=2022 level=sitc2. 
coverage flow=Import first_year=2020 last_year=2022 level=section. 
