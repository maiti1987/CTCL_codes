# -*- coding: utf-8 -*-
"""
Created on Mon Jun 24 16:34:10 2019

@author: tuf86648
"""

# -*- coding: utf-8 -*-
"""
Created on Sat Apr 28 01:58:26 2018

@author: tuf86648
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Jul 21 13:16:25 2016

@author: aniruddha
"""


import time

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as la
import pandas as pd
import gc

# Note  
# Identify a region by running kmeansSTFID >> 
# then assign HIGH_RISK_GEOID the GATids in file Prepare_Fake_Data.py and Draw_Map.py
# afterwards

#steps 1. Run Prepare_Fake_Data.py 1a. Then run Matching_ALL_Retro_MatchingEthn.v1.py
# 2. set FIRST_TIME_FLAG = 1 >>  will generate unique_place_ids
# 3. run Create_Neighborhood_Encoding.npy
# 4. make FIRST_TIME_FLAG = 0 >>  to get the results

Number_of_Simulations = 100 # 1000

FIRST_TIME_FLAG = 0
ecoding_distance_cutoff = 20.00 #in miles
lambda_hyperparameter = 0.01
# logistic            
def sigmoid(x):
  return 1 / (1 + np.exp(-x))
  
def calculaterisk(p):
    return -1 *np.log(1/p - 1)
#
#
    
def cost(X, Y, r, A):
    #N=X.shape[0] # No of training examples
    J = (-np.transpose(Y).dot(np.log(sigmoid(X.dot(r)))) - np.transpose(1-Y).dot(np.log(1-sigmoid(X.dot(r)))))
    return J

# Calculate Gradient    
def grad(X, Y, r, A):
    
     # find out the shape of the data
     m, n= X.shape
     y_p = sigmoid(X.dot(r))
     y_p=np.array(y_p)
     y_pred=y_p.reshape(m,)
     err= y_pred-Y
     
     C=X.T.dot(err)
     C=C.reshape((n, 1))
     B=A.dot(r)
    
     grad=C-B
     
     sqerr=np.sqrt(sum(n*n for n in err)/len(err))
    
     return  grad, sqerr

# Hessian     
def Hessian(X, Y, r, A ):
    m, n= X.shape
    y_p = sigmoid(X.dot(r))
    y_p=np.array(y_p)
    y_pred=y_p.reshape(m,)
    
    dg=[i*(1-i) for i in y_pred]
    R = sp.dia_matrix((dg, [0]), shape=(m, m))
    B=X.T.dot(R)
    C=sp.csr_matrix.dot(B,X)
    hess=C-A
    return hess

# prediction function
def predict(r, X, cutoff):
    m, n = X.shape
    pred = np.zeros(shape=(m, 1))

    h = sigmoid(X.dot(r))

    for it in range(0, h.shape[0]):
        if h[it] > cutoff:
            pred[it, 0] = 1
        else:
            pred[it, 0] = 0

    return pred


##start clock
tic=time.time()
#
# Data statistics



# Generate Location Data

#######################
# Load Data

data = pd.read_csv('MATCHED_Residential_History_with_weights.csv', dtype = {'ID': 'str', 'loc':'str', 'status':'str'}, parse_dates =['start', 'end'], infer_datetime_format =True)
#data = pd.read_csv('Residential_History_with_weights.csv', dtype = {'ID': 'str', 'loc':'str', 'status':'str'}, parse_dates =['start', 'end'], infer_datetime_format =True)
data['start'] = data['start'].dt.date
data['end'] = data['end'].dt.date


data = data[(data['status']=='CASE') | (data['status']=='CONTROL')]

if FIRST_TIME_FLAG:
    unique_place_ids = np.array(data['loc'].unique()) 
    np.save('unique_place_ids.npy', unique_place_ids) 
else :
    unique_place_ids = np.load('unique_place_ids.npy', allow_pickle=True) 

    unique_examples = np.array(data['ID'].unique())
    
    
    
    NumInstance=len(unique_examples)
    NumPlaces=len(unique_place_ids)
    
    X=np.zeros((NumInstance, NumPlaces))
    Y = [-1 for k in X] 
    
    grouped_data = data.groupby('ID')
    for group_name, df_group in grouped_data:
        identifier = df_group.iloc[0]['ID']
        status = df_group.iloc[0]['status']
        example_idndx = np.where(unique_examples==identifier)[0][0]
        if status == 'CASE':
            Y[example_idndx] = 1
        if status == 'CONTROL':
            Y[example_idndx] = 0
            
        for row_index, row in df_group.iterrows():
            loc = row['loc']
            loc_indx = np.where(unique_place_ids==loc)[0][0]
            start = row['start']
            end = row['end']
            weighted_time_in_month =  row['weight'] * (end - start).days/30
            X[example_idndx, loc_indx]= X[example_idndx, loc_indx] + weighted_time_in_month 
            
    
    Y = np.array(Y)
    # normalize    
    xrowsum= X.sum(axis=1)  
    
    for r,row in enumerate(X):
        if xrowsum[r]!=0:
            X[r,:]=X[r,:]/xrowsum[r]
    
    
    gc.collect()
    
    
    np.save('X.npy', X)
    
    NumInstance=len(X)
    NumPlaces=len(unique_place_ids)
    ###############################
    
    X=np.load('X.npy')
    
    
    ## compute neighborhood matrix encoding the neighborhood structure
    ##A=np.identity(NumPlaces) # Testing for now
    
    
    
    
    
    #A=sp.csc_matrix(A)
    #X=sp.csc_matrix(X)
    
    A = np.load('A_NJtrue_dist.npy')
    
    A = A < ecoding_distance_cutoff
    A = A.astype(float)
    A = lambda_hyperparameter * A
    for r,i in enumerate(unique_place_ids) :
        A[r,r] = 0 # required because  A < cutoff makes diagonal 1
        rowsum=np.sum(A[r,:])
        #print("row sum ", rowsum)
        A[r,r]=-1*rowsum
        
    
    
    
    print("building sparse matrices")    
    A=sp.csc_matrix(A)
    X=sp.csc_matrix(X)
    
    
    
    toc=time.time()
    print('Data load and processing time : ', toc-tic)
    
    for suffle_iteration in range(Number_of_Simulations):
        # Newton Rhapson
        tic = time.time()
        # Initialize initial r  
        r=np.random.rand(NumPlaces,1)
        eta= 1
        
        olderr=float("inf")
        errReduct=float("inf")
        flag=0
        for i in range(10) :
            tic1=time.time()
            if flag==0 :
                # calculate gradient and Hessian
                g, err=grad(X, Y, r, A)
                if olderr==err :
                    flag =1
                #print('iteration :  ', i, '  Error  : ', err)
                gc.collect()
                #print('calculating hessian H...')
                H=Hessian(X, Y, r, A)
                #print('calculating H inverse...')
                STEP=la.spsolve(H,g)
                STEP=STEP.reshape(NumPlaces,1)
                r=r-STEP
                errReduct=olderr-err
                print(err)
                olderr=err
                toc=time.time()
                #print('time = ', toc-tic1)
                
            
        pred=predict(r, X, 0.5)
        
        r=[k[0] for k in r]    
        # stop clock
        toc=time.time()
        print('Iteration {0} : Computation Time elapsed {1}'.format(suffle_iteration, toc-tic))
        
        
        if suffle_iteration ==0:
            tract_risks=pd.DataFrame(r,index=unique_place_ids ,columns=['original_risk'])
        else :  
            column = "Iteration_{0}".format(suffle_iteration)
            tract_risks[column] = r
            
        np.random.shuffle(Y)
        
    
    
    tract_risks.to_pickle('tract_risks_simulations.pckl')
                          
    
    tract_risks = pd.read_pickle('tract_risks_simulations.pckl')
    
    Confidence_Intervals = []
    for ind,row in tract_risks.iterrows():
        simulated_risks = []
        true_risk = row['original_risk']
        for it in range(1,Number_of_Simulations):
            column = 'Iteration_{0}'.format(it)
            r = row[column]
            simulated_risks.append(r)
            
            
        sorted_simulated_risks = np.sort(np.array(simulated_risks))  
        ci = 0
#        if true_risk < -np.log(5):
#            where_less = np.where(sorted_simulated_risks < true_risk)
#            ci = len(where_less[0])/float(Number_of_Simulations)
#        else:
#            where_greater = np.where(sorted_simulated_risks > true_risk)
#            ci = len(where_greater[0])/float(Number_of_Simulations)
    
        where_greater = np.where(sorted_simulated_risks > true_risk)
        ci = float(len(where_greater[0]))/float(Number_of_Simulations)        
        Confidence_Intervals.append(ci)   
            
        
    tract_risks['CI'] =   Confidence_Intervals  
    tract_risks.to_csv('tract_risks_simulations_withCI.csv')        
    
 