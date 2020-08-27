# -*- coding: utf-8 -*-
"""
Created on Fri Nov 22 15:47:27 2019

@author: tuf86648
source
https://towardsdatascience.com/mapping-with-matplotlib-pandas-geopandas-and-basemap-in-python-d11b57ab5dac
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
#vmin, vmax = -4, 1 #merged_data[variable].max()
mask = merged_data[variable] < vmin
merged_data.loc[mask, variable] = vmin


fig, ax = plt.subplots(1, figsize=(7, 11))
merged_data.plot(column=variable, cmap='BuGn', linewidth=0.1, ax=ax, edgecolor='0.98')

# remove the axis
ax.axis('off')
# add a title
ax.set_title('Computed Risk', fontdict={'fontsize': '25', 'fontweight' : '3'})

# Create colorbar as a legend
sm = plt.cm.ScalarMappable(cmap='BuGn', norm=plt.Normalize(vmin=vmin, vmax=vmax))




# empty array for the data range
sm._A = []
# add the colorbar to the figure
cbar = fig.colorbar(sm, fraction=0.08, ax=ax)



#saving our map as .png file.
fig.savefig('CTCL_risks.png', dpi=300)
plt.show()
plt.close()