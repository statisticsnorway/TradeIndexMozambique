* Encoding: UTF-8.


DEFINE create_weight_base(year_1=!tokens(1)
                         /share_total=!tokens(1)
                         /no_of_months=!tokens(1)
                         /no_of_months_seasons=!tokens(1)
                         /section_seasons=!tokens(1)
                         /price_cv=!tokens(1)
                         /max_by_min=!tokens(1)
                         /max_by_median=!tokens(1)
                         /median_by_min=!tokens(1)
                         /share_small=!tokens(1)
                         )

DATASET CLOSE all.
* Read data for previous year.
GET FILE=!quote(!concat('Data/weight_base_population_',!year_1,'.sav')).

* Will exclude values which are more than x% of export or import for check againt total.
* If a commodity has x% or more- of the import or export it shall not be included in the sum we check against.

COMPUTE share_total = HS_sum / T_sum.
EXECUTE.
formats share_total (f8.4) T_sum (f18.0) HS_sum (f18.0).
TEMPORARY.
SELECT IF (share_total) >= !share_total.
list comno flow month value T_sum HS_sum share_total.

* Create total for flow for 'small' commodities and add them to the dataset.
SELECT IF (share_total <= !share_total).
DATASET DECLARE valsum_ex_big.
AGGREGATE
  /OUTFILE='valsum_ex_big' 
  /BREAK=flow
  /T_sum_small=SUM(value)
.

* Data for previous year.
MATCH FILES file=!quote(!concat('data/weight_base_population_',!year_1,'.sav'))
                      /TABLE='valsum_ex_big'
                      /by flow.
EXECUTE.
DATASET CLOSE valsum_ex_big.

* Select only the data for year (by selecting the first commodity line for each commodity).
MATCH FILES file=*
           /by flow comno
           /FIRST=f.
EXECUTE.
SELECT IF (f = 1).
EXECUTE.
DELETE VARIABLES f month value weight price.

compute share_small = HS_sum / T_sum_small .
formats share_small (f8.5).
EXECUTE.

FREQUENCIES flow.

COMPUTE max_by_min = price_max / price_min.
COMPUTE max_by_median = price_max / price_median.
COMPUTE median_by_min = price_median / price_min.
EXECUTE.
FORMATS max_by_min max_by_median median_by_min (f8.4).

* The section_season macro variable does not work with more than one section!.
SELECT IF (no_of_months >= !no_of_months or (any(section,!section_seasons) and no_of_months >= !no_of_months_seasons)).
TITLE !CONCAT('After selection of no of months at least ',!no_of_months).
FREQUENCIES flow.
CTABLES
  /VLABELS VARIABLES=chapter no_of_months DISPLAY=LABEL
  /TABLE section [COUNT F40.0] BY no_of_months [C]
  /CATEGORIES VARIABLES=section ORDER=A KEY=VALUE EMPTY=EXCLUDE TOTAL=YES POSITION=AFTER
  /CATEGORIES VARIABLES=no_of_months ORDER=A KEY=VALUE EMPTY=EXCLUDE TOTAL=YES POSITION=AFTER
  /CRITERIA CILEVEL=95.

SELECT IF (price_cv < !price_cv).
TITLE !CONCAT('After selection of price co-variance less than ',!price_cv).
FREQUENCIES flow .

SELECT IF (max_by_min < !max_by_min).
TITLE !CONCAT('After selection of price max-by-min less than ',!max_by_min).
FREQUENCIES flow .

SELECT IF (max_by_median < !max_by_median).
TITLE !CONCAT('After selection of price max-by-median less than ',!max_by_median).
FREQUENCIES flow .

SELECT IF (median_by_min < !median_by_min).
TITLE !CONCAT('After selection of price median-by-min less than ',!median_by_min).
FREQUENCIES flow .

SELECT IF (share_small > !share_small).
TITLE !CONCAT('After selection of share of small more than ',!share_small).
FREQUENCIES flow.

SORT CASES by flow section.
SAVE OUTFILE='temp\sample.sav'.


* Check the coverage by section and total.
AGGREGATE
  /OUTFILE=* 
  /BREAK=year flow section  
  /Ssample_sum=SUM(HS_sum)
  /Spop_sum=MEAN(S_sum)
  /Sno_of_comm = N
  .

AGGREGATE
  /OUTFILE=* MODE=ADDVARIABLES 
  /BREAK=year flow 
  /Tsample_sum=SUM(Ssample_sum)
  /Tpop_sum=SUM(Spop_sum)
  /Tno_of_comm = SUM(Sno_of_comm)
  .

compute Scoverage = Ssample_sum * 100 / spop_sum.
compute Tcoverage = Tsample_sum * 100 / Tpop_sum.
EXECUTE.
    

list all.
SAVE OUTFILE=!quote(!concat('data/coverage_section_',!year_1,'.sav')).


* Check the coverage by sitc1 and total.
DATASET CLOSE all.
GET file='temp\sample.sav'.

AGGREGATE
  /OUTFILE=* 
  /BREAK=year flow sitc1  
  /Ssample_sum=SUM(HS_sum)
  /Spop_sum=MEAN(S1_sum)
  /Sno_of_comm = N
  .

AGGREGATE
  /OUTFILE=* MODE=ADDVARIABLES 
  /BREAK=year flow 
  /Tsample_sum=SUM(Ssample_sum)
  /Tpop_sum=SUM(Spop_sum)
  /Tno_of_comm = SUM(Sno_of_comm)
  .

compute Scoverage = Ssample_sum * 100 / spop_sum.
compute Tcoverage = Tsample_sum * 100 / Tpop_sum.
EXECUTE.
    
list all.
SAVE OUTFILE=!quote(!concat('data/coverage_sitc1_',!year_1,'.sav')).

* Check the coverage by sitc2 and total.
DATASET CLOSE all.
GET file='temp\sample.sav'.

AGGREGATE
  /OUTFILE=* 
  /BREAK=year flow sitc2  
  /Ssample_sum=SUM(HS_sum)
  /Spop_sum=MEAN(S1_sum)
  /Sno_of_comm = N
  .

AGGREGATE
  /OUTFILE=* MODE=ADDVARIABLES 
  /BREAK=year flow 
  /Tsample_sum=SUM(Ssample_sum)
  /Tpop_sum=SUM(Spop_sum)
  /Tno_of_comm = SUM(Sno_of_comm)
  .

compute Scoverage = Ssample_sum * 100 / spop_sum.
compute Tcoverage = Tsample_sum * 100 / Tpop_sum.
EXECUTE.
    
list all.
SAVE OUTFILE=!quote(!concat('data/coverage_sitc2_',!year_1,'.sav')).


* Select only the data for year by section (by selecting the first section line for each section).
MATCH FILES file='temp\sample.sav'
           /by flow section
           /FIRST=f.
EXECUTE.
SELECT IF (f = 1).
EXECUTE.
DELETE VARIABLES f.

AGGREGATE
  /OUTFILE=* MODE=ADDVARIABLES
  /BREAK=flow  
  /Tsample_sum=SUM(S_sum)
  .

COMPUTE Weight_S = T_sum * S_sum / Tsample_sum.
EXECUTE.

* Add a variable to check the calculation of weights.
AGGREGATE
  /OUTFILE=* MODE=ADDVARIABLES
  /BREAK=flow  
  /Check_Weight_S_sum=SUM(Weight_S)
.

* check to see that the weights are correctly calculated.
*TEMPORARY.
*SELECT IF (T_sum ne Check_Weight_S_sum).
*list flow comno T_sum Check_Weight_S_sum.

DELETE VARIABLES 
Year
comno
chapter
quarter T_sum
no_of_months
price_max
price_min
price_cv
HS_sum
S_sum
S1_sum
S2_sum
C_sum
T_sum_small
share_small
max_by_min
max_by_median
median_by_min
Tsample_sum
Check_Weight_S_sum
.
EXECUTE.

MATCH FILES file='temp\sample.sav'
           /TABLE=*
           /BY flow section
           .
EXECUTE.

SORT CASES BY flow chapter.
SAVE OUTFILE='temp\sample.sav'.

* Select only the data for year by chapter (by selecting the first section line for each chapter).
MATCH FILES file=*
           /by flow chapter
           /FIRST=f.
EXECUTE.
SELECT IF (f = 1).
EXECUTE.
DELETE VARIABLES f.

* Add sample totals.
AGGREGATE
  /OUTFILE=* MODE=ADDVARIABLES
  /BREAK=flow section 
  /Ssample_sum=SUM(C_sum)
.
COMPUTE Weight_C = Weight_S * C_sum / Ssample_sum.
EXECUTE.

* Add a variable to check the calculation of weights.
AGGREGATE
  /OUTFILE=* MODE=ADDVARIABLES
  /BREAK=flow  
  /Check_Weight_C_sum=SUM(Weight_C)
.

* check to see that the weights are correctly calculated.
*TEMPORARY.
*SELECT IF (T_sum ne Check_Weight_C_sum).
*list flow comno T_sum Check_Weight_C_sum.

DELETE VARIABLES 
Year
comno
section
quarter T_sum
no_of_months
price_max
price_min
price_cv
HS_sum
S_sum
S1_sum
S2_sum
C_sum
T_sum_small
share_small
max_by_min
max_by_median
median_by_min
Ssample_sum
Weight_S
Check_Weight_C_sum
.
EXECUTE.

MATCH FILES file='temp\sample.sav'
           /TABLE=*
           /BY flow chapter
           .
EXECUTE.


AGGREGATE
  /OUTFILE=* MODE=ADDVARIABLES
  /BREAK=flow chapter 
  /Csample_sum=SUM(HS_sum)
.

*COMPUTE Weight_Sx = T_sum * S_sum .
COMPUTE Weight_HS = Weight_C * HS_sum / Csample_sum.
EXECUTE.

* Add a variable to check the calculation of weights.
AGGREGATE
  /OUTFILE=* MODE=ADDVARIABLES
  /BREAK=flow  
  /Check_Weight_HS_sum=SUM(Weight_HS)
.

* check to see that the weights are correctly calculated.
*TEMPORARY.
*SELECT IF (T_sum ne Check_Weight_HS_sum).
*list flow comno T_sum Check_Weight_HS_sum.


SORT CASES by flow comno .
DELETE VARIABLES T_sum to price_min HS_sum to median_by_min Check_Weight_HS_sum Csample_sum.

compute weight_year = year.

EXECUTE.
* Save for previous year.

SAVE OUTFILE=!quote(!concat('data/weight_base_',!year_1,'.sav')).
 
!ENDDEFINE.

