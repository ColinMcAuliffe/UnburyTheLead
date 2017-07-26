from collections import defaultdict

import matplotlib.pyplot as plt
import utlUtilities as utl
import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime
import us

abbr2fips = us.states.mapping('abbr','fips')

# list of state abbreviations
states = ['AL','AK','AZ','AR','CA','CO','CT','DC','DE','FL','GA','HI','ID','IL','IN','IA','KS','KY','LA','ME','MD','MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ','NM','NY','NC','ND','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VT','VA','WA','WV','WI','WY']

figDir       = "Figures"

#Note, the state and county shape files must be downloaded from the census website and unzipped in the location as indicated below
shapeFileStates   = "../CommonData/ShapeFiles/cb_2015_us_state_500k/cb_2015_us_state_500k.shp"



#Get vectors of dates and cumulative disbursements for plotting
def getCumulativeDisbursements(df):
    disbDates   = df.disb_dt.values.tolist()
    disbAmounts = df.disb_amt.values.tolist()
    disbDatesFmt = []
    for d in disbDates:
        try:
            dd = datetime.strptime(d, '%d-%b-%y')
        except:
            dd = datetime.strptime(d.split()[0], '%Y-%m-%d')
        disbDatesFmt.append(dd)
    disbs       = zip(disbDatesFmt,disbAmounts)
    disbs.sort(key=lambda x: x[0])
    disbDates,disbAmounts = zip(*disbs)
    cumDisbs = np.cumsum(disbAmounts)/1000000.

    return disbDates,cumDisbs

#Filter disbursements by recipients which are trump businesses
def isTrumpBusiness(row,key="recipient_nm"):
    recipientName = row[key]
    #exclude reimbusements for trump surrogates named trump, and for transfers to trump committees
    exclude = ['TRUMP, ERIC','TRUMP, DONALD JR.','TRUMP, DONALD J.','TRUMP, LARA','TRUMP, ERIC','TRUMP, DONALD JR','TRUMP MAKE AMERICA GREAT AGAIN COMMITTEE','TRUMP VICTORY']
    
    if "TRUMP" in recipientName and recipientName not in exclude:
        return True
    if recipientName == "TAG AIR, INC.":
        return True
    if "MAR-A-LAGO" in recipientName:
        return True

    return False

def getDisbTotalsByRecipient(df):
    uniqueRecipients = set(df["recipient_nm"].tolist())
    disbTotals = []
    for recip in uniqueRecipients:
        dfRecip = df[df["recipient_nm"]==recip]
        disbTotals.append((recip,dfRecip["disb_amt"].sum()))
    disbTotals.sort(key=lambda x: x[1],reverse=True)
    disbTotalsStr = [(x[0],"${:,}".format(int(x[1]))) for x in disbTotals]
    return disbTotalsStr

keepers = ["recipient_name","disbursement_amount","disbursement_date","disbursement_description"]
keepers16 = ["recipient_nm","disb_desc","disb_dt","disb_amt"]
#Quarter 1 in 2017
dfTrumpQ1_17 = pd.read_csv(os.path.join("Q1_2017","data.csv"),index_col=False)
#Remove uneeded columns and rename to match 2016 data
for column in dfTrumpQ1_17:
    if column not in keepers:
        del dfTrumpQ1_17[column]
dfTrumpQ1_17.columns = keepers16

#Quarter 2 in 2017
dfTrumpQ2_17 = pd.read_csv(os.path.join("Q2_2017","data.csv"),index_col=False)
#Remove uneeded columns and rename to match 2016 data
for column in dfTrumpQ2_17:
    if column not in keepers:
        del dfTrumpQ2_17[column]
dfTrumpQ2_17.columns = keepers16

#All 2016 data
dfTrump16 = pd.read_csv("P80001571D-ALL.csv",index_col=False)
#Remove undeeded columns
for column in dfTrump16:
    if column not in keepers16:
        del dfTrump16[column]

#Concatenate
dfTrump = pd.concat([dfTrumpQ1_17,dfTrumpQ2_17,dfTrump16])
disbTotals = getDisbTotalsByRecipient(dfTrump)
for i,j in disbTotals[0:10]:
    print i,j
print "----"

dfTrumpLC = dfTrump[dfTrump["disb_desc"]=="LEGAL CONSULTING"]
dfTrumpLC = dfTrumpLC[dfTrumpLC.apply(isTrumpBusiness,axis=1)]
print dfTrumpLC

#Get disbursements to trump businesses only
dfTrump16 = dfTrump16[dfTrump16.apply(isTrumpBusiness,axis=1)]
dfTrumpQ1_17 = dfTrumpQ1_17[dfTrumpQ1_17.apply(isTrumpBusiness,axis=1)]
dfTrumpQ2_17 = dfTrumpQ2_17[dfTrumpQ2_17.apply(isTrumpBusiness,axis=1)]
print "Total disbursements to trump companies through 2016 ",dfTrump16["disb_amt"].sum()
print "Total disbursements to trump companies in Q1 2017 "  ,dfTrumpQ1_17["disb_amt"].sum()
print "Total disbursements to trump companies in Q2 2017 "  ,dfTrumpQ2_17["disb_amt"].sum()
#tabulate results by recipient
tabData = [["Recipient","Total Disbursements"]]

disbTotals = getDisbTotalsByRecipient(dfTrump16)
utl.html_table(tabData+disbTotals,"disbursements16.html")

disbTotals = getDisbTotalsByRecipient(dfTrumpQ1_17)
utl.html_table(tabData+disbTotals,"disbursementsQ1_17.html")

disbTotals = getDisbTotalsByRecipient(dfTrumpQ2_17)
utl.html_table(tabData+disbTotals,"disbursementsQ2_17.html")

#Concatenate
dfTrump = pd.concat([dfTrumpQ1_17,dfTrumpQ2_17,dfTrump16])
print "Total disbursements to trump companies ",dfTrump["disb_amt"].sum()
disbTotals = getDisbTotalsByRecipient(dfTrump)
utl.html_table(tabData+disbTotals,"disbursementsAll.html")

#tabulate results by recipient
uniqueRecipients = set(dfTrump["recipient_nm"].tolist())
tabData = [["Recipient","Total Disbursements"]]
    
fig = plt.figure(figsize=(12,6))
ax  = fig.add_subplot(111)
disbDates,cumDisbs         = getCumulativeDisbursements(dfTrump)
ax.plot(disbDates,cumDisbs,label="Cumulative Disbursements to Trump Companies",color='r',linewidth=3)
ax.set_ylabel("Millions of Dollars")
ax.grid()
ax.set_xlim((disbDates[0],datetime(2017, 7, 1, 0, 0)))
ax.legend(loc=2)
fig.savefig(os.path.join(figDir,"disbursements.png"))

