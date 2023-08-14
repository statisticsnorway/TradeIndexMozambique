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


* Quarterly first year.
read_quarter flow=Export year=2018 quarter=1.
read_quarter flow=Export year=2018 quarter=2.
read_quarter flow=Export year=2018 quarter=3.
read_quarter flow=Export year=2018 quarter=4.


* Yearly (first year 2019, base year 2018).
create_weight_base_population year_1=2018 outlier_limit=2.0 .
create_weight_base year_1=2018 
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
base_prices year=2019 year_1 = 2018.

* Quarterly (2019).
read_quarter flow=Export year=2019 quarter=1.
price_control year_base=2018 year=2019 quarter=1.
impute_price year_base=2018 quarter_1=4 year=2019 quarter=1.
indices_unchained year_base=2018 year=2019 quarter=1.

read_quarter flow=Export year=2019 quarter=2.
price_control year_base=2018 year=2019 quarter=2.
impute_price year_base=2018 quarter_1=1 year=2019 quarter=2.
indices_unchained year_base=2018 year=2019 quarter=2.

read_quarter flow=Export year=2019 quarter=3.
price_control year_base=2018 year=2019 quarter=3.
impute_price year_base=2018 quarter_1=2 year=2019 quarter=3.
indices_unchained year_base=2018 year=2019 quarter=3.

read_quarter flow=Export year=2019 quarter=4.
price_control year_base=2018 year=2019 quarter=4.
impute_price year_base=2018 quarter_1=3 year=2019 quarter=4.
indices_unchained year_base=2018 year=2019 quarter=4.

* After the first year (2019).
chain_first_year year=2019.

* Yearly (2020, base 2019).
create_weight_base_population year_1=2019 outlier_limit=2.0 .
create_weight_base year_1=2019 
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
base_prices year=2020 year_1 = 2019.

* Quarterly (2020).
read_quarter flow=Export year=2020 quarter=1.
price_control year_base=2019 year=2020 quarter=1.
impute_price year_base=2019 quarter_1=4 year=2020 quarter=1.
indices_unchained year_base=2019 year=2020 quarter=1.
chain_year year_base=2019 year=2020 .

read_quarter flow=Export year=2020 quarter=2.
price_control year_base=2019 year=2020 quarter=2.
impute_price year_base=2019 quarter_1=1 year=2020 quarter=2.
indices_unchained year_base=2019 year=2020 quarter=2.
chain_year year_base=2019 year=2020 .

read_quarter flow=Export year=2020 quarter=3.
price_control year_base=2019 year=2020 quarter=3.
impute_price year_base=2019 quarter_1=2 year=2020 quarter=3.
indices_unchained year_base=2019 year=2020 quarter=3.
chain_year year_base=2019 year=2020 .

read_quarter flow=Export year=2020 quarter=4.
price_control year_base=2019 year=2020 quarter=4.
impute_price year_base=2019 quarter_1=3 year=2020 quarter=4.
indices_unchained year_base=2019 year=2020 quarter=4.
chain_year year_base=2019 year=2020 .


* Yearly (2021, base 2020).
create_weight_base_population year_1=2020 outlier_limit=2.0 .
create_weight_base year_1=2020 
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
base_prices year=2021 year_1 = 2020.

* Quarterly (2021).
read_quarter flow=Export year=2021 quarter=1.
price_control year_base=2020 year=2021 quarter=1.
impute_price year_base=2020 quarter_1=4 year=2021 quarter=1.
indices_unchained year_base=2020 year=2021 quarter=1.
chain_year year_base=2020 year=2021 .

read_quarter flow=Export year=2021 quarter=2.
price_control year_base=2020 year=2021 quarter=2.
impute_price year_base=2020 quarter_1=1 year=2021 quarter=2.
indices_unchained year_base=2020 year=2021 quarter=2.
chain_year year_base=2020 year=2021 .

read_quarter flow=Export year=2021 quarter=3.
price_control year_base=2020 year=2021 quarter=3.
impute_price year_base=2020 quarter_1=2 year=2021 quarter=3.
indices_unchained year_base=2020 year=2021 quarter=3.
chain_year year_base=2020 year=2021 .

read_quarter flow=Export year=2021 quarter=4.
price_control year_base=2020 year=2021 quarter=4.
impute_price year_base=2020 quarter_1=3 year=2021 quarter=4.
indices_unchained year_base=2020 year=2021 quarter=4.
chain_year year_base=2020 year=2021 .



