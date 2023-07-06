* Encoding: UTF-8.
DEFINE read_quarter(flow=!tokens(1)
                   /year=!tokens(1)
                   /quarter=!tokens(1)
                   )
PRESERVE.
SET DECIMAL DOT.

DATASET CLOSE ALL.

GET DATA  /TYPE=TXT
  /FILE=!quote(!concat("data/",!flow," - ",!year,"_XPMI_Q",!quarter,".csv"))
  /ENCODING='UTF8'
  /DELCASE=LINE
  /DELIMITERS=","
  /ARRANGEMENT=DELIMITED
  /FIRSTCASE=2
  /LEADINGSPACES IGNORE=YES
  /VARIABLES=
  flow A1
  year F4
  month A2
  ref A14
  ItemID A8
  comno A8
  country A2
  unit A8
  weight AUTO
  quantity AUTO
  value AUTO
  valUSD AUTO
  itemno AUTO
  exporterNUIT A9
  /MAP.
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

SAVE OUTFILE=!quote(!concat("data/",!flow,"_",!year,"Q",!quarter,".sav"))

!ENDDEFINE.




