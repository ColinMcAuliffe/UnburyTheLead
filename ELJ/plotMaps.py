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


states = us.states.STATES
abbr2name = us.states.mapping('abbr', 'name')

figDir       = os.path.join("Figures","ExpectedAsymmetry")
dataDir      = "Data"

stateData = pd.read_csv(os.path.join(dataDir,"expAsym.csv"),dtype={"STATEFP": object})


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
shapeFileStates   = "../CommonData/ShapeFiles/cb_2015_us_state_500k/cb_2015_us_state_500k.shp"
gdf = gpd.read_file(shapeFileStates)
for cyc,cnm in zip(cycles,cnames):
        dfYear  = stateData[stateData["cycle"] == cnm]
        gdfYear = gdf.merge(dfYear,on="STATEFP") 
        gdfYear["expectedAsymPct"] = gdfYear["expectedAsymPct"]*100.
        utl.plotGDF(os.path.join(figDir,"expAsymPct_"+str(cnm)+".png"),gdfYear,"USALL",colorby="data",colorCol="expectedAsymPct",cfmt="%2.0f",cmap=plt.cm.bwr,climits=(-20.,20.),title=str(cnm)+"s")
        if cnm == 2010: utl.plotGDF(os.path.join(figDir,"Thumb.png"),gdfYear,"USALL",colorby="data",colorCol="expectedAsymPct",cmap=plt.cm.bwr,climits=(-20.,20.),cbar=False)
        utl.plotGDF(os.path.join(figDir,"expAsym_"+str(cnm)+".png"),gdfYear,"USALL",colorby="data",colorCol="expectedAsym",cmap=plt.cm.bwr,climits=(-6.,6.),title=str(cnm)+"s")
        
#1}}}
