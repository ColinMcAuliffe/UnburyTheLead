import pandas as pd
import numpy as np
import os
import us

states = us.states.STATES
abbr2name = us.states.mapping('abbr', 'name')
name2abbr = us.states.mapping('name', 'abbr')

dataDir       = "data"

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
dataDC     = [['State','cycle','AreaNumber','avgDemVote','avgRepVote']]
#Data by state and cycle
dataSC     = [['State','cycle','avgDemVoteInMostPartisanDem','avgRepVoteInMostPartisanDem','avgDemVoteInMostPartisanRep','avgRepVoteInMostPartisanRep']]
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
        repInMostPartisanDem = []
        repInMostPartisanRep = []
        for year in cyc:
            dfYear = dfCycle[dfCycle["raceYear"] == year]
            #Filter uncontested
            dfYear = dfYear[dfYear["Dem Vote %"] != 0.0]
            dfYear = dfYear[dfYear["Dem Vote %"] != 1.0]

            if len(dfYear) > 0:
                mostPartisanDemIdx = dfYear["Dem Vote %"].argmax() 
                mostPartisanRepIdx = dfYear["Dem Vote %"].argmin() 

                demInMostPartisanDem.append(dfYear["DemVotes"].loc[mostPartisanDemIdx])
                demInMostPartisanRep.append(dfYear["DemVotes"].loc[mostPartisanRepIdx])
                repInMostPartisanDem.append(dfYear["RepVotes"].loc[mostPartisanDemIdx])
                repInMostPartisanRep.append(dfYear["RepVotes"].loc[mostPartisanRepIdx])
        
        avgDemVoteInMostPartisanDem = np.mean(demInMostPartisanDem)
        avgRepVoteInMostPartisanDem = np.mean(repInMostPartisanDem)
        avgDemVoteInMostPartisanRep = np.mean(demInMostPartisanRep)
        avgRepVoteInMostPartisanRep = np.mean(repInMostPartisanRep)
        dataSC.append([abbr,state.fips,cnm,avgDemVoteInMostPartisanDem,avgRepVoteInMostPartisanDem,avgDemVoteInMostPartisanRep,avgRepVoteInMostPartisanRep])

        #Find the average dem and rep vote percentages in each district over all contested election in a cycle
        for i in range(numDistricts):
            dfDistrict = dfCycle[dfCycle["AreaNumber"] == i+1]
            votePct = np.array(dfDistrict["Dem Vote %"].values)
            #mask for uncontested elections
            mask = (votePct != 0.0) & (votePct != 1.0)
            demVote = np.array(dfDistrict["DemVotes"].values[mask])
            repVote = np.array(dfDistrict["RepVotes"].values[mask])
            if len(demVote) > 0:
                dmean = np.mean(demVote)
                rmean = np.mean(repVote)
            else:
                if votePct[0] == 0.0:
                    dmean = avgDemVoteInMostPartisanRep
                    rmean = avgRepVoteInMostPartisanRep
                elif votePct[0] == 1.0:
                    dmean = avgDemVoteInMostPartisanDem
                    rmean = avgRepVoteInMostPartisanDem
                else:
                    dmean = 0.0
                    rmean = 0.0
            dataDC.append([abbr,cnm,i+1,dmean,rmean])
            


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

imputeData = pd.read_csv(os.path.join(dataDir,"avgVotesByDistrictAndCycle.csv"))
imputedRep = []
imputedDem = []
for idx,row in congress.iterrows():
    if row["Dem Vote %"] == 1.0 or row["Dem Vote %"] == 0.0:
        year = row["raceYear"]
        state = row["State"]
        dist = row["AreaNumber"]
        cycle = year2Cycle(year)
        dfCycle = imputeData[imputeData["cycle"]==cycle]
        dfState = dfCycle[dfCycle["State"]==name2abbr[state]]
        dfDist  = dfState[dfState["AreaNumber"]==dist]
        imputedRep.append(dfDist["avgRepVote"].values[0])
        imputedDem.append(dfDist["avgDemVote"].values[0])
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
