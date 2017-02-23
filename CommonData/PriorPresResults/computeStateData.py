import pandas as pd
import numpy as np
import us

abbr2fips = us.states.mapping('abbr','fips')
fips2abbr = us.states.mapping('fips','abbr')
states = us.states.STATES
#load data, sort counties by number of votes
df = pd.read_csv("US_County_Level_Presidential_Results_08-16.csv",dtype={"fips_code": object})
df.index = range(len(df)) #reset index to 0 based
df["STATEFP"] = df.fips_code.apply(lambda x: x[0:2])

df_electors = pd.read_csv("electors.csv")

# headers for csv export
data08 = [['state_abbr','STATEFP','electoral_votes','dem_votes','rep_votes','ind_votes','votes_total']]
data12 = [['state_abbr','STATEFP','electoral_votes','dem_votes','rep_votes','ind_votes','votes_total']]
data16 = [['state_abbr','STATEFP','electoral_votes','dem_votes','rep_votes','ind_votes','votes_total']]
for state in states:
    print state.fips,state.abbr
    fips = state.fips
    abbr = state.abbr
    stateMatches_forEvotes = df_electors[df_electors['State'] == abbr].index.tolist()
    electors = df_electors.iloc[stateMatches_forEvotes[0], df_electors.columns.get_loc('Electors')]
    

    if fips == "02":
        #Alaska county level data not available, state level data from david liep's atlas
        dem_votes08 = 123594
        rep_votes08 = 193841
        ind_votes08 = 3783+1730+1660+1589
        tot_votes08 = dem_votes08+rep_votes08+ind_votes08

        dem_votes12 = 122640
        rep_votes12 = 164676
        ind_votes12 = 7392+2917+2870
        tot_votes12 = dem_votes12+rep_votes12+ind_votes12

        dem_votes16 = 116454
        rep_votes16 = 163387
        ind_votes16 = 18725+9201+5735+3866+1240
        tot_votes16 = dem_votes16+rep_votes16+ind_votes16
    else:
        #Find all counties in the state
        stateMatches = df[df['STATEFP'] == fips].index.tolist()

        #Get vote counts for the whole state
        dem_votes08 = np.sum(df.dem_2008.values[stateMatches])
        rep_votes08 = np.sum(df.gop_2008.values[stateMatches])
        ind_votes08 = np.sum(df.oth_2008.values[stateMatches])
        tot_votes08 = np.sum(df.total_2008.values[stateMatches])

        dem_votes12 = np.sum(df.dem_2012.values[stateMatches])
        rep_votes12 = np.sum(df.gop_2012.values[stateMatches])
        ind_votes12 = np.sum(df.oth_2012.values[stateMatches])
        tot_votes12 = np.sum(df.total_2012.values[stateMatches])

        dem_votes16 = np.sum(df.dem_2016.values[stateMatches])
        rep_votes16 = np.sum(df.gop_2016.values[stateMatches])
        ind_votes16 = np.sum(df.oth_2016.values[stateMatches])
        tot_votes16 = np.sum(df.total_2016.values[stateMatches])

    ##Add data to a list
    data08.append([abbr,fips,electors,dem_votes08,rep_votes08,ind_votes08,tot_votes08])
    data12.append([abbr,fips,electors,dem_votes12,rep_votes12,ind_votes12,tot_votes12])
    data16.append([abbr,fips,electors,dem_votes16,rep_votes16,ind_votes16,tot_votes16])
    
#Convert list to a data frame, create header, and save the result for later
stateData = pd.DataFrame(data08)
new_header = stateData.iloc[0] #grab the first row for the header
stateData = stateData[1:] #take the data less the header row
stateData.columns = new_header #set the header row as the df header
stateData.index = range(len(stateData))
stateData.to_csv("2008_pres_votes_by_state.csv")

stateData = pd.DataFrame(data12)
new_header = stateData.iloc[0] #grab the first row for the header
stateData = stateData[1:] #take the data less the header row
stateData.columns = new_header #set the header row as the df header
stateData.index = range(len(stateData))
stateData.to_csv("2012_pres_votes_by_state.csv")

stateData = pd.DataFrame(data16)
new_header = stateData.iloc[0] #grab the first row for the header
stateData = stateData[1:] #take the data less the header row
stateData.columns = new_header #set the header row as the df header
stateData.index = range(len(stateData))
stateData.to_csv("2016_pres_votes_by_state.csv")
