import pathlib
import sys

sys.path.append(pathlib.Path(__file__).parent.parent.__str__())

"""
FHIR EMR Dasboard
Note - this requires:
    dash-bootstrap-components>=1.0.0 and dash>=2.0 dash-bootstrap-templates>=1.0.4.
    dash_tabulator
NhanVietLe
"""
import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc
#from dash_bootstrap_templates import ThemeSwitchAIO

#import dash_daq as daq
from datetime import timedelta, date, datetime
#from dateutil import parser #use to parse date string to date object
import numpy as np

import plotly.graph_objects as go
from dash.exceptions import PreventUpdate

#from plotly import tools # tools using to export excel fiel
from pandasql import sqldf # Lib using to sql

import dash_tabulator 
#from dash.dependencies import Input, Output
 
# Disable safely "SettingWithCopyWarning" from pandas 
pd.options.mode.chained_assignment = None  # default='warn'

def do_this_if_x_is_not_NaN(x):
    return 1

def do_this_if_x_is_NaN(x):
    return 0

down = chr(9660) 
up =chr(9650)
#.apply(lambda x: '↗️' if x > 0 else '↘️')
#############################################
#local style HTML
#############################################
colors = {
    'pl.bkground': 'rgba(0, 0, 0, 0)',
    'pg.bkground': 'rgba(0, 0, 0, 0)',
    'drop.bkg': '#1E1E1E',
    'text.light': '#B6B6B6',
    'text.note': '#989898',
    'text.dark': '#000000'
}
fontnames = {
    'u': 'Segoe UI',
    'l': 'Segoe UI Light',
    's': 'Segoe UI Semibold',
    'b': 'Segoe UI Black'
    }

fontsz = {
    'f40': '2.5em'  ,
    'f30': '1.875em',
    'f26': '1.625em',
    'f24': '1.5em',
    'f18': '1.1em',
    'f16': '1em',
    'f14': '0.875em',
    'f12': '0.75em' ,
    'f10': '0.625em',
    'f09': '0.562em', 
    }
#############################################
# pass variables
#############################################
title = ['Bảng phân tích dữ liệu sức khỏe FHIR', 'Analytics Dashboard for FHIR Healthcare Data']
stitle= ['Dữ liệu thống kê từ máy chủ FHIR và CDR','Statistical data from FHIR and CDR servers']
color_scale = {
    'new_cases_smoothed':'redor', 
    'new_deaths_smoothed':'greys', 
    'people_vaccinated': 'blues', 
    'people_fully_vaccinated': 'greens' 
    }
cardtitle =['FHIR EMR', 'Nhân khẩu học', 'Kết quả điều trị']
cardstitle =[' ', 'Thống kê dựa trên dữ liệu sức khỏe FHIR', 'Thống kê dựa trên dữ liệu sức khỏe FHIR ']
cardcontent =['500', ' ', ' ']
cardnote =['Tổng số hồ sơ EMR ', 'dd/MM/yyyy-dd/MM/yyyy', 'dd/MM/yyyy-dd/MM/yyyy']
adcardnote =['Số lượt KCB','SL BN nhập viện','SL BN xuất viện','Số ca tử vong']
cardclass ={
    'h':'bg-primary bg-gradient fw-light text-white', 
    'b':'card-title fw-bold',
    's':'card-text',
    'g':'text-center shadow-sm rounded',
    }

#############################################
#Initialize empty array of given length
#############################################
sd = [0] * 4
s = "Nền sáng"
#############################################
#select the Bootstrap stylesheets and figure templates for the theme toggle here:
#############################################
template_theme1 = "lumen" # "simplex" #"flatly" #bg-primary bg-gradient text-white
template_theme2 = "darkly"
#url_theme1 = dbc.themes.FLATLY # Darkblue
#url_theme1 = dbc.themes.UNITED # Orange
url_theme1 = dbc.themes.COSMO #Blue
url_theme2 = dbc.themes.DARKLY #FLATLY #SUPERHERO

#############################################
dbc_css = ("https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css")
app = Dash(__name__, external_stylesheets=[url_theme1, dbc_css])
server = app.server
app.title = "FHIR Analytics"

#############################################
# Init some global variables
#############################################
dmax = date.today() + timedelta(days=-1)
n_days = 7
#switchBtnLbl ='Nền sáng'
#end_date_object = datetime.today() 
datetime_str = '01/12/23 00:00:01' # anchor date from data source 2023-01-12
end_date_object = datetime.strptime(datetime_str, '%m/%d/%y %H:%M:%S')

# Get date range to display on web
datetime_str = '01/12/23 00:00:01'
end_date_object = datetime.strptime(datetime_str, '%m/%d/%y %H:%M:%S')
start_date_object = end_date_object + timedelta(days=-n_days)

end_date_string = end_date_object.strftime('%d-%m-%Y')
start_date_string = start_date_object.strftime('%d-%m-%Y')
statisticsPeriod = "Chu kỳ thống kê: " + start_date_string + " - " + end_date_string

#############################################
# Loading & preprocessing data
#############################################
df = pd.read_csv('./data/patient.csv', index_col=0, parse_dates=True, encoding='utf-8')
dfa = pd.read_csv('./data/age.csv', parse_dates=True, encoding='utf-8')
dfg = pd.read_csv('./data/frsc.csv',  parse_dates=True, encoding='utf-8')
tx = pd.read_csv('./data/TxResults.csv', encoding='utf-8')

# Dataframe for query
dq = df.copy(deep=True)
dq.dropna(subset=['EndDtmEMR'], inplace=True)

# Create new columns to statistic
dq['FHIR_EMR'] = dq['StdDtm'].apply(lambda x: do_this_if_x_is_not_NaN(x) if x is not np.nan else do_this_if_x_is_NaN(x))
dq['EMR'] = dq['EndDtmEMR'].apply(lambda x: do_this_if_x_is_not_NaN(x) if x is not np.nan else do_this_if_x_is_NaN(x))

# Convert object column ["StdDtm", "EndDtmEMR"] to datetime64
dq[["StdDtm", "EndDtmEMR"]]=dq[["StdDtm", "EndDtmEMR"]].apply(pd.to_datetime)

dq['year'] = pd.to_datetime(dq['EndDtmEMR']).dt.isocalendar().year
dq['weekno'] = pd.to_datetime(dq['EndDtmEMR']).dt.isocalendar().week
dq['weeknum'] = pd.to_datetime(dq['EndDtmEMR']).dt.strftime('%Y-W%W')

# Replace NaN Values with Zeros in Pandas DataFrame
df = df.replace(np.nan, 0)

# preprocess fo dataset of tabulator
# Remove NaN value from EndDtmEMR
dfg.dropna(subset=['EndDtmEMR'], inplace=True)
# Convert object column ["StdDtm", "EndDtmEMR"] to datetime64
dfg[["StdDtm", "EndDtmEMR"]]=dfg[["StdDtm", "EndDtmEMR"]].apply(pd.to_datetime)

unpivot_df = pd.melt(dfg, id_vars=['EndDtmEMR', 'StdDtm', 'PtID'], 
                     value_vars=['AllergyIntolerance', 'CarePlan',
                                 'Condition', 'DiagnosticReport',
                                 'DocumentReference', 'Encounter',
                                 'FamilyMemberHistory', 'Goal',
                                 'Immunization', 'Medication',
                                 'MedicationDispense', 'MedicationRequest', 
                                 'Observation', 'Organization', 
                                 'Patient', 'Practitioner', 
                                 'Procedure', 'ServiceRequest'],
                     var_name="Attributes", value_name="Rsc", ignore_index = True)
#############################################
# Hide NaN from hoverlabels
# Formatting long numbers as strings
# Thousands with K, and millions with M
# Example: 7436313 as 7.44M, and 2345 as 2,34K
#############################################
def human_format(num):
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), 
                         ['', 'K', 'M', 'B', 'T'][magnitude])
#############################################
def spaces(n):
    return ' ' * n
#############################################
def freezeTopRow(values, data, calcParams):
    return values[0]
#############################################
# fitering data by date range
#############################################
def update_numEMR(p_df, s_dto, e_dto):
    dfg = p_df.copy(deep=True)
    #############################################
    # Creates a list containing 4 lists, each of 2 items, all set to empty
    # each card includes: 0- body | 1-sup info
    #############################################
    w, h = 2, 8
    card_rstl = [['' for x in range(w)] for y in range(h)]
  
    #############################################
    # Number of FHIR EMRs and EMRs by Date Range
    #############################################
    # Number Of EMR
    dfg['EndDtmEMR'] = pd.to_datetime(dfg['EndDtmEMR']).dt.strftime('%Y-%m-%d')
    dfg.index = pd.to_datetime(dfg['EndDtmEMR'])
    filterMask = (dfg['EndDtmEMR'] >= s_dto.strftime('%Y-%m-%d')) & (dfg['EndDtmEMR'] <= e_dto.strftime('%Y-%m-%d'))
    dfg = dfg[filterMask]
    numEMR = dfg['EndDtmEMR'].count()
    
    # Number of FHIR EMRs
    dfg['StdDtm'] = pd.to_datetime(dfg['StdDtm']).dt.strftime('%Y-%m-%d')
    dfg.index = pd.to_datetime(dfg['StdDtm'])
    filterMask = (dfg['StdDtm'] >= s_dto.strftime('%Y-%m-%d')) & (dfg['EndDtmEMR'] <= e_dto.strftime('%Y-%m-%d'))
    dfg = dfg[filterMask]
    numFHIREMR = dfg['StdDtm'].count()
    
    # Asign to Card result 0.
    card_rstl[0][0] = numEMR #"{:,.0f}".format(numEMR)
    card_rstl[0][1] = numFHIREMR #"{:,.0f}".format(numFHIREMR)
    
    #############################################
    # Standardization ratio FHIR EMR
    #############################################
    card_rstl[1][0] = (numFHIREMR/numEMR)*100 #"{:,.0f}".format(numFHIREMR/numEMR)
    
    # numEMR - numFHIREMR and ratio in prev period
    # previous start date & end date
    ps_dt = s_dto + timedelta(days=-n_days)
    pe_dt = e_dto + timedelta(days=-n_days)
    # Number Of EMR in previous period
    dfg = p_df.copy(deep=True)
    dfg['EndDtmEMR'] = pd.to_datetime(dfg['EndDtmEMR']).dt.strftime('%Y-%m-%d')
    dfg.index = pd.to_datetime(dfg['EndDtmEMR'])
    filterMask = (dfg['EndDtmEMR'] >= ps_dt.strftime('%Y-%m-%d')) & (dfg['EndDtmEMR'] <= pe_dt.strftime('%Y-%m-%d'))
    dfg = dfg[filterMask]
    pnumEMR = dfg['EndDtmEMR'].count()    

    # Number of FHIR EMRs
    dfg['StdDtm'] = pd.to_datetime(dfg['StdDtm']).dt.strftime('%Y-%m-%d')
    dfg.index = pd.to_datetime(dfg['StdDtm'])
    filterMask = (dfg['StdDtm'] >= ps_dt.strftime('%Y-%m-%d')) & (dfg['EndDtmEMR'] <= pe_dt.strftime('%Y-%m-%d'))
    dfg = dfg[filterMask]
    pnumFHIREMR = dfg['StdDtm'].count()
    card_rstl[1][1] = (pnumFHIREMR/pnumEMR)*100
    return card_rstl

#############################################
# query for advanced cards
#############################################
def update_acards(s_dto, e_dto):    
    #############################################
    # Advanced card
    # [0][0]-[0][1]: Encounter Times - Change
    # [1][0]-[1][1]: Admission Times - Change
    # [2][0]-[2][1]: Discharge Times - Change
    # [3][0]-[3][1]: Died number - Change
    #############################################
    # Creates a list containing 4 lists, each of 2 items, all set to empty
    # each card includes: 0- currently value | 1- Change% value
    #############################################
    w, h = 2, 4
    acards = [['' for x in range(w)] for y in range(h)]
    # Setting up date milestone
    # curently date range
    ###########################################################################
    sdate_object = datetime.fromisoformat(str(s_dto))
    sdate_string = sdate_object.strftime('%Y-%m-%d')    # Only use for render
    edate_object = datetime.fromisoformat(str(e_dto))
    edate_string = edate_object.strftime('%Y-%m-%d')    # Only use for render

    # previlously date range
    prev_edate_object = sdate_object + timedelta(days=-1)
    prev_sdate_object = prev_edate_object + timedelta(days=-n_days)
    prev_edate_string = prev_edate_object.strftime('%Y-%m-%d')
    prev_sdate_string = prev_sdate_object.strftime('%Y-%m-%d')
    
    sql = """
        select PtID, EndDtmEMR, StdDtm, IsInPtTx, AdmTDtm, TxResults
    	from dq
    	where (not(StdDtm is null))
              and (not(EndDtmEMR is null))
           """
    mysql = lambda q: sqldf(q, globals())
    
    dff=mysql(sql)
    #############################################
    # Get data for encounter - receipt number card
    # Lượt KCB
    # Convert to Date Formate: datetime64[ns] And Filter by cur Date Range 
    dff['StdDtm'] = pd.to_datetime(dff['StdDtm'].astype(str), format='%Y-%m-%d')
    cw = "(StdDtm >='" + sdate_string +"')and(StdDtm <='" + edate_string +"')"
    d1 = dff.query(cw)
    curReceipt = d1.count()['PtID']
    pw = "(StdDtm >='" + prev_sdate_string +"')and(StdDtm <='" + prev_edate_string +"')"
    d2 = dff.query(pw)
    preReceipt = d2.count()['PtID']
    changReceipt = 0 if preReceipt==0 else round(((curReceipt-preReceipt)/preReceipt)*100,2)
    sn = up if changReceipt>0 else down

    acards[0][0] = str("{:,}".format(curReceipt))
    acards[0][1] = str("{:,}".format(changReceipt)) + "% " + sn

    #############################################
    # Get data for Admission number card
    # Số lượt nhập viện
    cadmw = "(IsInPtTx==True)"
    d1 = d1.query(cadmw)
    curAdm = d1.count()['PtID']
    padmw = "(IsInPtTx==True)" # previous adm where
    d2 = d2.query(padmw)
    preAdm = d2.count()['PtID']
    changeAdm = 0 if preAdm==0 else round(((curAdm-preAdm)/preAdm)*100,2)
    sn = up if changeAdm>0 else down
    
    acards[1][0] = str("{:,}".format(curAdm))
    acards[1][1] = str("{:,}".format(changeAdm)) + "% " + sn    
    
    #############################################
    # Get data for Discharge number card
    # Số lượt xuất viện
    cdisw = "(AdmTDtm >='" + sdate_string +"') & (AdmTDtm <='" + edate_string +"')"
    d1 = d1.query(cdisw)
    curDis = d1.count()['PtID']
    pdisw = "(AdmTDtm >='" + prev_sdate_string +"') & (AdmTDtm <='" + prev_edate_string +"')" # previous discharge where
    d2= d2.query(pdisw)
    preDis = d2.count()['PtID']
    changeDis = 0 if preDis==0 else round(((curDis-preDis)/preDis)*100,2)
    sn = up if changeDis>0 else down

    acards[2][0] = str("{:,}".format(curDis))
    acards[2][1] = str("{:,}".format(changeDis)) + "% " + sn      

    #############################################
    # Get data for Died number card
    # Số ca tử vong
    cdiew = '(TxResults==5)'# cur died where
    d1 = d1.query(cdiew)
    curDied = d1.count()['PtID']
    pdiew = '(TxResults==5)'
    d2 = dff.query(pdiew)
    preDied = d2.count()['PtID']
    changeDied = 0 if preDis==0 else round(((curDied-preDied)/preDied)*100,2)
    sn = up if changeDied>0 else down
    
    acards[3][0] = str("{:,}".format(curDied))
    acards[3][1] = str("{:,}".format(changeDied)) + "% " + sn       
    return acards

#############################################
# query for multiple bar
#############################################
def bquery(s_dto, e_dto):
    mysql = lambda q: sqldf(q, globals())
    
    e_dts = e_dto.strftime('%Y-%m-%d')
    s_dts = s_dto.strftime('%Y-%m-%d')
    
    sql = """Select	year, weekno, weeknum, EncounterType, (year*100+weekno) as ywn,   
                    SUM(CASE  
                        WHEN StdDtm is null  
                            THEN 0 
                            ELSE 1 
                        END) as sFHIREMR, 
                    SUM(CASE 
                        WHEN EndDtmEMR is null 
                            THEN 0 
                            ELSE 1 
                        END) as sEMR,
            		ROUND(((SUM(CASE
                        WHEN StdDtm is null
                           THEN 0
                           ELSE 1
                        END) *1.00)/(SUM(CASE
                        WHEN EndDtmEMR is null
                           THEN 0
                           ELSE 1
                        END) *1.00)*100),3) as ratio
                from dq
                where (
                    (not(EndDtmEMR is null))AND
                    (strftime('%Y-%m-%d', EndDtmEMR) >='""" + s_dts +"""') AND
                    (strftime('%Y-%m-%d', EndDtmEMR) <='""" + e_dts + """'))
                group by year, weekno, weeknum, EncounterType 
                order by year, weekno, EncounterType"""
    dft=mysql(sql)
    return dft
#############################################    
bardf = bquery(start_date_object, end_date_object)
#############################################
# query for Donut chart
#############################################
def dquery(s_dto, e_dto):
    sdate_string = s_dto.strftime('%Y-%m-%d')
    edate_string = e_dto.strftime('%Y-%m-%d')
    
    mysql = lambda q: sqldf(q, globals())
    sql = """
    SELECT t.FHIRGender, (1.00*t.sGender) AS NumGender, ROUND(SUM(t.sGender) * 100.0 / SUM(SUM(t.sGender)) OVER (),2) AS Percentage
    From
    (
    	select (CASE
    				WHEN StdDtm is null
    				   THEN null
    				   ELSE [Gender]
    			  END) AS FHIRGender,
    			  COUNT(CASE
    				WHEN StdDtm is null
    				   THEN null
    				   ELSE [Gender]
    			  END) AS sGender
    	from dq
    	where (not(StdDtm is null))AND
    		((not(EndDtmEMR is null))AND
            (strftime('%Y-%m-%d', StdDtm) >='""" + sdate_string +"""') AND
            (strftime('%Y-%m-%d', StdDtm) <='""" + edate_string + """'))
    	group by (CASE
    				WHEN StdDtm is null
    				   THEN null
    				   ELSE [Gender]
    			  END)
    ) AS t
    GROUP BY t.FHIRGender, t.sGender
    """
    dft=mysql(sql)
    return dft
#############################################    
donutdf = dquery(start_date_object, end_date_object)
############################################# 
#############################################
# query for populationDonut chart
#############################################
def pquery(s_dto, e_dto):
    sdate_string = s_dto.strftime('%Y-%m-%d')
    edate_string = e_dto.strftime('%Y-%m-%d')
    
    mysql = lambda q: sqldf(q, globals())
    sql = """
    select t.AgeRange, t.FHIRGender, t.NumGender, (SUM(t.NumGender) * 100.0 / SUM(SUM(t.NumGender)) OVER ()) AS Percentage
    from
    (
        select AgeRange, FHIRGender, count(FHIRGender) AS NumGender
        from
        (
            select --EndDtmEMR, StdDtm, 
                   Gender AS FHIRGender,
            	   iif(Age>=0 AND Age <= 10,'1.[0-10]',iif(Age>=11 AND Age<=15,'2.[11-15]',iif(Age>=16 AND Age<=30,'3.[16-30]',iif(Age>=31 AND Age<=60,'4.[31-60]','5.[trên 60]')))) As AgeRange
            from dq 
            where (not(StdDtm is null)) 
                  AND (not(EndDtmEMR is null)) 
            	  AND (not(Gender like 'Không xác định')) --N''
                  AND ((strftime('%Y-%m-%d', StdDtm) >='""" + sdate_string +"""') 
                  AND (strftime('%Y-%m-%d', StdDtm) <='""" + edate_string + """'))
        ) as g
        group by AgeRange, FHIRGender
    ) as t
    group by t.AgeRange, t.FHIRGender, t.NumGender
    """
    dft=mysql(sql)
    unpivot_df= dft.pivot(index=['AgeRange'], columns='FHIRGender')
    #format column names
    unpivot_df.columns = ['_'.join(str(s).strip() for s in col if s) for col in unpivot_df.columns]
    #reset index
    unpivot_df.reset_index(inplace=True)
    t= dfa.merge(unpivot_df, on='AgeRange', how='left')

    c1=t['AgeRange']
    c2=t['NumGender_Nam'].replace(np.nan, 0)
    c3=t['NumGender_Nữ'].replace(np.nan, 0)
    c4=t['Percentage_Nam'].replace(np.nan, 0)
    c5=t['Percentage_Nữ'].replace(np.nan, 0)
    col ={
        'AgeRange':c1,
        'NumGender_Nam':c2,
        'NumGender_Nữ':c3,
        'Percentage_Nam':c4,
        'Percentage_Nữ':c5,
        }
    return col
#############################################    
popdf = pquery(start_date_object, end_date_object)
############################################# 
#############################################
# query for Sunburst chart
#############################################
def squery(s_dto, e_dto, val):
    sdate_string = s_dto.strftime('%Y-%m-%d')
    edate_string = e_dto.strftime('%Y-%m-%d')
    
    mysql = lambda q: sqldf(q, globals())
    if val==1:
        sql = """
            select t.Encounter, t.Gender, t.TxResults, t.PtNum, round((SUM(t.PtNum) * 100.0 / SUM(SUM(t.PtNum)) OVER ()),2) AS Percentage
            from
            (
                select g.Encounter, g.Gender, g.TxResults, count(g.PtID) as PtNum
                from
                (
                    select iif(a.IsInPtTx=1,'ĐT nội trú','KĐT ngoại trú') as Encounter, a.Gender, a.PtID, 
                           a.EndDtmEMR, a.StdDtm,  b.TxResults, a.ICD10
                    from dq a inner join tx b on (b.ID=a.TxResults)   
                    where (not(StdDtm is null))
                          and (not(EndDtmEMR is null))
                          and ((strftime('%Y-%m-%d', StdDtm) >='""" + sdate_string +"""') 
                          and (strftime('%Y-%m-%d', StdDtm) <='""" + edate_string + """'))
                ) as g
                group by g.Encounter, g.Gender, g.TxResults
             ) as t
            group by t.Encounter, t.Gender, t.TxResults, t.PtNum
        """
    else:
        sql = """
            select t.Encounter, t.TxResults, t.PtNum, round((SUM(t.PtNum) * 100.0 / SUM(SUM(t.PtNum)) OVER ()),2) AS Percentage
            from
            (
                select g.Encounter, g.TxResults, count(g.PtID) as PtNum
                from
                (
                    select iif(a.IsInPtTx=1,'ĐT nội trú','KĐT ngoại trú') as Encounter, a.PtID, 
                           a.EndDtmEMR, a.StdDtm,  b.TxResults, a.ICD10
                    from dq a inner join tx b on (b.ID=a.TxResults)   
                    where (not(StdDtm is null))
                          and (not(EndDtmEMR is null))
                          and ((strftime('%Y-%m-%d', StdDtm) >='""" + sdate_string +"""') 
                          and (strftime('%Y-%m-%d', StdDtm) <='""" + edate_string + """'))
                ) as g
                group by g.Encounter, g.TxResults
             ) as t
            group by t.Encounter, t.TxResults, t.PtNum
        """
    dft=mysql(sql)
    return dft
#############################################    
sundf = squery(start_date_object, end_date_object, 1)
#############################################    
# query for horizontal stack bar chart
#############################################
def hbquery(s_dto, e_dto):
    mysql = lambda q: sqldf(q, globals())    
    e_dts = e_dto.strftime('%Y-%m-%d')
    s_dts = s_dto.strftime('%Y-%m-%d')
    
    sql = """
            select g.ICD10, g.ICDDx, g.maleSum, g.femaleSum, g.diedSum,
                   round(sum(g.maleSum) * 100.0 / sum(sum(g.maleSum)) over (), 2) as perMaleSum,
                   round(sum(g.femaleSum) * 100.0 / sum(sum(g.femaleSum)) over (), 2) as perFemaleSum,
                   round(sum(g.diedSum) * 100.0 / sum(sum(g.diedSum)) over (), 2) as perDiedSum
            from
            (
                select ICD10, ICDDx,
                       sum(iif(Gender=='Nam',1,0)) as maleSum,
                       sum(iif(Gender=='Nữ',1,0)) as femaleSum,
                       sum(iif(TxResults==5,1,0)) as diedSum
                from dq   
                where (not(StdDtm is null))
                      and (not(EndDtmEMR is null))
                      and ((strftime('%Y-%m-%d', StdDtm) >='""" + s_dts +"""') 
                      and (strftime('%Y-%m-%d', StdDtm) <='""" + e_dts + """'))
                group by ICDDx
            ) as g
            group by g.ICDDx, g.maleSum, g.femaleSum, g.diedSum
        """
    dft=mysql(sql)
    return dft
#############################################    
hbardf = hbquery(start_date_object, end_date_object)
#############################################
def tabquery(s_dto, e_dto):
    sdate_string = s_dto.strftime('%Y-%m-%d')
    edate_string = e_dto.strftime('%Y-%m-%d')
    
    mysql = lambda q: sqldf(q, globals())
    sql="""
        select g.Attributes,
               sum(g.Rsc) as RscSum,
               round(sum(g.Rsc) * 100.0 / sum(sum(g.Rsc)) over (), 2) as perRsc
        from unpivot_df as g
        where (not(StdDtm is null))
              and (not(EndDtmEMR is null))
              and ((strftime('%Y-%m-%d', StdDtm) >='""" + sdate_string +"""') 
              and (strftime('%Y-%m-%d', StdDtm) <='""" + edate_string + """')) 
        group by g.Attributes
        """
    dff=mysql(sql)    
    return dff
#############################################
tabdf = tabquery(start_date_object, end_date_object)
#############################################
def boxquery(s_dto, e_dto):
    sdate_string = s_dto.strftime('%Y-%m-%d')
    edate_string = e_dto.strftime('%Y-%m-%d')

    mysql = lambda q: sqldf(q, globals())
    sql="""
        select g.PtID, g.Attributes,
               sum(g.Rsc) as RscSum,
               round(sum(g.Rsc) * 100.0 / sum(sum(g.Rsc)) over (), 2) as perRsc
        from unpivot_df as g
        where (not(StdDtm is null))
              and (not(EndDtmEMR is null))
              and ((strftime('%Y-%m-%d', StdDtm) >='""" + sdate_string +"""') 
              and (strftime('%Y-%m-%d', StdDtm) <='""" + edate_string + """')) 
        group by g.PtID, g.Attributes
        """
    dff=mysql(sql)
    aw = "Attributes in ('Condition', 'Observation', 'ServiceRequest', 'Encounter')"
    bdf = dff.query(aw)   
    return bdf
#############################################
boxdf = boxquery(start_date_object, end_date_object)
#############################################
header = html.Div(children=[
    dbc.Row([
        dbc.Col([
            html.H2(title[0], className="text-white",
                    style={'font-family': fontnames['l']})
            ], width=12)
        ]),
    dbc.Row([
        dbc.Col([html.Sup(stitle[0], style={'color':'#E6E6E6'})], width=12)
        ])
    ], className="bg-primary bg-gradient p-3 mb-2")

#############################################
# Define switching btn for dark-light screen
#############################################
switch = html.Div([dbc.Row([dbc.Col(children=[html.Sup("Số liệu được ghi nhận dựa trên việc chuẩn hóa EMRs và các bản ghi FHIR.", style={'font-weight': 'bold'}),
                                              html.Sup(" Cập nhật đến ngày " + dmax.strftime('%d-%m-%Y') + " (UTC)")]
                                    ,width=12)]
                           )])
#############################################
# Define criterias
#############################################
dpicker = dcc.DatePickerRange(id="date_range",
    #start_date_placeholder_text="Từ ngày",#"Start Period",
    #end_date_placeholder_text="Đến ngày",#"End Period",
    min_date_allowed=datetime(2020,1,1),
    max_date_allowed=datetime.today(),
    start_date=start_date_object,# datetime.today() + timedelta(days=-7),
    end_date=end_date_object, # datetime.today(),
    display_format='DD/MM/YYYY',
    first_day_of_week =1,#0,1,2,...6
    clearable=True,
    style = {'font-family': fontnames['u'],
             'font-size': '10px','display': 'inline-block', 'border-radius' : '2px', 
             'border' : '0px solid #ccc', 'color': '#333', 
             'border-spacing' : '0', 'border-collapse' :'separate',
             }
)

#############################################
# Define pg footer 
#############################################
bottom = html.P("© 2022 LAC VIET Computing Corp.")
#############################################
# Plots
#############################################
ggraph = html.Div(dcc.Graph(id="ggraph"), className="m-4") # Gauge chart
cgraph = html.Div(dcc.Graph(id="cgraph"), className="m-4") # Column bar chart
dgraph = html.Div(dcc.Graph(id="dgraph"), className="m-4") # Donut chart
pgraph = html.Div(dcc.Graph(id="pgraph"), className="m-4") # population chart
sgraph = html.Div(dcc.Graph(id="sgraph"), className="m-4") # sunburst  chart
xgraph = html.Div(dcc.Graph(id="xgraph"), className="m-4") # Box graph
chklst = html.Div(dbc.Checklist(
    options=[{"label": " KQ ĐT và giới tính", "value": 1}],
            value=[1], id="chk", inline=True, style={'font-size': fontsz['f12']}), className="m-1") # checkbox
hgraph = html.Div(dcc.Graph(id="hgraph", style={"maxHeight": "1500px"}))
tabulr = html.Div([dash_tabulator.DashTabulator(id='tabulator',
                                                columns=[],
                                                data=[],
                                                theme="tabulator", #"tabulator_modern", #"tabulator_modern", #"tabulator_simple",#"tabulator",
                                                rowSelected=False,
                                                ),
                   dcc.Interval(
                       id='interval-component-iu',
                       interval=1*10, # in milliseconds
                       n_intervals=0,
                       max_intervals=0
                       )
                   ], className="m-0")

# filter header of tabulator
initialHeaderFilter = [{"field":"col", "value":"blue"}]

#############################################
# Cards Info
#############################################
card = {
        '0':
            dbc.Card([ 
                dbc.CardHeader( [
                    html.H6(className=cardclass['b'], children=[cardtitle[0]], style={'color':'#000000', 'height':8}, id="c0t"),
                    html.H4(className=cardclass['b'], children=[cardcontent[0]], style={'color':'#FF0000'}, id="c0c"),
                    html.Sup(id="c0n", children=[cardnote[0]], style={'color':'#16145A'} ),
                    ],style={"height":90}),
                dbc.CardBody([ggraph], style={"height": 280})
                ], className="shadow"
                ),
        '1':
            dbc.Card([
                dbc.CardBody([
                    html.H6(className=cardclass['b'], children=["Tỷ lệ chuẩn hóa EMR theo loại hồ sơ"], style={'color':'#000000', 'height':1}, id="c1t"),
                    dbc.CardBody([cgraph], style={"height": 330})
                    ]),
                ], className="shadow"
                ),
        '2':
            dbc.Card([ 
                dbc.CardHeader( [
                    html.H6(className=cardclass['b'], children=[cardtitle[1]], style={'color':'#000000', 'height':8}, id="c2t"),
                    html.Sup(children=[cardstitle[1]], style={'color':'#16145A'}, id="c2s"),
                    html.Br(),
                    html.Sup(id="c2n", children=[cardnote[0]], style={'color':'#16145A'} ),
                    ],style={"height":90}),
                dbc.CardBody([dgraph], style={"height": 280})
                ], className="shadow"
                ),
        '3':
            dbc.Card([
                dbc.CardBody([
                    html.H6(className=cardclass['b'], children=["Thống kê theo nhóm tuổi và giới tính"], style={'color':'#000000', 'height':1}, id="c3t"),
                    dbc.CardBody([pgraph], style={"height": 330})
                    ]),
                ], className="shadow"
                ),  
        '4.0': # Advanced card 1
            dbc.Card([
                dbc.CardBody([
                    html.H4(
                        className=cardclass['b'],
                        children=[
                            html.Span(['500'], style={'color':'#0E1A77', 'font-size': fontsz['f18'], 'margin-top': '1px'}, id="c40h"),
                            html.Span(['Indicator'], style={'color':'#0E1A77', 'font-size': fontsz['f09'], 'marginLeft': '10px'}, id="c40c"),
                        ]),
                    html.Sup(id="c40n", children=[adcardnote[0]], style={'color':'#16145A'} ),
                    ]),
                ], style={"height": 88}, className="shadow"
                ),
        '4.1': # Advanced card 2
            dbc.Card([
                dbc.CardBody([
                    html.H4(
                        className=cardclass['b'],
                        children=[
                            html.Span(['319'], style={'color':'#DF3724', 'font-size': fontsz['f18'], 'margin-top': '1px'}, id="c41h"),
                            html.Span(['Indicator'], style={'color':'#DF3724', 'font-size': fontsz['f09'], 'marginLeft': '10px'}, id="c41c"),
                        ]),
                    html.Sup(id="c41n", children=[adcardnote[1]], style={'color':'#16145A'} ),
                    ]),
                ], style={"height": 88}, className="shadow"
                ),
        '4.2': # Advanced card 3
            dbc.Card([
                dbc.CardBody([
                    html.H4(
                        className=cardclass['b'],
                        children=[
                            html.Span(['319'], style={'color':'#0D6ABF', 'font-size': fontsz['f18'], 'margin-top': '1px'}, id="c42h"),
                            html.Span(['Indicator'], style={'color':'#0D6ABF', 'font-size': fontsz['f09'], 'marginLeft': '10px'}, id="c42c"),
                        ]),
                    html.Sup(id="c42n", children=[adcardnote[2]], style={'color':'#16145A'} ),
                    ]),
                ], style={"height": 88}, className="shadow"
                ),
        '4.3': # Advanced card 4
            dbc.Card([
                dbc.CardBody([
                    html.H4(
                        className=cardclass['b'],
                        children=[
                            html.Span(['Value'], style={'color':'#000000', 'font-size': fontsz['f18'], 'margin-top': '1px'}, id="c43h"),
                            html.Span(['Indicator'], style={'color':'#16145A', 'font-size': fontsz['f09'], 'marginLeft': '10px'}, id="c43c"),
                        ]),
                    html.Sup(id="c43n", children=[adcardnote[3]], style={'color':'#16145A'} ),#'margin-bottom': '10px'
                    ]),
                ], style={"height": 88}, className="shadow"
                ),
        '5':
            dbc.Card([ 
                dbc.CardHeader( [
                    html.H6(className=cardclass['b'], children=[cardtitle[2]], style={'color':'#000000', 'height':8}, id="c5t"),
                    html.Sup(children=[cardstitle[2]], style={'color':'#16145A'}, id="c5s"),
                    html.Br(),
                    html.Sup(id="c5n", children=[cardnote[2]], style={'color':'#16145A'} ),
                    ],style={"height":90}),
                dbc.CardBody([sgraph], style={"height": 280})
                ], className="shadow"
                ), 
        '6':
            dbc.Card([
                dbc.CardBody([
                    html.H6(className=cardclass['b'], children=["Thống kê bệnh tật và tử vong"], style={'color':'#000000', 'height':30}, id="c6t"),
                    dbc.CardBody([hgraph], style={"height": 300, "overflow-y": "scroll"}, className="no-scrollbars" )
                    ]),
                ], className="shadow"
                ),  
        '7':
            dbc.Card([
                dbc.CardBody([
                    dbc.CardBody([tabulr], style={"height": 330, 
                                                  "overflow-y": "scroll",
                                                  "margin-top": 20,
                                                  "margin-left": 0,
                                                  "margin-right": 0,
                                                  "margin-bottom": 20,
                                                  "padding": 0,
                                                  }, className="no-scrollbars" )
                    ]),
                ], className="shadow"
                ), 
        '8':
            dbc.Card([
                dbc.CardBody([
                    html.H6(className=cardclass['b'], children=["Tỷ lệ phân bố các bản ghi FHIR chính theo BN"], style={'color':'#000000', 'height':1}, id="c7t"),
                    dbc.CardBody([xgraph], style={"height": 360})
                    ]),
                ], className="shadow"
                ),              
        }
adcards = html.Div([
    dbc.Row([dbc.Col(dbc.Card(card['4.0'])),],style={"padding-bottom": "5px"}),
    dbc.Row([dbc.Col(dbc.Card(card['4.1'])),],style={"padding-bottom": "5px"}),
    dbc.Row([dbc.Col(dbc.Card(card['4.2'])),],style={"padding-bottom": "5px"}),
    dbc.Row([dbc.Col(dbc.Card(card['4.3'])),],style={"padding-bottom": "0px"}),
    ]
    )

#############################################
# layout
#############################################
app.layout = dbc.Container(children=[
    dbc.Row(
        [
            dbc.Col(width=1),
            dbc.Col(
                [
                    header,
                    switch,
                ], width=10
            ),
            dbc.Col(width=1)
        ]
    ),
    dbc.Row(
        [
            dbc.Col(width=1),
            dbc.Col(
                [
                   html.Div(id="lbl",children=[statisticsPeriod],
                                    style={'textAlign':'left',
                                           'font-size':'12'}),
                   dpicker
                ], width=10
            ),
            dbc.Col(width=1)
        ],className='div-user-controls'
    ),
    dbc.Row(
        [
        dbc.Col(width=1),
        dbc.Col(width=10),
        dbc.Col(width=1)
        ], className="mt-3"
        ),
    dbc.Row(
        [
        dbc.Col(width=1),
        dbc.Col([dbc.Card(card['0'])], width=3, className="shadow-sm rounded m-0"),
        dbc.Col([dbc.Card(card['1'])], width=7, className="shadow-sm rounded m-0"),
        dbc.Col(width=1)
        ]
        ),
    dbc.Row(
        [
        dbc.Col(width=1),
        dbc.Col(width=10),
        dbc.Col(width=1)
        ], className="mt-3"
        ),
    dbc.Row(
        [
        dbc.Col(width=1),
        dbc.Col([dbc.Card(card['2'])], width=3, className="shadow-sm rounded m-0"),
        dbc.Col([card['3']], width=7, className="shadow-sm rounded m-0"),
        dbc.Col(width=1)
        ]
        ),
    dbc.Row(
        [
        dbc.Col(width=1),
        dbc.Col(width=10),
        dbc.Col(width=1)
        ], className="mt-3"
        ),
    dbc.Row(
        [
        dbc.Col(width=1),
        dbc.Col([adcards], width=2),
        dbc.Col([dbc.Card(card['5'])], width=3,  className="shadow-sm rounded m-0"),
        dbc.Col([card['6']], width=5, className="shadow-sm rounded m-0"),
        dbc.Col(width=1)
        ], className="mt-3"
        ),
    dbc.Row(
        [
        dbc.Col(width=1),
        dbc.Col(width=2),
        dbc.Col([chklst], width=3),
        dbc.Col(width=5), 
        dbc.Col(width=1)
        ],
        ),
    dbc.Row(
        [
        dbc.Col(width=1),
        dbc.Col(width=10),
        dbc.Col(width=1)
        ], className="mt-3"
        ),
    dbc.Row(
        [
        dbc.Col(width=1),
        dbc.Col([card['7']], width=4, className="shadow-sm rounded m-0"),
        dbc.Col([card['8']], width=6, className="shadow-sm rounded m-0"),
        dbc.Col(width=1)
        ], 
        ),
    dbc.Row(
        [
        dbc.Col(width=1),
        dbc.Col(width=10),
        dbc.Col(width=1)
        ], className="mt-3"
        ),
    dbc.Row(
        [
        dbc.Col(width=1),
        dbc.Col(bottom),
        dbc.Col(width=1)
        ]
        ),
    ],
    
    fluid=True,
)
@app.callback([ Output('tabulator', 'columns'),
                Output('tabulator', 'data'),#],
                Output('tabulator', 'initialHeaderFilter')],
                [Input('interval-component-iu', 'n_intervals'),
                 Input("date_range", "start_date"),
                 Input("date_range", "end_date"),]
                )
def initialize(val, start_date , end_date):
    if (start_date is None)or(end_date is None):
        raise PreventUpdate
    start_date_object = datetime.fromisoformat(str(start_date))
    end_date_object = datetime.fromisoformat(str(end_date))
    tabdf = tabquery(start_date_object, end_date_object)
    data = tabdf.to_dict("records")
    columns = [
        {"title": "Bản ghi FHIR", "field": "Attributes", "width": "50%", "hozAlign": "left", "headerFilter": True }, 
        {"title": "SL Bản ghi", "field": "RscSum", "width": "30%", "hozAlign": "right", "formatter":"money",
         "formatterParams":{
             "thousand":",",
             "precision": False,
             }
         },                
        {"title": "Tỷ lệ %", "field": "perRsc", "width": "20%", "hozAlign": "left", "formatter": "progress",
         "formatterParams":{"color": "#FF0000",
                            "min": 0,
                            "max":100,
                            },
         "headerSort":False}
        ]
    
    return columns, data, initialHeaderFilter

@app.callback(
    Output("lbl", 'children'),
    Output("ggraph", "figure"),
    Output("cgraph", "figure"),
    Output('c0c', 'children'),
    Output('c0n', 'children'),
    Output('c2n', 'children'),
    Output("dgraph","figure"),
    Output("pgraph","figure"),
    Output('c40h','children'),
    Output('c40c','children'),
    Output('c41h','children'),
    Output('c41c','children'),    
    Output('c42h','children'),
    Output('c42c','children'),    
    Output('c43h','children'),
    Output('c43c','children'),
    Output('c5n', 'children'),
    Output("sgraph","figure"),
    Output("hgraph","figure"),
    Output("xgraph", "figure"),
    Input("date_range", "start_date"),
    Input("date_range", "end_date"),
    Input("chk", "value")
    )
def update_theme(start_date , end_date, chk_value):    
    if (start_date is None)or(end_date is None):
        raise PreventUpdate

    # get statistic periode from user
    start_date_object = datetime.fromisoformat(str(start_date))
    start_date_string = start_date_object.strftime('%d-%m-%Y') # Only use for render
    end_date_object = datetime.fromisoformat(str(end_date))
    end_date_string = end_date_object.strftime('%d-%m-%Y')     # Only use for render
    
    
    diff = date.fromisoformat(end_date_object.strftime('%Y-%m-%d')) - date.fromisoformat(start_date_object.strftime('%Y-%m-%d'))
    n_days = diff.days
    rslt = update_numEMR(df, start_date_object, end_date_object)
    
    adrslt = update_acards(start_date, end_date) 
    statisticsPeriod = "Chu kỳ thống kê: " + start_date_string + " - " + end_date_string 
    
    # Render Gauge Chart
    gfig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        domain = {'x': [0, 1], 'y': [0, 1]},
        value = rslt[1][0],
        number = {'suffix': "%"}, #, 'prefix': "Tỷ lệ " },
        title = {'text': "Tỷ lệ chuẩn hóa", 'font': {'size': 16}},
        delta = {'reference': rslt[1][1], 
                 'increasing': {'color': 'red'},
                 'decreasing': {'color': 'darkblue'},
                 'position': "bottom"},
        gauge = {'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "lightgray"},
                 'bar': {'color': '#F94144'},
                 'steps' : [
                     {'range': [0, 50], 'color':'#F8F8F8'},
                     {'range': [50, 100], 'color':'#D9D9D9'},
                     ],
                 'threshold' : {
                     'line': {'color': '#B73436', 'width': 4},
                     'thickness': 0.75, 'value': 80
                     },
                 'borderwidth': 1,
                 'bordercolor': "lightgray"
                 }
        ))  

    gfig.update_layout(margin=dict(t=0, b=0, r=0, l=0, pad=0), height=240)
    
    ###########################################################
    # Bar charts - Controlled text sizes, positions and angles
    ###########################################################
    # Get bar chart dataframe from query & callback vs period time
    bardf  = bquery(start_date_object, end_date_object)
    
    # Render Multiple Bars
    cfig = go.Figure(data=[      
        go.Bar(name='EMRs', x=[bardf['weeknum'],bardf['EncounterType']], y=bardf['sEMR'], marker_color='lightgray', orientation = "v", opacity = 0.9, customdata=bardf['ratio']),
        go.Bar(name='FHIR EMRs', x=[bardf['weeknum'],bardf['EncounterType']], y=bardf['sFHIREMR'], marker_color='red', orientation = "v", opacity = 0.9, customdata=bardf['ratio'])
        ])

    cfig.update_layout(barmode='group', height=260,
                       bargap=0.15, # gap between bars of adjacent location coordinates.
                       bargroupgap=0.05, # gap between bars of the same location coordinate.
                       margin=dict(t=0, b=5, r=0, l=5, pad=0),
                       legend=dict(orientation="h",
                                   yanchor="bottom",
                                   y=1.02,
                                   xanchor="right",
                                   x=1),
                       hovermode="y unified",
                       hoverlabel=dict(bgcolor='rgba(255,255,255,0.75)'),
                       uniformtext=dict(mode="hide", minsize=3),
                       plot_bgcolor = 'rgba(255, 255, 255, 0)',
                       paper_bgcolor = 'rgba(255, 255, 255, 0)'
                       )   

    hovertemp =  "<br><b>Chu kỳ thời gian:</b> %{x[0]}<br>"
    hovertemp += "<b>HT Khám chữa bệnh:</b> %{x[1]}<br>"
    hovertemp += "Số hồ sơ: %{y} <br>"
    hovertemp += "Tỷ lệ chuẩn hóa: %{customdata}%"
    cfig.update_traces(hovertemplate=hovertemp,
                       texttemplate='%{y}',
                       textposition='auto',#'outside'
                       textfont_size= 9
                       )
    
    ###########################################################
    # Pie and donut charts 
    ###########################################################
    # Get donut chart dataframe from query & callback vs period time
    donutdf = dquery(start_date_object, end_date_object)
    # render donut chart
    dfig = px.pie(donutdf, values=donutdf['NumGender'], names=donutdf['FHIRGender'], hole=.5,
                  custom_data=[donutdf['Percentage']],
                  color=donutdf['FHIRGender'],
                  color_discrete_map={'Nam':'#12239E',
                                      'Nữ':'#118DFF',
                                      'Không xác định':'#B6E9FF',
                                      },
                  )
    dfig.update_layout(margin=dict(t=0, b=5, r=0, l=0, pad=0), 
                       hoverlabel=dict(bgcolor='rgba(255,255,255,0.05)',
                                       font_size=12,
                                       font_family=fontnames['u']),
                       hovermode="x unified",
                       uniformtext=dict(mode="hide", minsize=3),
                       showlegend=False,     
                       height=220)
    dhovertemp = "<b>Giới tính:</b> %{label}<br>"
    dhovertemp += "Số lượng bệnh nhân: %{value:,} <br>"
    dhovertemp += "Tỷ lệ: %{customdata}%" 
    dfig.update_traces(hovertemplate=dhovertemp,
                       textposition='auto',
                       textfont_size= 12
                       )
    ###########################################################
    # Population pyramid charts 
    ###########################################################
    popdf = pquery(start_date_object, end_date_object)
    # render population pyramid chart
    ########################################################################### 
    age = popdf['AgeRange'].str.slice_replace(0,2, repl='') 
    sr1 = popdf['NumGender_Nam'] 
    sr2 = popdf['NumGender_Nữ']* -1
    psr1 = round(popdf['Percentage_Nam'],2) 
    psr2 = round(popdf['Percentage_Nữ'],2) 
    ###########################################################################
    # Creating instance of the figure
    pfig = go.Figure()
      
    # Adding Male data to the figure    
    mhovertemp = "<br><b>Độ tuổi</b> - %{y} <br>"
    mhovertemp += "Số lượng Nam: %{x:,} <br>" 
    mhovertemp += "Tỷ lệ: %{customdata:,}%"

    pfig.add_trace(go.Bar(
        y= age, x = sr1,
        name = 'Nam',
        orientation = 'h',
        hovertemplate=mhovertemp,
        texttemplate='%{x:,}',
        textposition='auto',
        textfont_size= 11,
        marker=dict(color='#12239E'),
        customdata=psr1,
        ))
      
    # Adding Female data to the figure
    fhovertemp = "<br><b>Độ tuổi</b> - %{y} <br>"
    fhovertemp += "Số lượng nữ: %{text:,}<br>"
    fhovertemp += "Tỷ lệ: %{customdata:,}%"
    
    pfig.add_trace(go.Bar(
        y = age, x = sr2,
        name = 'Nữ',
        orientation = 'h',
        text=-1 * sr2.astype('int'),
        hovertemplate=fhovertemp,
        texttemplate= '%{text:,}',
        textposition='auto',
        textfont_size= 11,
        marker=dict(color='#118DFF'),
        customdata=psr2,
        ))
      
    # Updating the layout for our graph
    pfig.update_layout(
        barmode='overlay', #'relative'
        bargap = 0.1,
        bargroupgap = 0,
        xaxis = dict(
            tickvals = [-6000, -5500, -5000, -4500, -4000, -3500, -3000, -2500, -2000, -1500, -1000,-500,
                        0, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 5500, 6000],
            ticktext = ['6,000', '5,500', '5,000', '4,500', '4,000', '3,500', '3,000', '2,500', '2,000', '1,500', '1,000', '500', '0',
                        '500', '1,000', '1,500', '2,000', '2,500', '3,000', '3,500', '4,000', '4,500', '5,000', '5,500', '6,000'],
            ),
        height=260,
        margin=dict(t=0, b=5, r=0, l=0),
        hoverlabel=dict(bgcolor='rgba(255,255,255,0.75)'),
        hovermode="y unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1),
        plot_bgcolor = 'rgba(255, 255, 255, 0)',
        paper_bgcolor = 'rgba(255, 255, 255, 0)'
        )
    ###########################################################
    # sunburst charts 
    ###########################################################
    # Get sunburst chart dataframe from query & callback vs period time
    if chk_value==[1]:
        sundf = squery(start_date_object, end_date_object, 1)
        sfig = px.sunburst(sundf,
                           path=['Encounter', 'TxResults', 'Gender'], 
                           values='PtNum',
                           custom_data=[sundf['Percentage']],
                           color='Encounter', 
                           color_discrete_map={
                               'KĐT ngoại trú': '#118dff',
                               'Tử vong': '#639CCD',
                               'Nặng': '#639CCD',
                               'Không thay đổi':'#99C9F1',
                               'Đã giảm':'#BADDFC',
                               'Khỏi': '#99C9F1',
                               'ĐT nội trú': '#32268d',
                               },
                           labels={
                                'Encounter': 'Hình thức KCB',
                                'TxResults':'Kết quả ĐT',
                                'Gender': 'Giới tính',
                                'Percentage': 'Tỷ lệ',
                                },
                           branchvalues='total', 
                           maxdepth=3,
                           )
    else:
        sundf = squery(start_date_object, end_date_object, 0)
        sfig = px.sunburst(sundf,
                           path=['Encounter', 'TxResults'], 
                           values='PtNum',
                           custom_data=[sundf['Percentage']],
                           color='Encounter', 
                           color_discrete_map={
                               'KĐT ngoại trú': '#118dff',
                               'Tử vong': '#639CCD',
                               'Nặng': '#639CCD',
                               'Không thay đổi':'#99C9F1',
                               'Đã giảm':'#BADDFC',
                               'Khỏi': '#99C9F1',
                               'ĐT nội trú': '#32268d',
                               },
                           labels={
                                'Encounter': 'Hình thức KCB',
                                'TxResults':'Kết quả ĐT',
                                'Gender': 'Giới tính',
                                'Percentage': 'Tỷ lệ',
                                },
                           branchvalues='total', 
                           maxdepth=2,
                           )

    sfig.update_layout(margin=dict(t=0, b=5, r=0, l=0, pad=0),
                       uniformtext=dict(mode="hide", minsize=9),
                       height=220,
                       )
    
    shovertemp = "<b>%{parent}</b><br>"
    shovertemp += "<b>%{label}</b><br>"
    shovertemp += "Số lượng: %{value:,} <br>"
    shovertemp += "Tỷ lệ: %{customdata[0]:,}%"  
    shovertemp += "<extra></extra>"
    sfig.update_traces(hovertemplate=shovertemp,
                       hoverlabel=dict(bgcolor='rgba(255,255,255,0.05)',
                                       font_size=12,
                                       font_family=fontnames['u']),
                       hoverlabel_bgcolor='rgba(255,255,255,0.001)',
                       hoverlabel_bordercolor='black',
                       selector=dict(type='sunburst')
    )
    
    ###########################################################
    # Horizontal stack bar chart
    ########################################################### 
    hbardf = hbquery(start_date_object, end_date_object)
    hbardf.rename(columns={"maleSum" : "Nam", "femaleSum": "Nữ", "diedSum" : "ca tử vong"}, inplace=True)
    hbarfig = px.bar(hbardf,
                     x=['Nam', 'Nữ', 'ca tử vong'],
                     y='ICD10', orientation='h',
                     hover_data={"variable": True,
                                 'ICDDx': True,
                                 'perMaleSum': ':,.2f',
                                 'perFemaleSum': ':,.2f',
                                 'perDiedSum': ':,.2f',
                                 },
                     labels={"value": "Số lượng",
                             "variable": "Thống kê theo",
                             "ICDDx":"Bệnh chẩn đoán",
                             "perMaleSum": "Tỷ lệ % BN Nam",
                             "perFemaleSum": "Tỷ lệ % BN Nữ",
                             "perDiedSum" : "Tỷ lệ % tử vong"
                             },
                     color='variable',
                     color_discrete_map={
                         'Nam': '#12239E',
                         'Nữ': '#118DFF',
                         'ca tử vong': '#B3B3B3',
                         },
                     height=1200,
                     )

    hbarfig.update_layout(autosize=True)
    hbarfig.update_layout(hovermode="y unified",
                          hoverlabel=dict(bgcolor='rgba(255,255,255,0.75)'),
                          showlegend=False,
                          margin=dict(t=0, b=5, r=0, l=0),
                          yaxis_title=None,
                          xaxis_title=None,
                          uniformtext_minsize=8, uniformtext_mode='hide',
                          plot_bgcolor = 'rgba(255, 255, 255, 0)',
                          paper_bgcolor = 'rgba(255, 255, 255, 0)'
                          )

    hbarfig.update_traces(
        texttemplate='%{x}',
        textposition='auto',
        textfont_size= 11,
        width=0.9,
        )
    hbarfig.update_xaxes(
        showline=True,
        linewidth=1,
        linecolor='#B3B3B3',
        tickmode = 'linear',
        dtick = 5,
        )

    hbarfig.update_yaxes(
        showline=True,
        linewidth=0.25,
        linecolor='#B3B3B3',
        tickmode = 'linear',
        )

    ###########################################################
    #tabdf = tabquery(start_date_object, end_date_object)
    ###########################################################
    # Box plots
    ###########################################################
    # Get data from list FHIR resource
    ###########################################################
    boxdf = boxquery(start_date_object, end_date_object)
    ###########################################################
    # Render Box Plot
    boxfig = px.box(
        boxdf, x="Attributes", y="RscSum",
        hover_data=["PtID","perRsc"],
        color='Attributes',
        color_discrete_map={
            'Condition': '#100352',
            'Encounter': '#2971b3',
            'Observation': '#118dff',
            'ServiceRequest': '#f73a07',
            },
        labels={
            "Attributes": "Loại bản ghi FHIR",
            "RscSum": "SL bản ghi",
            "perRsc": "Tỷ lệ %",
            "PtID": "Mã BN",
            },
        )
        
    boxfig.update_traces(quartilemethod="exclusive")
    boxfig.update_layout(
        height=280, hovermode="x unified",
        hoverlabel=dict(bgcolor='rgba(255,255,255,0.75)'),
        showlegend=False,
        margin=dict(t=0, b=5, r=0, l=0, pad=0),
        yaxis_title=None, # hide label on y-axis
        xaxis_title=None,
        uniformtext_minsize=8, uniformtext_mode='hide',
        plot_bgcolor = 'rgba(255, 255, 255, 0)',
        paper_bgcolor= 'rgba(255, 255, 255, 0)'
        )
    boxfig.update_yaxes(
        showline=True,
        linewidth=0.25,
        linecolor='#B3B3B3',
        tickmode = 'linear',
        dtick = 10,
        )

    # return card info
    ###########################################################
    cardcontent[0] = rslt[0][1]
    cardnote[0] = "Tổng số hồ sơ EMR " + str("{:,}".format(rslt[0][0]))
    cardcontent[1] = "Từ " + start_date_string + " đến " + end_date_string + ' [' + str(n_days) + ' ngày]'
    ###########################################################
    # Advanced card Info
    # [0][0]-[0][1]: Encounter Times - Change
    # [1][0]-[1]][1]: Admission Times - Change
    # [2][0]-[2][1]: Discharge Times - Change
    # [3][0]-[3][1]: Died number - Change
    return statisticsPeriod, gfig, cfig, "{:,}".format(cardcontent[0]), cardnote[0], cardcontent[1], dfig, pfig, adrslt[0][0], adrslt[0][1], adrslt[1][0], adrslt[1][1], adrslt[2][0], adrslt[2][1], adrslt[3][0], adrslt[3][1], cardcontent[1], sfig, hbarfig, boxfig

if __name__ == "__main__":
    app.run_server(debug=True)