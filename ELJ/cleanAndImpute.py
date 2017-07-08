import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import us

states = us.states.STATES
abbr2name = us.states.mapping('abbr', 'name')
name2abbr = us.states.mapping('name', 'abbr')

dataDir       = "data"
np.seterr(all='raise')
#load in original csv and clean it up a bit
congress = pd.read_csv(os.path.join(dataDir,"US_House_elections_1898_2016.csv"))
congress['RepVotes'] = congress['RepVotes'].str.replace(',','') 
congress['RepVotes'] = congress['RepVotes'].str.replace('Unopposed','1') 
congress['RepVotes'] = congress['RepVotes'].astype(float) 
congress['DemVotes'] = congress['DemVotes'].str.replace(',','') 
congress['DemVotes'] = congress['DemVotes'].str.replace('Unopposed','1') 
congress['DemVotes'] = congress['DemVotes'].astype(float) 

cyc70 = [1972,1974,1976,1978,1980]
cyc80 = [1982,1984,1986,1988,1990]
cyc90 = [1992,1994,1996,1998,2000]
cyc00 = [2002,2004,2006,2008,2010]
cyc10 = [2012,2014,2016]
cycles = [cyc70,cyc80,cyc90,cyc00,cyc10]
cnames = [1970,1980,1990,2000,2010]

def year2Cycle(year):
    if 1972 <= year and year <=1980:
        return 1970
    elif 1982 <= year and year <=1990:
        return 1980
    elif 1992 <= year and year <=2000:
        return 1990
    elif 2002 <= year and year <=2010:
        return 2000
    else:
        return 2010

#Data by district and cycle
dataDC     = [['State','cycle','AreaNumber','avgDemFrac','avgRepFrac']]
#Data by state and cycle
dataSC     = [['State','cycle','avgDemFracInMostPartisanDem','avgDemFracInMostPartisanRep']]
#Data by state and year
dataSY     = [['State','year','contestedFrac','avgTurnout']]

for state in states:
    abbr = state.abbr
    if abbr == "DC": continue
    dfState = congress[congress["State"] == state.name]
    for cyc,cnm in zip(cycles,cnames):
        dfCycle = dfState[dfState["raceYear"].isin(cyc)]
        numDistricts = dfCycle["AreaNumber"].max()
        #Find the average vote percentages in the most partisan districts
        demInMostPartisanDem = []
        demInMostPartisanRep = []
        for year in cyc:
            dfYear = dfCycle[dfCycle["raceYear"] == year]
            #Filter uncontested
            dfYear = dfYear[dfYear["Dem Vote %"] != 0.0]
            dfYear = dfYear[dfYear["Dem Vote %"] != 1.0]
            #get average turnout
            if len(dfYear) > 0:
                avgTurnout = np.mean(dfYear["DemVotes"].values + dfYear["RepVotes"].values)
            else:
                avgTurnout = 0.
            dataSY.append([abbr,year,float(len(dfYear))/float(numDistricts),avgTurnout])

            if len(dfYear) > 0:
                mostPartisanDemIdx = dfYear["Dem Vote %"].argmax() 
                mostPartisanRepIdx = dfYear["Dem Vote %"].argmin() 

                demInMostPartisanDem.append(dfYear["Dem Vote %"].loc[mostPartisanDemIdx])
                demInMostPartisanRep.append(dfYear["Dem Vote %"].loc[mostPartisanRepIdx])
        
        avgDemFracInMostPartisanDem = np.mean(demInMostPartisanDem)
        avgDemFracInMostPartisanRep = np.mean(demInMostPartisanRep)
        dataSC.append([abbr,cnm,avgDemFracInMostPartisanDem,avgDemFracInMostPartisanRep])

        #Find the average dem and rep vote percentages in each district over all contested election in a cycle
        for i in range(numDistricts):
            dfDistrict = dfCycle[dfCycle["AreaNumber"] == i+1]
            votePct = np.array(dfDistrict["Dem Vote %"].values)
            #mask for uncontested elections
            mask = (votePct != 0.0) & (votePct != 1.0)
            demVote = np.array(dfDistrict["DemVotes"].values[mask])
            repVote = np.array(dfDistrict["RepVotes"].values[mask])
            if len(demVote) > 0:
                dmean = np.mean(votePct[mask])
            else:
                if votePct[0] == 0.0:
                    dmean = avgDemFracInMostPartisanRep
                elif votePct[0] == 1.0:
                    dmean = avgDemFracInMostPartisanDem
                else:
                    dmean = 0.0
            rmean = 1.-dmean
            dataDC.append([abbr,cnm,i+1,dmean,rmean])
            

yrs = []
con = []
for cyc,cnm in zip(cycles,cnames):
    for year in cyc:
        dfYear = congress[congress["raceYear"] == year]
        #Filter uncontested
        dfYear = dfYear[dfYear["Dem Vote %"] != 0.0]
        dfYear = dfYear[dfYear["Dem Vote %"] != 1.0]
        yrs.append(year)
        con.append(len(dfYear))
fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(yrs,con)
fig.savefig("contestedByYear.png")

data = pd.DataFrame(dataSY)
new_header = data.iloc[0] #grab the first row for the header
data = data[1:] #take the data less the header row
data.columns = new_header #set the header row as the df header
data.index = range(len(data))
#manually fix turnout for states with no contested elections
idx = data[data['avgTurnout']==0.].index.tolist()
stCol = data.columns.get_loc('State')
avCol = data.columns.get_loc('avgTurnout')
for i in idx:
    state   = data.iloc[i,stCol]
    avgTurnout = 0.
    count      = 0.
    if state == data.iloc[i-1,stCol]:
        avgTurnout += data.iloc[i-1,avCol]
        count += 1.
    if state == data.iloc[i+1,stCol]:
        avgTurnout += data.iloc[i+1,avCol]
        count += 1.
    data.iloc[i,avCol] = avgTurnout/count

fig = plt.figure()
ax = fig.add_subplot(111)
for state in states:
    abbr = state.abbr
    if abbr == "DC": continue
    dfState = data[data["State"] == abbr]
    ax.plot(dfState['contestedFrac'])
fig.savefig("contested.png")
data.to_csv(os.path.join(dataDir,"avgTurnout.csv"))

data = pd.DataFrame(dataDC)
new_header = data.iloc[0] #grab the first row for the header
data = data[1:] #take the data less the header row
data.columns = new_header #set the header row as the df header
data.index = range(len(data))
data.to_csv(os.path.join(dataDir,"avgVotesByDistrictAndCycle.csv"))

data = pd.DataFrame(dataSC)
new_header = data.iloc[0] #grab the first row for the header
data = data[1:] #take the data less the header row
data.columns = new_header #set the header row as the df header
data.index = range(len(data))
data.to_csv(os.path.join(dataDir,"avgVotesInMostPartisanByStateAndCycle.csv"))

imputeData = pd.read_csv(os.path.join(dataDir,"avgTurnout.csv"))
imputeData2 = pd.read_csv(os.path.join(dataDir,"avgVotesByDistrictAndCycle.csv"))
imputedRep = []
imputedDem = []
for idx,row in congress.iterrows():
    if row["Dem Vote %"] == 1.0 or row["Dem Vote %"] == 0.0:
        year = row["raceYear"]
        state = row["State"]
        dist = row["AreaNumber"]
        dfYear = imputeData[imputeData["year"]==year]
        dfState = dfYear[dfYear["State"]==name2abbr[state]]
        avgTurnout = dfState["avgTurnout"].values[0]
        #For 75-25 split method
        #if row["Dem Vote %"] == 1.0:
        #    imputedRep.append(avgTurnout*.25)
        #    imputedDem.append(avgTurnout*.75)
        #else:
        #    imputedRep.append(avgTurnout*.75)
        #    imputedDem.append(avgTurnout*.25)


        cycle = year2Cycle(year)
        dfCycle = imputeData2[imputeData2["cycle"]==cycle]
        dfState = dfCycle[dfCycle["State"]==name2abbr[state]]
        dfDist  = dfState[dfState["AreaNumber"]==dist]
        imputedRep.append(avgTurnout*dfDist["avgRepFrac"].values[0])
        imputedDem.append(avgTurnout*dfDist["avgDemFrac"].values[0])
    else:
        imputedRep.append(row["RepVotes"])
        imputedDem.append(row["DemVotes"])
congress['imputedRep'] = pd.Series(imputedRep, index=congress.index)
congress['imputedDem'] = pd.Series(imputedDem, index=congress.index)

#centered totals
congress['centeredRep'] = congress['imputedRep']
congress['centeredDem'] = congress['imputedDem']
for state in states:
    abbr = state.abbr
    if abbr == "DC": continue
    dfState = congress[congress["State"] == state.name]
    for cyc,cnm in zip(cycles,cnames):
        dfCycle = dfState[dfState["raceYear"].isin(cyc)]
        for year in cyc:
            dfYear = dfCycle[dfCycle["raceYear"] == year]
            idx = dfYear.index.tolist()
            totalDem = dfYear["imputedDem"].sum()
	    totalRep = dfYear["imputedRep"].sum()
	    totalAvg = (totalDem+totalRep)/2.
	    multDem = totalAvg/totalDem
	    multRep = totalAvg/totalRep
            
	    congress.iloc[idx,congress.columns.get_loc('centeredDem')] = dfYear["imputedDem"].values*multDem
	    congress.iloc[idx,congress.columns.get_loc('centeredRep')] = dfYear["imputedRep"].values*multRep

congress.to_csv(os.path.join(dataDir,"congressImputed.csv"))
