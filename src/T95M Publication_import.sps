* Encoding: UTF-8.
* Close all datasets.
DATASET CLOSE ALL.

* Open the file.
GET FILE='data/index_chained_Import.sav'.


*-------------------------------------------------------------*
* 1. Detailed (Commodity). Clear output first.                *
*-------------------------------------------------------------*
OUTPUT CLOSE ALL.
OUTPUT NEW NAME=Detailed.

TEMPORARY.
SELECT IF (level = 'Commodity').
CTABLES
  /VLABELS VARIABLES=flow level series time index_chained DISPLAY=NONE
  /TABLE flow > level > series BY time > index_chained [MEAN]
  /SLABELS VISIBLE=NO
  /CATEGORIES VARIABLES=flow level series time ORDER=A KEY=VALUE EMPTY=EXCLUDE
  /TITLES TITLE='Chained index detailed.'.

OUTPUT EXPORT
  /CONTENTS EXPORT=VISIBLE
  /XLSX DOCUMENTFILE="publication\chained_index_detailed_Import.xlsx"
  OPERATION=CREATEFILE.

OUTPUT CLOSE NAME=Detailed.


*-------------------------------------------------------------*
* 2. Aggregated (non-Commodity). Clear output first.          *
*-------------------------------------------------------------*
OUTPUT CLOSE ALL.
OUTPUT NEW NAME=Aggregated.

TEMPORARY.
SELECT IF (level NE 'Commodity').
CTABLES
  /VLABELS VARIABLES=flow level series time index_chained DISPLAY=NONE
  /TABLE flow > level > series BY time > index_chained [MEAN]
  /SLABELS VISIBLE=NO
  /CATEGORIES VARIABLES=flow level series time ORDER=A KEY=VALUE EMPTY=EXCLUDE
  /TITLES TITLE='Chained index aggregated.'.

OUTPUT EXPORT
  /CONTENTS EXPORT=VISIBLE
  /XLSX DOCUMENTFILE="publication\chained_index_aggregated_Import.xlsx"
  OPERATION=CREATEFILE.

OUTPUT CLOSE NAME=Aggregated.


EXECUTE.
