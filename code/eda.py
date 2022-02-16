#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 13 20:41:54 2022

@author: charlie
"""
# %%
import netCDF4 as nc
import numpy as np
import numpy.ma as ma
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import utm
from matplotlib import animation
from mpl_toolkits.basemap import Basemap
import math


# %%
fn = "/home/charlie/Documents/Uni/Exeter - Data Science/MTHM604_Tackling_Sustainability_Challenges/MTHM604_week_2/data/rawData/TIGER_Model_2019-11/flow/output/TIGER_map.nc"
ds = nc.Dataset(fn)

#%% Functions

def CleanData(dataset, time, area, groupAmount = False):
    
    """
    Returns a dataframe that includes the variables that were extraced from the
    netCDF file
    
    Arguments:
        dataset:
        time:
        area:
        groupAmount:
    
    """
    
    
    
    def MakeDfFromMA(variable):
        df1 = dataset[variable][:]
        df1 = np.ma.getdata(df1)
        df1 = pd.DataFrame(df1)
        return df1

    variables = ['mesh2d_waterdepth', 'mesh2d_face_x', 'mesh2d_face_y', 'mesh2d_ucx', 'mesh2d_ucy', 'mesh2d_ucmag']

    count = 0
    for i in variables:
        if count == 0:
            if i in ['time', 'mesh2d_face_x', 'mesh2d_face_y']:
                df = MakeDfFromMA(i)
            else:
                df = pd.DataFrame(np.ma.masked_values(ds[i][time], -999).data)
            count += 1
        else:
            if i in ['time', 'mesh2d_face_x', 'mesh2d_face_y']:
                df2 = MakeDfFromMA(i)
                df = pd.concat([df, df2], axis = 1)
            else:
                df2 = pd.DataFrame(np.ma.masked_values(ds[i][time], -999).data)
                df = pd.concat([df, df2], axis = 1)
            count += 1
    df.columns = [variables]
    df['mesh2d_waterdepth'] = -1*df['mesh2d_waterdepth']
    df.columns = ['depth', 'locX', 'locY', 'velX', 'velY', 'mag']
    df = df[df['depth'] > -200]
    df = df[(df['locX'] >= area['easting0']) & (df['locX'] <= area['easting1']) & (df['locY'] >= area['northing0']) & (df['locY'] <= area['northing1'])]
    if groupAmount:
        df['locXgroup'] = df['locX'].apply(lambda x: round(x, -groupAmount))
        df['locYgroup'] = df['locY'].apply(lambda x: round(x, -groupAmount))
        df = df.groupby(by = ['locXgroup', 'locYgroup'], as_index = False).mean()
    
    df['lat'] = df.apply(lambda x: utm.to_latlon(x['locX'], x['locY'], 30, 'N')[0], axis = 1)
    df['lon'] = df.apply(lambda x: utm.to_latlon(x['locX'], x['locY'], 30, 'N')[1], axis = 1)
    df.drop(columns = ['locX', 'locY'], inplace = True)
    return df

def CalcVelocity(data, depthOfInterest = 2, powerLaw = 1/10, bottomRoughnessCoef = 0.32):
    data['velXseabed'] = pow(((data['depth']/depthOfInterest)/bottomRoughnessCoef*data['depth']), (powerLaw))*data['velX']
    data['velYseabed'] = pow(((data['depth']/depthOfInterest)/bottomRoughnessCoef*data['depth']), (powerLaw))*data['velY']
    data['magSeabed'] = data.apply(lambda x: math.sqrt(pow(x['velXseabed'], 2) + pow(x['velYseabed'], 2)), axis = 1)
    data.drop(columns = ['velX', 'velY', 'mag'], inplace = True)
    return data

# 2D Velocity and depth map

def Plot2dVectorField(area, data, depth = True, flow = True, mapRes = 'i', numArrows = 3):
    plt.clf()
    fig = plt.gcf()
    fig.set_size_inches(10, 10)
    
    x = data['lon']
    y = data['lat']
    z = data['depth']
    
    
    lat0, lon0 = y.min(), x.min()
    lat1, lon1 = y.max(), x.max()

    m = Basemap(projection='merc',
                llcrnrlon = lon0, urcrnrlon = lon1,
                llcrnrlat = lat0, urcrnrlat = lat1,
                resolution = mapRes)
    m.fillcontinents(color = 'darkgrey')
    m.drawcoastlines(color = 'black', linewidth=0.2)
    x2, y2 = m(x.tolist(), y.tolist())  # transform coordinates
    
    if depth:
        plt.scatter(x2,
                    y2, 
                    c=z,
                    s=30,
                    alpha = 0.2,
                    cmap="mako",
                    marker = 'o',
                    edgecolors = 'none')
        
        
    X,Y,U,V,C = (x, y, data['velXseabed'], data['velYseabed'], data['magSeabed'])
    X2, Y2 = m(X.tolist(), Y.tolist())
    
    # numArrows selects how many arrows to render, 1 = all, 3 = every third arrow etc
    if flow:

        plt.quiver(X2[::numArrows], Y2[::numArrows], U[::numArrows], V[::numArrows], C[::numArrows],
            units='inches', 
            cmap = 'twilight', 
            alpha = 0.7,
            scale_units = 'xy',
            width = 0.02,
            headwidth = 3,
            headlength = 3,
            headaxislength = 3,
            minlength = 0.001
            )
    m.colorbar()
    m.arcgisimage(service='ESRI_Imagery_World_2D', xpixels = 1500, verbose= True)
    return fig

def CreateImageStack(area,  ncFileLocation, timeRange = [5, 15], powerLaw = 1/10, depthOfInterest = 2, bottomRoughnessCoef = 0.32, depth = False, flow = True, mapRes = 'i', numArrows = 10, groupAmount = 2):
    area = area

    listDf = []
    x = input("Is this the final render? (y/n)")
    if x.lower() == 'y':
        saveTo = 'final'
    else:
        saveTo = 'test'
    
    for i in range(timeRange[0], timeRange[1]):
        df = CleanData(dataset = ds,
                       time = i,
                       area = area,
                       groupAmount = groupAmount)
        df = CalcVelocity(data = df,
                          powerLaw = powerLaw,
                          depthOfInterest = depthOfInterest,
                          bottomRoughnessCoef = bottomRoughnessCoef)
        Plot2dVectorField(area = area,
                          data = df,
                          depth = depth,
                          flow = flow,
                          mapRes = mapRes,
                          numArrows=numArrows).savefig(f"/home/charlie/Documents/Uni/Exeter - Data Science/MTHM604_Tackling_Sustainability_Challenges/MTHM604_week_2/plots/{saveTo}/2chan{i}.png")
        print("Finished: ", i)
    print("Done")
    
#%% Defining Areas

# Falmouth area
falArea = {
        'easting0': 347767.59,
        'northing0': 5550347.91,
        'easting1': 361496.43,
        'northing1': 5564169.61
        }

# Total Channel
channelArea = {
        'easting0': 100000,
        'northing0': 0.0,
        'easting1': 999999,
        'northing1': 10000000.00
        }
#%% Falmouth Area GIF

# For creating gif of Falmouth Harbour
area = falArea
fn = "/home/charlie/Documents/Uni/Exeter - Data Science/MTHM604_Tackling_Sustainability_Challenges/MTHM604_week_2/data/rawData/TIGER_Model_2019-11/flow/output/TIGER_map.nc"
ds = nc.Dataset(fn)

listDf = []
for i in range(6, 8):
    df = CleanData(dataset = ds,
                   time = i,  
                   area = area,
                   groupAmount = 2)
    df = CalcVelocity(data = df,
                      powerLaw = 1/10,
                      depthOfInterest = df['depth']/2,
                      bottomRoughnessCoef = 0.32)
    Plot2dVectorField(area = area,
                      data = df,
                      depth = False,
                      flow = True,
                      mapRes = 'f',
                      numArrows=3).savefig(f"/home/charlie/Documents/Uni/Exeter - Data Science/MTHM604_Tackling_Sustainability_Challenges/MTHM604_week_2/plots/{i}.png")
    print("Finished: ", i)
    
    
# %% Channel Area GIF


# For creating gif of whole channel area
area = channelArea
fn = "/home/charlie/Documents/Uni/Exeter - Data Science/MTHM604_Tackling_Sustainability_Challenges/MTHM604_week_2/data/rawData/TIGER_Model_2019-11/flow/output/TIGER_map.nc"
ds = nc.Dataset(fn)

listDf = []
x = [5, 15]
for i in range(5, 15):
    df = CleanData(dataset = ds,
                   time = i,
                   area = area,
                   groupAmount = 3)
    df = CalcVelocity(data = df,
                      powerLaw = 1/10,
                      depthOfInterest = df['depth']/2,
                      bottomRoughnessCoef = 0.32)
    Plot2dVectorField(area = area,
                      data = df,
                      depth = False,
                      flow = True,
                      mapRes = 'i',
                      numArrows=10).savefig(f"/home/charlie/Documents/Uni/Exeter - Data Science/MTHM604_Tackling_Sustainability_Challenges/MTHM604_week_2/plots/2chan{i}.png")
    print("Finished: ", i)

    
# %%


fn = "/home/charlie/Documents/Uni/Exeter - Data Science/MTHM604_Tackling_Sustainability_Challenges/MTHM604_week_2/data/rawData/TIGER_Model_2019-11/flow/output/TIGER_map.nc"
# Total Channel
channelArea = {
        'easting0': 100000,
        'northing0': 0.0,
        'easting1': 999999,
        'northing1': 10000000.00
        }

CreateImageStack(channelArea, fn, timeRange = [0, 100])




#%%
ds = nc.Dataset(fn)
#%%
def CreateImageStackMulti(timeRange, area = channelArea,  ncFileLocation = fn, powerLaw = 1/10, depthOfInterest = 2, bottomRoughnessCoef = 0.32, depth = False, flow = True, mapRes = 'i', numArrows = 10, groupAmount = 2):
    area = area
    

    listDf = []
    for i in timeRange:
        df = CleanData(dataset = ds,
                       time = i,
                       area = area,
                       groupAmount = groupAmount)
        df = CalcVelocity(data = df,
                          powerLaw = powerLaw,
                          depthOfInterest = depthOfInterest,
                          bottomRoughnessCoef = bottomRoughnessCoef)
        Plot2dVectorField(area = area,
                          data = df,
                          depth = depth,
                          flow = flow,
                          mapRes = mapRes,
                          numArrows=numArrows).savefig(f"/home/charlie/Documents/Uni/Exeter - Data Science/MTHM604_Tackling_Sustainability_Challenges/MTHM604_week_2/plots/test/multichan{i}.png")
        print("Finished: ", i)
    print("Done")

import multiprocessing
import pty

pid = pty.fork()
if not pid:
    if __name__ == "__main__":
        arr1=[2,3,8,9]
        arr2=[4, 5, 7, 10]
        p1=multiprocessing.Process(target=CreateImageStackMulti,args=(arr1,))
        p2=multiprocessing.Process(target=CreateImageStackMulti,args=(arr2,))
        
        p1.start()
        p2.start()
        
        print("Done")

# %%
fig, axs = plt.subplots(5)
fig.suptitle('Vertically stacked subplots')

for count, dataframe in enumerate(listDf):
    
    axs[i].scatter(dataframe.index, dataframe['mag'], c= dataframe['mag'], cmap = 'mako', s = 0.3, alpha = 0.3)
    
# %%

plt.scatter(listDf[1].index, listDf[1]['mag'], c= listDf[1]['mag'], cmap = 'mako', s = 0.3, alpha = 0.3)

# %%

test = pd.DataFrame(columns = ['locX', 'locY', 'velX', 'velY', 'depth', 'mag'])
test['locX']= pd.DataFrame(ds.variables['mesh2d_face_x'][:])
test['locY']= pd.DataFrame(ds.variables['mesh2d_face_y'][:])
test['velX']= pd.DataFrame(np.ma.masked_values(ds['mesh2d_ucx'][100], -999).data)
test['velY'] = pd.DataFrame(np.ma.masked_values(ds['mesh2d_ucy'][100], -999).data)
test['depth'] = pd.DataFrame(np.ma.masked_values(ds['mesh2d_waterdepth'][100], -999).data)
test['mag'] = pd.DataFrame(np.ma.masked_values(ds['mesh2d_ucmag'][100], -999).data)
test['locXgroup'] = test['locX'].apply(lambda x: round(x, -))
test['locYgroup'] = test['locY'].apply(lambda x: round(x, -2))
#%%

# Creating a plot using the grouped distance. Groups points and averages
# velocity within 100m2
test = CleanData(ds, 100, ['mesh2d_waterdepth', 'mesh2d_face_x', 'mesh2d_face_y', 'mesh2d_ucx', 'mesh2d_ucy', 'mesh2d_ucmag'], falArea, 2)
test = CalcVelocity(test, depthOfInterest = test['depth']/2)
Plot2dVectorDepth(area = falArea,
                  data = test,
                  depth = False,
                  flow = True,
                  mapRes = 'f',
                  numArrows=3).savefig(f"/home/charlie/Documents/Uni/Exeter - Data Science/MTHM604_Tackling_Sustainability_Challenges/MTHM604_week_2/plots/test.png")
# %%
















def update_quiver(num, Q, X, Y):
    """updates the horizontal and vertical vector components by a
    fixed increment on each frame
    """

    U = np.cos(X + num*0.1)
    V = np.sin(Y + num*0.1)

    Q.set_UVC(U,V)

    return Q,

# you need to set blit=False, or the first set of arrows never gets
# cleared on subsequent frames
anim = animation.FuncAnimation(fig, update_quiver, fargs=(Q, X, Y),
                               interval=50, blit=False)
fig.tight_layout()
plt.show()




#df3 = df2[(df2['lon'] >= lon0) & (df2['lon'] <= lon1) & (df2['lat'] >= lat0)& (df2['lat'] <= lat1)]
df2 = listDf[0]
x = df2[(df2['lon'] >= lon0) & (df2['lon'] <= lon1) & (df2['lat'] >= lat0)& (df2['lat'] <= lat1)]['lon']
y = df2[(df2['lon'] >= lon0) & (df2['lon'] <= lon1) & (df2['lat'] >= lat0)& (df2['lat'] <= lat1)]['lat']
z = df2[(df2['lon'] >= lon0) & (df2['lon'] <= lon1) & (df2['lat'] >= lat0)& (df2['lat'] <= lat1)]['depth']

# mwidth = 100
# mheight = 100
# lonCenter = -5.040450
# latCenter = 50.144219

fig = plt.gcf()
fig.set_size_inches(10, 10)

m = Basemap(projection='merc',
            llcrnrlon = lon0, urcrnrlon = lon1,
            llcrnrlat = lat0, urcrnrlat = lat1,
            resolution='h')

m.fillcontinents()
m.drawcoastlines(color = 'black', linewidth=0.2)
x2, y2 = m(x.tolist(), y.tolist())  # transform coordinates
p1 = plt.scatter(x2, y2,c=z, s=12, alpha = 0.2, cmap="mako") 
m1 = m.colorbar(p1)
X,Y,U,V,C = (df2['lon'], df2['lat'], df2['velXseabed'], df2['velYseabed'], df2['mag'])
X2, Y2 = m(X.tolist(), Y.tolist())
# Select how many arrows to render, 1 = all
numArrows = 1
Q = plt.quiver(X2[::numArrows], Y2[::numArrows], U[::numArrows], V[::numArrows], C[::numArrows], 
           units='width', 
           cmap = 'twilight', 
           capstyle = 'round', 
           alpha = 0.7, 
           headwidth = 2, 
           headlength = 3,
           minlength = 0.1)

def update_quiver(num, Q, X, Y):
    """updates the horizontal and vertical vector components by a
    fixed increment on each frame
    """

    U = listDf[num]['velXseabed']
    V = listDf[num]['velYseabed']
    C = listDf[num]['mag']

    Q.set_UVC(U,V, C)

    return Q,

# you need to set blit=False, or the first set of arrows never gets
# cleared on subsequent frames
anim = animation.FuncAnimation(fig, update_quiver, fargs=(Q, X, Y),
                               interval=10, blit=False)
fig.tight_layout()
plt.show()
