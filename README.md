# Import Alamut Export Data to the Db

## Steps to replicate the final.txt input file
- Load in the file in Excel
- filter out all columns where the last assembly is not GRCh38 or GRCH37
- filter for entries which do not have a ????-??-??T timestamp in the column following Notes
- extract all columns including Notes column
- Now switch to the filtered out columns
- Copy the all columns except Notes to the same file
- Copy them to another file
- Append all data until the timestamp
- Remove timestamp, timestamp, type column following the data
- Copy the data to the final sheet
- Replace all german characters (äüöß) with its counterpart
- Create a final.txt as tab seperated export from Excel 
- run the main script

## Output
The script will generate a csv file containing all rows of the final.txt (input file) where the post request did not work. This file can mostly be ignored as it seems to contain duplicate entries which somehow showed up.
