import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

import numpy as np
import utlUtilities as utl
import os
import math
from scipy import stats
import copy
import us
import pandas as pd
from platypus import NSGAII,Problem,Real
from mpl_toolkits.mplot3d import Axes3D

figDir       = os.path.join("Figures","SimVsAsymptotic")

nDist = 18

def SafeAndSkew(x):
    xa = np.array(x)
    safe = len(xa[xa>=.550])
    C1,p1 = utl.unstdSkewTest(x,0.0057)
    meanDiff = np.abs(np.mean(x)-0.5)-0.005
    return [safe,p1/2.0],[meanDiff]

def Declination(x):
    x = np.array(x)
    N = float(len(x))

    demWon = x[x >=0.5]
    kd = float(len(demWon))

    repWon = 1.-x[x < 0.5]
    kr = N-kd

    tq = np.arctan((1.-2.*np.mean(repWon))/(kr/N))
    tp = np.arctan((2.*np.mean(demWon-1.))/(kd/N))
    decl = 2.*(tp-tq)/np.pi
    meanDiff = np.abs(np.mean(x)-0.5)-0.005
    return [decl],[meanDiff]

def DeclAndT2(x):
    x = np.array(x)
    N = float(len(x))

    demWon = x[x >=0.5]
    kd = float(len(demWon))

    repWon = x[x < 0.5]
    kr = N-kd

    tq = np.arctan((1.-2.*np.mean(repWon))/(kr/N))
    tp = np.arctan((2.*np.mean(demWon)-1.)/(kd/N))
    decl = 2.*(tp-tq)/np.pi

    meanDiff = np.abs(np.mean(x)-0.5)-0.005
    #return [decl,p/2.],[meanDiff]
    #return [np.mean(demWon)-np.mean(repWon),p/2.],[meanDiff]
    return decl,np.mean(demWon)-np.mean(1.-repWon)

def DeclAndT(x):
    x = np.array(x)
    N = float(len(x))

    demWon = x[x >=0.5]
    kd = float(len(demWon))

    repWon = x[x < 0.5]
    kr = N-kd

    tq = np.arctan((1.-2.*np.mean(repWon))/(kr/N))
    tp = np.arctan((2.*np.mean(demWon)-1.)/(kd/N))
    decl = 2.*(tp-tq)/np.pi

    meanDiff = np.abs(np.mean(x)-0.5)-0.005
    #return [decl,p/2.],[meanDiff]
    #return [np.mean(demWon)-np.mean(repWon),p/2.],[meanDiff]
    return [decl,np.mean(demWon)-np.mean(1.-repWon)],[meanDiff]

def MMSimple(x):
    x = np.array(x)
    demWon = x[x >=0.5]
    repWon = 1.-x[x < 0.5]
    meanDiff = np.abs(np.mean(x)-0.5)-0.005
    return [np.abs(np.mean(demWon)-np.mean(repWon))],[meanDiff]

def DenomAndT(x):
    x = np.array(x)
    demWon = x[x >=0.5]
    repWon = 1.-x[x < 0.5]
    t,p = stats.ttest_ind(demWon, repWon, equal_var = True)

    v1 = np.var(demWon, ddof=1)
    v2 = np.var(repWon, ddof=1)
    n1 = len(demWon)
    n2 = len(repWon)
    df = n1 + n2 - 2.0
    svar = ((n1 - 1) * v1 + (n2 - 1) * v2) / df
    denom = np.sqrt(svar * (1.0 / n1 + 1.0 / n2))
    
    meanDiff = np.abs(np.mean(x)-0.5)-0.005
    return [denom,p/2.0],[meanDiff,denom-0.02]#,v1-0.001,v2-0.001,p-0.05]

def sortByObj(idx,result):
    res = [(s.objectives[idx],s.variables) for s in result]
    res.sort(key=lambda x: x[0])
    return res

safeLimit = 0.550
low,upp   = 0.15,0.85

xlim = (0.495,0.505)
ylim = (0.0,0.15)

niter   = 10000

#13 of 18 safe wins{{{
nSafe = 11

fig = plt.figure()
ax = fig.add_subplot(111)


problem = Problem(nDist, 2,1)
pTypes = []
for i in range(nDist):
    if i < nSafe:
        pTypes.append(Real(safeLimit,upp))
    else:
        pTypes.append(Real(low,1.-safeLimit))
        
problem.types[:] = pTypes
#problem.function = DenomAndT
problem.function = DeclAndT
problem.directions[:] = [Problem.MINIMIZE,Problem.MINIMIZE]
#problem.directions[:] = [Problem.MINIMIZE,Problem.MAXIMIZE]
problem.constraints[:] = "<=0"
algorithm = NSGAII(problem)
algorithm.run(niter)
ax.scatter([s.objectives[0] for s in algorithm.result],
           [s.objectives[1]/0.5 for s in algorithm.result],color='r',label="Pareto Front")

fig2 = plt.figure(figsize=(8,10))
ax2  = fig2.add_subplot(111)
res = sortByObj(0,algorithm.result)
for i,s in enumerate(res):
    x = np.array(s[1])
    demWon = x[x >=0.5]
    repWon = x[x < 0.5]
    mD = np.mean(demWon)
    mR = np.mean(repWon)
    #print DenomAndT(s[1])
    print DeclAndT(s[1])
    if i == 0:
        ax2.scatter(s[1],np.ones(nDist)*i+1,color='b',label="District Vote Shares")
        ax2.plot(mD  ,i+1,color='g',label='Dem Mean',marker="+")
        ax2.plot(1.-mR  ,i+1,color='r',label='Rep Mean',marker="+")
    else:
        ax2.scatter(s[1],np.ones(nDist)*i+1,color='b')
        ax2.scatter(mD  ,i+1,color='g',marker="+")
        ax2.scatter(1.-mR  ,i+1,color='r',marker="+")
    ax2.plot(np.mean(s[1])  ,i+1,color='y',marker="+")
ax2.grid()
ax2.set_ylim((0,101))
ax2.set_xlim((0.,1.))
ax2.set_xlabel("Democratic Vote Share")
ax2.set_ylabel("Pareto Optimal Solution Number")
ax2.xaxis.set_major_locator(MaxNLocator(11))
ax2.yaxis.set_major_locator(MaxNLocator(11))

lgd = plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,ncol=3,mode="expand")
fig2.savefig(os.path.join(figDir,"solutionsT.png"), additional_artists=lgd,bbox_inches="tight")



ax.grid()
ax.set_ylabel("P-Value")
ax.set_xlabel("Stadndard Deviation of Vote Shares")
#ax.set_xlim(xlim)
#ax.set_ylim(ylim)
lgd = ax.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,ncol=3,mode="expand")
fig.savefig(os.path.join(figDir,"paretoT.png"), additional_artists=lgd,bbox_inches="tight")
#}}}

#
##for mm simple{{{
#niter   = 10000
#nSafe = [7,8,9,10,11]
#safeLimit = [0.51,0.53,0.55]
#
#fig = plt.figure()
#ax = fig.add_subplot(111)
#for sL in safeLimit:
#    ps = []
#    for ns in nSafe:
#        problem = Problem(nDist, 1,1)
#        pTypes = []
#        for i in range(nDist):
#            if i < ns:
#                pTypes.append(Real(sL,upp))
#            else:
#                pTypes.append(Real(low,sL))
#                
#        problem.types[:] = pTypes
#        problem.function = Declination
#        problem.directions[:] = [Problem.MINIMIZE]
#        problem.constraints[:] = "<=0"
#        algorithm = NSGAII(problem)
#        algorithm.run(niter)
#        
#        
#        ps.append(np.max([s.objectives[0] for s in algorithm.result]))
#    ax.plot(nSafe,ps,label="Safe Win Limit = "+str(sL))
#
#ax.grid()
#ax.set_ylabel("P-Value")
#ax.set_xlabel("Number of Safe Wins")
#lgd = ax.legend(loc=3)
#fig.savefig(os.path.join(figDir,"gamingMMS.png"), additional_artists=lgd,bbox_inches="tight")
##}}}
#

