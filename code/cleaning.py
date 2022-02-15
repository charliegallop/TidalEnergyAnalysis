#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 13 20:41:54 2022

@author: charlie
"""
#%%
import netCDF4 as nc
import numpy as np
import numpy.ma as ma
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

#%%

fn = "/home/charlie/Documents/Uni/Exeter - Data Science/MTHM604_Tackling_Sustainability_Challenges/MTHM604_week_2/data/rawData/TIGER_Model_2019-11/flow/output/TIGER_map.nc"
ds = nc.Dataset(fn)

#%%

# print all variable names and shape of each variable
for i in ds.variables.keys():
    print(i, ': ', ds[i].shape)
    
    # projected_coordinate_system :  ()
    # mesh2d :  ()
    # mesh2d_node_x :  (146637,)
    # mesh2d_node_y :  (146637,)
    # mesh2d_node_z :  (146637,)
    # mesh2d_edge_x :  (426111,)
    # mesh2d_edge_y :  (426111,)
    # mesh2d_edge_nodes :  (426111, 2)
    # mesh2d_face_nodes :  (279464, 4)
    # mesh2d_edge_faces :  (426111, 2)
    # mesh2d_face_x :  (279464,)
    # mesh2d_face_y :  (279464,)
    # mesh2d_face_x_bnd :  (279464, 4)
    # mesh2d_face_y_bnd :  (279464, 4)
    # mesh2d_edge_type :  (426111,)
    # mesh2d_flowelem_ba :  (279464,)
    # mesh2d_flowelem_bl :  (279464,)
    # time :  (2593,)
    # timestep :  (2593,)
    # mesh2d_waterdepth :  (2593, 279464)
    # mesh2d_s1 :  (2593, 279464)
    # mesh2d_ucx :  (2593, 279464)
    # mesh2d_ucy :  (2593, 279464)
    # mesh2d_ucmag :  (2593, 279464)
    # mesh2d_czs :  (2593, 279464)
    
#%%

# Return individual variables

meshx = ds['mesh2d_node_x'][:]
meshy = ds['mesh2d_node_y'][:]
meshz = ds['mesh2d_node_z'][:]

# %%
timeStep = 1
dfX = pd.DataFrame(ds['mesh2d_ucx'][:, timeStep], columns = ['velX'])
dfY = pd.DataFrame(ds['mesh2d_ucy'][:, timeStep], columns = ['velY'])
dfMag = pd.DataFrame(ds['mesh2d_ucmag'][:, timeStep], columns = ['mag'])
df = pd.concat([dfX, dfY, dfMag], axis = 1)
df['locX'] = ds['mesh2d_face_x'][timeStep].data
df['locY'] = ds['mesh2d_face_y'][timeStep].data
df.to_csv("ts2.csv")
#%%

# Make a dataframe from masked array which can be joined to master df

def MakeDfFromMA(variable):
    df = ds[variable][:]
    df = np.ma.getdata(df)
    df = pd.DataFrame(df)
    return df

#%%

# Setting which time point to look at

timeStamp = 100

#%%

# get the x and y vector velocities for the first location
vecX = pd.DataFrame(np.ma.masked_values(ds['mesh2d_ucx'][timeStamp], -999).data)
vecY = pd.DataFrame(np.ma.masked_values(ds['mesh2d_ucy'][timeStamp], -999).data)
# %%

plt.scatter(vecX[0], vecY[0], s = 0.1)

# %%
mag = pd.DataFrame(np.ma.masked_values(ds['mesh2d_ucmag'][timeStamp], -999).data)

# %%

# do the same with the water depth

depth = pd.DataFrame(np.ma.masked_values(ds['mesh2d_waterdepth'][timeStamp], -999))


#%%

dftime = MakeDfFromMA('time')
dfX = MakeDfFromMA('mesh2d_face_x')
dfY = MakeDfFromMA('mesh2d_face_y')

# %%

df = pd.concat([depth, dfX, dfY, vecX, vecY, mag], axis = 1)



#%%

df.columns = ['depth', 'locx', 'locy', 'velx', 'vely', 'mag']


#%%
df['depth'] = -1*df['depth']
#%%
import utm
df = df[(df['locx'] <= 999999) & (df['locx'] >= 100000)]
#%%
df['lat'] = df.apply(lambda x: utm.to_latlon(x['locx'], x['locy'], 30, 'N')[0], axis = 1)
df['lon'] = df.apply(lambda x: utm.to_latlon(x['locx'], x['locy'], 30, 'N')[1], axis = 1)

#%%

# Converting the depth-averaged velocity to velocity at a given depth
powerLaw = 1/10
depthOfInterest = df['depth']/2
bottomRoughnessCoef = 0.32
df['velXseabed'] = pow((depthOfInterest/bottomRoughnessCoef*df['depth']), (powerLaw))*df['velx']
df['velYseabed'] = pow((depthOfInterest/bottomRoughnessCoef*df['depth']), (powerLaw))*df['vely']

#%%
plt.scatter(df.index, df['mag'], c= df['mag'], cmap = 'mako', s = 0.3, alpha = 0.3)

#%%
#df2 = df[(df['lat'] > 50.1) & (df['lat'] < 50.2) & (df['lon'] > 5) & (df['lon'] < 5.08)]
df2 = df.copy()
df2 = df2[df2['depth'] > -300]
df2 = df2.reset_index()

# %%

# 3D depth plot

from mpl_toolkits import mplot3d

fig = plt.figure()

ax = plt.axes(projection = '3d')

z = df2['depth']
x = df2['lon']
y = df2['lat']
c = z

ax.scatter(x, y, z, c = z, s = 1)

plt.show()
# %%

# 2D Velocity and depth map

from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np

# lat0 = 48
# lat1 = 51
# lon0 = -5.5
# lon1 = -1

# df3 = df2[(df2['lon'] >= lon0) & (df2['lon'] <= lon1) & (df2['lat'] >= lat0)& (df2['lat'] <= lat1)]
# x = df2[(df2['lon'] >= lon0) & (df2['lon'] <= lon1) & (df2['lat'] >= lat0)& (df2['lat'] <= lat1)]['lon']
# y = df2[(df2['lon'] >= lon0) & (df2['lon'] <= lon1) & (df2['lat'] >= lat0)& (df2['lat'] <= lat1)]['lat']
# z = df2[(df2['lon'] >= lon0) & (df2['lon'] <= lon1) & (df2['lat'] >= lat0)& (df2['lat'] <= lat1)]['depth']

df3 = df2.copy()
x = df2['lon']
y = df2['lat']
z = df2['mag']

lat0 = 45
lat1 = 55
lon0 = -10
lon1 = 10

# mwidth = 100
# mheight = 100
# lonCenter = -5.040450
# latCenter = 50.144219

fig = plt.gcf()
fig.set_size_inches(10, 10)

m = Basemap(projection='merc',
            llcrnrlon = lon0, urcrnrlon = lon1,
            llcrnrlat = lat0, urcrnrlat = lat1,
            resolution='c')
m.fillcontinents(color='black')
m.drawcoastlines(color = 'black', linewidth=0.2)
x2, y2 = m(x.tolist(), y.tolist())  # transform coordinates
p1 = plt.scatter(x2, y2,c=z, s=12, alpha = 0.2, cmap="mako") 
m1 = m.colorbar(p1)
X,Y,U,V,C = (df3['lon'], df3['lat'], df3['velXseabed'], df3['velYseabed'], df3['mag'])
X2, Y2 = m(X.tolist(), Y.tolist())
# Select how many arrows to render, 1 = all
numArrows = 5
Q = plt.quiver(X2[::numArrows], Y2[::numArrows], U[::numArrows], V[::numArrows], C[::numArrows], 
           units='inches', 
           cmap = 'twilight', 
           capstyle = 'round', 
           alpha = 0.7,
           scale_units = 'xy',
           minlength = 0.1)
plt.show()


# %%

#2D depth plot

from mpl_toolkits.basemap import Basemap

f, ax = plt.subplots()

m = Basemap(projection='merc',
            llcrnrlon = lon0, urcrnrlon = lon1,
            llcrnrlat = lat0, urcrnrlat = lat1,
            resolution='h')
m.fillcontinents()
m.drawcoastlines(color = 'black', linewidth=0.2)
X, Y = m(x.tolist(), y.tolist())
points = ax.scatter(X, Y, c=z, s=10, alpha = 0.2, cmap="mako")
f.colorbar(points)
