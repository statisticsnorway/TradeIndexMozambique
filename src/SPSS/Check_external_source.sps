* Encoding: UTF-8.

DATASET CLOSE all.
GET DATA
  /TYPE=XLSX
  /FILE='data\Externla source List.xlsx'
  /SHEET=name 'Export'
  /CELLRANGE=FULL
  /READNAMES=ON
 .
EXECUTE.

STRING flow (a1).
COMPUTE flow = 'E'.
ALTER TYPE Description (a99) .
ALTER TYPE Group (a66).
EXECUTE. 

SORT CASES by flow comno.

SAVE OUTFILE='temp/extern_source_export.sav'.

DATASET CLOSE all.
GET DATA
  /TYPE=XLSX
  /FILE='data\Externla source List.xlsx'
  /SHEET=name 'Import'
  /CELLRANGE=FULL
  /READNAMES=ON
 .
EXECUTE.

STRING flow (a1).
COMPUTE flow = 'I'.
ALTER TYPE Description (a99) .
ALTER TYPE Group (a66).
EXECUTE. 

SORT CASES by flow comno.

SAVE OUTFILE='temp/extern_source_import.sav'.

DATASET CLOSE all.
ADD FILES file='temp/extern_source_export.sav'
         /file='temp/extern_source_import.sav'
         .
EXECUTE.
MATCH FILES file=*
           /last=last
           /by flow Comno
           .
EXECUTE.
SELECT IF (last = 1).
EXECUTE.
DELETE VARIABLES last.

SAVE OUTFILE='data/extern_source.sav'.

MATCH FILES file='data/tradedata_Export_2022.sav'
           /table=*
           /in=ext_source
           /by flow Comno
           .
EXECUTE.

SELECT IF (ext_source = 1).

recode outlier_dev_median_q
    (0 = 0)
    (1 = 2)
    (2 = 1)
    into outlier_dev_median_quarter
    .
VALUE LABELS outlier_dev_median_quarter
 0 'No outlier'
 1 'Special case, kept'
 2 'Outlier'
 .  
CTABLES
  /FORMAT MAXCOLWIDTH=128
  /VLABELS VARIABLES=comno outlier_dev_median_quarter value price DISPLAY=NONE
  /VLABELS VARIABLES=value price DISPLAY=LABEL
  /TABLE comno > outlier_dev_median_quarter BY value [COUNT F40.0, SUM, COLPCT.SUM PCT40.1] + price [MEAN F40.1, STDDEV F40.1]
  /CATEGORIES VARIABLES=comno ORDER=A KEY=VALUE EMPTY=EXCLUDE TOTAL=YES POSITION=BEFORE LABEL='Grand total'
  /CATEGORIES VARIABLES=outlier_dev_median_quarter ORDER=A KEY=VALUE EMPTY=EXCLUDE TOTAL=YES POSITION=BEFORE
  /TITLES
    TITLE='Outlier share for commodities with external sources of data'.





