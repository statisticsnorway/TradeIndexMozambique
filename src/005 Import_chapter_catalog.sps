﻿* Encoding: UTF-8.

* Import catalog with chapters.

DATASET CLOSE all.
GET DATA
  /TYPE=XLSX
  /FILE='Data\Chapter_Section.xlsx'
  /SHEET=name 'Ark1'
  /CELLRANGE=FULL
  /READNAMES=OFF
.
EXECUTE.

RENAME VARIABLES (v2=section) (v1=chapter).
EXECUTE.

SAVE OUTFILE='Data\Chapter_Section.sav'.

