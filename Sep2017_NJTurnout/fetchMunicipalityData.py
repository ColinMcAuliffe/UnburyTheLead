import os
import numpy as np
import pandas as pd
import geopandas as gpd
from us import states
from census import Census
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(color_codes=True)

gdfCounty = gpd.read_file(os.path.join("..","CommonData","ShapeFiles","cb_2015_us_county_500k","cb_2015_us_county_500k.shp"))
gdfCounty = gdfCounty[gdfCounty["STATEFP"]=="34"]
gdfCounty = gdfCounty[["NAME","COUNTYFP"]]
gdfCounty["NAME"] = gdfCounty["NAME"].str.lower()
gdfCounty = gdfCounty.rename(columns={"NAME":"CountyName"})

gdfCousub = gpd.read_file(os.path.join("..","CommonData","ShapeFiles","tl_2016_34_cousub","tl_2016_34_cousub.shp"))
gdfCousub = gdfCousub[gdfCousub["NAME"] != "County subdivisions not defined"]
gdfCousub = gdfCousub.merge(gdfCounty,on="COUNTYFP")
gdfCousub.index = range(len(gdfCousub))

gdfCousub["NAMELSAD"] = gdfCousub["NAMELSAD"].str.lower()
gdfCousub["NAMELSAD"] = gdfCousub["NAMELSAD"].str.replace(" township"," twp")
gdfCousub["NAMELSAD"] = gdfCousub["NAMELSAD"].str.replace(" borough"," boro")
gdfCousub["NAMELSAD"] = gdfCousub["NAMELSAD"].str.replace(" city city"," city")
gdfCousub["NAMELSAD"] = gdfCousub["NAMELSAD"].str.replace("city of","")
gdfCousub["NAMELSAD"] = gdfCousub["NAMELSAD"].str.replace(" ","")
#Manually fix a few individual names
gdfCousub.ix[gdfCousub["NAMELSAD"] == "lindenwoldboro","NAMELSAD"] = "lindenwoodboro"
gdfCousub.ix[gdfCousub["NAMELSAD"] == "neptunecityboro","NAMELSAD"] = "neptunecity"

df = pd.read_csv(os.path.join("ElectionResults","NJTurnout.csv"),index_col=0)
df["Municipality Name"] = df["Municipality Name"].str.lower()
df["Municipality Name"] = df["Municipality Name"].str.replace(" township"," twp")
df["Municipality Name"] = df["Municipality Name"].str.replace(" borough"," boro")
df["Municipality Name"] = df["Municipality Name"].str.replace(" city of"," city")
df["Municipality Name"] = df["Municipality Name"].str.replace(".","")
df["Municipality Name"] = df["Municipality Name"].str.replace(" ","")

#Manually fix a few individual names
df.ix[df["County Name"] == "may","County Name"] = "cape may"
df.ix[df["Municipality Name"] == "cinnnaminsontwp","Municipality Name"] = "cinnaminsontwp"
df.ix[df["Municipality Name"] == "essexfellscity","Municipality Name"] = "essexfellsboro"
df.ix[df["Municipality Name"] == "hacketstowntown","Municipality Name"] = "hackettstowntown"
df.ix[df["Municipality Name"] == "hammonton","Municipality Name"] = "hammontontown"
df.ix[df["Municipality Name"] == "lakecomo","Municipality Name"] = "lakecomoboro"
df.ix[df["Municipality Name"] == "mountephriamboro","Municipality Name"] = "mountephraimboro"
df.ix[df["Municipality Name"] == "newbrunswicktwp","Municipality Name"] = "newbrunswickcity"
df.ix[df["Municipality Name"] == "northbergentown","Municipality Name"] = "northbergentwp"
df.ix[df["Municipality Name"] == "northfieldtwp","Municipality Name"] = "northfieldcity"
df.ix[df["Municipality Name"] == "orangecity","Municipality Name"] = "orangetwp"
df.ix[df["Municipality Name"] == "peapack&gladstoneboro","Municipality Name"] = "peapackandgladstoneboro"
df.ix[df["Municipality Name"] == "phillpsburgtown","Municipality Name"] = "phillipsburgtown"
df.ix[df["Municipality Name"] == "portrepublic","Municipality Name"] = "portrepubliccity"
df.ix[df["Municipality Name"] == "sayervilleboro","Municipality Name"] = "sayrevilleboro"
#Stafford in ocean county was misnamed stratford
df.ix[df["Municipality Name"] == "stratfordtwp","Municipality Name"] = "staffordtwp"
df.ix[df["Municipality Name"] == "travistockboro","Municipality Name"] = "tavistockboro"
df.ix[df["Municipality Name"] == "teterboro","Municipality Name"] = "teterboroboro"
df.ix[df["Municipality Name"] == "woodlandpark","Municipality Name"] = "woodlandparkboro"

df["CMname"] = df["County Name"] + df["Municipality Name"]
gdfCousub["CMname"] = gdfCousub["CountyName"] + gdfCousub["NAMELSAD"]

gdfCousub = gdfCousub.merge(df,on="CMname")
#To use this part get a api key from the census and put it in a file called census_key.txt
ckey = open('census_key.txt').readline().rstrip()
c  = Census(ckey, year=2010)

income     = c.acs5.state_county_subdivision('B19013_001E', states.NJ.fips, Census.ALL, Census.ALL)

incomeCou  = c.acs5.state_county('B19013_001E', states.NJ.fips, Census.ALL)
totalWorkers     = c.acs5.state_county_subdivision('B08006_001E', states.NJ.fips, Census.ALL, Census.ALL)
CTVWorkers     = c.acs5.state_county_subdivision('B08006_002E', states.NJ.fips, Census.ALL, Census.ALL)

def censusResponse2df(responseDicts,itemName,areaType,areaName,gdf):
    if areaType == "county subdivision":
        data = [[itemName,"GEOID"]]
    else:
        data = [[itemName,"COUNTYFP"]]
    for d in responseDicts:
        if areaType == "county subdivision":
            data.append([d[itemName],d['state']+d['county']+d['county subdivision']])
        else:
            data.append([d[itemName],d['county']])
    data = pd.DataFrame(data)
    new_header = data.iloc[0] #grab the first row for the header
    data = data[1:] #take the data less the header row
    data.columns = new_header #set the header row as the df header
    data.index = range(len(data))

    if areaType == "county subdivision":
        gdf = gdf.merge(data,on="GEOID")
    else:
        gdf = gdf.merge(data,on="COUNTYFP")
    return gdf
    
gdfCousub = censusResponse2df(incomeCou,'B19013_001E','county','GEOID',gdfCousub)
gdfCousub["B19013_001E"] = gdfCousub["B19013_001E"].fillna(0.)
gdfCousub = gdfCousub.rename(columns={"B19013_001E":"MHI_COU"})
print gdfCousub["MHI_COU"]

gdfCousub = censusResponse2df(income,'B19013_001E','county subdivision','GEOID',gdfCousub)
gdfCousub["B19013_001E"] = gdfCousub["B19013_001E"].fillna(0.)

gdfCousub = censusResponse2df(totalWorkers,'B08006_001E','county subdivision','GEOID',gdfCousub)
gdfCousub["B08006_001E"]       = gdfCousub["B08006_001E"].fillna(0.)

gdfCousub = censusResponse2df(CTVWorkers,'B08006_002E','county subdivision','GEOID',gdfCousub)
gdfCousub["B08006_002E"]     = gdfCousub["B08006_002E"].fillna(0.)

gdfCousub["CTVPct"] = gdfCousub["B08006_002E"].astype(np.float64)/gdfCousub["B08006_001E"].astype(np.float64)
print gdfCousub[["CTVPct","B19013_001E"]]

print gdfCousub.sort_values("B19013_001E")

gdfCousub.to_file(filename= os.path.join("NJShapeFilewData","NJCousub.shp"))


