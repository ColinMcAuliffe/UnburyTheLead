import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib.patches import Rectangle

import pandas as pd
import numpy as np
import os
import us
from scipy import stats
from scipy.optimize import curve_fit

from ELJcommon import getDemVotesAndSeats,get_spasym,get_asymFromPct,getExpAsym,varWithShrinkage,betaMOM,list2df,colorBins,getAllSVMetrics

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
binsT = np.linspace(-6.,6.,100)
limit = 0.03
perm = [(a, b) for a in range(4) for b in range(4) if (a < b)]
#Compute and plot seats votes measures{{{1

# gfAsym vs spAsym | mmd vs spAsym | EG vs spAsym
#                  | mmd vs gfAsym | EG vs gfAsym
#                                  | EG vs mmd

for cnm,cyc in zip(cnames,cycles):
    dfCycle      = dataAB[dataAB["cycle"]==cnm]
    dfCyclePop   = dataABState[dataABState["cycle"]==cnm]
    for state in states:
        abbr = state.abbr
        if abbr == "DC": continue
        dfState    = dfCycle[dfCycle["State"] == abbr]
        dfStatePop = dfCyclePop[dfCyclePop["State"] == abbr]
        betaParams = zip(dfState["alphaCen"].tolist(),dfState["betaCen"].tolist())
        stateBeta  = (dfStatePop["alpha"].tolist()[0],dfStatePop["beta"].tolist()[0])
        betaParams.append(stateBeta)
        ndist = len(dfState)
        if ndist > 2:
            results = getAllSVMetrics(betaParams)
            lims = []
            for i in range(4):
                l1 = np.abs(np.min(results[i,:]))
                l2 = np.abs(np.max(results[i,:]))
                l  = 1.05*np.max([l1,l2])
                lims.append((-l,l))

            fig, axes = plt.subplots(3, 3, sharey='row',sharex='col')
            for i,j in perm:
                axes[i][j-1].scatter(results[j,:],results[i,:])
                axes[i][j-1].set_xlim(lims[j])
                axes[i][j-1].set_ylim(lims[i])
                axes[i][j-1].grid()
                axes[i][j-1].xaxis.set_major_locator(MaxNLocator(5))
                axes[i][j-1].yaxis.set_major_locator(MaxNLocator(5))
                
            fig.savefig(os.path.join(figDir,abbr+str(cnm)+"sct.png"))
            plt.close()
            




