import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib.patches import Rectangle

import pandas as pd
import numpy as np
import os
import us
from scipy import stats
from scipy.optimize import curve_fit

from ELJcommon import getDemVotesAndSeats,get_spasym,get_asymFromPct,getExpAsym,varWithShrinkage,betaMOM,list2df,colorBins,getExpMMandT,convolveBetas

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
#dataMM = [['State','cycle','expectedMM','stdvMM','expectedMMg','stdvMMg','stdvPct','ndist']]
#fig1, ((axt1, axt2), (axt3, axt4)) = plt.subplots(2, 2, sharex="col", sharey=True,figsize=(18,10))
#fig2, ((axs1, axs2), (axs3, axs4)) = plt.subplots(2, 2, sharex="col", sharey=True,figsize=(18,10))
#
#fig3, axh = plt.subplots(1,1)
#fig4, ((axl1, axl2), (axl3, axl4)) = plt.subplots(2, 2, sharex="col", sharey=True,figsize=(18,10))
#
#for cnm,cyc in zip(cnames,cycles):
#    dfCycle      = dataAB[dataAB["cycle"]==cnm]
#    dfCyclePop   = dataABState[dataABState["cycle"]==cnm]
#    for state in states:
#        abbr = state.abbr
#        if abbr == "DC": continue
#        dfStatePop = dfCyclePop[dfCyclePop["State"].str.contains(abbr)]
#        #if np.abs(0.5-dfStatePop["mean"].values[0]) > limit: continue
#        dfState    = dfCycle[dfCycle["State"].str.contains(abbr)]
#        betaParams = zip(dfState["alpha"].tolist(),dfState["beta"].tolist())
#        ndist = len(dfState)
#        if ndist > 2:
#            expMM,expMMg,expT = getExpMMandT(betaParams)
#
#            mn = np.mean(expMM)
#            st = np.std(expMM,ddof=1)
#            stA = dfStatePop["stdv of votePct"].values[0]*np.sqrt(0.5708/float(ndist))
#            p5  = stats.norm.ppf(.95,scale=st)
#            p5A = stats.norm.ppf(.95,scale=stA)
#            p5d = stats.norm.cdf(p5,scale=stA)
#            
#            mng = np.mean(expMMg)
#            stg = np.std(expMMg,ddof=1)
#
#            mt = np.mean(expT)
#            df = len(dfState)-2
#            #st = np.std(expMM,ddof=1)
#            #stA = dfStatePop["stdv of votePct"].values[0]/np.sqrt(float(len(dfState)))
#            #p5  = stats.norm.ppf(.95,scale=st)
#            #p5A = stats.norm.ppf(.95,scale=stA)
#            
#            #plot some selected states and cycles
#            if abbr == "TX" and cnm == 1980:
#                N, bins, patches = axs1.hist(expMM-mn,bins=binsMM,normed=1.,label="Sims of mean-med, centered")
#                axs1.plot(binsMM,stats.norm.pdf(binsMM,scale=st),linewidth=4,label="Normal Fit to sims")
#                axs1.plot(binsMM,stats.norm.pdf(binsMM,scale=stA),linewidth=4,label="Asymptotic Distribution of mean-med")
#                axs1.set_xlabel("TX, 1980's")
#                axs1.legend()
#                axs1.set_xlim((-.1,.1))
#                axs1.grid()
#
#                N, bins, patches = axt1.hist(expT-mt,bins=binsT,normed=1.,label="Sims of T-stat, centered")
#                axt1.plot(binsT,stats.t.pdf(binsT,df),linewidth=4,label="Asymptotic Distribution of T-stat")
#                #axt1.plot(binsMM,stats.norm.pdf(binsMM,scale=stA))
#                axt1.legend()
#                axt1.set_xlabel("TX, 1980's")
#                axt1.grid()
#
#                x,l,mean,stdv,skew = convolveBetas(betaParams)
#                print "TX",mean,stdv,skew
#                axl1.plot(1.-x[0:500],l[0:500],linewidth=4,color='r')
#                axl1.plot(x[500:],l[500:],linewidth=4,color='b')
#                axl1.legend()
#                axl1.set_xlabel("TX, 1980's")
#                axl1.grid()
#            if abbr == "CA" and cnm == 1980:
#                N, bins, patches = axs3.hist(expMM-mn,bins=binsMM,normed=1.)
#                axs3.plot(binsMM,stats.norm.pdf(binsMM,scale=st),linewidth=4)
#                axs3.plot(binsMM,stats.norm.pdf(binsMM,scale=stA),linewidth=4)
#                axs3.set_xlabel("CA, 1980's")
#                axs3.grid()
#
#                N, bins, patches = axt3.hist(expT-mt,bins=binsT,normed=1.)
#                axt3.plot(binsT,stats.t.pdf(binsT,df),linewidth=4)
#                #axt3.plot(binsMM,stats.norm.pdf(binsMM,scale=stA))
#                axt3.set_xlabel("CA, 1980's")
#                axt3.grid()
#
#                x,l,mean,stdv,skew = convolveBetas(betaParams)
#                print "CA",mean,stdv,skew
#                axl3.plot(1.-x[0:500],l[0:500],linewidth=4,color='r')
#                axl3.plot(x[500:],l[500:],linewidth=4,color='b')
#                axl3.legend()
#                axl3.set_xlabel("CA, 1980's")
#                axl3.grid()
#            if abbr == "IL" and cnm == 2010:
#                N, bins, patches = axs2.hist(expMM-mn,bins=binsMM,normed=1.)
#                axs2.plot(binsMM,stats.norm.pdf(binsMM,scale=st),linewidth=4)
#                axs2.plot(binsMM,stats.norm.pdf(binsMM,scale=stA),linewidth=4)
#                axs2.set_xlabel("PA, 2010's")
#                axs2.set_xlim((-.1,.1))
#                axs2.grid()
#
#                N, bins, patches = axt2.hist(expT-mt,bins=binsT,normed=1.)
#                axt2.plot(binsT,stats.t.pdf(binsT,df),linewidth=4)
#                #axt2.plot(binsMM,stats.norm.pdf(binsMM,scale=stA))
#                axt2.set_xlabel("PA, 2010's")
#                axt2.grid()
#
#                x,l,mean,stdv,skew = convolveBetas(betaParams)
#                print "PA",mean,stdv,skew
#                axl2.plot(1.-x[0:500],l[0:500],linewidth=4,color='r')
#                axl2.plot(x[500:],l[500:],linewidth=4,color='b')
#                axl2.legend()
#                axl2.set_xlabel("PA, 2010's")
#                axl2.grid()
#            if abbr == "MA" and cnm == 2010:
#                N, bins, patches = axs4.hist(expMM-mn,bins=binsMM,normed=1.)
#                axs4.plot(binsMM,stats.norm.pdf(binsMM,scale=st),linewidth=4)
#                axs4.plot(binsMM,stats.norm.pdf(binsMM,scale=stA),linewidth=4)
#                axs4.set_xlabel("NC, 2010's")
#                axs4.grid()
#
#                N, bins, patches = axt4.hist(expT-mt,bins=binsT,normed=1.)
#                axt4.plot(binsT,stats.t.pdf(binsT,df),linewidth=4)
#                #axt4.plot(binsMM,stats.norm.pdf(binsMM,scale=stA))
#                axt4.set_xlabel("NC, 2010's")
#                axt4.grid()
#
#                x,l,mean,stdv,skew = convolveBetas(betaParams)
#                print "NC",mean,stdv,skew
#                axl4.plot(1.-x[0:500],l[0:500],linewidth=4,color='r')
#                axl4.plot(x[500:],l[500:],linewidth=4,color='b')
#                axl4.legend()
#                axl4.set_xlabel("NC, 2010's")
#                axl4.grid()
#            dataMM.append([abbr,cnm,mn,st,mng,stg,dfStatePop["stdv of votePct"].values[0],ndist])
#
#
#
#fig1.savefig(os.path.join(figDir,"80vs10T.png"))
#fig2.savefig(os.path.join(figDir,"80vs10MM.png"))
#fig4.savefig(os.path.join(figDir,"80vs10DL.png"))
#
#list2df(dataMM,os.path.join(dataDir,"expMM"))
dataMM = pd.read_csv(os.path.join(dataDir,"expMM.csv"))


def mcMMg(n,nsamp=10000):
    samples = np.random.uniform(low=0.15,high=0.85,size=(int(n),nsamp))
    mean = np.mean(samples,axis=0)
    median = np.median(samples,axis=0)
    C = mean-median
    return np.std(C,ddof=1)

def mcMM(n,nsamp=10000):
    samples = np.random.normal(size=(int(n),nsamp))
    mean = np.mean(samples,axis=0)
    median = np.median(samples,axis=0)
    stdv = np.std(samples,axis=0,ddof=1)
    C = (mean-median)/stdv
    return np.std(C,ddof=1)
    
def getKdeMMvar(data):
    kde = stats.gaussian_kde(data)
    x = np.linspace(np.min(data),np.max(data),2000)
    pdf = kde(x)
    mean = np.trapz(x*pdf,x=x)
    var  = np.trapz((x-mean)**2*pdf,x=x)
    std  = np.sqrt(var)
    meanLoc = np.argmin(np.abs(x-mean))
    print meanLoc
    smef = mean - 2.*np.trapz(x[0:meanLoc+1]*pdf[0:meanLoc+1],x=x[0:meanLoc+1])
    emx  = 4.*var*kde(mean)**2
    cbVar = 1.+1./emx-2.*smef/(std*np.sqrt(emx))
    cbVar2 = var+1./(4.*kde(mean)**2)-smef/(kde(mean))
    return cbVar,cbVar2

#get all vote percentages
votePct = np.array(congress["Dem Vote %"].values)
#ignore uncontested
votePct = votePct[(votePct != 0.0) & (votePct != 1.0)] 
#symmetrize
votePct = np.concatenate((1.-votePct,votePct))
cbv,cbv2 = getKdeMMvar(votePct)
a,b,c,d = stats.beta.fit(votePct,floc=0.,fscale=1.)
print a,b

fig = plt.figure()
ax  = fig.add_subplot(111)
ax.scatter(dataMM['ndist'].values,dataMM['stdvMM'].values,label="Simulated with beta model")

popt,pconv = curve_fit(lambda x, m: m*x, 1./np.sqrt(dataMM['ndist'].values),dataMM['stdvMM'].values)
ns = range(3,60)
nst = [1./np.sqrt(n) for n in ns]
std = [mcMM(n) for n in ns]
stda = [np.sqrt(0.5708/float(n)) for n in ns]
stdk = [np.sqrt(cbv/float(n)) for n in ns]
stdf = [popt[0]/np.sqrt(float(n)) for n in ns]
print popt**2,cbv
ax.plot(ns,stdf,label="Relationship Fitted to Simulation Data")
ax.plot(ns,stdk,label="Asymptotic, Historical Data")
ax.plot(ns,stda,label="Asymptotic, Unit Normal")
ax.set_xlabel("Number of Districts")
ax.set_ylabel("Sampling Standard Deviation of (Mean-Median)/SD")
ax.legend()
ax.grid()
fig.savefig(os.path.join(figDir,"stdv_nMM.png"))

def getMiraVarUni(a=0.,b=1.):
    pdf = 1./(b-a)
    var = (b-a)**2/12.
    mean = (a+b)/2.
    median = (a+b)/2.
    smef = mean - pdf*(median**2-a**2)
    return 4.*var+1./pdf**2-4.*smef/pdf


fig = plt.figure()
ax  = fig.add_subplot(111)
ax.scatter(dataMM['ndist'].values,dataMM['stdvMMg'].values,label="Simulated with beta model")

popt,pconv = curve_fit(lambda x, m: m*x, 1./np.sqrt(dataMM['ndist'].values),dataMM['stdvMMg'].values)
ns = range(3,60)
nst = [1./np.sqrt(n) for n in ns]
std = [mcMMg(n) for n in ns]
stdk = [np.sqrt(cbv2/float(n)) for n in ns]
stdf = [popt[0]/np.sqrt(float(n)) for n in ns]
print popt**2,cbv2
ax.plot(ns,stdf,label="Relationship Fitted to Simulation Data")
ax.plot(ns,stdk,label="Asymptotic, Historical Data")
ax.set_xlabel("Number of Districts")
ax.set_ylabel("Sampling Standard Deviation of Mean-Median")
ax.legend()
ax.grid()
fig.savefig(os.path.join(figDir,"stdv_nMMg.png"))

fig = plt.figure()
ax  = fig.add_subplot(111)
ax.scatter(dataMM['expectedMMg'].values,dataMM['expectedMM'].values)
#ax.scatter(dataMM['stdvMMg'].values,dataMM['stdvMM'].values)
fig.savefig(os.path.join(figDir,"mvm.png"))

fig = plt.figure()
ax  = fig.add_subplot(111)
ax.scatter(dataMM['stdvPct'].values/np.sqrt(dataMM['ndist'].values),dataMM['stdvMMg'].values)
ax.plot([0.,.1],[0.,.1])
#ax.scatter(dataMM['stdvPct'].values,dataMM['stdvMM'].values,color='g')
#ax.scatter(dataMM['stdvMMg'].values,dataMM['stdvMM'].values)
fig.savefig(os.path.join(figDir,"mvms.png"))
#1}}}

