from matplotlib.patches import Polygon
from matplotlib.colors import rgb2hex

import matplotlib.pyplot as plt
import geopandas as gpd
import pandas as pd
import numpy as np
import shapely
import pyproj

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
   
def plotShapely(geom,ax,proj=None,scale=None,shift=None,bbox=None,color='k',facecolor=None,linewidth=0.5):
    if geom.geom_type == "Polygon":
        ax = plotPolygon(geom,ax,proj=proj,scale=scale,shift=shift,color=color,facecolor=facecolor,linewidth=linewidth)
    elif geom.geom_type == "MultiPolygon":
        for i,part in enumerate(geom):
            if bbox is None:
                ax = plotPolygon(part,ax,proj=proj,scale=scale,shift=shift,color=color,facecolor=facecolor,linewidth=linewidth)
            else:
                if part.intersects(bbox):
                    ax = plotPolygon(part,ax,proj=proj,scale=scale,shift=shift,color=color,facecolor=facecolor,linewidth=linewidth)
    
    return ax

def plotGDF(fname,gdf,projection,colorby=None,boolDict=None,colorCol=None,cmap=None,cbar=True,cmapScale=1.,title=None,linewidth=0.5,climits=None,cfmt="%3.1f"):
    if projection == "USALL":
        #use Albers equal area projection for contiguous 48, local state plane projections for HI and AK
        proj   = pyproj.Proj("+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=37.5 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs")
        projHI = pyproj.Proj("+init=EPSG:26962")
        projAK = pyproj.Proj("+init=EPSG:26935")
    elif projection == "LOWER48":
        #use Albers equal area projection for contiguous 48
        proj   = pyproj.Proj("+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=37.5 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs")

    # data range
    if colorby == "data":
        dmin = gdf[colorCol].min()
        dmax = gdf[colorCol].max()
        if climits is None:
            climits = (dmin,dmax)

    fig = plt.figure()
    ax  = fig.add_subplot(111)
    for index,row in gdf.iterrows():
        geom = row.geometry
        if projection == "USALL":
            if row.STATEFP == u"02":
                scale = .35
                shift = (-1700000.,-1300000.)
                cProj = projAK
                bbox = None
            elif row.STATEFP == u"15":
                scale = None
                shift = (-1100000.,-1200000.)
                cProj = projHI
                bbox  = shapely.geometry.box(-161.,-151.,18.,22.)
            else:
                scale = None
                shift = None
                cProj = proj
                bbox = None
        elif projection == "LOWER48":
            scale = None
            shift = None
            cProj = proj
            bbox = None

        if colorby is None:
            ax = plotShapely(geom,ax,proj=cProj,scale=scale,shift=shift,onlyIdx=onlyIdx,color='k',linewidth=linewidth)
        elif colorby == "data":
            color = rgb2hex(cmap((row[colorCol]-climits[0])/(climits[1]-climits[0]))[:3])
            ax = plotShapely(geom,ax,proj=cProj,scale=scale,shift=shift,bbox=bbox,color='k',facecolor=color,linewidth=linewidth)
        elif colorby == "boolDict":
            color = boolDict["default"]
            for column,trueColor in boolDict["conditions"].iteritems():
                if row[column]:
                    color = trueColor
            ax = plotShapely(geom,ax,proj=cProj,scale=scale,shift=shift,bbox=bbox,color='k',facecolor=color,linewidth=linewidth)

            

    ax.set_aspect("equal")
    ax.axis("off")
    ax.autoscale_view()
    
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
    
    fig.savefig(fname)
    plt.close()
    return
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
    
