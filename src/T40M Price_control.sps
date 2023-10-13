* Encoding: UTF-8.
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

FREQUENCIES transactionHS_under_limit.

SELECT IF (transactionHS_under_limit = 0).
EXECUTE.

*REMOVE OUTLIERS TRANSACTION LEVEL WITHIN GROUP AND QUARTER - MAD
*WE DO NOT REMOVE VARIATION STD FROM MEAN DUE TO BE ABLE TO DETECT CHANGE IN COMPOSITON IN COMNO. 

FREQUENCIES outlier_dev_median_q.

SELECT IF (outlier_dev_median_q = 0 OR outlier_dev_median_q = 2).
EXECUTE.



*REMOVE VARIABLES

*DETECT EXTREME PRICE CHANGE FOR TRANSACTIONS WITHIN QUARTER (DEVIATION FROM BASEPRICE)

COMPUTE price = value / uv_weight.
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


SELECT IF (outlier_time = 0).
EXECUTE.
*DELETE VARIABLES price_chg.
*EXECUTE.


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

*REMOVE OUTLIERS based on STANDARD DEVIATION

SELECT IF (outlier_sd_q = 0).
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
N_price
transactionHS_under_limit
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
