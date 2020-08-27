# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 22:04:46 2019

@author: tuf86648
"""


import time

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as la
import pandas as pd
from simpledbf import Dbf5
from geopy import distance

UStract = Dbf5('USA_tract_Coordinates.dbf')
UStract_data=UStract.to_dataframe()


## compute precision matrix encoding the neighborhood structure
##A=np.identity(NumPlaces) # Testing for now

# read aggregated tracts
AGGREGATION_FLAG = True
if AGGREGATION_FLAG:
    agg_CT_List = Dbf5('Agg_CT_List_Coords.dbf')
    agg_CT_List=agg_CT_List.to_dataframe()
    agg_CT_List_reindexed = agg_CT_List.set_index("GEOID10")


unique_place_ids = np.load('unique_place_ids.npy', allow_pickle=True ) 
NumPlaces = len(unique_place_ids)


A1=np.zeros(shape=(NumPlaces, NumPlaces))
A=np.zeros(shape=(NumPlaces, NumPlaces))
cutoff=20.00
lon=[]
lat=[]

for r,i in enumerate(unique_place_ids) :
      found = False
      if AGGREGATION_FLAG:
          Xloc = agg_CT_List_reindexed[agg_CT_List_reindexed.GATid == i]          
          if len(Xloc) >= 1:
              Xloc = Xloc.iloc[0]
              found = True              
      else :
          Xloc=UStract_data[UStract_data.GEOID10==str(int(float(i)))]
          if len(Xloc)==1:
             found = True 
          
      print("row  ", r)
      if found:
          lon.append(float(Xloc.POINT_X))
          lat.append(float(Xloc.POINT_Y))
      else :
          print("can not find tract ", i)
          lon.append(0.0)
          lat.append(0.0)

lamb=0.05
for r,i in enumerate(unique_place_ids) :
   print("row  :  ", r)
   for c,j in enumerate(unique_place_ids) :
       if r > c :
           try :
               if lon[r]==0.0 or lon[c]==0.0:
                   print("Can not find tract ")
                   print(i,j)
                   dist=10000000
               else :
                   #dist=np.sqrt((lon[r]-lon[c])**2 + (lat[r]-lat[c])**2 )
                   dist = distance.distance((lat[c], lon[c]), (lat[r], lon[r])).miles
                   #print('Distance = ', dist)
           except :
               print("Can not find tract ")
               print(i,j)
               dist=10000000
           A1[r,c]=dist
           A1[c,r]=dist
           if dist < cutoff :
               A[r,c]=1
               A[c,r]=1


np.save('A_NJtrue_dist.npy', A1)















#### old code ####


#for r,i in enumerate(unique_place_ids) :
#      Xloc=UStract_data[UStract_data.GEOID10==str(i)]
#      print("row  ", r)
#      if len(Xloc)==1:
#          lon.append(float(Xloc.POINT_X))
#          lat.append(float(Xloc.POINT_Y))
#      else :
#          print("can not find tract ", i)
#          lon.append(0.0)
#          lat.append(0.0)
#
#lamb=0.01
#for r,i in enumerate(unique_place_ids) :
#   print("row  :  ", r)
#   for c,j in enumerate(unique_place_ids) :
#       if r > c :
#           try :
#               if lon[r]==0.0 or lon[c]==0.0:
#                   print("Can not find tract ")
#                   print(i,j)
#                   dist=10000000
#               else :
#                   #dist=np.sqrt((lon[r]-lon[c])**2 + (lat[r]-lat[c])**2 )
#                   dist = distance.distance((lat[c], lon[c]), (lat[r], lon[r])).miles
#           except :
#               print("Can not find tract ")
#               print(i,j)
#               dist=10000000
#           A1[r,c]=dist
#           A1[c,r]=dist
#           if dist < cutoff :
#               A[r,c]=1
#               A[c,r]=1
#
#
#np.save('A_NJtrue_dist_lamb0.01.npy', A1)
#np.save('A_NJcutoff_0_05.npy', A)
          
#for r,i in enumerate(unique_place_ids) :
#    rowsum=np.sum(A[r,:])
#    print("row sum ", rowsum)
#    A[r,r]=-1*rowsum
    
