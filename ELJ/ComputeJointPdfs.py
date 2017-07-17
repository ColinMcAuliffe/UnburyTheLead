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
#Compute and plot seats votes measures{{{1
#data = [['State','cycle','meanPopVote','expAsym','expGA','expMM','expEG','covAsym','covGA','covMM','covEG','prOp_SA-GA','prOp_SA-MM','prOp_SA-EG','prOp_GA-MM','prOp_GA-EG','prOp_MM-EG','corr_SA-GA','corr_SA-MM','corr_SA-EG','corr_GA-MM','corr_GA-EG','corr_MM-EG','MI_SA-GA','MI_SA-MM','MI_SA-EG','MI_GA-MM','MI_GA-EG','MI_MM-EG','ndist']]
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
#            expAsym = np.mean(results[0,:])/float(ndist)
#            expGA   = np.mean(results[1,:])/float(ndist)
#            expMM   = np.mean(results[2,:])
#            expEG   = np.mean(results[3,:])
#            #covAsym = np.std(results[0,:]*100./float(ndist),ddof=1)/np.abs(expAsym*100.)
#            #covGA   = np.std(results[1,:]*100./float(ndist),ddof=1)/np.abs(expGA*100.)
#            #covMM   = np.std(results[2,:]*100.,ddof=1)/np.abs(expMM*100.)
#            #covEG   = np.std(results[3,:]*100.,ddof=1)/np.abs(expEG*100.)
#            covAsym = np.std(results[0,:]/float(ndist),ddof=1)
#            covGA   = np.std(results[1,:]/float(ndist),ddof=1)
#            covMM   = np.std(results[2,:],ddof=1)
#            covEG   = np.std(results[3,:],ddof=1)
#
#            prOp_SA_GA = getPrOp(results[0,:],results[1,:])
#            prOp_SA_MM = getPrOp(results[0,:],results[2,:])
#            prOp_SA_EG = getPrOp(results[0,:],results[3,:])
#            prOp_GA_MM = getPrOp(results[1,:],results[2,:])
#            prOp_GA_EG = getPrOp(results[1,:],results[3,:])
#            prOp_MM_EG = getPrOp(results[2,:],results[3,:])
#
#            MI_SA_GA = getMI(results[0,:],results[1,:],[binsSA,binsGA])
#            MI_SA_MM = getMI(results[0,:],results[2,:],[binsSA,binsMM])
#            MI_SA_EG = getMI(results[0,:],results[3,:],[binsSA,binsEG])
#            MI_GA_MM = getMI(results[1,:],results[2,:],[binsGA,binsMM])
#            MI_GA_EG = getMI(results[1,:],results[3,:],[binsGA,binsEG])
#            MI_MM_EG = getMI(results[2,:],results[3,:],[binsMM,binsEG])
#
#
#            corr_SA_GA = stats.pearsonr(results[0,:],results[1,:])[0]
#            corr_SA_MM = stats.pearsonr(results[0,:],results[2,:])[0]
#            corr_SA_EG = stats.pearsonr(results[0,:],results[3,:])[0]
#            corr_GA_MM = stats.pearsonr(results[1,:],results[2,:])[0]
#            corr_GA_EG = stats.pearsonr(results[1,:],results[3,:])[0]
#            corr_MM_EG = stats.pearsonr(results[2,:],results[3,:])[0]
#            data.append([abbr,cnm,meanPopVote,expAsym,expGA,expMM,expEG,covAsym,covGA,covMM,covEG,prOp_SA_GA,prOp_SA_MM,prOp_SA_EG,prOp_GA_MM,prOp_GA_EG,prOp_MM_EG,corr_SA_GA,corr_SA_MM,corr_SA_EG,corr_GA_MM,corr_GA_EG,corr_MM_EG,MI_SA_GA,MI_SA_MM,MI_SA_EG,MI_GA_MM,MI_GA_EG,MI_MM_EG,float(ndist)])
#            
#list2df(data,os.path.join(dataDir,"jointPdfs"))
data = pd.read_csv(os.path.join(dataDir,"jointPdfs.csv"))
dataClose = data[np.abs(0.5-data['meanPopVote']) <= 0.03]

fig = plt.figure()
ax = fig.add_subplot(111)
ax.scatter(np.abs(0.5-data['meanPopVote']),data['prOp_MM-EG'])
fig.savefig(os.path.join(figDir,"prOp_SA-EG.png"))

fig = plt.figure()
ax = fig.add_subplot(111)
ax.scatter(np.abs(data['expAsym']),data['prOp_MM-EG'])
fig.savefig(os.path.join(figDir,"prOp_SA-EG.png"))

fig = plt.figure()
ax = fig.add_subplot(111)
ax.scatter(data['ndist'],data['prOp_MM-EG'])
fig.savefig(os.path.join(figDir,"prOp_SA-EG.png"))

fig = plt.figure()
ax = fig.add_subplot(111)
ax.scatter(data['expMM'],data['expEG'])
ax.scatter(dataClose['expMM'],dataClose['expEG'],color='g')
fig.savefig(os.path.join(figDir,"prOp_SA-EG.png"))

fig = plt.figure()
ax = fig.add_subplot(111)
ax.scatter(data['ndist'],data['covMM'])
ax.scatter(data['ndist'],data['covEG'],color='g')
ax.scatter(data['ndist'],data['covAsym'],color='r')
fig.savefig(os.path.join(figDir,"prOp_SA-EG.png"))

fig, axes = plt.subplots(2, 3, sharey=True,sharex=True)
axes[0][0].scatter(np.abs(0.5-data['meanPopVote']),data['MI_SA-GA'],color='b',label='SA-GA')
axes[0][0].legend()
axes[0][0].grid()

axes[0][1].scatter(np.abs(0.5-data['meanPopVote']),data['MI_SA-MM'],color='g',label='SA-MM')
axes[0][1].legend()
axes[0][1].grid()

axes[0][2].scatter(np.abs(0.5-data['meanPopVote']),data['MI_SA-EG'],color='r',label='SA-EG')
axes[0][2].legend()
axes[0][2].grid()

axes[1][0].scatter(np.abs(0.5-data['meanPopVote']),data['MI_GA-MM'],color='c',label='GA-MM')
axes[1][0].legend()
axes[1][0].grid()

axes[1][1].scatter(np.abs(0.5-data['meanPopVote']),data['MI_GA-EG'],color='k',label='GA-EG')
axes[1][1].legend()
axes[1][1].grid()

axes[1][2].scatter(np.abs(0.5-data['meanPopVote']),data['MI_MM-EG'],color='m',label='MM-EG')
axes[1][2].legend()
axes[1][2].grid()
fig.savefig(os.path.join(figDir,"MI.png"))


