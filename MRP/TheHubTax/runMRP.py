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
from matplotlib.gridspec import GridSpec

#import utlUtilities as utl
sns.set(color_codes=True)

import us

def joinFig(name):
    return os.path.join("Figures",name)

df = pd.read_csv(os.path.join("Poll","TheHub.csv"))

#Age category
df["AgeCat"] = 0
ageCats = [(18.,44.),
           (45.,64.),
           (65.,150.)]

for i,bounds in enumerate(ageCats):
    df.ix[(df["D101"] >= bounds[0])&(df["D101"] <= bounds[1]), 'AgeCat'] = i
ageLabel = ["Age: <45","45-64","65+"]

#Education category
#HS grad or GED
HSCode           = [2,3] #Graduated HS or attended tech school
someCollegeCodes = [4,5] #S
collegeGradCodes = [6,7]

df["EduCat"] = 0 #No HS
#df.ix[df["D102"].isin(HSCode)          , 'EduCat'] = 1
#df.ix[df["D102"].isin(someCollegeCodes), 'EduCat'] = 2
df.ix[df["D102"].isin(collegeGradCodes), 'EduCat'] = 1
#eduLabel = ["Edu: No HS Dipl","HS Grad","Some College","4yr Degree and up"]
eduLabel = ["College Grad"]

#Race category
df["RaceCat"] = 0 #Race other than BWH
df.ix[df["D300"]==1, 'RaceCat'] = 1 #B
df.ix[df["D300"]==2, 'RaceCat'] = 2 #W
df.ix[df["D300"]==3, 'RaceCat'] = 3 #H
raceLabel = ["Race: other","Black","White","Hisp"]

#Gender
df["gender"] = df["D100"] - 1
genderLabel = ["Female"]

#Income category
df["IncomeCat"] = df["D900"] - 1
incomeLabel = ["Income: <25k","25k-50k","50k-75k","75k-100k","100k-150k",">150k","Unknown"]

#State
df["state_initnum"] = df["D400" ] - 1

#Encode strongly agree and somewhat agree as 1, 0 otherwise
df["CorpCut"] = 0
df.ix[df["BAT5R1"]==1, 'CorpCut'] = 1 #Strong agree
#df.ix[df["BAT5R1"]==2, 'CorpCut'] = 1 #Somewhat agree

uniq_survey_df = (df.groupby(['RaceCat', 'gender', 'EduCat', 'AgeCat', 'state_initnum']).CorpCut.agg(['sum','size']).reset_index())
print uniq_survey_df

def hierarchical_normal(name, shape, mu=0.,cs=5.):
    delta = pm.Normal('delta_{}'.format(name), 0., 1., shape=shape)
    sigma = pm.HalfCauchy('sigma_{}'.format(name), cs)
    
    return pm.Deterministic(name, mu + delta * sigma)

def encodeInteraction(a1,a2):
    n1 = len(np.unique(a1))
    return a2*n1+a1

female   = uniq_survey_df.gender.values

race   = uniq_survey_df.RaceCat.values
n_race = len(np.unique(race))

age   = uniq_survey_df.AgeCat.values
n_age = len(np.unique(age))

collegeGrad   = uniq_survey_df.EduCat.values
#n_edu = len(np.unique(edu))

#inc   = uniq_survey_df.IncomeCat.values
#n_inc = len(np.unique(inc))

state = uniq_survey_df.state_initnum.values
n_state = 51

N   = uniq_survey_df['size'].values
yes = uniq_survey_df['sum'].values


#State data
state_df = pd.read_csv(os.path.join("..","CommonData","StateData","StateData.csv"))
logitTrump = state_df["logitTrump"].values
Gini = state_df["Gini"].values
MedianIncome = np.log(state_df["MedianHHIncome"].values)-np.mean(np.log(state_df["MedianHHIncome"].values))
region = state_df["region"].values
n_region = 5
regionLabel = ['North East','Mid West','South','West','DC']
print state_df
print np.sum(yes)

NUTS_KWARGS = {'target_accept': 0.99,'max_treedepth':30}
SEED = 4260026 # from random.org, for reproducibility

np.random.seed(SEED)

ndraws = 1000
ntune  = 500
with pm.Model() as model:
    #Baseline intercept
    a0   = pm.Normal('a0',mu=0.,sd=5.)

    #State level predictors
    a_region = hierarchical_normal('region',n_region)
    a_Trump   = pm.Normal('Trump',mu=0.,sd=5.)
    a_MedInc  = pm.Normal('MedianIncome',mu=0.,sd=5.)
    #a_Gini  = pm.Normal('Gini',mu=0.,sd=5.)
    mu_state = a_region[region] + a_MedInc*MedianIncome+ a_Trump*logitTrump#+ a_Gini*Gini
    a_state  = hierarchical_normal('state',n_state,mu=mu_state)

    #Individual predictors
    a_female = pm.Normal('female',mu=0.,sd=5.)
    a_collegeGrad = pm.Normal('collegeGrad',mu=0.,sd=5.)
    a_race = hierarchical_normal('race',n_race)
    a_age = hierarchical_normal('age',n_age)

    eta = a0 + a_female*female + a_collegeGrad*collegeGrad + a_race[race] + a_age[age] + a_state[state]
    p          = pm.math.sigmoid(eta)
    likelihood = pm.Binomial("CorpCut",N,p,observed=yes)

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
axs = pm.forestplot(trace,varnames=["female","race","age","collegeGrad"],ylabels=genderLabel+raceLabel+ageLabel+eduLabel)
plt.savefig(joinFig("ForestIndividual.png"))
plt.close()

plt.figure(figsize=(10,10))
axs = pm.forestplot(trace,varnames=["state"],ylabels=state_df["abbr"].values)
plt.savefig(joinFig("ForestState.png"))
plt.close()

plt.figure()
axs = pm.forestplot(trace,varnames=["Trump","MedianIncome","region"],ylabels=["Trump","MedianIncome"]+regionLabel)
#axs = pm.forestplot(trace,varnames=["Trump","MedianIncome","Gini","region"])
plt.savefig(joinFig("ForestRegion.png"))
plt.close()

print max(np.max(score) for score in pm.gelman_rubin(trace).values())
plt.figure()
pm.energyplot(trace)
plt.savefig(joinFig("Energy.png"))
plt.close()
