* Encoding: UTF-8.
DATASET CLOSE all.
get FILE="data/index_chained_import.sav".

if (series = lag(series)) index_change = index_chained - lag(index_chained).
EXECUTE.
if (series = lag(series)) index_change_pct = (index_chained - lag(index_chained))*100/lag(index_chained).
EXECUTE.

* Encoding: UTF-8.
TEMPORARY.
SELECT IF (any(level,'Total') = 1). 
GRAPH /LINE = sum(index_change_pct) by time series 
      /TITLE='Percentage change: Total index  - Import'.

TEMPORARY.
SELECT IF (any(level,'Sitc 1') = 1 AND series = '3'). 
GRAPH /LINE = sum(index_change_pct) by time series 
      /TITLE='Percentage change: Index Sitc 1  - Import'.



TEMPORARY.
SELECT IF (any(level,'Sitc 2') = 1 AND series = '33'). 
GRAPH /LINE = sum(index_change_pct) by time series 
      /TITLE='Percentage change: Index Sitc 2  - Import'.



TEMPORARY.
SELECT IF (series = '76011000' OR series = '76011000x').
GRAPH /LINE = sum(index_change_pct) by time series 
      /TITLE='Percentage change: Index Commodity - HS8  - Import'.


