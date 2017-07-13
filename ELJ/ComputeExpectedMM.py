import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib.patches import Rectangle

import pandas as pd
import numpy as np
import os
import us
from scipy import stats
from scipy.optimize import curve_fit

from ELJcommon import getDemVotesAndSeats,get_spasym,get_asymFromPct,getExpAsym,varWithShrinkage,betaMOM,list2df,colorBins,getExpMMandStdv,convolveBetas

states = us.states.STATES
abbr2name = us.states.mapping('abbr', 'name')

figDir       = os.path.join("Figures","SimVsAsymptotic")
dataDir      = "Data"

congress    = pd.read_csv(os.path.join(dataDir,"congressImputed.csv"))
data        = pd.read_csv(os.path.join(dataDir,"historicStdv.csv"))
stateData   = pd.read_csv(os.path.join(dataDir,"historicSAsym.csv"),dtype={"STATEFP": object})
dataAB      = pd.read_csv(os.path.join(dataDir,"betaParams.csv"))
dataABState = pd.read_csv(os.path.join(dataDir,"betaParamsState.csv"))


cyc70 = [1972,1974,1976,1978,1980]
cyc80 = [1982,1984,1986,1988,1990]
cyc90 = [1992,1994,1996,1998,2000]
cyc00 = [2002,2004,2006,2008,2010]
cyc10 = [2012,2014,2016]
cycles = [cyc70,cyc80,cyc90,cyc00,cyc10]
cnames = [1970,1980,1990,2000,2010]
binsMM = np.linspace(-.10,.10,100)
binsT = np.linspace(-6.,6.,100)
limit = 0.03
#Compute and plot expected mean median difference{{{1
dataMM = [['State','cycle','expectedCs','stdvCs','expectedCu','stdvCu','expStdv','ndist']]
fig1, ((axs1, axs2), (axs3, axs4)) = plt.subplots(2, 2, sharex="col", sharey=True)

for cnm,cyc in zip(cnames,cycles):
    dfCycle      = dataAB[dataAB["cycle"]==cnm]
    dfCyclePop   = dataABState[dataABState["cycle"]==cnm]
    for state in states:
        abbr = state.abbr
        if abbr == "DC": continue
        dfStatePop = dfCyclePop[dfCyclePop["State"].str.contains(abbr)]
        dfState    = dfCycle[dfCycle["State"].str.contains(abbr)]
        betaParams = zip(dfState["alpha"].tolist(),dfState["beta"].tolist())
        ndist = len(dfState)
        if ndist > 2:
            expCs,expCu,stdvV = getExpMMandStdv(betaParams)

            mn = np.mean(expCs)
            st = np.std(expCs,ddof=1)
            stA = dfStatePop["stdv of votePct"].values[0]*np.sqrt(0.5708/float(ndist))
            
            mng = np.mean(expCu)
            stg = np.std(expCu,ddof=1)
            estdv = np.mean(stdvV)

            #plot some selected states and cycles
            if abbr == "TX" and cnm == 1980:
                N, bins, patches = axs1.hist(expCs-mn,bins=binsMM,normed=1.,label="Sims of mean-med, centered")
                axs1.plot(binsMM,stats.norm.pdf(binsMM,scale=st),linewidth=4,label="Normal Fit to sims")
                axs1.plot(binsMM,stats.norm.pdf(binsMM,scale=stA),linewidth=4,label="Asymptotic Distribution of mean-med")
                axs1.set_xlabel("TX, 1980's")
                axs1.legend()
                axs1.set_xlim((-.1,.1))
                axs1.grid()

            if abbr == "CA" and cnm == 1980:
                N, bins, patches = axs3.hist(expCs-mn,bins=binsMM,normed=1.)
                axs3.plot(binsMM,stats.norm.pdf(binsMM,scale=st),linewidth=4)
                axs3.plot(binsMM,stats.norm.pdf(binsMM,scale=stA),linewidth=4)
                axs3.set_xlabel("CA, 1980's")
                axs3.grid()

            if abbr == "IL" and cnm == 2010:
                N, bins, patches = axs2.hist(expCs-mn,bins=binsMM,normed=1.)
                axs2.plot(binsMM,stats.norm.pdf(binsMM,scale=st),linewidth=4)
                axs2.plot(binsMM,stats.norm.pdf(binsMM,scale=stA),linewidth=4)
                axs2.set_xlabel("PA, 2010's")
                axs2.set_xlim((-.1,.1))
                axs2.grid()

            if abbr == "MA" and cnm == 2010:
                N, bins, patches = axs4.hist(expCs-mn,bins=binsMM,normed=1.)
                axs4.plot(binsMM,stats.norm.pdf(binsMM,scale=st),linewidth=4)
                axs4.plot(binsMM,stats.norm.pdf(binsMM,scale=stA),linewidth=4)
                axs4.set_xlabel("NC, 2010's")
                axs4.grid()

            dataMM.append([abbr,cnm,mn,st,mng,stg,estdv,ndist])



fig1.savefig(os.path.join(figDir,"80vs10.png"))

list2df(dataMM,os.path.join(dataDir,"expMM"))
dataMM = pd.read_csv(os.path.join(dataDir,"expMM.csv"))


def getKdeMMvar(data):
    kde = stats.gaussian_kde(data)
    x = np.linspace(0.,1.,2000)
    pdf = kde(x)
    mean = np.trapz(x*pdf,x=x)
    var  = np.trapz((x-mean)**2*pdf,x=x)
    std  = np.sqrt(var)
    meanLoc = np.argmin(np.abs(x-mean))
    smef = mean - 2.*np.trapz(x[0:meanLoc+1]*pdf[0:meanLoc+1],x=x[0:meanLoc+1])
    emx  = 4.*var*kde(mean)**2
    cbVar = 1.+1./emx-2.*smef/(std*np.sqrt(emx))
    cbVar2 = var+1./(4.*kde(mean)**2)-smef/(kde(mean))
    return cbVar,cbVar2,kde

#get all vote percentages
votePct = np.array(congress["Dem Vote %"].values)
#ignore uncontested
votePct = votePct[(votePct != 0.0) & (votePct != 1.0)] 
#symmetrize
votePct = np.concatenate((1.-votePct,votePct))
cbv,cbv2,kde = getKdeMMvar(votePct)
print "Asymptotic variance from KDE estimate for Cs = ",cbv
print "Asymptotic variance from KDE estimate for Cu = ",cbv2
fig = plt.figure()
ax  = fig.add_subplot(111)
ax.hist(votePct,100,normed=True)
x = np.linspace(0.,1.,300)
ax.plot(x,kde(x),linewidth=4)
ax.grid()
fig.savefig(os.path.join(figDir,"Kde.png"))

fig = plt.figure()
ax  = fig.add_subplot(111)
ax.scatter(dataMM['expStdv'].values,dataMM['stdvCs'].values)
ax.grid()
fig.savefig(os.path.join(figDir,"Stdvs.png"))

fig = plt.figure()
ax  = fig.add_subplot(111)
ax.scatter(dataMM['ndist'].values,dataMM['stdvCs'].values,label="Simulated with beta model")

popt,pconv = curve_fit(lambda x, m: m*x, 1./np.sqrt(dataMM['ndist'].values),dataMM['stdvCs'].values)
ns = range(3,60)
nst = [1./np.sqrt(n) for n in ns]
stda = [np.sqrt(0.5708/float(n)) for n in ns]
stdk = [np.sqrt(cbv/float(n)) for n in ns]
stdf = [popt[0]/np.sqrt(float(n)) for n in ns]
print "fitted variance for Cs = ",popt**2
ax.plot(ns,stdf,label="Relationship Fit to Simulated Variances")
ax.plot(ns,stdk,label="Asymptotic, Historical Data")
ax.plot(ns,stda,label="Asymptotic, Unit Normal")
ax.set_xlabel("Number of Districts")
ax.set_ylabel("Sampling Standard Deviation of Cs")
ax.legend()
ax.grid()
fig.savefig(os.path.join(figDir,"stdv_nCs.png"))

def getMiraVarUni(a=0.,b=1.):
    pdf = 1./(b-a)
    var = (b-a)**2/12.
    std = np.sqrt(var)
    mean = (a+b)/2.
    median = (a+b)/2.
    smef = mean - pdf*(median**2-a**2)
    emx  = 4.*var*pdf**2
    cbVar = 1.+1./emx-2.*smef/(std*np.sqrt(emx))
    cbVar2 = var+1./(4.*pdf**2)-smef/(pdf)
    return cbVar,cbVar2

print getMiraVarUni()
print getMiraVarUni(a=.15,b=.85)

fig = plt.figure()
ax  = fig.add_subplot(111)
ax.scatter(dataMM['ndist'].values,dataMM['stdvCu'].values,label="Simulated with beta model")

popt,pconv = curve_fit(lambda x, m: m*x, 1./np.sqrt(dataMM['ndist'].values),dataMM['stdvCu'].values)
ns = range(3,60)
nst = [1./np.sqrt(n) for n in ns]
stdk = [np.sqrt(cbv2/float(n)) for n in ns]
stdf = [popt[0]/np.sqrt(float(n)) for n in ns]
print "fitted variance for Cu = ",popt**2
ax.plot(ns,stdf,label="Relationship Fit to Simulated Variances")
ax.plot(ns,stdk,label="Asymptotic, Historical Data")
ax.set_xlabel("Number of Districts")
ax.set_ylabel("Sampling Standard Deviation of Cu")
ax.legend()
ax.grid()
fig.savefig(os.path.join(figDir,"stdv_nCu.png"))

#1}}}

