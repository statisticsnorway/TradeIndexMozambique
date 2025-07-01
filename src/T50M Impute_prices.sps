* Encoding: UTF-8.

DEFINE impute_price(year_base=!tokens(1)
                   /quarter_1=!tokens(1)
                   /year=!tokens(1)
                   /quarter=!tokens(1)
                   /flow=!tokens(1)
                   )


DATASET CLOSE all.
* Choose previous year.
!IF (!quarter = 1) !THEN 
 GET FILE=!quote(!concat('Data/base_price_',!flow,'_',!year_base,'.sav')).
 RENAME VARIABLES base_price = price.
 DELETE VARIABLES impute_base.
 EXECUTE.
!ELSE 
 GET FILE=!quote(!concat('Data/price_impute_',!flow,'_',!year,'Q',!quarter_1,'.sav')).
!IFEND
COMPUTE qrt = 0.
EXECUTE.
SAVE OUTFILE='temp\price_imputed_t1.sav' .

GET FILE=!quote(!concat('data\tradedata_no_outlier_',!flow,'_',!year,'Q',!quarter,'.sav')).

COMPUTE qrt = 1.
AGGREGATE /OUTFILE='temp\quarter.sav'
          /BREAK=Year quarter
          /qrt = MEAN(qrt)
          .

*AGGREGATE FROM MONTH TO QUARTER ON HS-LEVEL.

AGGREGATE /OUTFILE=*
          /BREAK=flow comno qrt
          /value_quarter = SUM(value_month)
          /uv_weight_quarter = SUM(uv_weight_month)
          .

COMPUTE price = value_quarter /uv_weight_quarter.
EXECUTE.
DELETE VARIABLES value_quarter uv_weight_quarter.

ADD FILES FILE='temp\price_imputed_t1.sav'
         /FILE=*.

SORT CASES BY flow comno .

FREQUENCIES qrt.

CASESTOVARS
  /ID=flow comno
  /INDEX= qrt
  /SEPARATOR='_'
  /GROUPBY=VARIABLE.
EXECUTE.

* Previous year.
MATCH FILES FILE=*
           /TABLE=!quote(!concat('Data/weight_base_',!flow,'_',!year_base,'.sav'))
           /IN=from_wgt
           /BY flow comno
           .
FREQUENCIES from_wgt.

* Select only those who are in the weight file.

SELECT IF (from_wgt = 1).
EXECUTE.
DELETE VARIABLES from_wgt Year quarter.
EXECUTE.

* Compute price relative.
COMPUTE  price_rel = price_1 / price_0.
COMPUTE product = price_rel * Weight_HS.
EXECUTE.

AGGREGATE /OUTFILE=* MODE=ADDVARIABLES overwrite=yes
          /BREAK=flow section
          /prod_sum = SUM(product)
          .

* aggregated weight for those who have valid values for price (and product).
COMPUTE Weight_section = Weight_HS * NOT(sysmis(product)).
EXECUTE.

AGGREGATE /OUTFILE=* MODE=ADDVARIABLES OVERWRITE=yes
          /BREAK=flow section
          /Weight_section = SUM(Weight_section)
          .

compute impute = sysmis(price_1).
do if (impute = 1).
  compute price_1 =  price_0 * prod_sum /  Weight_section.
  compute price_rel = price_1 / price_0.
end if.

FREQUENCIES impute.


AGGREGATE /OUTFILE=* MODE=ADDVARIABLES OVERWRITE=YES
          /BREAK=flow 
          /prod_sum = SUM(product)
          .

* aggregated weight for those who have valid values for price (and product).
COMPUTE Weight_flow = Weight_HS * NOT(sysmis(product)).
EXECUTE.

AGGREGATE /OUTFILE=* MODE=ADDVARIABLES OVERWRITE=YES
          /BREAK=flow
          /Weight_flow = SUM(Weight_flow)
          .

if (impute = 1) impute = sysmis(price_1) + 1 .
do if (impute = 2).
  compute price_1 =  price_0 * prod_sum / Weight_flow.
  compute price_rel = price_1 / price_0.
end if.
COMPUTE  weight_price_rel = price_rel * weight_HS.
EXECUTE.

FREQUENCIES impute.

DELETE VARIABLES Weight_flow price_0 .
RENAME VARIABLES price_1 = price .

COMPUTE qrt = 1.

MATCH FILES FILE=*
           /TABLE='temp\quarter.sav'
           /BY qrt
           .
EXECUTE.
DELETE VARIABLES qrt.
EXECUTE.
* actual quarter.
save OUTFILE=!quote(!concat('Data/price_impute_',!flow,'_',!year,'Q',!quarter,'.sav')).
!ENDDEFINE.




