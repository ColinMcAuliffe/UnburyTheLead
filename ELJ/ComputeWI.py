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
import glob
from matplotlib.patches import Rectangle


from ELJcommon import getDemVotesAndSeats,get_spasym,get_asymFromPct,getExpAsym,varWithShrinkage,betaMOM,list2df,colorBins,get_asymFromCenteredPct

figDir       = os.path.join("Figures","WI2010")
dataDir      = "Data"
figExt       = ".png"


#wiData = [['District','DemVotes','RepVotes','Year']]
#for txt in glob.glob(os.path.join(dataDir,"wi2000","*.txt")):
#    year = os.path.basename(txt)
#    try:
#        year = int(year.replace(".txt",""))
#    except:
#        continue
#    with open(txt,'r') as f:
#        for line in f:
#            line = line.split()
#            district = line[0]
#            line = list(line[18:20])
#            votes = [float(x.replace(",","")) for x in line]
#            wiData.append([district]+votes+[year])

#list2df(wiData,os.path.join(dataDir,"wi2000_vote_counts"))
wiAssembly2 = pd.read_csv(os.path.join(dataDir,"wi2000","wi2000_vote_counts.csv"))

wiAssembly = pd.read_csv(os.path.join(dataDir,"wi2010","wi2010_vote_counts.csv"))
wiAssembly['DemVotes'] = wiAssembly['DemVotes'].astype(float) 
wiAssembly['RepVotes'] = wiAssembly['RepVotes'].astype(float) 

cyc00 = [2006,2008,2010]
cyc10 = [2012,2014,2016]
cycles = [cyc00,cyc10]
cnames = [2000,2010]
bins6 = np.linspace(-6.25,6.25,26)
bins7 = np.linspace(-7.25,7.25,30)

#Compute specific asymmetry and historic mean and stdv{{{1
#Compute data{{{2
stateData = [['year','demVotes','repVotes','demVoteFrac','repVoteFrac','demSeats','demSeatFrac','specAsym (seats)','specAsym (fraction)','mean-median','margin']]
fig = plt.figure(figsize=(10,8))
ax  = fig.add_subplot(211)
for cyc,cnm in zip(cycles,cnames):
    dfCycle = wiAssembly[wiAssembly["Year"].isin(cyc)]
    numDistricts = dfCycle["District"].max()
    mm = []
    st = []
    for year in cyc:
        dfYear = dfCycle[dfCycle["Year"] == year]
        sp = get_spasym(dfYear["DemVotes"].values,dfYear["RepVotes"].values)
        mm.append(sp)
        dem_total,rep_total,popVote,seats,seatFrac = getDemVotesAndSeats(dfYear["DemVotes"].values,dfYear["RepVotes"].values)
        pcts = dfYear["DemVotes"].values/(dfYear["DemVotes"].values+dfYear["RepVotes"].values)
        if len(dfYear) > 1:
            meanMed = np.mean(pcts)-np.median(pcts)
        else:
            meanMed = 0.
        stateData.append([year,dem_total,rep_total,popVote,1.-popVote,seats,seatFrac,sp,sp/float(len(dfYear)),meanMed,0.5-popVote])

    ax.plot(cyc,mm,marker='x',color='0.5')

list2df(stateData,os.path.join(dataDir,"historicSAsymWI"))
stateData = pd.read_csv(os.path.join(dataDir,"historicSAsymWI.csv"),dtype={"STATEFP": object})
print stateData[["specAsym (seats)","year"]]
print 99-stateData['demSeats']

#2}}}
#Compute data with 2000 districts{{{2
stateData2 = [['year','demVotes','repVotes','demVoteFrac','repVoteFrac','demSeats','demSeatFrac','specAsym (seats)','specAsym (fraction)','mean-median','margin']]
fig = plt.figure(figsize=(10,8))
ax  = fig.add_subplot(211)
for cyc,cnm in zip(cycles,cnames):
    dfCycle = wiAssembly2[wiAssembly2["Year"].isin(cyc)]
    numDistricts = dfCycle["District"].max()
    mm = []
    st = []
    for year in cyc:
        dfYear = dfCycle[dfCycle["Year"] == year]
        sp = get_spasym(dfYear["DemVotes"].values,dfYear["RepVotes"].values)
        mm.append(sp)
        dem_total,rep_total,popVote,seats,seatFrac = getDemVotesAndSeats(dfYear["DemVotes"].values,dfYear["RepVotes"].values)
        pcts = dfYear["DemVotes"].values/(dfYear["DemVotes"].values+dfYear["RepVotes"].values)
        if len(dfYear) > 1:
            meanMed = np.mean(pcts)-np.median(pcts)
        else:
            meanMed = 0.
        stateData2.append([year,dem_total,rep_total,popVote,1.-popVote,seats,seatFrac,sp,sp/float(len(dfYear)),meanMed,0.5-popVote])

    ax.plot(cyc,mm,marker='x',color='0.5')

list2df(stateData2,os.path.join(dataDir,"historicSAsymWI2000"))
stateData2 = pd.read_csv(os.path.join(dataDir,"historicSAsymWI2000.csv"),dtype={"STATEFP": object})
print stateData2[["specAsym (seats)","year",'demSeats']]
print 99-stateData2['demSeats']
fig = plt.figure()
ax1 = fig.add_subplot(111)
ax1.plot(stateData2["year"].values,99-stateData2["demSeats"].values,color='b',label="Seat Count, 2000 Map")
ax1.plot(stateData2["year"].values[3:],99-stateData2["demSeats"].values[3:],ms=8,mew=3,marker="x",ls="None",color='b')

ax1.plot(stateData["year"].values,99-stateData["demSeats"].values,color='g',label="Seat Count, 2010 map")
ax1.plot(stateData["year"].values[0:3],99-stateData["demSeats"].values[0:3],ms=8,mew=3,marker="x",color='g')
ax1.set_ylim(33,66)
ax1.set_xlim((2005,2017))
ax1.set_ylabel("Republican Seats Won")
ax1.legend(loc=4)
ax1.grid()
fig.savefig(os.path.join(figDir,"WI_2000_2010_seats"+figExt))

p5_2000  = 0.18181818181818177*99./2.
p25_2000 = 0.13131313131313127*99./2.
p75_2000 = 0.06060606060606061*99./2.
p95_2000 = 0.010101010101010055*99./2.
m2000    = np.array([0.09425757575754891*99/2.]*6)
p5_2010  = 0.25252525252525254*99./2.
p25_2010 = 0.21212121212121215*99./2.
p75_2010 = 0.1515151515151515*99./2.
p95_2010 = 0.11111111111111105*99./2.
m2010    = np.array([0.1815279797979752*99/2.]*6)
fig = plt.figure()
ax2 = fig.add_subplot(111)
ax2.plot(stateData2["year"].values,m2000,color='b',ls="--",linewidth=3,label="Exp. Asym. 2000 map")
#ax2.add_patch(Rectangle((2006,p5_2000),10,p95_2000-p5_2000,color='b',alpha=0.2))
ax2.add_patch(Rectangle((2006,p25_2000),10,p75_2000-p25_2000,color='b',alpha=0.2))

ax2.plot(stateData2["year"].values,m2010,color='g',ls="--",linewidth=3,label="Exp. Asym. 2010 map")
#ax2.add_patch(Rectangle((2006,p5_2010),10,p95_2010-p5_2010,color='g',alpha=0.2))
ax2.add_patch(Rectangle((2006,p25_2010),10,p75_2010-p25_2010,color='g',alpha=0.2))

ax2.plot(stateData2["year"].values[3:],stateData2["specAsym (seats)"].values[3:],ms=8,mew=3,marker="x",ls="None",color='m')
ax2.plot(stateData2["year"].values,stateData2["specAsym (seats)"].values,color='m',label="Obs. Asym. 2000 Map")

ax2.plot(stateData["year"].values,stateData["specAsym (seats)"].values,color='r',label="Obs. Asym. 2010 map")
ax2.plot(stateData["year"].values[0:3],stateData["specAsym (seats)"].values[0:3],ms=8,mew=3,marker="x",color='r')
ax2.grid()


ax2.set_ylim(-14,14)
ax2.set_xlim((2005,2017))
ax2.set_ylabel("Asymmetry, Seats")
ax2.legend(loc=4,ncol=2)
fig.savefig(os.path.join(figDir,"WI_2000_2010"+figExt))

fig = plt.figure()
ax1 = fig.add_subplot(111)
diff = stateData2["demSeats"]-stateData["demSeats"]
diffm = [np.mean(diff)]*6
ax1.add_patch(Rectangle((2006,p5_2010-m2000[0]),10,p95_2010-p5_2010,color='b',alpha=0.2))
ax1.add_patch(Rectangle((2006,p25_2010-m2000[0]),10,p75_2010-p25_2010,color='b',alpha=0.4))
ax1.plot(stateData2["year"].values,m2010-m2000,color='b',ls="--",linewidth=3,label="Difference in Exp. Asym.")
ax1.plot(stateData2["year"].values,diff,color='r',linewidth=2,label="Difference in Seats")
ax1.plot(stateData2["year"].values,diffm,color='r',ls="--",linewidth=3,label="Average Difference in Seats")
ax1.legend(loc=4)
ax1.set_ylabel("Seats")
fig.savefig(os.path.join(figDir,"WI_2000_2010diff"+figExt))

#2}}}
##Plot historic asymmetry and seats vs votes{{{2
#ax.grid()
#ax  = fig.add_subplot(212)
#fig2 = plt.figure()
##fig2 = plt.figure(figsize=oneByOne)
#ax2  = fig2.add_subplot(111)
#needlab = True
#for cyc,cnm in zip(cycles,cnames):
#    dfCycle = congress[congress["raceYear"].isin(cyc)]
#    demStates = []
#    repStates = []
#    for state in states:
#        abbr = state.abbr
#        if abbr == "DC": continue
#        dfState = dfCycle[dfCycle["State"] == state.name]
#        votePct = np.array(dfState["Dem Vote %"].values)
#        demWon  = len(votePct[votePct > 0.5])
#        if demWon > len(dfState)/2.:
#            demStates.append(abbr)
#        else:
#            repStates.append(abbr)
#    mm = []
#    mmR = []
#    mmD = []
#    pop = []
#    sts = []
#    sas = []
#    for year in cyc:
#        dfYear = stateData[stateData["year"] == year]
#        mm.append(np.sum(dfYear["specAsym (seats)"].values))
#
#        dfYear = stateData[stateData["year"] == year]
#        dfYear = dfYear[dfYear["State"].isin(repStates)]
#        mmR.append(np.sum(dfYear["specAsym (seats)"].values))
#
#        dfYear = stateData[stateData["year"] == year]
#        dfYear = dfYear[dfYear["State"].isin(demStates)]
#        mmD.append(np.sum(dfYear["specAsym (seats)"].values))
#
#        dfYear = congress[congress["raceYear"] == year]
#        dem_total = float(np.sum(dfYear["DemVotes"].values))
#        rep_total = float(np.sum(dfYear["RepVotes"].values))
#        popVote = dem_total/(dem_total+rep_total)
#        seats = float(len(dfYear["Dem Vote %"].values[dfYear["Dem Vote %"].values>0.5]))
#        totSeats = float(len(dfYear))
#        seatFrac = seats/totSeats
#        pop.append(popVote)
#        sts.append(seatFrac)
#        dfYear = stateData[stateData["year"] == year]
#        sas.append(seatFrac+float(np.fix(np.sum(dfYear["specAsym (seats)"].values)))/totSeats)
#    ax.plot(cyc,mm,marker='x',color='k',linewidth=4)
#    ax.plot(cyc,mmR,marker='x',color='r',linewidth=4)
#    ax.plot(cyc,mmD,marker='x',color='b',linewidth=4)
#    if needlab:
#        ax2.plot(cyc,pop,color='b',label="Pop vote share")
#        ax2.plot(cyc,sts,color='g',label="Seat share")
#        ax2.plot(cyc,sas,color='r',label="Seat share, asymmetry removed")
#        needlab=False
#    else:
#        ax2.plot(cyc,pop,color='b')
#        ax2.plot(cyc,sts,color='g')
#        ax2.plot(cyc,sas,color='r')
#
#ax.grid()
#fig.savefig(os.path.join(figDir,"historicSA"+figExt))
#ax2.grid()
#ax2.set_xlabel("Year")
#ax2.set_ylabel("Seat or Vote Share")
#ax2.legend()
#ax2 = setFontSize(ax2,12)
#fig2.savefig(os.path.join(figDir,"sv"+figExt))
##2}}}
##plot asymmetry vs mean median difference{{{2
#fig = plt.figure()
#ax  = fig.add_subplot(111)
#ax.scatter(stateData["specAsym (fraction)"].values,stateData["mean-median"].values)
#closeStates = stateData[stateData["margin"].abs() < 0.03]
#ax.scatter(closeStates["specAsym (fraction)"].values,closeStates["mean-median"].values,color='g')
#ax.grid()
#ax.set_xlabel("Specific Asymmetry")
#ax.set_ylabel("Mean - Median")
#fig.savefig(os.path.join(figDir,"sctMM"+figExt))
##2}}}
##Plot histograms of the stdv for each cycle{{{2
#fig, ((ax1, ax2,ax3), (ax4, ax5, ax6)) = plt.subplots(2, 3, sharex=True, sharey=True,figsize=(10,8))
#x   = np.linspace(0.,.3,100)
#
#a,b,c,d = stats.beta.fit(data.Stdv.values[data.Stdv.values > 0.],floc=0.,fscale=1.)
#y   = stats.beta.pdf(x,a,b)
#ax1.hist(data.Stdv.values,50,normed=True)
#ax1.plot(x,y,linewidth=4,color='g')
#ax1.xaxis.set_major_locator(MaxNLocator(4))
#ax1.yaxis.set_major_locator(MaxNLocator(4))
#ax1.set_xlabel("All Cycles")
#ax1.grid()
#
#axhist  = [ax2,ax3,ax4,ax5,ax6]
#mean = []
#med  = []
#p75  = []
#for cyc,ax in zip(cnames,axhist):
#    dfCycle = data[data["cycle"]==cyc]
#    a,b,c,d = stats.beta.fit(dfCycle.Stdv.values[dfCycle.Stdv.values > 0.],floc=0.,fscale=1.)
#    y   = stats.beta.pdf(x,a,b)
#    ax.hist(dfCycle.Stdv.values,50,normed=True)
#    ax.plot(x,y,linewidth=4,color='g')
#    ax.xaxis.set_major_locator(MaxNLocator(4))
#    ax.yaxis.set_major_locator(MaxNLocator(4))
#    ax.set_xlabel(str(cyc))
#    ax.grid()
#    mean.append(np.mean(dfCycle.Stdv.values))
#    med.append(np.median(dfCycle.Stdv.values))
#    p75.append(np.percentile(dfCycle.Stdv.values,75))
#fig.savefig(os.path.join(figDir,"StdvHist"+figExt))
##2}}}
##Plot histograms of the mean for each cycle{{{2
#fig, ((ax1, ax2,ax3), (ax4, ax5, ax6)) = plt.subplots(2, 3, sharex=True, sharey=True,figsize=(10,8))
#x   = np.linspace(0.,.3,100)
#
#binsm = np.linspace(0.,1.0,51)
#N, bins, patches = ax1.hist(data.Mean.values,bins=binsm,normed=True)
#bins,patches = colorBins(bins,patches,0.5,lt='r',gt='b',gray=False)
#ax1.xaxis.set_major_locator(MaxNLocator(4))
#ax1.yaxis.set_major_locator(MaxNLocator(4))
#ax1.set_xlabel("All Cycles")
#ax1.grid()
#
#axhist  = [ax2,ax3,ax4,ax5,ax6]
#for cyc,ax in zip(cnames,axhist):
#    dfCycle = data[data["cycle"]==cyc]
#    N, bins, patches = ax.hist(dfCycle.Mean.values,bins=binsm,normed=True)
#    bins,patches = colorBins(bins,patches,0.5,lt='r',gt='b',gray=False)
#    ax.xaxis.set_major_locator(MaxNLocator(4))
#    ax.yaxis.set_major_locator(MaxNLocator(4))
#    ax.set_xlabel(str(cyc))
#    ax.grid()
#fig.savefig(os.path.join(figDir,"MeanHist"+figExt))
##2}}}
##Plot change in the stdv over time{{{2
#fig = plt.figure()
#ax  = fig.add_subplot(111)
#ax.plot(cnames,mean,label="mean")
#ax.plot(cnames,med,label="median")
#ax.plot(cnames,p75,label="75th percentile")
#ax.grid()
#ax.set_xlabel("election cycle")
#ax.legend()
#fig.savefig(os.path.join(figDir,"stdvDS"+figExt))
##2}}}
##1}}}
##Obtain beta distribution parameters{{{1
##Get mean variance for each cycle
#expVar = {}
#for cyc in cnames:
#    dfCycle = data[data["cycle"]==cyc]
#    expVar[cyc] = np.mean(dfCycle["Var"].values)
#expVarGlob = np.mean(data["Var"].values)
#dataAB      = [['State','cycle','AreaNumber','alpha','beta','alphaCen','betaCen']]
#dataABState = [['State','cycle','mean','alpha','beta','stdv of votePct']]
#for state in states:
#    abbr = state.abbr
#    if abbr == "DC": continue
#    dfState = congress[congress["State"] == state.name]
#    for cyc,cnm in zip(cycles,cnames):
#        dfCycle = dfState[dfState["raceYear"].isin(cyc)]
#        #beta params for the state popular vote
#        pop = []
#        std = []
#        for year in cyc:
#            dfYear = dfCycle[dfCycle["raceYear"] == year]
#            dem_total,rep_total,popVote,seats,seatFrac = getDemVotesAndSeats(dfYear["imputedDem"].values,dfYear["imputedRep"].values)
#            demPct = dfYear["imputedDem"].values/(dfYear["imputedDem"].values+dfYear["imputedRep"].values)
#            pop.append(popVote)
#            if len(demPct) > 1:
#                std.append(np.std(demPct,ddof=1))
#            else:
#                std.append(0.)
#
#        alpha,beta,loc,scale = betaMOM(pop,useLocScale=False)
#        dataABState.append([abbr,cnm,np.mean(pop),alpha,beta,np.mean(std)])
#
#        numDistricts = dfCycle["AreaNumber"].max()
#        #Beta params for each district
#        for i in range(numDistricts):
#            dfDistrict = dfCycle[dfCycle["AreaNumber"] == i+1]
#            votePct = dfDistrict["centeredDem"].values/(dfDistrict["centeredDem"].values+dfDistrict["centeredRep"].values)
#            alphaCen,betaCen,locCen,scaleCen = betaMOM(votePct,shrinkage=expVarGlob,useLocScale=False)
#            votePct = dfDistrict["imputedDem"].values/(dfDistrict["imputedDem"].values+dfDistrict["imputedRep"].values)
#            alpha,beta,loc,scale = betaMOM(votePct,shrinkage=expVarGlob,useLocScale=False)
#            dataAB.append([abbr,cnm,i+1,alpha,beta,alphaCen,betaCen])
#
#list2df(dataAB,os.path.join(dataDir,"betaParams"))
#dataAB = pd.read_csv(os.path.join(dataDir,"betaParams.csv"))
##dAB = dataAB[dataAB["State"]=="WI"]
##dAB = dAB[dAB["cycle"]==2010]
##print dAB
#
#list2df(dataABState,os.path.join(dataDir,"betaParamsState"))
#dataABState = pd.read_csv(os.path.join(dataDir,"betaParamsState.csv"))
##dAB = dataABState[dataABState["State"]=="WI"]
##dAB = dAB[dAB["cycle"]==2010]
##print dAB
##1}}}
#
#fig = plt.figure()
#ax  = fig.add_subplot(111)
#ax.scatter(stateData["demVoteFrac"].values,stateData["specAsym (seats)"].values)
#fig.savefig(os.path.join(figDir,"sct"+figExt))
#
#fig = plt.figure()
#ax  = fig.add_subplot(111)
#ax.scatter(stateData["demVoteFrac"].values,stateData["demSeatFrac"].values)
#fig.savefig(os.path.join(figDir,"sct2"+figExt))
#
#fig, ((ax1, ax2,ax3), (ax4, ax5, ax6)) = plt.subplots(2, 3, sharex=True, sharey=True,figsize=(18,10))
#
#axhist  = [ax2,ax3,ax4,ax5,ax6]
#spasmAll = []
#for cyc,cnm,ax in zip(cycles,cnames,axhist):
#    spasm = []
#    for year in cyc:
#        dfYear = stateData[stateData["year"]==year]
#        spasm = np.concatenate((spasm,dfYear["specAsym (seats)"].values))
#        spasmAll = np.concatenate((spasmAll,dfYear["specAsym (seats)"].values))
#    N, bins, patches = ax.hist(spasm,bins=bins6,normed=True)
#    bins,patches = colorBins(bins,patches,0.)
#
#    ax.xaxis.set_major_locator(MaxNLocator(6))
#    ax.yaxis.set_major_locator(MaxNLocator(6))
#    ax.set_xlabel(str(cnm))
#    ax.grid()
#
#N, bins, patches = ax1.hist(spasmAll,bins=bins6,normed=True)
#bins,patches = colorBins(bins,patches,0.)
#
#ax1.set_xlabel("All Cycles")
#ax1.grid()
#fig.savefig(os.path.join(figDir,"SpasmHist"+figExt))
#
