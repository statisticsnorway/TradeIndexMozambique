* Encoding: UTF-8.
DATASET CLOSE all.
GET DATA
  /TYPE=XLSX
  /FILE='cat\Special series_XPMI.xlsx'
  /SHEET=name 'Export'
  /CELLRANGE=FULL
  /READNAMES=ON
 .
EXECUTE.

STRING flow (a1).
COMPUTE flow = 'E'.
ALTER TYPE Description (a99) .
ALTER TYPE Group (a66).
EXECUTE. 

IF (group =  '') group = lag(group).
EXECUTE.

SORT CASES by flow comno.

SAVE OUTFILE='temp/Special series_XPMI_export.sav'.

DATASET CLOSE all.
GET DATA
  /TYPE=XLSX
  /FILE='cat\Special series_XPMI.xlsx'
  /SHEET=name 'Import'
  /CELLRANGE=FULL
  /READNAMES=ON
 .
EXECUTE.

STRING flow (a1).
COMPUTE flow = 'I'.
ALTER TYPE Description (a99) .
ALTER TYPE Group (a66).
EXECUTE. 

IF (group =  '') group = lag(group).
EXECUTE.

SORT CASES by flow comno.

SAVE OUTFILE='temp/Special series_XPMI_import.sav'.

DATASET CLOSE all.
ADD FILES file='temp/Special series_XPMI_export.sav'
         /file='temp/Special series_XPMI_import.sav'
         .
EXECUTE.
DELETE VARIABLES v4 Description.
EXECUTE.

MATCH FILES file=*
           /last=last
           /by flow Comno
           .
EXECUTE.

SELECT IF (last = 1).
EXECUTE.
DELETE VARIABLES last.
SAVE OUTFILE='data/Special_series.sav'.

