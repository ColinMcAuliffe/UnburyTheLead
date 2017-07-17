import pandas as pd
import numpy as np
import os
from scipy import stats

def getDemVotesAndSeats(dem,rep):
    dem_total = float(np.sum(dem))
    rep_total = float(np.sum(rep))
    popVote = dem_total/(dem_total+rep_total)
    demVotePct = dem/(dem+rep)
    seats = float(len(demVotePct[demVotePct>0.5]))
    seatFrac = seats/float(len(demVotePct))
    return dem_total,rep_total,popVote,seats,seatFrac

def get_spasym(dem,rep):
    if len(dem) > 1:
        dem = dem.astype(float)
        rep = rep.astype(float)
        dem_total = np.sum(dem)
        rep_total = np.sum(rep)
        popVote = np.sum(dem)/(np.sum(dem)+np.sum(rep))
        demVote = dem/(dem+rep)
        actSeats = float(len(demVote[demVote<0.5]))
        repFlp  = rep*dem_total/rep_total
        demFlp  = dem*rep_total/dem_total
        demVote = demFlp/(demFlp+repFlp)
        flpSeats = float(len(demVote[demVote>0.5]))

        return (actSeats-flpSeats)/2.
    else:
        return 0.

def get_GrofAsym(dem,rep):
    if len(dem) > 1:
        dem = dem.astype(float)
        rep = rep.astype(float)
        dem_total = np.sum(dem)
        rep_total = np.sum(rep)
        totalAvg  = (dem_total+rep_total)/2.
        multDem = totalAvg/dem_total
	multRep = totalAvg/rep_total
        dem = dem*multDem
        rep = rep*multRep
        
        demVote = dem/(dem+rep)
        actSeats = float(len(demVote[demVote<0.5]))
        flpSeats = float(len(demVote[demVote>0.5]))

        return (actSeats-flpSeats)/2.
    else:
        return 0.

def get_EfficiencyGap(dem,rep):
    nseats = float(len(dem))
    if nseats > 1.:
        popVote = np.sum(dem)/(np.sum(dem)+np.sum(rep))
        demPct = dem/(dem+rep)
        demSeats = float(len(demPct[demPct>=0.5]))/nseats
        return 2.*popVote - demSeats - 0.5
    else:
        return 0.

def get_MMDFromCenteredPct(demPct):
    #popular vote is last element in demPct, ignored
    dem  = np.array(demPct[0:-1])
    if len(dem) > 1:
        return 0.5 - np.median(dem)
    else:
        return 0.

def get_EGFromCenteredPct(demPct):
    #popular vote is last element in demPct
    popVoteDem   = demPct[-1]
    dem  = np.array(demPct[0:-1])
    rep  = 1.-dem
    nseats = float(len(dem))
    if nseats > 1.:
        demSeats = float(len(rep[rep<=popVoteDem]))/nseats
        return 2.*popVoteDem - demSeats - 0.5
    else:
        return 0.

def get_asymFromCenteredPct(demPct):
    #popular vote is last element in demPct
    popVoteDem   = demPct[-1]
    popVoteRep   = 1.-popVoteDem
    dem  = np.array(demPct[0:-1])
    rep  = 1.-dem
    nseats = float(len(dem))

    if len(dem) > 1:
        demSeats = float(len(rep[rep<=popVoteDem]))
        repSeats = nseats - float(len(rep[rep<=popVoteRep]))
        return (repSeats-demSeats)/2.
    else:
        return 0.

def get_GFAsymFromCenteredPct(demPct):
    popVoteDem   = 0.5
    popVoteRep   = 0.5
    #popular vote is last element in demPct, ignored
    dem  = np.array(demPct[0:-1])
    rep  = 1.-dem
    nseats = float(len(dem))

    if len(dem) > 1:
        demSeats = float(len(rep[rep<=popVoteDem]))
        repSeats = nseats - float(len(rep[rep<=popVoteRep]))
        return (repSeats-demSeats)/2.
    else:
        return 0.

def get_MMDFromCenteredPct(demPct):
    #popular vote is last element in demPct, ignored
    dem  = np.array(demPct[0:-1])
    if len(dem) > 1:
        return 0.5 - np.median(dem)
    else:
        return 0.

def get_EGFromCenteredPct(demPct):
    #popular vote is last element in demPct
    popVoteDem   = demPct[-1]
    dem  = np.array(demPct[0:-1])
    rep  = 1.-dem
    nseats = float(len(dem))
    if nseats > 1.:
        demSeats = float(len(rep[rep<=popVoteDem]))/nseats
        return 2.*popVoteDem - demSeats - 0.5
    else:
        return 0.

def get_asymFromPct(demPct,decenter=True):
    #popular vote is last element in demPct
    popVote   = demPct[-1]
    dem  = np.array(demPct[0:-1])
    rep  = 1.-dem
    if decenter:
        demTotal = np.sum(dem)
        repTotal = np.sum(rep)
        pct = demTotal/(demTotal+repTotal)
        dem = dem*popVote/pct
        rep = 1.-dem

    demVote = dem/(dem+rep)
    actSeats = float(len(demVote[demVote<0.5]))
    if len(dem) > 1:
        repFlp  = rep*popVote/(1.-popVote)
        demFlp  = dem*(1.-popVote)/popVote
        demVote = demFlp/(demFlp+repFlp)
        flpSeats = float(len(demVote[demVote>0.5]))
        return (actSeats-flpSeats)/2.
    else:
        return 0.

def getMeanMeanDiff(x):
    dem = x[x>0.5]
    rep = x[x<0.5]
    rep = 1.-rep
    if len(dem) > 1 and len(rep) > 1:
        t,p = stats.ttest_ind(dem, rep, equal_var = True)
        return t
    else:
        return 0.

def getExpMMandStdv(params,nsims=10000):
    #simulate
    results = []
    for a,b in params:
        results.append(stats.beta.rvs(a,b,size=nsims))
    results = np.array(results)
    mean    = np.mean(results,axis=0)
    median  = np.median(results,axis=0)
    stdv    = np.std(results,axis=0,ddof=1)
    return (mean-median)/stdv,mean-median,stdv

def getExpMMandT(params,nsims=10000):
    #simulate
    results = []
    for a,b in params:
        results.append(stats.beta.rvs(a,b,size=nsims))
    results = np.array(results)
    mean    = np.mean(results,axis=0)
    median  = np.median(results,axis=0)
    stdv    = np.std(results,axis=0,ddof=1)
    t       = np.apply_along_axis(getMeanMeanDiff,0,results)
    return (mean-median)/stdv,mean-median,t

def getExpAsym(params,dist="Beta",nsims=10000):
    #simulate
    results = []
    if dist == "Beta":
        for a,b in params:
            results.append(stats.beta.rvs(a,b,size=nsims))
    elif dist == "TN":
        for m,s in params:
            a, b = (0. - m) / s, (1. - m) / s
            results.append(stats.truncnorm.rvs(a,b,loc=m,scale=s,size=nsims))
    results = np.array(results)
    asym    = np.apply_along_axis(get_asymFromCenteredPct,0,results)
    return asym

def getAllSVMetrics(params,nsims=10000):
    #simulate
    results = []
    for a,b in params:
        results.append(stats.beta.rvs(a,b,size=nsims))
    results = np.array(results)
    #Specific asymmetry
    spAsym  = np.apply_along_axis(get_asymFromCenteredPct,0,results)
    #Grofman asymmetry
    gfAsym  = np.apply_along_axis(get_GFAsymFromCenteredPct,0,results)
    #Mean - Median
    mmd     = np.apply_along_axis(get_MMDFromCenteredPct,0,results)
    #Efficiency Gap
    eg      = np.apply_along_axis(get_EGFromCenteredPct,0,results)
    return np.array([spAsym,gfAsym,mmd,eg])


def convolveBetas(params,npoints=1000):
    x = np.linspace(0.,1.,npoints)
    a,b = params[0]
    likelihood = stats.beta.pdf(x,a,b)
    for a,b in params[1:]:
        #likelihood = np.convolve(likelihood,stats.beta.pdf(x,a,b),mode="same")
        likelihood += stats.beta.pdf(x,a,b)
    #normalize
    likelihood = likelihood/float(len(params))
    mean = np.trapz(x*likelihood,x=x)
    stdv = np.sqrt(np.trapz((x-mean)**2*likelihood,x=x))
    skew = np.trapz((x-mean)**3*likelihood,x=x)/stdv**3
    return x,likelihood,mean,stdv,skew
def meanWithShrinkage(x,shrinkMean):
    N = float(len(x))
    if N == 0.: return shrinkMean
    mean = (np.sum(x)+shrinkMean)/(N+1.)
    return mean

def varWithShrinkage(x,shrinkVar):
    N = float(len(x))
    if N == 0.: return shrinkVar
    mean = np.mean(x)
    var = (np.sum((x - mean)**2)+shrinkVar)/N
    return var

def normalEst(x,shrinkage=None,mean=None):
    if mean is None: mean = np.mean(x)
    if shrinkage is None:
        var  = np.var(x,ddof=1)
    else:
        var = varWithShrinkage(x,shrinkage)
    return mean,np.sqrt(var)

def betaMOM(x,shrinkage=None,mean=None,useLocScale=False):
    if mean is None: mean = np.mean(x)
    if shrinkage is None:
        var  = np.var(x,ddof=1)
    else:
        var = varWithShrinkage(x,shrinkage)
        #mean = meanWithShrinkage(x,0.5)
    if useLocScale:
        if mean < 0.5:
            loc   = 0.
            scale = mean*2.
        else:
            scale = (1.-mean)*2.
            loc   = 1.-scale
    else:
        loc, scale = 0.,1.
    #account for location and scale
    mean = (mean-loc)/scale
    var  = var/scale**2
    c = mean*(1.-mean)/var-1.
    alpha = mean*c
    beta  = (1.-mean)*c
    return alpha,beta,loc,scale

def list2df(data,dname):
    data = pd.DataFrame(data)
    new_header = data.iloc[0] #grab the first row for the header
    data = data[1:] #take the data less the header row
    data.columns = new_header #set the header row as the df header
    data.index = range(len(data))
    data.to_csv(dname+".csv")

def colorBins(bins,patches,lim,lt='b',gt='r',gray=True):
    for i in range(len(patches)):
        center = (bins[i]+bins[i+1])/2.
        if center < lim:
            patches[i].set_facecolor(lt)
        elif center > lim:
            patches[i].set_facecolor(gt)
    
        if gray and np.abs(center) < 1.E-10:
            patches[i].set_facecolor('.75')
    return bins,patches

def setLimits(ax):
    lims = ax.get_ylim()
    y1 = np.max(np.abs(lims))
    y0 = -1.*y1
    ax.set_ylim([y0,y1])
    return ax

def year2Cycle(year):
    if 1972 <= year and year <=1980:
        return 1970
    elif 1982 <= year and year <=1990:
        return 1980
    elif 1992 <= year and year <=2000:
        return 1990
    elif 2002 <= year and year <=2010:
        return 2000
    else:
        return 2010

