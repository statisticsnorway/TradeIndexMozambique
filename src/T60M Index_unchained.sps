* Encoding: UTF-8.

DEFINE indices_unchained(year_base=!tokens(1)
                        /year=!tokens(1)
                        /quarter=!tokens(1)
                        /flow=!tokens(1)
                        )


DATASET CLOSE all.
* Actual year and quarter.
GET FILE=!quote(!concat('Data/price_impute_',!flow,'_',!year,'Q',!quarter,'.sav')).

* base prices from previous year.
MATCH FILES FILE=*
           /IN=from_impute
           /FILE=!quote(!concat('Data/base_price_',!flow,'_',!year_base,'.sav'))
           /BY flow comno 
           .
EXECUTE.
FREQUENCIES from_impute.

SELECT IF (from_impute = 1).
EXECUTE.
DELETE VARIABLES from_impute.
EXECUTE.

COMPUTE index_unchained = price / base_price * 100.
COMPUTE index_weight = index_unchained * Weight_HS.

STRING level (A60) series (A60).
COMPUTE level = 'Commodity'.
COMPUTE series = comno.
EXECUTE.

* add special series information.
MATCH FILES FILE=*
           /TABLE='Data/Special_series.sav'
           /IN=special
           /BY flow comno 
           .
EXECUTE.
FREQUENCIES special group.

SAVE OUTFILE='data/index_commodity.sav'.
          
AGGREGATE /OUTFILE=*
          /BREAK=flow section Year quarter
          /weight_hs = SUM(Weight_HS)
          /index_weight = SUM(index_weight)
          .
EXECUTE.

COMPUTE index_unchained = index_weight / weight_hs .
STRING level (A60) series (A60).
COMPUTE series = section.
COMPUTE level = 'Section'.
EXECUTE.


SAVE OUTFILE='data/index_section.sav'.

DATASET CLOSE all.
GET FILE='data/index_commodity.sav'.

AGGREGATE /OUTFILE=*
          /BREAK=flow Year quarter
          /weight_hs = SUM(Weight_HS)
          /index_weight = SUM(index_weight)
          .
EXECUTE.

COMPUTE index_unchained = index_weight / weight_hs .

STRING level (A60) series (A60).
COMPUTE series = flow.
COMPUTE level = 'Total'.
EXECUTE.

SAVE OUTFILE='data/index_total.sav'. 

DATASET CLOSE all.
GET FILE='data/index_commodity.sav'.

AGGREGATE /OUTFILE=*
          /BREAK=flow sitc1 Year quarter
          /weight_hs = SUM(Weight_HS)
          /index_weight = SUM(index_weight)
          .
EXECUTE.

COMPUTE index_unchained = index_weight / weight_hs .

STRING level (A60) series (A60).
COMPUTE level = 'Sitc 1'.
COMPUTE series = sitc1.
EXECUTE.

SAVE OUTFILE='data/index_sitc1.sav'. 

DATASET CLOSE all.
GET FILE='data/index_commodity.sav'.

AGGREGATE /OUTFILE=*
          /BREAK=flow sitc2 Year quarter
          /weight_hs = SUM(Weight_HS)
          /index_weight = SUM(index_weight)
          .
EXECUTE.

COMPUTE index_unchained = index_weight / weight_hs .

STRING level (A60) series (A60).
COMPUTE level = 'Sitc 2'.
COMPUTE series = sitc2.
EXECUTE.

SAVE OUTFILE='data/index_sitc2.sav'. 

* Export/import without the special series.
DATASET CLOSE all.
GET FILE='data/index_commodity.sav'.
SELECT IF (special = 0).
EXECUTE.

AGGREGATE /OUTFILE=*
          /BREAK=flow Year quarter
          /weight_hs = SUM(Weight_HS)
          /index_weight = SUM(index_weight)
          .
EXECUTE.

COMPUTE index_unchained = index_weight / weight_hs .

STRING level (A60) series (A60).

!IF (!flow = 'Export') !THEN
 COMPUTE level = 'Total export without Electricity, mineral coal and aluminium'.
 COMPUTE series = 'Total export without Electricity, mineral coal and aluminium'.
!ELSE 
 COMPUTE level = 'Total import without Fuel and electricity'.
 COMPUTE series = 'Total import without Fuel and electricity'.
!IFEND
EXECUTE.

SAVE OUTFILE='data/index_total_no_special.sav'. 

DATASET CLOSE all.
GET FILE='data/index_commodity.sav'.

AGGREGATE /OUTFILE=*
          /BREAK=flow group Year quarter
          /weight_hs = SUM(Weight_HS)
          /index_weight = SUM(index_weight)
          .
EXECUTE.

COMPUTE index_unchained = index_weight / weight_hs .

STRING level (A60) series (A60).
COMPUTE level = 'Special commodities'.
COMPUTE series = group.

IF (group = '' & flow = 'E') series = 'Total export without Electricity, mineral coal and aluminium'.
IF (group = '' & flow = 'I') series = 'Total import without Fuel and electricity'.

EXECUTE.
delete variables group.
EXECUTE.

SAVE OUTFILE='data/index_special.sav'. 

ADD FILES file=*
         /file='data/index_total.sav'
         /file='data/index_commodity.sav'
         /file='data/index_section.sav'
         /file='data/index_sitc1.sav'
         /file='data/index_sitc2.sav'
         .
EXECUTE.
string time (a6) .
compute time = concat(string(year,f4),'Q',string(quarter,f1)).
EXECUTE.


DELETE VARIABLES 
index_weight
comno
price
chapter
section
Weight_S
Weight_C
weight_year
price_rel
product
Weight_section
prod_sum
weight_price_rel
base_price
.
EXECUTE.

* Choose actual year.
ADD FILES FILE=!quote(!concat('Data/index_unchained_',!flow,'_',!year,'.sav'))
         /FILE=*
         .
EXECUTE.

* Check to see if the index for the quarter is already made, if so we keep the latest version.
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

do if (lag(series) = series).
 compute index_unchained_change = (index_unchained / lag(index_unchained) - 1) * 100.
else. 
 compute index_unchained_change = ((index_unchained / 100) -1) * 100.
END IF.

EXECUTE.
format index_unchained_change (f8.2).
COMPUTE weight_hs_total = weight_hs.

TEMPORARY.
SELECT IF (level = 'Total').
SAVE OUTFILE='temp/index_unchained_total.sav' 
    /keep=time weight_hs_total.

DELETE VARIABLES weight_hs_total.
EXECUTE.
SORT CASES by time.
MATCH FILES file=*
           /table='temp/index_unchained_total.sav'
           /by time
           .

COMPUTE share_of_total_base_value = weight_hs / weight_hs_total * 100.
EXECUTE.
format index_unchained_change share_of_total_base_value (f8.2).
DELETE VARIABLES weight_hs_total.
EXECUTE.
SORT CASES BY flow level series year quarter.
VARIABLE LABELS 
    share_of_total_base_value 'Share of total base value'.

CTABLES
  /VLABELS VARIABLES=flow level series time index_unchained DISPLAY=NONE
  /VLABELS VARIABLES=share_of_total_base_value DISPLAY=LABEL
  /TABLE flow > level > series BY time > index_unchained [MEAN] + share_of_total_base_value [mean] 
  /SLABELS VISIBLE=NO
  /CATEGORIES VARIABLES=flow level series time ORDER=A KEY=VALUE EMPTY=EXCLUDE
  /TITLES
    TITLE='Unchained index.'.


*ADD LIST OF INDEXSERIES WITH INDEXCHANGE LARGER THAN X PER CENT

SAVE outfile=!quote(!concat('Data/index_unchained_',!flow,'_',!year,'.sav'))
 /KEEP= year quarter time flow level series index_unchained weight_hs.
!ENDDEFINE.




