# -*- coding: utf-8 -*-
"""
Created on Wed Jun  2 18:24:24 2021

@author: mkona
"""

#function which reads the different technology given in the csv file for each stp and return a list

def read_technology_type(stp_type):
    technology_combination = stp_type.split('+')
    return technology_combination
    
    



#Preliminary and primary treatment to be taken into account
#We will consider coarse screen and grit chamber as preliminary treatment having no influence on the pollutant concentrations (not exactly true for SS)
#Primary treatment is only a primary sedimentation, affecting only TSS, which would remove up to 70% TSS 
# def primary_treatment(tss):
#     f_tss = (1-0.25) * tss
#     return f_tss

#main function 
def process_efficiency(stp_type, tss, cod , bod, nitrate, TN, ammonia, phosphate, TP ):
    """
    take the WW imput parameters and the operating conditions to return the output pollutant concentration
    """
    if stp_type == 'ASP':
        f_tss, f_cod, f_bod, f_nitrate, f_TN, f_ammonia, f_phosphate, f_TP  = asp_function(tss, cod, bod, nitrate, TN, ammonia, phosphate, TP)
        
    elif stp_type == 'EA':
        f_tss, f_cod, f_bod, f_nitrate, f_TN, f_ammonia, f_phosphate, f_TP  = ea_function(tss, cod, bod, nitrate, TN, ammonia, phosphate, TP)
        
    elif stp_type == 'UASB':
        f_tss, f_cod, f_bod, f_nitrate, f_TN, f_ammonia, f_phosphate, f_TP  = uasb_function(tss, cod, bod, nitrate, TN, ammonia, phosphate, TP)
        
    
    elif stp_type == 'SBR':
        f_tss, f_cod, f_bod, f_nitrate, f_TN, f_ammonia, f_phosphate, f_TP  = sbr_function(tss, cod, bod, nitrate, TN, ammonia, phosphate, TP)
    
    elif stp_type == 'MBR':
        f_tss, f_cod, f_bod, f_nitrate, f_TN, f_ammonia, f_phosphate, f_TP  = mbr_function(tss, cod, bod, nitrate, TN, ammonia, phosphate, TP)
    
    elif stp_type == 'MBBR':
        f_tss, f_cod, f_bod, f_nitrate, f_TN, f_ammonia, f_phosphate, f_TP  = mbbr_function(tss, cod, bod, nitrate, TN, ammonia, phosphate, TP)
    
    elif stp_type == 'ABR':
        f_tss, f_cod, f_bod, f_nitrate, f_TN, f_ammonia, f_phosphate, f_TP  = abr_function(tss, cod, bod, nitrate, TN, ammonia, phosphate, TP)
    
    elif stp_type == 'UASB+EA':
        f_tss, f_cod, f_bod, f_nitrate, f_TN, f_ammonia, f_phosphate, f_TP  = uasb_ea_function(tss, cod, bod, nitrate, TN, ammonia, phosphate, TP)
    
    else:
        print('technology not modelized')
        f_tss, f_cod, f_bod, f_nitrate, f_TN, f_ammonia, f_phosphate, f_TP  = tss, cod , bod, nitrate, TN, ammonia, phosphate, TP
        
    
    return f_tss, f_cod, f_bod, f_nitrate, f_TN, f_ammonia, f_phosphate, f_TP


#create processes functions according to litterature




def wetland_efficiency(tss, cod, bod, nitrate, TN, ammonia, phosphate, TP):
    f_tss = (1-0.67) * tss
    f_cod = (1-0.45) * cod
    f_bod = (1-0.66) * bod
    f_nitrate = (1-0.9) * nitrate
    f_TN = (1-0.60) * TN
    f_ammonia = (1-0.89) * ammonia
    f_phosphate = (1-0.40) * phosphate
    f_TP = (1-0.70) * TP
    return f_tss,f_cod,f_bod, f_nitrate, f_TN, f_ammonia, f_phosphate, f_TP

def asp_function(tss, cod, bod, nitrate, TN, ammonia, phosphate, TP):
    f_tss = (1-0.80) * tss
    f_cod = (1-0.83) * cod
    f_bod = (1-0.86) * bod
    f_nitrate = (1+4.80) * nitrate
    f_TN = (1-0.60) * TN
    f_ammonia = (1-0.84) * ammonia
    f_phosphate = 0
    f_TP = 0  
    return f_tss,f_cod,f_bod, f_nitrate, f_TN, f_ammonia, f_phosphate, f_TP
    
def uasb_function(tss, cod, bod, nitrate, TN, ammonia, phosphate, TP):
    f_tss = (1-0.60) * tss
    f_cod = (1-0.67) * cod
    f_bod = (1-0.64) * bod
    f_nitrate = (1-0.90) * nitrate
    f_TN = (1-0.16) * TN
    f_ammonia = (1-0.04) * ammonia
    f_phosphate = 0
    f_TP = 0
    return f_tss,f_cod,f_bod, f_nitrate, f_TN, f_ammonia, f_phosphate, f_TP

def ea_function(tss, cod, bod, nitrate, TN, ammonia, phosphate, TP):
    f_tss = (1-0.69) * tss
    f_cod = (1-0.7712) * cod
    f_bod = (1-0.8444) * bod
    f_nitrate = (1-0.72) * nitrate
    f_TN = (1-0.7071) * TN
    f_ammonia = (1-0.29) * ammonia
    f_phosphate = (1-0.1325) * phosphate
    f_TP = 0
    return f_tss,f_cod,f_bod, f_nitrate, f_TN, f_ammonia, f_phosphate, f_TP

def sbr_function(tss, cod, bod, nitrate, TN, ammonia, phosphate, TP):
    f_tss = (1-0.69) * tss
    f_cod = (1-0.93) * cod
    f_bod = (1-0.90) * bod  
    f_nitrate = 0
    f_TN = (1-0.71) * TN
    f_ammonia = (1-0.62) * ammonia
    f_phosphate = (1-0.85) * phosphate
    f_TP = (1-0.84) * TP
    return f_tss,f_cod,f_bod, f_nitrate, f_TN, f_ammonia, f_phosphate, f_TP

def mbr_function(tss, cod, bod, nitrate, TN, ammonia, phosphate, TP):
    f_tss = (1-0.67) * tss
    f_cod = (1-0.96) * cod
    f_bod = (1-0.99) * bod   
    f_nitrate = 0
    f_TN = (1-0.96) * TN
    f_ammonia = (1-0.93) * ammonia
    f_phosphate = 0
    f_TP = (1-0.79) * TP
    return f_tss,f_cod,f_bod, f_nitrate, f_TN, f_ammonia, f_phosphate, f_TP

def mbbr_function(tss, cod, bod, nitrate, TN, ammonia, phosphate, TP):
    f_tss = (1-0.85) * tss
    f_cod = (1-0.86) * cod
    f_bod = (1-0.94) * bod
    f_nitrate = 0
    f_TN = (1-0.92) * TN
    f_ammonia = 0
    f_phosphate = 0
    f_TP = 0
    return f_tss,f_cod,f_bod, f_nitrate, f_TN, f_ammonia, f_phosphate, f_TP

def abr_function(tss, cod, bod, nitrate, TN, ammonia, phosphate, TP):
    f_tss = (1-0.61) * tss
    f_cod = (1-0.60) * cod
    f_bod = (1-0.45) * bod   
    f_nitrate = 0
    f_TN = 0
    f_ammonia = (1+0.40) * ammonia
    f_phosphate = 0
    f_TP = (1+0.21) * TP
    return f_tss,f_cod,f_bod, f_nitrate, f_TN, f_ammonia, f_phosphate, f_TP

def uasb_ea_function(tss, cod, bod, nitrate, TN, ammonia, phosphate, TP):
    f_tss = (1-0.79) * tss
    f_cod = (1-0.89) * cod
    f_bod = (1-0.88) * bod   
    f_nitrate = (1-0.29) * bod  
    f_TN = (1-0.545) * ammonia
    f_ammonia = (1-0.72) * ammonia
    f_phosphate = (1-0.133)
    f_TP = 0
    return f_tss,f_cod,f_bod, f_nitrate, f_TN, f_ammonia, f_phosphate, f_TP   





#cost functions 
def total_cost(stp_type,stp_capacity,treated_volume,design_BOD, treated_BOD ):
    technology_combination = read_technology_type(stp_type)
    capital_costs , O_M_costs = 0 , 0  
    for technology in technology_combination:
       capital_costs , O_M_costs = capital_costs + process_cost(technology,stp_capacity,treated_volume,design_BOD, treated_BOD )[0] , O_M_costs + process_cost(technology,stp_capacity,treated_volume,design_BOD, treated_BOD )[1]
    return capital_costs, O_M_costs


def process_cost(stp_type,stp_capacity,treated_volume,design_BOD, treated_BOD):
    """
    take the STP capacity and treated volume to return the capital costs and the O&M costs of each technology
    """
    #capital costs is in US$/m3/d or US$/PE and the stp_capacity/treated_volume are in m3/d
    #PE is the popultaion equivalent calculated from the total BOD load per day and the BOD produced by one inhab per day
   
    design_PE = design_BOD/0.060
    treated_PE = treated_BOD/0.060
    
    if stp_type == 'UASB':
        capital_costs = 494 * stp_capacity**(-0.2)
        O_M_costs = 457 * treated_volume**(-0.49) * 365
        
    
    elif stp_type == 'ASP':
        capital_costs = 0.206 * (design_PE * 10**(-3))**(0.954) * 10**(6)
        O_M_costs = 0.022 * (treated_PE* 10**(-3))**(0.672) * 10**(6)
        
        
    elif stp_type == 'EA':
        capital_costs = 0.206 * (design_PE * 10**(-3))**(0.775) * 10**(6)
        O_M_costs = 0.0098 * (treated_PE* 10**(-3))**(0.763) * 10**(6)
             
        
    elif stp_type == 'MBR':
        capital_costs = 1.18 * 82147 * stp_capacity **(-0.495) #multiplication by 1.18 to change the currency 
        O_M_costs = 1.18 * 4.4499 * treated_volume **(-0.34)
         
    elif stp_type == 'SBR':
        capital_costs = 0.75 * 1.18 * 82147 * stp_capacity **(-0.495) #25% less expensive than MBR
        O_M_costs = 0.75 * 1.18 * 4.4499 * treated_volume **(-0.34)
        
    elif stp_type == 'Wetland':
        capital_costs = 494 * stp_capacity **(-0.2)
        O_M_costs = 457 * treated_volume **(-0.49)
       
    elif stp_type == 'MBBR':
        capital_costs = 0.67 * 1.18 * 82147 * stp_capacity **(-0.495) #33% less expensive than MBR
        O_M_costs = 0.67 * 1.18 * 4.4499 * treated_volume **(-0.34)
        return capital_costs, O_M_costs

    elif stp_type == 'ABR':
        capital_costs = 0.25 * (494 * stp_capacity **(-0.2)) #the cheapest
        O_M_costs = 0.25 * (457 * treated_volume **(-0.49))
    
    elif stp_type == 'UASB+EA':
        capital_costs = 0
        O_M_costs = 0
    
    
    else:
        print('technology not modelized')
        capital_costs , O_M_costs = 0 , 0  
        
    return capital_costs , O_M_costs 
       

########################################################################################

def process_efficiency_2(stp_type, tss, cod , bod, nitrate, ammonia, phosphate, ):
    """
    take the WW imput parameters and the operating conditions to return the output pollutant concentration
    """
    if stp_type == 'ASP':
        f_tss, f_cod, f_bod, f_nitrate, f_ammonia, f_phosphate = asp_function(tss, cod, bod, nitrate, ammonia, phosphate)
        
    elif stp_type == 'EA':
        f_tss, f_cod, f_bod, f_nitrate, f_ammonia, f_phosphate = ea_function(tss, cod, bod, nitrate, ammonia, phosphate)
        
    elif stp_type == 'UASB':
        f_tss, f_cod, f_bod, f_nitrate, f_ammonia, f_phosphate = uasb_function(tss, cod, bod, nitrate, ammonia, phosphate)
        
    
    elif stp_type == 'SBR':
        f_tss, f_cod, f_bod, f_nitrate, f_ammonia, f_phosphate = sbr_function(tss, cod, bod, nitrate, ammonia, phosphate)
    
    elif stp_type == 'MBR':
        f_tss, f_cod, f_bod, f_nitrate, f_ammonia, f_phosphate = mbr_function(tss, cod, bod, nitrate, ammonia, phosphate)
    
    elif stp_type == 'MBBR':
        f_tss, f_cod, f_bod, f_nitrate, f_ammonia, f_phosphate  = mbbr_function(tss, cod, bod, nitrate, ammonia, phosphate)
    
    elif stp_type == 'ABR':
        f_tss, f_cod, f_bod, f_nitrate, f_ammonia, f_phosphate  = abr_function(tss, cod, bod, nitrate, ammonia, phosphate)
    
    elif stp_type == 'UASB+EA':
        f_tss, f_cod, f_bod, f_nitrate, f_ammonia, f_phosphate  = uasb_ea_function_2(tss, cod, bod, nitrate, ammonia, phosphate)
    
    else:
        print('technology not modelized')
        f_tss, f_cod, f_bod, f_nitrate, f_ammonia, f_phosphate = tss, cod , bod, nitrate, ammonia, phosphate
        
    
    return f_tss, f_cod, f_bod, f_nitrate, f_ammonia, f_phosphate,


def uasb_ea_function_2(tss, cod, bod, nitrate, ammonia, phosphate):
    f_tss = (1-0.79) * tss
    f_cod = (1-0.89) * cod
    f_bod = (1-0.88) * bod   
    f_nitrate = (1-0.29) * bod  
    f_ammonia = (1-0.72) * ammonia
    f_phosphate = (1-0.133)
    return f_tss,f_cod,f_bod, f_nitrate, f_ammonia, f_phosphate 

def wetland_efficiency_2(tss, cod, bod, nitrate, ammonia, phosphate):
    f_tss = (1-0.67) * tss
    f_cod = (1-0.45) * cod
    f_bod = (1-0.66) * bod
    f_nitrate = (1-0.9) * nitrate
    f_ammonia = (1-0.89) * ammonia
    f_phosphate = (1-0.40) * phosphate
    return f_tss,f_cod,f_bod, f_nitrate, f_ammonia, f_phosphate