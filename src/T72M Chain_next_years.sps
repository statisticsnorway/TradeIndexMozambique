* Encoding: UTF-8.

DEFINE chain_year(year_base=!tokens(1)
                 /year=!tokens(1)
                 )


DATASET CLOSE all.

* First, get the index from last quarter previous year.
GET FILE='data\index_chained.sav' /KEEP=flow level series index_chained year quarter.
SELECT IF (year = !year_base and quarter = 4).
EXECUTE.
RENAME VARIABLES index_chained = index_chained_base.
    
DELETE VARIABLES Year quarter.

* Match with actual year.
MATCH FILES FILE=!quote(!concat('Data/index_unchained_',!year,'.sav'))
           /TABLE=*
           /BY flow level series
           .
EXECUTE.

SAVE OUTFILE='temp\index_chained_detailed.sav'.

SELECT IF (level = 'Total' and quarter = 1).
EXECUTE.
RENAME VARIABLES index_chained_base = index_total_base.
SAVE OUTFILE 'temp\index_chained_total.sav' /keep=flow index_total_base.

MATCH FILES file='temp\index_chained_detailed.sav'
           /TABLE='temp\index_chained_total.sav'
           /BY flow.
EXECUTE.

COMPUTE impute_index_chained_base = missing(index_chained_base).
IF (missing(index_chained_base) = 1) index_chained_base = index_total_base.
EXECUTE.

COMPUTE chain_factor = index_chained_base / 100.
COMPUTE index_chained = chain_factor * index_unchained.
EXECUTE.

DELETE VARIABLES index_total_base.
EXECUTE.

ADD FILES FILE='data\index_chained.sav'
         /FILE=*
         .
EXECUTE.

SORT CASES BY flow level series year quarter.
MATCH FILES FILE=*
           /LAST=last_idx
           /BY flow level series year quarter
           .
FREQUENCIES last_idx time.

SELECT IF (last_idx = 1).
EXECUTE.
FREQUENCIES last_idx.
DELETE VARIABLES last_idx.

* Table created only for the last 4 years.
TEMPORARY.
SELECT IF (year >= !year-3).
CTABLES
  /VLABELS VARIABLES=flow level series time index_chained DISPLAY=NONE
  /TABLE flow > level > series BY time > index_chained [MEAN]
  /SLABELS VISIBLE=NO
  /CATEGORIES VARIABLES=flow level series time ORDER=A KEY=VALUE EMPTY=EXCLUDE
  /CRITERIA CILEVEL=95
  /TITLES
    TITLE='Chained index.'.

SAVE OUTFILE='data\index_chained.sav'.

!ENDDEFINE.

