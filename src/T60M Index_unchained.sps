* Encoding: UTF-8.

DEFINE indices_unchained(year_base=!tokens(1)
                        /year=!tokens(1)
                        /quarter=!tokens(1)
                        )


DATASET CLOSE all.
* Actual year and quarter.
GET FILE=!quote(!concat('Data/price_impute_',!year,'Q',!quarter,'.sav')).

* base prices from previous year.
MATCH FILES FILE=*
           /IN=from_impute
           /FILE=!quote(!concat('Data/base_price_',!year_base,'.sav'))
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

STRING level (A30) series (a25).
COMPUTE level = 'Commodity'.
COMPUTE series = comno.
EXECUTE.


SAVE OUTFILE='data/index_commodity.sav'.
          
AGGREGATE /OUTFILE=*
          /BREAK=flow section Year quarter
          /weight_hs = SUM(Weight_HS)
          /index_weight = SUM(index_weight)
          .
EXECUTE.

COMPUTE index_unchained = index_weight / weight_hs .
STRING level (A30) series (a25).
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

STRING level (A30) series (a25).
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

STRING level (A30) series (a25).
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

STRING level (A30) series (a25).
COMPUTE level = 'Sitc 2'.
COMPUTE series = sitc2.
EXECUTE.

SAVE OUTFILE='data/index_sitc2.sav'. 

* Export without gas.
DATASET CLOSE all.
GET FILE='data/index_commodity.sav'.
SELECT IF (flow = 'E' and char.substr(comno,1,4) NE '2716').
EXECUTE.

AGGREGATE /OUTFILE=*
          /BREAK=flow Year quarter
          /weight_hs = SUM(Weight_HS)
          /index_weight = SUM(index_weight)
          .
EXECUTE.

COMPUTE index_unchained = index_weight / weight_hs .

STRING level (A30) series (a25).
COMPUTE level = 'Total export without Gas'.
COMPUTE series = 'Total export without Gas'.
EXECUTE.

SAVE OUTFILE='data/index_total_no_gas.sav'. 

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
weight_hs
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
ADD FILES FILE=!quote(!concat('Data/index_unchained_',!year,'.sav'))
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

CTABLES
  /VLABELS VARIABLES=flow level series time index_unchained DISPLAY=NONE
  /TABLE flow > level > series BY time > index_unchained [MEAN]
  /SLABELS VISIBLE=NO
  /CATEGORIES VARIABLES=flow level series time ORDER=A KEY=VALUE EMPTY=EXCLUDE
  /CRITERIA CILEVEL=95
  /TITLES
    TITLE='Unchained index.'.

SAVE outfile=!quote(!concat('Data/index_unchained_',!year,'.sav')).
!ENDDEFINE.

