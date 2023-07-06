* Encoding: UTF-8.
* Macro to create value labels from Spss dataset, the code must be a string variable.
DEFINE ValueLabelFromDataset 
               (infile=!tokens(1)
                /codevar=!tokens(1)
                /textvar=!tokens(1)
                /vars=!charend('\')
                /outfile=!tokens(1)
                /includecode=!default(0) !tokens(1)
               )

FILE HANDLE ValueLabelDataset /NAME=!infile . 
FILE HANDLE ValueLabelSyntax /NAME=!outfile . 

DATASET CLOSE ALL.
GET FILE=ValueLabelDataset /KEEP=!codevar !textvar.

SELECT IF (missing(!codevar) = 0).

SORT CASES BY !codevar.

MATCH FILES FILE=*
           /BY !codevar
           /FIRST = first_id
           .
SELECT IF (first_id = 1).

STRING vlabel (a130).
!if (!includecode = 1) !then
 COMPUTE vlabel = concat(' ',ltrim(!codevar)," '",ltrim(!codevar)," ",!textvar,"'").
!else
 COMPUTE vlabel = concat(' ',ltrim(!codevar)," '",!textvar,"'").
!ifend
COMPUTE caseno = $casenum.
execute.
AGGREGATE
  /OUTFILE=* MODE=ADDVARIABLES
  /BREAK=
  /max_code=MAX(caseno).

DO IF ($CASENUM  = 1).
PRINT OUTFILE=ValueLabelSyntax
       /!concat("'ADD VALUE LABELS ",!vars,"'").      
END IF .

PRINT OUTFILE=ValueLabelSyntax
 / vlabel  .
DO IF ($CASENUM = max_code).
PRINT OUTFILE=ValueLabelSyntax
       /'.'.
END IF .
EXECUTE.

!ENDDEFINE.

