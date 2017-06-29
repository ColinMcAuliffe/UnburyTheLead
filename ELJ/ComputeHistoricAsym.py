import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import utlUtilities as utl
import geopandas as gpd
from matplotlib.patches import Rectangle

import pandas as pd
import numpy as np
import os
import us
from scipy import stats

from ELJcommon import getDemVotesAndSeats,get_spasym,get_asymFromPct,getExpAsym,varWithShrinkage,betaMOM,list2df,colorBins,get_asymFromCenteredPct

def setFontSize(ax,fs):
    for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] +
             ax.get_xticklabels() + ax.get_yticklabels()):
        item.set_fontsize(fs)
    plt.setp(ax.get_legend().get_texts(), fontsize=fs)
    return ax
states = us.states.STATES
abbr2name = us.states.mapping('abbr', 'name')

figDir       = os.path.join("Figures","HistoricAsymmetry")
dataDir      = "Data"
figExt       = ".png"

congress = pd.read_csv(os.path.join(dataDir,"congressImputed.csv"))

cyc70 = [1972,1974,1976,1978,1980]
cyc80 = [1982,1984,1986,1988,1990]
cyc90 = [1992,1994,1996,1998,2000]
cyc00 = [2002,2004,2006,2008,2010]
cyc10 = [2012,2014,2016]
cycles = [cyc70,cyc80,cyc90,cyc00,cyc10]
cnames = [1970,1980,1990,2000,2010]
bins6 = np.linspace(-6.25,6.25,26)
bins7 = np.linspace(-7.25,7.25,30)

oneByOne = (6.5,6.5)
#Compute specific asymmetry and historic mean and stdv{{{1
#Compute data{{{2
data      = [['State','cycle','AreaNumber','Mean','Stdv','Var']]
stateData = [['State','STATEFP','year','demVotes','repVotes','demVoteFrac','repVoteFrac','demSeats','demSeatFrac','specAsym (seats)','specAsym (fraction)','mean-median','margin','ndist']]
fig = plt.figure(figsize=(10,8))
ax  = fig.add_subplot(211)
for state in states:
    abbr = state.abbr
    if abbr == "DC": continue
    dfState = congress[congress["State"] == state.name]
    for cyc,cnm in zip(cycles,cnames):
        dfCycle = dfState[dfState["raceYear"].isin(cyc)]
        numDistricts = dfCycle["AreaNumber"].max()
        mm = []
        st = []
        for year in cyc:
            dfYear = dfCycle[dfCycle["raceYear"] == year]
            sp = get_spasym(dfYear["imputedDem"].values,dfYear["imputedRep"].values)
            mm.append(sp)
            dem_total,rep_total,popVote,seats,seatFrac = getDemVotesAndSeats(dfYear["imputedDem"].values,dfYear["imputedRep"].values)
            pcts = dfYear["imputedDem"].values/(dfYear["imputedDem"].values+dfYear["imputedRep"].values)
            if len(dfYear) > 1:
                meanMed = np.mean(pcts)-np.median(pcts)
            else:
                meanMed = 0.
            stateData.append([abbr,state.fips,year,dem_total,rep_total,popVote,1.-popVote,seats,seatFrac,sp,sp/float(len(dfYear)),meanMed,0.5-popVote,len(dfYear)])

        ax.plot(cyc,mm,marker='x',color='0.5')

        for i in range(numDistricts):
            dfDistrict = dfCycle[dfCycle["AreaNumber"] == i+1]
            votePct = np.array(dfDistrict["Dem Vote %"].values)
            votePct = votePct[(votePct != 0.0) & (votePct != 1.0)] 
            if len(votePct) > 1:
                ddof = 1
                std = np.std(votePct,ddof=ddof)
                var = np.var(votePct,ddof=ddof)
                mean = np.mean(votePct)
                data.append([abbr,cnm,i+1,mean,std,var])

list2df(data,os.path.join(dataDir,"historicStdv"))
data = pd.read_csv(os.path.join(dataDir,"historicStdv.csv"))

list2df(stateData,os.path.join(dataDir,"historicSAsym"))
stateData = pd.read_csv(os.path.join(dataDir,"historicSAsym.csv"),dtype={"STATEFP": object})

stateDataLarge = stateData[stateData['specAsym (seats)'].abs() > 2]
stateDataLarge.to_csv(os.path.join(dataDir,"historicSAsymLarge.csv"))
#2}}}
#Plot historic asymmetry and seats vs votes{{{2
ax.grid()
ax  = fig.add_subplot(212)
fig2 = plt.figure()
#fig2 = plt.figure(figsize=oneByOne)
ax2  = fig2.add_subplot(111)
needlab = True
for cyc,cnm in zip(cycles,cnames):
    dfCycle = congress[congress["raceYear"].isin(cyc)]
    demStates = []
    repStates = []
    for state in states:
        abbr = state.abbr
        if abbr == "DC": continue
        dfState = dfCycle[dfCycle["State"] == state.name]
        votePct = np.array(dfState["Dem Vote %"].values)
        demWon  = len(votePct[votePct > 0.5])
        if demWon > len(dfState)/2.:
            demStates.append(abbr)
        else:
            repStates.append(abbr)
    mm = []
    mmR = []
    mmD = []
    pop = []
    sts = []
    sas = []
    for year in cyc:
        dfYear = stateData[stateData["year"] == year]
        mm.append(np.sum(dfYear["specAsym (seats)"].values))

        dfYear = stateData[stateData["year"] == year]
        dfYear = dfYear[dfYear["State"].isin(repStates)]
        mmR.append(np.sum(dfYear["specAsym (seats)"].values))

        dfYear = stateData[stateData["year"] == year]
        dfYear = dfYear[dfYear["State"].isin(demStates)]
        mmD.append(np.sum(dfYear["specAsym (seats)"].values))

        dfYear = congress[congress["raceYear"] == year]
        dem_total = float(np.sum(dfYear["DemVotes"].values))
        rep_total = float(np.sum(dfYear["RepVotes"].values))
        popVote = dem_total/(dem_total+rep_total)
        seats = float(len(dfYear["Dem Vote %"].values[dfYear["Dem Vote %"].values>0.5]))
        totSeats = float(len(dfYear))
        seatFrac = seats/totSeats
        pop.append(popVote)
        sts.append(seatFrac)
        dfYear = stateData[stateData["year"] == year]
        sas.append(seatFrac+float(np.fix(np.sum(dfYear["specAsym (seats)"].values)))/totSeats)
    ax.plot(cyc,mm,marker='x',color='k',linewidth=4)
    ax.plot(cyc,mmR,marker='x',color='r',linewidth=4)
    ax.plot(cyc,mmD,marker='x',color='b',linewidth=4)
    if needlab:
        ax2.plot(cyc,pop,color='b',label="Pop vote share")
        ax2.plot(cyc,sts,color='g',label="Seat share")
        ax2.plot(cyc,sas,color='r',label="Seat share, asymmetry removed")
        needlab=False
    else:
        ax2.plot(cyc,pop,color='b')
        ax2.plot(cyc,sts,color='g')
        ax2.plot(cyc,sas,color='r')

ax.grid()
fig.savefig(os.path.join(figDir,"historicSA"+figExt))
ax2.grid()
ax2.set_xlabel("Year")
ax2.set_ylabel("Seat or Vote Share")
ax2.legend()
ax2 = setFontSize(ax2,12)
fig2.savefig(os.path.join(figDir,"sv"+figExt))
#2}}}
#plot asymmetry vs mean median difference{{{2
fig = plt.figure()
ax  = fig.add_subplot(111)
ax.scatter(stateData["specAsym (fraction)"].values,stateData["mean-median"].values)
closeStates = stateData[stateData["margin"].abs() < 0.03]
ax.scatter(closeStates["specAsym (fraction)"].values,closeStates["mean-median"].values,color='g')
ax.grid()
ax.set_xlabel("Specific Asymmetry")
ax.set_ylabel("Mean - Median")
fig.savefig(os.path.join(figDir,"sctMM"+figExt))
#2}}}
#Plot histograms of the stdv for each cycle{{{2
fig, ((ax1, ax2,ax3), (ax4, ax5, ax6)) = plt.subplots(2, 3, sharex=True, sharey=True)
xu = 0.015
x   = np.linspace(0.,xu,100)

a,b,c,d = stats.beta.fit(data.Var.values[data.Var.values > 0.],floc=0.,fscale=1.)
y   = stats.beta.pdf(x,a,b)
print np.mean(data.Var.values)
ax1.hist(data.Var.values,50,normed=True)
ax1.plot(x,y,linewidth=4,color='g')
ax1.xaxis.set_major_locator(MaxNLocator(4))
ax1.yaxis.set_major_locator(MaxNLocator(4))
ax1.set_xlim((0.,xu))
ax1.set_xlabel("All Cycles")
ax1.grid()

axhist  = [ax2,ax3,ax4,ax5,ax6]
mean = []
med  = []
p75  = []
for cyc,ax in zip(cnames,axhist):
    dfCycle = data[data["cycle"]==cyc]
    a,b,c,d = stats.beta.fit(dfCycle.Var.values[dfCycle.Stdv.values > 0.],floc=0.,fscale=1.)
    y   = stats.beta.pdf(x,a,b)
    ax.hist(dfCycle.Var.values,50,normed=True)
    ax.plot(x,y,linewidth=4,color='g')
    ax.xaxis.set_major_locator(MaxNLocator(4))
    ax.yaxis.set_major_locator(MaxNLocator(4))
    ax.set_xlabel(str(cyc))
    ax.grid()
    mean.append(np.mean(dfCycle.Var.values))
    med.append(np.median(dfCycle.Var.values))
    p75.append(np.percentile(dfCycle.Var.values,75))
fig.savefig(os.path.join(figDir,"VarHist"+figExt))
#2}}}
#Plot histograms of the mean for each cycle{{{2
fig, ((ax1, ax2,ax3), (ax4, ax5, ax6)) = plt.subplots(2, 3, sharex=True, sharey=True)
x   = np.linspace(0.,.3,100)

binsm = np.linspace(0.,1.0,51)
N, bins, patches = ax1.hist(data.Mean.values,bins=binsm,normed=True,linewidth=0)
bins,patches = colorBins(bins,patches,0.5,lt='r',gt='b',gray=False)
ax1.xaxis.set_major_locator(MaxNLocator(4))
ax1.yaxis.set_major_locator(MaxNLocator(4))
ax1.set_xlabel("All Cycles")
ax1.grid()

axhist  = [ax2,ax3,ax4,ax5,ax6]
for cyc,ax in zip(cnames,axhist):
    dfCycle = data[data["cycle"]==cyc]
    N, bins, patches = ax.hist(dfCycle.Mean.values,bins=binsm,normed=True,linewidth=0)
    bins,patches = colorBins(bins,patches,0.5,lt='r',gt='b',gray=False)
    ax.xaxis.set_major_locator(MaxNLocator(4))
    ax.yaxis.set_major_locator(MaxNLocator(4))
    ax.set_xlabel(str(cyc))
    ax.grid()
fig.savefig(os.path.join(figDir,"MeanHist"+figExt))
#2}}}
#Plot change in the stdv over time{{{2
fig = plt.figure()
ax  = fig.add_subplot(111)
ax.plot(cnames,mean,label="mean")
ax.plot(cnames,med,label="median")
ax.plot(cnames,p75,label="75th percentile")
ax.grid()
ax.set_xlabel("election cycle")
ax.legend()
fig.savefig(os.path.join(figDir,"stdvDS"+figExt))
#2}}}
#1}}}
#Obtain beta distribution parameters{{{1
#Get mean variance for each cycle
expVar = {}
for cyc in cnames:
    dfCycle = data[data["cycle"]==cyc]
    expVar[cyc] = np.mean(dfCycle["Var"].values)
expVarGlob = np.mean(data["Var"].values)
dataAB      = [['State','cycle','AreaNumber','alpha','beta','alphaCen','betaCen']]
dataABState = [['State','cycle','mean','alpha','beta','stdv of votePct']]
for state in states:
    abbr = state.abbr
    if abbr == "DC": continue
    dfState = congress[congress["State"] == state.name]
    for cyc,cnm in zip(cycles,cnames):
        dfCycle = dfState[dfState["raceYear"].isin(cyc)]
        #beta params for the state popular vote
        pop = []
        std = []
        for year in cyc:
            dfYear = dfCycle[dfCycle["raceYear"] == year]
            dem_total,rep_total,popVote,seats,seatFrac = getDemVotesAndSeats(dfYear["imputedDem"].values,dfYear["imputedRep"].values)
            demPct = dfYear["imputedDem"].values/(dfYear["imputedDem"].values+dfYear["imputedRep"].values)
            pop.append(popVote)
            if len(demPct) > 1:
                std.append(np.std(demPct,ddof=1))
            else:
                std.append(0.)

        alpha,beta,loc,scale = betaMOM(pop,useLocScale=False)
        dataABState.append([abbr,cnm,np.mean(pop),alpha,beta,np.mean(std)])

        numDistricts = dfCycle["AreaNumber"].max()
        #Beta params for each district
        for i in range(numDistricts):
            dfDistrict = dfCycle[dfCycle["AreaNumber"] == i+1]
            votePct = dfDistrict["centeredDem"].values/(dfDistrict["centeredDem"].values+dfDistrict["centeredRep"].values)
            #alphaCen,betaCen,locCen,scaleCen = betaMOM(votePct,shrinkage=expVarGlob,useLocScale=False)
            alphaCen,betaCen,locCen,scaleCen = betaMOM(votePct,shrinkage=expVar[cnm],useLocScale=False)
            votePct = dfDistrict["imputedDem"].values/(dfDistrict["imputedDem"].values+dfDistrict["imputedRep"].values)
            #alpha,beta,loc,scale = betaMOM(votePct,shrinkage=expVarGlob,useLocScale=False)
            alpha,beta,loc,scale = betaMOM(votePct,shrinkage=expVar[cnm],useLocScale=False)
            dataAB.append([abbr,cnm,i+1,alpha,beta,alphaCen,betaCen])

list2df(dataAB,os.path.join(dataDir,"betaParams"))
dataAB = pd.read_csv(os.path.join(dataDir,"betaParams.csv"))
#dAB = dataAB[dataAB["State"]=="WI"]
#dAB = dAB[dAB["cycle"]==2010]
#print dAB

list2df(dataABState,os.path.join(dataDir,"betaParamsState"))
dataABState = pd.read_csv(os.path.join(dataDir,"betaParamsState.csv"))
#dAB = dataABState[dataABState["State"]=="WI"]
#dAB = dAB[dAB["cycle"]==2010]
#print dAB
#1}}}

fig = plt.figure()
ax  = fig.add_subplot(111)
ax.scatter(stateData["demVoteFrac"].values,stateData["specAsym (seats)"].values)
fig.savefig(os.path.join(figDir,"sct"+figExt))

fig = plt.figure()
ax  = fig.add_subplot(111)
ax.scatter(stateData["demVoteFrac"].values,stateData["demSeatFrac"].values)
fig.savefig(os.path.join(figDir,"sct2"+figExt))

fig = plt.figure()
ax  = fig.add_subplot(111)

def ecdf(a):
    sorted=np.sort(a)
    x2 = []
    y2 = []
    y = 0
    for x in sorted: 
        x2.extend([x,x])
        y2.append(y)
        y += 1.0 / len(a)
        y2.append(y)
    return x2,y2

for cyc,cnm in zip(cycles,cnames):
    dfYear = stateData[stateData["year"].isin(cyc)]
    dfYear = dfYear[dfYear["ndist"] > 1]
    #dfYear = dfYear[dfYear["specAsym (seats)"].abs() > 0]
    x,y = ecdf(dfYear["specAsym (seats)"].values)
    ax.plot(x,y,label=str(cnm))

ax.grid()
ax.set_xlim((-6,6))
ax.set_ylim((0,1))
ax.legend(loc=2)
fig.savefig(os.path.join(figDir,"asymEdf"+figExt))

fig, ((ax1, ax2,ax3), (ax4, ax5, ax6)) = plt.subplots(2, 3, sharex=True, sharey=True,figsize=(18,10))

axhist  = [ax2,ax3,ax4,ax5,ax6]
spasmAll = []
for cyc,cnm,ax in zip(cycles,cnames,axhist):
    spasm = []
    for year in cyc:
        dfYear = stateData[stateData["year"]==year]
        spasm = np.concatenate((spasm,dfYear["specAsym (seats)"].values))
        spasmAll = np.concatenate((spasmAll,dfYear["specAsym (seats)"].values))
    N, bins, patches = ax.hist(spasm,bins=bins6,normed=True)
    bins,patches = colorBins(bins,patches,0.)

    ax.xaxis.set_major_locator(MaxNLocator(6))
    ax.yaxis.set_major_locator(MaxNLocator(6))
    ax.set_xlabel(str(cnm))
    ax.grid()

N, bins, patches = ax1.hist(spasmAll,bins=bins6,normed=True)
bins,patches = colorBins(bins,patches,0.)

ax1.set_xlabel("All Cycles")
ax1.grid()
fig.savefig(os.path.join(figDir,"SpasmHist"+figExt))

