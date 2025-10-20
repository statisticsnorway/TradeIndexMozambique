* Encoding: UTF-8.
DATASET CLOSE all.
get FILE="data/index_chained_Import.sav".

* Encoding: UTF-8.
TEMPORARY.
SELECT IF (any(level,'Total') = 1). 
GRAPH /LINE = mean(index_chained) by time 
      /TITLE='Total index'.
   TITLE='Chained index.'.

TEMPORARY.
SELECT IF (any(level,'Sitc 1') = 1 AND series = '3'). 
GRAPH /LINE = mean(index_chained) by time series
      /TITLE='Index sitc'.
   TITLE='Chained index.'.



TEMPORARY.
SELECT IF (any(level,'Sitc 2') = 1 AND series = '33'). 
GRAPH /LINE = mean(index_chained) by time series
      /TITLE='Index sitc'.
   TITLE='Chained index.'.



TEMPORARY.
SELECT IF (series = '27101939' OR series = '27101239').
GRAPH /LINE = mean(index_chained) by time series
      /TITLE='Index sitc'.
   TITLE='Chained index.'.


