from matplotlib.patches import Polygon
from matplotlib.colors import rgb2hex
from scipy import stats

from sklearn.model_selection import GridSearchCV
from sklearn.neighbors import KernelDensity
from sklearn import mixture

import matplotlib.pyplot as plt
import geopandas as gpd
import pandas as pd
import numpy as np
import shapely
import pyproj
import os

#Utility functions for unbury the lead projects

def html_table(lol,outFile):
    with open(outFile,"w") as f:
        f.write('<table>\n')
        for i,sublist in enumerate(lol):
            if i == 0:
                f.write('  <tr><td><strong>\n')
                f.write('    </strong></td><td><strong>'.join(sublist)+"\n")
                f.write('  </strong></td></tr>\n')
            else:
                f.write('  <tr><td>\n')
                f.write('    </td><td>'.join(sublist)+"\n")
                f.write('  </td></tr>\n')
        f.write('</table>\n')
    return

def mergeGDF(shapeFile,dataFile,on):
    gdf = gpd.read_file(shapeFile)
    #Make sure pandas reads the identifier as a string
    df  = pd.read_csv(dataFile,dtype={on: object})

    gdf = gdf.merge(df,on=on)

    #Get rid of duplicates
    dups = [x for x in gdf if x.endswith('_y')]
    if len(dups) > 0:
        gdf.drop(dups, axis=1, inplace=True)
        for col in gdf:
            if col.endswith('_x'):
                gdf.rename(columns={col:col.rstrip('_x')}, inplace=True)

    return gdf


def plotPolygon(geom,ax,proj=None,scale=None,shift=None,color='k',facecolor=None,linewidth=0.5):
    x,y = geom.exterior.xy
    if proj is not None:
        poly = [proj(*c) for c in zip(x,y)]
        x,y  = zip(*poly) 
    if scale is not None:
        x = [scale*i for i in x]
        y = [scale*i for i in y]
    if shift is not None:
        x = [shift[0]+i for i in x]
        y = [shift[1]+i for i in y]

    if facecolor is None:
        ax.plot(x,y,color=color,linewidth=linewidth)
    else:
        ax.add_patch(Polygon(zip(x,y),facecolor=facecolor,edgecolor=color,linewidth=linewidth))
    return ax
   
def plotShapely(geom,ax,proj=None,scale=None,shift=None,bbox=None,color='k',facecolor=None,linewidth=0.5,dotSize=None,dotColor=None,dotShift=None):
    if geom.geom_type == "Polygon":
        ax = plotPolygon(geom,ax,proj=proj,scale=scale,shift=shift,color=color,facecolor=facecolor,linewidth=linewidth)
    elif geom.geom_type == "MultiPolygon":
        for i,part in enumerate(geom):
            if bbox is None:
                ax = plotPolygon(part,ax,proj=proj,scale=scale,shift=shift,color=color,facecolor=facecolor,linewidth=linewidth)
            else:
                if part.intersects(bbox):
                    ax = plotPolygon(part,ax,proj=proj,scale=scale,shift=shift,color=color,facecolor=facecolor,linewidth=linewidth)
    if dotSize is not None:
        centroid = geom.centroid
        centroid = proj(centroid.x,centroid.y)
        if dotShift is not None:
            centroid = [centroid[i]+dotShift[i] for i in range(2)]
        circle = plt.Circle(centroid, dotSize, color=dotColor)
        ax.add_artist(circle)
    
    return ax

def plotGDF(fname,gdf,projection,colorby=None,boolDict=None,colorCol=None,cmap=None,cbar=True,cmapScale=1.,title=None,linewidth=0.5,climits=None,cfmt="%3.2f",dotby=None,dotCol=None,dotColor=None,dotShift=None,fig=None,ax=None,save=True,linecolor='k',lims=None,Annotate=None,AnnCoords=None):
    if projection == "USALL":
        #use Albers equal area projection for contiguous 48, local state plane projections for HI and AK
        proj   = pyproj.Proj("+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=37.5 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs")
        projHI = pyproj.Proj("+init=EPSG:26962")
        projAK = pyproj.Proj("+init=EPSG:26935")
    elif projection == "LOWER48":
        #use Albers equal area projection for contiguous 48
        proj   = pyproj.Proj("+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=37.5 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs")
    elif projection is None:
        proj = None

    # data range
    if colorby == "data":
        dmin = gdf[colorCol].min()
        dmax = gdf[colorCol].max()
        if climits is None:
            climits = (dmin,dmax)

    if fig is None:
        fig = plt.figure()
        ax  = fig.add_subplot(111)
    for index,row in gdf.iterrows():
        geom = row.geometry
        if projection == "USALL":
            if row.STATEFP == u"02": #Alaske
                scale = .35
                shift = (-1700000.,-1300000.)
                cProj = projAK
                bbox = None
                dotShift = None
            elif row.STATEFP == u"15": #Hawaii
                scale = None
                shift = (-1100000.,-1200000.)
                cProj = projHI
                bbox  = shapely.geometry.box(-161.,-151.,18.,22.)
                dotShift = None
            elif row.STATEFP == u"09": #CT
                scale = None
                shift = None
                cProj = proj
                bbox  = None
                dotShift = (0.,-1000000.)
            else:
                scale = None
                shift = None
                cProj = proj
                bbox = None
                dotShift = None
        elif projection == "LOWER48":
            scale = None
            shift = None
            cProj = proj
            bbox = None
        elif projection is None:
            scale = None
            shift = None
            cProj = None
            bbox = None

        if dotCol is not None:
            dotSize = 400.*np.sqrt(row[dotCol]/np.pi)
        else:
            dotSize = None

        if colorby is None:
            ax = plotShapely(geom,ax,proj=cProj,scale=scale,shift=shift,color=linecolor,linewidth=linewidth,dotSize=dotSize,dotColor=dotColor,dotShift=dotShift)
        elif colorby == "data":
            color = rgb2hex(cmap((row[colorCol]-climits[0])/(climits[1]-climits[0]))[:3])
            ax = plotShapely(geom,ax,proj=cProj,scale=scale,shift=shift,bbox=bbox,color=linecolor,facecolor=color,linewidth=linewidth,dotSize=dotSize,dotColor=dotColor,dotShift=dotShift)
        elif colorby == "boolDict":
            color = boolDict["default"]
            for column,trueColor in boolDict["conditions"].iteritems():
                if row[column]:
                    color = trueColor
            ax = plotShapely(geom,ax,proj=cProj,scale=scale,shift=shift,bbox=bbox,color=linecolor,facecolor=color,linewidth=linewidth,dotSize=dotSize,dotColor=dotColor,dotShift=dotShift)

            

    ax.set_aspect("equal")
    ax.axis("off")
    if lims is None:
        ax.autoscale_view()
    else:
        ax.set_xlim(lims[0])
        ax.set_ylim(lims[1])

    if Annotate is not None:
        x1,x2 = ax.get_xlim()
        y1,y2 = ax.get_ylim()
        yd = y2-y1
        xd = x2-x1
        trans = ax.get_yaxis_transform()
        for index,row in gdf.iterrows():
            if (row[colorCol]-climits[0])/(climits[1]-climits[0]) < 0.25:
                color = rgb2hex(cmap(0.9)[:3])
            else:
                color = 'w'
            color = 'k'
            ax.annotate(s=str(index+1), xy=row[AnnCoords],horizontalalignment='center',color=color)
            ax.annotate(s=str(index+1)+" - "+row[Annotate], xy=(0.98,y2),xycoords=trans,horizontalalignment='left',color='k', annotation_clip=False)
            y2 = y2 - yd/float(len(gdf))


    
    if cmap is not None and cbar:
        ncolors = 10.
        mappable = plt.cm.ScalarMappable(cmap=cmap)
        mappable.set_array([])
        mappable.set_clim(0.0, ncolors)
        llim = climits[0]*cmapScale
        ulim = climits[1]*cmapScale
        ticklabels = np.linspace(llim,ulim,ncolors)
        colorbar = fig.colorbar(mappable,orientation='horizontal',shrink=0.7,pad=0.)
        colorbar.set_ticks(np.linspace(0, ncolors, ncolors))
        ticklabels = [cfmt % x for x in np.nditer(ticklabels)]
        if llim > dmin*cmapScale:
            ticklabels[0] += "-"
        if ulim < dmax*cmapScale:
            ticklabels[-1] += "+"
        colorbar.set_ticklabels(ticklabels)

    #Set title
    if title is not None:ax.set_title(title)
    
    if save:
        fig.savefig(fname)
        plt.close()
    return fig,ax
#Compute efficiency gap
def getEfficiencyGap(df):
    demWinnersIdx = df[df['dem_votes'] > df['rep_votes']].index.tolist()
    repWinnersIdx = df[df['dem_votes'] < df['rep_votes']].index.tolist()

    dem_votes   = np.sum(df.dem_votes.values)
    rep_votes   = np.sum(df.rep_votes.values)
    total_votes   = np.sum(df.dem_votes.values)+np.sum(df.rep_votes.values)
    total_votesEV = np.sum(df.votes_total.values*df.electoral_votes.values)
    #Wasted votes are votes for the losing party in a state, as well as votes beyond what was neccesary for the state win
    demWasted = np.sum(df.dem_votes.values[repWinnersIdx]) + np.sum(df.dem_votes.values[demWinnersIdx]-df.rep_votes.values[demWinnersIdx]-1)
    repWasted = np.sum(df.rep_votes.values[demWinnersIdx]) + np.sum(df.rep_votes.values[repWinnersIdx]-df.dem_votes.values[repWinnersIdx]-1)
    EG = 100.*float(demWasted-repWasted)/float(total_votes)
    
    demWastedEV = np.sum(df.dem_votes.values[repWinnersIdx]*df.electoral_votes.values[repWinnersIdx]) + np.sum((df.dem_votes.values[demWinnersIdx]-df.rep_votes.values[demWinnersIdx]-1)*df.electoral_votes.values[demWinnersIdx])
    repWastedEV = np.sum(df.rep_votes.values[demWinnersIdx]*df.electoral_votes.values[demWinnersIdx]) + np.sum((df.rep_votes.values[repWinnersIdx]-df.dem_votes.values[repWinnersIdx]-1)*df.electoral_votes.values[repWinnersIdx])
    EGEV = 100.*float(demWastedEV-repWastedEV)/float(total_votesEV)

    demVotePct  = 100.*np.sum(df.dem_votes.values)/float(total_votes)
    demStatePct = 100.*float(len(demWinnersIdx))/51.
    demEVotePct = 100.*float(np.sum(df.electoral_votes.values[demWinnersIdx]))/538.
    return demWasted,repWasted,EG,EGEV,demVotePct,demStatePct,demEVotePct

#Compute votes Evotes
def getVotesEvotesCurve(df,swingRange,n):
    #get original vote percentages
    increment = df.dem_votes.values*swingRange/float(n)
    
    #start at lower end
    df["dem_votes"] -= increment*n
    df["rep_votes"] += increment*n
    demWinnersIdx = df[df['dem_votes'] > df['rep_votes']].index.tolist()
    total_votes   = np.sum(df.dem_votes.values)+np.sum(df.rep_votes.values)
    demVoteFrac   = np.sum(df.dem_votes.values)/float(total_votes)
    demVotes  = [demVoteFrac]
    demEVotes = [float(np.sum(df.electoral_votes.values[demWinnersIdx]))/538.]
    for i in range(2*n):
        df["dem_votes"] += increment
        df["rep_votes"] -= increment
        total_votes   = np.sum(df.dem_votes.values)+np.sum(df.rep_votes.values)
        demVoteFrac   = np.sum(df.dem_votes.values)/float(total_votes)
        demVotes.append(demVoteFrac)
        demWinnersIdx = df[df['dem_votes'] > df['rep_votes']].index.tolist()
        demEVotes.append(float(np.sum(df.electoral_votes.values[demWinnersIdx]))/538.)

    #return as percentage
    demVotes = np.array(demVotes)*100.
    demEVotes = np.array(demEVotes)*100.

    return demVotes,demEVotes

def getSVAsymmetry(V,S):
    #Find excess seats at 50% vote
    idx = np.argmin(np.abs(V-50.))
    needInterp = True
    if V[idx] < 50.:
        idx1 = idx
        idx2 = idx+1
    elif V[idx] >50.:
        idx1 = idx-1
        idx2 = idx
    else:
        needInterp = False

    if needInterp:
        excessAt50 = S[idx1] + (50.-V[idx1])*(S[idx2]-S[idx1])/(V[idx2]-V[idx1])
    else:
        excessAt50 = S[idx]


    #Find votes needed for a majority of seats
    idx = np.argmin(np.abs(S-50.))
    needInterp = True
    if S[idx] < 50.:
        idx1 = idx
        idx2 = idx+1
    elif S[idx] >50.:
        idx1 = idx-1
        idx2 = idx
    else:
        needInterp = False

    if needInterp:
        votesForMaj = V[idx1] + (50.-S[idx1])*(V[idx2]-V[idx1])/(S[idx2]-S[idx1])
    else:
        votesForMaj = V[idx]

    return excessAt50,votesForMaj
    
def asymTestAD(x):
    if len(x) < 3:
        return 0.,1.
    mean = np.mean(x)
    #reflect data around the mean
    xref = 2.*mean-x
    AD,C,p = stats.anderson_ksamp((x,xref))
    return AD,p

def asymTestKS(x):
    if len(x) < 3:
        return 0.,1.
    mean = np.mean(x)
    #reflect data around the mean
    xref = 2.*mean-x
    return stats.ks_2samp(x,xref)

def lopsidedWinsTest(demPct,repPct):
    demWon = demPct[demPct > repPct]
    repWon = repPct[repPct > demPct]
    if len(demWon) < 2 or len(repWon) < 2:
        return demWon,repWon,0.,0.,True

    t,p = stats.ttest_ind(demWon, repWon, equal_var = False)
    #Get one sided p value
    p = p/2.
    winDiff = np.mean(demWon) - np.mean(repWon)
    return demWon,repWon,winDiff,p,False

def getWinMargins(df,demColumn,repColumn,state=None):
    if state is not None:
        df = df[df["CD"].str.contains(state)]

    demWon = df[df[demColumn] > df[repColumn]][demColumn].tolist()
    repWon = df[df[repColumn] > df[demColumn]][repColumn].tolist()
    return demWon,repWon

def MADSkewTest(x):
    n = float(len(x))
    if n < 3.: return 0.,1.
    X = np.mean(x)
    M = np.median(x)
    MAD = 1.4826*np.median(np.abs(x-M))
    C = (X-M)/MAD
    p = 2.*(1.-stats.norm.cdf(np.abs(C)*np.sqrt(n/0.5708)))

    return C,p

def IQRSkewTest(x):
    n = float(len(x))
    X = np.mean(x)
    M = np.median(x)
    q75, q25 = np.percentile(x, [75 ,25])
    iqr = q75 - q25
    C = (X-M)/iqr

    return C

def unstdSkewTest(x,var):
    n = float(len(x))
    if n < 3.: return 0.,1.
    X = np.mean(x)
    M = np.median(x)
    C = X-M
    p = 2.*(1.-stats.norm.cdf(np.abs(C)*np.sqrt(n/var)))

    return C,p

def cabilioSkewTest(x):
    n = float(len(x))
    if n < 3.: return 0.,1.
    X = np.mean(x)
    M = np.median(x)
    s = np.std(x,ddof=1)
    C = (X-M)/s
    p = 2.*(1.-stats.norm.cdf(np.abs(C)*np.sqrt(n/0.5708)))

    return C,p

def miaoSkewTest(x):
    n = float(len(x))
    X = np.mean(x)
    M = np.median(x)
    J = np.sqrt(np.pi/2.)*np.mean(np.abs(x-M))
    T = (X-M)/J
    p = 2.*(1.-stats.norm.cdf(np.abs(T)*np.sqrt(n/0.5708)))

    return T,p

def specificAsym(x):
    n = len(x)
    if n < 3: return 0
    Votes = np.mean(x)
    Seats = len(x[x>.5])
    if Votes > .5:
        SeatsFlipped = len(x[x>2.*Votes-.5])
    else:
        SeatsFlipped = len(x[x<2.*Votes-.5])

    return Seats-SeatsFlipped

def vertAsymSigned(x):
    n = float(len(x))
    if n < 3.: return 0.
    X = np.mean(x)
    nOver = float(len(x[x>X]))/n
    return 0.5-nOver

def vertAsym(x):
    n = float(len(x))
    if n < 3.: return 0.
    X = np.mean(x)
    nOver = float(len(x[x>X]))/n
    return np.abs(0.5-nOver)

def dispersionTest(x):
    n   = float(len(x))
    q75, q25 = np.percentile(x, [75 ,25])
    iqr = q75 - q25
    s   = np.std(x,ddof=1)
    q = iqr/s-1.349
    p = 2*(1.-stats.norm.cdf(np.sqrt(n)*np.abs(q),scale=np.sqrt(1.566)))
    return q,p

def safeWinsTestSafe(x):
    n = len(x)
    if n == 1: return 0.,1.
    q,p = dispersionTest(x)
    #Get one sided p value
    p = p/2.

    return q,p

def twoSidedFromSim(sim,s):
    p = float(len(sim[sim<=-np.abs(s)]))/float(len(sim))
    p+= float(len(sim[sim>np.abs(s)]))/float(len(sim))
    return p

def mmDiffSD(x,sim=None):
    n = len(x)
    if n < 3: return 0.,1.,0.,1.
    
    C1,p = cabilioSkewTest(x)
    if sim is None: sim = np.loadtxt(os.path.join("/Users/Christina/Desktop/UTL/Utilities/SAST",str(n)+"skewSD.txt"))
    p1 = twoSidedFromSim(sim,C1)

    return C1,p1

def mmDiffMAD(x,sim=None):
    n = len(x)
    if n < 3: return 0.,1.
    
    C   = MADSkewTest(x)
    if sim is None: sim = np.loadtxt(os.path.join("/Users/Christina/Desktop/UTL/Utilities/SAST",str(n)+"skewMAD.txt"))
    p = twoSidedFromSim(sim,C)

    return C,p

def mmDiffIQR(x,sim=None):
    n = len(x)
    if n < 3: return 0.,1.,0.,1.
    
    C2   = IQRSkewTest(x)
    if sim is None: sim = np.loadtxt(os.path.join("/Users/Christina/Desktop/UTL/Utilities/SAST",str(n)+"skewIQR.txt"))
    p2 = twoSidedFromSim(sim,C2)

    return C2,p2

def dispersionMAD(x):
    n = len(x)
    if n < 3: return 0.
    
    M = np.median(x)
    MAD = 1.4826*np.median(np.abs(x-M))
    s   = np.std(x,ddof=1)

    M   = s/MAD-1.

    return M

def dispersionMNum(x,sim=None):
    n = len(x)
    if n < 3: return 0.,1.
    
    M = np.median(x)
    MAD = 1.4826*np.median(np.abs(x-M))
    s   = np.std(x,ddof=1)

    M   = s/MAD-1.
    if sim is None: sim = np.loadtxt(os.path.join("/Users/Christina/Desktop/UTL/Utilities/SAST",str(n)+"dispM.txt"))
    p3 = twoSidedFromSim(sim,M)

    return M,p3

def dispersionRNum(x,sim=None):
    n = len(x)
    if n < 3: return 0.,1.
    
    X = np.mean(x)
    M = np.median(x)
    J = np.sqrt(np.pi/2.)*np.mean(np.abs(x-M))
    s   = np.std(x,ddof=1)

    R   = s/J-1.
    if sim is None: sim = np.loadtxt(os.path.join("/Users/Christina/Desktop/UTL/Utilities/SAST",str(n)+"dispJ.txt"))
    p3 = twoSidedFromSim(sim,R)

    return R,p3

def dispersionNum(x,sim=None):
    n = len(x)
    if n < 3: return 0.,1.
    
    q,p = dispersionTest(x)
    if sim is None: sim = np.loadtxt(os.path.join("/Users/Christina/Desktop/UTL/Utilities/SAST",str(n)+"disp.txt"))
    p3 = twoSidedFromSim(sim,q)

    return q,p3


def sastOmni(x,sim=None):
    n = len(x)
    if n < 3: return 0.,1.
    
    mmd = np.mean(x) - np.median(x)
    C1,p = cabilioSkewTest(x)
    q,p = dispersionTest(x)
    if sim is None: sim = np.loadtxt(os.path.join("/Users/Christina/Desktop/UTL/Utilities/SAST",str(n)+"SASTomni.txt"))
    ss = C1**2+q**2
    p = twoSidedFromSim(sim,ss)

    return ss,p

def mmDiffCompare(x,sim1=None,sim2=None,sim3=None):
    n = len(x)
    if n < 3: return 0.,1.,0.,1.
    
    mmd = np.mean(x) - np.median(x)
    C1,p = cabilioSkewTest(x)
    C2   = IQRSkewTest(x)
    q,p = dispersionTest(x)
    if sim1 is None: sim1 = np.loadtxt(os.path.join("/Users/Christina/Desktop/UTL/Utilities/SAST",str(n)+"skewSD.txt"))
    if sim2 is None: sim2 = np.loadtxt(os.path.join("/Users/Christina/Desktop/UTL/Utilities/SAST",str(n)+"skewIQR.txt"))
    if sim3 is None: sim3 = np.loadtxt(os.path.join("/Users/Christina/Desktop/UTL/Utilities/SAST",str(n)+"disp.txt"))
    p1 = twoSidedFromSim(sim1,C1)
    p2 = twoSidedFromSim(sim2,C2)
    p3 = twoSidedFromSim(sim3,q)

    return C1,p1,C2,p2,q,p3

def safeWinsTestSwing(x):
    n = len(x)
    if n == 1: return 0.,1.
    
    mmd = np.mean(x) - np.median(x)
    C,p = cabilioSkewTest(x)
    #Get one sided p value
    p = p/2.
    return C,p

def getCDshorth(x):
    X = np.mean(x)
    M = np.median(x)
    s = np.std(x,ddof=1)
    C = (X-M)/s

    shorth,mShorth = getShorth(x)
    D = shorth/s-1.349
    return C,D

def getCD(x):
    X = np.mean(x)
    M = np.median(x)
    s = np.std(x,ddof=1)
    C = (X-M)/s

    q75, q25 = np.percentile(x, [75 ,25])
    iqr = q75 - q25
    D = iqr/s-1.349
    return C,D

def SASTshorth(x):
    n = len(x)
    if len(x) < 3: return 1.
    sim = np.loadtxt(os.path.join("/Users/Christina/Desktop/UTL/Utilities/SAST",str(n)+"SASTshorth.txt"))
    C,D = getCDshorth(x)
    if C >= 0. and D >= 0.:
        #idx = sim[:,0] >= C
        idx = (sim[:,0] >= C) & (sim[:,1] >= D)
        #idx = sim[:,1] >= D
    elif C >= 0. and D < 0.:
        #idx = sim[:,0] >= C
        idx = (sim[:,0] >= C) & (sim[:,1] <= D)
        #idx = sim[:,1] <= D
    elif C < 0. and D < 0.:
        #idx = sim[:,0] <= C
        idx = (sim[:,0] <= C) & (sim[:,1] <= D)
        #idx = sim[:,1] <= D
    elif C < 0. and D >= 0.:
        #idx = sim[:,0] <= C
        idx = (sim[:,0] <= C) & (sim[:,1] >= D)
        #idx = sim[:,1] >= D

    N    = float(len(sim[:,0]))
    prob = float(len(sim[idx,0]))/N
    return prob
        
def SAST(x,sim=None):
    n = len(x)
    if len(x) < 5: return 1.
    if sim is None:sim = np.loadtxt(os.path.join("/Users/Christina/Desktop/UTL/Utilities/SAST",str(n)+".txt"))
    C,D = getCD(x)
    if C >= 0. and D >= 0.:
        #idx = sim[:,0] >= C
        idx = (sim[:,0] >= C) & (sim[:,1] >= D)
        #idx = sim[:,1] >= D
    elif C >= 0. and D < 0.:
        #idx = sim[:,0] >= C
        idx = (sim[:,0] >= C) & (sim[:,1] <= D)
        #idx = sim[:,1] <= D
    elif C < 0. and D < 0.:
        #idx = sim[:,0] <= C
        idx = (sim[:,0] <= C) & (sim[:,1] <= D)
        #idx = sim[:,1] <= D
    elif C < 0. and D >= 0.:
        #idx = sim[:,0] <= C
        idx = (sim[:,0] <= C) & (sim[:,1] >= D)
        #idx = sim[:,1] >= D

    N    = float(len(sim[:,0]))
    prob = float(len(sim[idx,0]))/N
    return prob
        
def getShorth(x):
    n = len(x)
    nShorth = int(round(float(n)/2.))
    shorth = np.abs(np.max(x) - np.min(x))
    sIdx   = 0
    x = np.sort(x)
    for i in range(n-nShorth+1):
        cRange = np.abs(x[i+nShorth-1] - x[i])
        if cRange < shorth:
            shorth = cRange
            sIdx   = i

    mShorth = np.mean(x[sIdx:sIdx+nShorth])
    return shorth,mShorth

def shorthTest(x):
    if len(x) < 3: return 0.,1.
    shorth,mShorth = getShorth(x)
    s = np.std(x,ddof=1)
    D = shorth/s-1.349
    n = len(x)
    sim = np.loadtxt(os.path.join("/Users/Christina/Desktop/UTL/Utilities/SAST/"+str(n)+"shorth.txt"))
    if D <= 0.:
        p = float(len(sim[sim<=D]))/float(len(sim))
    else:
        p = float(len(sim[sim>=D]))/float(len(sim))
    return D,p


def get2PartySeatShare(demPct,repPct):
    demWon = demPct[demPct > repPct]
    repWon = repPct[repPct > demPct]
    demFrac = float(len(demWon))/float(len(demPct))
    return demFrac

def get2PartyVoteShare(df,state):
    idx = df[df["state_abbr"] == state].index.tolist()
    if len(idx) == 1:
        dem = df.dem_votes.values[idx[0]]
        rep = df.rep_votes.values[idx[0]]
        demFrac = float(dem)/float(dem+rep)
    else:
        demFrac = 0.
    
    return demFrac

def gmmSimple(model,x):
    p = np.zeros((len(x)))
    for w,m,s in model:
        p += w*stats.norm.pdf(x,loc=m,scale=s)
    return p


def getGMMLikelihood(model,x):
    p = gmmSimple(model,x)
    l = np.sum(np.log(p))
    return l

def estFromWins(x):
    #estimate single component model
    weights1 = [1.]
    means1 = [np.mean(x)]
    stdvs1 = [np.std(x)]
    model1 = zip(weights1,means1,stdvs1)
    #estimate two component model
    wins = x[x >= 50.]
    loss = x[x < 50.]
    if len(wins) > 2 and len(loss) > 2:
        wMean = np.mean(wins)
        lMean = np.mean(loss)
        means2 = [wMean,lMean]
        wStd  = np.std(wins)
        lStd  = np.std(loss)
        stdvs2 = [wStd,lStd]
        wWeight = float(len(wins))/float(len(x))
        lWeight = float(len(loss))/float(len(x))
        weights2 = [wWeight,lWeight]
        model2 = zip(weights2,means2,stdvs2)
    else:
        model2 = None
    return model1,model2

def getAICw(AIC):
    AIC = np.array(AIC)
    minAIC = np.min(AIC)
    delAIC = AIC-minAIC
    AICw = np.exp(-0.5*delAIC) 
    AICw = AICw/np.sum(AICw)
    return AICw

def gmmAPriori(x):
    #estimate parameters
    model1,model2 = estFromWins(x)
    if model2 is None:
        l1 = getGMMLikelihood(model1,x)
        AIC = [4.-2.*l1]
        return [model1],AIC
    else:
        l1 = getGMMLikelihood(model1,x)
        l2 = getGMMLikelihood(model2,x)
        AIC = [4.-2.*l1,10.-2.*l2]
        return [model1,model2],AIC

def gaussianMixture(samples,NCOMP):
    models = []
    for ncomp in NCOMP:
        gmix = mixture.GaussianMixture(n_components=ncomp, covariance_type='full')
        gmix.fit(samples)
        #If a mixture component has a very small covariance it might be the result of a singularity
        if np.all(gmix.covariances_ > 1.0E-6):
            models.append(gmix)
    AIC    = [m.aic(samples) for m in models]
    return models,AIC

def bayesianGaussianMixture(samples,NCOMP):
    models = []
    for ncomp in NCOMP:
        gmix = mixture.BayesianGaussianMixture(n_components=ncomp, covariance_type='full')
        models.append(gmix.fit(samples))
    return models

def fit_kde(x,numBandwidth=40,hmin=0.1,hmax=1.0):
    grid = GridSearchCV(KernelDensity(),{'bandwidth': np.linspace(hmin, hmax, numBandwidth)},cv=20) # 20-fold cross-validation
    grid.fit(x[:, None])
    print grid.best_params_
    return grid.best_estimator_
