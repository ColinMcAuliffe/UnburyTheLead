import os
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import scipy as sp
import seaborn as sns
from matplotlib.ticker import MaxNLocator
from scipy.special import logit,expit
import pymc3 as pm
import cPickle as pickle # python 2

import itertools as itt

#import utlUtilities as utl
sns.set(color_codes=True)

import us

def joinFig(name):
    return os.path.join("Figures",name)

def encodeInteraction(a1,a2):
    n1 = len(np.unique(a1))
    return a2*n1+a1

def hierarchical_studentT(name, shape, mu=0.,cs=5.):
    sigma = pm.HalfCauchy('sigma_{}'.format(name),cs)
    nu    = pm.Exponential('nu_minus_one_{}'.format(name), 1/29.) + 1
    
    return pm.StudentT(name, mu=mu,sd=sigma,nu=nu,shape=shape)

def hierarchical_normal(name, shape, mu=0.,cs=5.):
    delta = pm.Normal('delta_{}'.format(name), 0., 1., shape=shape)
    sigma = pm.HalfCauchy('sigma_{}'.format(name), cs)
    
    return pm.Deterministic(name, mu + delta * sigma)

def getInteractionLabel(l1,l2):
    return [a+", "+b for a,b in itt.product(l1,l2)]

stateData = pd.read_csv(os.path.join("..","CommonData","StateData","StateData.csv"))
logitTrump = stateData["logitTrump"].values
state_region = stateData["region"].values
WhtDiff = stateData["PercentWhiteDiff"].values
regionLabel = ['North East','Mid West','South','West','DC']

print stateData

df = pd.read_table(os.path.join("..","CCES_Data","CCES16_Common_OUTPUT_Jul2017_VV.tab"))

#Age category
df["AGE"] = 2016.-df["birthyr"]
df["AgeCat"] = 0
ageCats = [(18.,29.),
           (30.,44.),
           (45.,64.),
           (65.,150.)]
ageLabel = ["18-29","30-44","45-64","65+"]

for i,bounds in enumerate(ageCats):
    df.ix[(df["AGE"] >= bounds[0])&(df["AGE"] <= bounds[1]), 'AgeCat'] = i

#Education category
#HS grad or GED
HSCode           = [2]
someCollegeCodes = [3,4]
collegeGradCodes = [5,6]

df["EduCat"] = 0 #No HS
df.ix[df["educ"].isin(HSCode)          , 'EduCat'] = 1
df.ix[df["educ"].isin(someCollegeCodes), 'EduCat'] = 2
df.ix[df["educ"].isin(collegeGradCodes), 'EduCat'] = 3
eduLabel = ["No HS Dipl","HS Grad","Some College","College Grad"]

#Race category
df["RaceCat"] = 0 #Race other than BWH
df.ix[df["race"]==1, 'RaceCat'] = 1 #W
df.ix[df["race"]==2, 'RaceCat'] = 2 #B
df.ix[df["race"]==3, 'RaceCat'] = 3 #H
raceLabel = ["Other Race","White","Black","Hispanic"]

#Income category
_0_20           = [1,2]
_20_40          = [3,4]
_40_70          = [5,6,7]
_70_150         = [8,9,10,11]
_150Plus        = [31,12,13,14,15,16]

df["IncCat"] = 0 #Unknown
df.ix[df["faminc"].isin(_0_20)   , 'IncCat'] = 1
df.ix[df["faminc"].isin(_20_40)  , 'IncCat'] = 2
df.ix[df["faminc"].isin(_40_70)  , 'IncCat'] = 3
df.ix[df["faminc"].isin(_70_150) , 'IncCat'] = 4
df.ix[df["faminc"].isin(_150Plus), 'IncCat'] = 5
incLabel = ["Income Refused","Under 20k","20-40k","40-70k","70-150k","Over 150k"]

#Gender
df["gender"] = df["gender"] - 1
genderLabel = ["Female"]

#State
df["STATEFP"] = df["inputstate"]
df = pd.merge(df,stateData[["state_initnum","abbr","STATEFP"]],on="STATEFP")
stateLabel = stateData["abbr"].tolist()
print df

#CC16_422d, on if white people have advantages
#Keep only those who answered, code less than 8
df = df[df["CC16_422d"] < 8]

#Encode strongly agree and somewhat agree as 1, 0 otherwise
df["WhtAdv"] = 0
df.ix[df["CC16_422d"]==1, 'WhtAdv'] = 1 #Strong agree
df.ix[df["CC16_422d"]==2, 'WhtAdv'] = 1 #Somewhat agree

uniq_survey_df = (df.groupby(['RaceCat', 'gender','IncCat', 'EduCat', 'AgeCat', 'state_initnum']).WhtAdv.agg(['sum','size']).reset_index())
print uniq_survey_df

gender_race   = encodeInteraction(uniq_survey_df.gender.values,uniq_survey_df.RaceCat.values)
n_gender_race = len(np.unique(gender_race))

female   = uniq_survey_df.gender.values

race   = uniq_survey_df.RaceCat.values
n_race = len(np.unique(race))

age   = uniq_survey_df.AgeCat.values
n_age = len(np.unique(age))

edu   = uniq_survey_df.EduCat.values
n_edu = len(np.unique(edu))

inc   = uniq_survey_df.IncCat.values
n_inc = len(np.unique(inc))

age_edu   = encodeInteraction(uniq_survey_df.AgeCat.values,uniq_survey_df.EduCat.values)
n_age_edu = len(np.unique(age_edu))
age_eduLabel = getInteractionLabel(ageLabel,eduLabel)
print age_eduLabel

race_edu   = encodeInteraction(race,edu)
n_race_edu = n_race*n_edu
race_eduLabel = getInteractionLabel(raceLabel,eduLabel)

race_inc   = encodeInteraction(race,inc)
n_race_inc = n_race*n_inc
race_incLabel = getInteractionLabel(raceLabel,incLabel)

state = uniq_survey_df.state_initnum.values - 1
n_state = 51
n_region = 5

race_state   = encodeInteraction(race,state)
n_race_state = n_race*n_state
race_stateLabel = getInteractionLabel(raceLabel,stateLabel)

N   = uniq_survey_df['size'].values
yes = uniq_survey_df['sum'].values

NUTS_KWARGS = {'target_accept': 0.99,'max_treedepth':30}
SEED = 4260026 # from random.org, for reproducibility

np.random.seed(SEED)

ndraws = 1000
ntune  = 500

with pm.Model() as model:
    #Baseline intercept
    a0   = pm.Normal('a0',mu=0.,sd=5.)

    #State level predictors
    a_region  = hierarchical_normal('region',n_region)
    a_Trump   = pm.Normal('Trump',mu=0.,sd=5.)
    a_WhtDiff = pm.Normal('WhtDiff',mu=0.,sd=5.)
    mu_state  = a_region[state_region] + a_Trump*logitTrump + a_WhtDiff*WhtDiff
    a_state   = hierarchical_studentT('state',n_state,mu=mu_state)


    #Individual predictors
    a_female = pm.Normal('female',mu=0.,sd=5.)
    a_race       = hierarchical_normal('race',n_race)
    a_age        = hierarchical_normal('age',n_age)
    a_edu        = hierarchical_normal('edu',n_edu)
    a_inc        = hierarchical_normal('inc',n_inc)
    a_race_edu   = hierarchical_normal('race_edu',n_race_edu)
    a_race_state = hierarchical_normal('race_state',n_race_state)
    a_race_inc   = hierarchical_normal('race_inc',n_race_inc)

    eta = a0 + a_female*female + a_race[race] + a_age[age] + a_edu[edu] + a_inc[inc] + a_state[state] + a_race_state[race_state] + a_race_edu[race_edu] + a_race_inc[race_inc]
    p          = pm.math.sigmoid(eta)
    likelihood = pm.Binomial("WhtAdv",N,p,observed=yes)

    trace = pm.sample(draws=ndraws,tune=ntune,njobs=3,init="advi+adapt_diag", random_seed=SEED,nuts_kwargs=NUTS_KWARGS)

    
with open(joinFig('my_model.pkl'), 'wb') as buff:
    pickle.dump(trace, buff)
with open(joinFig('my_model.pkl'), 'rb') as buff:
    trace = pickle.load(buff)  


plt.figure()
axs = pm.traceplot(trace)
plt.savefig(joinFig("Trace.png"))
plt.close()

plt.figure()
axs = pm.forestplot(trace,varnames=["female","race","age","edu","inc"],ylabels=genderLabel+raceLabel+ageLabel+eduLabel+incLabel)
plt.savefig(joinFig("ForestIndividual.png"))
plt.close()

plt.figure(figsize=(10,20))
axs = pm.forestplot(trace,varnames=["state"],ylabels=stateLabel)
plt.savefig(joinFig("ForestState.png"))
plt.close()

plt.figure(figsize=(10,40))
axs = pm.forestplot(trace,varnames=["race_state"],ylabels=race_stateLabel)
plt.savefig(joinFig("ForestRaceState.png"))
plt.close()

plt.figure()
axs = pm.forestplot(trace,varnames=["race_edu"],ylabels=race_eduLabel)
plt.savefig(joinFig("ForestRaceEdu.png"))
plt.close()

plt.figure()
axs = pm.forestplot(trace,varnames=["race_inc"],ylabels=race_incLabel)
plt.savefig(joinFig("ForestRaceInc.png"))
plt.close()

plt.figure()
axs = pm.forestplot(trace,varnames=["Trump","WhtDiff","region"],ylabels=["% Trump"]+regionLabel)
plt.savefig(joinFig("ForestRegion.png"))
plt.close()

print max(np.max(score) for score in pm.gelman_rubin(trace).values())
plt.figure()
pm.energyplot(trace)
plt.savefig(joinFig("Energy.png"))
plt.close()

plt.figure()
axs = sns.jointplot(expit(logitTrump),trace["state"].mean(axis=0))
plt.savefig(joinFig("stateVtrump.png"))
plt.close()
