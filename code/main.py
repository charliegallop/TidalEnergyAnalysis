# -*- coding: utf-8 -*-

from functions import CreateImageStack
import netCDF4 as nc

fn = "/home/charlie/Documents/Uni/Exeter - Data Science/MTHM604_Tackling_Sustainability_Challenges/MTHM604_week_2/data/rawData/TIGER_Model_2019-11/flow/output/TIGER_map.nc"

# Falmouth area
falArea = {
        'easting0': 347767.59,
        'northing0': 5550347.91,
        'easting1': 361496.43,
        'northing1': 5564169.61
        }

CreateImageStack(falArea, fn, timeRange = [100, 101], mapRes = "c")