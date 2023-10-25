* Encoding: UTF-8.
DATASET CLOSE all.
get FILE="data/index_chained_Export.sav".

if (series = lag(series)) index_change = index_chained - lag(index_chained).
EXECUTE.
if (series = lag(series)) index_change_pct = (index_chained - lag(index_chained))*100/lag(index_chained).
EXECUTE.

TEMPORARY.
SELECT IF (level = 'Sitc 1').
GRAPH /LINE = sum(index_change_pct) by time series 
      /TITLE='Percentage change'.

TEMPORARY.
SELECT IF (level = 'Sitc 1').
GRAPH /LINE = sum(index_chained) by time series 
      /TITLE='Chained index'.


