# -*- coding: utf-8 -*-
"""
Created on Tue Sep 10 14:21:19 2019

@author: tuf86648
"""

import numpy as np
import pandas as pd
import datetime
from dateutil.relativedelta import  relativedelta
from geopy import distance
import matplotlib.pyplot as plt


alldata=pd.read_pickle("all_data_v2_fixed_stfid_DLC.pkl")

#address_data = pd.read_csv("NJCURRENTADD.csv")
#data_colon_serlected = pd.read_csv("scenario_1new.csv")
#colon_case_ids = np.array(data_colon_serlected['temple_id'])
#alldata = alldata[alldata['temple_id'].isin(colon_case_ids)]




NEWEST_WINS_FLAG = True
OLDEST_WINS_FLAG = False
LONGEST_WINS_FLAG = False
SHORTEST_WINS_FLAG = False
RANDOM_SELECTION_FLAG = False

NO_GAP_FLAG = False


date_List=[]
date_List_dict ={}

for ind,row in alldata.iterrows():
    rowdata=[]
    for tspan in range(2,23):
        st_col = "start_{0}".format(tspan)
        ls_col = "last_{0}".format(tspan) 
        stfid = "stfid_{0}".format(tspan)
        rowdata.append((row[st_col],row[ls_col], row[stfid], row['temple_id']))
        
    date_List.append(rowdata)
    date_List_dict[ int(row['temple_id'])] = rowdata



Modified_date_List={}

all_selected_date_lists = {}

highest_number_of_seg =0

ALL_Candidate_Intervals = {}


Num_Addresses_All = []
Zero_Discard_All = []
Avail_Time = []
# Iterate through all the data row by row
for key in date_List_dict.keys():
    item = date_List_dict[key]
    # take only the valid data/ discard the rest
    valid_items1=[k for k in item if (isinstance(k[0], datetime.date) or isinstance(k[1], datetime.date) )] # check if and/or
    

    # discard very small time span days
    valid_items = [k for k in valid_items1 if ( (k[1]-k[0]).days > 1)] #     
    num_of_addesses=len(valid_items)

    ##### STATS
    Num_Addresses_All.append(len(valid_items1))
    Zero_Discard_All.append(len(valid_items1) - num_of_addesses)

    time_lengths = np.array([(k[1]-k[0]).days for k in valid_items1])
    Avail_Time.append(time_lengths.sum())
    
    ####    
    
    
    final_row_data=[]
    if num_of_addesses > 0:
        if num_of_addesses >1 :
            # separate out start and end time
            start_times=[k[0] for k in valid_items]
            end_times=[k[1] for k in valid_items]
            stfids = [k[2] for k in valid_items]
            
            # sort by start time then sort by time difference
            infdate = datetime.datetime.strptime("1901-12-01", "%Y-%m-%d").date()
            to_sort = np.array([[(k[0]-infdate).days, (k[1]-k[0]).days] for k in valid_items])
            
            start_time_sorted_indices=np.lexsort((to_sort[:,1], to_sort[:,0]))
            
            sorted_start_time=[start_times[k] for k in start_time_sorted_indices]
            
            
            # arrange end times based on the sorted start time
            end_time_sortedbystart=[end_times[k] for k in start_time_sorted_indices]
            stfids_sortedbystart=[stfids[k] for k in start_time_sorted_indices]
            
            edges = list(set(sorted_start_time).union(set(end_time_sortedbystart)))
            
            sorted_edges = np.sort(edges)
            
            all_intervals_with_candidate_items = []
            
            for i in range(len(sorted_edges)-1):
                interval = (sorted_edges[i], sorted_edges[i+1])
                #find intervals
                candidate_items = []
                for j in range(len(start_time_sorted_indices)):
                    
                    if (sorted_start_time[j]  <= interval[0]) and (end_time_sortedbystart[j] >= interval[1]):
                        candidate_items.append((sorted_start_time[j], end_time_sortedbystart[j] , stfids_sortedbystart[j] ))
                all_intervals_with_candidate_items.append((interval, candidate_items)) 
                
    ALL_Candidate_Intervals[key] = all_intervals_with_candidate_items



#year_cohort =  [datetime.datetime.strptime("1920-01-01", "%Y-%m-%d").date(), datetime.datetime.strptime("1930-01-01", "%Y-%m-%d").date(),
#                datetime.datetime.strptime("1940-01-01", "%Y-%m-%d").date(), datetime.datetime.strptime("1950-01-01", "%Y-%m-%d").date(),
#                datetime.datetime.strptime("1960-01-01", "%Y-%m-%d").date(), datetime.datetime.strptime("1970-01-01", "%Y-%m-%d").date(),
#                datetime.datetime.strptime("1980-01-01", "%Y-%m-%d").date(), datetime.datetime.strptime("1990-01-01", "%Y-%m-%d").date(),
#                datetime.datetime.strptime("2000-01-01", "%Y-%m-%d").date(), datetime.datetime.strptime("2010-01-01", "%Y-%m-%d").date(),
#                datetime.datetime.strptime("2018-01-01", "%Y-%m-%d").date()]  


year_cohort = [datetime.datetime.strptime("{0}-01-01".format(k), "%Y-%m-%d").date() for k in range(1940, 2018, 10)]
year_cohort.append(datetime.datetime.strptime("2018-01-01", "%Y-%m-%d").date())


Maximum_address = 5
missing_address_time = [0 for k in year_cohort[:-1]]
address_time = [0 for k in year_cohort[:-1]]
all_possible_address_time = [[m for m in address_time] for k in range(Maximum_address)]


 
count3 =  0 
for key in ALL_Candidate_Intervals.keys():    
    count3 = count3+1
    date_of_birth = alldata[alldata['temple_id']==key].iloc[0]['dateofdx']- relativedelta(years=int(alldata[alldata['temple_id']==key].iloc[0]['age_at_dia'])) + relativedelta(years=18)
    
    if date_of_birth < year_cohort[0]:
        date_of_birth = year_cohort[0]
    items = ALL_Candidate_Intervals[key]
    
    for idx,candiadte_interval in enumerate(items):

        start = candiadte_interval[0][0]
        end = candiadte_interval[0][1]
     
        
        
        candidate_stfids = [k[2] for k in candiadte_interval[1]]
        unique_candidate_stfids = np.unique(candidate_stfids)
        num_address = len(unique_candidate_stfids)
        if num_address >= Maximum_address-1:
            num_address = Maximum_address-1
        # missing just after birth
        if idx== 0:
            if date_of_birth < start :
                start_missing = date_of_birth
                end_missing = start
                for i, yc in enumerate(year_cohort):
                    if i < len(year_cohort)-1:
                        if (start_missing >= year_cohort[i]) and (start_missing <= year_cohort[i+1]) :
                            if (end_missing >= year_cohort[i+1]):                                
                                  all_possible_address_time[0][i] = all_possible_address_time[0][i] + (year_cohort[i+1] - start_missing).days/365
                                  start_missing = year_cohort[i+1] 
                            else :
                                  all_possible_address_time[0][i] = all_possible_address_time[0][i] + (end_missing - start_missing).days/365
                                   

        
        
        
        if start < year_cohort[0]:
            start = year_cohort[0]
        if end < year_cohort[0]:
            end = year_cohort[0]
        start1 = start
        end1 = end            
        for i, yc in enumerate(year_cohort):
            if i < len(year_cohort)-1:
               if (start1 >= year_cohort[i]) and (start1 <= year_cohort[i+1]) :
                            if (end1 >= year_cohort[i+1]):    
                                 all_possible_address_time[num_address][i] = all_possible_address_time[num_address][i] + (year_cohort[i+1] - start1).days/365
                                 start1 = year_cohort[i+1] 
 
                            else :
                                 all_possible_address_time[num_address][i] = all_possible_address_time[num_address][i] + (end1 - start1).days/365
                   
                   
        
#        # next item on the list
#        if idx < len(items)-1:
#            next_dt_item = items[idx+1]
#        else:
#            next_dt_item = None
#        
#        if next_dt_item :
#            if (end - next_dt_item[0][0]).days > 10:
#                start_missing = end
#                end_missing = next_dt_item[0][0]
#                for i, yc in enumerate(year_cohort):
#                    if i < len(year_cohort)-1:
#                        if (start_missing >= year_cohort[i]) and (start_missing <= year_cohort[i+1]) :
#                            if (end_missing >= year_cohort[i+1]): 
#                                missing_address_time[i] = missing_address_time[i] + (year_cohort[i+1] - start_missing).days
#                                start_missing = year_cohort[i+1] 
#                            else : 
#                                missing_address_time[i] = missing_address_time[i] + (end_missing - start_missing).days
          
        
          
          


import pandas as pd
import numpy as np

#A = all_possible_address_time
#for k,a in enumerate(all_possible_address_time):
#    for j,b in enumerate(a):
#        all_possible_address_time[k][j] = all_possible_address_time[k][j] /365
#        

X_AXIS = ["{0}-{1}".format(k, k+10) for k in range(1940, 2009, 10)]
X_AXIS.append("2010-2018")
index = pd.Index(X_AXIS, name='')

data = {}
data["Missing Address"] = all_possible_address_time[0]
data["Single Address"] = all_possible_address_time[1]
for k in range(2,Maximum_address-1):
    col_name = "{0} Addresses".format(k)
    data[col_name] = all_possible_address_time[k]

col_name = "{0} or more Addresses ".format(Maximum_address-1)
data[col_name] = all_possible_address_time[Maximum_address-1]

df = pd.DataFrame(data, index=index)

#ax = df.plot(kind='bar', stacked=True, figsize=(12, 8))
#plt.xticks(rotation=45)
#ax.set_ylabel('Accumulative Time in Years')
#plt.savefig('missing_data_accumulative18.png', format='png')
#plt.savefig('missing_data_accumulative18.jpg', format='jpg')
#plt.savefig('missing_data_accumulative18.eps', format='eps')


#plt.savefig('missing_data_accumulative18_daniel_accumulative_daniel_from_beginning.png', format='png')
#plt.savefig('missing_data_accumulative18_daniel_accumulative_daniel_from_beginning.jpg', format='jpg')
#plt.savefig('missing_data_accumulative18_daniel_accumulative_daniel_from_beginning.eps', format='eps')

#plt.show()
#plt.close()



#ax = plt.figure(1)
#bins = np.arange(22) - 0.5
#plt.hist(Num_Addresses_All, bins)
#x_ticks = [k if k%2==0 else 200 for k in range(21) ]
#plt.xticks(x_ticks)
#plt.xlim([-1, 21])
#
#plt.title('Histogram of Number of available residential records')
#plt.xlabel('Number of available residential records')
#plt.ylabel('Number of individuals')
#figname = 'Hist_Num_Address.png'
#plt.savefig(figname, type = 'png')
#figname = 'Hist_Num_Address.eps'
#plt.savefig(figname, type = 'eps')
#plt.show()
#plt.close()



f55 = open("ASCII_ART_where_are_they_missing.txt", "w+")
gaps = []

for key in ALL_Candidate_Intervals.keys():
    records  = ALL_Candidate_Intervals[key]
    gap = 0
    oo = ""
    for r in records:
        if len(r[1]) == 0:
            gap = gap + 1
            oo = oo + " XX "
        if len(r[1]) == 1:
            oo = oo + "--->"
        if len(r[1]) > 1:
            oo = oo + "===>"
    
    f55.write(oo)
    f55.write("\n")     
    if gap > 0:
        print(oo)
    gaps.append(gap)

f55.close()
    
numgapstotal = sum(np.array(gaps) >0)
print(numgapstotal, "#########################numgapstotal")