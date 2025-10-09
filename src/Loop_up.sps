* Encoding: UTF-8.
DATASET CLOSE all.
get file='Data/tradedata_Export_2023.sav'.

SELECT IF (comno = '07139010').
sort cases by quarter (A) price (d).

* Encoding: UTF-8.
DATASET CLOSE all.
get file='Data/weight_base_population_Export_2023.sav'.

SELECT IF (comno = '07139010').
sort cases by quarter (A) price (d).


