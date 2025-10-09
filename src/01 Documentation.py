# ## XMPI documentation for data structure and catalouges

# +
# Documentation text for XMPI program
doc_text = """
=========================
XMPI Program Documentation
=========================

1. Folder Structure
-------------------
For the program to run correctly, ensure you have the following folders **at the same level as the program folder**:

- `../data` - Contains raw and processed data files
- `../cat` - Contains catalogue files, labels, and reference data
- `../src` - Contains all source scripts for processing and analysis
- `../publication` - Destination folder for generated reports, publications, and output files

2. Input File Structure
----------------------
The input CSV file for the T010 Read Trade Quarter script must have the following columns:

'flow', 
'year',
'month',
'comno',
'country',
'weight',
'quantity',
'unit',
'value',
'valUSD',
'itemid',
'exporterNUIT',
'ref',
'ItemID'

Example data format:

flow,year,month,ref,ItemID,comno,country,unit,weight,quantity,value,valUSD,itemno,exporterNUIT
E,2023,01,23329310076,156361478,49019900,IN,KG,187,200,9675,151,16,800000181
E,2023,01,23328776867,156103918,49019900,ZA,KG,1250,1250,12892,202,29,132650012
E,2023,01,23328525928,155990530,73181500,ZA,KG,3500,12393,46573,729,3,401175083
E,2023,01,23328659109,156051969,08012200,AE,KG,14320,14320,3230735,50575,1,400693498
E,2023,01,23328727979,156082953,72045000,AE,KG,250000,250000,6768300,105953,1,401000062
E,2023,01,23328735351,156086514,90171000,AO,PST,56,1,33132,519,2,400372314


3. Naming Convention
--------------------
Save the file as: **Flow - YYYY_QQ.csv**

- Flow: either **Export** or **Import**
- YYYY: 4-digit year
- QQ: Quarter (Q1, Q2, Q3, Q4)

**Example:** Export - 2024_Q1.csv

4. Notes
--------
- Variable separator: semi-colon (;)
- Decimal separator: comma (,)
- All numeric columns must not contain text
- Ensure correct country codes for Corigin and Cdestination

5. Tips & Common Errors
-----------------------
- Make sure the input CSV has the exact column order.
- Do not include empty rows at the top of the CSV file.
- Use UTF-8 encoding to avoid special character issues.
- Always check that catalogue files in `../cat` are updated.
- When running scripts, ensure current working directory is the program folder.


6. Catalogue & Auxiliary Files
------------------------------

The following files must be available in the `../cat` folder. They are used to map HS codes to classifications, configure special series, and support additional processing and comparisons.

1. HS_ISIC.xlsx
   --------------
   Maps HS codes to ISIC categories.

   Example:

   Code       ISIC
   ---------- -----
   01011000   A0142
   01011100   A0142
   01011900   A0142
   01012000   A0142

2. HS_SITC.xlsx
   --------------
   Maps HS codes to SITC categories.

   Example:

   Code       SITC
   ---------- -----
   01011000   0015
   01011100   0015
   01011900   0015
   01012000   0015

3. Chapter_Section.xlsx
   ---------------------
   Maps HS chapter codes to their respective sections.

   Example:

   Chapter   Section
   --------- -------
   01        I
   02        I
   03        I
   04        I
   05        I
   06        II

4. use_quantity.xlsx
   -----------------
   Lists HS codes for which **quantity** should be used instead of weight when calculating the unit value.

   Example:

   use_quantity
   ------------
   01011000
   01011100
   01011900
   01012000

   *Update if additional codes should use quantity instead of weight.*

5. special_series1.xlsx
   ---------------------
   Defines special series indices for selected commodities.

   Example:

   comno      special_serie
   ---------- --------------
   71023100   Diamond_index
   71081200   Diamond_index
   03047490   Fish_index
   27101230   Fuel_index

   *Update if you want to create additional special series.  
   Also update code in `T60 Index unchained` to generate the series.*

6. special_series2_total_without.xlsx
   -----------------------------------
   Defines "total without" series, i.e., indices excluding selected commodities.

   Example:

   comno      special_serie2
   ---------- -----------------------
   71023100   Total_without_diamonds
   71081200   Total_without_diamonds
   03047490   Total_without_fish
   27101230   Total_without_fuel

   *Update if you want to create additional "total without" series.  
   Also update code in `T60 Index unchained` to generate the series.*

7. compare_other_source.csv
   -------------------------
   Used to compare XMPI with other official statistics (e.g., CPI) in `T95`.

   Example:

   flow;source;comno;202101;202102;202103;...
   CPI;CPI;CPI - FOOD AND NON-ALCOHOLIC BEVERAGES;161.2;164.7;...

   *Update this file if you want to benchmark XMPI against other data sources.*

8. donors.csv
   -----------
   Contains time series data for selected commodities, used for comparison or donor input.

   Example:

   flow;source;comno;202101;202102;...
   1;PPI - B0721 - Mining of uranium;26121000;44;52;65;...

9. HS_revision_replacement.csv
   ----------------------------
   Defines replacement HS codes when revisions occur.

   Example:

   comno;comno_new;valid_from
   (empty template – update when HS revisions are implemented)

10. labels.csv
   ------------
   Contains labels for flows, sections, and other categorical variables.

   Example:

   category,code,label
   flow,1,Import
   flow,2,Export
   section,I,Live animals; animal products (Chapters 01–05)
   section,V,Mineral products (Chapters 25–27)


"""



# Save the documentation as a text file
with open("XMPI_documentation.txt", "w", encoding="utf-8") as f:
    f.write(doc_text)

print("Documentation file created: XMPI_documentation.txt")


# +
# Step 2: Ask user if they want to read it
answer = input("Do you want to read the XMPI documentation for datastructure and catalogues? (yes/no): ").strip().lower()

if answer == "yes":
    try:
        with open("XMPI_documentation.txt", "r", encoding="utf-8") as f:
            print("\n" + "="*50 + "\n")
            print(f.read())
            print("\n" + "="*50 + "\n")
    except FileNotFoundError:
        print("Documentation file not found. Please check the path.")
else:
    print("Documentation not displayed.")
