# SPSS Examples
Here are some examples for the Foreign Trade data that is to be used for the Price index for foreign trade.

It is possible to use SPSS menus for most of the tasks in SPSS. However, the syntax files that actually run the programs shall be saved. This is useful both for documentation and for the ability to re-run syntaxes.

The order of the syntaxes should also be documented. This can be done in a separate document.

Most of the menus create quite good syntax. However, there are a few tasks where the pasted syntaxes is not so good. One example of this is the check for duplicates, which create a much longer and complicated syntax than is necessary.
## Read csv files
When we work in SPSS, we always work on SPSS datasets. They shall have the file extension .sav. We can use the File, Open, Data to let SPSS guide us through the process.

The first window will look something like this:

![](images/examples-import1.jpg "Open data window")

We will not open an SPSS file, but a csv file. We change the file type to csv and then some files shall appear. We click once on the last file and it will be shown in the file name part of the window:

![](images/examples-import2.jpg "Files in folder")

Now we must click on the paste button the make sure the syntax will the copied. When we do that, the next window will pop up:

![](images/examples-import3.jpg "Import wizard - step 1")

We go the next step and fill in the right parameters for: 

- variable arrangement
- header line
- decimal symbol

![](images/examples-import4.jpg "Import wizard - step 2")

Then we choose the parameters for:
- first line of data
- case representation
- number of cases to import
  
![](images/examples-import5.jpg "Import wizard - step 3")

Now we will choose the
- delimiters (only semicolon in our data)
- text qualifier
- how to treat leading and trailing blanks

![](images/examples-import6.jpg "Import wizard - step 4")

In the next step we can change the names and types of the variables to be imported. It is often easier to do this after we have pasted the syntax so we leave it as it is:

![](images/examples-import7.jpg "Import wizard - step 5")

In the last step we can choose to cache the data which we usually don't need. We must remember to paste the syntax:

![](images/examples-import8.jpg "Import wizard - step 6")

The pastede syntax will look like this:

```spss
PRESERVE.
 SET DECIMAL COMMA.

GET DATA  /TYPE=TXT
  /FILE="C:\Users\krl\TradeIndexMozambique\data\Export - 2021_XPMI.csv"
  /DELCASE=LINE
  /DELIMITERS=";"
  /ARRANGEMENT=DELIMITED
  /FIRSTCASE=2
  /DATATYPEMIN PERCENTAGE=95.0
  /VARIABLES=
  flow AUTO
  year AUTO
  month AUTO
  comno AUTO
  ref AUTO
  ItemID AUTO
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
```

We see that all columns will be imported with auto detected format. This may cause a problem later because for one data file a column (variable) may be defined as numeric and the next data file as a string. When we want to add these together SPSS will not allow us. Columns to be added together must be of the same type. Hence, we can decide the types ourselves. We can choose between numeric (F) and string (A). It can be difficult to choose the number of decimals for numeric variables, so we can just change columns the string variables. We also want to avoid the last column from our import. The enhanced syntax can look like this:

```spss
PRESERVE.
 SET DECIMAL COMMA.

GET DATA  /TYPE=TXT
  /FILE="C:\Users\krl\TradeIndexMozambique\data\Export - 2021_XPMI.csv"
  /DELCASE=LINE
  /DELIMITERS=";"
  /ARRANGEMENT=DELIMITED
  /FIRSTCASE=2
  /DATATYPEMIN PERCENTAGE=95.0
  /VARIABLES=
  flow A1
  year A4
  month A2
  comno A8
  ref A11
  ItemID A8
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
```


## Know your data
When we have imported data to SPSS, we can begin to look at the data. There are some basic procedures we can use to get an overview of the data.

- frequencies   for categorical data with few unique values
- descriptives  for numeric data
- means         for numeric data by categories
- crosstab      for two-way frequencies

In addition to this, it is possible to make temporary selections of the data with the `temporary` and `select if` commands.

### Frequencies
We can start with a simple frequency table for two of the variables in our dataset:

``` spss
FREQUENCIES flow unit.
```

The output will be like this:

![](images/examples-freq1.jpg "Frequency of flow and unit")

Before the actual frequency tables we get summary of missing values for each of the variables. In the frequency tables, we see that there is one row for each category and the number of cases are counted.

Now we can create the same tables for a subset of the data. After we have created the table, we want all our data to be available again. Then we can use the `temporary` and `select if` commands. The syntax:

``` spss
TEMPORARY.
SELECT IF (country = 'PT').
FREQUENCIES flow unit.
```

Now, the frequency tables will only include exports to Portugal:

![](images/examples-freq2.jpg "Frequency of flow and unit for one country")

### Descriptives
For numeric variables, we can get an overview by using the *descriptives* procedure. We can do like this:

``` spss
DESCRIPTIVES weight quantity value.
```

The output will be like this:

![](images/examples-descriptives1.jpg "Basic descriptives")

Unfortunately, there is no way to avoid scientific notation on large numbers.

We can specify which statistics to calculate:

``` spss
DESCRIPTIVES weight quantity value /statistics = sum mean min max.
```

![](images/examples-descriptives2.jpg "Descriptives with selected statistics")

### Means
When we want to have numeric statistics grouped, we can use the means command. The measure is mentioned before the `by` parameter and the variable to group by after:

``` spss
MEANS value BY month.
```

We get an output table like this:

![](images/examples-means1.jpg "Basic means")

We can choose the statistics ourselves:

``` spss
MEANS value BY month /CELLS=sum min max mean.
```

The output:

![](images/examples-means2.jpg "Means with selected statistics")

When have more than one measure variable, the table layout changes;

``` spss
MEANS weight value BY month /CELLS=sum min.
```

First, we get a case processing summary which gives us a brief overview of included and excluded cases. Then our statistics are pivoted 90 degrees:

![](images/examples-means3.jpg "Descriptives with selected statistics for more measure variables")


## Value labels
When we want to present our results, we don't want to present codes. Instead, we have classifications which turns codes into to texts. In SPSS these ar called *value labels*

If the classification is in an Excel spreadsheet with separate columns for the code and text, we can use an Excel function to put them together in a way that is suitable for SPSS. That means the code should be in quotes (for string variables), the text should be in quotes, and we can add the code to be a part of the text. The spreadsheet looks like this:

![](images/examples-valuelabels1.jpg "Country list in Excel")

When we have a spreadsheet with columns like these we can use this function to create a column with the classification ready for SPSS:

``` excel
=CONCATENAR("'";A2;"'";" '";A2;" ";D2;"'")  (Portuguese)
=CONCATENATE("'";A2;"'";" '";A2;" ";D2;"'") (English)
=KJED.SAMMEN("'";A2;"'";" '";A2;" ";D2;"'") (Norwegian)
```

When this is working for one cell, we can copy the formula to all cells in the new column. The new column is added:

![](images/examples-valuelabels2.jpg "Country list in Excel with value labels column" )

Now we can copy the column and paste it into SPSS. Then we add the *value labels* command before the list and a dot after:

``` spss
VALUE LABELS country
'00' '00 Zona Neutra'
'AC' 'AC Ilhas Ascensão'
'AD' 'AD Andorra'
'AE' 'AE Emirados Árabes Unidos'
'AF' 'AF Afeganistão'
'AG' 'AG Antigua e Barbuda'
'AI' 'AI Anguila'
'AL' 'AL Albânia'
'AM' 'AM Arménia'
'AN' 'AN Antilhas Holandesas'
'AO' 'AO Angola'
'AQ' 'AQ Antártida'
'AR' 'AR Argentina'
'AS' 'AS Samoa Americana'
'AT' 'AT Áustria'
'AU' 'AU Austrália'
'AW' 'AW Aruba'
'AX' 'AX Alanda'
'AZ' 'AZ Azerbaijão'
'BA' 'BA Bósnia e Herzegovina'
'BB' 'BB Barbados'
'BD' 'BD Bangladesh'
'BE' 'BE Bélgica'
'BF' 'BF Burquina Fasso'
'BG' 'BG Bulgária'
'BH' 'BH Barém'
'BI' 'BI Burundi'
'BJ' 'BJ Benin'
'BL' 'BL São Bartolomeu'
'BM' 'BM Bermudas'
'BN' 'BN Brunei'
'BO' 'BO Bolívia'
'BQ' 'BQ Bonaire'
'BR' 'BR Brasil'
'BS' 'BS Bahamas'
'BT' 'BT Butão'
'BV' 'BV Ilha Bouvet'
'BW' 'BW Botsuana'
'BY' 'BY Bielorrússia'
'BZ' 'BZ Belize'
'CA' 'CA Canadá'
'CC' 'CC Ilhas Cocos (Keeling)'
'CD' 'CD RD Congo'
'CF' 'CF República Centro-Africana'
'CG' 'CG Congo'
'CH' 'CH Suíça'
'CI' 'CI Costa do Marfim'
'CK' 'CK Ilhas Cook'
'CL' 'CL Chile'
'CM' 'CM Camarões'
'CN' 'CN China'
'CO' 'CO Colômbia'
'CR' 'CR Costa Rica'
'CS' 'CS Checoslováquia'
'CU' 'CU Cuba'
'CV' 'CV Cabo Verde'
'CW' 'CW Curaçao'
'CX' 'CX Ilha do Natal'
'CY' 'CY Chipre'
'CZ' 'CZ República Checa'
'DE' 'DE Alemanha'
'DJ' 'DJ Jiboti'
'DK' 'DK Dinamarca'
'DM' 'DM Dominica'
'DO' 'DO República Dominicana'
'DZ' 'DZ Argélia'
'EC' 'EC Equador'
'EE' 'EE Estónia'
'EG' 'EG Egipto'
'EH' 'EH Saara Ocidental'
'ER' 'ER Eritreia'
'ES' 'ES Espanha'
'ET' 'ET Etiópia'
'EU' 'EU União Europeia'
'FI' 'FI Finlândia'
'FJ' 'FJ Fiji'
'FK' 'FK Ilhas Falkland'
'FM' 'FM Micronésia'
'FO' 'FO Ilhas Faroé'
'FR' 'FR França'
'FX' 'FX França Metropolitana'
'GA' 'GA Gabão'
'GB' 'GB Reino Unido'
'GD' 'GD Grenada'
'GE' 'GE Georgia'
'GF' 'GF Guiana Francesa'
'GG' 'GG Guernsey'
'GH' 'GH Gana'
'GI' 'GI Gibraltar'
'GL' 'GL Gronelândia'
'GM' 'GM Gâmbia'
'GN' 'GN Guiné'
'GP' 'GP Guadalupe'
'GQ' 'GQ Guiné Equatorial'
'GR' 'GR Grécia'
'GT' 'GT Guatemala'
'GU' 'GU Guam'
'GW' 'GW Guiné Bissau'
'GY' 'GY Guiana'
'HK' 'HK Hong Kong'
'HM' 'HM Ilhas Heard'
'HN' 'HN Honduras'
'HR' 'HR Croácia'
'HT' 'HT Haiti'
'HU' 'HU Hungria'
'ID' 'ID Indonésia'
'IE' 'IE Irlanda'
'IL' 'IL Israel'
'IM' 'IM Ilha do Homen'
'IN' 'IN Índia'
'IO' 'IO Território Britânico no Oceano'
'IQ' 'IQ Iraque'
'IR' 'IR Irão'
'IS' 'IS Islândia'
'IT' 'IT Itália'
'JE' 'JE Jersey'
'JM' 'JM Jamaica'
'JO' 'JO Jordânia'
'JP' 'JP Japão'
'KE' 'KE Quénia'
'KG' 'KG Quirguistão'
'KH' 'KH Camboja'
'KI' 'KI Quiribati'
'KM' 'KM Comores'
'KN' 'KN São Cristóvão e Nevis'
'KP' 'KP Coreia do Norte'
'KR' 'KR Coreia do Sul'
'KW' 'KW Koweit'
'KY' 'KY Ilhas Caymans'
'KZ' 'KZ Cazaquistão'
'LA' 'LA Laos'
'LB' 'LB Líbano'
'LC' 'LC Santa Lúcia'
'LI' 'LI Liechtenstein'
'LK' 'LK Sri Lanka'
'LR' 'LR Libéria'
'LS' 'LS Lesoto'
'LT' 'LT Lituânia'
'LU' 'LU Luxemburgo'
'LV' 'LV Letónia'
'LY' 'LY Líbia'
'MA' 'MA Marrocos'
'MC' 'MC Mónaco'
'MD' 'MD Moldávia'
'ME' 'ME Montenegro'
'MG' 'MG Madagáscar'
'MH' 'MH Ilhas Marshall'
'MK' 'MK Macedónia do Norte'
'ML' 'ML Mali'
'MM' 'MM Myanmar'
'MN' 'MN Mongólia'
'MO' 'MO Macau'
'MP' 'MP Marianas Setentrionais'
'MQ' 'MQ Martinica'
'MR' 'MR Mauritânia'
'MS' 'MS Monserrate'
'MT' 'MT Malta'
'MU' 'MU Maurícias'
'MV' 'MV Maldivas'
'MW' 'MW Malaui'
'MX' 'MX México'
'MY' 'MY Malásia'
'MZ' 'MZ Moçambique'
'NA' 'NA Namíbia'
'NC' 'NC Novo Caledónia'
'NE' 'NE Níger'
'NF' 'NF Ilha Norfolk'
'NG' 'NG Nigéria'
'NI' 'NI Nicarágua'
'NL' 'NL Países Baixos'
'NO' 'NO Noruega'
'NP' 'NP Nepal'
'NR' 'NR Nauru'
'NU' 'NU Niue'
'NZ' 'NZ Nova Zelândia'
'OM' 'OM Omã'
'PA' 'PA Panamá'
'PE' 'PE Peru'
'PF' 'PF Polinésia Francesa'
'PG' 'PG Papua Nova Guiné'
'PH' 'PH Filipinas'
'PK' 'PK Paquistão'
'PL' 'PL Polónia'
'PM' 'PM São Pedro e Miquelão'
'PN' 'PN Pitcairn'
'PR' 'PR Porto Rico'
'PT' 'PT Portugal'
'PW' 'PW Palau'
'PY' 'PY Paraguai'
'QA' 'QA Qatar'
'RE' 'RE Reunião'
'RO' 'RO Roménia'
'RS' 'RS Sérvia'
'RU' 'RU Rússia'
'RW' 'RW Ruanda'
'SA' 'SA Arábia Saudita'
'SB' 'SB Ilhas Salomão'
'SC' 'SC Seicheles'
'SD' 'SD Sudão'
'SE' 'SE Suécia'
'SG' 'SG Singapura'
'SH' 'SH Santa Helena'
'SI' 'SI Eslovénia'
'SJ' 'SJ Ilhas Svalbard  e Mayen'
'SK' 'SK República Eslovaca'
'SL' 'SL Serra Leoa'
'SM' 'SM San Marino'
'SN' 'SN Senegal'
'SO' 'SO Somália'
'SR' 'SR Suriname'
'SS' 'SS Sudão do Sul'
'ST' 'ST São Tomé e Príncipe'
'SU' 'SU ex-URSS'
'SV' 'SV El Salvador'
'SX' 'SX São Martinho'
'SY' 'SY Síria'
'SZ' 'SZ Essuatíni'
'TC' 'TC Ilhas Turks e Caicos'
'TD' 'TD Chade'
'TF' 'TF Terras Austrais Francesas'
'TG' 'TG Togo'
'TH' 'TH Tailândia'
'TJ' 'TJ Tajiquistão'
'TK' 'TK Toquelau'
'TL' 'TL Timor-Leste'
'TM' 'TM Turquemenistão'
'TN' 'TN Tunísia'
'TO' 'TO Tonga'
'TP' 'TP Timor-Leste'
'TR' 'TR Turquia'
'TT' 'TT Trindade e Tobago'
'TV' 'TV Tuvalu'
'TW' 'TW Taiwan'
'TZ' 'TZ Tanzânia'
'UA' 'UA Ucrânia'
'UG' 'UG Uganda'
'UM' 'UM EUA Territórios Insulares'
'US' 'US Estados Unidos'
'UY' 'UY Uruguai'
'UZ' 'UZ Uzbequistão'
'VA' 'VA Estado de Vaticano'
'VC' 'VC São Vicente e Granadinas'
'VE' 'VE Venezuela'
'VG' 'VG Ilhas Virgens Britânicas'
'VI' 'VI Ilhas Virgens Americanas'
'VN' 'VN Vietname'
'VU' 'VU Vanuatu'
'WF' 'WF Ilhas Wallis e Futuna'
'WS' 'WS Samoa'
'XK' 'XK Kosovo'
'XX' 'XX Organizações Internacionais'
'YE' 'YE Iémen'
'YT' 'YT Maiote'
'YU' 'YU Jugoslávia'
'ZA' 'ZA África  do Sul'
'ZM' 'ZM Zâmbia'
'ZW' 'ZW Zimbabué'
'ZZ' 'ZZ Outros Países'
.
```

Now we can make a frequency table to see if there are any countries which have not added text:

``` spss
FREQUENCIES country.
```

## New variables
There are two different kind of variables we can use in SPSS:

- String (character)
- Numeric (includes date and time variables)

String variables has to be defined before we assign them values. This is done with the `string` command. Numeric variables can assign a value when it is created. For both string and numeric variables, we assign values with the `compute` command. Here, we create a numeric variable for price and a string variable for HS2. For SPSS to actually do these calculations, we can add the `execute` command:

``` spss
COMPUTE pricekg = value / weight.

STRING hs2 (a2).
COMPUTE hs2 = CHAR.SUBSTR(comno,1,2).

EXECUTE.
```

We see in the syntax above that we use `char.substr`. This is a function that extracts parts of a string variable. The `char.substr` takes three parameters:
- the name of the variable to extract from
- the first position to extract
- the number of characters to extract

There are many useful functions in SPSS in addition to `char.substr`.

## Format variables
SPSS determines have to display variables. For numeric variables, the display format chosen by SPSS may not be as we like it to be. We can then change it by using the `formats` command. This command does not change any data, just the way it is displayed. Here we format the price per kg with 2 decimals:

``` spss
FORMATS pricekg (f14.2).
```

14 digit is the total number of characters to display, of which 2 is decimals and 1 is the decimal sign.

## Sort datasets
We can sort our datasets either by ascending og descending values. The command we use is `sort cases`. The default is to sort by ascending values. To sort descening instead, we include `(D)` after the variables name in the `sort cases` command. However, all variables will now be sorted descending unless we add an (A) to the variable before the variable with `(D)`. We will now sort the data by the background variables:

``` spss
SORT CASES BY flow year month comno country.
```

To sort the last variable descending and the other ones ascending we can do like this:

``` spss
SORT CASES BY flow year comno (A) valusd (D).
```

## Save datasets
To save a dataset, we use the `save` command:

``` spss
SAVE OUTFILE='C:\Users\krl\TradeIndexMozambique\data\export_2021.sav'.
``` 

We see above and the other places where datasets are mentioned that the whole path to the file is included. This is not ideal because there will be several places to change if we cahnge the location of the data files. Instead we should extract the main path from the string and put it in a `cd` command. The `cd` (change directory) is changing the working directory for the SPSS files. This command should be put in a separate syntax file, which we should always run as our first syntax every time we open SPSS.

``` spss
CD 'c:\users\krl\TradeIndexMozambique'.
```

## Open an SPSS dataset
When we have saved an SPSS dataset it can later be opened again. We use the `get` command for this. But first, we should be certain that we don't have more than one dataset open at the same time, as this can cause problems and confusion. This is done with the command `dataset close all`. An example:

``` spss
DATASET CLOSE ALL.
GET FILE='data\export_2021.sav'.
```

## Aggregation
There are two ways we do aggregation:
- Create a new dataset on an aggregated level of the data
- Add aggregated data to every row of the dataset

We can do both with the `aggregate` command. First, we will see how we can agregate to a new file. We knpw now that our data has one row for each combination of *flow*, *year*, *month*, *comno* and *country*. When we aggregate we first choose the aggregation level. For instance, we can aggregate to the level of *flow*, *year* and *country*. These will be our break variables. Now that we have decide the aggregation level, we need to decide what variables we want to aggregate and what kind of aggregation to do. The aggreagtion variables will usually be one or more of our measure variables. We can choose between different statistics for how to aggregate, like sum, mean, max, min etc. Here is an example where we calculate the sum of the *valusd* variable by *flow*, *year* and *country*:

``` spss
AGGREGATE 
    /OUTFILE=* 
    /BREAK flow year country
    /no_of_rows = N()
    /valusd = SUM(valusd)
    .
```
The aggregated dataset:

![](images/examples-aggregate1.jpg "Aggregated dataset")

Now we will look at the second way to aggregate, where we add aggregated variables to the exixting dataset. First, we have to reopen the original dataset. Then we can add the new variables with the `aggregate` command. The clue here is to use the `mode = addvariables` parameter. The aggregated variables will get the same value for each row in the group of the break level, here *flow*, *year* and *comno*:

``` spss
DATASET CLOSE ALL.
GET FILE='data\export_2021.sav'.

AGGREGATE 
    /OUTFILE=* MODE=ADDVARIABLES
    /BREAK flow year comno
    /no_of_rows = N()
    /valusd_comno_max = MAX(valusd)
    /valusd_comno_min = MIN(valusd)
    .

SORT CASES BY flow year comno (A) valusd (D).
```

Now we have added some aggregated variables. They all have the same values within the aggregation level used:

![](images/examples-aggregate2.jpg "Aggregated variables added")

## Duplicates
We can use the ```match files``` command to check for duplicates. The way to do that is to mark each row in the dataset as first or not first within the group of variables we will check for duplicates within. Usually we check for duplicates on the variables that is to identify a row. In our dataset it is the variables *flow*, *year*, *month*, *comno*, *ref*, *ItemID* and *country*. After we have added the mark for first or not within the group, we can make a frequency table to get an owerview of the amount of duplicates. Here is an example on a duplicate check with a frequency check table:

``` spss
DATASET CLOSE ALL.
GET FILE='C:\Users\krl\TradeIndexMozambique\data\export_2021.sav'.
SORT CASES BY flow year month comno ref ItemID country.

MATCH FILES FILE=*
           /BY flow year month comno ref ItemID country
           /FIRST = first_id
           .

FREQUENCIES first_id.
```

If there are any rows with *first_id* = 1, we can check them a little bit more. 

We will now check for duplicates on the level of *flow*, *year*, *month*, *comno* and *country*:

``` spss
DELETE VARIABLES first_id.

SORT CASES BY flow year month comno country.

MATCH FILES FILE=*
           /BY flow year month comno country
           /FIRST = first_id
           .

FREQUENCIES first_id.
```

Before we create an index we want to aggregate the data to the level where there is one row for each combination of *flow*, *year*, *month*, *comno* and *country*:

``` spss
AGGREGATE 
    /OUTFILE=* 
    /BREAK flow year month comno country
    /weight = SUM(weight)
    /quantity = sum(quantity)
    /value = SUM(value)
    /valusd = SUM(valusd)
    .
```

When we now do a duplicate check there are no duplicates:

``` spss
MATCH FILES FILE=*
           /BY flow year month comno country
           /FIRST = first_id
           .

FREQUENCIES first_id.
```
## Read Excel files
We read an Excel file more or less the same way as a delimited text-file, with the *get data* command. This time we use type parameter xlsx. When we use the file, open wizard we paste a syntax like this:

``` spss
DATASET CLOSE ALL.
GET DATA
  /TYPE=XLSX
  /FILE='data\Commodities_Catalogue_XPMI.xlsx'
  /SHEET=name 'Pauta Grupos_2023_'
  /CELLRANGE=FULL
  /READNAMES=ON
.
EXECUTE.
```

We can delete variables we don't need and also check for duplicates:

``` spss
DELETE VARIABLES DescriçãoSH8 TO Descriptionsitcr4_3 Descriptionsitcr4_2 Descriptionsitcr4_1 TO becno.
EXECUTE.

SORT CASES BY comno.
MATCH FILES FILE=*
           /BY comno
           /FIRST = first_id
           .

FREQUENCIES first_id.

DELETE VARIABLES first_id.
```
Finally, we can save our dataset:

``` spss
SAVE OUTFILE='data\commodity_sitc.sav'.
```

## Matching files
We use the *match files* command to macth files. It has two different ways to match files. Either we can choose that both files should provide with cases, or we can choose to use one of the files as a keyed table. A keyed table may not have any duplicates. Cases in the keyed table with key variables whose values do not appear in the other file are not written to the output file. If there are more than one case with the same key value and that value is in the keyed table as well, all cases will get the information from the keyed table. We define a data set as a keyed table by using the *table* subcommand. Ordinary files are named with the *file* subcommand. If there are duplicates (i.e. more than one case with the same values for the key variables) SPSS will match 1 to 1 as long as it is possible and then match 1 to 0 or 0 to 1. The files we match have to be sorted on the key variables by which they will be matched by before we use the *match files* command. 

We now want to match the data file with the data file with the list of commodities and add the sitc codes to the data file. The list of commodities will be a keyd table which we define with the *table* sub-command. 

To check whether the *comno* value is found in the catalog, we include the *in* sub-command. It will create a new variable, which value will be one when the catalog contribute to the match (it matches) and zero when it does not contribute (it does not match).

``` spss
DATASET CLOSE ALL.
GET FILE='data\export_agg_2021.sav'.
SORT CASES BY comno.

MATCH FILES FILE=*
           /TABLE='data\commodity_sitc.sav'
           /IN=found_sitc
           /BY comno
           .

FREQUENCIES found_sitc sitcr4_1.
DELETE VARIABLES found_sitc.
SAVE OUTFILE='data\export_sitc_2021.sav'.
```

## Tabulation
We often want to present our data as tables. In SPSS, we can use the *ctables* command to create many different types of tables. We will look at a few of them now. The syntax for *ctables* is more complex than other commands, thus it is helpful to start with using the SPSS menus to create our first tables. However, we always paste the syntax. It is found under Analyze, Tables, Custom Tables.

The Custom Tables window looks like this:

![](images/examples-ctables1.jpg "The Custom Tables window")

We will drag and drop variables into the rows and columns. The variables may be used as

- Nominal: Each value of the variable will be a line or column 
- Ordinal: Each value of the variable will be an ordered line or column 
- Scale: A numeric variable used for measures

If a variable is nor defined as the type it shall have in the table, we can right-click on the variable and change the type.

For our first table, we want to have sitc 1 in the rows and months in the columns. We drag the variable *sitc4_1* from the list of variables and drop it within the Rows dimension and *month* in the Columns:

![](images/examples-ctables2.jpg "One nominal variable in each dimension")

We can now paste the syntax. It will look like this:

```spss
CTABLES
  /VLABELS VARIABLES=sitcr4_1 month DISPLAY=LABEL
  /TABLE sitcr4_1 BY month [COUNT F40.0]
  /CATEGORIES VARIABLES=sitcr4_1 month ORDER=A KEY=VALUE EMPTY=EXCLUDE.
```

These sub-commands are used:
- vlabels: Define how labels are to be presented
- table: The elements in the table and their placement
- categories: Parameters for the categorical (nominal, ordinal) variables

The table look like this when we run the syntax:

![](images/examples-ctables3.jpg "Table with one variable in each dimension")

We see that the number of cases is counted in the cells in the table. We can change that to a measure instead. We open the Custom tables window again. It will remember the previous table. Now we choose the *valusd* variable and drop it underneath the months: 

![](images/examples-ctables4.jpg "Scale variable added")

We can paste the syntax:

```spss
CTABLES
  /VLABELS VARIABLES=sitcr4_1 month valusd DISPLAY=LABEL
  /TABLE sitcr4_1 BY month > valusd [MEAN]
  /CATEGORIES VARIABLES=sitcr4_1 month ORDER=A KEY=VALUE EMPTY=EXCLUDE
.
```

We run the program and get our table:

![](images/examples-ctables5.jpg "Table with mean values")

We see that the figures have 2 decimals, which we don't need. We open the window again. Then we click on *summary statistics* in bottom left corner which will open a new window. In this window, we change the format from *Auto* to *n,nnn*. Finally, we change to number of decimals to 0:

![](images/examples-ctables6.jpg "Summary statistics window")

We apply our changes to the selection and close the window. Then we can paste the syntax again:

```spss
CTABLES
  /VLABELS VARIABLES=sitcr4_1 month valusd DISPLAY=LABEL
  /TABLE sitcr4_1 BY month > valusd [MEAN F40.0]
  /CATEGORIES VARIABLES=sitcr4_1 month ORDER=A KEY=VALUE EMPTY=EXCLUDE
.
```

Let us add som totals in the rows and columns. We can choose to put the totals before or after the categorical variables. In the Custom tables window, we can click on the categorical variable in the rows and then we will be able to click on the *Categories and totals* button. We choose that the totals should be before (above) the category:

![](images/examples-ctables7.jpg "Categories and Totals")

We apply the options and do the same for the *month* variable in the columns. Then we paste the syntax:

```spss
CTABLES
  /VLABELS VARIABLES=sitcr4_1 month valusd DISPLAY=LABEL
  /TABLE sitcr4_1 BY month > valusd [MEAN F40.0]
  /CATEGORIES VARIABLES=sitcr4_1 month ORDER=A KEY=VALUE EMPTY=EXCLUDE TOTAL=YES POSITION=BEFORE
.
```

The change in the syntax is that the parameters *Total* and *Position* in the *categories* sub-command are added.   

The table is now with total row and total column:

![](images/examples-ctables8.jpg "Totals row and column")

Now, we can add a title to the table. To do that we swap to the *titles* tab in the Custom tables window:

![](images/examples-ctables9.jpg "Table titles")

In the pasted syntax, a *titles* sub-command is added

```spss
CTABLES
  /VLABELS VARIABLES=sitcr4_1 month valusd DISPLAY=LABEL
  /TABLE sitcr4_1 BY month > valusd [MEAN F40.0]
  /CATEGORIES VARIABLES=sitcr4_1 month ORDER=A KEY=VALUE EMPTY=EXCLUDE TOTAL=YES POSITION=BEFORE
   /TITLES
    TITLE='Average export value in USD by sitc and month.'.
```

As we now have information in the title, we ca remove some of it in the table. First, we can hide the *mean* header in every column. We click on the *Hide* button. Then we want to remove the valusd header as well. We right-click on the *valusd* column and uncheck the display of variable label, and do the same for the *month* column:

![](images/examples-ctables10.jpg "Hide column headers")

In the syntax, there are some additions. One more *vlabels* sub-command and a *slabels* sub-command is added: 

```spss
CTABLES
  /VLABELS VARIABLES=sitcr4_1 DISPLAY=LABEL  
  /VLABELS VARIABLES=month valusd DISPLAY=NONE
  /TABLE sitcr4_1 BY month > valusd [MEAN F40.0]
  /SLABELS VISIBLE=NO
  /CATEGORIES VARIABLES=sitcr4_1 month ORDER=A KEY=VALUE EMPTY=EXCLUDE TOTAL=YES POSITION=BEFORE
  /TITLES
    TITLE='Average export value in USD by sitc and month.'.
```

The table looks quite nice now:

![](images/examples-ctables11.jpg "Titles included")

When we have two or more categories in the same dimension in the table, either rows or columns, we can either have them nested or stacked. We will first look at a nested table. Me move the *month* variable from the columns to the rows and put it to the right of the *sitc4_1* variable. It can be dropped when a red square appears at the right side of the variable.

![](images/examples-ctables12.jpg "Categories nested")

The syntax is here:

```spss
CTABLES
  /VLABELS VARIABLES=sitcr4_1 DISPLAY=LABEL  
  /VLABELS VARIABLES=month valusd DISPLAY=NONE
  /TABLE sitcr4_1 > month BY valusd [MEAN F40.0]
  /SLABELS VISIBLE=NO
  /CATEGORIES VARIABLES=sitcr4_1 month ORDER=A KEY=VALUE EMPTY=EXCLUDE TOTAL=YES POSITION=BEFORE
  /TITLES
    TITLE='Average export value in USD by sitc and month.'.
```

The first part of the table:

![](images/examples-ctables13.jpg "Nested table")

Now we can stack the variables instead. We move the *month* underneath the *sitc4_1* variable:

![](images/examples-ctables14.jpg "Categories stacked")

The pasted syntax:

```spss
CTABLES
  /VLABELS VARIABLES=sitcr4_1 DISPLAY=LABEL  
  /VLABELS VARIABLES=month valusd DISPLAY=NONE
  /TABLE sitcr4_1 + month BY valusd [MEAN F40.0]
  /SLABELS VISIBLE=NO
  /CATEGORIES VARIABLES=sitcr4_1 month ORDER=A KEY=VALUE EMPTY=EXCLUDE TOTAL=YES POSITION=BEFORE
  /TITLES
    TITLE='Average export value in USD by sitc and month.'.
```
The table is now stacked:

![](images/examples-ctables15.jpg "Stacked table")

The difference in the syntax between nested and stacked table is that the > sign is used for nested tables and the sign + for stacked.

When the figures in the cells are very high, they may be presented in a less radable way. When we for instance change from dollars to meticais for the measured values and also change from mean to sum, the figures will be much higher. Here is the syntax:

```spss
CTABLES
  /VLABELS VARIABLES=sitcr4_1 DISPLAY=LABEL  /VLABELS VARIABLES=month value DISPLAY=NONE
  /TABLE sitcr4_1 + month BY value [SUM F40.0]
  /SLABELS VISIBLE=NO
  /CATEGORIES VARIABLES=sitcr4_1 month ORDER=A KEY=VALUE EMPTY=EXCLUDE TOTAL=YES POSITION=BEFORE
  /TITLES
    TITLE='Export value by sitc and month.'.
```
And here is the output:

![](images/examples-ctables16.jpg "Figures with scientific notation due to lack of space")

These figures are not easy to read. To get rid of the scientific notation, we choose the options in the ctables windows and change the maximum width:

![](images/examples-ctables17.jpg "Ctables otions window")

When we paste the syntax, a *format* sub-command will be added to our syntax:

```spss
CTABLES
  /FORMAT EMPTY=ZERO MISSING='.' MINCOLWIDTH=36 MAXCOLWIDTH=132 UNITS=POINTS
  /VLABELS VARIABLES=sitcr4_1 DISPLAY=LABEL  /VLABELS VARIABLES=month value DISPLAY=NONE
  /TABLE sitcr4_1 + month BY value [SUM F40.0]
  /SLABELS VISIBLE=NO
  /CATEGORIES VARIABLES=sitcr4_1 month ORDER=A KEY=VALUE EMPTY=EXCLUDE TOTAL=YES POSITION=BEFORE
  /TITLES
    TITLE='Export value by sitc and month.'.
```

The figures are now formatted in a better way for presentation:
![](images/examples-ctables18.jpg "Better cell display format")


## Macros
We use macros when we want to execute almost the same syntax code several times. Instead of copying the code lots of times, we write it in a macro. The places in the code that will be changed each time we run the code, will be replaced with macro variables. These macro variables will be used as parameters to the macro.

A macro is defined with a DEFINE command and ends with an !ENDDEFINE command. The macro consists of a set of SPSS commands. To be able to change the code slightly each time we execute it, we use macro variables as parameters. These macro variables are set to different values each time we call the macro. We need to call the macro with its name for execution. We can call the macro as many times as we like. When we call the macro we also set the values for the macro variables used in the macro. The macro variables values are used as parameters in the macro. Each place the macro variable is mentioned in the macro, the parameter will replace the macro name. 

We will now make a macro for a simple *ctables* command. We start simple with just one parameter that can be changed, the variable in the rows. We call the parameter rowvar. This parameter is to be defined in the *define* command. The parameter has a keyword telling how the parameter is to be used. Most often we use the keyword *tokens(1)*, which means the parameter has one value. 

Every place in our code where we want to replace the value of the parameter, we type in the parameter with the prefix !. We see that in the syntax  below, where we have replaced the variable name *sitcr4_1* with *!rowvar* three places:

```spss
DEFINE tabul (rowvar=!tokens(1))

CTABLES
  /FORMAT EMPTY=ZERO MISSING='.' MINCOLWIDTH=36 MAXCOLWIDTH=132 UNITS=POINTS
  /VLABELS VARIABLES=!rowvar DISPLAY=LABEL  
  /VLABELS VARIABLES=month valusd DISPLAY=NONE
  /TABLE !rowvar BY month > valusd [MEAN F40.0]
  /SLABELS VISIBLE=NO
  /CATEGORIES VARIABLES=!rowvar month ORDER=A KEY=VALUE EMPTY=EXCLUDE TOTAL=YES POSITION=BEFORE
  /TITLES
    TITLE='Average export value in USD by sitc and month.'.

!ENDDEFINE.
```

The macro is now defined and can be used. We do that by giving the name of the macro followed by the parameter with its value. Here we call it two times with different values:
```spss
tabul rowvar=sitcr4_1.
tabul rowvar=sitcr4_2.
```

Let us make the macro a little bit more flexible. We add two more parameters, one for the column variable and one for the measure variable:

```spss
DEFINE tabul (rowvar=!tokens(1)
             /colvar=!tokens(1)
             /measurevar=!tokens(1)
             )

CTABLES
  /FORMAT EMPTY=ZERO MISSING='.' MINCOLWIDTH=36 MAXCOLWIDTH=132 UNITS=POINTS
  /VLABELS VARIABLES=!rowvar DISPLAY=LABEL  
  /VLABELS VARIABLES=!colvar !measurevar DISPLAY=NONE
  /TABLE !rowvar BY !colvar > !measurevar [MEAN F40.0]
  /SLABELS VISIBLE=NO
  /CATEGORIES VARIABLES=!rowvar !colvar ORDER=A KEY=VALUE EMPTY=EXCLUDE TOTAL=YES POSITION=BEFORE
  /TITLES
    TITLE='Average export value in USD by sitc and month.'.

!ENDDEFINE.
```
When we run the macro, we add the new parameters and run three times with different values:

```spss
tabul rowvar=sitcr4_1 colvar=month measurevar=valusd.
tabul rowvar=month colvar=sitcr4_1 measurevar=valusd.
tabul rowvar=sitcr4_2 colvar=flow measurevar=value.
```

We enhance the macro some more by introducing the possibility to decide the measure type ourselves. This is added as a new parameter, called *stat*:

```spss
DEFINE tabul (rowvar=!tokens(1)
             /colvar=!tokens(1)
             /measurevar=!tokens(1)
             /stat=!tokens(1) 
             )

CTABLES
  /FORMAT EMPTY=ZERO MISSING='.' MINCOLWIDTH=36 MAXCOLWIDTH=132 UNITS=POINTS
  /VLABELS VARIABLES=!rowvar DISPLAY=LABEL  
  /VLABELS VARIABLES=!colvar !measurevar DISPLAY=NONE
  /TABLE !rowvar BY !colvar > !measurevar [!stat F40.0]
  /SLABELS VISIBLE=NO
  /CATEGORIES VARIABLES=!rowvar !colvar ORDER=A KEY=VALUE EMPTY=EXCLUDE TOTAL=YES POSITION=BEFORE
  /TITLES
    TITLE='Average export value in USD by sitc and month.'.

!ENDDEFINE.
```

Two executions of the macro with different parameter values:

```spss
tabul rowvar=sitcr4_1 colvar=month measurevar=valusd stat=sum.
tabul rowvar=country colvar=month measurevar=valusd stat=mean.
```

When we look at the table, we see that the title is not updated when we do changes. It is important that i reflects the actual content of the table. Hence, we add a title parameter to our macro:

```spss
DEFINE tabul (rowvar=!tokens(1)
             /colvar=!tokens(1)
             /measurevar=!tokens(1)
             /stat=!tokens(1)
             /title=!tokens(1) 
             )

CTABLES
  /FORMAT EMPTY=ZERO MISSING='.' MINCOLWIDTH=36 MAXCOLWIDTH=132 UNITS=POINTS
  /VLABELS VARIABLES=!rowvar DISPLAY=LABEL  
  /VLABELS VARIABLES=!colvar !measurevar DISPLAY=NONE
  /TABLE !rowvar BY !colvar > !measurevar [!stat F40.0]
  /SLABELS VISIBLE=NO
  /CATEGORIES VARIABLES=!rowvar !colvar ORDER=A KEY=VALUE EMPTY=EXCLUDE TOTAL=YES POSITION=BEFORE
  /TITLES
    TITLE=!title.

!ENDDEFINE.
```
Now ,we can run a table again:

```spss
tabul rowvar=sitcr4_1 
      colvar=month 
      measurevar=value
      stat=sum 
      title='Export value by sitc and month.'
.
```

We can make another macro. This time we want to make a macro that read an external csv file and saves it as an SPSS file. The parameters to change will be:

- Flow (export or import)
- Year
- Quarter

As all these parameters are parts of the file name, which is given within a string, we have to use the macro function *!concat* to add the string togehter. Furthermore, we have to use the *!quote* macro function to add quotes to the text. We also have to use slash (/) instead of backslash (\\) in the path of the filename. The syntax look like this:

```spss
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
```

Now, we can read the files for one year:

```spss
read_quarter flow=Export year=2018 quarter=1.
read_quarter flow=Export year=2018 quarter=2.
read_quarter flow=Export year=2018 quarter=3.
read_quarter flow=Export year=2018 quarter=4.
```

# Add files together
Files with the same attributes can be added together. The attributes that need to be the same is the variable names and variable types. The rows in all the added files will be concatenated dataset by dataset.

In this example we add the files for each quarter together to create a file for the whole year. But first, we make sure that the file for the first quarter is the active file:

```spss
DATASET CLOSE ALL.
GET FILE='data/Export_2018Q1.sav'.
ADD FILES FILE=*
         /FILE='data/Export_2018Q2.sav'
         /FILE='data/Export_2018Q3.sav'
         /FILE='data/Export_2018Q4.sav'
.
EXECUTE.
```

