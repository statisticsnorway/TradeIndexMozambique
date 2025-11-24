* Encoding: UTF-8.

*Run after read_trade_quarter


*--------------------------------------------------------------------*
* STEP 1: Check 1 — Multiple units per comno.
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

SAVE OUTFILE=!QUOTE(!CONCAT("temp/UnitCheck_",!year,"Q",!quarter,".sav")).
DATASET CLOSE UnitCheck.
DATASET ACTIVATE DataSet1.

*--------------------------------------------------------------------*
* STEP 2: Check 2 — Quantity missing or zero for use_quantity items.
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

SAVE OUTFILE=!QUOTE(!CONCAT("temp/commodities_issue_quantity_",!year,"Q",!quarter,".sav")).

DATASET CLOSE IssueCheck.
DATASET ACTIVATE DataSet1.

!ENDDEFINE.
