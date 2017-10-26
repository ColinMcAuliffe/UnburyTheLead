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
from matplotlib.ticker import MaxNLocator,FuncFormatter
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
SEED = 4260026 # from random.org, for reproducibility

np.random.seed(SEED)

ndraws = 5000
ntune  = 500
nppdraws = 300

df = pd.read_csv(os.path.join("ElectionResults","2016Votes_RVs.csv"))

df["CongRate"]   = (df["Wenzel"]+df["RF"])/df["Registered Voters"]
df["RFRate"]     = df["RF"]/(df["Wenzel"]+df["RF"])
df["Clinton"]    = df["Clinton"].astype(np.int64)
df["Trump"]      = df["Trump"].astype(np.int64)
df["Wenzel"]     = df["Wenzel"].astype(np.int64)
df["RF"]         = df["RF"].astype(np.int64)
df["Registered Voters"] = df["Registered Voters"].astype(np.int64)

df["PresVotes"] = df["Clinton"]+df["Trump"]
df["CongVotes"] = df["Wenzel"]+df["RF"]

gdfCousub = gpd.read_file(os.path.join("NJ11Shapefiles","NJ11Cousub.shp"))
gdfCousub = gdfCousub.merge(df,on="NAME")

countyFIPS = np.unique(gdfCousub["COUNTYFP"].values)

print gdfCousub

#Use morris and sussex as training data
morrisSussex = ['027','037']
passaicEssex = ['013','031']

dfMS = gdfCousub[gdfCousub["COUNTYFP"].isin(morrisSussex)]
dfPE = gdfCousub[gdfCousub["COUNTYFP"].isin(passaicEssex)]

print dfMS
registered = dfMS["Registered Voters"].values
congVotes  = dfMS["CongVotes"].values
mhi        = np.log(dfMS["MedianHouseholdIncome"].values)
meanMhi    = np.mean(mhi)
mhiMc      = mhi - meanMhi

registeredPE = dfPE["Registered Voters"].values
congVotesPE  = dfPE["CongVotes"].values
rfRate       = dfPE["RFRate"].values
mhiPE        = np.log(dfPE["MedianHouseholdIncome"].values)
mhiPEMc      = mhiPE - meanMhi

#with pm.Model() as model:
#    b0       = pm.Normal("b0",mu=0.,sd=5.)
#    bMHI     = pm.Normal("MHI",mu=0.,sd=5.)
#
#    turnout = b0 + bMHI*mhiMc
#    alpha   = pm.Beta("Oops",alpha=1.,beta=9.)
#    p       = alpha*0.5 + (1.-alpha)*pm.math.sigmoid(turnout)
#
#    obs     = pm.Binomial('obs', registered, p, observed=congVotes)
#    
#    trace = pm.sample(draws=ndraws,tune=ntune,njobs=3,init="advi+adapt_diag", random_seed=SEED,nuts_kwargs=NUTS_KWARGS)
#    
#plt.figure()
#axs = pm.traceplot(trace)
#plt.savefig(os.path.join("Figures","TraceNJ11.png"))
#plt.close()
#
#with open('my_modelNJ11.pkl', 'wb') as buff:
#    pickle.dump(trace, buff)

with open('my_modelNJ11.pkl', 'rb') as buff:
    trace = pickle.load(buff)  

pp_samples = []
for rand_loc in np.random.randint(0, len(trace), 3000):
    rand_sample = trace[rand_loc]
    prob = rand_sample["Oops"]*0.5 + (1.-rand_sample["Oops"])*expit(rand_sample["b0"] + rand_sample['MHI']*mhiPEMc)
    sample = [np.random.binomial(n,p) for p,n in zip(prob,registeredPE)]
    pp_samples.append(sample)

pp_samples = np.array(pp_samples)
registeredPE = registeredPE.astype(np.float64)
pp_diff      = pp_samples-congVotesPE[np.newaxis,:]
totalVotes   = np.sum(pp_diff,axis=1)

twoParty = np.sum(congVotesPE)+np.sum(congVotes)
g = sns.distplot(100.*totalVotes/float(twoParty))
plt.xlabel("Percentage of the 2 Party Vote from Matching Turnout Trends in all Counties")
plt.savefig(os.path.join("Figures","VoteDiff.png"))
plt.close()

pp_samples = pp_samples/registeredPE[np.newaxis,:]
pp_mean = np.mean(pp_samples,axis=0)
pp_stdv = np.std(pp_samples,axis=0)*2.



fig = plt.figure()
ax  = fig.add_subplot(111)
mIdx = dfMS[dfMS["COUNTYFP"]=="027"].index.tolist()
ax.scatter(dfMS[dfMS["COUNTYFP"]=="027"]["MedianHouseholdIncome"],dfMS[dfMS["COUNTYFP"]=="027"]["CongRate"],color='b',label="Morris")
ax.scatter(dfMS[dfMS["COUNTYFP"]=="037"]["MedianHouseholdIncome"],dfMS[dfMS["COUNTYFP"]=="037"]["CongRate"],color='g',label="Sussex")
ax.scatter(dfPE[dfPE["COUNTYFP"]=="013"]["MedianHouseholdIncome"],dfPE[dfPE["COUNTYFP"]=="013"]["CongRate"],color='y',label="Essex")
ax.scatter(dfPE[dfPE["COUNTYFP"]=="031"]["MedianHouseholdIncome"],dfPE[dfPE["COUNTYFP"]=="031"]["CongRate"],color='m',label="Passaic")

evl = np.linspace(np.log(50000.),np.log(190000.),100)
cr  = trace["Oops"][:,np.newaxis]*0.5 + (1.-trace["Oops"][:,np.newaxis])*expit(trace["b0"][:,np.newaxis] + trace['MHI'][:,np.newaxis]*(evl-meanMhi))
cr  = cr.T
## Calculate credible regions and plot over the datapoints
dfp = pd.DataFrame(np.percentile(cr,[2.5, 25, 50, 75, 97.5], axis=1).T
                     ,columns=['025','250','500','750','975'])
dfp['x'] = np.exp(evl)

pal = sns.color_palette('Reds')
plt.subplots_adjust(top=0.95)


ax.fill_between(dfp['x'], dfp['025'], dfp['975'], alpha=0.5,color=pal[1])
ax.fill_between(dfp['x'], dfp['250'], dfp['750'], alpha=0.5,color=pal[4])
ax.plot(dfp['x'], dfp['500'], alpha=0.6, color=pal[5], label='Trendline for Morris and Sussex')
plt.legend()


ax.set_ylabel("Congressional Turnout by Municipality")
ax.set_xlabel("Municipality Median Household Income")
ax.get_xaxis().set_major_formatter(FuncFormatter(lambda x, p: format(int(x), ',')))
ax.legend(loc=4)
ax.set_title("2016 Congressional Turnout in Passaic and Essex Fell Below Average")
fig.savefig(os.path.join("Figures","NJ11.png"))
plt.close()

fig = plt.figure()
ax  = fig.add_subplot(111)

ax.scatter(np.exp(mhi),dfMS["CongRate"].values)
ax.scatter(np.exp(mhiPE),dfPE["CongRate"].values)
ax.errorbar(np.exp(mhiPE),pp_mean,yerr=pp_stdv,fmt="o",label="County Intercepts +- 2 stdv",color='r')

ax.set_ylabel("Congressional Turnout by Municipality")
ax.set_xlabel("Municipality Median Household Income")
ax.get_xaxis().set_major_formatter(FuncFormatter(lambda x, p: format(int(x), ',')))
ax.legend(loc=4,ncol=2)
fig.savefig(os.path.join("Figures","NJ11pp.png"))
plt.close()


print "Max GR score: ",max(np.max(score) for score in pm.gelman_rubin(trace).values())
plt.figure()
pm.energyplot(trace)
plt.savefig(os.path.join("Figures","Energy.png"))
plt.close()

