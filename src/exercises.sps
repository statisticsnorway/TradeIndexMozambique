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

FREQUENCIES country.


STRING hs4 (a4).
COMPUTE hs4 = CHAR.SUBSTR(comno,1,4).
STRING hs2 (a2).
COMPUTE hs2 = CHAR.SUBSTR(hs4,1,2).
EXECUTE.
FREQUENCIES hs2.

COMPUTE price_usd = valusd / weight.
DESCRIPTIVES price_usd.

MEANS price_usd by hs2.

FORMATS price_usd (F13.2).

SAVE OUTFILE='C:\Users\krl\TradeIndexMozambique\data\export_2019.sav'.

SAVE OUTFILE='data\export_2019.sav'.


AGGREGATE 
    /OUTFILE=* 
    /BREAK flow year country
    /value_sum = SUM(value)
    /value_mean = MEAN(value)
    /value_median = MEDIAN(value)
    .

DATASET CLOSE ALL.
GET FILE='data\export_2019.sav'.

AGGREGATE 
    /OUTFILE=* MODE=ADDVARIABLES
    /BREAK flow year comno country
    /no_of_rows = N()
    /price_usd_max = MAX(price_usd)
    /price_usd_min = MIN(price_usd)
    /price_usd_median = MEDIAN(price_usd)
    /price_usd_sd = SD(price_usd)
    /price_usd_mean = MEAN(price_usd)
    .

AGGREGATE 
    /OUTFILE=* MODE=ADDVARIABLES
    /BREAK flow year 
    /t_sum_valusd = SUM(valusd)
    .


PRESERVE.
SET DECIMAL DOT.

GET DATA  /TYPE=TXT
  /FILE="data\Export - 2020_XPMI_Q1.csv"
  /ENCODING='UTF8'
  /DELCASE=LINE
  /DELIMITERS=","
  /ARRANGEMENT=DELIMITED
  /FIRSTCASE=2
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

FORMATS weight quantity value valusd (f14).

SORT CASES BY flow year month comno ref ItemID country.

MATCH FILES FILE=*
           /BY flow year month comno ref ItemID country
           /FIRST = first_id
           .

FREQUENCIES first_id.

DELETE VARIABLES first_id.

SAVE OUTFILE='data/export_2020Q1.sav'.

DATASET CLOSE ALL.
GET DATA
  /TYPE=XLSX
  /FILE='data\Commodities_Catalogue_XPMI.xlsx'
  /SHEET=name 'Pauta Grupos_2023_'
  /CELLRANGE=FULL
  /READNAMES=ON
.
EXECUTE.

DELETE VARIABLES DescriçãoSH8 TO Descriptionsitcr4_3 Descriptionsitcr4_2 Descriptionsitcr4_1 TO becno.
EXECUTE.

RENAME VARIABLES sitcr4_1 = sitc1 sitcr4_2 = sitc2.

SORT CASES BY comno.
MATCH FILES FILE=*
           /BY comno
           /FIRST = first_id
           .

FREQUENCIES first_id.

DELETE VARIABLES first_id.

SAVE OUTFILE='data\commodity_sitc.sav'.

DATASET CLOSE ALL.
GET FILE='data/export_2020Q1.sav'.

SORT CASES BY comno.
MATCH FILES FILE=*
           /TABLE='data\commodity_sitc.sav'
           /IN=found_sitc
           /BY comno
           .

FREQUENCIES found_sitc sitc1.
DELETE VARIABLES found_sitc.


CTABLES
  /VLABELS VARIABLES=unit month DISPLAY=LABEL
  /TABLE unit [COUNT F40.0] BY month
  /CATEGORIES VARIABLES=unit month ORDER=A KEY=VALUE EMPTY=EXCLUDE
.

CTABLES
  /VLABELS VARIABLES=unit month valUSD DISPLAY=LABEL
  /TABLE unit BY month > valUSD [MEAN]
  /CATEGORIES VARIABLES=unit month ORDER=A KEY=VALUE EMPTY=EXCLUDE
.


CTABLES
  /VLABELS VARIABLES=unit month valUSD DISPLAY=LABEL
  /TABLE unit BY month > valUSD [COUNT F40.0, MEAN F40.0, SUM F40.0]
  /CATEGORIES VARIABLES=unit month ORDER=A KEY=VALUE EMPTY=EXCLUDE
.



CTABLES
  /VLABELS VARIABLES=unit month valUSD DISPLAY=NONE
  /TABLE unit BY month > valUSD [COUNT F40.0, MEAN F40.0, SUM F40.0]
  /CATEGORIES VARIABLES=unit month ORDER=A KEY=VALUE EMPTY=EXCLUDE
  /TITLES
    TITLE='Value in USD by unit and month'.


AGGREGATE 
    /OUTFILE=* 
    /BREAK country
    /valusd_sum = SUM(value)
    .

SORT CASES BY valusd_sum (D).

SELECT IF ($casenum <=10).
EXECUTE.
SORT CASES BY country.

SAVE OUTFILE='data/big10.sav' / keep=country.

DATASET CLOSE ALL.
GET FILE='data/export_2020Q1.sav'.

SORT CASES BY country.
MATCH FILES FILE=*
           /TABLE='data\big10.sav'
           /IN=found_big
           /BY country
           .
EXECUTE.

IF (found_big = 0) country='ZZ'.

FREQUENCIES country.

CTABLES
  /VLABELS VARIABLES=country month valUSD DISPLAY=NONE
  /TABLE country BY month > valUSD [SUM F40.0]
  /SLABELS VISIBLE=NO
  /CATEGORIES VARIABLES=country ORDER=D KEY=SUM (valUSD) EMPTY=EXCLUDE TOTAL=YES POSITION=BEFORE
  /CATEGORIES VARIABLES=month ORDER=A KEY=VALUE EMPTY=EXCLUDE TOTAL=YES POSITION=BEFORE
  /TITLES
    TITLE='Value in USD for 10 largest export countries, by month. '.

DATASET CLOSE ALL.
GET FILE='data/export_2020Q1.sav'.

TEMPORARY.
SELECT IF (any(country,'SE','NO')).
MEANS valusd BY comno /CELLS=count sum min max mean .

SET MPRINT = on.

DEFINE selected_means (value=!tokens(1))

TEMPORARY.
SELECT IF (any(country,!value)).
MEANS valusd BY comno /CELLS=count sum min max mean .

!ENDDEFINE.

selected_means value='SE'.
selected_means value='NO'.

DEFINE selected_means (values=!ENCLOSE('[',']'))

TEMPORARY.
SELECT IF (any(country,!values)).
MEANS valusd BY comno /CELLS=count sum min max mean .

!ENDDEFINE.

selected_means values=['NO','SE'].
selected_means values=['DK','FI'].

DEFINE selected_means (selection_variable=!TOKENS(1),
                      /values=!ENCLOSE('[',']'))

TEMPORARY.
SELECT IF (any(!selection_variable,!values)).
MEANS valusd BY comno /CELLS=count sum min max mean .

!ENDDEFINE.

selected_means selection_variable=country values=['NO','SE'].
selected_means selection_variable=unit values=['L'].
selected_means selection_variable=unit values=['L','LI'].

SET MPRINT = off.
DEFINE selected_means (selection_variable=!TOKENS(1),
                      /values=!ENCLOSE('[',']')
                      /measure_variable=!TOKENS(1),
                      /by_variable=!TOKENS(1)
                      )

TEMPORARY.
SELECT IF (any(!selection_variable,!values)).
TITLE !CONCAT('Table selected on ',!selection_variable,': ',!values,'.').
MEANS !measure_variable BY !by_variable /CELLS=count sum min max mean .

!ENDDEFINE.

selected_means 
    selection_variable=unit 
    values=['L','LI']
    measure_variable=weight
    by_variable=month
    .

selected_means 
    selection_variable=comno 
    values=['05119990','07049000']
    measure_variable=valusd
    by_variable=country
    .


