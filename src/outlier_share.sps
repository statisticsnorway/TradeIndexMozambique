* Encoding: UTF-8.
DATASET CLOSE all.
get FILE="data/Export_2020Q1.sav".
ADD FILES FILE=*
         /FILE='data/Export_2020Q2.sav'
         /FILE='data/Export_2020Q3.sav'
         /FILE='data/Export_2020Q4.sav'
.
recode outlier_dev_median_q
    (0 = 0)
    (1 = 2)
    (2 = 1)
    into outlier_dev_median_quarter
    .
VALUE LABELS outlier_dev_median_quarter
 0 'No outlier'
 1 'Special case, kept'
 2 'Outlier'
 .           

CTABLES
  /FORMAT MAXCOLWIDTH=128
  /VLABELS VARIABLES=outlier_dev_median_quarter value price DISPLAY=LABEL
  /TABLE outlier_dev_median_quarter BY value [COUNT F40.0, SUM, COLPCT.SUM PCT40.1] + price [MEAN, STDDEV]
  /CATEGORIES VARIABLES=outlier_dev_median_quarter ORDER=A KEY=VALUE EMPTY=EXCLUDE TOTAL=YES POSITION=BEFORE
  /TITLES
    TITLE='Outliers on standard deviation.'.

* Find the sum of each comno.
AGGREGATE
  /OUTFILE=* MODE=ADDVARIABLES
  /BREAK=flow year quarter comno outlier_dev_median_quarter 
  /comno_sum=SUM(value)
.

sort cases by flow year quarter comno outlier_dev_median_quarter  .

match files file=*
    /by flow year quarter comno outlier_dev_median_quarter
    /last = l_comno.
.

sort cases by  flow (A) year (A) quarter (A) outlier_dev_median_quarter(D) comno_sum (D) comno (A) l_comno (D).

* number the comno by sum.
DO IF ($casenum = 1 or quarter NE lag(quarter)).
 COMPUTE  comno_counter=1.
ELSE IF (l_comno = 1).
 COMPUTE  comno_counter=comno_counter+1.
END IF.
LEAVE comno_counter.
EXECUTE.

sort cases by flow year quarter comno.

TEMPORARY.
SELECT IF (comno_counter < 11 and l_comno = 1 and quarter = 4).
SAVE OUTFILE='temp/largest_outliers.sav' /KEEP flow year quarter comno.

MATCH FILES file=*
           /table='temp/largest_outliers.sav'
           /in=largest
           /by flow year quarter comno
           .

* table of the 10 largest values for outliers.
TEMPORARY .
SELECT IF (largest = 1).
CTABLES
  /FORMAT MAXCOLWIDTH=128
  /VLABELS VARIABLES=comno outlier_dev_median_quarter value price DISPLAY=NONE
  /VLABELS VARIABLES=value price DISPLAY=LABEL
  /TABLE comno > outlier_dev_median_quarter BY value [COUNT F40.0, SUM, COLPCT.SUM PCT40.1] + price [MEAN F40.1, STDDEV F40.1]
  /CATEGORIES VARIABLES=comno ORDER=A KEY=VALUE EMPTY=EXCLUDE TOTAL=YES POSITION=BEFORE LABEL='Grand total'
  /CATEGORIES VARIABLES=outlier_dev_median_quarter ORDER=A KEY=VALUE EMPTY=EXCLUDE TOTAL=YES POSITION=BEFORE
  /TITLES
    TITLE='Outlier share for 10 largest commodities based on outlier values'.

DELETE VARIABLES comno_counter l_comno comno_sum outlier_dev_median_quarter. 



* med median_q.


CTABLES
  /VLABELS VARIABLES=outlier_dev_median_quarter value price DISPLAY=LABEL
  /TABLE outlier_dev_median_quarter BY value [COUNT F40.0, SUM, COLPCT.SUM PCT40.1] + price [MEAN, STDDEV]
  /CATEGORIES VARIABLES=outlier_dev_median_quarter ORDER=A KEY=VALUE EMPTY=EXCLUDE TOTAL=YES POSITION=BEFORE
  /TITLES
    TITLE='Outliers on standard deviation.'.

* Find the sum of each comno.
AGGREGATE
  /OUTFILE=* MODE=ADDVARIABLES
  /BREAK=flow comno outlier_dev_median_quarter 
  /comno_sum=SUM(value)
.

sort cases by comno outlier_dev_median_quarter  .

match files file=*
    /by comno outlier_dev_median_quarter
    /last = l_comno.
.

sort cases by outlier_dev_median_quarter(D) comno_sum (D) comno (A) l_comno (D).

* number the comno by sum.
DO IF ($casenum = 1).
 COMPUTE  comno_counter=1.
ELSE IF (l_comno = 1).
 COMPUTE  comno_counter=comno_counter+1.
END IF.
LEAVE comno_counter.
EXECUTE.

sort cases by comno.

TEMPORARY.
SELECT IF (comno_counter < 11 and l_comno = 1).
SAVE OUTFILE='temp/largest_outliers.sav' /KEEP comno.

MATCH FILES file=*
           /table='temp/largest_outliers.sav'
           /in=largest
           /by comno
           .

VALUE LABELS outlier_dev_median_quarter
 0 'No outlier'
 2 'Other kept cases'
 1 'Outlier'
 .           

* table of the 10 largest values for outliers.
TEMPORARY .
SELECT IF (largest = 1).
CTABLES
      /VLABELS VARIABLES=comno outlier_dev_median_quarter value price DISPLAY=NONE
  /VLABELS VARIABLES=value price DISPLAY=LABEL
  /TABLE comno > outlier_dev_median_quarter BY value [COUNT F40.0, SUM, COLPCT.SUM PCT40.1] + price [MEAN F40.1, STDDEV F40.1]
  /CATEGORIES VARIABLES=comno ORDER=A KEY=VALUE EMPTY=EXCLUDE TOTAL=YES POSITION=BEFORE LABEL='Grand total'
  /CATEGORIES VARIABLES=outlier_dev_median_quarter ORDER=A KEY=VALUE EMPTY=EXCLUDE TOTAL=YES POSITION=BEFORE
  /TITLES
    TITLE='Outlier share for 10 largest commodities based on outlier values'.

DELETE VARIABLES comno_counter l_comno comno_sum. 

