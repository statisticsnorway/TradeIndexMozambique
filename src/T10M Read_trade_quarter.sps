* Encoding: UTF-8.
DEFINE read_quarter(flow=!tokens(1)
                   /year=!tokens(1)
                   /quarter=!tokens(1)
                   /outlier_limit_upper=!tokens(1)
                   /outlier_limit_lower=!tokens(1)
                   )
PRESERVE.
SET DECIMAL DOT.

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

FREQUENCIES found_section.

DELETE VARIABLES found_section.

COMPUTE quarter = number(month,f2) / 3.
COMPUTE quarter = TRUNC(quarter) + (quarter > TRUNC(quarter)).
EXECUTE.

* When the weight is 0 we set it to 1 as suggested by INE.
IF (weight = 0) weight = 1.

* For commodity 27160000 we use quantity as weight.
IF (comno = '27160000') weight = quantity. 

* When the value is 0, we delete the whole case.
SELECT IF NOT(value = 0). 

COMPUTE price = value / weight.
execute.

AGGREGATE
  /OUTFILE=* MODE=ADDVARIABLES
  /BREAK=flow comno quarter 
  /sd_comno=SD(price)
  /mean_comno=MEAN(price)
.

* Mark outliers.
compute ul = mean_comno + (!outlier_limit_upper * sd_comno).
compute ll = mean_comno - (!outlier_limit_lower * sd_comno).
EXECUTE.
COMPUTE outlier = 0.
if (price < ll or price > ul) outlier=1.
EXECUTE.

FREQUENCIES outlier.
MEANS TABLES=value BY outlier
  /CELLS=MEAN COUNT STDDEV SUM.

*DELETE VARIABLES ul ll sd_comno mean_comno.
EXECUTE.

SAVE OUTFILE=!quote(!concat("data/",!flow,"_",!year,"Q",!quarter,".sav"))

!ENDDEFINE.




