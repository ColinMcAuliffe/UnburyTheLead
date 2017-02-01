import pandas as pd
import numpy as np
import us

abbr2fips = us.states.mapping('abbr','fips')
# list of state abbreviations
states = ['AL','AK','AZ','AR','CA','CO','CT','DC','DE','FL','GA','HI','ID','IL','IN','IA','KS','KY','LA','ME','MD','MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ','NM','NY','NC','ND','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VT','VA','WA','WV','WI','WY']

#load data, sort counties by number of votes
df = pd.read_csv("2016_pres_votes_by_county.csv")
df = df.sort_values(by=["tot_votes"],ascending=False)
df.index = range(len(df)) #reset index to 0 based

#Compute fraction nationwide votes per county, compute the cumulative vote fraction starting with the largest county and moving in order
vote_pct = df.tot_votes.values/np.sum(df.tot_votes.values)
cumulative_vote  = np.cumsum(vote_pct)
#We can find where the cumulative vote passes 50% and 80% to determine the number of counties controlling this vote share
popular_majority = np.min(np.where(cumulative_vote > 0.5))
popular_80Pct    = np.min(np.where(cumulative_vote > 0.8))
natMajCounties   = range(popular_majority)

ncounties = float(np.shape(cumulative_vote)[0])
pct50_counties = 100.*float(popular_majority)/ncounties
pct50_votes    = 100.*cumulative_vote[popular_majority]
pct80_counties = 100.*float(popular_80Pct)/ncounties
pct80_votes    = 100.*cumulative_vote[popular_80Pct]
print "%10.2f percent of votes are from %10.2f percent of counties" %(pct50_votes,pct50_counties)
print "%10.2f percent of votes are from %10.2f percent of counties" %(pct80_votes,pct80_counties)

df_electors = pd.read_csv("electors.csv")

# headers for csv export
data = [['state_abbr','STATEFP', 'electoral_votes','dem_votes','rep_votes','ind_votes','votes_total','flipped_by_ind','el_votes_per_pop_vote','min_counties_for_state_win','rep_margin','rep_margin_as_frac_of_min_county_votes','el_vote_per_county_frac','el_vote_per_county_frac_per_diff','el_vote_per_county_frac_per_frac','lost_votes','dem_lost','rep_lost','ind_lost','win_margin','allStateMajInNatMaj','dem_votesInTop5','rep_votesInTop5','ind_votesInTop5']]

state_countyIdx = {}
demWinners = []
repWinners = []
for state in states:
    #get number of electors for state
    stateMatches_forEvotes = df_electors[df_electors['State'] == state].index.tolist()
    electors = df_electors.iloc[stateMatches_forEvotes[0], df_electors.columns.get_loc('Electors')]
    FIPS = abbr2fips[state]

    #Find all counties in the state
    stateMatches = df[df['state_abbr'] == state].index.tolist()
    nscounties = float(len(stateMatches))

    #Get vote counts for the whole state
    dem_votes = np.sum(df.dem_votes.values[stateMatches])
    rep_votes = np.sum(df.rep_votes.values[stateMatches])
    ind_votes = np.sum(df.ind_votes.values[stateMatches])
    tot_votes = np.sum(df.tot_votes.values[stateMatches])
    rep_margin = rep_votes - dem_votes

    #ratio of electoral votes to total votes
    electoralPerPopular = electors/tot_votes

    #Determine who won the state, compute win margin and lost votes, or votes that were not cast for the state wide winner
    flipped_by_ind = "No"
    if dem_votes > rep_votes:
        demWinners.append(state)
        lost_votes = rep_votes+ind_votes
        demLost    = 0
        repLost    = rep_votes
        indLost    = ind_votes
        win_gap    = dem_votes-rep_votes
        win_margin = win_gap/tot_votes
        if ind_votes > win_gap:
            flipped_by_ind = "To Trump"
    else:
        repWinners.append(state)
        lost_votes = dem_votes+ind_votes
        demLost    = dem_votes
        repLost    = 0
        indLost    = ind_votes
        win_gap    = rep_votes-dem_votes
        win_margin = win_gap/tot_votes
        if ind_votes > win_gap:
            flipped_by_ind = "To Clinton"
    
    #Counties are already sorted by the number of votes, so we can use the same technique to find the number of counties controlling 50% of the vote in a state that we used to compute the counties controlling a nationwide majority
    vote_pct           = df.tot_votes.values[stateMatches]/tot_votes
    cumulative_vote    = np.cumsum(vote_pct)
    stateMajCounty     = np.min(np.where(cumulative_vote > 0.5))
    stateMajorityVotes = cumulative_vote[stateMajCounty]*tot_votes

    countiesInTop5 = [i for i in stateMatches if i in natMajCounties]
    dem_votesInTop5 = np.sum(df.dem_votes.values[countiesInTop5])
    rep_votesInTop5 = np.sum(df.rep_votes.values[countiesInTop5])
    ind_votesInTop5 = np.sum(df.ind_votes.values[countiesInTop5])
    
    
    #See if there are any counties required for the state majority that are not in the counties required for the national majority
    #Note the variable popularMajority contains the rank of the smallest state in the national majority majority, while stateMatches[stateMajCounties] contains the rank of the smallest county in the state majority counties
    allStateMajInNatMaj = stateMatches[stateMajCounty] <= popular_majority
    

    #Compute various quantities that will help navigate the results
    #Fraction of counties with 50% of the vote in a state
    min_counties_for_win    = float(stateMajCounty+1)/nscounties
    #State wide republican win margin as a fraction of the vote count in state's most populous counties. This number is negative if democrats won the state
    rep_margin_asFrac       = rep_margin/stateMajorityVotes
    #Proportion of electors to the fraction of counties needed for a statewide majority. A higher number tells us that a state has a relatively large number of electors which can be won with a small fraction of counties
    el_vote_per_county_frac = electors/min_counties_for_win
    #Elector to county fraction ratio divided by the republican win margin. This will help us find swing states that could have been easily tipped by votes in their populous counties and have a large effect on the electoral result
    el_vote_per_county_frac_per_diff = electors/(min_counties_for_win*rep_margin)
    el_vote_per_county_frac_per_frac = electors/(min_counties_for_win*rep_margin_asFrac)

    #Add data to a list
    data.append([state,FIPS, electors, dem_votes,rep_votes,ind_votes,tot_votes,flipped_by_ind,electoralPerPopular,min_counties_for_win,rep_margin,rep_margin_asFrac,el_vote_per_county_frac,el_vote_per_county_frac_per_diff,el_vote_per_county_frac_per_frac,lost_votes,demLost,repLost,indLost,win_margin,allStateMajInNatMaj,rep_votesInTop5,dem_votesInTop5,ind_votesInTop5])
    
#Convert list to a data frame, create header, and save the result for later
stateData = pd.DataFrame(data)
new_header = stateData.iloc[0] #grab the first row for the header
stateData = stateData[1:] #take the data less the header row
stateData.columns = new_header #set the header row as the df header
stateData.index = range(len(stateData))
stateData.to_csv("2016_pres_votes_by_state.csv")
