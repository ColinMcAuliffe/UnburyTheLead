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
dataExp = [['State','STATEFP','cycle','expectedAsym','expectedAsymPct','mode','p05','p95','ndist']]
fig, ((ax1, ax2,ax3), (ax4, ax5, ax6)) = plt.subplots(2, 3, sharex=True, sharey=True,figsize=(18,10))
fig2, ((axs1, axs2), (axs3, axs4)) = plt.subplots(2, 2, sharex="col", sharey=True)

axhist  = [ax2,ax3,ax4,ax5,ax6]

allSims = []

fig3, axh = plt.subplots(1,1)

fig4, ((axh1, axh2,axh3), (axh4, axh5, axh6)) = plt.subplots(2, 3, sharex=True, sharey=True)
axhist4  = [axh1,axh2,axh3,axh4,axh5]

fig5, ((axn1, axn2,axn3), (axn4, axn5, axn6)) = plt.subplots(2, 3, sharex=True, sharey=True)
axhist5  = [axn1,axn2,axn3,axn4,axn5]

fig6, axn = plt.subplots(1,1)

fig7, ((ax71,ax72)) = plt.subplots(2, 1, sharex="col", sharey=True)

binsTot = np.linspace(-0.5,60.5,42)
binsNet = np.linspace(-40.5,40.5,82)
for cnm,cyc,ax,axhs4,axhn5 in zip(cnames,cycles,axhist,axhist4,axhist5):
    dfCycle      = dataAB[dataAB["cycle"]==cnm]
    dfCyclePop   = dataABState[dataABState["cycle"]==cnm]
    sims = []
    simsByState = []
    for state in states:
        abbr = state.abbr
        if abbr == "DC": continue
        dfState    = dfCycle[dfCycle["State"] == abbr]
        dfStatePop = dfCyclePop[dfCyclePop["State"] == abbr]
        betaParams = zip(dfState["alphaCen"].tolist(),dfState["betaCen"].tolist())
        stateBeta  = (dfStatePop["alpha"].tolist()[0],dfStatePop["beta"].tolist()[0])
        betaParams.append(stateBeta)
        if len(dfState) > 1:
            expAsym = getExpAsym(betaParams).tolist()
            sims+=expAsym
            simsByState.append(expAsym)
            allSims+=expAsym
            mean = np.mean(expAsym)
            mode = stats.mode(expAsym)[0][0]
            p05  = np.percentile(expAsym,5)
            p95  = np.percentile(expAsym,95)
        else:
            mode = 0.
            mean = 0.
            p05  = 0.
            p95  = 0.


        dataExp.append([abbr,state.fips,cnm,mean,mean/float(len(dfState)),mode,p05,p95,len(dfState)])
        if abbr == "TX" and cnm == 1980:
            N, bins, patches = axs1.hist(expAsym,bins=bins6,normed=1.)
            bins,patches = colorBins(bins,patches,0.)
            axs1.set_xlabel("TX, 1980's")
            axs1.grid()

        if abbr == "CA" and cnm == 1980:
            N, bins, patches = axs3.hist(expAsym,bins=bins6,normed=1.)
            bins,patches = colorBins(bins,patches,0.)
            axs3.set_xlabel("CA, 1980's")
            axs3.grid()

        if abbr == "PA" and cnm == 2010:
            N, bins, patches = axs2.hist(expAsym,bins=bins6,normed=1.)
            bins,patches = colorBins(bins,patches,0.)
            axs2.set_xlabel("PA, 2010's")
            axs2.grid()

        if abbr == "NC" and cnm == 2010:
            N, bins, patches = axs4.hist(expAsym,bins=bins6,normed=1.)
            bins,patches = colorBins(bins,patches,0.)
            axs4.set_xlabel("NC, 2010's")
            axs4.grid()

        if abbr == "CA" and cnm == 2000:
            N, bins, patches = ax71.hist(expAsym,bins=bins7,normed=1.)
            bins,patches = colorBins(bins,patches,0.)
            ax71.set_xlabel("CA, 2000's")
            ax71.grid()

        if abbr == "CA" and cnm == 2010:
            N, bins, patches = ax72.hist(expAsym,bins=bins7,normed=1.)
            bins,patches = colorBins(bins,patches,0.)
            ax72.set_xlabel("CA, 2010's")
            ax72.grid()


        

    N, bins, patches = ax.hist(sims,bins=bins6,normed=True)
    bins,patches = colorBins(bins,patches,0.)

    ax.xaxis.set_major_locator(MaxNLocator(6))
    ax.yaxis.set_major_locator(MaxNLocator(6))
    ax.set_xlabel(str(cnm))
    ax.grid()

    simsByState = np.array(simsByState)

    totalAsym = np.sum(np.absolute(simsByState),axis=0)
    N, bins, patches = axhs4.hist(totalAsym,bins=binsTot,normed=True,color="0.75")
    axhs4.grid()
    axhs4.set_xlabel(str(cnm))

    netAsym = np.sum(simsByState,axis=0)
    N, bins, patches = axhn5.hist(netAsym,bins=binsNet,linewidth=0,normed=True)
    bins,patches = colorBins(bins,patches,0.)
    axhn5.grid()
    axhn5.set_xlim((-40.,40.))
    axhn5.xaxis.set_major_locator(MaxNLocator(6))
    axhn5.yaxis.set_major_locator(MaxNLocator(6))
    axhn5.set_xlabel(str(cnm))


    meanAsym = np.mean(totalAsym)
    asymp75  = np.percentile(totalAsym,75)
    asymp25  = np.percentile(totalAsym,25)
    asymp95  = np.percentile(totalAsym,95)
    asymp05  = np.percentile(totalAsym, 5)
    axh.add_patch(Rectangle((cyc[0],asymp05),8,asymp95-asymp05,color='0.75',alpha=0.2))
    axh.add_patch(Rectangle((cyc[0],asymp25),8,asymp75-asymp25,color='0.75',alpha=0.5))
    axh.plot(cyc,[meanAsym]*len(cyc),color='0.75',linewidth=4)

    meanAsym = np.mean(netAsym)
    asymp75  = np.percentile(netAsym,75)
    asymp25  = np.percentile(netAsym,25)
    asymp95  = np.percentile(netAsym,95)
    asymp05  = np.percentile(netAsym, 5)
    axn.add_patch(Rectangle((cyc[0],asymp05),8,asymp95-asymp05,color='0.75',alpha=0.2))
    axn.add_patch(Rectangle((cyc[0],asymp25),8,asymp75-asymp25,color='0.75',alpha=0.5))
    axn.plot(cyc,[meanAsym]*len(cyc),color='0.75',linewidth=4)

fig2.savefig(os.path.join(figDir,"80vs10"+figExt))
fig7.savefig(os.path.join(figDir,"00vs10CA"+figExt))

list2df(dataExp,os.path.join(dataDir,"expAsym"))
dataExp = pd.read_csv(os.path.join(dataDir,"expAsym.csv"))

for state in states:
    abbr = state.abbr
    if abbr == "DC": continue
    dfState    = dataExp[dataExp["State"] == abbr]
    dfState2   = stateData[stateData["State"] == abbr]
    fig2 = plt.figure()
    axst = fig2.add_subplot(111)
    needLab = True
    for cyc,cnm in zip(cycles,cnames):
        dfCycle = dfState[dfState["cycle"] == cnm]
        meanAsym = dfCycle['expectedAsym'].values[0]
        mode     = dfCycle['mode'].values[0]
        asymp95  = dfCycle['p95'].values[0]
        asymp05  = dfCycle['p05'].values[0]
        lim = np.max(np.abs([asymp95,asymp05]))+0.5
        axst.add_patch(Rectangle((cyc[0],asymp05),8,asymp95-asymp05,color='0.75',alpha=0.2))
        axst.plot(cyc,[meanAsym]*len(cyc),color='0.75',linewidth=4)
        axst.plot(cyc,[mode]*len(cyc),color='b',linewidth=4)
        mm = []
        for year in cyc:
            dfYear = dfState2[dfState2["year"] == year]
            mm.append(dfYear["specAsym (seats)"].values[0])
        axst.plot(cyc,mm,marker='x',color='k',linewidth=4)
    axst.grid()
    axst.set_ylim((-lim,lim))


    fig2.savefig(os.path.join(figDirLBS,"expAsym"+abbr+figExt))
    plt.close(fig2)

for cyc,cnm in zip(cycles,cnames):
    st = []
    sn = []
    for year in cyc:
        dfYear = stateData[stateData["year"] == year]
        st.append(np.sum(np.abs(dfYear["specAsym (seats)"].values)))
        sn.append(np.sum(dfYear["specAsym (seats)"].values))
        #mm.append(np.sum(np.floor(np.abs(dfYear["specAsym (seats)"].values))))
        #mm.append(np.sum(dfYear["specAsym (seats)"].values))
    axh.plot(cyc,st,marker='x',color='k',linewidth=4)
    axn.plot(cyc,sn,marker='x',color='k',linewidth=4)

axh.grid()
y0,y1 = axh.get_ylim()
axh.set_ylim((0,y1))
fig3.savefig(os.path.join(figDir,"totalAsym"+figExt))

axn.grid()
axn = setLimits(axn)
fig6.savefig(os.path.join(figDir,"netAsym"+figExt))

axh6.set_axis_off()
axn6.set_axis_off()
fig4.savefig(os.path.join(figDir,"totalAsymHist"+figExt))
fig5.savefig(os.path.join(figDir,"netAsymHist"+figExt))

N, bins, patches = ax1.hist(allSims,bins=bins6,normed=True)
bins,patches = colorBins(bins,patches,0.)

ax1.xaxis.set_major_locator(MaxNLocator(6))
ax1.yaxis.set_major_locator(MaxNLocator(6))
ax1.set_xlabel("All Cycles")
ax1.grid()

fig.savefig(os.path.join(figDir,"ExpasmHist2"+figExt))

stateDataLarge = dataExp[dataExp['expectedAsym'].abs() > 2]
stateDataLarge.to_csv(os.path.join(dataDir,"expSAsymLarge.csv"))

fig = plt.figure()
ax  = fig.add_subplot(111)
rank = range(1,51)
for cyc,cnm in zip(cycles,cnames):
    dfCycle      = dataExp[dataExp["cycle"]==cnm]
    dfCycle['abs'] = dfCycle['expectedAsym'].abs()
    dfCycle      = dfCycle.sort('abs',ascending=False)
    print dfCycle[0:10]
    expAsym = np.sort(dfCycle['expectedAsym'].abs())[::-1]
    ax.plot(rank,expAsym,marker='.',label=str(cnm))
print "______"
ax.legend()
ax.set_xlabel("Rank")
ax.set_ylabel("Expected Asymmetry")
ax.grid()
fig.savefig(os.path.join(figDir,"asymRankS"+figExt))

fig = plt.figure()
ax  = fig.add_subplot(111)
rank = range(1,51)
for cyc,cnm in zip(cycles,cnames):
    dfCycle      = dataExp[dataExp["cycle"]==cnm]
    dfCycle      = dfCycle[dfCycle["ndist"]>5]
    dfCycle['abs'] = dfCycle['expectedAsymPct'].abs()
    dfCycle      = dfCycle.sort('abs',ascending=False)
    print dfCycle[0:10]
    expAsym = np.sort(dfCycle['expectedAsymPct'].abs())[::-1]
    ax.plot(rank[0:len(expAsym)],expAsym,marker='.',label=str(cnm))
ax.legend()
ax.set_xlabel("Rank")
ax.set_ylabel("Expected Asymmetry as a % of Available Seats")
ax.grid()
fig.savefig(os.path.join(figDir,"asymRank"+figExt))
#1}}}
#make a table for the a few states from 2000 to 2010
states2010 = ["PA","NC","GA","VA","MI","OH","WI","CA","NY","IL"]
lens = len(states2010)+2
df2010      = dataExp[dataExp["cycle"]==2010]
df2000      = dataExp[dataExp["cycle"]==2000]
def getStringFromAsym(asym):
    if asym < 0.:
        return "D %2.2f" %(abs(asym))
    else:
        return "R %2.2f" %(asym)

fig = plt.figure()
ax  = fig.add_subplot(111)
hly  = 0.2
hlx  = 1.0
with open(os.path.join("EmpiricalBayes","largeStatesTab.tex"),"w") as f: 
    f.write(r"\begin{table}[htb!]"+"\n")
    f.write(r"\centering"+"\n")
    f.write(r"\caption{Change in Expected Specific Asymmetry from 2000 to 2010 for states with large asymmetries in 2010 \label{tab:Asym2000to2010}}"+"\n")
    f.write(r"\begin{tabular}{|l|l|l|l|}"+"\n")
    f.write(r"\hline"+"\n")
    f.write(r"State & Expected Specific     & Expected Specific & Net Change\\"+"\n")
    f.write(r"      & Asymmetry, 2000 Cycle & Asymmetry, 2010 Cycle & \\"+"\n")
    f.write(r"\hline"+"\n")
    f.write(r"\hline"+"\n")
    for i,st in enumerate(states2010):
        esa2000 = df2000[df2000["State"]==st].expectedAsymPct.values[0]*100.
        esa2010 = df2010[df2010["State"]==st].expectedAsymPct.values[0]*100.
        diff = esa2010-esa2000
        #sign change
        if esa2000*esa2010 < 0:
            if esa2000 < 0:
                ax.plot([esa2000,0.0],[lens-i-2,lens-i-2],color='b',linewidth=4)
                ax.plot([0.0,esa2010],[lens-i-2,lens-i-2],color='r',linewidth=4)
            else:
                ax.plot([esa2000,0.0],[lens-i-2,lens-i-2],color='r',linewidth=4)
                ax.plot([0.0,esa2010],[lens-i-2,lens-i-2],color='b',linewidth=4)
        else:
            if esa2000 < 0:
                ax.plot([esa2000,esa2010],[lens-i-2,lens-i-2],color='b',linewidth=4)
            else:
                ax.plot([esa2000,esa2010],[lens-i-2,lens-i-2],color='r',linewidth=4)

        if esa2010 < 0:
            color='b'
        else:
            color='r'

        if diff < 0:
            ax.plot([esa2010],[lens-i-2],color=color,marker='<',markersize=14)
        else:
            ax.plot([esa2010],[lens-i-2],color=color,marker='>',markersize=14)
        
        esa2000 = getStringFromAsym(esa2000)
        esa2010 = getStringFromAsym(esa2010)
        diff = getStringFromAsym(diff)
        f.write(abbr2name[st]+" & "+esa2000+r"\% & "+esa2010+r"\% & " + diff + r"\\"+"\n")
        f.write(r"\hline"+"\n")
    f.write(r"\end{tabular}"+"\n")
    f.write(r"\end{table}"+"\n")
ax.set_ylim((0,len(states2010)+1))
ax.grid()
ax.set_xlim((-22,22))
ax.yaxis.set_major_locator(MaxNLocator(len(states2010)+2))
ax.set_yticklabels([""]+states2010[::-1]+[""])
fig.savefig(os.path.join(figDir,"diff2000to2010"+figExt))
#skew plot
sk = []
for idx,row in stateData.iterrows():
    year = row["year"]
    state = row["State"]
    cycle = year2Cycle(year)
    df = dataExp[dataExp["State"]==state]
    df = df[df["cycle"]==cycle]
    sk.append(df["expectedAsymPct"].tolist()[0]-row["specAsym (fraction)"])
fig = plt.figure()
ax  = fig.add_subplot(111)
ax.scatter(sk,stateData["demVoteFrac"])
ax.grid()
ax.set_xlabel("Expected Asymmetry - Observed Asymmetry")
ax.set_ylabel("Statewide Democratic Vote Share")
fig.savefig(os.path.join(figDir,"skew"+figExt))

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
fig.savefig(os.path.join(figDir,"ExpasmHist"+figExt))

