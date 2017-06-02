import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import utlUtilities as utl
import geopandas as gpd

import pandas as pd
import numpy as np
import os
import us
from scipy import stats

def getDemVotesAndSeats(dem,rep):
    dem_total = float(np.sum(dem))
    rep_total = float(np.sum(rep))
    popVote = dem_total/(dem_total+rep_total)
    demVotePct = dem/(dem+rep)
    seats = float(len(demVotePct[demVotePct>0.5]))
    seatFrac = seats/float(len(demVotePct))
    return dem_total,rep_total,popVote,seats,seatFrac

def get_spasym(dem,rep):
    if len(dem) > 2:
        dem = dem.astype(float)
        rep = rep.astype(float)
        dem_total = np.sum(dem)
        rep_total = np.sum(rep)
        popVote = np.sum(dem)/(np.sum(dem)+np.sum(rep))
        demVote = dem/(dem+rep)
        actSeats = float(len(demVote[demVote<0.5]))
        repFlp  = rep*dem_total/rep_total
        demFlp  = dem*rep_total/dem_total
        demVote = demFlp/(demFlp+repFlp)
        flpSeats = float(len(demVote[demVote>0.5]))

        return (actSeats-flpSeats)/2.
    else:
        return 0.


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

data      = [['State','cycle','AreaNumber','Mean','Stdv']]
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
            stateData.append([abbr,state.fips,year,dem_total,rep_total,popVote,1.-popVote,seats,seatFrac,sp,sp/float(len(dfYear))])
        ax.plot(cyc,mm,marker='x',color='0.5')

        for i in range(numDistricts):
            dfDistrict = dfCycle[dfCycle["AreaNumber"] == i+1]
            votePct = np.array(dfDistrict["Dem Vote %"].values)
            votePct = votePct[(votePct != 0.0) & (votePct != 1.0)] 
            if len(votePct) > 1:
                std = np.std(votePct,ddof=1)
                mean = np.mean(votePct)
                data.append([abbr,cnm,i+1,mean,std])

data = pd.DataFrame(data)
new_header = data.iloc[0] #grab the first row for the header
data = data[1:] #take the data less the header row
data.columns = new_header #set the header row as the df header
data.index = range(len(data))
data.to_csv("historicStdv.csv")

data = pd.read_csv("historicStdv.csv")

stateData = pd.DataFrame(stateData)
new_header = stateData.iloc[0] #grab the first row for the header
stateData = stateData[1:] #take the data less the header row
stateData.columns = new_header #set the header row as the df header
stateData.index = range(len(stateData))
stateData.to_csv("historicSAsym.csv")

stateDataLarge = stateData[stateData['specAsym (seats)'].abs() > 2]
stateDataLarge.to_csv("historicSAsymLarge.csv")


stateData = pd.read_csv("historicSAsym.csv",dtype={"STATEFP": object})

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

shapeFileStates   = "../CommonData/ShapeFiles/cb_2015_us_state_500k/cb_2015_us_state_500k.shp"
gdf = gpd.read_file(shapeFileStates)
for cyc in cycles:
    for year in cyc:
        dfYear  = stateData[stateData["year"] == year]
        gdfYear = gdf.merge(dfYear,on="STATEFP") 
        utl.plotGDF(os.path.join(figDir,"spa_"+str(year)+".png"),gdfYear,"USALL",colorby="data",colorCol="specAsym (seats)",cmap=plt.cm.bwr,climits=(-6,6))
        d = np.min([0.5 - np.min(dfYear["demVoteFrac"].values),np.max(dfYear["demVoteFrac"].values) - 0.5])
        utl.plotGDF(os.path.join(figDir,"pop_"+str(year)+".png"),gdfYear,"USALL",colorby="data",colorCol="repVoteFrac",cmap=plt.cm.bwr,climits=(.5-d,0.5+d),cfmt="%0.2f")
        

ax2.grid()
ax2.legend()
fig2.savefig(os.path.join(figDir,"sv.png"))

fig = plt.figure()
ax  = fig.add_subplot(111)
ax.scatter(stateData["demVoteFrac"].values,stateData["specAsym (seats)"].values)
fig.savefig(os.path.join(figDir,"sct.png"))

fig = plt.figure()
ax  = fig.add_subplot(111)
ax.scatter(stateData["demVoteFrac"].values,stateData["demSeatFrac"].values)
fig.savefig(os.path.join(figDir,"sct2.png"))

fig, ((ax1, ax2,ax3), (ax4, ax5, ax6)) = plt.subplots(2, 3, sharex=True, sharey=True,figsize=(18,10))
x   = np.linspace(0.,.3,100)

axhist  = [ax1,ax2,ax3,ax4,ax5]
bins = np.linspace(0.,12.,24)-6.
for cyc,cnm,ax in zip(cycles,cnames,axhist):
    spasm = []
    for year in cyc:
        dfYear = stateData[stateData["year"]==year]
        spasm = np.concatenate((spasm,dfYear["specAsym (seats)"].values))
    ax.hist(spasm,bins=bins,rwidth=0.5)
    ax.xaxis.set_major_locator(MaxNLocator(6))
    ax.yaxis.set_major_locator(MaxNLocator(6))
    ax.set_xlabel(str(cnm))
    ax.grid()
fig.savefig(os.path.join(figDir,"SpasmHist.png"))

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

