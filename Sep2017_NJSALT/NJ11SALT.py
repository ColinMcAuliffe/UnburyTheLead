
import os
import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.ticker import FormatStrFormatter
from matplotlib.ticker import MaxNLocator
import utlUtilities as utl
import seaborn as sns
sns.set(color_codes=True)
from shapely.ops import cascaded_union

df = pd.read_csv("15zp31nj.csv",dtype={"Zip":object})
df = df[~df["Zip"].isnull()]
df = df[df["Categoty"].isnull()]
df = df[["Zip","(1)","(62)","(63)","(64)","(65)","(66)","(67)"]]
for col in df.columns:
    if col == "Zip": continue
    df[col] = df[col].str.replace(",","")
    df[col] = df[col].astype(np.float64)

totalSALT = df["(63)"].sum()/df["(62)"].sum() + df["(65)"].sum()/df["(64)"].sum() + df["(67)"].sum()/df["(66)"].sum()
totalSALT2 = (df["(63)"].sum() + df["(65)"].sum() + df["(67)"].sum())/df["(1)"].sum()
SLFrac = df["(62)"].sum()/df["(1)"].sum()
REFrac = df["(66)"].sum()/df["(1)"].sum()

#Municipality group to zip group mapping
muniGroup2Zips = {}
muniGroup2Zips["Bloomfield"]   = ["07003"]
muniGroup2Zips["Bloomingdale"] = ["07403"]
muniGroup2Zips["Boonton"]         = ["07005"] #town and twp
muniGroup2Zips["Butler+Kinnelon"]  = ["07405"]
muniGroup2Zips["Byram"]  = ["07821"] #also andover and green twp
muniGroup2Zips["Caldwells"]  = ["07006"]
muniGroup2Zips["Cedar Grove"] = ["07009"]
muniGroup2Zips["Chathams+Green Village"] = ["07928","07935"]
muniGroup2Zips["Denville"] = ["07834"]
muniGroup2Zips["East Hanover"] = ["07936"]
muniGroup2Zips["Essex Fells"] = ["07021"]
muniGroup2Zips["Fairfield"] = ["07004"]
muniGroup2Zips["Florham Park"] = ["07932"]
muniGroup2Zips["Hanover"] = ["07981","07927"] #whippany + cedar knolls
muniGroup2Zips["Harding"] = ["07976"] #new vernon
muniGroup2Zips["Hopatcong"] = ["07843"] 
muniGroup2Zips["Jefferson"] = ["07438","07435"] #oak ridge and newfoundland
muniGroup2Zips["Lincoln Park"] = ["07035"] 
muniGroup2Zips["Little Falls+Woodland Park"] = ["07424"] 
muniGroup2Zips["Livingston"] = ["07039"] 
muniGroup2Zips["Madison"] = ["07940"] 
muniGroup2Zips["Mendham"] = ["07945"] #town + twp
muniGroup2Zips["Upper Montclair"] = ["07043"]
muniGroup2Zips["Montville+Towaco"] = ["07045","07082"]
muniGroup2Zips["Morris Plains"] = ["07950"]
muniGroup2Zips["Morristown"] = ["07960"]
muniGroup2Zips["Mountain Lakes"] = ["07046"]
muniGroup2Zips["North Haledon"] = ["07508"]
muniGroup2Zips["Nutley"] = ["07110"]
muniGroup2Zips["Ogdensburg"] = ["07439"]
muniGroup2Zips["Parsippany"] = ["07054"]
muniGroup2Zips["Pequannock"] = ["07444"]
muniGroup2Zips["Pompton Lakes"] = ["07442"]
muniGroup2Zips["Randolph"] = ["07869"] #+dover
muniGroup2Zips["Riverdale"] = ["07457"]
muniGroup2Zips["Rockaway"] = ["07866"]
muniGroup2Zips["Roseland"] = ["07068"]
muniGroup2Zips["Sparta"] = ["07871"]
muniGroup2Zips["Stanhope"] = ["07874"]
muniGroup2Zips["Totowa"] = ["07502"]
muniGroup2Zips["Verona"] = ["07044"]
muniGroup2Zips["Wanaque"] = ["07465"]
muniGroup2Zips["Wayne"] = ["07470"]
muniGroup2Zips["West Orange"] = ["07052"]

#zip code to municipality group mapping
zip2MuniGroup = {}
for key,value in muniGroup2Zips.iteritems():
    for zipCode in value:
	zip2MuniGroup[zipCode] = key

df = df[df["Zip"].isin(zip2MuniGroup.keys())]

#Add muni group and group all zips with the same group
df["MuniGroup"] = df["Zip"].apply(lambda x: zip2MuniGroup[x])
df = df.groupby("MuniGroup",as_index=False).sum()

#total salt using method from nj.com
df["totalSALT"] = df["(63)"]/df["(62)"] + df["(65)"]/df["(64)"] + df["(67)"]/df["(66)"]

#total salt divided by total returns
df["totalSALT2"] = (df["(63)"] + df["(65)"] + df["(67)"])/df["(1)"]

df["SLFrac"] = df["(62)"]/df["(1)"]
df["REFrac"] = df["(66)"]/df["(1)"]

dfVotes = pd.read_csv("2016Votes_RVs.csv")
#Municipality group to municipality mapping
muniGroup2Munis = {}
muniGroup2Munis["Bloomfield"]   = ["bloomfield"]
muniGroup2Munis["Bloomingdale"] = ["bloomingdale"]
muniGroup2Munis["Boonton"]         = ["boonton boro","boonton twp"] #town and twp
muniGroup2Munis["Butler+Kinnelon"]  = ["butler","kinnelon"]
muniGroup2Munis["Byram"]  = ["byram"] #also andover and green twp but not for voting data
muniGroup2Munis["Caldwells"]  = ["caldwell","north caldwell","west caldwell"]
muniGroup2Munis["Cedar Grove"] = ["cedar grove"]
muniGroup2Munis["Chathams+Green Village"] = ["chatham boro","chatham twp"]
muniGroup2Munis["Denville"] = ["denville"]
muniGroup2Munis["East Hanover"] = ["east hanover"]
muniGroup2Munis["Essex Fells"] = ["essex fells"]
muniGroup2Munis["Fairfield"] = ["fairfield"]
muniGroup2Munis["Florham Park"] = ["florham park"]
muniGroup2Munis["Hanover"] = ["hanover"] #whippany + cedar knolls
muniGroup2Munis["Harding"] = ["harding"] #new vernon zip code
muniGroup2Munis["Hopatcong"] = ["hopatcong"] 
muniGroup2Munis["Jefferson"] = ["jefferson"] #oak ridge and newfoundland
muniGroup2Munis["Lincoln Park"] = ["lincoln park"] 
muniGroup2Munis["Little Falls+Woodland Park"] = ["little falls","woodland park"] 
muniGroup2Munis["Livingston"] = ["livingston"] 
muniGroup2Munis["Madison"] = ["madison"] 
muniGroup2Munis["Mendham"] = ["mendham boro","mendham twp"] #town + twp
muniGroup2Munis["Upper Montclair"] = ["montclair"]
muniGroup2Munis["Montville+Towaco"] = ["montville"]
muniGroup2Munis["Morris Plains"] = ["morris plains"]
muniGroup2Munis["Morristown"] = ["morris twp","morristown"] #town + twp
muniGroup2Munis["Mountain Lakes"] = ["mountain lakes"]
muniGroup2Munis["North Haledon"] = ["north haledon"]
muniGroup2Munis["Nutley"] = ["nutley"]
muniGroup2Munis["Ogdensburg"] = ["ogdensburg"]
muniGroup2Munis["Parsippany"] = ["parsippany"]
muniGroup2Munis["Pequannock"] = ["pequannock"]
muniGroup2Munis["Pompton Lakes"] = ["pompton lakes"]
muniGroup2Munis["Randolph"] = ["randolph","victory gardens"] #+dover
muniGroup2Munis["Riverdale"] = ["riverdale"]
muniGroup2Munis["Rockaway"] = ["rockaway boro","rockaway twp"]
muniGroup2Munis["Roseland"] = ["roseland"]
muniGroup2Munis["Sparta"] = ["sparta"]
muniGroup2Munis["Stanhope"] = ["stanhope"]
muniGroup2Munis["Totowa"] = ["totowa"]
muniGroup2Munis["Verona"] = ["verona"]
muniGroup2Munis["Wanaque"] = ["wanaque"]
muniGroup2Munis["Wayne"] = ["wayne"]
muniGroup2Munis["West Orange"] = ["west orange"]

#muni to municipality group mapping
muni2MuniGroup = {}
for key,value in muniGroup2Munis.iteritems():
    for muni in value:
	muni2MuniGroup[muni] = key

#Add muni group and group all munis with the same group
dfVotes["MuniGroup"] = dfVotes["NAME"].apply(lambda x: muni2MuniGroup[x])

dfVotes = dfVotes.groupby("MuniGroup",as_index=False).sum()
dfVotes["Rfrac"] = dfVotes["RF"]/dfVotes["Registered Voters"]
print dfVotes
df = pd.merge(df,dfVotes,on="MuniGroup")

plt.figure()
g = sns.jointplot(df["Rfrac"].values,df["SLFrac"].values,kind="reg",robust=True)
g.ax_joint.axhline(SLFrac,color='k',ls=":",label="State wide average")
g.ax_joint.legend(loc=4)
g.ax_joint.set_xlabel("Freylinghuysen Share of Reg. Voters in 2016")
g.ax_joint.set_ylabel("Fraction of Returns w. S&L Income Tax Deduction")
plt.tight_layout()
plt.savefig("SLFrac.png")
plt.close()

plt.figure()
g = sns.jointplot(df["Rfrac"].values,df["REFrac"].values,kind="reg",robust=True)
g.ax_joint.axhline(REFrac,color='k',ls=":",label="Statewide Average")
g.ax_joint.legend(loc=4)
g.ax_joint.set_xlabel("Freylinghuysen Share of Reg. Voters in 2016")
g.ax_joint.set_ylabel("Fraction of Returns w. Property Tax Deduction")
plt.tight_layout()
plt.savefig("REFrac.png")

plt.figure()
g = sns.jointplot(df["Rfrac"].values,df["totalSALT"].values,kind="reg",robust=True)
g.ax_joint.axhline(totalSALT,color='k',ls=":",label="Statewide Average")
g.ax_joint.legend(loc=4)
g.ax_joint.set_xlabel("Freylinghuysen Share of Reg. Voters in 2016")
g.ax_joint.set_ylabel("Total SALT Deductions, $1000's")
plt.tight_layout()
plt.savefig("totalSALT.png")

plt.figure()
g = sns.jointplot(df["Rfrac"].values,df["totalSALT2"].values,kind="reg",robust=True)
g.ax_joint.axhline(totalSALT2,color='k',ls=":",label="Statewide Average")
g.ax_joint.legend(loc=4)
g.ax_joint.set_xlabel("Freylinghuysen Share of Reg. Voters in 2016")
g.ax_joint.set_ylabel("SALT Deductions per Return, $1000's")
plt.tight_layout()
plt.savefig("totalSALT2.png")

gdf = gpd.read_file(os.path.join("NJ11Shapefiles","NJ11Cousub.shp"))

mergedGeom = []
for idx,row in df.iterrows():
    mg = row["MuniGroup"]
    munis = muniGroup2Munis[mg]
    geoms = gdf[gdf["NAME"].isin(munis)].geometry.values
    mergedGeom.append(cascaded_union(geoms))

gdf = gpd.GeoDataFrame(df, crs={'init': u'epsg:4269'}, geometry=mergedGeom)
gdf = gdf.to_crs({"+proj":"aea +lat_1=29.5 +lat_2=45.5 +lat_0=37.5 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs"})

gdf["REFrac"] = gdf["REFrac"] - REFrac
gdf["SLFrac"] = gdf["SLFrac"] - SLFrac

print "State Avg RE, SL"
print REFrac,SLFrac

gdf['coords'] = gdf['geometry'].apply(lambda x: x.representative_point().coords[:])
gdf['coords'] = [coords[0] for coords in gdf['coords']]

fig,ax = plt.subplots(figsize=(13,9.5))
fig,ax = utl.plotGDF("REMap.png",gdf,None,colorby="data",colorCol='REFrac',cmap=plt.cm.bwr,fig=fig,ax=ax,Annotate="MuniGroup",AnnCoords="coords",climits=(-0.3,0.3))
plt.close()

fig,ax = plt.subplots(figsize=(13,9.5))
fig,ax = utl.plotGDF("SLMap.png",gdf,None,colorby="data",colorCol='SLFrac',cmap=plt.cm.bwr,fig=fig,ax=ax,Annotate="MuniGroup",AnnCoords="coords",climits=(-0.3,0.3))
plt.close()

fig,ax = plt.subplots(figsize=(13,9.5))
fig,ax = utl.plotGDF("thumb.png",gdf,None,colorby="data",colorCol='SLFrac',cmap=plt.cm.bwr,fig=fig,ax=ax,cbar=False)
plt.close()


