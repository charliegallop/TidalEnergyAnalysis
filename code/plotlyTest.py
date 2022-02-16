#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 15 16:29:41 2022

@author: charlie
"""
import plotly.graph_objects as go
from plotly.offline import plot
import plotly.express as px
import plotly.io as pio
pio.renderers.default='browser'


fig = px.scatter_geo(test, lat= "lat",
                     lon = "lon",
                     size="magSeabed", # size of markers, "pop" is one of the columns of gapminder
                     )
fig.show()