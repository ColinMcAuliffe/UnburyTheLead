from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import urllib

# list of state abbreviations
states = ['AL','AK','AZ','AR','CA','CO','CT','DC','DE','FL','GA','HI','ID','IL','IN','IA','KS','KY','LA','ME','MD','MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ','NM','NY','NC','ND','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VT','VA','WA','WV','WI','WY']

#The page for each state on townhall has a statewide summary, but we don't want to read that, this function will let us skip over the summary and just read the county results
def cond(x):
    if x:
        return x.startswith("table ec-table") and not "table ec-table ec-table-summary" in x
    else:
        return False

#Since we need to match data from the census and from townhall.com using county names, let's process the names in each data set to make them easier to match
def preprocess_countyName(name,state):
    #Lower case
    name = name.lower()
    #Remove various words that might be in one data set but not the other
    rmList = ["st.","ste.","sainte","county","parish","co."]
    name = name.split()
    name = [x for x in name if x not in rmList]
    #remove spaces
    name = "".join(name)
    #Special cases: shannon county SD is now called Oglala Lakota
    if name == "shannon" and state == "SD":
        name = "oglalalakota"
    return name

def party2colname(party):
    if party.lower() == "gop":
        return "rep_votes"
    elif party.lower() == "dem":
        return "dem_votes"
    else:
        return "ind_votes"

#Get census data. We need this because the townhall data does not have the FIPS codes for each county, and we need those to plots on maps
#read county_fips data from https://www.census.gov/geo/reference/codes/cou.html, into a pandas data frame
print "Fetching and prepping census data"
df = pd.read_csv('http://www2.census.gov/geo/docs/reference/codes/files/national_county.txt',sep=',',header=None, dtype=object)
df.columns = ['state_abbr', 'STATEFP', 'COUNTYFP', 'county_name', 'fips_class_code']

#These are the data we will taking from town hall or adding. We have the votes for democrat, republican, and independent candidates as well as the total votes cast in each county. Additionally, we have a combined fips code, which is the concatenated state and county fips code converted to an integer
nrow = df.shape[0]
df['dem_votes'] = pd.Series(np.zeros(nrow), index=df.index)
df['rep_votes'] = pd.Series(np.zeros(nrow), index=df.index)
df['ind_votes'] = pd.Series(np.zeros(nrow), index=df.index)
df['tot_votes'] = pd.Series(np.zeros(nrow), index=df.index)

#prepare census data to be matched with townhall data
for state in states:
    stateMatches = df[df['state_abbr'] == state].index.tolist()
    for countyIdx in stateMatches:
        #Apply various operations on the county name to make it easier to match with townhall
        df.iloc[countyIdx, df.columns.get_loc("county_name")]      = preprocess_countyName(df.iloc[countyIdx, df.columns.get_loc("county_name")],state)
        #Shannon county SD is now called Oglala Lakota, and has a different county FIPS code than what's in the census data
        if df.iloc[countyIdx, df.columns.get_loc("county_name")] == "oglalalakota":
            df.iloc[countyIdx, df.columns.get_loc("COUNTYFP")] = "102"
        #Some cities are treated as counties, especially in virginia. Such cities have a fips class code of C7. Here we make sure the 'city' is appended to the end of the name so that we can distinguish between the city of Fairfax and Fairfax county for example.
        if df.iloc[countyIdx, df.columns.get_loc("fips_class_code")] == "C7":
            if "city" not in df.iloc[countyIdx, df.columns.get_loc("county_name")]: df.iloc[countyIdx, df.columns.get_loc("county_name")]+="city"

#set the GEOID, which is just the concatenated state and county FIPS codes
df['GEOID'] = df.apply(lambda row: row["STATEFP"]+row["COUNTYFP"], axis=1)


#scrape townhall election data and add it to a data frame
#Data from alaska is not reported by county. We'll just take the statewide data and divide it evenly amonst AK's counties
ak_counties = df[(df['state_abbr'] == 'AK')].shape[0]  
# loop through each state's web page http://townhall.com/election/2016/president/%s/county, where %s is the state abbr\n",
for state in states:
    print "getting county level data for "+state
    #find all of the indices of the counties in the current state
    stateMatches = df[df['state_abbr'] == state].index.tolist()

    #Read the html file from townhall.com for the current state, we will use Beautiful soup to help pull the info we want
    html  = urllib.urlopen('http://townhall.com/election/2016/president/' + state + '/county').read()
    bsObj = BeautifulSoup(html,"lxml")
    #Each page on townhall.com has a number of tables in it. This will find them all so that we can loop through each one
    tables = bsObj.findAll('table', attrs={'class':cond})
    for table in tables:
        #This will keep us from trying to extract data from a hierarchical table
        if table.findParent("table") is None:
            table_body = table.find('tbody')

            #The table for each county has a row for each candidate, with the winning candidate on top
            #The county name is in the first column of the first row
            rows = table_body.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                # the first row has 4 columns
                if len(cols) == 4:
                    # get the text of the county name
                    divs = cols[0].find_all('div')
                    county = divs[0].text.strip()

                    #Find all the indices of counties which match the name of the current county
                    countyMatches = df[df['county_name'] == preprocess_countyName(county,state)].index.tolist()
                    #There are multiple counties with the same name in different states, so make sure we get the right one
                    bothMatches   = list(set(stateMatches) & set(countyMatches))
                    #This handles some exceptions in case their are multiple counties that match the state and county name
                    if len(bothMatches) != 1: 
                        if state in ["AK","DC"]:
                            bothMatches = list(stateMatches)
                        if state == "VA":
                            countyMatches = df[df['county_name'] == preprocess_countyName(county+"city",state)].index.tolist()
                            bothMatches   = list(set(stateMatches) & set(countyMatches))
                    #Get the votes, remove commas. Zero votes is represented as a -, so replace that with a 0
                    total_votes = int(cols[2].text.strip().replace(',','').replace('-','0'))
                    #Get party name, and determine which column in the data frame to add the votes to
                    party = cols[1]['class'][0]
                    colName = party2colname(party)

                    #For alaska divide the state votes evenly amonst the counties
                    if state == "AK":
                        total_votes = total_votes/ak_counties

                    #add the votes to the data frame
                    df.iloc[bothMatches, df.columns.get_loc(colName)]      = total_votes
                    df.iloc[bothMatches, df.columns.get_loc('tot_votes')] += total_votes
                # all other tbody tr have three td
                else:
                    party = cols[1]['class'][0]
                    total_votes = int(cols[1].text.strip().replace(',','').replace('-','0'))
                    if state == "AK":
                        total_votes = total_votes/ak_counties
                    colName = party2colname(party)
                    df.iloc[bothMatches, df.columns.get_loc(colName)]      = total_votes
                    df.iloc[bothMatches, df.columns.get_loc('tot_votes')] += total_votes
                    

#This filters out counties in the census data which had no votes. This includes counties in US territories
df = df[df.tot_votes != 0]
#Save the result, so we can use it later
print "saving the results"
df.to_csv("2016_pres_votes_by_county.csv")
print "Done!"
