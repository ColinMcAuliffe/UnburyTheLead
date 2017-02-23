import matplotlib.pyplot as plt
import utlUtilities as utl
import geopandas as gpd
import pandas as pd
import numpy as np
import pysal
import os

# list of state abbreviations
states = ['AL','AK','AZ','AR','CA','CO','CT','DC','DE','FL','GA','HI','ID','IL','IN','IA','KS','KY','LA','ME','MD','MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ','NM','NY','NC','ND','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VT','VA','WA','WV','WI','WY']

shapeFileCounties = "../CommonData/ShapeFiles/cb_2015_us_county_500k/cb_2015_us_county_500k.shp"
shapeFileStates   = "../CommonData/ShapeFiles/cb_2015_us_state_500k/cb_2015_us_state_500k.shp"
countyData        = "../CommonData/Presidential_Election_2016_Results/2016_pres_votes_by_county.csv"
stateData         = "../CommonData/Presidential_Election_2016_Results/2016_pres_votes_by_state.csv"

dfStates   = utl.mergeGDF(shapeFileStates,stateData,"STATEFP")
dfCounties = utl.mergeGDF(shapeFileCounties,countyData,"GEOID")

figDir       = "Figures"

#Read shape file and compute neighbors by county
print "computing neighboring counties"
w  = pysal.weights.Queen.from_dataframe(dfCounties)
#Make a list of the geoids of border counties
borderCounties = []
for index,row in dfCounties.iterrows():
    state = row["STATEFP"]
    neighbors = w.neighbors[index]
    if len(neighbors) == 0:continue
    if np.any(dfCounties.STATEFP.values[neighbors]!=state): borderCounties.append(row["GEOID"])

def flagRepBorder(row):
    if row["GEOID"] in borderCounties and row["rep_votes"] > row["dem_votes"]:
        return True
    else:
        return False

def flagDemBorder(row):
    if row["GEOID"] in borderCounties and row["dem_votes"] > row["rep_votes"]:
        return True
    else:
        return False

dfCounties["isDemBorder"] = dfCounties.apply(flagDemBorder,axis=1)
dfCounties["isRepBorder"] = dfCounties.apply(flagRepBorder,axis=1)

#replace commas for 2008 election data
def replComma(x):
    try:
        x = float(x.replace(",",""))
    except:
        pass
    return x

#Compute efficiency gap and weighted efficiency gap for 2008 and 2016
state2008 = pd.read_csv("../CommonData/PriorPresResults/2008_pres_votes_by_state.csv")
state2012 = pd.read_csv("../CommonData/PriorPresResults/2012_pres_votes_by_state.csv")

demWasted2008,repWasted2008,EG2008,EGEV2008,demVotePct2008,demStatePct2008,demEvotePct2008 = utl.getEfficiencyGap(state2008)
demWasted2012,repWasted2012,EG2012,EGEV2012,demVotePct2012,demStatePct2012,demEvotePct2012 = utl.getEfficiencyGap(state2012)
demWasted2016,repWasted2016,EG2016,EGEV2016,demVotePct2016,demStatePct2016,demEvotePct2016 = utl.getEfficiencyGap(dfStates)

ms = 8
pctLim = (40.,60.)
fig = plt.figure()
ax  = fig.add_subplot(111)
ax.plot(pctLim,pctLim,color='k',label="Proportional")
ax.plot(demVotePct2008,demEvotePct2008,marker = ".",color='b',linestyle="None",markersize=ms,label="2008 result")
ax.plot(demVotePct2012,demEvotePct2012,marker = "d",color='b',linestyle="None",markersize=ms,label="2012 result")
ax.plot(demVotePct2016,demEvotePct2016,marker = ".",color='r',linestyle="None",markersize=ms,label="2016 result")
ax.plot([demVotePct2008,demVotePct2008],[demVotePct2008,demEvotePct2008],color='b',label="2008 electoral efficiency")
ax.plot([demVotePct2012,demVotePct2012],[demVotePct2012,demEvotePct2012],color='b',label="2012 electoral efficiency",linestyle="--")
ax.plot([demVotePct2016,demVotePct2016],[demVotePct2016,demEvotePct2016],color='r',label="2016 electoral efficiency")
ax.set_xlabel("Democratic % of Popular Vote")
ax.set_ylabel("Democratic % of Electoral Vote")
ax.grid()
ax.set_xlim((45.,55.))
ax.set_ylim((30.,70.))
ax.legend(loc=2)
fig.savefig(os.path.join(figDir,"prop1.png"))

fig = plt.figure()
ax  = fig.add_subplot(111)
ax.plot(pctLim,pctLim,color='k',label="Proportional")
ax.plot(demVotePct2008,demEvotePct2008,marker = ".",color='b',linestyle="None",markersize=ms,label="2008, actual")
ax.plot(demVotePct2012,demEvotePct2012,marker = "d",color='b',linestyle="None",markersize=ms,label="2012, actual")
ax.plot(demVotePct2016,demEvotePct2016,marker = ".",color='r',linestyle="None",markersize=ms,label="2016, actual")
demVote,demEvote = utl.getVotesEvotesCurve(state2008,.2,100)
ax.plot(demVote,demEvote,color='b',label="2008, hypothetical")
demVote,demEvote = utl.getVotesEvotesCurve(state2012,.2,100)
ax.plot(demVote,demEvote,color='b',label="2012, hypothetical",linestyle="--")
demVote,demEvote = utl.getVotesEvotesCurve(dfStates,.2,100)
ax.plot(demVote,demEvote,color='r',label="2016, hypothetical")
ax.set_xlabel("Democratic % of Popular Vote")
ax.set_ylabel("Democratic % of Electoral Vote")
ax.grid()
ax.set_xlim((45.,55.))
ax.set_ylim((30.,70.))
ax.legend(loc=2)
fig.savefig(os.path.join(figDir,"prop2.png"))

tabData = [["Year","Wasted Dem. Votes (Millions)","Wasted Rep. Votes (Millions)","Efficiency Gap"]]
tabData.append(["2008"]+["%10.2f" %(x/1000000.) for x in [demWasted2008,repWasted2008]]+["Dem. %10.2f" %(np.abs(EG2008))+"%"])
tabData.append(["2012"]+["%10.2f" %(x/1000000.) for x in [demWasted2012,repWasted2012]]+["Dem. %10.2f" %(np.abs(EG2012))+"%"])
tabData.append(["2016"]+["%10.2f" %(x/1000000.) for x in [demWasted2016,repWasted2016]]+["Rep. %10.2f" %(EG2016)+"%"])
utl.html_table(tabData,os.path.join(figDir,"EG.html"))

print "plotting border counties"
boolDict = {"conditions":{"isDemBorder":'b',"isRepBorder":'r'},"default":'w'}
utl.plotGDF(os.path.join(figDir,"borderCounties.png"),dfCounties,"USALL",colorby="boolDict",boolDict=boolDict,title="Border Counties")
#Thumbnail
utl.plotGDF(os.path.join(figDir,"thumb.png"),dfCounties,"USALL",colorby="boolDict",boolDict=boolDict)

#make a dictionary mapping combined state and county name to combined fips
combName2GEOID = {}
for index, row in dfCounties.iterrows():
    key = row["state_abbr"]+row["county_name"]
    combName2GEOID[key] = row["GEOID"]

#shuffle and plot{{{1
def shuffle_and_plot(stateData,shuffleDict,name,prettyName):
    stateData1 = stateData.copy()
    #use 0 base indexing
    stateData1.index = range(len(stateData1))
    #recompute vote tallies and create mapping of county FIPS to new state
    county2state = {}
    total_counties_shuffled = 0
    total_states_shuffledFrom = []
    total_states_shuffledTo = []
    shuffledCounties = []
    total_votes_shuffled = 0.
    #Shuffle votes from one state to another
    for stateTo,shufList in shuffleDict.iteritems():
        stateToIdx   = stateData1[stateData1['state_abbr'] == stateTo].index.tolist()
        if stateTo not in total_states_shuffledTo: total_states_shuffledTo.append(stateTo)
        for county in shufList:
            stateFrom = county[0:2]
            if stateFrom not in total_states_shuffledFrom: total_states_shuffledFrom.append(stateFrom)
            stateFromIdx = stateData1[stateData1['state_abbr'] == stateFrom].index.tolist()
            FIPS = combName2GEOID[county]
            countyIdx = dfCounties[dfCounties['GEOID'] == FIPS].index.tolist()
            dem_votes = dfCounties.iloc[countyIdx, dfCounties.columns.get_loc("dem_votes")] 
            rep_votes = dfCounties.iloc[countyIdx, dfCounties.columns.get_loc("rep_votes")] 
            ind_votes = dfCounties.iloc[countyIdx, dfCounties.columns.get_loc("ind_votes")] 
            tot_votes = dfCounties.iloc[countyIdx, dfCounties.columns.get_loc("tot_votes")] 
            #take votes away from the from state total, and add them to the to state total
            stateData1.iloc[stateToIdx, stateData1.columns.get_loc("dem_votes")] += dem_votes.values
            stateData1.iloc[stateToIdx, stateData1.columns.get_loc("rep_votes")] += rep_votes.values
            stateData1.iloc[stateToIdx, stateData1.columns.get_loc("ind_votes")] += ind_votes.values
            stateData1.iloc[stateToIdx, stateData1.columns.get_loc("votes_total")] += tot_votes.values

            stateData1.iloc[stateFromIdx, stateData1.columns.get_loc("dem_votes")] -= dem_votes.values
            stateData1.iloc[stateFromIdx, stateData1.columns.get_loc("rep_votes")] -= rep_votes.values
            stateData1.iloc[stateFromIdx, stateData1.columns.get_loc("ind_votes")] -= ind_votes.values
            stateData1.iloc[stateFromIdx, stateData1.columns.get_loc("votes_total")] -= tot_votes.values

            total_counties_shuffled += 1
            total_votes_shuffled += tot_votes.values[0]
            county2state[FIPS] = stateTo
            dfCounties.iloc[countyIdx, dfCounties.columns.get_loc("STATEFP")] = stateData1.iloc[stateToIdx[0], stateData1.columns.get_loc("STATEFP")]
            shuffledCounties.append(FIPS)




    #recount state winners
    stateData1["isDemWinner"] = stateData1.apply(lambda row: row["dem_votes"] > row["rep_votes"],axis=1)
    demWinnersIdx = stateData1[stateData1['isDemWinner']].index.tolist()
    demWinners = stateData1.iloc[demWinnersIdx,stateData1.columns.get_loc('state_abbr')].values
    demEvotes = np.sum(stateData1.iloc[demWinnersIdx,stateData1.columns.get_loc('electoral_votes')].values)
    
    stateData1["isRepWinner"] = stateData1.apply(lambda row: row["rep_votes"] > row["dem_votes"],axis=1)
    repWinnersIdx = stateData1[stateData1['isRepWinner']].index.tolist()
    repWinners = stateData1.iloc[repWinnersIdx,stateData1.columns.get_loc('state_abbr')].values
    repEvotes  = np.sum(stateData1.iloc[repWinnersIdx,stateData1.columns.get_loc('electoral_votes')].values)
    
    #Get total number of electoral votes moved
    stateData1["demFlipped"] = stateData1.apply(lambda row: row["isDemWinner"] and row["isRepWinnerO"],axis=1)
    demFlippedIdx = stateData1[stateData1['demFlipped']].index.tolist()
    if len(demFlippedIdx) > 0:
        demFlipped = stateData1.iloc[demFlippedIdx,stateData1.columns.get_loc('state_abbr')].values
        demFlippedEvotes = np.sum(stateData1.iloc[demFlippedIdx,stateData1.columns.get_loc('electoral_votes')].values)
    else:
        demFlippedEvotes = 0

    stateData1["repFlipped"] = stateData1.apply(lambda row: row["isRepWinner"] and row["isDemWinnerO"],axis=1)
    repFlippedIdx = stateData1[stateData1['repFlipped']].index.tolist()
    if len(repFlippedIdx) > 0:
        repFlipped = stateData1.iloc[repFlippedIdx,stateData1.columns.get_loc('state_abbr')].values
        repFlippedEvotes = np.sum(stateData1.iloc[repFlippedIdx,stateData1.columns.get_loc('electoral_votes')].values)
    else:
        repFlippedEvotes = 0

    totFlipped = demFlippedEvotes+repFlippedEvotes
    #Compute efficiency gap and other stats
    popDiffFrac = 100.*total_votes_shuffled/np.sum(stateData.votes_total.values)
    elDiffFrac  = np.abs(306.-repEvotes)
    ratio = elDiffFrac/popDiffFrac
    demWasted,repWasted,EG,EGEV,demVotePct,demStatePct,demEvotePct = utl.getEfficiencyGap(stateData1)
    
    repWinners = []
    for index,row in dfCounties.iterrows():
        state = row.STATEFP
        stateIdx = stateData1[stateData1['STATEFP'] == state].index.tolist()
        isRepWinner = stateData1.iloc[stateIdx[0], stateData1.columns.get_loc("isRepWinner")]
        repWinners.append(isRepWinner)
    
    dfCounties["isRepWinner"] = gpd.GeoSeries(repWinners,index=dfCounties.index)

    if EG < 0.:
        party = "D"
    else:
        party = "R"
    EG = np.abs(EG)
    title = 'D:'+str(demEvotes)+" R:"+str(repEvotes)+"  votes moved:"+"%1.2f"%(popDiffFrac)+"% Eff. Gap:"+party+"%1.2f"%(EG)+"%"
    boolDict = {"conditions":{"isRepWinner":'r'},"default":'b'}
    #utl.plotGDF(os.path.join(figDir,name),dfCounties,"USALL",colorby="boolDict",boolDict=boolDict,title=title)

    demWastedStr  = "%2.2f" % (demWasted/1000000.)
    repWastedStr  = "%2.2f" % (repWasted/1000000.)
    effGapStr     = party+" %2.2f" % (EG) + "%"
    votesMovedStr = "%1.2f" %(total_votes_shuffled/1000000.)+ " (%1.2f" % (popDiffFrac) + "%)"
    votesFlippedStr = str(totFlipped)+ " (%1.2f" % (100.*totFlipped/538.) + "%)"
    return [prettyName,demWastedStr,repWastedStr,effGapStr,votesMovedStr,votesFlippedStr]
    #1}}}

#Original state winners
dfStates["isDemWinnerO"] = dfStates.apply(lambda row: row["dem_votes"] > row["rep_votes"],axis=1)
dfStates["isRepWinnerO"] = dfStates.apply(lambda row: row["rep_votes"] > row["dem_votes"],axis=1)

tabData = [["","Wasted Dem. Votes*","Wasted Rep. Votes*","Efficiency Gap","Votes Moved* (% of total)","Electoral Votes Flipped (% of total)"]]
demWastedStr  = "%2.2f" % (demWasted2016/1000000.)
repWastedStr  = "%2.2f" % (repWasted2016/1000000.)
effGapStr     = "R"+" %2.2f" % (EG2016) + "%"
votesMovedStr = "-"
votesFlippedStr = "-"
res = ["2016 Actual",demWastedStr,repWastedStr,effGapStr,votesMovedStr,votesFlippedStr]
tabData.append(res)
#close wins for trump were in FL, GA, NC, PA, MI, WI, AZ
#Flip florida and michigan
fl2al = ['FLescambia','FLokaloosa','FLsantarosa']
mi2oh = ['MImonroe']
shuffleDict = {"AL":fl2al,"OH":mi2oh}
res = shuffle_and_plot(dfStates,shuffleDict,"shuffle_FLMI.png","FL, MI")
tabData.append(res)

il2wi = ['ILlake']
nj2pa = ['NJcamden']
shuffleDict = {"PA":nj2pa,"OH":mi2oh,"WI":il2wi}
res = shuffle_and_plot(dfStates,shuffleDict,"shuffle_MIWIPA.png","MI, PA, WI")
tabData.append(res)

#close wins for clinton were in NV, CO, MN, NH, ME, VA

#Flip Nevada, new hampshire and Virginia for Trump
nv2ca = ['NVclark']
nh2ma = ['NHcheshire']
va2md = ['VAfairfax']
shuffleDict = {"CA":nv2ca,"MA":nh2ma,"MD":va2md}
res = shuffle_and_plot(dfStates,shuffleDict,"shuffle_NVNHVA.png","NV, NH, VA")
tabData.append(res)

#Combine all scenarios
shuffleDict = {"CA":nv2ca,"MA":nh2ma,"MD":va2md,"AL":fl2al,"OH":mi2oh,"PA":nj2pa,"WI":il2wi}
res = shuffle_and_plot(dfStates,shuffleDict,"shuffle_ALL.png","All")
tabData.append(res)

utl.html_table(tabData,os.path.join(figDir,"scenarios.html"))

