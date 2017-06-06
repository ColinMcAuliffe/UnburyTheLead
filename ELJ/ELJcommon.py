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

def get_asymFromPct(demPct):
    #popular vote is last element in demPct
    popVote   = demPct[-1]
    dem  = np.array(demPct[0:-1])
    actSeats = float(len(dem[dem<0.5]))
    if len(dem) > 1:
        rep     = 1.0-dem
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

def getExpMMandT(params,nsims=10000):
    #simulate
    results = []
    for a,b in params:
        results.append(np.random.beta(a,b,size=nsims))
    results = np.array(results)
    mean    = np.mean(results,axis=0)
    median  = np.median(results,axis=0)
    t       = np.apply_along_axis(getMeanMeanDiff,0,results)
    return mean-median,t

def getExpAsym(params,nsims=10000):
    #simulate
    results = []
    for a,b in params:
        results.append(np.random.beta(a,b,size=nsims))
    results = np.array(results)
    asym    = np.apply_along_axis(get_asymFromPct,0,results)
    return asym

def varWithShrinkage(x,shrinkVar):
    N = float(len(x))
    if N == 0.: return shrinkVar
    mean = np.mean(x)
    var = (N*np.sum((x - mean)**2)/(N+1.)+shrinkVar)/(N+1.)
    return var

def betaMOM(x,shrinkage=None):
    if shrinkage is None:
        var = np.var(x,ddof=1)
    else:
        var = varWithShrinkage(x,shrinkage)
    mean = np.mean(x)
    c = mean*(1.-mean)/var-1.
    alpha = mean*c
    beta  = (1.-mean)*c
    return alpha,beta

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
