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

def plotGDF(fname,gdf,projection,colorby=None,boolDict=None,colorCol=None,cmap=None,cbar=True,cmapScale=1.,title=None,linewidth=0.5,climits=None):
    if projection == "USALL":
        #use Albers equal area projection for contiguous 48, local state plane projections for HI and AK
        proj   = pyproj.Proj("+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=37.5 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs")
        projHI = pyproj.Proj("+init=EPSG:26962")
        projAK = pyproj.Proj("+init=EPSG:26935")

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
        ticklabels = ["%3.1f" % x for x in np.nditer(ticklabels)]
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
    
