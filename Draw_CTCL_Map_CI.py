# -*- coding: utf-8 -*-
"""
Created on Sat Jul  4 20:28:10 2020

@author: aniruddha maiti
"""


import numpy as np
import pandas as pd
import shapefile as shp
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
from simpledbf import Dbf5


shp_path = "./draw/US_tract_2010.shp"
df = gpd.read_file(shp_path)
NJ_df = df[df["STATEFP10"] == '34']
NJ_df['njtract'] = pd.to_numeric(NJ_df['njtract'], downcast='integer')

tract_column = 'Unnamed: 0'
variable = "original_risk"
#variable = "Cases"
#variable = 'smoothed_ratio'

Tract_Risk = pd.read_csv("tract_risks_simulations_withCI.csv")
# For quick results discard simulation results
#Tract_Risk = Tract_Risk[[tract_column, variable]]

AGGREGATION_FLAG = True
if AGGREGATION_FLAG:
    agg_CT_List = Dbf5('Agg_CT_List_Coords.dbf')
    agg_CT_List=agg_CT_List.to_dataframe()
    agg_CT_List_reindexed = agg_CT_List.set_index("GEOID10")
    agg_CT_List_reindexed = agg_CT_List_reindexed['GATid']
    NJ_df['njtract'] = NJ_df['njtract'].astype(str)
    merged_data = NJ_df.set_index('njtract').join(agg_CT_List_reindexed)
    merged_data = merged_data.join( Tract_Risk.set_index(tract_column), on='GATid')
    
else :
    merged_data = NJ_df.set_index('njtract').join(Tract_Risk.set_index(tract_column))

merged_data = merged_data.dropna(subset=[variable])
vmin, vmax = merged_data[variable].min(), merged_data[variable].max() # range for the choropleth
#vmin, vmax = -7, 0.6 #merged_data[variable].max()


fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(7, 6), gridspec_kw={'width_ratios': [3, 3.4]})


variable = "original_risk"
merged_data = merged_data.dropna(subset=[variable])
vmin, vmax = merged_data[variable].min(), merged_data[variable].max() # range for the choropleth
#vmin, vmax = -2.9, 5
sm = plt.cm.ScalarMappable(cmap='BuGn', norm=plt.Normalize(vmin=vmin, vmax=vmax))
#fig, ax = plt.subplots(1, figsize=(7, 11))
merged_data.geometry.boundary.plot(color=None, edgecolor='0.2', linewidth = 0.1, ax=ax[0]) 
#merged_data.plot(column=variable, cmap='BuGn', alpha=2.0, linewidth=0.0, ax=ax[1], edgecolor='0.98', figsize=(8,12))
merged_data.plot(column=variable, cmap='BuGn', alpha=2.0, linewidth=0.0, ax=ax[0], edgecolor='0.98')
# remove the axis


# remove the axis
ax[0].axis('off')
# add a title
ax[0].set_title('Predicted Risk', fontdict={'fontsize': '14', 'fontweight' : '3'})

# Create colorbar as a legend
sm = plt.cm.ScalarMappable(cmap='BuGn', norm=plt.Normalize(vmin=vmin, vmax=vmax))

# empty array for the data range
sm._A = []
# add the colorbar to the figure
cbar = fig.colorbar(sm, fraction=0.08, ax=ax[0])

#saving our map as .png file.
#fig.savefig('Predicted_Risk.png', dpi=300)
#plt.show()
#plt.close()

#-------------------------------------------------------------------------------------

#
variableCI = "CI"
merged_data = merged_data.dropna(subset=[variableCI])

merged_data["CIdraw"] = None

CI_cutoff = 5.0
mask = merged_data[variableCI] < CI_cutoff

mask2 = merged_data[variableCI] >= CI_cutoff

#mask3 = merged_data[variable] > 0.5

merged_data.loc[mask, "CIdraw"] = merged_data[variable] #make 
merged_data.loc[mask2, "CIdraw"] = vmin #make 
#merged_data.loc[mask3, "CIdraw"] = vmin #make 

#mask = merged_data[variable] < CI_cutoff
#merged_data.loc[mask, variable] = 1

#fig, ax = plt.subplots(1, figsize=(7, 11))
merged_data.geometry.boundary.plot(color=None, edgecolor='0.2', linewidth = 0.1, ax=ax[1]) 
merged_data.plot(column="CIdraw", cmap='BuGn', alpha=2.0, linewidth=0.0, ax=ax[1], edgecolor='0.98')
# remove the axis
ax[1].axis('off')
# add a title
ax[1].set_title('Significant High Risk', fontdict={'fontsize': '14', 'fontweight' : '3'})

#saving our map as .png file.
fig.savefig('Predicted_Risk_CTCL.png', dpi=300)
plt.show()
plt.close()
