import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib.patches import Rectangle

import pandas as pd
import numpy as np
import os
import us
from scipy import stats

from ELJcommon import getDemVotesAndSeats,get_spasym,get_asymFromPct,getExpAsym,varWithShrinkage,betaMOM,list2df,colorBins

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
bins6 = np.linspace(-6.25,6.25,26)
bins7 = np.linspace(-7.25,7.25,30)
#Compute and plot expected asymmetry{{{1
dataExp = [['State','cycle','expectedAsym']]
fig, ((ax1, ax2,ax3), (ax4, ax5, ax6)) = plt.subplots(2, 3, sharex=True, sharey=True,figsize=(18,10))

axhist  = [ax2,ax3,ax4,ax5,ax6]

allSims = []
fig2, ((axs1, axs2), (axs3, axs4)) = plt.subplots(2, 2, sharex="col", sharey=True,figsize=(18,10))

fig3, axh = plt.subplots(1,1)

fig4, ((axh1, axh2,axh3), (axh4, axh5, axh6)) = plt.subplots(2, 3, sharex=True, sharey=True,figsize=(18,10))
axhist4  = [axh1,axh2,axh3,axh4,axh5]

binsTot = np.linspace(9.5,70.5,62)
binsTot = np.linspace(-40.5,40.5,82)
simsByStateAll = []
for cnm,cyc,ax,axhs4 in zip(cnames,cycles,axhist,axhist4):
    dfCycle      = dataAB[dataAB["cycle"]==cnm]
    dfCyclePop   = dataABState[dataABState["cycle"]==cnm]
    sims = []
    simsByState = []
    for state in states:
        abbr = state.abbr
        if abbr == "DC": continue
        dfState    = dfCycle[dfCycle["State"].str.contains(abbr)]
        dfStatePop = dfCyclePop[dfCyclePop["State"].str.contains(abbr)]
        betaParams = zip(dfState["alpha"].tolist(),dfState["beta"].tolist())
        stateBeta  = (dfStatePop["alpha"].tolist()[0],dfStatePop["beta"].tolist()[0])
        betaParams.append(stateBeta)
        if len(dfState) > 1:
            expAsym = getExpAsym(betaParams).tolist()
            sims+=expAsym
            simsByState.append(expAsym)
            simsByStateAll.append(expAsym)
            allSims+=expAsym
        else:
            expAsym = np.zeros((10000))


        #plot some selected states and cycles
        if abbr == "TX" and cnm == 1980:
            N, binedges = np.histogram(expAsym,bins=bins7,density=True)
            for i in range(len(binedges)-1):
                axs1.add_patch(Rectangle((1982,binedges[i]),8,0.5,alpha=N[i]))

            df = stateData[stateData["State"]=="TX"]
            df = df[df["year"].isin(cyc80)]
            axs1.plot(df["year"].values,df["specAsym (seats)"].values,color='k',linewidth=4)
            axs1.set_ylim((-7,7))
            axs1.set_xlabel("TX, 1980's")
            axs1.grid()
            axs1.get_xaxis().get_major_formatter().set_useOffset(False)
        if abbr == "CA" and cnm == 1980:
            N, binedges = np.histogram(expAsym,bins=bins7,density=True)
            for i in range(len(binedges)-1):
                axs3.add_patch(Rectangle((1982,binedges[i]),8,0.5,alpha=N[i]))

            df = stateData[stateData["State"]=="CA"]
            df = df[df["year"].isin(cyc80)]
            axs3.plot(df["year"].values,df["specAsym (seats)"].values,color='k',linewidth=4)
            axs3.set_ylim((-7,7))
            axs3.set_xlabel("CA, 1980's")
            axs3.grid()
            axs3.get_xaxis().get_major_formatter().set_useOffset(False)
        if abbr == "PA" and cnm == 2010:
            N, binedges = np.histogram(expAsym,bins=bins7,density=True)
            for i in range(len(binedges)-1):
                axs2.add_patch(Rectangle((2012,binedges[i]),8,0.5,alpha=N[i]))

            df = stateData[stateData["State"]=="PA"]
            df = df[df["year"].isin(cyc10)]
            axs2.plot(df["year"].values,df["specAsym (seats)"].values,color='k',linewidth=4)
            axs2.set_ylim((-7,7))
            axs2.set_xlabel("PA, 2010's")
            axs2.grid()
            axs2.get_xaxis().get_major_formatter().set_useOffset(False)
        if abbr == "NC" and cnm == 2010:
            N, binedges = np.histogram(expAsym,bins=bins7,density=True)
            for i in range(len(binedges)-1):
                axs4.add_patch(Rectangle((2012,binedges[i]),8,0.5,alpha=N[i]))

            df = stateData[stateData["State"]=="NC"]
            df = df[df["year"].isin(cyc10)]
            axs4.plot(df["year"].values,df["specAsym (seats)"].values,color='k',linewidth=4)
            axs4.set_ylim((-7,7))
            axs4.set_xlabel("NC, 2010's")
            axs4.grid()
            axs4.get_xaxis().get_major_formatter().set_useOffset(False)
        dataExp.append([abbr,cnm,np.mean(expAsym)])

    N, bins, patches = ax.hist(sims,bins=bins6,normed=True)
    bins,patches = colorBins(bins,patches,0.)

    ax.xaxis.set_major_locator(MaxNLocator(6))
    ax.yaxis.set_major_locator(MaxNLocator(6))
    ax.set_xlabel(str(cnm))
    ax.grid()

    #simsByState = np.absolute(np.array(simsByState))
    simsByState = np.array(simsByState)
    totalAsym = np.sum(simsByState,axis=0)
    N, bins, patches = axhs4.hist(totalAsym,bins=binsTot,normed=True)
    bins,patches = colorBins(bins,patches,0.)

    axhs4.grid()
    axhs4.set_xlabel(str(cnm))
    meanAsym = np.mean(totalAsym)
    asymp75  = np.percentile(totalAsym,75)
    asymp25  = np.percentile(totalAsym,25)
    axh.plot(cyc,[meanAsym]*len(cyc),color='0.75',linewidth=4)
    axh.plot(cyc,[asymp75]*len(cyc),color='0.75',linewidth=2)
    axh.plot(cyc,[asymp25]*len(cyc),color='0.75',linewidth=2)

fig2.savefig(os.path.join(figDir,"80vs10.png"))


for cyc,cnm in zip(cycles,cnames):
    dfCycle = congress[congress["raceYear"].isin(cyc)]
    mm = []
    for year in cyc:
        dfYear = stateData[stateData["year"] == year]
        #mm.append(np.sum(np.abs(dfYear["specAsym (seats)"].values)))
        mm.append(np.sum(dfYear["specAsym (seats)"].values))
    axh.plot(cyc,mm,marker='x',color='k',linewidth=4)

axh.grid()
fig3.savefig(os.path.join(figDir,"totalAsym.png"))

axh6.set_axis_off()
fig4.savefig(os.path.join(figDir,"totalAsymHist.png"))

N, bins, patches = ax1.hist(allSims,bins=bins6,normed=True)
bins,patches = colorBins(bins,patches,0.)

ax1.xaxis.set_major_locator(MaxNLocator(6))
ax1.yaxis.set_major_locator(MaxNLocator(6))
ax1.set_xlabel("All Cycles")
ax1.grid()

fig.savefig(os.path.join(figDir,"ExpasmHist2.png"))

list2df(dataExp,os.path.join(dataDir,"expAsym"))
dataExp = pd.read_csv(os.path.join(dataDir,"expAsym.csv"))

stateDataLarge = dataExp[dataExp['expectedAsym'].abs() > 2]
stateDataLarge.to_csv(os.path.join(dataDir,"expSAsymLarge.csv"))
#1}}}
fig, ((ax1, ax2,ax3), (ax4, ax5, ax6)) = plt.subplots(2, 3, sharex=True, sharey=True,figsize=(18,10))

axhist  = [ax2,ax3,ax4,ax5,ax6]
allAsym = []
for cyc,cnm,ax in zip(cycles,cnames,axhist):
    dfYear = dataExp[dataExp["cycle"]==cnm]
    N, bins, patches = ax.hist(dfYear["expectedAsym"].values,bins=bins6,normed=True)
    allAsym+=dfYear["expectedAsym"].tolist()
    bins,patches = colorBins(bins,patches,0.)

    ax.xaxis.set_major_locator(MaxNLocator(6))
    ax.yaxis.set_major_locator(MaxNLocator(6))
    ax.set_xlabel(str(cnm))
    ax.grid()

N, bins, patches = ax1.hist(allAsym,bins=bins6,normed=True)
bins,patches = colorBins(bins,patches,0.)

ax1.set_xlabel("All Cycles")
ax1.grid()
fig.savefig(os.path.join(figDir,"ExpasmHist.png"))

