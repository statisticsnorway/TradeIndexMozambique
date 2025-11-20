* Encoding: UTF-8.

DEFINE base_prices(year_1=!tokens(1)
                  /year=!tokens(1)
                  /flow=!tokens(1)
                  /outlier_median_year_limit_upper=!tokens(1)
                  /outlier_median_year_limit_lower=!tokens(1)
                  )

DATASET CLOSE all.

GET FILE=!quote(!concat('data/',!flow,'_',!year_1,'Q1.sav')).
ADD FILES FILE=*
         /FILE=!quote(!concat('data/',!flow,'_',!year_1,'Q2.sav'))
         /FILE=!quote(!concat('data/',!flow,'_',!year_1,'Q3.sav'))
         /FILE=!quote(!concat('data/',!flow,'_',!year_1,'Q4.sav'))
                     .
 
ALTER TYPE comno (A9).
EXECUTE.
                     
SORT CASES BY flow comno.                   
SAVE OUTFILE=!quote(!concat('data/tradedata_',!flow,'_',!year_1,'.sav')).
* Previous year.
GET FILE=!quote(!concat('Data/weight_base_',!flow,'_',!year_1,'.sav')).
AGGREGATE outfile=*
         /BREAK =flow comno section Weight_HS
         /num=N(flow).
DELETE VARIABLES num.
EXECUTE.

MATCH FILES FILE=!quote(!concat('data/tradedata_',!flow,'_',!year_1,'.sav'))
           /TABLE=*
           /in =From_base
           /by flow comno
           .

FREQUENCIES from_base.

* Previous year.
SELECT IF (from_base = 1 and year = !year_1).
EXECUTE.

COMPUTE price = value / uv_weight.
execute.


CTABLES
  /FORMAT MAXCOLWIDTH=128
  /VLABELS VARIABLES=outlier_sd value price DISPLAY=LABEL
  /TABLE outlier_sd BY value [COUNT F40.0, SUM, COLPCT.SUM PCT40.1] + price [MEAN, STDDEV]
  /CATEGORIES VARIABLES=outlier_sd ORDER=A KEY=VALUE EMPTY=EXCLUDE TOTAL=YES POSITION=BEFORE
  /TITLES
    TITLE='Outliers on standard deviation from mean.'.

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
DO IF ($casenum = 1 or quarter NE lag(quarter)).
 COMPUTE  comno_counter=1.
ELSE IF (l_comno = 1).
 COMPUTE  comno_counter=comno_counter+1.
END IF.
LEAVE comno_counter.
EXECUTE.

sort cases by flow year quarter comno.

TEMPORARY.
SELECT IF (comno_counter < 11 and l_comno = 1 and quarter = 4).
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



SELECT IF (outlier_sd = 0).
EXECUTE.
TITLE 'Number of cases after removal of outliers for standard deviation'.
FREQUENCIES flow.

* Add no of transactions after removal.
AGGREGATE
  /OUTFILE=* MODE=ADDVARIABLES
  /BREAK=flow comno quarter 
  /no_trans_after_rm=N()
.


*AGGREGATE VALUE AND WEIGHT AND CALCULATE PRICE  PER MONTH FOR COMNO-LEVEL.

AGGREGATE /OUTFILE=*
          /BREAK=flow comno section Weight_HS Year quarter month
          /value_month = SUM(value)
          /uv_weight_month = SUM(uv_weight)
          /use_external = FIRST(use_external)
          .

COMPUTE price = value_month / uv_weight_month.
EXECUTE.



*DETECT EXTREME PRICE CHANGE FOR MONTHLY PRICES WITHIN BASEYEAR (DEVIATION FROM MEDIAN PRICE MONTH in YEAR).

AGGREGATE
  /OUTFILE=* MODE=ADDVARIABLES
  /BREAK=flow comno 
  /price_median_year=MEDIAN(price)
  .

IF (SYSMIS(price_median_year)) outlier_median_baseyear = $SYSMIS.
IF (NOT SYSMIS(price_median_year)) price_chg = price / price_median_year.

DO IF (NOT SYSMIS(price_chg)).
   DO IF (price_chg < !outlier_median_year_limit_lower).
     COMPUTE outlier_median_baseyear = 1.
   ELSE IF (price_chg > !outlier_median_year_limit_upper).
     COMPUTE outlier_median_baseyear = 2.
   ELSE.
     COMPUTE outlier_median_baseyear = 0.
   END IF.
END IF.


* Remove outlier tag for external source.
IF (use_external = 1) outlier_median_baseyear = 0.
EXECUTE.

FREQUENCIES outlier_median_baseyear.


*REMOVE EXTREME PRICE CHANGES.
SELECT IF (outlier_median_baseyear = 0).
EXECUTE.


TITLE 'Number of cases after removal of outliers for median'.
FREQUENCIES flow.


save OUTFILE=!quote(!concat('data/tradedata_base_no_outlier_',!flow,'_',!year,'.sav')).

*AGGREGATE VALUE AND WEIGHT AND CALCULATE PRICE FOR COMNO-LEVEL.

AGGREGATE /OUTFILE=*
          /BREAK=flow comno section Weight_HS Year quarter
          /value_quarter = SUM(value_month)
          /weight_quarter = SUM(uv_weight_month)
          .

COMPUTE price = value_quarter / weight_quarter.
EXECUTE.
FORMATS quarter (f8).

DELETE VARIABLES value_quarter weight_quarter year.

CASESTOVARS
  /ID=flow comno section Weight_HS 
  /INDEX= quarter 
  /SEPARATOR='_'
  /GROUPBY=VARIABLE.
EXECUTE.

* Compute price relative.
COMPUTE  price_rel_1 = price_4 / price_3.
COMPUTE  price_rel_2 = price_4 / price_2.

COMPUTE product_1 = price_rel_1 * Weight_HS.
COMPUTE product_2 = price_rel_2 * Weight_HS.
EXECUTE.


AGGREGATE /OUTFILE=* MODE=ADDVARIABLES
          /BREAK=flow section
          /prod_sum_1 = SUM(product_1)
          /prod_sum_2 = SUM(product_2)
          .

* aggregated weight for those who have valid values for price (and product).
COMPUTE Weight_section = Weight_HS * NOT(sysmis(product_1)).
EXECUTE.

AGGREGATE /OUTFILE=* MODE=ADDVARIABLES OVERWRITE=yes
          /BREAK=flow section
          /Weight_section = SUM(Weight_section)
          .

compute impute_base = sysmis(price_4).
do if (impute_base = 1).
   IF (sysmis(price_3) = 0) price_4 =  price_3 * prod_sum_1 /  Weight_section.
   IF  (sysmis(price_3) = 1)  price_4 =  price_2 * prod_sum_2 /  Weight_section.
end if.

FREQUENCIES impute_base.


AGGREGATE /OUTFILE=* MODE=ADDVARIABLES OVERWRITE=YES
          /BREAK=flow 
          /prod_sum_1 = SUM(product_1)
          /prod_sum_2 = SUM(product_2)
          .

* aggregated weight for those who have valid values for price (and product).
COMPUTE Weight_flow = Weight_HS * NOT(sysmis(product_1)).
EXECUTE.

AGGREGATE /OUTFILE=* MODE=ADDVARIABLES OVERWRITE=YES
          /BREAK=flow 
          /Weight_flow = SUM(Weight_flow)
          .

if (impute_base = 1) impute_base = sysmis(price_4) + 1 .
do if (impute_base = 2).
   IF (sysmis(price_3) = 0) price_4 =  price_3 * prod_sum_1 /  Weight_flow.
   IF  (sysmis(price_3) = 1)  price_4 =  price_2 * prod_sum_2 /  Weight_flow.
end if.

FREQUENCIES impute_base.

TITLE 'List of imputed commodities'.
TEMPORARY.
SELECT IF (any(impute_base,1,2)).
LIST ALL.

RENAME VARIABLES (price_4 = base_price) .


* Save for previous year.
SAVE OUTFILE=!quote(!concat('Data/base_price_',!flow,'_',!year_1,'.sav')) /KEEP flow comno base_price impute_base.


* Create an empty dataset for unchained indexes for actual year.
SELECT IF(flow = '7').
EXECUTE.
SAVE OUTFILE=!quote(!concat('Data/index_unchained_',!flow,'_',!year,'.sav')) /KEEP=flow.

!ENDDEFINE.