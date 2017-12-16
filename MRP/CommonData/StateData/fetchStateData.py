import os
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import scipy as sp
import seaborn as sns
from matplotlib.ticker import MaxNLocator
from scipy.special import logit,expit

from census import Census
sns.set(color_codes=True)

import us

def joinFig(name):
    return os.path.join("Figures",name)

states = us.states.STATES
fips2abbr = us.states.mapping('fips','abbr')
abbr2fips = us.states.mapping('abbr','fips')
name2abbr = us.states.mapping('name','abbr')
name2abbr['Washington DC'] = "DC"

stateData = pd.read_csv("2016ElectionState.csv")
stateData["abbr"] = stateData["State"].apply(lambda x: name2abbr[x])
stateData = stateData.sort_values("abbr")
stateData["logitTrump"] = logit(stateData["Trump"]/100.)

#Pull some state data from jastellic's MRP primer
STATE_URL = 'http://www.princeton.edu/~jkastell/MRP_primer/state_level_update.dta'

state_df = (pd.read_stata(STATE_URL,columns=['sstate_initnum', 'sstate','p_evang', 'p_mormon', 'kerry_04']).rename(columns={'sstate_initnum': 'state_initnum', 'sstate': 'abbr'}).assign(p_relig=lambda df: df.p_evang + df.p_mormon))

#Set up abbr to zero indexed initnum mapping
abbr2initnum = {}
for abbr,initnum in zip(state_df["abbr"].values,state_df["state_initnum"].values):
    abbr2initnum[abbr] = initnum-1

DATA_PREFIX = 'http://www.princeton.edu/~jkastell/MRP_primer/'

survey_df = (pd.read_stata(os.path.join(DATA_PREFIX, 'gay_marriage_megapoll.dta'),columns=['race_wbh', 'age_cat', 'edu_cat', 'female','state_initnum', 'state', 'region_cat', 'region', 'statename','poll', 'yes_of_all']).dropna(subset=['race_wbh', 'age_cat', 'edu_cat', 'state_initnum']))

#Set up abbr to zero indexed region mapping
abbr2region = {}
for abbr in state_df["abbr"].values:
    if abbr in ["AK","HI"]:
        abbr2region[abbr] = 3
    else:
        abbr2region[abbr] = int(survey_df[survey_df["state"]==abbr]["region_cat"].values[0])-1

stateData = pd.merge(state_df,stateData,on="abbr")
stateData["region"] = stateData["abbr" ].apply(lambda x: abbr2region[x])
stateData["STATEFP"] = stateData["abbr" ].apply(lambda x: abbr2fips[x])


def censusResponse2df(responseDicts,itemNames,newNames,df):
    newNames.append("STATEFP")
    data=[newNames]
    for d in responseDicts:
        items = [float(d[i]) for i in itemNames]
        items.append(d['state'])
        data.append(items)
    data = pd.DataFrame(data)
    new_header = data.iloc[0] #grab the first row for the header
    data = data[1:] #take the data less the header row
    data.columns = new_header #set the header row as the df header
    data.index = range(len(data))

    df = pd.merge(data,df,on="STATEFP")
    return df
    
ckey = open('census_key.txt').readline().rstrip()

c  = Census(ckey, year=2014)
itemNames  = ['B19013_001E','B19083_001E']
newNames   = ['MedianHHIncome','Gini']
income     = c.acs5.state(itemNames, Census.ALL)
stateData = censusResponse2df(income,itemNames,newNames,stateData)

c  = Census(ckey, year=2010)
itemNames  = ['B19013_001E','B19083_001E']
newNames   = ['MedianHHIncome2010','Gini2010']
income     = c.acs5.state(itemNames, Census.ALL)
stateData = censusResponse2df(income,itemNames,newNames,stateData)

stateData["MHIdiff"] = stateData['MedianHHIncome']-stateData['MedianHHIncome2010']
stateData["Ginidiff"] = stateData['Gini']-stateData['Gini2010']


c  = Census(ckey, year=2010)
itemNames  = ['P0010001','P0030002']
newNames   = ['Pop2010','WhitePop2010']
income     = c.sf1.state(itemNames, Census.ALL)
stateData = censusResponse2df(income,itemNames,newNames,stateData)

c  = Census(ckey, year=2000)
itemNames  = ['P001001','P003003']
newNames   = ['Pop2000','WhitePop2000']
income     = c.sf1.state(itemNames, Census.ALL)
stateData = censusResponse2df(income,itemNames,newNames,stateData)

stateData["PercentWhite2000"] = stateData["WhitePop2000"]/stateData["Pop2000"]
stateData["PercentWhite2010"] = stateData["WhitePop2010"]/stateData["Pop2010"]
stateData["PercentWhiteDiff"] = stateData["PercentWhite2010"]-stateData["PercentWhite2000"]

#Get some irs data on taxes
import urllib2
from bs4 import BeautifulSoup, SoupStrainer

quote_page = "https://www.irs.gov/statistics/soi-tax-stats-historic-table-2"
page = urllib2.urlopen(quote_page)
soup = BeautifulSoup(page,'html.parser', parse_only=SoupStrainer('a'))
i = 0
salt = []
tax  = []
data = [["abbr","totalTaxPC","SALT_DeductionsPC"]]
for link in soup:
    if link.has_attr('href'):
	href = link['href']
	fname = href.split("/")[-1]
	conds = "xlsx" in href and fname[0:2]=="15" and "cm" not in fname and "us" not in fname and "oa" not in fname
	if conds:
	    abbr = fname[6:8].upper()
            df = pd.read_excel(href,skiprows=6,skipfooter=28)
	    totReturnsIdx          = df[df[" "]=="Number of returns"].index.tolist()[0]
	    deductionsOnTaxPaidIdx = df[df[" "]=="Total taxes paid:  Number"].index.tolist()[0]
	    totTaxLiabilityIdx     = df[df[" "]=="Total tax liability:  [17] Number"].index.tolist()[0]

	    numReturns     = df.ix[totReturnsIdx,1]
	    numSALTReturns = df.ix[deductionsOnTaxPaidIdx,1]
	    totalSALT      = df.ix[deductionsOnTaxPaidIdx+1,1]
	    numReturnsWTax = df.ix[totTaxLiabilityIdx,1]
	    totalTax       = df.ix[totTaxLiabilityIdx+1,1]
            data.append([abbr,totalSALT/numSALTReturns,totalTax/numReturns])

data = pd.DataFrame(data)
new_header = data.iloc[0] #grab the first row for the header
data = data[1:] #take the data less the header row
data.columns = new_header #set the header row as the df header
data.index = range(len(data))
stateData = pd.merge(data,stateData,on="abbr").sort_values("state_initnum")

print len(stateData)
sns.pairplot(stateData[["MedianHHIncome","Gini","Trump","MHIdiff","Ginidiff","PercentWhiteDiff","totalTaxPC"]])
plt.savefig("pair.png")

stateData.to_csv("StateData.csv")
