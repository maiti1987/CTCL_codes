# -*- coding: utf-8 -*-
"""
Created on Wed Jul  1 05:09:35 2020

@author: aniruddha maiti
"""


import numpy as np
import pandas as pd
import shapefile as shp
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
from simpledbf import Dbf5


AGGREGATION_FLAG = True


shp_path = "./draw/US_tract_2010.shp"
df = gpd.read_file(shp_path)
NJ_df = df[df["STATEFP10"] == '34']
if AGGREGATION_FLAG:
    NJ_df['njtract'] = pd.to_numeric(NJ_df['njtract'], downcast='integer')
NJ_df = NJ_df.copy()

agg_CT_List = Dbf5('Agg_CT_List_Coords.dbf')
agg_CT_List=agg_CT_List.to_dataframe()
agg_CT_List_reindexed = agg_CT_List.set_index("GEOID10")

# Variables according to the values as inPrepare_Fake_Data.py


#HIGH_RISK_GEOID = ['GATid1066', 'GATid1243', 'GATid1254', 'GATid1299', 'GATid1311',   
#'GATid1429', 'GATid1435', 'GATid1446', 'GATid1489', 'GATid1593',   
#'GATid1598', 'GATid1604', 'GATid1609', 'GATid1630', 'GATid165',   
#'GATid1650', 'GATid1660', 'GATid169', 'GATid1690', 'GATid1704',   
#'GATid1706', 'GATid254', 'GATid373', 'GATid423', 'GATid908',   
#'GATid943', 'GATid951']


HIGH_RISK_GEOID = ['GATid1012', 'GATid1160', 'GATid1212', 'GATid1390', 'GATid1417',   
'GATid1436', 'GATid1594', 'GATid1599', 'GATid1670', 'GATid238',   
'GATid405', 'GATid458', 'GATid506']


#HIGH_RISK_GEOID =  [ 'GATid894', 'GATid894', 'GATid1519', 'GATid1519', 'GATid1519',   
#'GATid894', 'GATid1519', 'GATid1519', 'GATid894', 'GATid1519',   
#'GATid1519', 'GATid894', 'GATid1519' ]


print('NUMBER of High Risk Tracts = ', len(HIGH_RISK_GEOID))

High_Risk_Prob = 0.3
Low_Risk_Prob = 0.01

NJ_df['underlying_true_risk'] = [None for _ in range(len(NJ_df))]

cc = 0
for indx, row in NJ_df.iterrows():
    if agg_CT_List_reindexed.loc[str(int(row['njtract']))].GATid in HIGH_RISK_GEOID:
        true_risk = High_Risk_Prob
        cc += 1
    else :
        true_risk = Low_Risk_Prob
    
    NJ_df.at[indx, 'underlying_true_risk'] = true_risk



#-------------------------------------------------------
tract_column = 'Unnamed: 0'
Tract_Risk = pd.read_csv("tract_risks_simulations_withCI.csv")
Tract_Risk = Tract_Risk[[tract_column, 'original_risk']]


if AGGREGATION_FLAG:
    agg_CT_List_reindexed = agg_CT_List_reindexed['GATid']
    NJ_df['njtract'] = NJ_df['njtract'].astype(str)
    merged_data = NJ_df.set_index('njtract').join(agg_CT_List_reindexed)
    merged_data = merged_data.join( Tract_Risk.set_index(tract_column), on='GATid')
    
else :
    merged_data = NJ_df.set_index('njtract').join(Tract_Risk.set_index(tract_column))


#-------------------------------------------------------------------------


#-------------------------------------------------------------------------
variable = "underlying_true_risk"
merged_data = merged_data.dropna(subset=[variable])
vmin, vmax = merged_data[variable].min(), merged_data[variable].max() # range for the choropleth


fig, ax = fig, ax = plt.subplots(figsize=(7, 6))
merged_data.geometry.boundary.plot(color=None,edgecolor='0.2', linewidth = 0.1, ax=ax) 
merged_data.plot(column=variable, cmap='BuGn',alpha=2.0, ax = ax, linewidth=0.0, edgecolor='0.98')
#merged_data.plot(column=variable, cmap='BuGn', ax = ax, linewidth=0.0, edgecolor='0.9')

# remove the axis
ax.axis('off')
# add a title
#ax[0].set_title('High Risk region', fontdict={'fontsize': '20', 'fontweight' : '3'})

# Create colorbar as a legend
#sm = plt.cm.ScalarMappable(cmap='BuGn', norm=plt.Normalize(vmin=vmin, vmax=vmax))

# empty array for the data range
#sm._A = []
# add the colorbar to the figure

#cbar = fig.colorbar(sm, fraction=0.046, ax=ax[0])

#saving our map as .png file.
#fig.savefig('Original Risk.png', dpi=300)
#plt.show()
#plt.close()


#saving our map as .png file.
fig.savefig('sim_high_risk_area4.png', dpi=300)
plt.show()
plt.close()

#-------------------------------------------------------------------------------------


