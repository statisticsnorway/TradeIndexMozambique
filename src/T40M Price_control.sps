﻿* Encoding: UTF-8.
DEFINE price_control(year_base=!tokens(1)
                     /year=!tokens(1)
                     /quarter=!tokens(1)
                     /flow=!tokens(1)
                     /outlier_time_limit_upper=!tokens(1)
                     /outlier_time_limit_lower=!tokens(1)
                     /outlier_sd_limit_upper=!tokens(1)
                     /outlier_sd_limit_lower=!tokens(1)
                     )

DATASET CLOSE all.

GET FILE=!quote(!concat('data/',!flow,'_',!year,'Q',!quarter,'.sav')).

COMPUTE qrt = 0.
EXECUTE.


MATCH FILES file=*
           /table=!quote(!concat('Data/base_price_',!flow,'_',!year_base,'.sav'))
           /in=from_wgt
           /by flow comno
           /drop impute_base
           .

EXECUTE.

FREQUENCIES from_wgt.
SELECT IF (from_wgt = 1).
EXECUTE.
DELETE VARIABLES from_wgt.
EXECUTE.

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
  /VLABELS VARIABLES=outlier_dev_median_quarter value price DISPLAY=LABEL
  /TABLE outlier_dev_median_quarter BY value [COUNT F40.0, SUM, COLPCT.SUM PCT40.1] + price [MEAN, STDDEV]
  /CATEGORIES VARIABLES=outlier_dev_median_quarter ORDER=A KEY=VALUE EMPTY=EXCLUDE TOTAL=YES POSITION=BEFORE
  /TITLES
    TITLE='Outliers on standard deviation.'.

* Find the sum of each comno.
AGGREGATE
  /OUTFILE=* MODE=ADDVARIABLES
  /BREAK=flow year quarter comno outlier_dev_median_quarter 
  /comno_sum=SUM(value)
.

sort cases by flow year quarter comno outlier_dev_median_quarter  .

match files file=*
    /by flow year quarter comno outlier_dev_median_quarter
    /last = l_comno.
.

sort cases by  flow (A) year (A) quarter (A) outlier_dev_median_quarter(D) comno_sum (D) comno (A) l_comno (D).

* number the comno by sum.
DO IF ($casenum = 1).
 COMPUTE  comno_counter=1.
ELSE IF (l_comno = 1).
 COMPUTE  comno_counter=comno_counter+1.
END IF.
LEAVE comno_counter.
EXECUTE.

sort cases by flow year quarter comno.

TEMPORARY.
SELECT IF (comno_counter < 11 and l_comno = 1).
SAVE OUTFILE='temp/largest_outliers.sav' /KEEP flow year quarter comno.

MATCH FILES file=*
           /table='temp/largest_outliers.sav'
           /in=largest
           /by flow year quarter comno
           .

* table of the 10 largest values for outliers.
TEMPORARY .
SELECT IF (largest = 1).
CTABLES
  /FORMAT MAXCOLWIDTH=128
  /VLABELS VARIABLES=comno outlier_dev_median_quarter value price DISPLAY=NONE
  /VLABELS VARIABLES=value price DISPLAY=LABEL
  /TABLE comno > outlier_dev_median_quarter BY value [COUNT F40.0, SUM, COLPCT.SUM PCT40.1] + price [MEAN F40.1, STDDEV F40.1]
  /CATEGORIES VARIABLES=comno ORDER=A KEY=VALUE EMPTY=EXCLUDE TOTAL=YES POSITION=BEFORE LABEL='Grand total'
  /CATEGORIES VARIABLES=outlier_dev_median_quarter ORDER=A KEY=VALUE EMPTY=EXCLUDE TOTAL=YES POSITION=BEFORE
  /TITLES
    TITLE='Outlier share for 10 largest commodities based on outlier values'.

DELETE VARIABLES comno_counter l_comno comno_sum outlier_dev_median_quarter. 


*REMOVE OUTLIERS TRANSACTION LEVEL WITHIN GROUP AND QUARTER - MAD.

FREQUENCIES outlier_dev_median_q.

SELECT IF (outlier_dev_median_q = 0 OR outlier_dev_median_q = 2).
EXECUTE.
TITLE 'Number of cases after removal of outliers for median quarter'.
FREQUENCIES flow.

*DETECT EXTREME PRICE CHANGE FOR TRANSACTIONS WITHIN QUARTER (DEVIATION FROM BASEPRICE).

COMPUTE price = value / uv_weight.
COMPUTE price_chg = price / base_price.
FORMATS price_chg (f5.2).
EXECUTE.
DO IF (price_chg < !outlier_time_limit_lower).
 COMPUTE outlier_time = 1.
ELSE IF (price_chg > !outlier_time_limit_upper).
 COMPUTE outlier_time = 2.
ELSE.
  COMPUTE outlier_time = 0.
end if.

FREQUENCIES outlier_time.

SELECT IF (outlier_time = 0).
EXECUTE.
TITLE 'No of cases after outlier removal for price change from base price'.
FREQUENCIES flow.


* Perform the AGGREGATE operation for outlier_median_quarter = 0.
AGGREGATE
  /OUTFILE=* MODE=ADDVARIABLES
  /BREAK=flow comno quarter 
  /sd_comno_q=SD(price)
  /mean_comno_q=MEAN(price).

* Mark outlier_sd_q.
COMPUTE ul_sd = mean_comno_q + (!outlier_sd_limit_upper * sd_comno_q).
COMPUTE ll_sd = mean_comno_q - (!outlier_sd_limit_lower * sd_comno_q).
COMPUTE outlier_sd_q = 0.
IF (price < ll_sd OR price > ul_sd) outlier_sd_q = 1.
EXECUTE.

FREQUENCIES outlier_sd_q.

*REMOVE OUTLIERS based on STANDARD DEVIATION.

SELECT IF (outlier_sd_q = 0).
EXECUTE.
TITLE 'Number of cases after removal of outliers for standard deviation'.
FREQUENCIES flow.

*Remove comnos with only one transaction for current quarter.
SELECT IF (N_transactions > 1).
EXECUTE.


* Add no of transactions after removal.
AGGREGATE
  /OUTFILE=* MODE=ADDVARIABLES
  /BREAK=flow comno quarter 
  /no_trans_after_rm=N()
.

FREQUENCIES flow.


save OUTFILE=!quote(!concat('data/tradedata_no_outlier_',!flow,'_',!year,'Q',!quarter,'.sav')).

DELETE VARIABLES 
flow
ItemID
country
unit
valUSD
itemno
exporterNUIT
sitc2
sitc1
chapter
section
N_transactions
price_median_quarter
deviation_from_median
MAD
modified_Z
outlier_dev_median_q
sd_comno
mean_comno
ul
ll
outlier_sd
qrt
outlier_time
sd_comno_q
mean_comno_q
ul_sd
ll_sd
outlier_sd_q
no_trans_after_rm
.
EXECUTE.

save OUTFILE=!quote(!concat('data/pricedata_no_outlier_',!flow,'_',!year,'Q',!quarter,'.sav')).

!ENDDEFINE.

