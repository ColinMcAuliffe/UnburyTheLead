import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm

import utlUtilities as utl
import geopandas as gpd
from matplotlib.patches import Rectangle

import pandas as pd
import numpy as np
import os
import us
from scipy import stats,special

from ELJcommon import getDemVotesAndSeats,get_spasym,get_asymFromPct,getExpAsym,varWithShrinkage,betaMOM,list2df,colorBins,get_asymFromCenteredPct,normalEst

def setFontSize(ax,fs):
    for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] +
             ax.get_xticklabels() + ax.get_yticklabels()):
        item.set_fontsize(fs)
    plt.setp(ax.get_legend().get_texts(), fontsize=fs)
    return ax
states = us.states.STATES
abbr2name = us.states.mapping('abbr', 'name')

figDir       = os.path.join("Figures","HistoricAsymmetry")
dataDir      = "Data"
figExt       = ".png"

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

oneByOne = (6.5,6.5)
data = pd.read_csv(os.path.join(dataDir,"historicStdv.csv"))
stateData = pd.read_csv(os.path.join(dataDir,"historicSAsym.csv"),dtype={"STATEFP": object})

xu = 0.32
n  = 200
xs   = np.linspace(0.01,xu,n)
a,b,c,d = stats.beta.fit(data.Stdv.values[data.Stdv.values > 0.],floc=0.,fscale=1.)
pdfs   = stats.beta.pdf(xs,a,b)

kde = stats.gaussian_kde(data.Mean.values)
xm   = np.linspace(0.0001,.9999,n)
pdfm = kde(xm)

XS,XM = np.meshgrid(xs,xm)
ALPHA = ((1.-XM)/XS**2-1./XM)*XM**2
BETA  = ALPHA*(1./XM-1.)

PDFS,PDFM = np.meshgrid(pdfs,pdfm)
jointPDF = PDFS*PDFM
fig = plt.figure()
ax = fig.gca(projection='3d')
# Plot the surface.
surf = ax.plot_surface(XS, XM, jointPDF, cmap=cm.jet,
                       linewidth=0, antialiased=False)
#plt.show()

dfState = congress[congress["State"] == "California"]
dfCycle = dfState[dfState["raceYear"].isin(cyc00)]
dfDistrict = dfCycle[dfCycle["AreaNumber"] == 1]
votePct = np.array(dfDistrict["Dem Vote %"].values)
print votePct
xm = XM.flatten().tolist()
xs = XS.flatten().tolist()
def getLikelihood(m,s,x):
    a, b = (0. - m) / s, (1. - m) / s
    #pdf = stats.norm.pdf(x,loc=m,scale=s)
    pdf = stats.truncnorm.pdf(x, a, b,loc=m,scale=s)
    return np.sum(np.log(pdf))
    #return np.prod(pdf)
likelihood = np.array([getLikelihood(m,s,votePct) for m,s in zip(xm,xs)])
likelihood = likelihood.reshape((n,n))
print np.shape(ALPHA),np.shape(BETA),np.shape(likelihood)
post = likelihood+np.log(jointPDF)
idx  = np.argmax(post)
print xm[idx],xs[idx]
idx  = np.argmax(likelihood)
print xm[idx],xs[idx]
fig = plt.figure()
ax = fig.gca(projection='3d')
# Plot the surface.
surf = ax.plot_surface(XS, XM, likelihood+np.log(jointPDF), cmap=cm.jet,
                       linewidth=0, antialiased=False)
plt.show()




