* Encoding: UTF-8.


PRESERVE.
 SET DECIMAL COMMA.

GET DATA  /TYPE=TXT
  /FILE="C:\Users\krl\TradeIndexMozambique\data\Export - 2019_XPMI.csv"
  /ENCODING='UTF8'
  /DELCASE=LINE
  /DELIMITERS=";"
  /ARRANGEMENT=DELIMITED
  /FIRSTCASE=2
  /DATATYPEMIN PERCENTAGE=95.0
  /VARIABLES=
  flow AUTO
  year AUTO
  month AUTO
  ref AUTO
  ItemID AUTO
  comno AUTO
  country AUTO
  unit AUTO
  weight AUTO
  quantity AUTO
  value AUTO
  valUSD AUTO
  itemno AUTO
  exporterNUIT AUTO
  exportername AUTO
  /MAP.
RESTORE.


GET DATA  /TYPE=TXT
  /FILE="C:\Users\krl\TradeIndexMozambique\data\Export - 2019_XPMI.csv"
  /ENCODING='UTF8'
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
RESTORE.

FREQUENCIES flow unit country.


TEMPORARY.
SELECT IF (country = 'NO').
FREQUENCIES comno .

DESCRIPTIVES weight quantity value valusd.

DESCRIPTIVES weight quantity value /statistics = sum mean min max stddev.

TEMPORARY.
SELECT IF (country = 'ZA').
DESCRIPTIVES weight quantity value /statistics = sum mean min max stddev.

MEANS valUSD BY unit.
MEANS valUSD BY unit /CELLS=sum min max mean stddev.
MEANS valUSD value BY unit /CELLS=sum min max mean stddev.


TEMPORARY.
SELECT IF (country = 'LS').
MEANS valUSD BY comno /CELLS=sum min max mean stddev.


STRING hs4 (a4).
COMPUTE hs4 = CHAR.SUBSTR(comno,1,4).
STRING hs2 (a2).
COMPUTE hs2 = CHAR.SUBSTR(hs4,1,2).
EXECUTE.
FREQUENCIES hs2.

COMPUTE price_usd = valusd / weight.
DESCRIPTIVES price_usd.

MEANS price_usd by hs2.

