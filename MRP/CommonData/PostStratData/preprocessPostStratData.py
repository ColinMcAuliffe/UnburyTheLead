import os
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import scipy as sp
import seaborn as sns
from matplotlib.ticker import MaxNLocator
from scipy.special import logit,expit
#import utlUtilities as utl
sns.set(color_codes=True)
from us import states

df = pd.read_csv(os.path.join("Data","acs5yr2015.csv"))

df = df[df["AGE"] > 17]
df.index = range(len(df))
df["AgeCat"] = 0
ageCats = [(18.,29.),
           (30.,44.),
           (45.,64.),
           (65.,150.)]

for i,bounds in enumerate(ageCats):
    df.ix[(df["AGE"] >= bounds[0])&(df["AGE"] <= bounds[1]), 'AgeCat'] = i

#HS grad or GED
HSCode           = [63,64]
someCollegeCodes = [65,71,81]
collegeGradCodes = [101,114,115,116]

df["EduCat"] = 0
df.ix[df["EDUCD"].isin(HSCode)          , 'EduCat'] = 1
df.ix[df["EDUCD"].isin(someCollegeCodes), 'EduCat'] = 2
df.ix[df["EDUCD"].isin(collegeGradCodes), 'EduCat'] = 3

print len(df)
print len(df[df["EduCat"]==0])
print np.unique(df[df["EduCat"]==0].EDUCD)
print np.unique(df["RACED"])
print np.unique(df["SEX"])

df_agged = (df.groupby(['STATEFIP', 'AgeCat', 'EduCat','SEX']).PERWT.agg({'n': 'sum'}).reset_index())
print df_agged
#print df_agged['n'].sum()
#CENSUS_URL = 'http://www.princeton.edu/~jkastell/MRP_primer/poststratification%202000.dta'
#
#census_df = (pd.read_stata(CENSUS_URL).rename(columns=lambda s: s.lstrip('c_').lower()))
#print np.unique(census_df['region'])
