* Encoding: UTF-8.
DEFINE coverage(first_year=!tokens(1) 
               /last_year=!tokens(1)                     
               /flow=!tokens(1)
               /level=!tokens(1)
               )
               
DATASET CLOSE ALL.
GET FILE=!quote(!concat('data/coverage_',!level,'_',!flow,'_',!first_year,'.sav')).
 !DO !y = !first_year !TO !last_year
  ADD FILES file=*
           /file=!quote(!concat('data/coverage_',!level,'_',!flow,'_',!y,'.sav')).
 !DOEND 

* As me may not do mathematical calculations on macro variables, we read the first file twice and delete duplicates.
sort cases by  year flow !level.
MATCH FILES FILE=*
           /LAST=last_idx
           /BY year flow !level
           .

SELECT IF (last_idx = 1).
EXECUTE.
delete variables last_idx.
execute.

formats Ssample_sum (f14) Spop_sum (f14) Tsample_sum (f14) Tpop_sum (f14) .

!IF (!level = 'sitc1' !or !level = 'sitc2') !THEN
 INSERT file=!quote(!concat('src/valuelabels_',!level,'.sps')).
!IFEND

VALUE LABELS flow
    'I' 'Import'
    'E' 'Export'
    .

OMS 
    /SELECT TABLES
    /DESTINATION FORMAT=XLSX OUTFILE=!quote(!concat('temp/coverage_',!level,'_',!flow,'_',!first_year,'_',!last_year,'.xlsx')).
CTABLES
  /FORMAT EMPTY=ZERO MISSING='.' MINCOLWIDTH=124 MAXCOLWIDTH=256 UNITS=POINTS
  /SMISSING VARIABLE
  /VLABELS VARIABLES=flow Year !level DISPLAY=NONE
  /VLABELS VARIABLES=Ssample_sum Spop_sum Sno_of_comm Scoverage Tcoverage DISPLAY=label
  /TABLE flow > !level BY (Ssample_sum [SUM F40.0 COLPCT.SUM] + Spop_sum [SUM F40.0 COLPCT.SUM] + Sno_of_comm 
    [SUM] + Scoverage [MEAN] + Tcoverage 
    [MEAN]) > Year [C]
  /SLABELS VISIBLE=NO
  /CATEGORIES VARIABLES=flow Year ORDER=A KEY=VALUE EMPTY=EXCLUDE
  /CATEGORIES VARIABLES=!level ORDER=A KEY=VALUE EMPTY=EXCLUDE TOTAL=YES POSITION=BEFORE
.
OMSEND.

!ENDDEFINE.



