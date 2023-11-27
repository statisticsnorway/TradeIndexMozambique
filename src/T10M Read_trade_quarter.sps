* Encoding: UTF-8.
DEFINE read_quarter(flow=!tokens(1)
                   /year=!tokens(1)
                   /quarter=!tokens(1)
                   /outlier_sd_limit_upper=!tokens(1)
                   /outlier_sd_limit_lower=!tokens(1)
                   /outlier_dev_median_quarter_limit=!tokens(1)
                   )
PRESERVE.
SET DECIMAL DOT.

* Read commodities that shall use quantity instead of weight as denominator.
DATASET CLOSE ALL.
GET DATA
  /TYPE=XLSX
  /FILE='data\Commodities_use_quantity.xlsx'
  /SHEET=name 'Commodities'
  /CELLRANGE=FULL
  /READNAMES=ON
  .
EXECUTE.
SORT CASES BY comno.
select if (comno NE '').
alter type comno (a8).

SAVE OUTFILE='data\Commodities_use_quantity.sav'.

DATASET CLOSE ALL.

GET DATA  /TYPE=TXT
  /FILE=!quote(!concat("data/",!flow," - ",!year,"_XPMI_Q",!quarter,".csv"))
  /DELCASE=LINE
  /DELIMITERS=","
  /ARRANGEMENT=DELIMITED
  /FIRSTCASE=2
  /VARIABLES=
  flow A1
  year F4
  month A2
  ref A14
  ItemID A8
  comno A8
  country A2
  unit A8
  weight F17
  quantity F17
  value F17
  valUSD F17
  itemno F17
  exporterNUIT A9
  .
RESTORE.

FORMATS weight quantity (F12.0) value valusd (F17.0).

SORT CASES BY comno.
MATCH FILES FILE=*
           /TABLE='data\commodity_sitc.sav'
           /IN=found_sitc
           /BY comno
           .

FREQUENCIES found_sitc.

DELETE VARIABLES found_sitc.

STRING chapter (a2).
COMPUTE chapter = char.substr(comno,1,2).

MATCH FILES FILE=*
           /TABLE='data\Chapter_Section.sav'
           /IN=found_section
           /BY chapter
           .

TITLE 'Check if section found for all read data'.
FREQUENCIES found_section.

TEMPORARY.
SELECT IF (found_section = 1 and comno NE '').
TITLE 'Check if section found for those who have comno'.
FREQUENCIES found_section.

DELETE VARIABLES found_section.

COMPUTE quarter = number(month,f2) / 3.
COMPUTE quarter = TRUNC(quarter) + (quarter > TRUNC(quarter)).
EXECUTE.

*CLEAN DATA - REMOVE OBVIOUS ERRORS.

* Match with commodities that will use quantity as unit value.
MATCH FILES file=*
           /TABLE='data\Commodities_use_quantity.sav'
           /IN=use_quantity
           /BY comno
           .
EXECUTE.

FREQUENCIES use_quantity.

DO IF (use_quantity = 1).
 COMPUTE uv_weight = quantity. 
ELSE. 
 COMPUTE uv_weight = weight. 
END IF. 

EXECUTE.
DELETE VARIABLES use_quantity.

* When the weight is 0 we delete the whole case.
SELECT IF NOT(uv_weight = 0).
execute. 

* When the value is 0, we delete the whole case.
SELECT IF NOT(value = 0). 

*COMPUTE PRICE PER TRANSACTION.
COMPUTE price = value / uv_weight.
execute.


* COUNT NUMBER OF TRANSACTIONS PER COMNO.

AGGREGATE
  /OUTFILE=* MODE=ADDVARIABLES
  /BREAK=flow comno quarter
  /N_transactions=N.

EXECUTE.

*OUTLIER DETECTION - MAD (ABSOLUTE DEVIATION FROM MEDIAN) - STANDARD DEVIATION FROM THE MEAN .
*MAD (ABSOLUTE DEVIATION FROM MEDIAN) .
* Calculate the Median (M) and Median Absolute Deviation (MAD).

AGGREGATE
  /OUTFILE=* MODE=ADDVARIABLES
  /BREAK=flow comno quarter 
  /price_median_quarter=MEDIAN(price)
  .

COMPUTE deviation_from_median = ABS(price - price_median_quarter).
EXECUTE.

AGGREGATE 
  /OUTFILE=* MODE=ADDVARIABLES
  /BREAK=flow comno quarter 
  /MAD = MEDIAN(deviation_from_median).
EXECUTE.

COMPUTE modified_Z = 0.6745 * deviation_from_median / MAD

DO IF (MAD = 0.0).
  COMPUTE outlier_dev_median_q = 2.
ELSE IF (ABS(modified_Z) > !outlier_dev_median_quarter_limit).
  COMPUTE outlier_dev_median_q = 1.
ELSE.
  COMPUTE outlier_dev_median_q = 0.
END IF.

FREQUENCIES outlier_dev_median_q.

*STANDARD DEVIATION FROM THE MEAN.

AGGREGATE
  /OUTFILE=* MODE=ADDVARIABLES
  /BREAK=flow comno quarter 
  /sd_comno=SD(price)
  /mean_comno=MEAN(price).

* Mark outlier_sd.
compute ul = mean_comno + (!outlier_sd_limit_upper * sd_comno).
compute ll = mean_comno - (!outlier_sd_limit_lower * sd_comno).
EXECUTE.
COMPUTE outlier_sd = 0.
if (price < ll or price > ul) outlier_sd=1.
EXECUTE.

FREQUENCIES outlier_sd.

MEANS TABLES=value BY outlier_dev_median_q outlier_sd 
  /CELLS=MEAN COUNT STDDEV SUM.

EXECUTE.

SORT CASES BY flow comno.

SAVE OUTFILE=!quote(!concat("data/",!flow,"_",!year,"Q",!quarter,".sav"))

!ENDDEFINE.







