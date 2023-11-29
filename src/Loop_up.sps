* Encoding: UTF-8.
DATASET CLOSE all.
get file='Data/tradedata_Export_2022.sav'.

SELECT IF (comno = '71039100').
sort cases by quarter (A) price (d).

