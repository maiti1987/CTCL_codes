# -*- coding: utf-8 -*-
"""
Created on Sat Dec 14 13:27:55 2019

@author: tuf86648
"""

import numpy as np
import pandas as pd
import shapefile as shp
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
import datetime
from dateutil.relativedelta import relativedelta

inputfilename = "shore_all_data_with_time_span_in_monthFx_all_time_NEWEST_WINS"
pkl_file = inputfilename + ".pkl"
data = pd.read_pickle(pkl_file)

shp_path = "./draw/US_tract_2010.shp"
df = gpd.read_file(shp_path)
NJ_df = df[df["STATEFP10"] == '34']


first_snapshot = datetime.datetime.strptime("2000-01-01", "%Y-%m-%d").date()
second_snapshot = datetime.datetime.strptime("2010-01-01", "%Y-%m-%d").date()
Snapshots = []

for ind,row in data.iterrows():
    first_snapshot_stfid = 'XX'
    second_snapshot_stfid = 'XX'
    for tspan in range(2, 40):
        st_col = "Nsrt_{0}".format(tspan)
        lt_col = "Nlst_{0}".format(tspan)
        stfid = "Nloc_{0}".format(tspan)
        if len(row[stfid]) == 11:
            if (row[st_col] <= first_snapshot) and (row[lt_col]>= first_snapshot) and int(row[stfid])!=0:
                first_snapshot_stfid = row[stfid]
    
    
            if (row[st_col] <= second_snapshot) and (row[lt_col]>= second_snapshot) and int(row[stfid])!=0:
                second_snapshot_stfid = row[stfid]
                
    Snapshots.append([first_snapshot_stfid, second_snapshot_stfid])
    

tract_dict = {}
for ind,row in NJ_df.iterrows():
    tract = str(int(row['njtract']))
    tract_dict[tract] = [0,0,0,0] # total2000, total 2010,  moving out, moving in

for r in Snapshots:
    if r[0]!= 'XX' and r[1]!= 'XX' :
       if r[0] in tract_dict: 
           tract_dict[r[0]][0] =  tract_dict[r[0]][0] + 1
           
       if r[1] in tract_dict:  
           tract_dict[r[1]][1] =  tract_dict[r[1]][1] + 1
       if r[0]!=r[1]:
           if r[0] in tract_dict: 
               tract_dict[r[0]][2] =  tract_dict[r[0]][2] + 1
           if r[1] in tract_dict:  
               tract_dict[r[1]][3] =  tract_dict[r[1]][3] + 1