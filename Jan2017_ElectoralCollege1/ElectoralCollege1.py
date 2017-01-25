from matplotlib.patches import Polygon
from matplotlib.colors import rgb2hex
from collections import defaultdict

import matplotlib.pyplot as plt
import utlUtilities as utl
import geopandas as gpd
import pandas as pd
import numpy as np
import pyproj
import sys
import os

# list of state abbreviations
states = ['AL','AK','AZ','AR','CA','CO','CT','DC','DE','FL','GA','HI','ID','IL','IN','IA','KS','KY','LA','ME','MD','MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ','NM','NY','NC','ND','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VT','VA','WA','WV','WI','WY']

figDir       = "Figures"

#Note, the state and county shape files must be downloaded from the census website and unzipped in the location as indicated below
shapeFileStates   = "../CommonData/ShapeFiles/cb_2015_us_state_500k/cb_2015_us_state_500k.shp"
shapeFileCounties = "../CommonData/ShapeFiles/cb_2015_us_county_500k/cb_2015_us_county_500k.shp"
countyData        = "../CommonData/Presidential_Election_2016_Results/2016_pres_votes_by_county.csv"
stateData         = "../CommonData/Presidential_Election_2016_Results/2016_pres_votes_by_state.csv"

dfStates = utl.mergeGDF(shapeFileStates,stateData,"STATEFP")
dfCounties = utl.mergeGDF(shapeFileCounties,countyData,"GEOID")


dfCounties = dfCounties.sort_values(by=["tot_votes"],ascending=False)
dfCounties.index = range(len(dfCounties))
vote_pct = dfCounties.tot_votes.values/np.sum(dfCounties.tot_votes.values)
cumulative_vote  = np.cumsum(vote_pct)
ncounties = float(np.shape(cumulative_vote)[0])
popular_majority = np.min(np.where(cumulative_vote > 0.5))
popular_80Pct    = np.min(np.where(cumulative_vote > 0.8))
pop_counties = list(dfCounties.index)[0:popular_majority]
pop_counties = range(popular_majority)
pop_countiesTot = np.sum(dfCounties.tot_votes.values[pop_counties])
pop_countiesDem = np.sum(dfCounties.dem_votes.values[pop_counties])
pop_countiesRep = np.sum(dfCounties.rep_votes.values[pop_counties])
print "Clinton votes in top counties ",pop_countiesDem,pop_countiesDem/pop_countiesTot
print "Trump votes in top counties ",pop_countiesRep,pop_countiesRep/pop_countiesTot
dfCounties["InNatMaj"] = dfCounties.tot_votes.apply(lambda x: x >= dfCounties.tot_votes.values[popular_majority])

#Plot distribution of votes by county
print "plotting vote distribution by county"
fig = plt.figure()
ax = fig.add_subplot(111)
ax.semilogy(dfCounties.tot_votes.values,color='k')
one1 = np.ones(ncounties)
x = np.arange(ncounties) + 1.
ax.fill_between(x[0:popular_majority+1], one1[0:popular_majority+1], dfCounties.tot_votes.values[0:popular_majority+1], facecolor='green', interpolate=True)
ax.fill_between(x[popular_majority:popular_80Pct+1], one1[popular_majority:popular_80Pct+1], dfCounties.tot_votes.values[popular_majority:popular_80Pct+1], facecolor='cyan', interpolate=True)
ax.grid()
ax.set_xlabel("County Rank by Number of Presidential Votes in 2016")
ax.set_ylabel("Number of Votes")
fig.savefig(os.path.join(figDir,"pop.png"))
plt.close()


#Reweight vote count where state votes are weighted by their proportion of electoral votes to popular votes
#Total votes nationally by party
demVotes = np.sum(dfStates.dem_votes.values)
repVotes = np.sum(dfStates.rep_votes.values)
indVotes = np.sum(dfStates.ind_votes.values)
totVotes = demVotes+repVotes+indVotes
#Fraction of votes nationally by party
demFrac  = demVotes/totVotes
repFrac  = repVotes/totVotes
indFrac  = indVotes/totVotes
#Multiply votes by state weight
wDemVotes = np.sum(dfStates.el_votes_per_pop_vote.values*dfStates.dem_votes.values)
wRepVotes = np.sum(dfStates.el_votes_per_pop_vote.values*dfStates.rep_votes.values)
wIndVotes = np.sum(dfStates.el_votes_per_pop_vote.values*dfStates.ind_votes.values)
wTotVotes = wDemVotes+wRepVotes+wIndVotes
#Fraction of weighted votes
wDemFrac  = wDemVotes/wTotVotes
wRepFrac  = wRepVotes/wTotVotes
wIndFrac  = wIndVotes/wTotVotes
#Compute weigted votes so that the total votes are preserved
wDemVotes = wDemFrac*totVotes
wRepVotes = wRepFrac*totVotes
wIndVotes = wIndFrac*totVotes

#Make a table of the weighted votes
tableData = [[" ","Republican","Democrat","Independent","Total"]]

tableData.append(["Votes (millions)"]+["%10.2f" %(x/1000000.) for x in [repVotes,demVotes,indVotes,totVotes]])
tableData.append(["Percentage"]+["%10.2f" %(x*100.)+"%" for x in [repFrac,demFrac,indFrac]]+["-"])
tableData.append(["Weighted Votes (millions)"]+["%10.2f" %(x/1000000.) for x in [wRepVotes,wDemVotes,wIndVotes]]+["-"])
tableData.append(["Percentage of weighted votes"]+["%10.2f" %(x*100.)+"%" for x in [wRepFrac,wDemFrac,wIndFrac]]+["-"])
tableData.append(["Vote Difference (millions)"]+["%10.2f" %(x/1000000.) for x in [wRepVotes-repVotes,wDemVotes-demVotes,wIndVotes-indVotes]]+["-"])
tableData.append(["Percentage Difference"]+["%10.2f" %(x*100.)+"%" for x in [wRepFrac-repFrac,wDemFrac-demFrac,wIndFrac-indFrac]]+["-"])
utl.html_table(tableData,os.path.join(figDir,"WeightedVotes.html"))

#Tabulate some stats for close races with large proportions of votes in population centers 
stateList = ["MI","FL","PA","WI"]
tabdata   = [["State","Rep. Statewide Margin","Rep. Votes*","Dem. Votes*","Ind. Votes*","Margin as % of all votes*"]]
for state in stateList:
    idx  = dfStates.loc[dfStates['state_abbr'] == state].index.tolist()
    marg = dfStates.rep_margin.values[idx[0]]
    dem  = dfStates.dem_votesInTop5.values[idx[0]]
    rep  = dfStates.rep_votesInTop5.values[idx[0]]
    ind  = dfStates.ind_votesInTop5.values[idx[0]]
    tabdata.append([state]+[str(int(x)) for x in [marg,rep,dem,ind]]+["%10.2f"%(100.*marg/(rep+dem+ind))+"%"])

tabdata.append(["* these totals are only for counties which are in the top 5% of counties which account for a nationwide majority of votes"])
utl.html_table(tabdata,os.path.join(figDir,"Swing.html"))

#Tabulate lost votes
tableData = [[" ","Republican","Democrat","Independent","Total"]]
repVotes = np.sum(dfStates.rep_votes)
demVotes = np.sum(dfStates.dem_votes)
indVotes = np.sum(dfStates.ind_votes)
totVotes = repVotes+demVotes+indVotes
repLost = np.sum(dfStates.rep_lost)
demLost = np.sum(dfStates.dem_lost)
indLost = np.sum(dfStates.ind_lost)
totLost = repLost+demLost+indLost
repLostFrac = repLost/np.sum(dfStates.rep_votes)
demLostFrac = demLost/np.sum(dfStates.dem_votes)
indLostFrac = indLost/np.sum(dfStates.ind_votes)
totLostFrac = totLost/np.sum(dfStates.votes_total.values)
tableData.append(["Votes (millions)"]+["%10.2f" %(x/1000000.) for x in [repVotes,demVotes,indVotes,totVotes]])
tableData.append(["Lost Votes (millions)"]+["%10.2f" %(x/1000000.) for x in [repLost,demLost,indLost,totLost]])
tableData.append(["Percentage Lost"]+["%10.2f" %(x*100.)+"%" for x in [repLostFrac,demLostFrac,indLostFrac,totLostFrac]])
utl.html_table(tableData,os.path.join(figDir,"LostVotes.html"))

print "plotting popular vote winner with top counties"
boolDict = {"conditions":{"InNatMaj":'b'},"default":'r'}
utl.plotGDF(os.path.join(figDir,"pop_votesByCounty.png"),dfCounties,"USALL",colorby='boolDict',boolDict=boolDict,title="Top 5% of Counties Forming a National Majority")

print "plotting electoral map for extreme win candidate"
boolDict = {"conditions":{"allStateMajInNatMaj":'b'},"default":'r'}
utl.plotGDF(os.path.join(figDir,"electoralMapExtreme.png"),dfStates,"USALL",colorby="boolDict",boolDict=boolDict,title="Electoral Map for Extreme Candidate")

print "plotting total votes by state"
utl.plotGDF(os.path.join(figDir,"pop_votesByState.png"),dfStates,"USALL",colorby="data",colorCol="votes_total",cmap=plt.cm.Greens,cmapScale=1.e-6,title="Votes by State (millions)")

print "plotting win margin by state"
utl.plotGDF(os.path.join(figDir,"win_marginByState.png"),dfStates,"USALL",colorby="data",colorCol="win_margin",cmap=plt.cm.Greens,title="Win Margin by State (%)",climits=(0.,.1),cmapScale=100.)

print "plotting win margin by state"
utl.plotGDF(os.path.join(figDir,"electoralPerPopByState.png"),dfStates,"USALL",colorby="data",colorCol="el_votes_per_pop_vote",cmap=plt.cm.Greens,title="Electoral Votes per 100,000 Popular Votes",cmapScale=100000.)

print "plotting lost votes by state"
utl.plotGDF(os.path.join(figDir,"lostVotesByState.png"),dfStates,"USALL",colorby="data",colorCol="lost_votes",cmap=plt.cm.Greens,title="Lost Votes by State (Millions)",cmapScale=1.e-6)

print "plotting events by state"
utl.plotGDF(os.path.join(figDir,"lostVotesByState.png"),dfStates,"USALL",colorby="data",colorCol="lost_votes",cmap=plt.cm.Greens,title="Lost Votes by State (Millions)",cmapScale=1.e-6)


#Plot state events{{{1
print "plotting state events"
#data from fairvote
clintonEvents = {
        "Colorado":3,
        "Florida":36,
        "Iowa":7,
        "Michigan":8,
        "New Hampshire":6,
        "Nevada":8,
        "North Carolina":24,
        "Ohio":18,
        "Pennsylvania":26,
        "Virginia":5,
        "Wisconsin":5,
        "Arizona":3,
        "Illinois":1,
        "Nebraska":1
        }

trumpEvents = {
        "Colorado":16,
        "Florida":35,
        "Iowa":14,
        "Michigan":14,
        "New Hampshire":15,
        "Nevada":9,
        "North Carolina":31,
        "Ohio":30,
        "Pennsylvania":28,
        "Virginia":18,
        "Wisconsin":9,
        "Arizona":7,
        "California":1,
        "Connecticut":1,
        "Georgia":3,
        "Indiana":2,
        "Maine":3,
        "Minnesota":2,
        "Mississippi":1,
        "Missouri":2,
        "Nebraska":1,
        "New Mexico":3,
        "Texas":1,
        "Utah":1,
        "Washington":1
        }

totEvents = 399.
combEvents = defaultdict(float)
for key,value in clintonEvents.iteritems():
    combEvents[key] += 100.*float(value)/totEvents
for key,value in trumpEvents.iteritems():
    combEvents[key] += 100.*float(value)/totEvents

import us
def getEvents(row):
    state = getattr(us.states,row['state_abbr'])
    try:
        events = combEvents[state.name]
    except:
        events = 0.
    return events

dfStates["Events"] = dfStates.apply(getEvents, axis=1)
utl.plotGDF(os.path.join(figDir,"campaignEvents.png"),dfStates,"USALL",colorby="data",colorCol="Events",cmap=plt.cm.Greens,title="Percentage of Total Campaign Events Held in Each State")
#1}}}

#Flag lost counties
demWinners = []
repWinners = []
for idx,row in dfStates.iterrows():
    if row["dem_votes"] > row["rep_votes"]:
        demWinners.append(row["STATEFP"])
    else:
        repWinners.append(row["STATEFP"])

def flagDemLost(row):
    if row["STATEFP"] in repWinners and row["dem_votes"] > row["rep_votes"]:
        return True
    else:
        return False

def flagRepLost(row):
    if row["STATEFP"] in demWinners and row["rep_votes"] > row["dem_votes"]:
        return True
    else:
        return False


dfCounties["isDemLost"] = dfCounties.apply(flagDemLost,axis=1)
dfCounties["isRepLost"] = dfCounties.apply(flagRepLost,axis=1)
print "plotting lost counties"
boolDict = {"conditions":{"isDemLost":'b',"isRepLost":"r"},"default":'w'}
utl.plotGDF(os.path.join(figDir,"lostCounties.png"),dfCounties,"USALL",colorby="boolDict",boolDict=boolDict,title="Lost Counties")
#Thumbnail
utl.plotGDF(os.path.join(figDir,"thumb.png"),dfCounties,"USALL",colorby="boolDict",boolDict=boolDict)

