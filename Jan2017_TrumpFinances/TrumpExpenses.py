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
    disbDates   = [datetime.strptime(d, '%d-%b-%y') for d in disbDates]
    disbs       = zip(disbDates,disbAmounts)
    disbs.sort(key=lambda x: x[0])
    disbDates,disbAmounts = zip(*disbs)
    cumDisbs = np.cumsum(disbAmounts)/1000000.

    return disbDates,cumDisbs

#Get vectors of dates and cumulative donations for plotting
def getCumulativeDonations(df):
    donationDates = df.contb_receipt_dt.values.tolist()
    donationAmounts = df.contb_receipt_amt.values.tolist()
    donationDates = [datetime.strptime(d, '%d-%b-%y') for d in donationDates]
    donations = zip(donationDates,donationAmounts)
    donations.sort(key=lambda x: x[0])
    donationDates,donationAmounts = zip(*donations)
    cumDonations = np.cumsum(donationAmounts)/1000000.
    return donationDates,cumDonations


#Filter disbursements by recipients which are trump businesses
def isTrumpBusiness(row):
    recipientName = row["recipient_nm"]
    exclude = ['TRUMP, ERIC','TRUMP, DONALD JR.','TRUMP, DONALD J.','TRUMP, LARA','TRUMP, ERIC','TRUMP, DONALD JR']
    if "TRUMP" in recipientName and recipientName not in exclude:
        return True
    if recipientName == "TAG AIR, INC.":
        return True

    return False

#Filter donations by dollar amount
def filterByDollarAmt(df,amt,useAbs=True):
    if useAbs:
        return df[np.abs(df['contb_receipt_amt'])<amt]
    else:
        return df[df['contb_receipt_amt']<amt and df['contb_receipt_amt']>0.]


#Filter retired donors
def isRetired(row):
    strList = ["RETIRED"]
    return row["contbr_occupation"] in strList or row["contbr_employer"] in strList

#Filter self employed donors
def isSelfEmployed(row):
    strList = ["SELF-EMPLOYED","SELF EMPLOYED","SELFEMPLOYED"]
    return row["contbr_occupation"] in strList or row["contbr_employer"] in strList

#Filter unemployed or disabled donors
def isUnemployedOrDisabled(row):
    strList = ["UNEMPLOYED","DISABLED"]
    return row["contbr_occupation"] in strList or row["contbr_employer"] in strList

#Load FEC data containing disbursement info
dfTrump = pd.read_csv("P80001571D-ALL.csv",index_col=False)
#Get disbursements to trump businesses only
dfTrump = dfTrump[dfTrump.apply(isTrumpBusiness,axis=1)]
print "Total disbursements to trump companies ",dfTrump["disb_amt"].sum()

#tabulate results by recipient
uniqueRecipients = set(dfTrump["recipient_nm"].tolist())
tabData = [["Recipient","Total Disbursements"]]
disbTotals = []
for recip in uniqueRecipients:
    dfRecip = dfTrump[dfTrump["recipient_nm"]==recip]
    disbTotals.append((recip,dfRecip["disb_amt"].sum()))

disbTotals.sort(key=lambda x: x[1],reverse=True)
disbTotalsStr = [(x[0],"${:,}".format(int(x[1]))) for x in disbTotals]
utl.html_table(tabData+disbTotalsStr,"disbursements.html")
    
#Load FEC data containing donation info
dfDonations = pd.read_csv("P80001571-ALL.csv",index_col=False)

#Get donation less than 50 dollarS
dfDonationsLT50 = filterByDollarAmt(dfDonations,50.,useAbs=True)
#Donations from retirees
dfDonationsRet = dfDonations[dfDonations.apply(isRetired,axis=1)]
#Donations from self employed individuals
dfDonationsSE  = dfDonations[dfDonations.apply(isSelfEmployed,axis=1)]
#Unemployed or disabled individuals
dfDonationsUD  = dfDonations[dfDonations.apply(isUnemployedOrDisabled,axis=1)]

tabData = [["Group","Total Donations"]]
tabData.append(["Retired"               ,"${:,}".format(int(dfDonationsRet["contb_receipt_amt"].sum()))])
tabData.append(["Self Employed"         ,"${:,}".format(int(dfDonationsSE["contb_receipt_amt"].sum()))])
tabData.append(["Amounts less than $50" ,"${:,}".format(int(dfDonationsLT50["contb_receipt_amt"].sum()))])
tabData.append(["Unemployed or Disabled","${:,}".format(int(dfDonationsUD["contb_receipt_amt"].sum()))])
utl.html_table(tabData,"donations.html")

stateData = [["STATEFP","Contrib","Contrib_U50","Contrib_Retired"]]
for state in states:
    dfState = dfDonations[dfDonations["contbr_st"]==state]
    dfStateLT50 = dfDonationsLT50[dfDonationsLT50["contbr_st"]==state]
    dfStateRet  = dfDonationsRet[dfDonationsRet["contbr_st"]==state]
    stateData.append([abbr2fips[state],dfState["contb_receipt_amt"].sum(),dfStateLT50["contb_receipt_amt"].sum(),dfStateRet["contb_receipt_amt"].sum()])

stateData = pd.DataFrame(stateData)
new_header = stateData.iloc[0] #grab the first row for the header
stateData = stateData[1:] #take the data less the header row
stateData.columns = new_header #set the header row as the df header
stateData.index = range(len(stateData))
stateData.to_csv("Donations_by_state.csv")

dfStates = utl.mergeGDF(shapeFileStates,"Donations_by_state.csv","STATEFP")

print "plotting donations by state"
utl.plotGDF(os.path.join(figDir,"contrib.png"),dfStates,"USALL",colorby="data",colorCol="Contrib",cmapScale=1.0E-6,cmap=plt.cm.Greens,title="Contributions From Individuals by State (Millions)")
utl.plotGDF(os.path.join(figDir,"thumb.png"),dfStates,"USALL",colorby="data",colorCol="Contrib",cmap=plt.cm.Greens,cbar=False)
utl.plotGDF(os.path.join(figDir,"contribU50.png"),dfStates,"USALL",colorby="data",colorCol="Contrib_U50",cmapScale=1.0E-6,cmap=plt.cm.Greens,title="Contributions Under 50 Dollars by State (Millions)")
utl.plotGDF(os.path.join(figDir,"contribRet.png"),dfStates,"USALL",colorby="data",colorCol="Contrib_Retired",cmapScale=1.0E-6,cmap=plt.cm.Greens,title="Contributions From Retirees by State (Millions)")


fig = plt.figure(figsize=(12,6))
ax  = fig.add_subplot(111)
disbDates,cumDisbs         = getCumulativeDisbursements(dfTrump)
ax.plot(disbDates,cumDisbs,label="Cumulative Disbursements to Trump Companies",color='r',linewidth=3)
donationDates,cumDonations = getCumulativeDonations(dfDonationsRet)
ax.plot(donationDates,cumDonations,label="Cumulative Itemized Donations From Retirees",color='g',linewidth=3)
donationDates,cumDonations = getCumulativeDonations(dfDonationsSE)
ax.plot(donationDates,cumDonations,label="Cumulative Itemized Donations From Self Employed Individuals",color='c',linewidth=3)
ax.set_ylabel("Millions of Dollars")
ax.grid()
ax.set_xlim((disbDates[0],datetime(2016, 12, 1, 0, 0)))
ax.legend(loc=2)
fig.savefig(os.path.join(figDir,"disbursements-donations.png"))

