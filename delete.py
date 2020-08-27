# -*- coding: utf-8 -*-
"""
Created on Sat Jul  4 23:59:03 2020

@author: aniruddha maiti
"""

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

    where_less = np.where(sorted_simulated_risks > true_risk)
    ci = (len(where_less[0])*100.0)/(Number_of_Simulations)    
    Confidence_Intervals.append(ci)  