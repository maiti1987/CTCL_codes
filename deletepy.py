# -*- coding: utf-8 -*-
"""
Created on Wed Dec  4 14:05:07 2019

@author: tuf86648
"""

import numpy as np
import pandas as pd
import shapefile as shp
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd

shp_path = "./draw/US_tract_2010.shp"
df = gpd.read_file(shp_path)
NJ_df = df[df["STATEFP10"] == '34']


Tract_Risk = pd.read_csv("tract_risks_simulations_withCI.csv")
Tract_Risk = Tract_Risk[['tract', 'original_risk']]



merged_data = NJ_df.set_index('njtract').join(Tract_Risk.set_index('tract'))



variable = "original_risk"
merged_data = merged_data.dropna(subset=[variable])
vmin, vmax = merged_data[variable].min(), merged_data[variable].max() # range for the choropleth

fig, ax = plt.subplots(1, figsize=(7, 11))
merged_data.plot(column=variable, cmap='BuGn', linewidth=0.8, ax=ax, edgecolor='0.8')

# remove the axis
ax.axis('off')
# add a title
ax.set_title('Predicted Risk in NJ', fontdict={'fontsize': '25', 'fontweight' : '3'})

# Create colorbar as a legend
sm = plt.cm.ScalarMappable(cmap='BuGn', norm=plt.Normalize(vmin=vmin, vmax=vmax))




# empty array for the data range
#sm._A = []
# add the colorbar to the figure
cbar = fig.colorbar(sm)


plt.show()
plt.close()