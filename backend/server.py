import json
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS, cross_origin
from jira import JIRA
from table_classes import bundle_rows, audit_rows
import pandas as pd
import os
from jira_functions import *
from io import BytesIO, StringIO
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app, supports_credentials=True, allow_headers='Content-Type')

bundle_rows_incl = []
bundle_rows_off = []
bundle_rows_data = []
bundle_rows_org = []
phire_audit_list = []
fiscal_year_1 = '2022'
fiscal_year_2 = '2023'
test_jira = ''
report_title = ''

bundle_dates = ["11/01/2021", "05/02/2021", "10/03/2021", "04/04/2021", "09/05/2021", "02/07/2021",
 "03/07/2021", "08/08/2021", "01/10/2021", "12/13/2021", "11/14/2021", "10/18/2021", "09/24/2021",
  "07/25/2021", "12/27/2021", "06/27/2021", "11/29/2021", "05/30/2021", "01/10/2022", "01/24/2022",
  "02/07/2022", "02/21/2022", "03/07/2022", "03/21/2022", "04/04/2022", "04/18/2022", "05/02/2022",
  "05/16/2022", "05/31/2022", "06/13/2022", "06/27/2022", "07/11/2022", "07/25/2022", "08/08/2022",
  "08/22/2022", "09/06/2022", "09/23/2022"]

jira_obj = JIRA(os.getenv("HOST_URL"),basic_auth=(os.getenv("JIRA_USER_ID"),os.getenv("JIRA_API_KEY")))

def processInfo(issue,title):
    global test_jira
    test_jira = issue
    global report_title
    report_title = title
    print('JIRA ISSUE:', test_jira)
    print("BUNDLE NAME:", report_title)

def processOrg(startDate, endDate, type):
    #Creating a search query of organizational update
    org_issues = jira_obj.search_issues('(labels = FY'+fiscal_year_1+'OrgDept OR labels = FY'+fiscal_year_2+'OrgDept) AND (updated >= ' + startDate + ' AND updated <= ' + endDate + ') ORDER BY updated DESC')
    issue_count = 0
    if(len(org_issues) > 0):
        for issue in org_issues:
            row = {'CR':'N/A - No PHIRE CR', 'Tracking #':issue.key, 'Target DB':'HRS', 'Migrated On':jira_obj.issue(issue.key).fields.updated, 'Migrated By':'N/A', 'CR Type':'N/A'}
            ser = pd.Series(data=row, index=['CR', 'Tracking #', 'Target DB', 'Migrated On', 'Migrated By', 'CR Type'])
            result = process_jira(jira_obj, ser, 'Org Dept Update')
            if(result == None):
                print("Problem with ", row["Tracking #"])
                continue
            else:
                bundle_rows_org.append(result.toList())
            issue_count += 1
            row['Migrated On'] = row['Migrated On'].replace("T", " ")[:19]
            phire_result = audit_rows(row['CR'], row['Tracking #'], row['Target DB'], row['Migrated On'], row['Migrated By'], row['CR Type'], 'ORG_DEPT_UPDATE')
            phire_audit_list.append(phire_result.toList())
            print("Processing ",type + ": ",issue_count,"/",len(org_issues), "  Included in Bundle: ", len(bundle_rows_incl), 
            " Off-Bundle: ", len(bundle_rows_off), " Data Update: ", len(bundle_rows_data), " Org Dept Update: ", len(bundle_rows_org))
    else:
        print("NO ORGANIZATION DEPARTMENT UPDATE AT THIS TIME")

def processCSV(data, type):
    count = 0
    #remove the headers 
    data.pop(0)
    df = pd.DataFrame(data,columns=['CR', 'Tracking #', 'Target DB', 'Migrated On', 'Migrated By', 'CR Type'])
    #removing testing data
    if 'TEST' in df.values:
        df.drop(df[df["Tracking #"] == 'TEST'].index, inplace=True)

    #segregating bundle data into lists based on on-bundle, off-bundle, data update
    total_count = df.shape[0]
    for index, row in df.iterrows():
        #print(row["Tracking #"])
        if row["Migrated On"].split(" ")[0] in bundle_dates:
            result = process_jira(jira_obj, row, "Included in Bundle")
            if(result == None):
                print("Problem with ", row["Tracking #"])
                continue
            else:
                bundle_rows_incl.append(result.toList())
        elif row["CR Type"] == "HFIX":
            result = process_jira(jira_obj, row, "Data Update")
            if(result == None):
                print("Problem with ", row["Tracking #"])
                continue
            else:
                bundle_rows_data.append(result.toList())
        else:
            result = process_jira(jira_obj, row, "Off-bundle")
            if(result == None):
                print("Problem with ", row["Tracking #"])
                continue
            else:
                bundle_rows_off.append(result.toList())
        count += 1
        src_query = 'UW_MIGR_HISTORY_AUDIT_LAB' if type == 'Migration Data' else 'UW_SQL_HISTORY_AUDIT_LAB'
        phire_result = audit_rows(row['CR'], row['Tracking #'], row['Target DB'], row['Migrated On'], row['Migrated By'], row['CR Type'], src_query)
        phire_audit_list.append(phire_result.toList())
        print("Processing ",type,": ",count,"/",total_count, "  Included in Bundle: ", len(bundle_rows_incl), 
        " Off-Bundle: ", len(bundle_rows_off), " Data Update: ", len(bundle_rows_data), " Org Dept Update: ", len(bundle_rows_org))        

@app.route('/form', methods=['POST'])
@cross_origin(supports_credentials=True)
def processForm():
    if request.method == 'POST':
        processInfo(request.json['issue'], request.json['title'])
        #Process Migration Data
        if(request.json['isMigr'] == 'on' and 'fileMigr' in request.json.keys()):
            processCSV(request.json['fileMigr']['data'], "Migration Data")
        #Process SQL Data
        if(request.json['isSQL'] == 'on' and 'fileSQL' in request.json.keys()):
            processCSV(request.json['fileSQL']['data'], "SQL Data")
        #Process Organization Department Update Data
        if(request.json['inclOrg'] == 'on'):
            processOrg(request.json["startDate"], request.json["endDate"], "Org Dept Update")
        return jsonify({'process':'done'})

@app.route('/stat', methods=['GET'])
@cross_origin(supports_credentials=True)
def sendStats():
    final_df = createBundleDF(bundle_rows_incl, bundle_rows_off, bundle_rows_data, bundle_rows_org)
    teamStat = getTeamStat(final_df)
    typeStat = getTypeStat(final_df)
    categoryStat = getCategoryStat(final_df)
    bundleStat = {
        'Included':len(bundle_rows_incl),
        'Off-Bundle':len(bundle_rows_off),
        'Data-Update':len(bundle_rows_data),
        'Organization':len(bundle_rows_org),
    }
    final_stat = {
        'Bundle':bundleStat,
        'Team':teamStat,
        'Category':categoryStat,
        'Type':typeStat
    }
    return jsonify(final_stat)

@app.route('/download') 
@cross_origin(supports_credentials=True)
def download_excel():
    out_stream = BytesIO()
    export_bundle(out_stream, bundle_rows_incl, bundle_rows_off, bundle_rows_data, bundle_rows_org, phire_audit_list)
    out_stream.seek(0)
    return send_file(out_stream, download_name="BundleReport.xlsx", as_attachment=True)

@app.route('/upload')
@cross_origin(supports_credentials=True)
def upload_report():
    export_bundle(report_title+".xlsx",bundle_rows_incl, bundle_rows_off, bundle_rows_data, bundle_rows_org, phire_audit_list)
    print('Test JIRA: ',test_jira)
    comment_header = 'The ' + report_title + ' has been attached and the bundle includes:\n'
    comment_included = str(len(bundle_rows_incl)) + ' On Bundle Items\n'
    comment_off = str(len(bundle_rows_off)) + ' Off Bundle Items\n'
    comment_org = str(len(bundle_rows_org)) + ' Organizational Department Updates\n'
    comment_data = str(len(bundle_rows_data)) + ' Data Updates (SQL)\n'
    comment_footer = str(len(bundle_rows_incl) + len(bundle_rows_off) + len(bundle_rows_data) + len(bundle_rows_org)) + " items in total went to HRS/EPM."
    jira_comment = comment_header + comment_included + comment_off + comment_org + comment_data + comment_footer
    jira_obj.add_comment(test_jira, jira_comment)
    jira_obj.add_attachment(issue=test_jira, attachment=report_title+".xlsx")
    return jsonify({'process':'done'})

@app.route('/')
@cross_origin(supports_credentials=True)
def test():
    return("Hello React")

if __name__ == "__main__":
    app.run(debug=True)