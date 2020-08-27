# -*- coding: utf-8 -*-
"""
Created on Wed Dec  4 11:51:49 2019

@author: tuf86648
"""


from sklearn.cluster import KMeans
import numpy as np
from simpledbf import Dbf5

agg_CT_List = Dbf5('Agg_CT_List_Coords.dbf')
agg_CT_List=agg_CT_List.to_dataframe()
agg_CT_List_reindexed = agg_CT_List.set_index("GEOID10")


X = [agg_CT_List_reindexed['GATid'], agg_CT_List_reindexed['GATx'], agg_CT_List_reindexed['GATy']]
X = np.array(X).T
y_pred = KMeans(n_clusters=8).fit_predict(X[:, 1:])

Cluster_No = 3
X1 = X[np.where(y_pred==Cluster_No)][:,0]
X1 = np.unique(X1)
st = '[ '
for ix, x in enumerate(X1):    
    if ix % 5 ==0 and ix !=0:
        st = st   + '  \n\r'
    st = st +  "'" + x +  "'" + ', '
st = st[:-2] + ' ]'
print(st)