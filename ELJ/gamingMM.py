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

def Skew(x):
    C1,p1 = utl.unstdSkewTest(x,0.0057)
    meanDiff = np.abs(np.mean(x)-0.5)-0.005
    return [p1/2.0],[meanDiff]

def SDAndSkewSD(x):
    sd = np.std(x,ddof=1)
    C1,p1 = utl.cabilioSkewTest(x)
    meanDiff = np.abs(np.mean(x)-0.5)-0.005
    return [sd,p1/2.0],[meanDiff]

def sortByObj(idx,result):
    res = [(s.objectives[idx],s.variables) for s in result]
    res.sort(key=lambda x: x[0])
    return res

safeLimit = 0.550
low,upp   = 0.15,0.85

xlim = (0.495,0.505)
ylim = (0.0,0.15)

niter   = 100000

#14 of 18 safe wins{{{
nSafe = 14

fig = plt.figure()
ax = fig.add_subplot(111)


problem = Problem(nDist, 2,1)
pTypes = []
for i in range(nDist):
    if i < nSafe:
        pTypes.append(Real(safeLimit,upp))
    else:
        pTypes.append(Real(low,safeLimit))
        
problem.types[:] = pTypes
problem.function = SDAndSkewSD
problem.directions[:] = [Problem.MINIMIZE,Problem.MAXIMIZE]
problem.constraints[:] = "<=0"
algorithm = NSGAII(problem)
algorithm.run(niter)
ax.scatter([s.objectives[0] for s in algorithm.result],
           [s.objectives[1] for s in algorithm.result],color='r',label="Pareto Front")

fig2 = plt.figure(figsize=(8,10))
ax2  = fig2.add_subplot(111)
res = sortByObj(0,algorithm.result)
for i,s in enumerate(res):
    if i == 0:
        ax2.scatter(s[1],np.ones(nDist)*i+1,color='b',label="District Vote Shares")
        ax2.plot(np.mean(s[1])  ,i+1,color='g',label='Mean',marker="+")
        ax2.plot(np.median(s[1]),i+1,color='r',label='Median',marker="+")
    else:
        ax2.scatter(s[1],np.ones(nDist)*i+1,color='b')
        ax2.scatter(np.mean(s[1])  ,i+1,color='g',marker="+")
        ax2.scatter(np.median(s[1]),i+1,color='r',marker="+")
ax2.grid()
ax2.set_ylim((0,101))
ax2.set_xlim((0.,1.))
ax2.set_xlabel("Democratic Vote Share")
ax2.set_ylabel("Pareto Optimal Solution Number")
ax2.xaxis.set_major_locator(MaxNLocator(11))
ax2.yaxis.set_major_locator(MaxNLocator(11))

lgd = plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,ncol=3,mode="expand")
fig2.savefig(os.path.join(figDir,"solutions.png"), additional_artists=lgd,bbox_inches="tight")



ax.grid()
ax.set_ylabel("P-Value")
ax.set_xlabel("Stadndard Deviation of Vote Shares")
#ax.set_xlim(xlim)
#ax.set_ylim(ylim)
lgd = ax.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,ncol=3,mode="expand")
fig.savefig(os.path.join(figDir,"pareto.png"), additional_artists=lgd,bbox_inches="tight")
#}}}


#for Cu{{{
niter   = 5000
nSafe = [7,8,9,10,11]
safeLimit = [0.51,0.53,0.55]

fig = plt.figure()
ax = fig.add_subplot(111)
for sL in safeLimit:
    ps = []
    for ns in nSafe:
        problem = Problem(nDist, 1,1)
        pTypes = []
        for i in range(nDist):
            if i < ns:
                pTypes.append(Real(sL,upp))
            else:
                pTypes.append(Real(low,sL))
                
        problem.types[:] = pTypes
        problem.function = Skew
        problem.directions[:] = [Problem.MAXIMIZE]
        problem.constraints[:] = "<=0"
        algorithm = NSGAII(problem)
        algorithm.run(niter)
        
        
        ps.append(np.max([s.objectives[0] for s in algorithm.result]))
    ax.plot(nSafe,ps,label="Safe Win Limit = "+str(sL))

ax.grid()
ax.set_ylabel("P-Value")
ax.set_xlabel("Number of Safe Wins")
ax.set_ylim((0.,0.6))
lgd = ax.legend(loc=3)
fig.savefig(os.path.join(figDir,"gamingCu.png"), additional_artists=lgd,bbox_inches="tight")
#}}}

