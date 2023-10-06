* Encoding: UTF-8.
DEFINE price_control(year_base=!tokens(1)
                     /year=!tokens(1)
                     /quarter=!tokens(1)
                     /flow=!tokens(1)
                     /outlier_time_limit_upper=!tokens(1)
                     /outlier_time_limit_lower=!tokens(1)
                     )

DATASET CLOSE all.

GET FILE=!quote(!concat('data/',!flow,'_',!year,'Q',!quarter,'.sav')).

COMPUTE qrt = 0.
EXECUTE.

* Delete outliers.  
SELECT IF (outlier = 0).
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

<<<<<<< Updated upstream
* Add no of transactions.
AGGREGATE
  /OUTFILE=* MODE=ADDVARIABLES
  /BREAK=flow comno quarter 
  /no_trans=N()
.
=======
FREQUENCIES transactionHS_under_5.

SELECT IF (transactionHS_under_5 = 0).
EXECUTE.

*REMOVE OUTLIERS TRANSACTION LEVEL WITHIN GROUP AND QUARTER - MAD
*WE DO NOT REMOVE VARIATION STD FROM MEAN DUE TO BE ABLE TO DETECT CHANGE IN COMPOSITON IN COMNO. 

FREQUENCIES Outlier_mad.

SELECT IF (Outlier_mad = 0 OR Outlier_mad = 2).
EXECUTE.



*REMOVE VARIABLES

*DETECT EXTREME PRICE CHANGE FOR TRANSACTIONS WITHIN QUARTER (DEVIATION FROM BASEPRICE)
>>>>>>> Stashed changes

COMPUTE price = value / weight.
COMPUTE price_chg = price / base_price.
FORMATS price_chg (f5.2).
EXECUTE.
DO IF (price / base_price < !outlier_time_limit_lower).
 COMPUTE outlier_time = 1.
ELSE IF (price / base_price > !outlier_time_limit_upper).
 COMPUTE outlier_time = 2.
ELSE.
  COMPUTE outlier_time = 0.
end if.


FREQUENCIES outlier_time.

TEMPORARY.
SELECT IF (any(outlier_time,1,2)).
list all. 

SELECT IF (outlier_time = 0).
EXECUTE.
<<<<<<< Updated upstream
DELETE VARIABLES price_chg.
EXECUTE.

save OUTFILE=!quote(!concat('data/tradedata_no_outlier_',!flow,'_',!year,'Q',!quarter,'.sav')).

=======
*DELETE VARIABLES price_chg.
*EXECUTE.


* Perform the AGGREGATE operation for outlier_median_quarter = 0.
AGGREGATE
  /OUTFILE=* MODE=ADDVARIABLES
  /BREAK=flow comno quarter 
  /sd_comno_filter=SD(price)
  /mean_comno_filter=MEAN(price).

* Mark outliers.
COMPUTE ul_filter = mean_comno_filter + (!outlier_limit_upper * sd_comno_filter).
COMPUTE ll_filter = mean_comno_filter - (!outlier_limit_lower * sd_comno_filter).
COMPUTE outlier_filter = 0.
IF (price < ll_filter OR price > ul_filter) outlier_filter = 1.


*STD FROM MEAN IN READ QUARTER - CHECK AGAINST OUTLIER_MAD --> SHOULD NOT BE MANY CASES LEFT
FREQUENCIES outlier.


*RUN TEST ON STANDARD DEVIATION AND REMOVE OUTLIERS
SELECT IF (outlier_filter = 0).
EXECUTE.


* SECOND REMOVAL OF OUTLIERS USING STANDARD DEVIATION AFTER REMOVAL OF EXTREMES AND ERROR - BOUNDRIES SHOULD BE BETTER (INCLUDE?)
FREQUENCIES outlier_filter.
*MEANS TABLES=value BY outlier_filter
 * /CELLS=MEAN COUNT STDDEV SUM.

FREQUENCIES transactionHS_under_5.


* Add no of transactions after removal.
AGGREGATE
  /OUTFILE=* MODE=ADDVARIABLES
  /BREAK=flow comno quarter 
  /no_trans_after_rm=N()
.


save OUTFILE=!quote(!concat('data/tradedata_no_outlier_',!flow,'_',!year,'Q',!quarter,'.sav')).

DELETE VARIABLES 
flow
ItemID
country
unit
valUSD
itemno
exporterNUIT
N_price
transactionHS_under_5
price_median_quarter
deviation_median
MAD
modified_Z
Outlier_mad
sd_comno
mean_comno
ul
ll
outlier
qrt
outlier_time
sd_comno_filter
mean_comno_filter
ul_filter
ll_filter
outlier_filter
no_trans_after_rm
.
EXECUTE.

save OUTFILE=!quote(!concat('data/pricedata_no_outlier_',!flow,'_',!year,'Q',!quarter,'.sav')).

>>>>>>> Stashed changes
!ENDDEFINE.
