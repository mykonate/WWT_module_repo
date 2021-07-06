# -*- coding: utf-8 -*-
"""
Created on Wed Jun  2 18:24:24 2021

@author: mkona
"""

#function which reads the different technology given in the csv file for each stp and return a list

def read_technology_type(stp_type):
    technology_combination = stp_type.split('/')
    return technology_combination
    
    
def total_efficiency(stp_type, i_tss, i_cod, i_bod):
    technology_combination = read_technology_type(stp_type)
    tss, cod, bod =  i_tss, i_cod, i_bod
    for technology in technology_combination:
        tss, cod, bod = process_efficiency(technology, tss, cod, bod)
    return tss, cod, bod


#main function 
def process_efficiency(stp_type, tss, cod , bod ):
    """
    take the WW imput parameters and the operating conditions to return the output pollutant concentration
    """
    if stp_type == 'ASP':
        f_tss, f_cod, f_bod  = asp_function(tss, cod, bod)
        
    elif stp_type == 'EA':
        f_tss, f_cod, f_bod  = ea_function(tss, cod, bod)
        
    elif stp_type == 'USBA':
        f_tss, f_cod, f_bod  = usba_function(tss, cod, bod)
        
    elif stp_type == 'wetland':
        f_tss, f_cod, f_bod  = wetland_function(tss, cod, bod)
    
    elif stp_type == 'UASB+EA':
        f_tss, f_cod, f_bod = uasb_ea_function(tss, cod, bod)
       
    
    
    else:
        print('technology not modelized')
        f_tss, f_cod, f_bod = tss, cod , bod
        
    
    return f_tss, f_cod, f_bod


# #create processes functions according to litterature


def uasb_ea_function(tss, cod, bod):
    f_tss = (1-0.735)*tss
    f_cod = (1-0.78)*cod
    f_bod = (1-0.82)*bod
    return f_tss,f_cod,f_bod

def wetland_function(tss, cod, bod):
    f_tss = (1-0.80)*tss
    f_cod = (1-0.45)*cod
    f_bod = (1-0.66)*bod
    return f_tss,f_cod,f_bod