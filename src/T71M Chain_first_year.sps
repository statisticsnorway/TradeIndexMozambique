* Encoding: UTF-8.

DEFINE chain_first_year(year=!tokens(1))


DATASET CLOSE all.

* Choose first year.
GET FILE=!quote(!concat('Data/index_unchained_',!year,'.sav')).

AGGREGATE /OUTFILE=* MODE=ADDVARIABLES
          /BREAK=flow series level Year
          /index_mean = MEAN(index_unchained)
          .
EXECUTE.

COMPUTE index_chained = index_unchained * 100 / index_mean.
EXECUTE.

DELETE VARIABLES index_mean.
EXECUTE.

CTABLES
  /VLABELS VARIABLES=flow level series time index_chained DISPLAY=NONE
  /TABLE flow > level > series BY time > index_chained [MEAN]
  /SLABELS VISIBLE=NO
  /CATEGORIES VARIABLES=flow level series time ORDER=A KEY=VALUE EMPTY=EXCLUDE
  /TITLES
    TITLE='Chained index.'.
    
SAVE OUTFILE='data\index_chained.sav'.

!ENDDEFINE.


