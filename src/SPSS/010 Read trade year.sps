* Encoding: UTF-8.

DATASET CLOSE all.
GET DATA  /TYPE=TXT
  /FILE="data\Export - 2018_XPMI.csv"
  /ENCODING='UTF-8'
  /DELCASE=LINE
  /DELIMITERS=";"
  /ARRANGEMENT=DELIMITED
  /FIRSTCASE=2
  /DATATYPEMIN PERCENTAGE=95.0
  /VARIABLES=
  flow A1
  year A4
  month A2
  ref A11
  ItemID A8
  comno A8
  country A2
  unit AUTO
  weight AUTO
  quantity AUTO
  value AUTO
  valUSD AUTO
  itemno AUTO
  exporterNUIT A9
  /MAP.

FORMATS weight  quantity (f12.1) value (f14.0) valusd (f14.2).

FREQUENCIES flow month country unit.

SAVE OUTFILE='data/export_2018.sav'.

