# SPSS Exercises
These exercises is using data from the foreign trade in INE Mozambique. The data is originally stored in Excel spreadsheets. 
## Read csv files
1. Use the menus to import the 'Export - 2019_XPMI.csv' file. It is a semicolon delimited file with comma as decimal sign. The csv file has the first row as a header. Remember to paste the syntax!
2. Copy the pasted program and change the copy so that these variables will be string variables (the length is given in the brackets): flow (1), year (4), month (2), ref (11), ItemID (8), comno (8), country (2), exporterNUIT (9). Omit the *exportername* column from the import.

## Frequencies
1. Make a frequency table for the *flow*, *unit* and *country* variables
2. Make a temporary selection for the country 'NO' and make a frequency table for *comno*.

## Descriptives
1. Make a descriptives table for the variables *weight*, *quantity*, *value* and *valusd*.
2. Make the same table, but select these statistics: sum mean min max stddev
3. Make a descriptives tables for the same variables, but only for the country 'ZA'

### Means
1. Make a table with *valusd* as a measure variable grouped by *unit*.
2. Make the same table as above, but choose these statistics:  sum mean min max stddev
3. Make a table as above but add the *value* variable as a measure variable
4. Make a table with *valusd* as a measure variable grouped by *comno* for the country 'LS'


## Value labels
1. Create value labels for *country* by using the spreadsheet 'Country Catologue_XPMI.xlsx'. Use the concatenar function in Excel to create the a column that follows the syntax rules for value labels in SPSS. Then copy the new column into an SPSS syntax.
2. Create a frequency table for the *country* variable. Are there any countries that ended up without a country name?

``` excel
=CONCATENAR("'";A2;"'";" '";A2;" ";D2;"'")  (Portuguese)
```

## New variables
1. Create a new string variable called *hs4* that contains the first 4 characters of the *comno* variable
2. Create a new string variable called *hs2* that contains the first 2 characters of the *hs4* variable. Create a frequency table for the new *hs2* variable.
3. Create a new numeric variable called *price_usd* that calculates the price per kr in usd. 
4. Create a descriptives table for the new *price_usd* variable. 
5. Make a means table for *price_usd* by *hs2*.

## Format variables
1. Format the variable *price_usd* with total width of 13, including 2 decimals.

## Save datasets
1. Save the data in the data folder as 'export_2019.sav'.
2. Open a new syntax window and add a `cd` command that points to your main folder for the Foreign trade system. Save the syntax as 'start.sps' in the src folder.
3. Change the path from absolute to relative in the save command from the first exercise under the Save datasets chapter.

## Aggregation
1. Aggregate the dataset to *flow*, *year* and *country*. Calculate the sum, mean and median of the variable *value* as *value_sum*, *value_mean* and *value_median*. 
2. Reopen the SPSS dataset. Then add the aggregated variables *price_usd_max*, *price_usd_min*, *price_usd_median*, *price_usd_sd* and *price_usd_mean* as the max, min, median, standard deviation and mean of the *price_usd* variable. Also add the *no_of_months* variable as the count of rows. The aggregation level is *flow*, *year*, *comno* and *country*.
3. Add the sum of the valusd as *t_sum_valusd* by the aggregation level *flow* and *year*.

## Duplicates
1. Import the export for 2020 quarter 1.
2. Format the variables *weight quantity value valusd* with the f14 format.
3. Check for duplicates by the variables *flow year month comno ref ItemID country*. Remember to keep a variable that gives information if a row is first within the group or not, call it *first _id*
4. Make a frequency table for the variable *first _id*.
5. Delete the variable *first _id*
6. Save the dataset as 'data/export_2020Q1.sav'
7. Import the spreadsheet 'data\Commodities_Catalogue_XPMI.xlsx'
8. Delete all variables except *comno, sitcr4_1* and *sitcr4_2*
9. Rename the variables *sitcr4_1* to *sitc1* and *sitcr4_2* to *sitc2*.
10. Check for duplicates by comno the same way as for the previous dataset
11. Delete the *first_id* variable
12. Save the dataset as 'data\commodity_sitc.sav'

## Match files
1. Match the file 'data/export_2020Q1.sav' and 'data\commodity_sitc.sav' by comno. The last dataset is a table dataset. Create a variable called *found_sitc* which is true (1)when sitc codes are found in the table and false (0) when they are not found 
2. Make a frequency table for the variables *found_sitc* and *sitc1*.
3. Delete the variable *found_sitc*

## Tabulation
1. Make a table from the above dataset *unit* as a nominal variable in the rows and *month* as a nominal variable in the columns. Count number of rows.
2. Do the same table as above, but count the average of the variable *valusd*.
3. Expand the table with the count and sum of the variable *valusd*.
4. Add a title to the table and remove the labels from the *unit* and *month* variables.
5. Create a table for *country* where there is one row for each of the largest by valusd. The other countries should be gathered in a *other* group. To find the 10 largest we can use the `aggregate` command with country as the break variable. Then we can sort the cases by descending *valusd*. Then we select the first 10 cases by using the internal variable *$casenum* in a `select if` command. Then we sort the cases by *country* and save the dataset with a new name. Now it is time to match the two files together and mark when big countries are found. If a big country is found we recode the country to ZZ. Finally, we can make the table with `ctables` and order the countries by descending *valusd*.
## Macros
1. Close all datasets and open the dataset export_2020Q1.sav in the data fodler.
2. Make a temporary selection where country is SE and NO (use the `any` function). Make a means table for the temporary selected data where you use *valusd* as the measure variable, *comno* as the category variable and count the statistics *count*, *sum*, *min*, *max* and *mean*.
3. Set the mprint option to on.
4. Create a macro called *selected_means* where you define the value of country as a macro variable that you call *value*. Replace the actual value in the `any` function with the macro variable *!value*. Call the macro with the value 'SE'.
5. Call the macro once more, now with value 'NO'.
6. Copy the macro and enhance it so it can take more than one country as a parameter to the `any` function. To do that you can replace the !TOKENS=(1) with !ENCLOSE('[',']') when you define the macro. When you call the macro you put the values in brackets like this: ['NO','SE'], to select the countries 'NO' and 'SE'.
7. Call the macro with the countries 'DK' and 'FI'.
8. Add one more parameter, called *selection_variable*. It shall replace the variable *country* in the macro. This will make it possible for us to both choose which variable to select on and the values to select. Call the macro where you select the values 'NO' and 'SE' from the variable *country*.
9. Call the macro again, now select the value 'L' from the *unit* variable.
10. Call the macro once more, now select the values 'L' and 'LI' from the *unit* variable.
11. Do three more enhancements to the macro. The first is to make it possible to choose which measure variable to use so that we don't always have to get the *valusd* variable. Call the macro variable *measure_variable*. The second is to make it possible to choose the category variable so we will not be stuck with the *comno* variable there. Call the macro variable *by_variable*. The third is to add a title which includes the selection variable with its values. To do that we will use the `title` command and the `!concat` function. Call the macro with *unit* as the selection variable with its values 'L' and 'LI', the measure variable *weight* and the catecory variable *month*.
12. Call the macro with *comno* as the selection variable with its values '05119990' and '07049000', the measure variable *valusd* and the catecory variable *country*.