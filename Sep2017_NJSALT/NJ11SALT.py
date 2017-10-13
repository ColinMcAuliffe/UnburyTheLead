
#Import packages
#the os package is for some miscellaneous file operations
import os

#pandas is for analyzing and storing data
#geopandas is pandas 
#                    + a package for reading and writing shapefiles called fiona
#                    + a package for computational geometry called shapely
import pandas as pd
import geopandas as gpd

#Numpy is a generic python math library
import numpy as np

#matplotlib is for plotting
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.ticker import FormatStrFormatter
from matplotlib.ticker import MaxNLocator

#Seaborn is a statistical visualization package that is built on top of matplotlib
#The set color codes bit sets a bunch of options that generally make plots look nicer than the matplotlib defaults
import seaborn as sns
sns.set(color_codes=True)

#Cascaded union lets you efficiently join multiple contiguous areas into one area
from shapely.ops import cascaded_union

#These are assorted functions that I wrote, for this script I use a cutom function for plotting shapefiles
import utlUtilities as utl

#The tax data is in a csv file which I cleaned a little from the raw excel off the irs website
#the dtype option tells pandas to read the Zip column as a string of characters, because by
#default it will assume it is numeric data and for example 07940 would be read as 7940.0
df = pd.read_csv("15zp31nj.csv",dtype={"Zip":object})

#Now we want to get rid of some rows in the data frame because the csv had some blank rows, and also some rows 
#that correspond to breakdowns by income within a zip code and we only want the summary for the whole zip.
#This method selects row where a condition is true. Below the condition is ~df["Zip"].isnull(). 
#df["Zip"].isnull() means rows where the value of the column Zip is blank, the ~ in front means not.
#So we are making a data frame from the original data frame where the zip code column is not blank, and then
#Overwrite the old data frame with the new one. This gets rid of the blank rows. Similarly, the second line
#Selects only rows where the income category is empty, which is overall zip code summary
df = df[~df["Zip"].isnull()]
df = df[df["Categoty"].isnull()]


#This is not really needed but here all columns except the relvant ones are dropped. Instead of using a 
#Condition to select columns, they are manualy specified in a list
df = df[["Zip","(1)","(62)","(63)","(64)","(65)","(66)","(67)"]]

#The numbers in the dataframe have commas and so python thinks they are character strings and not numbers 
#We want to remove the commas and then convert the strings to numbers. Below, we select all of the columns
#In the dataframe (skipping the zip column) and do the conversion
cols = ["(1)","(62)","(63)","(64)","(65)","(66)","(67)"]
for col in cols:
    df[col] = df[col].str.replace(",","")
    df[col] = df[col].astype(np.float64)

#These are the statewide averages for the proportion of returns using S&L income and property tax deductions
#For example df["(62)"].sum() means add upp all the rows in the column named "(62)" in the data frame
SLFrac = df["(62)"].sum()/df["(1)"].sum()
REFrac = df["(66)"].sum()/df["(1)"].sum()

totalSALT = df["(63)"].sum()/df["(62)"].sum() + df["(65)"].sum()/df["(64)"].sum() + df["(67)"].sum()/df["(66)"].sum()
totalSALT2 = (df["(63)"].sum() + df["(65)"].sum() + df["(67)"].sum())/df["(1)"].sum()

#Municipality group to zip group mapping
#This uses a python data structure called a dictionary. A dictionary has a keys which correspond to values
#The key is basically an identifier for the value. In this case the key is the name of a census county
#subdivision (or group of subdivisions) and the value is a list of zip codes. So the dictionary tells us
#Which zip codes are associated with a group of municipalities. All the info is entered manually since I
#Don't know how to automate this
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
#This is a dictionary which represents the inverse of the muni2Zip mapping.
#Instead of telling us zip codes that are associated with a muni group, it
#Tells us which muni group a zip code belongs to We construct it by looping 
#over all of the zip codes and making a dictionary where the keys are zip codes
zip2MuniGroup = {}
for key,value in muniGroup2Zips.iteritems():
    for zipCode in value:
	zip2MuniGroup[zipCode] = key

#This filters out all of the non NJ11 zip codes in our tax data
df = df[df["Zip"].isin(zip2MuniGroup.keys())]

#Now we add a column to the tax data frame for muni group since we want to
#eventually merge all zips in the same muni group. The line below creates a new
#column by apply a function to Zip column. In this case, the function just uses
#the zip to muni group dictionary to look up the muni group name for each zip
df["MuniGroup"] = df["Zip"].apply(lambda x: zip2MuniGroup[x])

#This is one line of code that does a lot of work. Groupby collects data into
#groups so that each group consists of rows which have the same value of the
#column MuniGroup. The .sum() means that pandas will make new rows that are the 
#sum of the all of the values within a group
df = df.groupby("MuniGroup",as_index=False).sum()

#Add new columns to the grouped data frame for the SALT stats in each zip code group
#total salt using method from nj.com
df["totalSALT"] = df["(63)"]/df["(62)"] + df["(65)"]/df["(64)"] + df["(67)"]/df["(66)"]

#total salt divided by total returns
df["totalSALT2"] = (df["(63)"] + df["(65)"] + df["(67)"])/df["(1)"]

df["SLFrac"] = df["(62)"]/df["(1)"]
df["REFrac"] = df["(66)"]/df["(1)"]

#Now we read in a csv file with the voting data. We need to eventually merge this
#with tax data, but first we need to make sure that merge municipalities into groups 
#that match the zip code groups. Note that all of this business is not usually needed
#and it is just because we have tax data by zip and voting data by muni and they don't
#match up too nicely
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

#We get the muni to muni group mapping similar to before. The groupby operation
#on the voting data is also similar to before
#muni to municipality group mapping
muni2MuniGroup = {}
for key,value in muniGroup2Munis.iteritems():
    for muni in value:
	muni2MuniGroup[muni] = key

#Add muni group and group all munis with the same group
dfVotes["MuniGroup"] = dfVotes["NAME"].apply(lambda x: muni2MuniGroup[x])

dfVotes = dfVotes.groupby("MuniGroup",as_index=False).sum()
dfVotes["Rfrac"] = dfVotes["RF"]/dfVotes["Registered Voters"]

#We now have two data frames corresponding to our muni groups. df has the tax data
#and dfVotes has the voting data. They get merged together with pd.merge. The on 
#option let's us specify how we want to merge. In this case the two data frames are
#matched by the values in the muniGroup column
df = pd.merge(df,dfVotes,on="MuniGroup")

#These are a bunch of plots using seaborn's jointplot function which is like a scatter
#plot with extra whistles and bells. Here we're asking it to also do a robust linear 
#regression on the data we're comparing
plt.figure()
g = sns.jointplot(df["Rfrac"].values,df["SLFrac"].values,kind="reg",robust=True)
g.ax_joint.axhline(SLFrac,color='k',ls=":",label="State wide average")
g.ax_joint.legend(loc=4)
g.ax_joint.set_xlabel("Frelinghuysen Share of Reg. Voters in 2016")
g.ax_joint.set_ylabel("Fraction of Returns w. S&L Income Tax Deduction")
plt.tight_layout()
plt.savefig("SLFrac.png")
plt.close()

plt.figure()
g = sns.jointplot(df["Rfrac"].values,df["REFrac"].values,kind="reg",robust=True)
g.ax_joint.axhline(REFrac,color='k',ls=":",label="Statewide Average")
g.ax_joint.legend(loc=4)
g.ax_joint.set_xlabel("Frelinghuysen Share of Reg. Voters in 2016")
g.ax_joint.set_ylabel("Fraction of Returns w. Property Tax Deduction")
plt.tight_layout()
plt.savefig("REFrac.png")

plt.figure()
g = sns.jointplot(df["Rfrac"].values,df["totalSALT"].values,kind="reg",robust=True)
g.ax_joint.axhline(totalSALT,color='k',ls=":",label="Statewide Average")
g.ax_joint.legend(loc=4)
g.ax_joint.set_xlabel("Frelinghuysen Share of Reg. Voters in 2016")
g.ax_joint.set_ylabel("Total SALT Deductions, $1000's")
plt.tight_layout()
plt.savefig("totalSALT.png")

plt.figure()
g = sns.jointplot(df["Rfrac"].values,df["totalSALT2"].values,kind="reg",robust=True)
g.ax_joint.axhline(totalSALT2,color='k',ls=":",label="Statewide Average")
g.ax_joint.legend(loc=4)
g.ax_joint.set_xlabel("Frelinghuysen Share of Reg. Voters in 2016")
g.ax_joint.set_ylabel("SALT Deductions per Return, $1000's")
plt.tight_layout()
plt.savefig("totalSALT2.png")

#Now we're going to use geopandas to load in the NJ11 municipality shape file
gdf = gpd.read_file(os.path.join("NJ11Shapefiles","NJ11Cousub.shp"))

#Since we had to merge municipal data, we also have to merge the shapes. To
#make sure that the merged shapes are in the same order as out tax + voting 
#data frame, we make a list of merged geometries by looping over each row
#of the data frame, grabbing all of the municipal shapes for a muni group,
#and merging them
mergedGeom = []
for idx,row in df.iterrows():
    mg = row["MuniGroup"]
    munis = muniGroup2Munis[mg]
    geoms = gdf[gdf["NAME"].isin(munis)].geometry.values
    mergedGeom.append(cascaded_union(geoms))

#Now we make a geodataframe with our tax+voting data and the merged geometries
#The crs option specifies the coordinate system. epsg:4269 is the default for 
#all census shape files as far as I know. 
gdf = gpd.GeoDataFrame(df, crs={'init': u'epsg:4269'}, geometry=mergedGeom)
#This changes the coordinate system to an albers equal area projection for better plotting in 2D
gdf = gdf.to_crs({"+proj":"aea +lat_1=29.5 +lat_2=45.5 +lat_0=37.5 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs"})

#This gives us the SALT data in munis relative to state averages
gdf["REFrac"] = gdf["REFrac"] - REFrac
gdf["SLFrac"] = gdf["SLFrac"] - SLFrac


#This is a way to get the coordinates of a point that is inside each of our shapes
#The point will be used to annotate the plot in a moment
gdf['coords'] = gdf['geometry'].apply(lambda x: x.representative_point().coords[:])
gdf['coords'] = [coords[0] for coords in gdf['coords']]

#These plot maps with the data using a custom function with options on specifying color schemes
#Color bars, annotations, etc. 
fig,ax = plt.subplots(figsize=(13,9.5))
fig,ax = utl.plotGDF("REMap.png",gdf,None,colorby="data",colorCol='REFrac',cmap=plt.cm.bwr,fig=fig,ax=ax,Annotate="MuniGroup",AnnCoords="coords",climits=(-0.3,0.3))
plt.close()

fig,ax = plt.subplots(figsize=(13,9.5))
fig,ax = utl.plotGDF("SLMap.png",gdf,None,colorby="data",colorCol='SLFrac',cmap=plt.cm.bwr,fig=fig,ax=ax,Annotate="MuniGroup",AnnCoords="coords",climits=(-0.3,0.3))
plt.close()

fig,ax = plt.subplots(figsize=(13,9.5))
fig,ax = utl.plotGDF("thumb.png",gdf,None,colorby="data",colorCol='SLFrac',cmap=plt.cm.bwr,fig=fig,ax=ax,cbar=False)
plt.close()
#The end

