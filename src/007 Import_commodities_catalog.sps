* Encoding: UTF-8.
DATASET CLOSE ALL.
GET DATA
  /TYPE=XLSX
  /FILE='cat\Commodities_Catalogue_XPMI.xlsx'
  /SHEET=name 'Pauta Grupos_2023_'
  /CELLRANGE=FULL
  /READNAMES=ON
.
EXECUTE.

* --- Extend comno width before appending.
ALTER TYPE comno (A9).
EXECUTE.

SAVE OUTFILE='temp/commcat.sav'.

ValueLabelFromDataset 
 infile='temp/commcat.sav' 
 codevar=sitcr4_1 
 textvar=Descriptionsitcr4_1
 vars=sitc1 \
 outfile="src/valuelabels_sitc1.sps" 
 includecode=1
 .

ValueLabelFromDataset 
 infile='temp/commcat.sav' 
 codevar=sitcr4_2 
 textvar=Descriptionsitcr4_2
 vars=sitc2 \
 outfile="src/valuelabels_sitc2.sps" 
 includecode=1
 .

ValueLabelFromDataset 
 infile='temp/commcat.sav' 
 codevar=SH2 
 textvar=DescriçãoSH2
 vars=chapter \
 outfile="src/valuelabels_chapter.sps" 
 includecode=1
 .

GET FILE='temp/commcat.sav'.

DELETE VARIABLES DescriçãoSH8 TO Descriptionsitcr4_3 Descriptionsitcr4_2 Descriptionsitcr4_1 TO becno.
EXECUTE.

SORT CASES BY comno.
MATCH FILES FILE=*
           /BY comno
           /FIRST = first_id
           .

FREQUENCIES first_id.

DELETE VARIABLES first_id.
RENAME VARIABLES sitcr4_1 = sitc1 sitcr4_2 = sitc2.
EXECUTE.

* --- Extend comno width before appending.
ALTER TYPE comno (A9).
EXECUTE.


SAVE OUTFILE='data\commodity_sitc.sav'.





