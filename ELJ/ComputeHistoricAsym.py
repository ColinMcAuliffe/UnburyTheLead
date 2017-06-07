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

from ELJcommon import getDemVotesAndSeats,get_spasym,get_asymFromPct,getExpAsym,varWithShrinkage,betaMOM,list2df,colorBins

states = us.states.STATES
abbr2name = us.states.mapping('abbr', 'name')

figDir       = "Figures"
dataDir      = "Data"

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
#Compute specific asymmetry and historic mean and stdv{{{1
data      = [['State','cycle','AreaNumber','Mean','Stdv','Var']]
stateData = [['State','STATEFP','year','demVotes','repVotes','demVoteFrac','repVoteFrac','demSeats','demSeatFrac','specAsym (seats)','specAsym (fraction)']]
fig = plt.figure(figsize=(10,8))
ax  = fig.add_subplot(211)
for state in states:
    abbr = state.abbr
    if abbr == "DC": continue
    dfState = congress[congress["State"].str.contains(state.name)]
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
            pcts = np.concatenate((pcts,[popVote]))
            sp2 = get_asymFromPct(pcts)
            if sp != sp2:
                print sp,sp2
            stateData.append([abbr,state.fips,year,dem_total,rep_total,popVote,1.-popVote,seats,seatFrac,sp,sp/float(len(dfYear))])
        ax.plot(cyc,mm,marker='x',color='0.5')

        for i in range(numDistricts):
            dfDistrict = dfCycle[dfCycle["AreaNumber"] == i+1]
            votePct = np.array(dfDistrict["Dem Vote %"].values)
            votePct = votePct[(votePct != 0.0) & (votePct != 1.0)] 
            if len(votePct) > 1:
                ddof = 0
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

ax.grid()
ax  = fig.add_subplot(212)
fig2 = plt.figure()
ax2  = fig2.add_subplot(111)
needlab = True
for cyc,cnm in zip(cycles,cnames):
    dfCycle = congress[congress["raceYear"].isin(cyc)]
    demStates = []
    repStates = []
    for state in states:
        abbr = state.abbr
        if abbr == "DC": continue
        dfState = dfCycle[dfCycle["State"].str.contains(state.name)]
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
        ax2.plot(cyc,pop,color='b',label="Congressional pop vote %")
        ax2.plot(cyc,sts,color='g',label="Congressional seat %")
        ax2.plot(cyc,sas,color='r',label="Congressional seat %, asymmetry removed")
        needlab=False
    else:
        ax2.plot(cyc,pop,color='b')
        ax2.plot(cyc,sts,color='g')
        ax2.plot(cyc,sas,color='r')

ax.grid()
fig.savefig(os.path.join(figDir,"historicSA.png"))
ax2.grid()
ax2.legend()
fig2.savefig(os.path.join(figDir,"sv.png"))

#Plot histograms of the stdv for each cycle
fig, ((ax1, ax2,ax3), (ax4, ax5, ax6)) = plt.subplots(2, 3, sharex=True, sharey=True,figsize=(10,8))
x   = np.linspace(0.,.3,100)

a,b,c,d = stats.beta.fit(data.Stdv.values[data.Stdv.values > 0.],floc=0.,fscale=1.)
y   = stats.beta.pdf(x,a,b)
ax1.hist(data.Stdv.values,50,normed=True)
ax1.plot(x,y,linewidth=4,color='g')
ax1.xaxis.set_major_locator(MaxNLocator(4))
ax1.yaxis.set_major_locator(MaxNLocator(4))
ax1.set_xlabel("All Cycles")
ax1.grid()

axhist  = [ax2,ax3,ax4,ax5,ax6]
mean = []
med  = []
p75  = []
for cyc,ax in zip(cnames,axhist):
    dfCycle = data[data["cycle"]==cyc]
    a,b,c,d = stats.beta.fit(dfCycle.Stdv.values[dfCycle.Stdv.values > 0.],floc=0.,fscale=1.)
    y   = stats.beta.pdf(x,a,b)
    ax.hist(dfCycle.Stdv.values,50,normed=True)
    ax.plot(x,y,linewidth=4,color='g')
    ax.xaxis.set_major_locator(MaxNLocator(4))
    ax.yaxis.set_major_locator(MaxNLocator(4))
    ax.set_xlabel(str(cyc))
    ax.grid()
    mean.append(np.mean(dfCycle.Stdv.values))
    med.append(np.median(dfCycle.Stdv.values))
    p75.append(np.percentile(dfCycle.Stdv.values,75))
fig.savefig(os.path.join(figDir,"StdvHist.png"))

#Plot histograms of the mean for each cycle
fig, ((ax1, ax2,ax3), (ax4, ax5, ax6)) = plt.subplots(2, 3, sharex=True, sharey=True,figsize=(10,8))
x   = np.linspace(0.,.3,100)

binsm = np.linspace(0.,1.0,51)
N, bins, patches = ax1.hist(data.Mean.values,bins=binsm,normed=True)
bins,patches = colorBins(bins,patches,0.5,lt='r',gt='b',gray=False)
ax1.xaxis.set_major_locator(MaxNLocator(4))
ax1.yaxis.set_major_locator(MaxNLocator(4))
ax1.set_xlabel("All Cycles")
ax1.grid()

axhist  = [ax2,ax3,ax4,ax5,ax6]
for cyc,ax in zip(cnames,axhist):
    dfCycle = data[data["cycle"]==cyc]
    N, bins, patches = ax.hist(dfCycle.Mean.values,bins=binsm,normed=True)
    bins,patches = colorBins(bins,patches,0.5,lt='r',gt='b',gray=False)
    ax.xaxis.set_major_locator(MaxNLocator(4))
    ax.yaxis.set_major_locator(MaxNLocator(4))
    ax.set_xlabel(str(cyc))
    ax.grid()
fig.savefig(os.path.join(figDir,"MeanHist.png"))

fig = plt.figure()
ax  = fig.add_subplot(111)
ax.plot(cnames,mean,label="mean")
ax.plot(cnames,med,label="median")
ax.plot(cnames,p75,label="75th percentile")
ax.grid()
ax.set_xlabel("election cycle")
ax.legend()
fig.savefig(os.path.join(figDir,"stdvDS.png"))

fig = plt.figure()
ax  = fig.add_subplot(111)
sorted = np.sort(data.Stdv.values)
yvals = np.arange(len(sorted))/float(len(sorted))
ax.plot(sorted, yvals)
ax.grid()
fig.savefig(os.path.join(figDir,"edf.png"))

#1}}}
#Obtain beta distribution parameters{{{1
#Get mean variance for each cycle
expVar = {}
for cyc in cnames:
    dfCycle = data[data["cycle"]==cyc]
    expVar[cyc] = np.mean(dfCycle["Var"].values)
dataAB      = [['State','cycle','AreaNumber','alpha','beta','loc','scale','mean','skew']]
dataABState = [['State','cycle','mean','alpha','beta','loc','scale','stdv of votePct']]
for state in states:
    abbr = state.abbr
    if abbr == "DC": continue
    dfState = congress[congress["State"].str.contains(state.name)]
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
            std.append(np.std(demPct,ddof=1))

        if np.std(pop) < 0.00001:
            alpha,beta,loc,scale = betaMOM(pop,useLocScale=False)
        else:
            alpha,beta,loc,scale = stats.beta.fit(pop,floc=0.,fscale=1.)
        dataABState.append([abbr,cnm,np.mean(pop),alpha,beta,loc,scale,np.mean(std)])

        numDistricts = dfCycle["AreaNumber"].max()
        #Beta params for each district
        for i in range(numDistricts):
            dfDistrict = dfCycle[dfCycle["AreaNumber"] == i+1]
            votePct = np.array(dfDistrict["imputedDem"].values/(dfDistrict["imputedRep"].values+dfDistrict["imputedDem"].values))
            if np.std(votePct) < 0.001:
                alpha,beta,loc,scale = betaMOM(votePct,shrinkage=expVar[cnm],useLocScale=False)
            else:
                alpha,beta,loc,scale = stats.beta.fit(votePct,floc=0.,fscale=1.)
            mean,skew = stats.beta.stats(alpha, beta, loc=loc, scale=scale, moments='ms')
            dataAB.append([abbr,cnm,i+1,alpha,beta,loc,scale,mean,skew])

list2df(dataAB,os.path.join(dataDir,"betaParams"))
dataAB = pd.read_csv(os.path.join(dataDir,"betaParams.csv"))

list2df(dataABState,os.path.join(dataDir,"betaParamsState"))
dataABState = pd.read_csv(os.path.join(dataDir,"betaParamsState.csv"))
#1}}}
#Plot maps of sp asymmetry{{{1
#shapeFileStates   = "../CommonData/ShapeFiles/cb_2015_us_state_500k/cb_2015_us_state_500k.shp"
#gdf = gpd.read_file(shapeFileStates)
#for cyc in cycles:
#    for year in cyc:
#        dfYear  = stateData[stateData["year"] == year]
#        gdfYear = gdf.merge(dfYear,on="STATEFP") 
#        utl.plotGDF(os.path.join(figDir,"spa_"+str(year)+".png"),gdfYear,"USALL",colorby="data",colorCol="specAsym (seats)",cmap=plt.cm.bwr,climits=(-6,6))
#        d = np.min([0.5 - np.min(dfYear["demVoteFrac"].values),np.max(dfYear["demVoteFrac"].values) - 0.5])
#        utl.plotGDF(os.path.join(figDir,"pop_"+str(year)+".png"),gdfYear,"USALL",colorby="data",colorCol="repVoteFrac",cmap=plt.cm.bwr,climits=(.5-d,0.5+d),cfmt="%0.2f")
#        
#1}}}

fig = plt.figure()
ax  = fig.add_subplot(111)
ax.scatter(stateData["demVoteFrac"].values,stateData["specAsym (seats)"].values)
fig.savefig(os.path.join(figDir,"sct.png"))

fig = plt.figure()
ax  = fig.add_subplot(111)
ax.scatter(stateData["demVoteFrac"].values,stateData["demSeatFrac"].values)
fig.savefig(os.path.join(figDir,"sct2.png"))

fig = plt.figure()
ax  = fig.add_subplot(111)
ax.scatter(dataAB["mean"].values,dataAB["skew"].values)
ax.set_xlabel("mean of estimated beta")
ax.set_ylabel("skew of estimated beta")
ax.grid()
fig.savefig(os.path.join(figDir,"sctMS.png"))

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
fig.savefig(os.path.join(figDir,"SpasmHist.png"))

