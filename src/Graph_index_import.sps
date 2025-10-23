* Encoding: UTF-8.
DATASET CLOSE all.
get FILE="data/index_chained_import.sav".

* Encoding: UTF-8.
TEMPORARY.
SELECT IF (any(level,'Total') = 1). 
GRAPH /LINE = mean(index_chained) by time 
      /TITLE='Total index  - Import (2024=100)'.
   TITLE='Chained index.'.

TEMPORARY.
SELECT IF (any(level,'Sitc 1') = 1 AND series = '3'). 
GRAPH /LINE = mean(index_chained) by time series
      /TITLE='Index Sitc 1  - Import (2024=100)'.
   TITLE='Chained index.'.



TEMPORARY.
SELECT IF (any(level,'Sitc 2') = 1 AND series = '33'). 
GRAPH /LINE = mean(index_chained) by time series
      /TITLE='Index Sitc 2  - Import (2024=100)'.
   TITLE='Chained index.'.



TEMPORARY.
SELECT IF (series = '76011000' OR series = '76011000x').
GRAPH /LINE = mean(index_chained) by time series
      /TITLE='Index Commodity - HS8  - Import (2024=100)'.
   TITLE='Chained index.'.


