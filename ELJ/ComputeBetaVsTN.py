import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib.patches import Rectangle

import pandas as pd
import numpy as np
import os
import us
from scipy import stats

from ELJcommon import getDemVotesAndSeats,get_spasym,get_asymFromPct,getExpAsym,varWithShrinkage,betaMOM,list2df,colorBins,setLimits,year2Cycle
from matplotlib.patches import Polygon

states = us.states.STATES
abbr2name = us.states.mapping('abbr', 'name')

figDir       = os.path.join("Figures","ExpectedAsymmetry")
figDirHBS    = os.path.join(figDir,"HistogramsByState")
figDirLBS    = os.path.join(figDir,"LinePlotsByState")
figExt       = ".png"
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
dataExp = [['State','cycle','expectedAsym','expectedAsymPct','mode','p05','p95','ndist']]
allSims = []

fig3, axh = plt.subplots(1,1)

binsTot = np.linspace(-0.5,60.5,42)
binsNet = np.linspace(-40.5,40.5,82)
for cnm,cyc in zip(cnames,cycles):
    dfCycle      = dataAB[dataAB["cycle"]==cnm]
    dfCyclePop   = dataABState[dataABState["cycle"]==cnm]
    sims = []
    simsByState = []
    simsByState2 = []
    for state in states:
        abbr = state.abbr
        if abbr == "DC": continue
        dfState    = dfCycle[dfCycle["State"] == abbr]
        dfStatePop = dfCyclePop[dfCyclePop["State"] == abbr]
        betaParams = zip(dfState["alphaCen"].tolist(),dfState["betaCen"].tolist())
        stateBeta  = (dfStatePop["alpha"].tolist()[0],dfStatePop["beta"].tolist()[0])
        betaParams.append(stateBeta)

        TNParams = zip(dfState["meanCen"].tolist(),dfState["stdCen"].tolist())
        stateTN  = (dfStatePop["mean"].tolist()[0],dfStatePop["std"].tolist()[0])
        TNParams.append(stateTN)
        if len(dfState) > 1:
            expAsym = getExpAsym(betaParams).tolist()
            simsByState.append(expAsym)

            expAsym = getExpAsym(TNParams,dist="TN").tolist()
            simsByState2.append(expAsym)
        else:
            mode = 0.
            mean = 0.
            p05  = 0.
            p95  = 0.


    simsByState = np.array(simsByState)
    totalAsym = np.sum(np.absolute(simsByState),axis=0)
    meanAsym = np.mean(totalAsym)
    asymp75  = np.percentile(totalAsym,75)
    asymp25  = np.percentile(totalAsym,25)
    asymp95  = np.percentile(totalAsym,95)
    asymp05  = np.percentile(totalAsym, 5)
    axh.add_patch(Rectangle((cyc[0],asymp05),8,asymp95-asymp05,color='0.75',alpha=0.2))
    axh.add_patch(Rectangle((cyc[0],asymp25),8,asymp75-asymp25,color='0.75',alpha=0.5))
    axh.plot(cyc,[meanAsym]*len(cyc),color='0.75',linewidth=4)

    simsByState = np.array(simsByState2)
    totalAsym = np.sum(np.absolute(simsByState),axis=0)
    meanAsym = np.mean(totalAsym)
    asymp75  = np.percentile(totalAsym,75)
    asymp25  = np.percentile(totalAsym,25)
    asymp95  = np.percentile(totalAsym,95)
    asymp05  = np.percentile(totalAsym, 5)
    axh.add_patch(Rectangle((cyc[0],asymp05),8,asymp95-asymp05,color='0.75',alpha=0.2))
    axh.add_patch(Rectangle((cyc[0],asymp25),8,asymp75-asymp25,color='0.75',alpha=0.5))
    axh.plot(cyc,[meanAsym]*len(cyc),color='0.75',linewidth=4)



#list2df(dataExp,os.path.join(dataDir,"expAsym2"))
#dataExp = pd.read_csv(os.path.join(dataDir,"expAsym2.csv"))


for cyc,cnm in zip(cycles,cnames):
    st = []
    sn = []
    for year in cyc:
        dfYear = stateData[stateData["year"] == year]
        st.append(np.sum(np.abs(dfYear["specAsym (seats)"].values)))
        sn.append(np.sum(dfYear["specAsym (seats)"].values))
    axh.plot(cyc,st,marker='x',color='k',linewidth=4)

axh.grid()
y0,y1 = axh.get_ylim()
axh.set_ylim((0,y1))
fig3.savefig(os.path.join(figDir,"totalAsym2"+figExt))

#1}}}

