# -*- coding: utf-8 -*-
"""
Created on Fri Nov 30 13:11:55 2018

@author: tuf86648
"""



import numpy as np
import pandas as pd
import datetime
from dateutil.relativedelta import  relativedelta
from geopy import distance
import matplotlib.pyplot as plt
from simpledbf import Dbf5


#AGGREGATION FLAG
AGGREGATION_FLAG = True
if AGGREGATION_FLAG:
    agg_CT_List = Dbf5('Agg_CT_List_Coords.dbf')
    agg_CT_List=agg_CT_List.to_dataframe()
    agg_CT_List_reindexed = agg_CT_List.set_index("GEOID10")

# Terminate date None means use dgx date as cutoff
Terminate_date =  datetime.datetime.strptime("2005-12-01", "%Y-%m-%d").date() #None

case_data = pd.read_csv("matchingCTCL_nhl.csv")
control_data = pd.read_csv("matchingCTCL_colons.csv")

case_ids = []
for indx, row in case_data.iterrows():
    case_ids.append(row['temple_id'])  

control_ids = []
for indx, row in control_data.iterrows():
    control_ids.append(row['temple_id'])  

# concatenate case and controls to iterate 
data = pd.concat([case_data, control_data], ignore_index=True)

# write data in csv Only looking back 
f_out = open('Residential_History.csv', 'w+')
f_out.write("ID,start,end,loc,status\n")

# years to look back fron date of diagnosis How_Many_Years_Retro years
How_Many_Years_Retro = 15

# iterate data and write csv
for ind,row in data.iterrows():
    rowdata=[]
    status = "NOT USED"
    
    if row['temple_id'] in case_ids:
        status = "CASE"
    if row['temple_id'] in control_ids:
        status =  "CONTROL"
    
    if Terminate_date is None:
        dateofdx = datetime.datetime.strptime(row['dateofdx'], '%m/%d/%Y').date()
    else :
        dateofdx = Terminate_date
    dateYback = dateofdx - relativedelta(years=How_Many_Years_Retro)

#    for tspan in range(2,23):
#        st_col = "start_{0}".format(tspan)
#        ls_col = "last_{0}".format(tspan) 
#        stfid = "stfid_{0}".format(tspan)
    
    for tspan in range(2,40):
        st_col = "Nsrt_{0}".format(tspan)
        ls_col = "Nlst_{0}".format(tspan) 
        stfid = "Nloc_{0}".format(tspan)
        
        
        # check if valid data
        if ((not pd.isna(row[st_col])) and (not pd.isna(row[ls_col])) and (not pd.isna(row[stfid])) and (".." not in str(row[stfid]))):
            
            srtdate = datetime.datetime.strptime(row[st_col], '%m/%d/%Y').date()
            enddate = datetime.datetime.strptime(row[ls_col], '%m/%d/%Y').date()
            
            #  year back ########################################################### check this logic carefully ----- might be wrong #######################################
            if (enddate >= dateYback) and (srtdate <= dateofdx) :
                # truncate if outside 5 years
                if srtdate <= dateYback:
                    srtdate = dateYback
                if enddate >= dateofdx:
                    enddate = dateofdx            
            
            
                str_stfid = str(int(float(row[stfid])))
                f_out.write("{0},{1},{2},{3},{4}\n".format(row['temple_id'],srtdate,  enddate, str_stfid, status))

f_out.close()

# read residential data split time segments by boundary. and give weight
res_data = pd.read_csv('Residential_History.csv', dtype= {'ID': str , 'loc': str , 'status': str }, parse_dates =['start', 'end'], infer_datetime_format =True)
res_data['start'] = res_data['start'].dt.date
res_data['end'] = res_data['end'].dt.date

# write data in csv 
f_weight = open('Residential_History_with_weights.csv', 'w+')
f_weight.write("ID,start,end,loc,status,weight\n")

dummy_outside_location_address = '99999999999'

grouped_data = res_data.groupby('ID')
infdate = datetime.datetime.strptime("1000-12-01", "%Y-%m-%d").date()
for group_name, df_group in grouped_data:
    date_List_dict ={}
    identifier = df_group.iloc[0]['ID']
    residence_list = []
    for row_index, row in df_group.iterrows():
        residence_list.append([row['start'], row['end'], row['loc'], row['status']])
    
    valid_items1=[k for k in residence_list if (isinstance(k[0], datetime.date) or isinstance(k[1], datetime.date) )]    
    valid_items = [k for k in valid_items1 if ( (k[1]-k[0]).days > 1)] # 

    num_of_addesses=len(valid_items)
    if num_of_addesses > 0:
        start_times=[k[0] for k in valid_items]
        end_times=[k[1] for k in valid_items]
        addresses = [k[2] for k in valid_items]
        statuses = [k[3] for k in valid_items]
        
        
        to_sort = np.array([[(k[0]-infdate).days, (k[1]-k[0]).days] for k in valid_items])
        start_time_sorted_indices=np.lexsort((to_sort[:,1], to_sort[:,0]))        
        sorted_start_time=[start_times[k] for k in start_time_sorted_indices]
        
        # other list values based on the sorted start time
        end_time_sortedbystart=[end_times[k] for k in start_time_sorted_indices]
        addresses_sortedbystart=[addresses[k] for k in start_time_sorted_indices]  
        statuses_sortedbystart=[statuses[k] for k in start_time_sorted_indices]  
        
        edges = list(set(sorted_start_time).union(set(end_time_sortedbystart)))
        sorted_edges = np.sort(edges)
        
        all_intervals_with_candidate_items = []
        for i in range(len(sorted_edges)-1):
            interval = (sorted_edges[i], sorted_edges[i+1])            
            candidate_items = []
            for j in range(len(start_time_sorted_indices)):               
                if (sorted_start_time[j]  <= interval[0]) and (end_time_sortedbystart[j] >= interval[1]):
                    candidate_items.append((sorted_start_time[j], end_time_sortedbystart[j] , addresses_sortedbystart[j], statuses_sortedbystart[j] ))
            all_intervals_with_candidate_items.append((interval, candidate_items)) 
        
        for item in all_intervals_with_candidate_items:
            if len(item[1])>0:
                weight = 1/float(len(item[1]))
                for candidate_addresses in item[1]:
                    if candidate_addresses[2][0:2] == '34':
                        location_identifier = candidate_addresses[2]
                        if AGGREGATION_FLAG:
                            location_identifier = agg_CT_List_reindexed.loc[location_identifier].GATid
                        f_weight.write("{0},{1},{2},{3},{4},{5}\n".format(identifier ,item[0][0],  item[0][1], location_identifier , candidate_addresses[3], weight ))
                    else :
                        f_weight.write("{0},{1},{2},{3},{4},{5}\n".format(identifier ,item[0][0],  item[0][1], dummy_outside_location_address , candidate_addresses[3], weight ))
    
            
f_weight.close()