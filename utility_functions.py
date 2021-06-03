# -*- coding: utf-8 -*-
"""
Created on Wed Jun  2 18:24:24 2021

@author: mkona
"""
#main function 
def process_efficiency(stp_type, ph, temperature, i_nitrate, i_do, i_phosphate ):
    """
    take the WW imput parameters and the operating conditions to return the output pollutant concentration
    """
    if stp_type == 'ASP':
        f_nitrate, f_do, f_phosphate = asp_function(i_nitrate, i_do, i_phosphate, ph, temperature)
        
    elif stp_type == 'EA':
        f_nitrate, f_do, f_phosphate = ea_function(i_nitrate, i_do, i_phosphate, ph, temperature)
        
    elif stp_type == 'USBA':
        f_nitrate, f_do, f_phosphate = usba_function(i_nitrate, i_do, i_phosphate, ph, temperature)
        
    elif stp_type == 'wetland':
        f_nitrate, f_do, f_phosphate = wetland_function(i_nitrate, i_do, i_phosphate, ph, temperature)
    
    elif stp_type == 'USBA+EA':
        f_nitrate, f_do, f_phosphate = usba_function(i_nitrate, i_do, i_phosphate, ph, temperature)
        f_nitrate, f_do, f_phosphate = ea_function(f_nitrate, f_do, f_phosphate, ph, temperature)
    
    else:
        print('technology not modelized')
        f_nitrate, f_do, f_phosphate = i_nitrate, i_do, i_phosphate
        
    
    return f_nitrate, f_do, f_phosphate


#create processes functions according to litterature
def asp_function(i_nitrate, i_do, i_phosphate, ph, temperature):
    return i_nitrate, i_do, i_phosphate