# -*- coding: utf-8 -*-
"""
Created on Tue Jun 16 01:06:21 2020

@author: tuf86648
"""
import random
import pandas as pd
from simpledbf import Dbf5
import datetime

# simulated dataset
Num_Patients = 1000
Gender_List = [1,2]
Race_List = [1,2,3,4, 5]
Poverty_Categories = [1,2,3,4]

patient_ids = [i+100000 for i in range(Num_Patients)]
data = pd.DataFrame(patient_ids, columns=['ids'])

genders = random.choices(Gender_List, k=Num_Patients)
data['gender'] = genders

races = random.choices(Race_List, k=Num_Patients)
data['race'] = races


UStract = Dbf5('USA_tract_Coordinates.dbf')
UStract_data=UStract.to_dataframe()

NJ_tract_slice = UStract_data[UStract_data['GEOID10'].str.startswith('34', na=False)]
NJ_tract = NJ_tract_slice.copy()


poverty_values = random.choices(Poverty_Categories, k=len(NJ_tract))
NJ_tract['poverty_category'] = poverty_values


def generate_random_dates(start_date, end_date):
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days   
    random_number_of_days = random.randrange(days_between_dates)
    random_date = start_date + datetime.timedelta(days=random_number_of_days)
    return random_date


def generate_random_time_segments(start_date, end_date):
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days  
    total_consume = 0
    start_time = start_date
    return_list = []
    while total_consume < days_between_dates:
        random_number_of_days = random.randrange(2*days_between_dates//random.randint(1,4))
        end_time = start_time + datetime.timedelta(days=random_number_of_days)
        total_consume = total_consume + random_number_of_days
        if end_time < end_date:
            return_list.append([start_time,end_time,random_number_of_days])
            start_time = end_time
        
    return_list.append([start_time, end_date, (end_date - start_time).days])
    return return_list

max_addresses = 0
all_addresses = []
for indx, row in data.iterrows():
    patient_id = row['ids']
    time_start = generate_random_dates(datetime.date(1990, 1, 1), datetime.date(1995, 1, 1))
    time_end = generate_random_dates(datetime.date(1995, 1, 1), datetime.date(2000, 1, 1))
    
    time_segments = generate_random_time_segments(time_start, time_end)
    
    time_segment_and_address = []
    
    for i in range(len(time_segments)):
        sample_locs = NJ_tract.sample()
        loc = sample_locs.iloc[0]['GEOID10']
        poverty = sample_locs.iloc[0]['poverty_category']
        
        temp_info = time_segments[i]
        temp_info.append(loc)
        temp_info.append(poverty)
        time_segment_and_address.append(temp_info)
    
    all_addresses.append(time_segment_and_address)
    if max_addresses < len(time_segments):
        max_addresses =  len(time_segments)
        
empty_col = ['' for i in range(len(data))]

for tspan in range(max_addresses):
    st_col = "start_date_{0}".format(tspan)
    ls_col = "end_date_{0}".format(tspan) 
    time_col = "days_{0}".format(tspan)
    loc = "loc_{0}".format(tspan)
    poverty_col = "poverty_{0}".format(tspan)
    
    data[st_col] = empty_col
    data[ls_col] = empty_col
    data[loc] = empty_col
    data[poverty_col] = empty_col
    
               
for tspan in range(max_addresses):
    st_col = "start_date_{0}".format(tspan)
    ls_col = "end_date_{0}".format(tspan) 
    time_col = "days_{0}".format(tspan)
    loc = "loc_{0}".format(tspan)    
    poverty_col = "poverty_{0}".format(tspan)
    
    start_dates = [k[tspan][0]  if len(k) > tspan else '' for k in all_addresses]
    data[st_col] = start_dates
    
    end_dates = [k[tspan][1]  if len(k) > tspan else '' for k in all_addresses]
    data[ls_col] = end_dates
        
    time_days = [k[tspan][2]  if len(k) > tspan else '' for k in all_addresses]
    data[time_col] = time_days

    loc_list = [k[tspan][3]  if len(k) > tspan else '' for k in all_addresses]
    data[loc] = loc_list
    
    poverty_values = [k[tspan][4]  if len(k) > tspan else '' for k in all_addresses]
    data[poverty_col] = poverty_values

        
        
data.to_csv('simulated_data.csv')         
NJ_tract.to_csv('simulated_stfid_poverty.csv')       

    
    



