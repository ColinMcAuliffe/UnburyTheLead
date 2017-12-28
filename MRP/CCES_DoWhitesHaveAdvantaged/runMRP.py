import os
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import scipy as sp
import seaborn as sns
from matplotlib.ticker import MaxNLocator
from scipy.special import logit,expit
from scipy.stats import expon,halfcauchy
import pymc3 as pm
import cPickle as pickle # python 2
from matplotlib.ticker import MaxNLocator

import itertools as itt

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
    #nu    = pm.HalfCauchy('nu_minus_one_{}'.format(name), 10.) + 1
    
    return pm.StudentT(name, mu=mu,sd=sigma,nu=nu,shape=shape)

def hierarchical_normalGV(name, shape, idx, mu=0.,cs=5.):
    delta = pm.Normal('delta_{}'.format(name), 0., 1., shape=shape)


    sigma_upp = pm.HalfCauchy('sigma_upp{}'.format(name), cs)
    sigma     = pm.HalfCauchy('sigma_{}'.format(name), sigma_upp,shape=len(np.unique(idx)))
    
    return pm.Deterministic(name, mu + delta * sigma[idx])

def hierarchical_normal(name, shape, mu=0.,cs=5.):
    delta = pm.Normal('delta_{}'.format(name), 0., 1., shape=shape)
    sigma = pm.HalfCauchy('sigma_{}'.format(name), cs)
    
    return pm.Deterministic(name, mu + delta * sigma)

def getInteractionLabel(l1,l2):
    return [a+", "+b for a,b in itt.product(l1,l2)]

def standardize(a):
    return (a - np.mean(a))/np.std(a)


#Load state data
stateData = pd.read_csv(os.path.join("..","CommonData","StateData","StateData.csv"))
print stateData[["abbr","state_initnum","region"]]
#Make DC part of the northeast
stateData.ix[stateData["region"]==4,'region'] = 0

state_region = stateData["region"].values
logitTrump_St = stateData["logitTrump"].values
logitWhite_St = logit(stateData["PercentWhite2010"].values)
logitEvang_St = logit(stateData["p_evang"].values/100.)
MHI_St        = standardize(stateData["MedianHHIncome"].values)
WhtDiffSt    = ((stateData["PercentWhiteDiff"]-np.mean(stateData["PercentWhiteDiff"]))/np.std(stateData["PercentWhiteDiff"])).values

#Load CD data
CDData = pd.read_csv(os.path.join("..","CommonData","CongDistrictData","CDData.csv"))
logitTrump_CD = logit(CDData["Trump 2016"].values/100.)
logitEvang_CD = logit(CDData["Evangel. Prot Congregation"].values/100.)
MHI_CD        = standardize(CDData["MedianHHIncome"].values)
TrumpSwing_CD = standardize(CDData["R16-R08"].values)
logitCTV_CD   = logit(CDData["CTVpct"].values)

district_state = CDData["state_initnum"].values


df = pd.read_table(os.path.join("..","CCES_Data","CCES16_Common_OUTPUT_Jul2017_VV.tab"))

#Age category
df["AGE"] = 2016.-df["birthyr"]
df["AgeCat"] = 0
df.ix[df["AGE"]<35, 'AgeCat'] = 1 #Millenial
ageLabel = ["Millenial"]

#Education category
HSCode           = [2]
someCollegeCodes = [3,4]
collegeGradCodes = [5,6]

df["EduCat"] = 0 #No college degree
df.ix[df["educ"].isin(collegeGradCodes), 'EduCat'] = 1
eduLabel = ["College Grad"]

#Race category
df["RaceCat"] = 0
df.ix[df["race"]==1, 'RaceCat'] = 1 #White

#Income category
under40k = [1,2,3,4]
df["IncCat"] = 0 #Unknown
df.ix[df["faminc"].isin(under40k)   , 'IncCat'] = 1

#Gender
df["gender"] = df["gender"] - 1

#State
df["STATEFP"] = df["inputstate"]
df = pd.merge(df,stateData[["state_initnum","abbr","STATEFP"]],on="STATEFP")
stateLabel = stateData["abbr"].tolist()

print np.unique(df["state_initnum"])
print len(np.unique(df["state_initnum"]))

#CC16_422d, on if white people have advantages
#Keep only those who answered, code less than 8
df = df[df["CC16_422d"] < 8]

#Encode strongly agree and somewhat agree as 1, 0 otherwise
df["WhtAdv"] = 0
df.ix[df["CC16_422d"]==1, 'WhtAdv'] = 1 #Strong agree
df.ix[df["CC16_422d"]==2, 'WhtAdv'] = 1 #Somewhat agree

#Condense survey responses by category
uniq_survey_df = (df.groupby(['RaceCat', 'gender', 'EduCat', 'AgeCat','IncCat', 'state_initnum']).WhtAdv.agg(['sum','size']).reset_index())
print uniq_survey_df

female    = uniq_survey_df.gender.values
white     = uniq_survey_df.RaceCat.values
millenial = uniq_survey_df.AgeCat.values
college   = uniq_survey_df.EduCat.values
under40k  = uniq_survey_df.IncCat.values

state = uniq_survey_df.state_initnum.values - 1
n_state = 51

N   = uniq_survey_df['size'].values
yes = uniq_survey_df['sum'].values
print "Yes: ",np.sum(yes)

NUTS_KWARGS = {'target_accept': 0.99,'max_treedepth':30}
SEED = 4260026 # from random.org, for reproducibility

np.random.seed(SEED)

ndraws = 1000
ntune  = 500


with pm.Model() as model:
    #Baseline intercept
    a0   = pm.Normal('baseline',mu=0.,sd=5.)

    #State level predictors
    a_region     = hierarchical_normal('region',4,cs=0.1)
    a_Trump      = pm.Normal('Trump',mu=0.,sd=5.)
    a_Evang      = pm.Normal('Evang',mu=0.,sd=5.)
    a_MdInc      = pm.Normal('MdInc',mu=0.,sd=5.)
    mu_state  = a_region[state_region] + a_Trump*logitTrump_St + a_Evang*logitEvang_St + a_MdInc*MHI_St
    a_state   = hierarchical_normalGV('state',n_state,state_region,mu=mu_state,cs=0.1)

    #Individual predictors
    a_female          = pm.Normal('female',mu=0.,sd=5.)
    a_white           = pm.Normal('white',mu=0.,sd=5.)
    a_millenial       = pm.Normal('millenial',mu=0.,sd=5.)
    a_college         = pm.Normal('college',mu=0.,sd=5.)
    a_under40k        = pm.Normal('under40k',mu=0.,sd=5.)
    a_femaleMillenial = pm.Normal('femaleMillenial',mu=0.,sd=5.)
    a_whiteFemale     = pm.Normal('whiteFemale',mu=0.,sd=5.)
    a_whiteCollege    = pm.Normal('whiteCollege',mu=0.,sd=5.)
    a_whiteMillenial  = pm.Normal('whiteMillenial',mu=0.,sd=5.)
    a_whiteUnder40k   = pm.Normal('whiteUnder40k',mu=0.,sd=5.)

    eta = a0 + a_female*female + a_white*white + a_millenial*millenial + a_college*college + a_under40k*under40k + a_whiteFemale*white*female + a_femaleMillenial*female*millenial + a_whiteCollege*white*college + a_whiteMillenial*white*millenial + a_whiteUnder40k*white*under40k + a_state[state]
    p         = pm.math.sigmoid(eta)
    likelihood = pm.Binomial("WhtAdv",N,p,observed=yes)

    trace = pm.sample(draws=ndraws,tune=ntune,njobs=3,init="advi+adapt_diag", random_seed=SEED,nuts_kwargs=NUTS_KWARGS)

    plt.figure()
    hcp5  = pm.HalfCauchy.dist(.1)
    hcpp5 = pm.HalfCauchy.dist(.1)
    axs = pm.traceplot(trace,varnames=["sigma_region","sigma_uppstate"],priors=[hcp5,hcpp5])
    plt.savefig(joinFig("TraceV.png"))
    plt.close()

    
with open(joinFig('my_model.pkl'), 'wb') as buff:
    pickle.dump(trace, buff)
with open(joinFig('my_model.pkl'), 'rb') as buff:
    trace = pickle.load(buff)  


plt.figure()
g = sns.jointplot(logitTrump_St,trace["state"].mean(axis=0))
plt.savefig(joinFig("distVtrump.png"))
plt.close()

plt.figure()
g = sns.jointplot(logitEvang_St,trace["state"].mean(axis=0))
plt.savefig(joinFig("distVevang.png"))
plt.close()

plt.figure()
g = sns.jointplot(MHI_St,trace["state"].mean(axis=0))
plt.savefig(joinFig("distVmhi.png"))
plt.close()

plt.figure()
axs = pm.traceplot(trace)
plt.savefig(joinFig("Trace.png"))
plt.close()

plt.figure()
axs = pm.forestplot(trace,varnames=['baseline',"female","white","millenial","college","under40k","femaleMillenial","whiteFemale","whiteMillenial","whiteCollege","whiteUnder40k"],rhat=False)
plt.savefig(joinFig("ForestIndividual.png"))
plt.close()

plt.figure()
axs = pm.forestplot(trace,varnames=["Trump","Evang","MdInc","region"],rhat=False)
plt.savefig(joinFig("ForestState.png"))
plt.close()

