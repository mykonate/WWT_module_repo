# -*- coding: utf-8 -*-
"""
Created on Wed Jun  2 18:24:24 2021

@author: mkona
"""
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
        # f_nitrate, f_do, f_phosphate = ea_function(f_nitrate, f_do, f_phosphate, ph, temperature)
    
    else:
        print('technology not modelized')
        f_tss, f_cod, f_bod = tss, cod , bod
        
    
    return f_tss, f_cod, f_bod


# #create processes functions according to litterature
# def asp_function(i_nitrate, i_do, i_phosphate, ph, temperature):
#     return i_nitrate, i_do, i_phosphate

def uasb_ea_function(tss, cod, bod):
    f_tss = (1-0.735)*tss
    f_cod = (1-0.78)*cod
    f_bod = (1-0.82)*bod
    return f_tss,f_cod,f_bod