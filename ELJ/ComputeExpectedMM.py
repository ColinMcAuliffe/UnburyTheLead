import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib.patches import Rectangle

import pandas as pd
import numpy as np
import os
import us
from scipy import stats

from ELJcommon import getDemVotesAndSeats,get_spasym,get_asymFromPct,getExpAsym,varWithShrinkage,betaMOM,list2df,colorBins,getExpMMandT

states = us.states.STATES
abbr2name = us.states.mapping('abbr', 'name')

figDir       = "Figures"
dataDir      = "Data"

congress    = pd.read_csv(os.path.join(dataDir,"congressImputed.csv"))
data        = pd.read_csv(os.path.join(dataDir,"historicStdv.csv"))
stateData   = pd.read_csv(os.path.join(dataDir,"historicSAsym.csv"),dtype={"STATEFP": object})
dataAB      = pd.read_csv(os.path.join(dataDir,"betaParams.csv"))
dataABState = pd.read_csv(os.path.join(dataDir,"betaParamsState.csv"))


cyc70 = [1972,1974,1976,1978,1980]
cyc80 = [1982,1984,1986,1988,1990]
cyc90 = [1992,1994,1996,1998,2000]
cyc00 = [2002,2004,2006,2008,2010]
cyc10 = [2012,2014,2016]
cycles = [cyc70,cyc80,cyc90,cyc00,cyc10]
cnames = [1970,1980,1990,2000,2010]
binsMM = np.linspace(-.10,.10,100)
binsT = np.linspace(-6.,6.,100)
limit = 0.03
#Compute and plot expected mean median difference{{{1
dataMM = [['State','cycle','expectedMM','stdvMM','stdvMMasymptotic','p5','p5asymptotic','p5d']]
fig1, ((axt1, axt2), (axt3, axt4)) = plt.subplots(2, 2, sharex="col", sharey=True,figsize=(18,10))
fig2, ((axs1, axs2), (axs3, axs4)) = plt.subplots(2, 2, sharex="col", sharey=True,figsize=(18,10))

fig3, axh = plt.subplots(1,1)

for cnm,cyc in zip(cnames,cycles):
    dfCycle      = dataAB[dataAB["cycle"]==cnm]
    dfCyclePop   = dataABState[dataABState["cycle"]==cnm]
    for state in states:
        abbr = state.abbr
        if abbr == "DC": continue
        dfStatePop = dfCyclePop[dfCyclePop["State"].str.contains(abbr)]
        if np.abs(0.5-dfStatePop["mean"].values[0]) > limit: continue
        dfState    = dfCycle[dfCycle["State"].str.contains(abbr)]
        betaParams = zip(dfState["alpha"].tolist(),dfState["beta"].tolist(),dfState["loc"].tolist(),dfState["scale"].tolist())
        if len(dfState) > 2:
            expMM,expT = getExpMMandT(betaParams)

            mn = np.mean(expMM)
            st = np.std(expMM,ddof=1)
            stA = dfStatePop["stdv of votePct"].values[0]/np.sqrt(float(len(dfState)))
            p5  = stats.norm.ppf(.95,scale=st)
            p5A = stats.norm.ppf(.95,scale=stA)
            p5d = stats.norm.cdf(p5,scale=stA)
            
            mt = np.mean(expT)
            df = len(dfState)-2
            #st = np.std(expMM,ddof=1)
            #stA = dfStatePop["stdv of votePct"].values[0]/np.sqrt(float(len(dfState)))
            #p5  = stats.norm.ppf(.95,scale=st)
            #p5A = stats.norm.ppf(.95,scale=stA)
            
            #plot some selected states and cycles
            if abbr == "TX" and cnm == 1980:
                N, bins, patches = axs1.hist(expMM-mn,bins=binsMM,normed=1.,label="Sims of mean-med, centered")
                axs1.plot(binsMM,stats.norm.pdf(binsMM,scale=st),linewidth=4,label="Normal Fit to sims")
                axs1.plot(binsMM,stats.norm.pdf(binsMM,scale=stA),linewidth=4,label="Asymptotic Distribution of mean-med")
                axs1.set_xlabel("TX, 1980's")
                axs1.legend()
                axs1.set_xlim((-.1,.1))
                axs1.grid()

                N, bins, patches = axt1.hist(expT-mt,bins=binsT,normed=1.,label="Sims of T-stat, centered")
                axt1.plot(binsT,stats.t.pdf(binsT,df),linewidth=4,label="Asymptotic Distribution of T-stat")
                #axt1.plot(binsMM,stats.norm.pdf(binsMM,scale=stA))
                axt1.legend()
                axt1.set_xlabel("TX, 1980's")
                axt1.grid()
            if abbr == "CA" and cnm == 1980:
                N, bins, patches = axs3.hist(expMM-mn,bins=binsMM,normed=1.)
                axs3.plot(binsMM,stats.norm.pdf(binsMM,scale=st),linewidth=4)
                axs3.plot(binsMM,stats.norm.pdf(binsMM,scale=stA),linewidth=4)
                axs3.set_xlabel("CA, 1980's")
                axs3.grid()

                N, bins, patches = axt3.hist(expT-mt,bins=binsT,normed=1.)
                axt3.plot(binsT,stats.t.pdf(binsT,df),linewidth=4)
                #axt3.plot(binsMM,stats.norm.pdf(binsMM,scale=stA))
                axt3.set_xlabel("CA, 1980's")
                axt3.grid()
            if abbr == "PA" and cnm == 2010:
                N, bins, patches = axs2.hist(expMM-mn,bins=binsMM,normed=1.)
                axs2.plot(binsMM,stats.norm.pdf(binsMM,scale=st),linewidth=4)
                axs2.plot(binsMM,stats.norm.pdf(binsMM,scale=stA),linewidth=4)
                axs2.set_xlabel("PA, 2010's")
                axs2.set_xlim((-.1,.1))
                axs2.grid()

                N, bins, patches = axt2.hist(expT-mt,bins=binsT,normed=1.)
                axt2.plot(binsT,stats.t.pdf(binsT,df),linewidth=4)
                #axt2.plot(binsMM,stats.norm.pdf(binsMM,scale=stA))
                axt2.set_xlabel("PA, 2010's")
                axt2.grid()
            if abbr == "NC" and cnm == 2010:
                N, bins, patches = axs4.hist(expMM-mn,bins=binsMM,normed=1.)
                axs4.plot(binsMM,stats.norm.pdf(binsMM,scale=st),linewidth=4)
                axs4.plot(binsMM,stats.norm.pdf(binsMM,scale=stA),linewidth=4)
                axs4.set_xlabel("NC, 2010's")
                axs4.grid()

                N, bins, patches = axt4.hist(expT-mt,bins=binsT,normed=1.)
                axt4.plot(binsT,stats.t.pdf(binsT,df),linewidth=4)
                #axt4.plot(binsMM,stats.norm.pdf(binsMM,scale=stA))
                axt4.set_xlabel("NC, 2010's")
                axt4.grid()
            dataMM.append([abbr,cnm,np.mean(expMM),st,stA,p5,p5A,p5d])



list2df(dataMM,os.path.join(dataDir,"expMM"))
dataMM = pd.read_csv(os.path.join(dataDir,"expMM.csv"))

fig1.savefig(os.path.join(figDir,"80vs10T.png"))
fig2.savefig(os.path.join(figDir,"80vs10MM.png"))

fig = plt.figure()
ax  = fig.add_subplot(111)
ax.scatter(dataMM['stdvMM'].values,dataMM['stdvMMasymptotic'].values)
ax.plot([0.,.14],[0,.14])
ax.grid()
ax.set_xlabel("Stdv of MM, Sims")
ax.set_ylabel("Stdv of MM, Asymptotic")
fig.savefig(os.path.join(figDir,"stdvMM.png"))

fig = plt.figure()
ax  = fig.add_subplot(111)
ax.scatter(dataMM['p5'].values,dataMM['p5asymptotic'].values)
ax.plot([0.,.2],[0,.2])
ax.grid()
ax.set_xlabel("95th percentile of mean-med, Sims")
ax.set_ylabel("95th percentile of mean-med, Asymptotic")
fig.savefig(os.path.join(figDir,"pMM.png"))

fig = plt.figure()
ax  = fig.add_subplot(111)
ax.hist(dataMM['p5d'].values)
print np.mean(dataMM['p5d'].values)
ax.grid()
fig.savefig(os.path.join(figDir,"p5d.png"))

#1}}}

