import matplotlib.pyplot as plt

from matplotlib.ticker import MaxNLocator
import utlUtilities as utl
import geopandas as gpd
from matplotlib.patches import Rectangle

import pandas as pd
import numpy as np
import os
import us
from scipy import stats

from ELJcommon import betaMOM

states = us.states.STATES
abbr2name = us.states.mapping('abbr', 'name')

figDir       = os.path.join("Figures","ExpectedAsymmetry")
dataDir      = "Data"

congress = pd.read_csv(os.path.join(dataDir,"congressImputed.csv"))


cyc70 = [1972,1974,1976,1978,1980]
cyc80 = [1982,1984,1986,1988,1990]
cyc90 = [1992,1994,1996,1998,2000]
cyc00 = [2002,2004,2006,2008,2010]
cyc10 = [2012,2014,2016]
cycles = [cyc70,cyc80,cyc90,cyc00,cyc10]
cnames = [1970,1980,1990,2000,2010]
bins6 = np.linspace(-6.25,6.25,26)
bins7 = np.linspace(-7.25,7.25,30)
#Plot maps of sp asymmetry{{{1
#shapeFileStates   = "../CommonData/ShapeFiles/cb_2015_us_state_500k/cb_2015_us_state_500k.shp"
#gdf = gpd.read_file(shapeFileStates)
#for cyc in cycles:
#    for year in cyc:
#        dfYear  = stateData[stateData["year"] == year]
#        gdfYear = gdf.merge(dfYear,on="STATEFP") 
#        utl.plotGDF(os.path.join(figDir,"spa_"+str(year)+".png"),gdfYear,"USALL",colorby="data",colorCol="specAsym (seats)",cmap=plt.cm.bwr,climits=(-6,6))
#        d = np.min([0.5 - np.min(dfYear["demVoteFrac"].values),np.max(dfYear["demVoteFrac"].values) - 0.5])
#        utl.plotGDF(os.path.join(figDir,"pop_"+str(year)+".png"),gdfYear,"USALL",colorby="data",colorCol="repVoteFrac",cmap=plt.cm.bwr,climits=(.5-d,0.5+d),cfmt="%0.2f")
#        
#1}}}
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, sharex=True, sharey='row',figsize=(18,10))

meansS = [0.30,0.45,0.55,0.70]
meansU = [0.18,0.55,0.57,0.70]
x = np.linspace(0.,1.,1000)
y = range(1,6)
for mean in meansS:
    a,b,l,c = betaMOM([mean],shrinkage=0.002)
    z       = stats.beta.pdf(x,a,b)
    ax1.plot(x,z)
    samps = stats.beta.rvs(a,b,size=5)
    ax3.plot(samps,y,ls="None",marker='x')
    
for mean in meansU:
    a,b,l,c = betaMOM([mean],shrinkage=0.002)
    z       = stats.beta.pdf(x,a,b)
    ax2.plot(x,z)
    samps = stats.beta.rvs(a,b,size=5)
    ax4.plot(samps,y,ls="None",marker='x')
    
    
ax1.set_ylabel("Probability")
ax3.set_xlabel("District Vote Share")
ax3.set_ylabel("Sample Election Number")
ax4.set_xlabel("District Vote Share")

ax3.set_ylim((0.0,6.0))
ax1.yaxis.set_major_locator(MaxNLocator(7))
ax3.yaxis.set_major_locator(MaxNLocator(7))
ax1.xaxis.set_major_locator(MaxNLocator(10))


ax1.grid()
ax2.grid()
ax3.grid()
ax4.grid()
fig.savefig(os.path.join(figDir,"popVsSamp.png"))
    
