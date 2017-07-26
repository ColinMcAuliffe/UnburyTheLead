import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib.patches import Rectangle

import pandas as pd
import numpy as np
import os
import us
from scipy import stats
from scipy.optimize import curve_fit

from ELJcommon import getDemVotesAndSeats,get_spasym,get_asymFromPct,getExpAsym,varWithShrinkage,betaMOM,list2df,colorBins,getAllSVMetrics,getMI

states = us.states.STATES
abbr2name = us.states.mapping('abbr', 'name')

figDir       = os.path.join("Figures","JointPDFs")
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
binsEG = np.linspace(-.30,.30,100)
binsSA = np.linspace(-7.25,7.25,30)
binsGA = np.linspace(-7.25,7.25,30)
allBins = [binsSA,binsGA,binsMM,binsEG]

binsT = np.linspace(-6.,6.,100)
limit = 0.03
perm = [(a, b) for a in range(4) for b in range(4) if (a < b)]
perm6= [(a, b) for a in range(6) for b in range(6) if (a < b)]
metricNames = ["SA","GA","MM","EG","TA","WA"]
metricTypes = ["d","d","c","c","c","c"]
expV = ['exp'+n for n in metricNames]
stdV = ['std'+n for n in metricNames]
prOpName = ['prOp_'+metricNames[i]+"_"+metricNames[j] for i,j in perm6]
corrName = ['corr_'+metricNames[i]+"_"+metricNames[j] for i,j in perm6]
MIName   = ['MI_'+metricNames[i]+"_"+metricNames[j] for i,j in perm6]
combName = [metricNames[i]+"_"+metricNames[j] for i,j in perm6]
#Compute and plot seats votes measures{{{1
#data = [['State','cycle','meanPopVote']+expV+stdV+prOpName+corrName+MIName+['ndist']]
#
## gfAsym vs spAsym | mmd vs spAsym | EG vs spAsym
##                  | mmd vs gfAsym | EG vs gfAsym
##                                  | EG vs mmd
##Probabilty of opposite sign
#def getPrOp(d1,d2):
#    N = float(len(d1))
#    d = d1*d2
#    return float(len(d[d<0.]))/N
#
#for cnm,cyc in zip(cnames,cycles):
#    dfCycle      = dataAB[dataAB["cycle"]==cnm]
#    dfCyclePop   = dataABState[dataABState["cycle"]==cnm]
#
#    dfCycleObs    = stateData[stateData["year"].isin(cyc)]
#    for state in states:
#        abbr = state.abbr
#        if abbr == "DC": continue
#        dfState    = dfCycle[dfCycle["State"] == abbr]
#        dfStatePop = dfCyclePop[dfCyclePop["State"] == abbr]
#        betaParams = zip(dfState["alphaCen"].tolist(),dfState["betaCen"].tolist())
#        stateBeta  = (dfStatePop["alpha"].tolist()[0],dfStatePop["beta"].tolist()[0])
#        meanPopVote  = dfStatePop["mean"].tolist()[0]
#        betaParams.append(stateBeta)
#
#        dfStateObs  = dfCycleObs[dfCycleObs["State"] == abbr]
#        ndist = len(dfState)
#        if ndist > 2:
#            results = getAllSVMetrics(betaParams)
#            observed = []
#            observed.append(np.array(dfStateObs['specAsym (seats)'].values))
#            observed.append(np.array(dfStateObs['Grofman Asym'].values))
#            observed.append(np.array(dfStateObs['mean-median'].values))
#            observed.append(np.array(dfStateObs['efficiency gap'].values))
#            observed = np.array(observed)
#            lims = []
#            for i in range(4):
#                l1 = np.abs(np.min(results[i,:]))
#                l2 = np.abs(np.max(results[i,:]))
#                l  = 1.05*np.max([l1,l2])
#                lims.append((-l,l))
#
#            fig, axes = plt.subplots(3, 3, sharey='row',sharex='col')
#            for i,j in perm:
#                axes[i][j-1].scatter(results[j,:],results[i,:])
#                axes[i][j-1].scatter(observed[j,:],observed[i,:],marker="*",color='r')
#                axes[i][j-1].set_xlim(lims[j])
#                axes[i][j-1].set_ylim(lims[i])
#                axes[i][j-1].grid()
#                axes[i][j-1].xaxis.set_major_locator(MaxNLocator(5))
#                axes[i][j-1].yaxis.set_major_locator(MaxNLocator(5))
#                
#            fig.savefig(os.path.join(figDir,abbr+str(cnm)+"sct.png"))
#            plt.close()
#
#            expVals  = [np.mean(results[i,:]) for i in range(6)]
#            stdVals  = [np.std(results[i,:],ddof=1) for i in range(6)]
#            prOpVals = [getPrOp(results[i,:],results[j,:]) for i,j in perm6]
#            corrVals = [stats.pearsonr(results[i,:],results[j,:])[0] for i,j in perm6]
#
#            MIVals = []
#            for i,j in perm6:
#                ti = metricTypes[i]
#                tj = metricTypes[j]
#                if ti == 'd' and tj == 'd':
#                    MI = getMI(results[i,:],results[j,:],'dd',bins=[binsSA,binsGA])
#                elif ti == 'c' and tj == 'd':
#                    MI = getMI(results[i,:],results[j,:],'cd')
#                elif ti == 'd' and tj == 'c':
#                    MI = getMI(results[j,:],results[i,:],'cd')
#                elif ti == 'c' and tj == 'c':
#                    MI = getMI(results[i,:],results[j,:],'cc')
#                MIVals.append(MI)
#
#
#            data.append([abbr,cnm,meanPopVote]+expVals+stdVals+prOpVals+corrVals+MIVals+[float(ndist)])
#            
#list2df(data,os.path.join(dataDir,"jointPdfs"))
data = pd.read_csv(os.path.join(dataDir,"jointPdfs.csv"))
dataClose = data[np.abs(0.5-data['meanPopVote']) <= 0.03]

fig, axes = plt.subplots(4, 4, sharey=True,sharex=True,figsize=(12,12))
idx = 0
for i in range(4):
    for j in range(4):
        if idx < 14:
            axes[i][j].scatter(np.abs(0.5-data['meanPopVote']),data[MIName[idx]],color='b',label=combName[idx])
            axes[i][j].legend()
            axes[i][j].grid()
        idx+=1

fig.savefig(os.path.join(figDir,"MI.png"))

fig, axes = plt.subplots(4, 4, sharey=True,sharex=True,figsize=(12,12))
idx = 0
for i in range(4):
    for j in range(4):
        if idx < 14:
            axes[i][j].scatter(np.abs(0.5-data['meanPopVote']),data[prOpName[idx]],color='b',label=combName[idx])
            axes[i][j].legend()
            axes[i][j].grid()
        idx+=1

fig.savefig(os.path.join(figDir,"prOp.png"))

fig, axes = plt.subplots(4, 4, sharey=True,sharex=True,figsize=(12,12))
idx = 0
for i in range(4):
    for j in range(4):
        if idx < 14:
            axes[i][j].scatter(np.abs(0.5-data['meanPopVote']),data[corrName[idx]],color='b',label=combName[idx])
            axes[i][j].legend()
            axes[i][j].grid()
        idx+=1

fig.savefig(os.path.join(figDir,"corr.png"))
