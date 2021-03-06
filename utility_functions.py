# -*- coding: utf-8 -*-
"""
Created on Wed Jun  2 18:24:24 2021

@author: mkona
"""

#function which reads the different technology given in the csv file for each stp and return a list

def read_technology_type(stp_type):
    technology_combination = stp_type.split('/')
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
    if stp_type == 'CAS':
        f_tss, f_cod, f_bod, f_nitrate, f_TN, f_ammonia, f_phosphate, f_TP  = cas_function(tss, cod, bod, nitrate, TN, ammonia, phosphate, TP)
        
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
    
    elif stp_type == 'UASB+SBR':
        f_tss, f_cod, f_bod, f_nitrate, f_TN, f_ammonia, f_phosphate, f_TP  = uasb_sbr_function(tss, cod, bod, nitrate, TN, ammonia, phosphate, TP)
    
    elif stp_type == 'UASB+MBBR':
        f_tss, f_cod, f_bod, f_nitrate, f_TN, f_ammonia, f_phosphate, f_TP  = uasb_mbbr_function(tss, cod, bod, nitrate, TN, ammonia, phosphate, TP)
    
    elif stp_type == 'UASB+MBR':
        f_tss, f_cod, f_bod, f_nitrate, f_TN, f_ammonia, f_phosphate, f_TP  = uasb_mbr_function(tss, cod, bod, nitrate, TN, ammonia, phosphate, TP)
 
    elif stp_type == 'SFCW':
        f_tss, f_cod, f_bod, f_nitrate, f_TN, f_ammonia, f_phosphate, f_TP  = wetland_efficiency(tss, cod, bod, nitrate, TN, ammonia, phosphate, TP)
    
    else:
        print('technology not modelized')
        f_tss, f_cod, f_bod, f_nitrate, f_TN, f_ammonia, f_phosphate, f_TP  = tss, cod , bod, nitrate, TN, ammonia, phosphate, TP
        
    
    return f_tss, f_cod, f_bod, f_nitrate, f_TN, f_ammonia, f_phosphate, f_TP


#create processes functions according to litterature




def wetland_efficiency(tss, cod, bod, nitrate, TN, ammonia, phosphate, TP):
    f_tss = (1-0.67) * tss
    f_cod = (1-0.63) * cod
    f_bod = (1-0.60) * bod
    f_nitrate = (1-0.73) * nitrate
    f_TN = (1-0.67) * TN
    f_ammonia = (1-0.63) * ammonia
    f_phosphate = (1-0.50) * phosphate
    f_TP = (1-0.46) * TP
    return f_tss,f_cod,f_bod, f_nitrate, f_TN, f_ammonia, f_phosphate, f_TP

def cas_function(tss, cod, bod, nitrate, TN, ammonia, phosphate, TP):
    f_tss = (1-0.80) * tss
    f_cod = (1-0.83) * cod
    f_bod = (1-0.87) * bod
    f_nitrate = (1+3.63) * nitrate
    f_TN = (1-0.68) * TN
    f_ammonia = (1-0.77) * ammonia
    f_phosphate = phosphate
    f_TP = TP
    return f_tss,f_cod,f_bod, f_nitrate, f_TN, f_ammonia, f_phosphate, f_TP
    
def uasb_function(tss, cod, bod, nitrate, TN, ammonia, phosphate, TP):
    f_tss = (1-0.60) * tss
    f_cod = (1-0.67) * cod
    f_bod = (1-0.64) * bod
    f_nitrate = (1-0.90) * nitrate
    f_TN = (1-0.16) * TN
    f_ammonia = (1-0.04) * ammonia
    f_phosphate = phosphate
    f_TP = TP
    return f_tss,f_cod,f_bod, f_nitrate, f_TN, f_ammonia, f_phosphate, f_TP

def ea_function(tss, cod, bod, nitrate, TN, ammonia, phosphate, TP):
    f_tss = (1-0.69) * tss
    f_cod = (1-0.78) * cod
    f_bod = (1-0.85) * bod
    f_nitrate = (1+7.20) * nitrate
    f_TN = (1-0.7071) * TN
    f_ammonia = (1-0.80) * ammonia
    f_phosphate = phosphate
    f_TP = TP
    return f_tss,f_cod,f_bod, f_nitrate, f_TN, f_ammonia, f_phosphate, f_TP

def sbr_function(tss, cod, bod, nitrate, TN, ammonia, phosphate, TP):
    f_tss = (1-0.80) * tss
    f_cod = (1-0.93) * cod
    f_bod = (1-0.95) * bod  
    f_nitrate = nitrate
    f_TN = (1-0.71) * TN
    f_ammonia = (1-0.98) * ammonia
    f_phosphate = (1-0.85) * phosphate
    f_TP = (1-0.84) * TP
    return f_tss,f_cod,f_bod, f_nitrate, f_TN, f_ammonia, f_phosphate, f_TP

def mbr_function(tss, cod, bod, nitrate, TN, ammonia, phosphate, TP):
    f_tss = (1-0.78) * tss
    f_cod = (1-0.96) * cod
    f_bod = (1-0.99) * bod   
    f_nitrate = nitrate
    f_TN = (1-0.96) * TN
    f_ammonia = (1-0.93) * ammonia
    f_phosphate = phosphate
    f_TP = (1-0.79) * TP
    return f_tss,f_cod,f_bod, f_nitrate, f_TN, f_ammonia, f_phosphate, f_TP

def mbbr_function(tss, cod, bod, nitrate, TN, ammonia, phosphate, TP):
    f_tss = (1-0.85) * tss
    f_cod = (1-0.86) * cod
    f_bod = (1-0.94) * bod
    f_nitrate = nitrate 
    f_TN = (1-0.92) * TN
    f_ammonia = ammonia
    f_phosphate = phosphate
    f_TP = TP
    return f_tss,f_cod,f_bod, f_nitrate, f_TN, f_ammonia, f_phosphate, f_TP

def abr_function(tss, cod, bod, nitrate, TN, ammonia, phosphate, TP):
    f_tss = (1-0.61) * tss
    f_cod = (1-0.60) * cod
    f_bod = (1-0.45) * bod   
    f_nitrate = nitrate
    f_TN = TN
    f_ammonia = (1+0.40) * ammonia
    f_phosphate = phosphate
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
    f_TP = TP
    return f_tss,f_cod,f_bod, f_nitrate, f_TN, f_ammonia, f_phosphate, f_TP   

def uasb_sbr_function(tss, cod, bod, nitrate, TN, ammonia, phosphate, TP):
    f_tss = (1-0.90) * tss
    f_cod = (1-0.90) * cod
    f_bod = (1-0.93) * bod
    f_nitrate = (1 + 4.80) * nitrate
    f_TN = (1-0.66) * TN
    f_ammonia = (1-0.96) * ammonia
    f_phosphate = phosphate
    f_TP = (1-0.61) * TP
    return f_tss,f_cod,f_bod, f_nitrate, f_TN, f_ammonia, f_phosphate, f_TP

def uasb_mbr_function(tss, cod, bod, nitrate, TN, ammonia, phosphate, TP):
    f_tss = (1-0.99) * tss
    f_cod = (1-0.95) * cod
    f_bod = (1-0.91) * bod
    f_nitrate = (1 + 4.80) * nitrate
    f_TN = (1-0.65) * TN
    f_ammonia = (1-0.98) * ammonia
    f_phosphate = phosphate
    f_TP = (1-0.73) * TP  
    return f_tss,f_cod,f_bod, f_nitrate, f_TN, f_ammonia, f_phosphate, f_TP

def uasb_mbbr_function(tss, cod, bod, nitrate, TN, ammonia, phosphate, TP):
    f_tss = (1 - 0.80) * tss
    f_cod = (1 - 0.86) * cod
    f_bod = (1 - 0.64) * bod
    f_nitrate = (1 + 4.80) * nitrate
    f_TN = (1 - 0.60) * TN
    f_ammonia = (1 - 0.34) * ammonia
    f_phosphate = phosphate
    f_TP = TP  
    return f_tss,f_cod,f_bod, f_nitrate, f_TN, f_ammonia, f_phosphate, f_TP

#cost functions 
def total_cost(stp_type,nb_inhabitant):
    technology_combination = read_technology_type(stp_type)
    capital_costs , O_M_costs = 0 , 0  
    for technology in technology_combination:
       capital_costs , O_M_costs = capital_costs + process_cost(technology,nb_inhabitant)[0] , O_M_costs + process_cost(technology,nb_inhabitant)[1]
    return capital_costs, O_M_costs


def process_cost(stp_type,nb_inhabitant):
    """
    take the STP capacity and treated volume to return the capital costs and the O&M costs of each technology
    """
    #capital costs is in US$/m3/d or US$/PE and the stp_capacity/treated_volume are in m3/d
    #PE is the popultaion equivalent calculated from the total BOD load per day and the BOD produced by one inhab per day
   
    # design_PE = design_BOD/0.060
    # treated_PE = treated_BOD/0.060
    
    if stp_type == 'UASB':
        capital_costs = (8 + 13.33)/2 * nb_inhabitant
        O_M_costs = (0.67 + 0.93)/2* nb_inhabitant
        
    
    elif stp_type == 'CAS':
        capital_costs = (26.67 + 42.67)/2 * nb_inhabitant
        O_M_costs = (2.67 + 5.33)/2* nb_inhabitant
        
        
    elif stp_type == 'EA':
       capital_costs = (24 + 32)/2 * nb_inhabitant
       O_M_costs = (2.67 + 5.33)/2* nb_inhabitant
             
        
    elif stp_type == 'MBR':
       capital_costs = (34.67 + 50.67)/2 * nb_inhabitant
       O_M_costs = (4 + 6.67)/2* nb_inhabitant
         
    elif stp_type == 'SBR':
        capital_costs = (24 + 32)/2 * nb_inhabitant
        O_M_costs = (2.67 + 5.33)/2* nb_inhabitant
        
    elif stp_type == 'SFCW':
        capital_costs = (13.33 + 21.32)/2 * nb_inhabitant
        O_M_costs = (0.67 + 1.07)/2* nb_inhabitant
       
    elif stp_type == 'MBBR':
        capital_costs = (18.67 + 32)/2 * nb_inhabitant
        O_M_costs = (2.13 + 4.00)/2* nb_inhabitant
        

    elif stp_type == 'ABR':
       capital_costs = (8 + 13.33)/2 * nb_inhabitant
       O_M_costs = (0.40 + 0.67)/2* nb_inhabitant
       
    elif stp_type == 'UASB+EA':
        capital_costs = (18.67 + 29.33)/2 * nb_inhabitant
        O_M_costs = (1.87 + 3.20)/2* nb_inhabitant
    
    
    elif stp_type == 'UASB+MBR':
        capital_costs = (18.67 + 29.33)/2 * nb_inhabitant
        O_M_costs = (1.87 + 3.20)/2* nb_inhabitant
        
    
    elif stp_type == 'UASB+MBBR':
        capital_costs = (17.33 + 26.67)/2 * nb_inhabitant
        O_M_costs = (1.87 + 3.20)/2* nb_inhabitant
        
        
    elif stp_type == 'UASB+SBR' : 
        capital_costs = (18.67 + 29.33)/2 * nb_inhabitant
        O_M_costs = (1.87 + 3.20)/2* nb_inhabitant
    
    else:
        print('technology not modelized')
        capital_costs , O_M_costs = 0 , 0  
        
    return capital_costs , O_M_costs 
       

########################################################################################
#function for the half-year study period

# def process_efficiency_2(stp_type, tss, cod , bod, nitrate, ammonia, phosphate, ):
#     """
#     take the WW imput parameters and the operating conditions to return the output pollutant concentration
#     """
#     if stp_type == 'CAS':
#         f_tss, f_cod, f_bod, f_nitrate, f_ammonia, f_phosphate = cas_function(tss, cod, bod, nitrate, ammonia, phosphate)
        
#     elif stp_type == 'EA':
#         f_tss, f_cod, f_bod, f_nitrate, f_ammonia, f_phosphate = ea_function(tss, cod, bod, nitrate, ammonia, phosphate)
        
#     elif stp_type == 'UASB':
#         f_tss, f_cod, f_bod, f_nitrate, f_ammonia, f_phosphate = uasb_function(tss, cod, bod, nitrate, ammonia, phosphate)
        
    
#     elif stp_type == 'SBR':
#         f_tss, f_cod, f_bod, f_nitrate, f_ammonia, f_phosphate = sbr_function(tss, cod, bod, nitrate, ammonia, phosphate)
    
#     elif stp_type == 'MBR':
#         f_tss, f_cod, f_bod, f_nitrate, f_ammonia, f_phosphate = mbr_function(tss, cod, bod, nitrate, ammonia, phosphate)
    
#     elif stp_type == 'MBBR':
#         f_tss, f_cod, f_bod, f_nitrate, f_ammonia, f_phosphate  = mbbr_function(tss, cod, bod, nitrate, ammonia, phosphate)
    
#     elif stp_type == 'ABR':
#         f_tss, f_cod, f_bod, f_nitrate, f_ammonia, f_phosphate  = abr_function(tss, cod, bod, nitrate, ammonia, phosphate)
    
#     elif stp_type == 'UASB+EA':
#         f_tss, f_cod, f_bod, f_nitrate, f_ammonia, f_phosphate  = uasb_ea_function_2(tss, cod, bod, nitrate, ammonia, phosphate)
    
#     else:
#         print('technology not modelized')
#         f_tss, f_cod, f_bod, f_nitrate, f_ammonia, f_phosphate = tss, cod , bod, nitrate, ammonia, phosphate
        
    
#     return f_tss, f_cod, f_bod, f_nitrate, f_ammonia, f_phosphate,


# def uasb_ea_function_2(tss, cod, bod, nitrate, ammonia, phosphate):
#     f_tss = (1-0.79) * tss
#     f_cod = (1-0.89) * cod
#     f_bod = (1-0.88) * bod   
#     f_nitrate = (1-0.29) * nitrate  
#     f_ammonia = (1-0.72) * ammonia
#     f_phosphate = (1-0.133)
#     return f_tss,f_cod,f_bod, f_nitrate, f_ammonia, f_phosphate 

# def wetland_efficiency_2(tss, cod, bod, nitrate, ammonia, phosphate):
#     f_tss = (1-0.67) * tss
#     f_cod = (1-0.45) * cod
#     f_bod = (1-0.66) * bod
#     f_nitrate = (1-0.9) * nitrate
#     f_ammonia = (1-0.89) * ammonia
#     f_phosphate = (1-0.40) * phosphate
#     return f_tss,f_cod,f_bod, f_nitrate, f_ammonia, f_phosphate