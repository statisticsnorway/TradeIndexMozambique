* Encoding: UTF-8.
DEFINE read_quarter(flow=!tokens(1)
                   /year=!tokens(1)
                   /quarter=!tokens(1)
                   /outlier_sd_limit=!tokens(1)
                   )

SET DECIMAL DOT.

* Read commodities that shall use quantity instead of weight as denominator.
DATASET CLOSE ALL.
GET DATA
  /TYPE=XLSX
  /FILE='cat\Commodities_use_quantity.xlsx'
  /SHEET=name 'Commodities'
  /CELLRANGE=FULL
  /READNAMES=ON.
EXECUTE.
SORT CASES BY comno.
SELECT IF (comno NE '').
ALTER TYPE comno (A9).
SAVE OUTFILE='data\Commodities_use_quantity.sav'.


GET DATA  
  /TYPE=TXT
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
    comno A9
    country A2
    unit A8
    weight F17
    quantity F17
    value F17
    valUSD F17
    itemno F17
    exporterNUIT A9.
EXECUTE.

FORMATS weight quantity (F12.0) value valusd (F17.0).
    
* --- Set measurement levels ---.

* Nominal variables.
VARIABLE LEVEL 
    flow year month ref ItemID comno country unit itemno exporterNUIT (NOMINAL).

* Scale variables.
VARIABLE LEVEL 
    weight quantity value valUSD (SCALE).
    
EXECUTE.


SORT CASES BY comno.

*Remove customs data where we use external source.


MATCH FILES FILE=*
 /TABLE=!quote(!concat("data\Use_external_source_",!flow,".sav"))
 /IN=use_external
 /BY comno.
EXECUTE.

TITLE "N. rows customs data kept - use ext. source (=1)".

FREQUENCIES use_external.

* Keep Customs data where use_external is NOT 1.
SELECT IF use_external = 0 OR MISSING(use_external).
EXECUTE.


SAVE OUTFILE=!quote(!concat("temp/inputdata_",!flow,".sav")).
DATASET CLOSE ALL. 



GET DATA  
  /TYPE=TXT
  /FILE=!quote(!concat("data/",!flow," - ",!year,"_External_source_Q",!quarter,".csv"))
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
    comno A9
    country A2
    unit A8
    weight F17
    quantity F17
    value F17
    valUSD F17
    itemno F17
    exporterNUIT A9.
EXECUTE.

FORMATS weight quantity (F12.0) value valusd (F17.0).

    
* --- Set measurement levels ---.

* Nominal variables.
VARIABLE LEVEL 
    flow year month ref ItemID comno country unit itemno exporterNUIT (NOMINAL).

* Scale variables.
VARIABLE LEVEL 
    weight quantity value valUSD (SCALE).
    
EXECUTE.




* Match with commodities that will use external source (=1).
SORT CASES BY comno.
MATCH FILES FILE=*
  /TABLE=!quote(!concat("data/Use_external_source_",!flow,".sav"))
  /IN=use_external
  /BY comno.
EXECUTE.


ADD FILES FILE=*
/FILE=!quote(!concat("temp/inputdata_",!flow,".sav"))
.
EXECUTE.

TITLE "N. rows from external source (=1)".
FREQUENCIES use_external.



SORT CASES BY comno.
MATCH FILES FILE=*
  /TABLE='data\commodity_sitc.sav'
  /IN=found_sitc
  /BY comno.
EXECUTE.

FREQUENCIES found_sitc.
DELETE VARIABLES found_sitc.

STRING chapter (A2).
COMPUTE chapter = CHAR.SUBSTR(comno,1,2).

MATCH FILES FILE=*
  /TABLE='data\Chapter_Section.sav'
  /IN=found_section
  /BY chapter.
EXECUTE.

TITLE 'Check if section found for all read data'.
FREQUENCIES found_section.

TEMPORARY.
SELECT IF (found_section = 1 AND comno NE '').
TITLE 'Check if section found for those who have comno'.
FREQUENCIES found_section.

DELETE VARIABLES found_section.

COMPUTE quarter = NUMBER(month,F2) / 3.
COMPUTE quarter = TRUNC(quarter) + (quarter > TRUNC(quarter)).
EXECUTE.

* --- Extend comno width before appending.
ALTER TYPE comno (A9).
EXECUTE.



* --- Append 'x' if ref starts with '99' or contains 'x'. 
* For those that starts with ref 99 in customs data or external source dataset will be tagged with an X after commodity number.
* When INE have decided on wether to use customs data or external source, this can be removed.
IF (CHAR.SUBSTR(ref,1,2) = '99' OR CHAR.INDEX(LOWER(ref),'x') > 0) comno = CONCAT(RTRIM(comno), 'x').
EXECUTE.



TITLE "Comno with external source FROM customs data".
* --- Show frequency of comno containing 'x'.
TEMPORARY.
SELECT IF CHAR.INDEX(LOWER(comno),'x') > 0 AND use_external = 0.
FREQUENCIES VARIABLES=comno.


TITLE "Comno with complete external source".
* --- Show frequency of comno containing 'x'.
TEMPORARY.
SELECT IF CHAR.INDEX(LOWER(comno),'x') > 0 AND use_external = 1.
FREQUENCIES VARIABLES=comno.


*CLEAN DATA - REMOVE OBVIOUS ERRORS.

* Match with commodities that will use quantity as unit value.
MATCH FILES FILE=*
  /TABLE='data\Commodities_use_quantity.sav'
  /IN=use_quantity
  /BY comno.
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
EXECUTE. 

* When the value is 0, we delete the whole case.
SELECT IF NOT(value = 0). 

* Compute price per transaction.
COMPUTE price = value / uv_weight.
EXECUTE.

* Count number of transactions per comno.
AGGREGATE
  /OUTFILE=* MODE=ADDVARIABLES
  /BREAK=flow comno quarter
  /N_transactions=N.
EXECUTE.

* Standard deviation from the mean.
AGGREGATE
  /OUTFILE=* MODE=ADDVARIABLES
  /BREAK=flow comno quarter 
  /sd_comno=SD(price)
  /mean_comno=MEAN(price).

* Mark outlier_sd.
IF (sd_comno > 0)  z_score = (price - mean_comno) / sd_comno.

COMPUTE outlier_sd = 0.
IF (ABS(z_score) > !outlier_sd_limit) outlier_sd = 1.
EXECUTE.


* Remove outlier tag for external source.
IF (use_external = 1) outlier_sd = 0.
EXECUTE.

FREQUENCIES outlier_sd.

MEANS TABLES=value BY outlier_sd 
  /CELLS=MEAN COUNT STDDEV SUM.
EXECUTE.

SORT CASES BY flow comno.

SAVE OUTFILE=!quote(!concat("data/",!flow,"_",!year,"Q",!quarter,".sav")).

!ENDDEFINE.
