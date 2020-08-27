# -*- coding: utf-8 -*-
"""
Created on Tue Mar 19 06:00:58 2019

@author: tuf86648
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from simpledbf import Dbf5


import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.datasets import make_moons, make_circles, make_classification
from sklearn.model_selection import KFold


import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.autograd import Variable


Available_Data_Cutoff = 0.9

FiveYrBack_FLAG = 0
FiveYrBack_NJ_FLAG = 0

TenYrBack_FLAG = 1
TenYrBack_NJ_FLAG = 0

FifteenYrBack_FLAG = 0
FifteenYrBack_NJ_FLAG = 0

TwentyYrBack_FLAG = 0
TwentyYrBack_NJ_FLAG = 0

ThirtyYrBack_FLAG = 0
ThirtyYrBack_NJ_FLAG = 0


FromBirth_FLAG = 0
FromBirth_NJ_FLAG = 0


# TIME_RETRO_COLUMNS.pkl is generated by Create_remove_flag_for_insufficient_time
data = pd.read_pickle("TIME_RETRO_COLUMNS.pkl")

if FiveYrBack_FLAG:
    data = data[data['AvailTime5Yback'] > Available_Data_Cutoff]

    
if FiveYrBack_NJ_FLAG:
    data = data[data['NJAvailTime5Yback'] > Available_Data_Cutoff]
    
if TenYrBack_FLAG:
    data = data[data['AvailTime10Yback'] > Available_Data_Cutoff]

if TenYrBack_NJ_FLAG:
    data = data[data['NJAvailTime10Yback'] > Available_Data_Cutoff]
    
if FifteenYrBack_FLAG:
    data = data[data['AvailTime15Yback'] > Available_Data_Cutoff]
    
if FifteenYrBack_NJ_FLAG:
    data = data[data['NJAvailTime15Yback'] > Available_Data_Cutoff]
    
if TwentyYrBack_FLAG:
    data = data[data['AvailTime20Yback'] > Available_Data_Cutoff]
    
if TwentyYrBack_NJ_FLAG:
    data = data[data['NJAvailTime20Yback'] > Available_Data_Cutoff]
    
if ThirtyYrBack_FLAG:
    data = data[data['AvailTime30Yback'] > Available_Data_Cutoff]

if ThirtyYrBack_NJ_FLAG:
    data = data[data['NJAvailTime30Yback'] > Available_Data_Cutoff]



if FromBirth_FLAG:
    data = data[data['AvailTimeFromBirth'] > Available_Data_Cutoff]

if FromBirth_NJ_FLAG:
    data = data[data['NJAvailTimeFromBirth'] > Available_Data_Cutoff]
    
    
    
    
    

data["temple_id"] = pd.to_numeric(data.temple_id, errors='coerce').fillna(0).astype(np.int64)
data["age_at_dia"] = pd.to_numeric(data.age_at_dia, errors='coerce').astype(np.int64)

data['BirthYear'] = data['YOB'].map(lambda x: x.year)

data['gen_group'] = pd.cut(data['BirthYear'], bins=[1920,1945,1965,1981, 2020], labels=['a', 'b', 'c', 'd'])


data_indices = data.index.get_values()

f = open('MatchingStat.txt', 'w+')
f2 = open('UnsucessFulmatchInfo.txt', 'w+')

f2.write("\nTotal data  {0}\n".format(len(data)))


traindata = data


# select case control
sim_data = pd.read_csv('Residential_History_with_weights.csv')
sim_data['ID'] = sim_data['ID'].astype(np.int64)

case_ids = sim_data[sim_data['status']=='CASE'].ID.unique()
# discard cases that have less residential data
discard = []
for c in case_ids:
    if c not in list(traindata['temple_id']):
        discard.append(c)
print('Taken care of in Prepare_Fake_Data.py')
print("DISCARDED BECAUSE OF LESS RESIDENTIAL DATA", len(discard))

case_ids = [i for i in case_ids if i not in discard]

control_ids = sim_data[sim_data['status']=='CONTROL'].ID.unique()

colon_train = traindata[traindata['temple_id'].isin(control_ids)]
nhl_train_CTCL = traindata[traindata['temple_id'].isin(case_ids)]
nhl_train_CTCL_indices = nhl_train_CTCL.index.get_values()

not_selected_so_far = list(colon_train.temple_id)
colon_train_remaining = colon_train[colon_train['temple_id'].isin(not_selected_so_far)]
unsuccessful_array=[]
less_than_three_control = []
select_so_far = []
case_count = 0
for ind,row in nhl_train_CTCL.iterrows():
    case_count =  case_count +1
    towrite_str = '\n{0} {1}---------------------------\n'.format(case_count, len(select_so_far))
    f.write(towrite_str)
    sex = row['sex_rec']
    age_at_dia = row['age_at_dia']
    yob = row['YOB'].year
    EthRace = row['EthRace']
    gen_group = row['gen_group']
    Select_for_this = []
    print("################## iteration : ", ind, "Temple ID ", row['temple_id'], "###########")   
    for m in range(5):
        match_string = "\n{0} {1} ".format(row['temple_id'], m)
        # GENDER
        matches1 = colon_train_remaining[colon_train_remaining['sex_rec']==sex]
        if len(matches1) > 0:
            match_string = match_string + "  MATCH_GENDER  "
            
            # RACE-Ethnicity
            matches2 = matches1[matches1['EthRace']==EthRace]
            if len(matches2) > 0 :
                match_string = match_string + "  MATCH_EthRace" 
                
                # AGE AT DIA
                matches3 = matches2[matches2['age_at_dia']==age_at_dia]
                if len(matches3) == 0: # if age at dia did not match look =-5
                    matches3 = matches2[(matches2['age_at_dia'] > (age_at_dia-5)) & ((matches2['age_at_dia'] < (age_at_dia+5)))]
                    if len(matches3) > 0:
                        match_string = match_string + "  MATCH_AgeDia+-5"
                else:
                    match_string = match_string + "  MATCH_Exact_AgeDia" 
                
                if len(matches3) > 0:
                    # YOB
                    matches2yb = matches3[matches3['BirthYear']==yob]   
                    if len(matches2yb) == 0: # ifYOB did not match look =-5
                        matches2yb = matches3[(matches3['BirthYear'] > (yob-5)) & ((matches3['BirthYear'] < (yob + 5)))]            
                        if len(matches2yb) > 0:
                            match_string = match_string + "  MATCH_YOB+-5"
                        else :
                            matches2yb = matches3[matches3['gen_group']==gen_group]   
                            if len(matches2yb) > 0:
                                  match_string = match_string + "  MATCH_GEN_COHORT"
                    else :
                        match_string = match_string + "  MATCH_ExactYOB"
                        
                    if len(matches2yb) > 0:                                              
                        print("--success >> remaining ", len(colon_train_remaining)) 
                        match3indices = matches2yb.temple_id ###################
                        selected_match3_index = np.random.choice(match3indices, 1, replace=False)  
                                        
                        for k1 in selected_match3_index:
                            match_string = match_string + "  Colon-Temple-ID = {0}".format(k1)
                            select_so_far.append(k1)
                            Select_for_this.append(k1)
                        not_selected_so_far = [it for it in  not_selected_so_far if it not in selected_match3_index]
                        colon_train_remaining = colon_train_remaining[colon_train_remaining['temple_id'].isin(not_selected_so_far)]
                                                
                        
                    else :
                        print("---- No age at dia match matching -- discarding ") 
                        f2.write("\n-------------------------\n {0} MATCHED ONLY {1} ".format(row['temple_id'], m))
                        for cotr in Select_for_this:
                            f2.write("  {0}".format(cotr))
                        f.write("\n---- No age at dia match matching -- discarding \n")
                        f2.write("\n---- No age at dia match --  \n")  
                        unsuccessful_array.append((row['temple_id'], m))
                        
                        # if less than 3 matches remove selected items
                        if m <3:
                            for r in Select_for_this:
                                select_so_far.remove(r)
                                not_selected_so_far.append(r)
                        break         
                
                else:
                    print("---- No YOB matching -- discarding ") 
                    f2.write("\n-------------------------\n {0} MATCHED ONLY {1} ".format(row['temple_id'], m))
                    for cotr in Select_for_this:
                        f2.write("  {0}".format(cotr))
                    f.write("\n---- No YOB match -- discarding \n") 
                    f2.write("\n---- No YOB match --  \n")  
                    unsuccessful_array.append((row['temple_id'], m))
                     # if less than 3 matches remove selected items
                    if m <3:
                        for r in Select_for_this:
                            select_so_far.remove(r)
                            not_selected_so_far.append(r)                  
                    
                    break
                    
                
                
            else:
               print("---- No Ethnicity-Race matching -- discarding")  
               f2.write("\n-------------------------\n {0} MATCHED ONLY {1} ".format(row['temple_id'], m))               
               for cotr in Select_for_this:
                    f2.write("  {0}".format(cotr))
                    
               f.write("\n---- No Ethnicity-Race matching -- discarding \n")  
               f2.write("\n---- No Ethnicity-Race match --  \n")  
               unsuccessful_array.append((row['temple_id'], m))
                                    # if less than 3 matches remove selected items
               if m <3:
                    for r in Select_for_this:
                        select_so_far.remove(r)
                        not_selected_so_far.append(r)   
               break
                

                    
            
        else :
           print("---- No Gender matching -- discarding")  
           f2.write("\n-------------------------\n {0} MATCHED ONLY {1} ".format(row['temple_id'], m))
           for cotr in Select_for_this:
               f2.write("  {0}".format(cotr))
           f.write("\n---- No Gender matching -- discarding \n")  
           f2.write("\n---- No Gender match --  \n")  
           unsuccessful_array.append((row['temple_id'], m))
           # if less than 3 matches remove selected items
           if m <3:
                for r in Select_for_this:
                    select_so_far.remove(r)
                    not_selected_so_far.append(r) 
           break
        
        f.write(match_string)
    

            

f.close()   
f2.close()             
#colon_data = colon_train[colon_train['temple_id'].isin(select_so_far)]
#colon_data.to_csv('matching_colons.csv')      
#nhl_train_CTCL.to_csv('matching_nhl.csv') 

unsucessfully__matched_cases = [a[0] for a in unsuccessful_array if a[1]<3]
less_than_five_match = [a[0] for a in unsuccessful_array if a[1]>2]
matched_sim_data = sim_data[sim_data['ID'].isin(select_so_far) | sim_data['ID'].isin(case_ids)]
matched_sim_data = matched_sim_data[~matched_sim_data['ID'].isin(unsucessfully__matched_cases)]

matched_sim_data.to_csv('MATCHED_Residential_History_with_weights.csv') 


print(matched_sim_data.groupby(by="status")['ID'].nunique())
print('shortage ', sum([5-a[1] for a in unsuccessful_array if a[1]>2]))

