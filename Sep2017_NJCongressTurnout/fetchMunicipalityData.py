import os
import numpy as np
import pandas as pd
import geopandas as gpd
from us import states
from census import Census
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(color_codes=True)

gdfCousub = gpd.read_file(os.path.join("..","Sep2017_NJTurnout","NJShapeFilewData","NJCousub.shp"))

df = pd.read_csv(os.path.join("ElectionResults","NJTurnout.csv"),index_col=0)
df["Municipality Name"] = df["Municipality Name"].str.lower()
df["Municipality Name"] = df["Municipality Name"].str.replace(" township"," twp")
df["Municipality Name"] = df["Municipality Name"].str.replace(" borough"," boro")
df["Municipality Name"] = df["Municipality Name"].str.replace(" city of"," city")
df["Municipality Name"] = df["Municipality Name"].str.replace(".","")
df["Municipality Name"] = df["Municipality Name"].str.replace(" ","")

df["County Name"] = df["County Name"].str.lower()
df["County Name"] = df["County Name"].str.replace(" ","")
df.ix[df["County Name"] == "capemay","County Name"]    = "cape may"
#Manually fix a few individual names
df.ix[df["Municipality Name"] == "estellemanor","Municipality Name"]         = "estellmanor"
df.ix[df["Municipality Name"] == "hillside","Municipality Name"]             = "hillsdale"
df.ix[df["Municipality Name"] == "woodridge","Municipality Name"]            = "wood-ridge"
df.ix[df["Municipality Name"] == "wycoff","Municipality Name"]               = "wyckoff"
df.ix[df["Municipality Name"] == "hainespirttwp","Municipality Name"]        = "hainesporttwp"
df.ix[df["Municipality Name"] == "easthamptontwp","Municipality Name"]       = "eastamptontwp"
df.ix[df["Municipality Name"] == "lindenwoldboro","Municipality Name"]       = "lindenwoodboro"
df.ix[df["Municipality Name"] == "mtephraimboro","Municipality Name"]        = "mountephraimboro"
df.ix[df["Municipality Name"] == "tavistokboro","Municipality Name"]         = "tavistockboro"
df.ix[df["Municipality Name"] == "wenoah","Municipality Name"]               = "wenonah"
df.ix[df["Municipality Name"] == "cityoftrenton","Municipality Name"]        = "trentoncity"
df.ix[df["Municipality Name"] == "ebrunswick","Municipality Name"]           = "eastbrunswick"
df.ix[df["Municipality Name"] == "avonboro","Municipality Name"]             = "avon-by-the-seaboro"
df.ix[df["Municipality Name"] == "neptunecityboro","Municipality Name"]      = "neptunecity"
df.ix[df["Municipality Name"] == "springlakehgtsboro","Municipality Name"]   = "springlakeheigtsboro"
df.ix[df["Municipality Name"] == "boontontownof","Municipality Name"]        = "boontontown"
df.ix[df["Municipality Name"] == "patterson","Municipality Name"]            = "patersoncity"
df.ix[df["Municipality Name"] == "salemeastward","Municipality Name"]        = "salem"
df.ix[df["Municipality Name"] == "salemwestward","Municipality Name"]        = "salem"
df.ix[df["Municipality Name"] == "springlakeheigtsboro","Municipality Name"] = "springlakeheightsboro"
df.ix[df["Municipality Name"] == "peapack-gladstone","Municipality Name"]    = "peapackandgladstone"
df.ix[(df["Municipality Name"] == "hillsdale")&(df["County Name"] == "union"),"Municipality Name"]            = "hillsidetwp"
df.ix[df["Municipality Name"] == "englewood","Municipality Name"]    = "englewoodcity"
df.ix[df["Municipality Name"] == "ridgefield","Municipality Name"]    = "ridgefieldboro"
df.ix[df["Municipality Name"] == "capemay","Municipality Name"]    = "capemaycity"
df.ix[df["Municipality Name"] == "wildwood","Municipality Name"]    = "wildwoodcity"
df.ix[df["Municipality Name"] == "woodbury","Municipality Name"]    = "woodburycity"
df.ix[df["Municipality Name"] == "clinton","Municipality Name"]    = "clintontown"
df.ix[df["Municipality Name"] == "bernards","Municipality Name"]    = "bernardstwp"
df.ix[df["Municipality Name"] == "roselle","Municipality Name"]    = "roselleboro"

df["CMname"] = df["County Name"] + df["Municipality Name"]
dfd = df.groupby('District',as_index=False).sum()
dfd["Margin"] = (dfd["Dem"].astype(np.float64)-dfd["Rep"].astype(np.float64))/dfd["Total"].astype(np.float64)
print dfd
df = df.groupby(["District",'CMname',"County Name"], as_index=False).sum()
df = pd.merge(df,dfd[["District","Margin"]],on="District")
df["District"] = df["District"].str.replace("district","")
df["District"] = df["District"].astype(np.int64)
print df
df["isDup"] = df["CMname"].apply(lambda name: len(df[df["CMname"]==name]) > 1)
df2 = df[df["isDup"]].sort_values("CMname")
df2["wM"] = df2["Total"]*df2["Margin"]
df2 = df2.groupby("CMname",as_index=False).sum()
df2["Margin"] = df2["wM"]/df2["Total"].astype(np.float64)

def fixCMname(name):
    newName = gdfCousub[gdfCousub["CMname"].str.contains(name)].CMname.values
    if len(newName) > 1:
        print newName,name

    return newName[0]

df["CMname"] = df["CMname"].apply(fixCMname)

gdfCousub = gdfCousub.merge(df[["CMname","District","Margin","Dem","Rep","Ind","Total"]],on="CMname")
gdfCousub.to_file(filename= os.path.join("NJShapeFilewData","NJCousub.shp"))
