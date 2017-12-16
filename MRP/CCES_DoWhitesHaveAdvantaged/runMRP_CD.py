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
    return os.path.join("Figures_CD",name)

def encodeInteraction(a1,a2):
    n1 = len(np.unique(a1))
    return a2*n1+a1

def hierarchical_studentT(name, shape, mu=0.,cs=5.):
    sigma = pm.HalfCauchy('sigma_{}'.format(name),cs)
    nu    = pm.Exponential('nu_minus_one_{}'.format(name), 1/29.) + 1
    #nu    = pm.HalfCauchy('nu_minus_one_{}'.format(name), 10.) + 1
    
    return pm.StudentT(name, mu=mu,sd=sigma,nu=nu,shape=shape)

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
stateData = stateData[stateData["abbr"]!="DC"]
stateData = stateData.sort_values("abbr")
stateData.index = range(len(stateData))

logitTrumpSt = stateData["logitTrump"].values
state_region = stateData["region"].values
logitWhiteSt = logit(stateData["PercentWhite2010"].values)
logitEvangSt = logit(stateData["p_evang"].values/100.)
WhtDiffSt    = ((stateData["PercentWhiteDiff"]-np.mean(stateData["PercentWhiteDiff"]))/np.std(stateData["PercentWhiteDiff"])).values

#Load CD data
CDData = pd.read_csv(os.path.join("..","CommonData","CongDistrictData","CDData.csv"))
logitTrump_CD = logit(CDData["Trump 2016"].values/100.)
logitEvang_CD = logit(CDData["Evangel. Prot Congregation"].values/100.)
MHI_CD        = standardize(CDData["MedianHHIncome"].values)
TrumpSwing_CD = standardize(CDData["R16-R08"].values)
logitCTV_CD   = logit(CDData["CTVpct"].values)

district_state = CDData["state_initnum"].values

regionLabel = ['North East','Mid West','South','West']


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
#Exclude DC
df = df[df["abbr"]!="DC"]

#Congressional District
#Alaska, Delaware, Montana, North Dakota, South Dakota, Vermont, and Wyoming
oneDist = ["AK","DE","MT","ND","SD","VT","WY"]
def getCDName(row):
    if row["abbr"] in oneDist:
        dname = "AL"
    else:
        dname = str(row["cdid115"]).zfill(2)
    return row["abbr"]+"-"+dname
df["CD"] = df.apply(getCDName,axis=1)
df = pd.merge(df,CDData[["CD_initnum","CD"]],on="CD")

#CC16_422d, on if white people have advantages
#Keep only those who answered, code less than 8
df = df[df["CC16_422d"] < 8]

#Encode strongly agree and somewhat agree as 1, 0 otherwise
df["WhtAdv"] = 0
df.ix[df["CC16_422d"]==1, 'WhtAdv'] = 1 #Strong agree
df.ix[df["CC16_422d"]==2, 'WhtAdv'] = 1 #Somewhat agree

#Respondent distributions
fig, axs = plt.subplots(1, 2, sharey=True)

rdisp = (df.groupby(['CD_initnum']).WhtAdv.agg(['sum','size']).reset_index())
axs[0] = sns.distplot(rdisp["size"],ax=axs[0],kde=False,norm_hist=False)
axs[0].set_ylabel("Number of Congressional Districts")
axs[0].set_xlabel("Number of Respondents")

rdisp = (df.groupby(['AgeCat','CD_initnum']).WhtAdv.agg(['sum','size']).reset_index())
axs[1] = sns.distplot(rdisp[rdisp["AgeCat"]==1]["size"],ax=axs[1],kde=False,norm_hist=False)
axs[1].set_xlabel("Number of Millenial Respondents")
fig.savefig(joinFig("AgeDist.png"))
plt.close()

#Condense survey responses by category
uniq_survey_df = (df.groupby(['RaceCat', 'gender', 'EduCat', 'AgeCat','IncCat', 'CD_initnum']).WhtAdv.agg(['sum','size']).reset_index())
print uniq_survey_df

female    = uniq_survey_df.gender.values
white     = uniq_survey_df.RaceCat.values
millenial = uniq_survey_df.AgeCat.values
college   = uniq_survey_df.EduCat.values
under40k  = uniq_survey_df.IncCat.values

district = uniq_survey_df.CD_initnum.values
n_district = 435

N   = uniq_survey_df['size'].values
yes = uniq_survey_df['sum'].values
print "Yes: ",np.sum(yes)

NUTS_KWARGS = {'target_accept': 0.99,'max_treedepth':30}
SEED = 4260026 # from random.org, for reproducibility

np.random.seed(SEED)

ndraws = 3000
ntune  = 500


with pm.Model() as model:
    #Baseline intercept
    a0   = pm.Normal('baseline',mu=0.,sd=5.)

    #District level predictors
    a_Trump      = pm.Normal('Trump',mu=0.,sd=5.)
    a_Evang      = pm.Normal('Evang',mu=0.,sd=5.)
    a_MdInc      = pm.Normal('MdInc',mu=0.,sd=5.)
    mu_district  = a_Trump*logitTrump_CD + a_Evang*logitEvang_CD + a_MdInc*MHI_CD
    a_district   = hierarchical_studentT('district',n_district,mu=mu_district)

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

    #Individual - district interactions
    a_districtMill   = hierarchical_normal('districtMillenial',n_district)

    eta = a0 + a_female*female + a_white*white + a_millenial*millenial + a_college*college + a_under40k*under40k + a_whiteFemale*white*female + a_femaleMillenial*female*millenial + a_whiteCollege*white*college + a_whiteMillenial*white*millenial + a_whiteUnder40k*white*under40k + a_district[district] + a_districtMill[district]*millenial
    p         = pm.math.sigmoid(eta)
    likelihood = pm.Binomial("WhtAdv",N,p,observed=yes)

    trace = pm.sample(draws=ndraws,tune=ntune,njobs=3,init="advi+adapt_diag", random_seed=SEED,nuts_kwargs=NUTS_KWARGS)

    
with open(joinFig('my_model.pkl'), 'wb') as buff:
    pickle.dump(trace, buff)
with open(joinFig('my_model.pkl'), 'rb') as buff:
    trace = pickle.load(buff)  

plt.figure()
g = sns.jointplot(trace["sigma_district"],trace["nu_minus_one_district"])
g.set_axis_labels("District Group Standard Dev.","District Group Normality Parameter")
plt.tight_layout()
plt.savefig(joinFig("joint_SigmaNu.png"))
plt.close()

print "normality param mean and median: ",np.mean(trace["nu_minus_one_district"]),np.median(trace["nu_minus_one_district"])

plt.figure()
g = sns.jointplot(logitTrump_CD,trace["district"].mean(axis=0))
plt.savefig(joinFig("distVtrump.png"))
plt.close()

plt.figure()
g = sns.jointplot(logitEvang_CD,trace["district"].mean(axis=0))
plt.savefig(joinFig("distVevang.png"))
plt.close()

plt.figure()
g = sns.jointplot(MHI_CD,trace["district"].mean(axis=0))
plt.savefig(joinFig("distVmhi.png"))
plt.close()

plt.figure()
axs = pm.traceplot(trace)
plt.savefig(joinFig("Trace.png"))
plt.close()

plt.figure()
axs = pm.traceplot(trace,varnames=["nu_minus_one_district","sigma_district","sigma_districtMillenial","district","districtMillenial"],combined=True)
axs[0][0].set_xlim((0.0,100.0))
axs[1][0].set_xlim((0.0,0.35))
axs[2][0].set_xlim((0.0,0.35))
axs[3][0].set_xlim((-2.0,2.0))
axs[4][0].set_xlim((-2.0,2.0))
plt.savefig(joinFig("Trace2.png"))
plt.close()

plt.figure()
axs = pm.forestplot(trace,varnames=['baseline',"female","white","millenial","college","under40k","femaleMillenial","whiteFemale","whiteMillenial","whiteCollege","whiteUnder40k"],rhat=False)
plt.savefig(joinFig("ForestIndividual.png"))
plt.close()

plt.figure()
axs = pm.forestplot(trace,varnames=["Trump","Evang","MdInc"],ylabels=["% Trump","% Evangelical","Income"],rhat=False)
plt.savefig(joinFig("ForestDistrictPredictors.png"))
plt.close()

print max(np.max(score) for score in pm.gelman_rubin(trace).values())
plt.figure()
pm.energyplot(trace)
plt.savefig(joinFig("Energy.png"))
plt.close()

cookDCCC = CDData[CDData["All DCCC Targets (As of 12/2017)"]>0.]
targetIdx    = cookDCCC["CD_initnum"].values
targetLabels = cookDCCC["CD"].values

#White millenial male college
wmmc = expit(trace['baseline'][:,np.newaxis] + trace["district"][:,targetIdx] + trace["districtMillenial"][:,targetIdx] + trace["white"][:,np.newaxis] + trace["millenial"][:,np.newaxis] + trace["college"][:,np.newaxis] + trace["whiteCollege"][:,np.newaxis] + trace["whiteMillenial"][:,np.newaxis])
wm   = expit(trace['baseline'][:,np.newaxis] + trace["district"][:,targetIdx] + trace["white"][:,np.newaxis])

fig = plt.figure()
ax = fig.add_subplot(111)
ax = sns.distplot(wm[:,53],ax=ax,label="White Male Non Millenial\n No College",color='b')
ax = sns.distplot(wmmc[:,53],ax=ax,label="White Male Millenial\n College Grad",color='g')
ax.set_xlabel("Probability NJ-11 Residents Agreeing that Whites have Advantages")
ax.axvline(0.5,ls=":")
ax.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,ncol=2, mode="expand", borderaxespad=0.)
fig.savefig(joinFig("wmmc.png"))

n = len(cookDCCC)
means = np.mean(wmmc,axis=0)
stdvs = np.std(wmmc,axis=0)

srtIdx = np.argsort(means)[::-1]

fig = plt.figure(figsize =(6,17) )
ax  = fig.add_subplot(111)
ax.errorbar(means[srtIdx],-1.*np.array(range(n)),xerr=stdvs[srtIdx],fmt="o")
ticks = [-l for l in range(n)]
ax.set_yticks(ticks)
ax.set_yticklabels(targetLabels[srtIdx])
ax.axvline(0.5,ls=":")
ax.set_xlim((0.2,.8))
ax.set_ylim((np.min(ticks)-1,np.max(ticks)+1))
ax.set_title("Probability of a White Male Millenial College Grad in Key 2018 \nCongressional Districts Agreeing that Whites have Advantages ")
ax.set_xlabel("Probability")
fig.savefig(joinFig("DCCC_Targets.png"))

