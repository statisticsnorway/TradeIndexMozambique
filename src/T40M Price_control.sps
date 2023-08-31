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

* Add no of transactions.
AGGREGATE
  /OUTFILE=* MODE=ADDVARIABLES
  /BREAK=flow comno quarter 
  /no_trans=N()
.

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
DELETE VARIABLES price_chg.
EXECUTE.

save OUTFILE=!quote(!concat('data/tradedata_no_outlier_',!flow,'_',!year,'Q',!quarter,'.sav')).

!ENDDEFINE.
