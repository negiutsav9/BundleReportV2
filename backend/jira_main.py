#import statements
from jira import JIRA
from table_classes import bundle_rows
import pandas as pd
import os
import glob
from jira_functions import *
from dotenv import load_dotenv

load_dotenv()

bundle_rows_incl = []
bundle_rows_off = []
bundle_rows_data = []
bundle_rows_org = []
bundle_rows_regr = []

bundle_dates = ["11/01/2021", "05/02/2021", "10/03/2021", "04/04/2021", "09/05/2021", "02/07/2021",
 "03/07/2021", "08/08/2021", "01/10/2021", "12/13/2021", "11/14/2021", "10/18/2021", "09/24/2021",
  "07/25/2021", "12/27/2021", "06/27/2021", "11/29/2021", "05/30/2021"]

#setting up jira api
jira_obj = JIRA(os.getenv("HOST_URL"),basic_auth=(os.getenv("JIRA_USER_ID"),os.getenv("JIRA_API_KEY")))

#saving phire data in a dataframe
csv_files = glob.glob("../PhireData_2021/*.csv")
phire_df = pd.concat((pd.read_csv(file) for file in csv_files))

#removing the test
if 'TEST' in phire_df.values:
    phire_df.drop(phire_df[phire_df["Tracking #"] == 'TEST'].index, inplace=True)

#processing phire dataframe

#segregating bundle data into lists based on on-bundle, off-bundle, data update
total_count = phire_df.shape[0]
count = 0
for index, row in phire_df.iterrows():
    #print(row["Tracking #"])
    if row["Migrated On"].split(" ")[0] in bundle_dates:
        result = process_jira(jira_obj, row, "Included in Bundle")
        if(result == None):
            print("Problem with ", row["Tracking #"])
            continue
        else:
            bundle_rows_incl.append(result)
    elif row["CR Type"] == "HFIX":
        result = process_jira(jira_obj, row, "Data Update")
        if(result == None):
            print("Problem with ", row["Tracking #"])
            continue
        else:
            bundle_rows_data.append(result)
    else:
        result = process_jira(jira_obj, row, "Off-bundle")
        if(result == None):
            print("Problem with ", row["Tracking #"])
            continue
        else:
            bundle_rows_off.append(result)
    count += 1
    print(count,"/",total_count, "  Included in Bundle: ", len(bundle_rows_incl), 
     " Off-Bundle: ", len(bundle_rows_off), " Data Update: ", len(bundle_rows_data))

#TODO: Extracting org_dept update using advanced search and within the range of given dates

#exporting the saved data into the excel workbook
#converting the classes stored into list
for index in range(0, len(bundle_rows_incl)):
    bundle_rows_incl[index] = bundle_rows_incl[index].toList()
for index in range(0, len(bundle_rows_data)):
    bundle_rows_data[index] = bundle_rows_data[index].toList()
for index in range(0, len(bundle_rows_off)):
    bundle_rows_off[index] = bundle_rows_off[index].toList()

final_df = createBundleDF(bundle_rows_incl, bundle_rows_off, bundle_rows_data, bundle_rows_org, bundle_rows_regr)
print(getTeamStat(final_df))
print(getTypeStat(final_df))
print(getCategoryStat(final_df))
export_bundle(bundle_rows_incl, bundle_rows_off, bundle_rows_data, bundle_rows_org)