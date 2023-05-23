* Encoding: UTF-8.
PRESERVE.
SET DECIMAL DOT.

GET DATA  /TYPE=TXT
  /FILE="data\Export - 2018_XPMI_Q1.csv"
  /ENCODING='UTF8'
  /DELCASE=LINE
  /DELIMITERS=","
  /ARRANGEMENT=DELIMITED
  /FIRSTCASE=2
  /LEADINGSPACES IGNORE=YES
  /DATATYPEMIN PERCENTAGE=95.0
  /VARIABLES=
  flow A1
  year A4
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
  year A4
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

SAVE OUTFILE=!quote(!concat("data/",!flow,"_",!year,"Q",!quarter,".sav"))

!ENDDEFINE.

read_quarter flow=Export year=2018 quarter=1.
read_quarter flow=Export year=2018 quarter=2.
read_quarter flow=Export year=2018 quarter=3.
read_quarter flow=Export year=2018 quarter=4.

DATASET CLOSE ALL.
GET FILE='data/Export_2018Q1.sav'.
ADD FILES FILE=*
         /FILE='data/Export_2018Q2.sav'
         /FILE='data/Export_2018Q3.sav'
         /FILE='data/Export_2018Q4.sav'
.
EXECUTE.

SAVE OUTFILE='data/Export_2018.sav'.

