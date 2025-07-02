* Encoding: UTF-8.
TEMPORARY.
SELECT IF (any(level,'Total') = 1). 
GRAPH /LINE = mean(index_chained) by time 
      /TITLE='Total index'.
   TITLE='Chained index.'.

TEMPORARY.
SELECT IF (any(level,'Sitc 1') = 1). 
GRAPH /LINE = mean(index_chained) by time series
      /TITLE='Index sitc'.
   TITLE='Chained index.'.


