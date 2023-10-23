* Encoding: UTF-8.

DEFINE create_weight_base_population(year_1=!tokens(1) 
                                    /flow=!tokens(1)
                                    )
                                    
DATASET CLOSE all.
GET FILE=!quote(!concat('data/',!flow,'_',!year_1,'Q1.sav')).
 !DO !q = 2 !TO 4
  ADD FILES file=*
           /file=!quote(!concat('data/',!flow,'_',!year_1,'Q',!q,'.sav')).
 !DOEND 

* Add totals for different levels for the value for all cases.
AGGREGATE
  /OUTFILE=* MODE=ADDVARIABLES
  /BREAK=flow
  /T_sum=SUM(value)
.

AGGREGATE
  /OUTFILE=* MODE=ADDVARIABLES
  /BREAK=flow section 
  /S_sum=SUM(value)
.

AGGREGATE
  /OUTFILE=* MODE=ADDVARIABLES
  /BREAK=flow chapter 
  /C_sum=SUM(value)
.

AGGREGATE
  /OUTFILE=* MODE=ADDVARIABLES
  /BREAK=flow sitc1 
  /S1_sum=SUM(value)
.

AGGREGATE
  /OUTFILE=* MODE=ADDVARIABLES
  /BREAK=flow sitc2 
  /S2_sum=SUM(value)
.
AGGREGATE
  /OUTFILE=* MODE=ADDVARIABLES
  /BREAK=flow comno
  /HS_sum=SUM(value)
  .

VARIABLE LABELS
 S_sum 'Total Section sum'
/C_sum 'Total Chapter sum'    
/S1_sum 'Total Sitc1 sum'
/S2_sum 'Total Sitc2 sum'
/HS_sum 'Total commodity sum'
/T_sum 'Total sum'
.

*REMOVE OBVIOUS ERRORS BEFORE CALCULATION OF PARAMETERS USED IN VALIDATION PROCESS OF COMNOS USED IN INDEX CALCULATION.
 
*DEVIATION FROM MEAN.
FREQUENCIES outlier_sd.
SELECT IF (outlier_sd = 0).
EXECUTE.


*REMOVE VARIABLES NOT IN USE.

*COUNT NUMBER OF TRANSACTIONS IN BASE YEAR.

AGGREGATE
  /OUTFILE=* MODE=ADDVARIABLES
  /BREAK=flow comno
  /no_of_transactions=N
  .

*CALCULATION PRICE per month:.

AGGREGATE
  /OUTFILE=* 
  /BREAK=year flow comno quarter month 
         section chapter sitc1 sitc2
         T_sum S_sum C_sum S1_sum S2_sum HS_sum no_of_transactions
  /uv_weight=SUM(uv_weight)
  /value=SUM(value)
.

compute price = value / uv_weight.

*CALCULATION OF VARIABLES, AGGREGATES FOR YEAR, USED IN SELECTION PROCESS.

AGGREGATE
  /OUTFILE=* MODE=ADDVARIABLES
  /BREAK=flow comno
  /no_of_months=N
  /price_max=MAX(price) 
  /price_min=MIN(price) 
  /price_median=MEDIAN(price) 
  /price_sd=SD(price)
  /price_mean=MEAN(price)
  .

COMPUTE price_cv = price_sd / price_mean.
FORMATS price_cv (f8.2).

EXECUTE.
DELETE VARIABLES price_mean price_sd.


SORT CASES by flow comno.
* Save for previous year.
SAVE OUTFILE=!quote(!concat('data/weight_base_population_',!flow,'_',!year_1,'.sav')).

TITLE 'Create weight base population finished'. 
 
!ENDDEFINE.
