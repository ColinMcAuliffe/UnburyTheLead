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

CDData = pd.read_csv("ResultsByDistrict08_16.csv")
CDData["logitTrump"] = logit(CDData["Trump 2016"]/100.)

df = pd.read_csv("CDReligion.csv")
df["CD"] = df["ABBcode"].apply(lambda x: x[0:2] + "-" + x[2:].zfill(2))
df["CD"] = df["CD"].str.replace("00","AL")
df["CD_initnum"] = range(len(df["CD"]))

CDData = pd.merge(CDData,df,on="CD")

CDData["abbr"] = CDData["CD"].apply(lambda x: x[0:2])
CDData["state_initnum"] = 0
for i,a in enumerate(np.unique(CDData["abbr"])):
    CDData.ix[CDData["abbr"]==a,"state_initnum"] = i


CookDCCC = pd.read_csv("Cook_DCCC.csv")
CookDCCC = CookDCCC.fillna(0.)
CookDCCC["CD"] = CookDCCC["District"]
CDData = pd.merge(CDData,CookDCCC,on="CD")

print CookDCCC[CookDCCC["All DCCC Targets (As of 12/2017)"]>0.]["CD"]

CDData["R16-R12"] = CDData["Trump 2016"] - CDData["Romney 2012"]
CDData["R16-R08"] = CDData["Trump 2016"] - CDData["McCain 2008"]

def censusResponse2df(responseDicts,itemNames,newNames,df):
    newNames.append("CD")
    data=[newNames]
    for d in responseDicts:
        items = [float(d[i]) for i in itemNames]
        items.append(fips2abbr[d['state']]+"-"+d['congressional district'])
        data.append(items)
    data = pd.DataFrame(data)
    new_header = data.iloc[0] #grab the first row for the header
    data = data[1:] #take the data less the header row
    data.columns = new_header #set the header row as the df header
    data.index = range(len(data))
    data["CD"] = df["CD"].str.replace("00","AL")

    df = pd.merge(data,df,on="CD")
    return df
    
ckey = open('census_key.txt').readline().rstrip()

c  = Census(ckey, year=2014)
itemNames  = ['B19013_001E','B19083_001E','B08006_001E','B08006_002E']
newNames   = ['MedianHHIncome','Gini','totalWorkers','CTVWorkers']
income     = c.acs5.state_district(itemNames, Census.ALL, Census.ALL)
CDData = censusResponse2df(income,itemNames,newNames,CDData)

#c  = Census(ckey, year=2010)
#itemNames  = ['P0010001','P0030002']
#newNames   = ['Pop2010','WhitePop2010']
#income     = c.sf1.state_district(itemNames, Census.ALL, Census.ALL)
#CDData = censusResponse2df(income,itemNames,newNames,CDData)
#
#CDData["PercentWhite2010"] = CDData["WhitePop2010"]/CDData["Pop2010"]
CDData['CTVpct'] = CDData['CTVWorkers']/CDData['totalWorkers']

sns.pairplot(CDData[["MedianHHIncome","Gini","Trump 2016","Evangel. Prot Congregation","R16-R12","R16-R08","CTVpct"]])
plt.savefig("pair.png")

CDData.to_csv("CDData.csv")
