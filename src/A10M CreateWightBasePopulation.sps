* Encoding: UTF-8.

DEFINE create_weight_base_population(year_1=!tokens(1),
                                    /outlier_limit=!tokens(1) 
                                    )

EXECUTE.
 GET FILE=!quote(!concat('data/Export_',!year_1,'Q1.sav')).
 !DO !q = 2 !TO 4
  ADD FILES file=*
           /file=!quote(!concat('data/Export_',!year_1,'Q',!q,'.sav')).
 !DOEND 


COMPUTE price = value / weight.
execute.

AGGREGATE
  /OUTFILE=* MODE=ADDVARIABLES
  /BREAK=flow comno 
  /sd_comno=SD(price)
  /mean_comno=MEAN(price)
.

* Delete outliers.
compute ul = mean_comno + (!outlier_limit * sd_comno).
compute ll = mean_comno - (!outlier_limit * sd_comno).
EXECUTE.
COMPUTE outlier = 0.
if (price < ll or price > ul) outlier=1.
EXECUTE.

FREQUENCIES outlier.
MEANS TABLES=valusd BY outlier
  /CELLS=MEAN COUNT STDDEV SUM.

SELECT IF (outlier = 0).
EXECUTE.

*delete variables ul ll outlier mean_comno sd_comno.
* Add totals for different levels for the value for all cases.
AGGREGATE
  /OUTFILE=* MODE=ADDVARIABLES
  /BREAK=flow
  /T_sum=SUM(value)
.

AGGREGATE
  /OUTFILE=* MODE=ADDVARIABLES
  /BREAK=flow comno
  /no_of_months=N
  /price_max=MAX(price) 
  /price_min=MIN(price) 
  /price_median=MEDIAN(price) 
  /price_sd=SD(price)
  /price_mean=MEAN(price)
  /HS_sum=SUM(value)
  .

COMPUTE price_cv = price_sd / price_mean.
FORMATS price_cv (f8.2).

EXECUTE.
DELETE VARIABLES price_mean price_sd.

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

VARIABLE LABELS
 S_sum 'Total Section sum'
/C_sum 'Total Chapter sum'    
/S1_sum 'Total Sitc1 sum'
/S2_sum 'Total Sitc2 sum'
.

SORT CASES by flow comno.
* Save for previous year.
SAVE OUTFILE=!quote(!concat('data/weight_base_population_',!year_1,'.sav')).
 
!ENDDEFINE.