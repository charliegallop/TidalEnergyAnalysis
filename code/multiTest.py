# -*- coding: utf-8 -*-

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
    df.columns = ['depth', 'locX', 'locY', 'velX', 'velY', 'mag']
    df['depth'] = -1*df['depth']
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
    return fig

def CreateImageStack(area,  ncFileLocation, timeRange = [5, 15], powerLaw = 1/10, depthOfInterest = 2, bottomRoughnessCoef = 0.32, depth = False, flow = True, mapRes = 'i', numArrows = 10, groupAmount = 2):
    area = area
    ds = nc.Dataset(fn)

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

#%%
arr = []
for i in range(ds.variables['time'][:].data.shape[0]):
    df = CleanData(ds, i, falArea, groupAmount = 2)
    df = CalcVelocity(df)
    df['id'] = i
    arr.append(df)
    print('Time step = ', i)

# %%

def CleanDataTest(dataset, time, area, groupAmount = False):
    
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
    df.columns = ['depth', 'locX', 'locY', 'velX', 'velY', 'mag']
    return df
    
arr = []
#x = ds.variables['time'][:].data.shape[0]

# %%
def CreateCsv(x):
    count = 0
    df = pd.DataFrame()
    df2 = pd.DataFrame()
    for i in range(x):
        df = CleanDataTest(ds, i, falArea)
        df['id'] = i
        df2 = df.append(df2)
        print('Time step = ', i)
        count += 1
        if count == 100:
            df2.to_csv(f'/home/charlie/Documents/Uni/Exeter - Data Science/MTHM604_Tackling_Sustainability_Challenges/MTHM604_week_2/data/tidyData/test{count}.csv')
            count = 0
            print("Made csv")
            df = pd.DataFrame()
            df2 = pd.DataFrame()
        
CreateCsv(110)
#%% 
import multiprocessing
   
if __name__ == "__main__":
    arr1=[2,3,8,9]
    arr2=[4, 5, 7, 10]
    p1=multiprocessing.Process(target=CreateCsv,args=(arr1,))
    p2=multiprocessing.Process(target=CreateCsv,args=(arr2,))
    
    p1.start()
    p2.start()
    
    p1.join()
    p2.join()
    
    print("Done")

