# -*- coding: utf-8 -*-
"""
Created on Thu Jul  2 03:59:20 2020

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

#HIGH_RISK_GEOID =  [ 'GATid894', 'GATid894', 'GATid1519', 'GATid1519', 'GATid1519',   
#'GATid894', 'GATid1519', 'GATid1519', 'GATid894', 'GATid1519',   
#'GATid1519', 'GATid894', 'GATid1519' ]

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


# empty array for the data range
#sm._A = []
# add the colorbar to the figure

#cbar = fig.colorbar(sm, fraction=0.046, ax=ax[0])

#saving our map as .png file.
#fig.savefig('Original Risk.png', dpi=300)
#plt.show()
#plt.close()


#-------------------------------------------------------------------------------------

variable = "original_risk"
merged_data = merged_data.dropna(subset=[variable])
vmin, vmax = merged_data[variable].min(), merged_data[variable].max() # range for the choropleth
vmin, vmax = -6.5, -0.5

fig, ax = plt.subplots(figsize=(7, 6))
merged_data.geometry.boundary.plot(color=None,edgecolor='0.2', linewidth = 0.1, ax=ax) 
merged_data.plot(column=variable, cmap='BuGn',alpha=2.0, ax = ax, linewidth=0.0, edgecolor='0.98')
#merged_data.plot(column=variable, cmap='BuGn', ax = ax, linewidth=0.0, edgecolor='0.9')

# remove the axis
ax.axis('off')
# add a title

# add a title
ax.set_title('Predicted Risk', fontdict={'fontsize': '20', 'fontweight' : '3'})

# Create colorbar as a legend
sm = plt.cm.ScalarMappable(cmap='BuGn', norm=plt.Normalize(vmin=vmin, vmax=vmax))

# empty array for the data range
sm._A = []
# add the colorbar to the figure
cbar = fig.colorbar(sm, fraction=0.08, ax=ax)

#saving our map as .png file.
fig.savefig('Predicted_Risk_A.png', dpi=300)
plt.show()
plt.close()
