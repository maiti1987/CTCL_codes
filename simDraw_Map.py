# -*- coding: utf-8 -*-
"""
Created on Wed Dec  4 02:16:34 2019

@author: tuf86648
"""

import numpy as np
import pandas as pd
import shapefile as shp
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
from simpledbf import Dbf5


AGGREGATION_FLAG = True

dataset_index = 4
placements = [['GATid1090', 'GATid1325', 'GATid1367', 'GATid1515', 'GATid1653',   
'GATid1686', 'GATid1688', 'GATid412', 'GATid749', 'GATid834'], 

[ 'GATid1036', 'GATid1036', 'GATid1036', 'GATid1036', 'GATid1156',   
'GATid1156', 'GATid1156', 'GATid1478', 'GATid1156', 'GATid1156',   
'GATid1156', 'GATid1156', 'GATid1156', 'GATid116', 'GATid1478',   
'GATid116', 'GATid1478', 'GATid1478', 'GATid1478', 'GATid1478',   
'GATid1478', 'GATid1036', 'GATid1478', 'GATid1478', 'GATid1478',   
'GATid116', 'GATid1478', 'GATid1478', 'GATid1478', 'GATid116',   
'GATid1036' ], 
 
['GATid1012', 'GATid1160', 'GATid1212', 'GATid1390', 'GATid1417',   
'GATid1436', 'GATid1594', 'GATid1599', 'GATid1670', 'GATid238',   
'GATid405', 'GATid458', 'GATid506'], 
['GATid1216', 'GATid1290', 'GATid1291', 'GATid1330', 'GATid1346',   
'GATid1359', 'GATid1403', 'GATid1442', 'GATid1483', 'GATid1486',   
'GATid1651', 'GATid1672', 'GATid1702', 'GATid212', 'GATid542',   
'GATid798', 'GATid916', 'GATid923', 'GATid954'], 
 
[ 'GATid1012', 'GATid1039', 'GATid1065', 'GATid1117', 'GATid1123',   
'GATid1160', 'GATid119', 'GATid1191', 'GATid1204', 'GATid1212',   
'GATid1228', 'GATid1283', 'GATid1341', 'GATid1351', 'GATid1363',   
'GATid1382', 'GATid1390', 'GATid1417', 'GATid1436', 'GATid1505',   
'GATid1516', 'GATid1517', 'GATid1518', 'GATid1542', 'GATid1561',   
'GATid1584', 'GATid1594', 'GATid1599', 'GATid16', 'GATid1631',   
'GATid1668', 'GATid1670', 'GATid1679', 'GATid1710', 'GATid1714',   
'GATid238', 'GATid278', 'GATid356', 'GATid379', 'GATid405',   
'GATid458', 'GATid5', 'GATid506', 'GATid509', 'GATid527',   
'GATid556', 'GATid569', 'GATid64', 'GATid720', 'GATid790',   
'GATid930', 'GATid933', 'GATid969' ],
 
 [ 'GATid1072', 'GATid116', 'GATid1257', 'GATid1270', 'GATid1288',   
'GATid1312', 'GATid1319', 'GATid1325', 'GATid1367', 'GATid1416',   
'GATid1455', 'GATid1462', 'GATid1478', 'GATid1515', 'GATid1531',   
'GATid1540', 'GATid1621', 'GATid1638', 'GATid1653', 'GATid1671',   
'GATid1686', 'GATid1688', 'GATid1694', 'GATid1711', 'GATid346',   
'GATid401', 'GATid412', 'GATid44', 'GATid446', 'GATid499',   
'GATid591', 'GATid749', 'GATid834', 'GATid844', 'GATid931',   
'GATid980' ],
 
 [ 'GATid100', 'GATid1090', 'GATid1134', 'GATid1186', 'GATid1220',   
'GATid1402', 'GATid1410', 'GATid1546', 'GATid1547', 'GATid1595',   
'GATid1647', 'GATid1676', 'GATid1677', 'GATid1713', 'GATid397',   
'GATid490', 'GATid579', 'GATid632', 'GATid89', 'GATid898',   
'GATid991' ]
]



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
HIGH_RISK_GEOID = placements[dataset_index]





print('NUMBER of High Risk Tracts = ', len(HIGH_RISK_GEOID))

High_Risk_Prob = 0.1
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
Tract_Risk = Tract_Risk[[tract_column, 'original_risk', 'CI']]


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


fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(7, 6), gridspec_kw={'width_ratios': [3, 3.4, 3]})
merged_data.geometry.boundary.plot(color=None, edgecolor='0.2', linewidth = 0.1, ax=ax[0]) 
merged_data.plot(column=variable, cmap='BuGn', alpha=2.0, linewidth=0.0, ax=ax[0], edgecolor='0.98')

# remove the axis
ax[0].axis('off')
# add a title
ax[0].set_title('High Risk region', fontdict={'fontsize': '14', 'fontweight' : '3'})

# Create colorbar as a legend
sm = plt.cm.ScalarMappable(cmap='BuGn', norm=plt.Normalize(vmin=vmin, vmax=vmax))

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
#vmin, vmax = -3.9468759765896673, 1.16595552279113
mask = merged_data[variable] < vmin
merged_data.loc[mask, variable] = vmin
#fig, ax = plt.subplots(1, figsize=(7, 11))
merged_data.geometry.boundary.plot(color=None, edgecolor='0.2', linewidth = 0.1, ax=ax[1]) 
#merged_data.plot(column=variable, cmap='BuGn', alpha=2.0, linewidth=0.0, ax=ax[1], edgecolor='0.98', figsize=(8,12))
merged_data.plot(column=variable, cmap='BuGn', alpha=2.0, linewidth=0.0, ax=ax[1], edgecolor='0.98')
# remove the axis


# remove the axis
ax[1].axis('off')
# add a title
ax[1].set_title('Predicted Risk', fontdict={'fontsize': '14', 'fontweight' : '3'})

# Create colorbar as a legend
sm = plt.cm.ScalarMappable(cmap='BuGn', norm=plt.Normalize(vmin=vmin, vmax=vmax))

# empty array for the data range
sm._A = []
# add the colorbar to the figure
cbar = fig.colorbar(sm, fraction=0.08, ax=ax[1])

#saving our map as .png file.
#fig.savefig('Predicted_Risk.png', dpi=300)
#plt.show()
#plt.close()

#-------------------------------------------------------------------------------------

#



variable = "CI"
merged_data = merged_data.dropna(subset=[variable])

mask = merged_data[variable] > 0.05
merged_data.loc[mask, variable] = -6
#merged_data.loc[mask1, variable] = -6


variable = "original_risk"
merged_data = merged_data.dropna(subset=[variable])
merged_data.loc[mask, variable] = -6

#fig, ax = plt.subplots(1, figsize=(7, 11))
merged_data.geometry.boundary.plot(color=None, edgecolor='0.2', linewidth = 0.1, ax=ax[2]) 
merged_data.plot(column=variable, cmap='BuGn', alpha=2.0, linewidth=0.0, ax=ax[2], edgecolor='0.98')
# remove the axis
ax[2].axis('off')
# add a title
ax[2].set_title('Risk is Significant', fontdict={'fontsize': '14', 'fontweight' : '3'})

#saving our map as .png file.
fig.savefig('Predicted_Risk.png', dpi=300)
plt.show()
plt.close()

