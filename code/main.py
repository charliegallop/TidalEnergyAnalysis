# -*- coding: utf-8 -*-

from functions import CreateImageStack
from functions import CreateImageStackStreamplot
import netCDF4 as nc
from PIL import Image
import pandas as pd
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import utm
from mpl_toolkits.basemap import Basemap
import math
import netCDF4 as nc
from matplotlib.offsetbox import (TextArea, DrawingArea, OffsetImage,
                                  AnnotationBbox)
from matplotlib.cbook import get_sample_data



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


#Moon Phases
    # 0 – new moon
    # 0-0.25 – waxing crescent
    # 0.25 – first quarter
    # 0.25-0.5 – waxing gibbous
    # 0.5 – full moon
    # 0.5-0.75 – waning gibbous
    # 0.75 – last quarter
    # 0.75 -1 – waning crescent

new = Image.open(r'/home/charlie/Documents/Uni/Exeter - Data Science/MTHM604_Tackling_Sustainability_Challenges/MTHM604_week_2/images/new.png')
full = Image.open(r'/home/charlie/Documents/Uni/Exeter - Data Science/MTHM604_Tackling_Sustainability_Challenges/MTHM604_week_2/images/full.png')
waningGibbous = Image.open(r'/home/charlie/Documents/Uni/Exeter - Data Science/MTHM604_Tackling_Sustainability_Challenges/MTHM604_week_2/images/waningGibbous.png')
waxingGibbous = Image.open(r'/home/charlie/Documents/Uni/Exeter - Data Science/MTHM604_Tackling_Sustainability_Challenges/MTHM604_week_2/images/waxingGibbous.png')
waningCrescent = Image.open(r'/home/charlie/Documents/Uni/Exeter - Data Science/MTHM604_Tackling_Sustainability_Challenges/MTHM604_week_2/images/waningCrescent.png')
waxingCrescent = Image.open(r'/home/charlie/Documents/Uni/Exeter - Data Science/MTHM604_Tackling_Sustainability_Challenges/MTHM604_week_2/images/waxingCrescent.png')
firsrtQuarter = Image.open(r'/home/charlie/Documents/Uni/Exeter - Data Science/MTHM604_Tackling_Sustainability_Challenges/MTHM604_week_2/images/firstQuarter.png')
thirdQuarter =  Image.open(r'/home/charlie/Documents/Uni/Exeter - Data Science/MTHM604_Tackling_Sustainability_Challenges/MTHM604_week_2/images/thirdQuarter.png')

moonPhasesImgs = {
    "new": new,
    "full": full,
    "waningGibbous": waningGibbous,
    "waxingGibbous": waxingGibbous,
    "waningCrescent": waningCrescent,
    "waxingCrescent": waxingCrescent,
    "firstQuarter": firsrtQuarter,
    "thirdQuarter": thirdQuarter
    }

moonPhases = pd.read_csv("/home/charlie/Documents/Uni/Exeter - Data Science/MTHM604_Tackling_Sustainability_Challenges/MTHM604_week_2/data/rawData/Dover 2019-10-26 to 2019-12-31.csv")
moonPhases['datetime'] = pd.to_datetime(moonPhases['datetime']).dt.date
# Ideal Parameters for Channel map:
    # groupAmount = 3
    # numArrows = 9

CreateImageStack(clippedChannelArea, fn, timeRange = [1470, 2592], mapRes = "h", groupAmount=3, numArrows=9, places = places, moonImgs = moonPhasesImgs, moonPhases = moonPhases, depthOfInterest = 10)
#CreateImageStackStreamplot(falArea, fn, timeRange=[100, 105], mapRes = "f", groupAmount = 4)