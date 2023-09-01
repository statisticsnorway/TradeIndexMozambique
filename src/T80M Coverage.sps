* Encoding: UTF-8.
DEFINE coverage(first_year=!tokens(1) 
               /last_year=!tokens(1)                     
               /flow=!tokens(1)
               /level=!tokens(1)
               )

DATASET CLOSE ALL.
*GET FILE=!quote(!concat('data/coverage_',!level,'_',!flow,'_',!first_year,'.sav')).
 !DO !y = !first_year !TO !last_year
  ADD FILES file=*
           /file=!quote(!concat('data/coverage_',!level,'_',!flow,'_',!y,'.sav')).
 !DOEND 

formats Ssample_sum (f14) Spop_sum (f14) Tsample_sum (f14) Tpop_sum (f14) .

!IF (!level = 'sitc1' !or !level = 'sitc2') !THEN
 INSERT file=!quote(!concat('src/valuelabels_',!level,'.sps')).
!IFEND

VALUE LABELS flow
    1 'Import'
    2 'Export'
    .

OMS 
    /SELECT TABLES
    /DESTINATION FORMAT=XLSX OUTFILE=!quote(!concat('temp/coverage_',!level,'_',!flow,'_',!first_year,'_',!last_year,'.xlsx')).
CTABLES
  /FORMAT EMPTY=ZERO MISSING='.' MINCOLWIDTH=124 MAXCOLWIDTH=256 UNITS=POINTS
  /SMISSING VARIABLE
  /VLABELS VARIABLES=flow Year !level 
    DISPLAY=NONE
  /VLABELS VARIABLES=Ssample_sum Spop_sum Sno_of_comm Tsample_sum Tpop_sum 
    Tno_of_comm Scoverage Tcoverage 
    DISPLAY=label
  /TABLE flow > !level BY (Ssample_sum [MEAN ] + Spop_sum [MEAN] + Sno_of_comm 
    [MEAN] + Tsample_sum [MEAN] + Tpop_sum [MEAN] + Tno_of_comm [MEAN] + Scoverage [MEAN] + Tcoverage 
    [MEAN]) > Year [C]
  /SLABELS VISIBLE=NO
  /CATEGORIES VARIABLES=flow Year !level ORDER=A KEY=VALUE EMPTY=EXCLUDE
.
OMSEND.

!ENDDEFINE.



