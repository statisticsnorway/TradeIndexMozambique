* Encoding: UTF-8.
DEFINE read_quarter(flow=!tokens(1)
                   /year=!tokens(1)
                   /quarter=!tokens(1)
                   /outlier_sd_limit=!tokens(1)
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
  /READNAMES=ON.
EXECUTE.
SORT CASES BY comno.
SELECT IF (comno NE '').
ALTER TYPE comno (A8).
SAVE OUTFILE='data\Commodities_use_quantity.sav'.

DATASET CLOSE ALL.

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
    comno A8
    country A2
    unit A8
    weight F17
    quantity F17
    value F17
    valUSD F17
    itemno F17
    exporterNUIT A9.
RESTORE.

FORMATS weight quantity (F12.0) value valusd (F17.0).

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
COMPUTE z_score = (price - mean_comno) / sd_comno.
COMPUTE outlier_sd = 0.
IF (ABS(z_score) > !outlier_sd_limit) outlier_sd = 1.
EXECUTE.

FREQUENCIES outlier_sd.

MEANS TABLES=value BY outlier_sd 
  /CELLS=MEAN COUNT STDDEV SUM.
EXECUTE.

SORT CASES BY flow comno.

SAVE OUTFILE=!quote(!concat("data/",!flow,"_",!year,"Q",!quarter,".sav")).

*--------------------------------------------------------------------*
* STEP 5: Check 1 — Multiple units per comno.
*--------------------------------------------------------------------*.
DATASET NAME DataSet1.
DATASET DECLARE UnitCheck.
DATASET COPY UnitCheck.
DATASET ACTIVATE UnitCheck.

SORT CASES BY comno unit.
MATCH FILES /FILE=* /BY comno unit /FIRST=firstunit.
SELECT IF firstunit=1.
AGGREGATE /OUTFILE=* MODE=ADDVARIABLES /BREAK=comno /n_unique_units=N.
IF (n_unique_units>1) multi_unit_flag=1.
IF (n_unique_units<=1) multi_unit_flag=0.
EXECUTE.

TITLE "Check 1 — Multiple units per comno".
FREQUENCIES VARIABLES=multi_unit_flag
  /FORMAT=DFREQ
  /ORDER=ANALYSIS.

*-- List each comno only once if it has multiple units.
SELECT IF (multi_unit_flag=1).
SORT CASES BY comno.
MATCH FILES /FILE=* /BY comno /FIRST=firstflag.
SELECT IF firstflag=1.
LIST comno n_unique_units.

SAVE OUTFILE='data/Comno_UnitCheck.sav'.
DATASET CLOSE UnitCheck.
DATASET ACTIVATE DataSet1.

*--------------------------------------------------------------------*
* STEP 6: Check 2 — Quantity missing or zero for use_quantity items.
*--------------------------------------------------------------------*.
DATASET DECLARE IssueCheck.
DATASET COPY IssueCheck.
DATASET ACTIVATE IssueCheck.

MATCH FILES FILE=* 
  /TABLE='data\Commodities_use_quantity.sav'
  /IN=use_quantity
  /BY comno.

COMPUTE quantity_issue = 0.
IF (use_quantity=1 AND (MISSING(unit) OR RTRIM(LTRIM(unit))="" OR quantity=0)) quantity_issue=1.
EXECUTE.

TITLE "Check 2 — Quantity missing or zero (use_quantity=1)".
FREQUENCIES VARIABLES=quantity_issue
  /FORMAT=DFREQ
  /ORDER=ANALYSIS.

*-- List each comno only once if issue found.
SELECT IF (quantity_issue=1).
SORT CASES BY comno.
MATCH FILES /FILE=* /BY comno /FIRST=firstissue.
SELECT IF firstissue=1.
LIST comno quantity_issue.

SAVE OUTFILE=!QUOTE(!CONCAT("data/commodities_issue_quantity_",!year,"Q",!quarter,".sav")).

DATASET CLOSE IssueCheck.
DATASET ACTIVATE DataSet1.

!ENDDEFINE.