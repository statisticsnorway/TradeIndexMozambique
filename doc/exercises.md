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