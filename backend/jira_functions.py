from turtle import bgcolor
from table_classes import bundle_rows
import xlsxwriter
import pandas as pd
from io import BytesIO

bundle_header = ["JIRA #", "Summary", "Team", "Bundle Status", "JIRA Status", "Assignee",
 "Reporter", "Priority", "Sub-Priority", "Category", "Prioritization Date", "HRS/EPM", "HRQA/EPQAS Date",
 "PHIRE CR#", "CR Type", "HRS/EPM Date", "Off Bundle Reason", "Project Association"]

audit_header = ["Phire CR Number", "JIRA Tracking #", "Target DB", "Migrated On", "Migrated By", "CR Type", "Query"]

def classify_category(project_title):
    project_type = ""
    if(project_title == "No"):
        project_type = "Ops"
    else:
        project_type = "Project"
    return project_type

def classify_crtype(phire_cr_type):
    bundle_crtype = ""
    if(phire_cr_type == "HFIX"):
        bundle_crtype = "Data Update/SQL"
    elif(phire_cr_type == "SCRP"):
        bundle_crtype = "Config/.dms"
    elif(phire_cr_type == "SCRT"):
        bundle_crtype = "Security"
    elif(phire_cr_type == "CODE"):
        bundle_crtype = "Code/Object"
    elif(phire_cr_type == "N/A"):
        bundle_crtype = "N/A (Configuration)"
    return bundle_crtype


def process_jira(jira_obj, row, bundle_status):
    try:
        issues = jira_obj.issue(row["Tracking #"])
    except:
        return None

    #processing jira-id of the JIRA
    try:
        jira_code = issues.key if issues.key is not None else "-"
    except:
        jira_code = "-"

    #processing summary (title) of the JIRA 
    try:
        summary = issues.fields.summary if issues.fields.summary is not None else "-"
    except:
        summary = "-"

    #processing team responsible for the JIRA 
    try:
        team = issues.fields.customfield_10085.value if issues.fields.customfield_10085 is not None else "-"
    except:
        team = "-"

    #processing bundle status of JIRA given in JIRA
    try:
        jira_status = issues.fields.status.name if issues.fields.status is not None else "-"
    except:
        jira_status = "-"
    
    try:
        assignee = issues.fields.assignee.displayName if issues.fields.assignee is not None else "-"
    except:
        assignee = "-"

    try:
        reporter = issues.fields.creator.displayName if issues.fields.creator is not None else "-"
    except:
        reporter = "-"
    
    try:
        priority = issues.fields.priority.name if issues.fields.priority is not None else "-"
    except:
        priority = "-"

    try:
        sub_priority = issues.fields.customfield_10332.value if issues.fields.customfield_10332 is not None else "-"
    except:
        sub_priority = "-"

    try:
        category = classify_category(issues.fields.customfield_10482.value) if issues.fields.customfield_10482 is not None else "-"
    except:
        category = "-"

    try:
        priortization_date = issues.fields.customfield_13090 if issues.fields.customfield_13090 is not None else "-"
    except:
        priortization_date = '-'
    
    try:
        isHRS = row['Target DB']
    except:
        isHRS = "-"

    try:
        hrqa_epqas_date = "-"
        comments = issues.fields.comment.comments
        for comment in comments:
            if ('Team: HRS Migration' in comment.author.displayName or 'jira_doit' in comment.author.displayName) and ('to HRQA / HRTRN is complete' in comment.body or 'EPQAS is complete' in comment.body):
                hrqa_epqas_date = comment.created[:10]
                print(jira_code,hrqa_epqas_date)
        if bundle_status=='Org Dept Update':
            hrqa_epqas_date = 'N/A'
    except:
        hrqa_epqas_date = "-"

    try:
        if isHRS == "HRS" and bundle_status != 'Org Dept Update':
            phire_cr = str("HRS-" + row["CR"])
        elif isHRS == "EPM":
            phire_cr = str("EPM-" + row["CR"]) 
        else:
            phire_cr = row["CR"]
    except:
        phire_cr = "-"

    try:
        off_reason = issues.fields.customfield_11693.value if issues.fields.customfield_11693 is not None else "-"
        if(bundle_status != 'Included in Bundle'):
            off_reason = '-'
    except:
        off_reason = "-"
    
    try:
        project_association = issues.fields.customfield_13390.value if issues.fields.customfield_13390 is not None else "-"
    except:
        project_association = "-"
    
    cr_type = classify_crtype(row["CR Type"])
    hrs_epm_date = row["Migrated On"].split(" ")[0] if bundle_status != "Org Dept Update" else row["Migrated On"].split("T")[0]

    new_bundle_obj = bundle_rows(jira_code, summary, team, bundle_status, jira_status, assignee, reporter, priority,
     sub_priority, category, priortization_date, isHRS, hrqa_epqas_date, phire_cr, cr_type, hrs_epm_date, off_reason,
     project_association)
    
    return new_bundle_obj

def export_bundle(out_stream = 'BundleList.xlsx', bundle_rows_incl = [], bundle_rows_off = [], bundle_rows_data = [], bundle_rows_org = [], phire_audit_list=[]):
    workbook = xlsxwriter.Workbook(out_stream)

    #Adding bundle report worksheet
    worksheet_br = workbook.add_worksheet('Bundle Report')

    #adjusting the cell width and format
    cell_format_table_header = workbook.add_format({"font_name":'Arial', "font_size":9, "align":"center",
     "valign":"vcenter", "border":1, 'text_wrap':True, 'bold':True})

    cell_format_included = workbook.add_format({"font_name":'Arial', "font_size":9, "align":"center",
     "valign":"vcenter", "border":1, 'text_wrap':True, 'bg_color':'white'})

    cell_format_off = workbook.add_format({"font_name":'Arial', "font_size":9, "align":"center",
     "valign":"vcenter", "border":1, 'text_wrap':True, 'bg_color':'yellow'})

    cell_format_data = workbook.add_format({"font_name":'Arial', "font_size":9, "align":"center",
     "valign":"vcenter", "border":1, 'text_wrap':True, 'bg_color':'8ea9db'})

    cell_format_org = workbook.add_format({"font_name":'Arial', "font_size":9, "align":"center",
     "valign":"vcenter", "border":1, 'text_wrap':True, 'bg_color':'a7f432'})

    #cell_format_title = workbook.add_format({"font_name":'Arial', "font_size":14})

    worksheet_br.set_column(0, 0, 15)
    worksheet_br.set_column(1, 1, 50)
    worksheet_br.set_column(2, 6, 22)
    worksheet_br.set_column(7, 8, 10)
    worksheet_br.set_column(9,9,10)
    worksheet_br.set_column(10,10,15)
    worksheet_br.set_column(11,11,10)
    worksheet_br.set_column(12,16,20)
    worksheet_br.set_column(17,17,30)

    #writing the header row of the bundle list documentation
    for column_index in range(0, len(bundle_header)):
        worksheet_br.write(0, column_index, bundle_header[column_index], cell_format_table_header)
    
    row_index = 1
    #writing the jira included in bundle and formatting the color background of these cells
    for row in bundle_rows_incl:
        worksheet_br.set_row(row_index,25)
        for column_index in range(0, len(row)):
            worksheet_br.write(row_index, column_index, row[column_index], cell_format_included)
        row_index += 1
    #writing the jira in off-bundle category and formatting the color background of these cells
    for row in bundle_rows_off:
        worksheet_br.set_row(row_index,25)
        for column_index in range(0, len(row)):
            worksheet_br.write(row_index, column_index, row[column_index], cell_format_off)
        row_index += 1
    #writing the jira in org dept update category and formatting the color background of these cells
    for row in bundle_rows_org:
        worksheet_br.set_row(row_index,25)
        for column_index in range(0, len(row)):
            worksheet_br.write(row_index, column_index, row[column_index], cell_format_org)
        row_index += 1
    #writing the jira in data update category and fomatting the color background of these cells
    for row in bundle_rows_data:
        worksheet_br.set_row(row_index,25)
        for column_index in range(0, len(row)):
            worksheet_br.write(row_index, column_index, row[column_index], cell_format_data)
        row_index += 1
    
    #Adding phire audit worksheet
    worksheet_pa = workbook.add_worksheet('Phire Audit')

    cell_format_header = workbook.add_format({"font_name":'Arial', "font_size":11, "align":"center",
     "valign":"vcenter", "border":1, 'text_wrap':True, 'bold':True})

    cell_format_audit = workbook.add_format({"font_name":'Arial', "font_size":9, "align":"center",
     "valign":"vcenter", "border":1, 'text_wrap':True, 'bg_color':'b5e2ff'})

    worksheet_pa.set_column(0,1,20)
    worksheet_pa.set_column(2,2,10)
    worksheet_pa.set_column(3,3,20)
    worksheet_pa.set_column(4,4,15)
    worksheet_pa.set_column(5,5,10)
    worksheet_pa.set_column(6,6,30)

    for column_index in range(0, len(audit_header)):
        worksheet_pa.write(0, column_index, audit_header[column_index], cell_format_header)

    row_index = 1
    for row in phire_audit_list:
        for column_index in range(0, len(row)):
            worksheet_pa.write(row_index, column_index, row[column_index], cell_format_audit)
        row_index += 1

    workbook.close()

def createBundleDF(bundle_rows_incl, bundle_rows_off, bundle_rows_data, bundle_rows_org):
    df_incl = pd.DataFrame(bundle_rows_incl, columns=['jira_code', 'summary', 'team', 'bundle_status', 'jira_status',
         'assignee', 'reporter', 'priority', 'sub_priority', 'category',
         'priortization_date', 'is_HRS', 'hrqa_epqas_date', 'phire_cr', 'cr_type',
         'hrs_epm_date', 'off_reason', 'project_association'])
    df_off = pd.DataFrame(bundle_rows_off, columns=['jira_code', 'summary', 'team', 'bundle_status', 'jira_status',
         'assignee', 'reporter', 'priority', 'sub_priority', 'category',
         'priortization_date', 'is_HRS', 'hrqa_epqas_date', 'phire_cr', 'cr_type',
         'hrs_epm_date', 'off_reason', 'project_association'])
    df_data = pd.DataFrame(bundle_rows_data, columns=['jira_code', 'summary', 'team', 'bundle_status', 'jira_status',
         'assignee', 'reporter', 'priority', 'sub_priority', 'category',
         'priortization_date', 'is_HRS', 'hrqa_epqas_date', 'phire_cr', 'cr_type',
         'hrs_epm_date', 'off_reason', 'project_association'])
    df_org = pd.DataFrame(bundle_rows_org, columns=['jira_code', 'summary', 'team', 'bundle_status', 'jira_status',
         'assignee', 'reporter', 'priority', 'sub_priority', 'category',
         'priortization_date', 'is_HRS', 'hrqa_epqas_date', 'phire_cr', 'cr_type',
         'hrs_epm_date', 'off_reason', 'project_association'])
    
    return pd.concat([df_incl, df_off, df_data, df_org])

def getTeamStat(df):
    return df['team'].value_counts().to_dict()

def getCategoryStat(df):
    return df['category'].value_counts().to_dict()

def getTypeStat(df):
    return df['cr_type'].value_counts().to_dict()