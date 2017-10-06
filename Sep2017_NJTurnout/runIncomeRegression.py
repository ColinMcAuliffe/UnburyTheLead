import os
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import itertools as itt
import sys
import time
import savReaderWriter as sRW
import pymc3 as pm
from theano import shared
import scipy as sp
import cPickle as pickle # python 2
import seaborn as sns
import networkx as nx
from matplotlib.ticker import MaxNLocator
from scipy.special import logit,expit
import utlUtilities as utl
sns.set(color_codes=True)

def plot_pp_glm(trace,ax,cou,xdata=None,ydata=None, eval=None, lm=None,label=None, samples=30, **kwargs):

    # Set default plotting arguments
    if 'lw' not in kwargs and 'linewidth' not in kwargs:
        kwargs['lw'] = .2
    if 'c' not in kwargs and 'color' not in kwargs:
        kwargs['c'] = 'k'

    kwargs['lw'] *= 6
    kwargs['alpha'] = 1.
    ax.plot(np.exp(eval), lm(eval, trace,cou=cou), **kwargs)
    kwargs.pop('label', None)

    if xdata is not None:
        ax.scatter(xdata,ydata,label=label,color=kwargs['color'])

    return ax


NUTS_KWARGS = {'target_accept': 0.99,'max_treedepth':30}
#NUTS_KWARGS = {'target_accept': 0.99}
SEED = 4260026 # from random.org, for reproducibility

np.random.seed(SEED)

ndraws = 5000
ntune  = 1000
nppdraws = 300

gdfCousub = gpd.read_file(os.path.join("NJShapeFilewData","NJCousub.shp"))

#drop 
drop = ["camdentavistockboro","camdenpinevalleyboro"]
gdfCousub = gdfCousub[~gdfCousub["CMname"].isin(drop)]
gdfCousub.index = range(len(gdfCousub))

countyFIPS = np.unique(gdfCousub["COUNTYFP"].values)

df = gdfCousub[["COUNTYFP","B19013_001","MHI_COU","CTVPct","Ballots Ca","Registered","CountyName"]].copy()
df["B19013_001"] = df["B19013_001"].astype(np.float64)
df["MHI_COU"] = df["MHI_COU"].astype(np.float64)
df["logMhi"] = np.log(df["B19013_001"])
df["logMhiCou"] = np.log(df["MHI_COU"])
df["Turnout"] = df["Ballots Ca"].astype(np.float64)/df["Registered"].astype(np.float64)

df["County"] = 0
countyNames = []
mhiCou  = []
regCou  = []
for i,c in enumerate(countyFIPS):
    df.ix[df["COUNTYFP"]==c,"County"] = i
    countyNames.append(df.ix[df["COUNTYFP"]==c,"CountyName"].values[0])
    mhiCou.append(df.ix[df["COUNTYFP"]==c,"MHI_COU"].values[0])
    regCou.append(df.ix[df["COUNTYFP"]==c,"Registered"].sum())
mhiCou     = np.log(mhiCou)
meanMhiCou = np.mean(mhiCou)
mhiCouMc   = mhiCou - meanMhiCou

regCou     = np.log(regCou)
meanRegCou = np.mean(regCou)
regCouMc   = regCou - meanRegCou


county = df["County"].values
n_cou  = len(np.unique(county))
mhi       = df["logMhi"].values
meanMhi   = np.mean(mhi)
mhiMc     = mhi - meanMhi
Turnout   = df["Turnout"].values

g = sns.jointplot(df["logMhi"].values,df["Turnout"])
g.set_axis_labels("Log Median Household Income in NJ Municipalities", "Turnout Rate in NJ Municipalities")
plt.tight_layout()
plt.savefig(os.path.join("Figures","logMhiVturnout.png"))
plt.close()

def hierarchical_studentT(name, shape, mu=0.,cs=5.):
    sigma = pm.HalfCauchy('sigma_{}'.format(name),cs)
    nu    = pm.Exponential('nu_minus_one_{}'.format(name), 1/29.) + 1
    
    return pm.StudentT(name, mu=mu,sd=sigma,nu=nu,shape=shape)

def hierarchical_normal(name, shape, mu=0.,cs=5.):
    delta = pm.Normal('delta_{}'.format(name), 0., 1., shape=shape)
    sigma = pm.HalfCauchy('sigma_{}'.format(name),cs)
    
    return pm.Deterministic(name, mu + delta * sigma)


#with pm.Model() as model:
#    b0       = pm.Normal("b0",mu=0.,sd=5.)
#    bMHI     = pm.Normal("MHI",mu=0.,sd=5.)
#    bMHICou  = pm.Normal("MHICou",mu=0.,sd=5.)
#    bRegCou  = pm.Normal("RegCou",mu=0.,sd=5.)
#    muCou    = bMHICou*mhiCouMc + bRegCou*regCouMc
#    bCounty  = hierarchical_studentT("County",mu=muCou,shape=n_cou)
#
#    turnout = b0 + bCounty[county] + bMHI*mhiMc
#    alpha   = pm.Beta("Oops",alpha=1.,beta=9.)
#    p       = alpha*0.5 + (1.-alpha)*pm.math.sigmoid(turnout)
#
#    obs     = pm.Binomial('obs', df["Registered"].values, p, observed=df["Ballots Ca"].values)
#    
#    trace = pm.sample(draws=ndraws,tune=ntune,init="advi+adapt_diag",njobs=3, random_seed=SEED,nuts_kwargs=NUTS_KWARGS)
#    
#plt.figure()
#axs = pm.traceplot(trace)
#plt.savefig(os.path.join("Figures","Trace.png"))
#plt.close()
#
#with open('my_model.pkl', 'wb') as buff:
#    pickle.dump(trace, buff)



with open('my_model.pkl', 'rb') as buff:
    trace = pickle.load(buff)  

fig = plt.figure()
ax  = fig.add_subplot(111)

evl = np.log(np.linspace(50000,110000,100))

for rand_loc in np.random.randint(0, len(trace), 300):
    rand_sample = trace[rand_loc]
    result = rand_sample['MHICou']*(evl-meanMhiCou)
    ax.plot(np.exp(evl), result,color='r',alpha=0.05)

result = trace['MHICou'].mean()*(evl-meanMhiCou)
ax.plot(np.exp(evl), result,color='r',linewidth=4,label="Regression Line for County Intercepts")

countyMean = trace["County"].mean(axis=0)
countyStdv = trace["County"].std(axis=0)
ax.errorbar(np.exp(mhiCou),countyMean,yerr=countyStdv,fmt="o",label="County Intercepts +- 1 stdv")
ax.set_ylabel("County Intercept")
ax.set_xlabel("County Median Household Income")
ax.legend(loc=2)
fig.savefig(os.path.join("Figures","CountyIncome.png"))
plt.close()


fig = plt.figure()
ax  = fig.add_subplot(111)

evl = np.log(np.linspace(10000,600000,100))

for rand_loc in np.random.randint(0, len(trace), 300):
    rand_sample = trace[rand_loc]
    result = rand_sample['RegCou']*(evl-meanRegCou)
    ax.plot(np.exp(evl), result,color='r',alpha=0.05)

result = trace['RegCou'].mean()*(evl-meanRegCou)
ax.plot(np.exp(evl), result,color='r',linewidth=4,label="Regression Line for County Intercepts")

ax.errorbar(np.exp(regCou),countyMean,yerr=countyStdv,fmt="o",label="County Intercepts +- 1 stdv")
ax.set_ylabel("County Intercept")
ax.set_xlabel("County Total Registered")
ax.legend(loc=1)
fig.savefig(os.path.join("Figures","CountyReg.png"))
plt.close()


print "Max GR score: ",max(np.max(score) for score in pm.gelman_rubin(trace).values())
plt.figure()
pm.energyplot(trace)
plt.savefig(os.path.join("Figures","Energy.png"))
plt.close()

axs = pm.forestplot(trace,varnames=["County"],ylabels=countyNames)
plt.savefig(os.path.join("Figures","forest.png"))
plt.close()

def lmR(x, trace,cou=0): 
    result = trace["Oops"].mean()*0.5 + (1.-trace["Oops"].mean())*expit(trace['b0'].mean() + trace['County'].mean(axis=0)[cou] + trace['MHI'].mean()*(x-meanMhi))
    return result

keyP= "Turnout"
keyReg = "B19013_001"

colors = [plt.cm.cool(i) for i in np.linspace(0, 1, n_cou)]
cidx   = range(n_cou)

fig,(ax1)  = plt.subplots(1,1,figsize=(10,6))
evl = np.linspace(np.min(mhi),np.max(mhi), 1000)

for co,idx in zip(colors,cidx):
    xdat = df[df["County"]==idx][keyReg]
    ydat = df[df["County"]==idx][keyP]
    cn   = df.ix[df["County"]==idx,"CountyName"].values[0]
    ax1  = plot_pp_glm(trace,ax1,idx ,xdata=xdat,ydata=ydat, eval=evl, lm=lmR, samples=nppdraws, label = cn, color=co  , alpha=.15)
ax1.legend(loc=4,ncol=5)
ax1.set_xlabel("Median Household Income")
ax1.set_ylabel("Turnout Rate")
ax1.set_title("Presidential Turnout")
fig.savefig(os.path.join("Figures","MHI_Turnout.png"))
    
fig,(ax1)  = plt.subplots(1,1,figsize=(10,6))
evl = np.linspace(np.min(mhi),np.max(mhi), 1000)

cnames = ["essex","morris","hunterdon"]
colors = ['g','y','m']
i = 0
for idx in cidx:
    cn   = df.ix[df["County"]==idx,"CountyName"].values[0]
    if cn not in cnames: continue
    xdat = df[df["County"]==idx][keyReg]
    ydat = df[df["County"]==idx][keyP]
    ax1  = plot_pp_glm(trace,ax1,idx ,xdata=xdat,ydata=ydat, eval=evl, lm=lmR, samples=nppdraws, label = cn, color=colors[i]  , alpha=.15)
    i +=1
ax1.legend(loc=4,ncol=5)
ax1.set_xlabel("Median Household Income")
ax1.set_ylabel("Turnout Rate")
ax1.set_title("Presidential Turnout")
#ax1.set_ylim((0.4,0.85))
fig.savefig(os.path.join("Figures","MHI_TurnoutME.png"))
