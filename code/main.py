# -*- coding: utf-8 -*-

from functions import CreateImageStack
from functions import CreateImageStackStreamplot
import netCDF4 as nc

fn = "/home/charlie/Documents/Uni/Exeter - Data Science/MTHM604_Tackling_Sustainability_Challenges/MTHM604_week_2/data/rawData/TIGER_Model_2019-11/flow/output/TIGER_map.nc"


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

clippedChannelArea = {
        'easting0': 260000,
        'northing0': 5270000,
        'easting1': 883406.65,
        'northing1': 5770000
        }

places = {
    'Falmouth': [(50.1534742, -5.0740758), (50, 90)],
    'Dover':[(51.129711, 1.311140), (-200, 40)],
    'Calais':[(50.951290,1.858686), (-10, -100)],
    'Cherbourg':[(49.6337308, -1.622137000000066), (0, -125)],
    'Isle of Wight': [(50.693848, -1.304734), (-50, 100)],
    'Le Conquet': [(48.359961, -4.774587), (150, 0)]
    }

# Ideal Parameters for Channel map:
    # groupAmount = 3
    # numArrows = 10

CreateImageStack(clippedChannelArea, fn, timeRange = [6, 500], mapRes = "i", groupAmount=3, numArrows=10, places = places)
#CreateImageStackStreamplot(falArea, fn, timeRange=[100, 105], mapRes = "f", groupAmount = 4)