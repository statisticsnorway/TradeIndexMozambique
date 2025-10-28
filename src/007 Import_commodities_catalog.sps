* Encoding: UTF-8.
DATASET CLOSE ALL.
GET DATA
  /TYPE=XLSX
  /FILE='cat\Commodities_Catalogue_XPMI_2024.xlsx'
  /SHEET=name 'Pauta Grupos'
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

* Make label syntax for series for sitc1 and sitc2.
GET FILE='temp/commcat.sav'.
DELETE VARIABLES comno TO Descriptionsitcr4_3 sitcr4_1_AGR TO becno.
EXECUTE.

STRING series (a2) series_labels (A172).
COMPUTE series = sitcr4_1.
COMPUTE series_labels = Descriptionsitcr4_1.

SAVE OUTFILE='temp/sitc1_cat' /KEEP series series_labels.

COMPUTE series = sitcr4_2.
COMPUTE series_labels = Descriptionsitcr4_2.

ADD FILES file=sitc1_cat
         /file=*
         .
EXECUTE.

SAVE OUTFILE='temp/series_cat.sav'.

ValueLabelFromDataset 
 infile='temp/series_cat.sav' 
 codevar=series 
 textvar=series_labels
 vars=series \
 outfile="src/valuelabels_series.sps" 
 includecode=1
 .




