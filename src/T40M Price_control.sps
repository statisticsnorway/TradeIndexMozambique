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
   

CTABLES
  /FORMAT MAXCOLWIDTH=128
  /VLABELS VARIABLES=outlier_sd value price DISPLAY=LABEL
  /TABLE outlier_sd BY value [COUNT F40.0, SUM, COLPCT.SUM PCT40.1] + price [MEAN, STDDEV]
  /CATEGORIES VARIABLES=outlier_sd ORDER=A KEY=VALUE EMPTY=EXCLUDE TOTAL=YES POSITION=BEFORE
  /TITLES
    TITLE='Outliers on standard deviation.'.

* Find the sum of each comno.
AGGREGATE
  /OUTFILE=* MODE=ADDVARIABLES
  /BREAK=flow year quarter comno outlier_sd 
  /comno_sum=SUM(value)
.

sort cases by flow year quarter comno outlier_sd  .

match files file=*
    /by flow year quarter comno outlier_sd
    /last = l_comno.
.

sort cases by  flow (A) year (A) quarter (A) outlier_sd(D) comno_sum (D) comno (A) l_comno (D).

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
  /VLABELS VARIABLES=comno outlier_sd value price DISPLAY=NONE
  /VLABELS VARIABLES=value price DISPLAY=LABEL
  /TABLE comno > outlier_sd BY value [COUNT F40.0, SUM, COLPCT.SUM PCT40.1] + price [MEAN F40.1, STDDEV F40.1]
  /CATEGORIES VARIABLES=comno ORDER=A KEY=VALUE EMPTY=EXCLUDE TOTAL=YES POSITION=BEFORE LABEL='Grand total'
  /CATEGORIES VARIABLES=outlier_sd ORDER=A KEY=VALUE EMPTY=EXCLUDE TOTAL=YES POSITION=BEFORE
  /TITLES
    TITLE='Outlier share for 10 largest commodities based on outlier values'.

DELETE VARIABLES comno_counter l_comno comno_sum . 



*REMOVE OUTLIERS based on STANDARD DEVIATION.

SELECT IF (outlier_sd = 0).
EXECUTE.
TITLE 'Number of cases after removal of outliers for standard deviation'.
FREQUENCIES flow.



*Remove comnos with only one transaction for current quarter.
SELECT IF (N_transactions > 1).
EXECUTE.


* Add no of transactions after removal.
AGGREGATE
  /OUTFILE=* MODE=ADDVARIABLES
  /BREAK=year flow comno quarter 
  /no_trans_after_rm=N()
.

FREQUENCIES flow.

*AGGREGATE TO MONTHLY PRICES.


AGGREGATE /OUTFILE=*
          /BREAK=year flow comno quarter month
          /value_month = SUM(value)
          /uv_weight_month = SUM(uv_weight)
          /base_price = MEAN(base_price)
          .


*DETECT EXTREME PRICE CHANGE FOR TRANSACTIONS WITHIN QUARTER (DEVIATION FROM BASEPRICE).

COMPUTE price = value_month / uv_weight_month.
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



save OUTFILE=!quote(!concat('data/tradedata_no_outlier_',!flow,'_',!year,'Q',!quarter,'.sav')).

DELETE VARIABLES 
flow
outlier_time
.
EXECUTE.

save OUTFILE=!quote(!concat('data/pricedata_no_outlier_',!flow,'_',!year,'Q',!quarter,'.sav')).

!ENDDEFINE.

