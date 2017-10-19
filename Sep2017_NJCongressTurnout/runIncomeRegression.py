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

NUTS_KWARGS = {'target_accept': 0.99,'max_treedepth':30}
SEED = 4260026 # from random.org, for reproducibility

np.random.seed(SEED)

ndraws = 5000
ntune  = 500

gdfCousub = gpd.read_file(os.path.join("NJShapeFilewData","NJCousub.shp"))

#drop 
drop = ["camdentavistockboro","camdenpinevalleyboro"]
split = ["oceanstaffordtwp","essexbloomfieldtwp","bergenteanecktwp","essexmontclairtwp","essexnewarkcity","middlesexoldbridgetwp","unionscotchplainstwp","salemsalemcity","essexwestorangetwp","oceanpointpleasantboro","hudsonjerseycity","gloucestereastgreenwichtwp","hudsonkearnytown","unionuniontwp","hudsonbayonnecity","monmouthmiddletowntwp"]
gdfCousub = gdfCousub[~gdfCousub["CMname"].isin(drop)]
gdfCousub = gdfCousub[~gdfCousub["CMname"].isin(split)]
gdfCousub.index = range(len(gdfCousub))

df = gdfCousub[["CMname","District","COUNTYFP","B19013_001","MHI_COU","CTVPct","Total","Registered","Ballots Ca","CountyName","Margin"]].copy()
df["B19013_001"] = df["B19013_001"].astype(np.float64)
df["MHI_COU"] = df["MHI_COU"].astype(np.float64)
df["logMhi"] = np.log(df["B19013_001"])
df["logMhiCou"] = np.log(df["MHI_COU"])
df["Turnout"] = df["Total"].astype(np.float64)/df["Ballots Ca"].astype(np.float64)

print df.sort_values("Turnout")

df["District"] = df["District"] - 1
dnames = np.unique(df["District"].values)
distMargin=[]
for d in dnames:
    distMargin.append(df.ix[df["District"]==d,"Margin"].values[0])
meanDistMargin = np.mean(distMargin)
distMarginMc   = distMargin-meanDistMargin


district = df["District"].values
n_dist   = len(np.unique(district))
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
#
#    bMargDist = pm.Normal("MargDist",mu=0.,sd=5.)
#    muDist    = bMargDist*distMarginMc
#    bDistrict = hierarchical_studentT("District",mu=muDist,shape=n_dist)
#
#    turnout = b0 + bDistrict[district] + bMHI*mhiMc
#    alpha   = pm.Beta("Oops",alpha=1.,beta=9.)
#    p       = alpha*0.5 + (1.-alpha)*pm.math.sigmoid(turnout)
#
#    obs     = pm.Binomial('obs', df["Ballots Ca"].values, p, observed=df["Total"].values)
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

districtMean = trace["District"].mean(axis=0)
districtStdv = trace["District"].std(axis=0)

fig, ax = plt.subplots(1,1, figsize=(7,7))

evl = np.linspace(0.,1.,100)
cr  = trace["MargDist"][:,np.newaxis]*(evl-meanDistMargin)
cr  = cr.T
## Calculate credible regions and plot over the datapoints
dfp = pd.DataFrame(np.percentile(cr,[2.5, 25, 50, 75, 97.5], axis=1).T
                     ,columns=['025','250','500','750','975'])
dfp['x'] = evl*100.

pal = sns.color_palette('Greens')
plt.subplots_adjust(top=0.95)

ax.fill_between(dfp['x'], dfp['025'], dfp['975'], alpha=0.5,color=pal[1], label='95% Confidence Region')
ax.fill_between(dfp['x'], dfp['250'], dfp['750'], alpha=0.5,color=pal[4], label='50% Confidence Region')
ax.plot(dfp['x'], dfp['500'], alpha=0.6, color=pal[5], label='Median Trendline')
plt.legend()

colors = ["b","r","r","r","b","b","r","b","b","b","r","b"]
for i in range(len(distMargin)):
    ax.annotate(str(i+1),(distMargin[i]*100.,districtMean[i]),color=colors[i])
ax.set_ylabel("District Intercept")
ax.set_xlabel("Margin of the Winning Candidate as a % of the District Vote")
ax.legend(loc=1)
ax.set_xlim((0.,80.))
fig.savefig(os.path.join("Figures","DistrictMarg.png"))
plt.close()


print "Max GR score: ",max(np.max(score) for score in pm.gelman_rubin(trace).values())
plt.figure()
pm.energyplot(trace)
plt.savefig(os.path.join("Figures","Energy.png"))
plt.close()

axs = pm.forestplot(trace,varnames=["District"])
plt.savefig(os.path.join("Figures","forestD.png"))
plt.close()
