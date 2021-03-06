# -*- coding: utf-8 -*-
"""
Created on Wed Jun  2 17:35:00 2021

@author: mkona
"""

#import relevant system/os commands
from os import chdir, listdir, getcwd

'''set the working directory (change this path to the location where all model 
input files are)'''

workdir = 'C:/Users/mkona/OneDrive/Bureau/Imperial_Msc EEBM_2021/Summer Project/project/WWT_module_repo/'
chdir(workdir)

#import relevant modules
import os #operating system
import csv #read csv files
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display


#ignore all warnings
import warnings
warnings.filterwarnings('ignore')

#import functions
from utility_functions import *

#constants
NB_LAKES = 37
NB_DAYS = 365
NB_STP = 1

#set WWT module input & output path directories 
input_dir = os.path.join(workdir, "inputs_WW")
output = os.path.join(workdir, "outputs_WW")

# load STP csv file into Pandas dataframe
stp_path = os.path.join(input_dir, "STP_data.csv")

stp_data = pd.read_csv(stp_path,
                       dtype={'STP_ID':'int64', 'name':'str', 'lake':'str','lake_ID':'int64', 
                       'capacity_volume':'float64', 'percentage_utilisation':'float64',
                       'technologies_type':'str'})


#load tanks/lakes csv file into Pandas dataframe
#raw data on lakes and their catchment
tank_path = os.path.join(input_dir, "tank_master.csv")

tank_data = pd.read_csv(tank_path, sep=";",
                        dtype={'ID':'int64', 'name':'str', 'area_max':'float32', 
                       'vol_max':'float64', 'vol_open':'float64', 
                       'vol_close':'float64', 'catch_size':'float64', 
                       'catch_pop':'int64', 'paved':'float64', 'DS_tank':'int64',
                       'divert':'str', 'treated':'float64', 'dchanw':'float64', 'dchanh':'float64','wetland':'str','wetland_surface':'float64'})

#calculated data on the catchment and the lakes dynamics
#not to be loaded when module is inserted in the whole cascade model
#all values are in mg/L

tank_data_2 = []

for i in range(NB_LAKES):
    tank_path_2 = os.path.join(input_dir, "tank_{}.csv".format(i))
    
    tank_data_2.append(pd.read_csv(tank_path_2,
                              dtype={'ID':'int64', 'name':'str',	'tank_wsarea':'float64',
                                     'tank_sewvol':'float64',	'tank_vopen':'float64',	'tank_evvol':'float64', 
                                     'tank_revol':'float64',	'spill':'float64',	'tank_uspill':'float64', 
                                     'tank_crunvol':'float64',	'tank_rajkalve':'float64',	
                                     'tank_inflow':'float64',	'tank_usdivert':'float64',	
                                     'tank_vclose':'float64', 'tank_stp':'float64',	'DS_tank':'int64',
                                     'divert':'str','treated':'float64'}))
    



#load all water sources quality csv file into Pandas dataframe
#here we only have data for jakkur lake
#data on wastewater quality generated from Jakkur catchment 
wastewater_quality_path = os.path.join(input_dir, "raw_sewage.csv")

jakkur_wastewater_quality_data = pd.read_csv(wastewater_quality_path, sep=";",
                        dtype={'Date':'str','TSS':'float64','BOD':'float64','COD':'float64',
                       'NO3-N':'float64','Nitrates':'float64', 'NH4-N':'float64', 
                       'TN':'float64','PO4-P':'float64','TP':'float64'})



#data on stormwater quality, calculated from litterature and Event Mean Concentration (EMC)
stormwater_quality_path = os.path.join(input_dir, "stormwater_quality.csv")

stormwater_quality_data = pd.read_csv(stormwater_quality_path, sep=";",
                        dtype={'BOD':'float64', 
                       'COD':'float64', 'TSS':'float64','TKN':'float64', 
                       'nitrate':'float64', 'TP':'float64','PO4-P':'float64',
                       'NH3-N':'float64'})


#data on lake water quality (only available for Jakkur lake so these data are 
#taken as a reference for a lake)
lake_quality_path = os.path.join(input_dir, "jakkur_lake_quality.csv")

jakkur_lake_quality_data = pd.read_csv(lake_quality_path, sep=";",
                        dtype={'Date':'str', 'TSS':'float64', 'BOD':'float64','COD':'float64','NO3-N':'float64',
                       'Nitrates':'float64', 'NH4-N':'float64', 
                       'TN':'float64','PO4-P':'float64','TP':'float64'})


#data of experimental concentrations in STP effluent 

stp_effluent_path = os.path.join(input_dir, "STP_effluent_experimental.csv")

stp_effluent_exp_data = pd.read_csv(stp_effluent_path, sep=";",
                        dtype={'Date':'str', 'TSS':'float64', 'BOD':'float64','COD':'float64','NO3-N':'float64',
                       'Nitrates':'float64', 'NH4-N':'float64', 
                       'TN':'float64','PO4-P':'float64','TP':'float64'})



#data of experimental concentrations in wetland effleunt

wetland_effluent_path = os.path.join(input_dir, "wetland_effluent_experimental.csv")

wetland_effluent_exp_data = pd.read_csv(wetland_effluent_path, sep=";",
                        dtype={'Date':'str', 'TSS':'float64', 'BOD':'float64','COD':'float64','NO3-N':'float64',
                       'Nitrates':'float64', 'NH4-N':'float64', 
                       'TN':'float64','PO4-P':'float64','TP':'float64'})

###################################################################

# Volumes of wastewater generated/Total untreated volume

volume_ww = np.zeros((NB_LAKES , NB_DAYS)) # volume of daily wastewater generated for each catchment
untreated_volume_ww = np.zeros((NB_LAKES , NB_DAYS)) # untreated volume of wastewater when the STP/STPs(when there are several ones discharging in the same lake) capacity are not sufficient
treated_volume_ww = np.zeros((NB_LAKES , NB_DAYS)) # treated volume of wastewater
tank_crunvol = np.zeros((NB_LAKES , NB_DAYS)) #SCS runoff volume
tank_uspill = np.zeros((NB_LAKES , NB_DAYS)) #upstream spill volume

#supply per capita assumed at 0.120 m3
slpcd = 120
#80% supply assumed to be sewage fraction
wwfracl = 0.8*slpcd

for day in range(NB_DAYS):
    for idx_lake in range(NB_LAKES):
        #calculation of wastewater volume generated
        if idx_lake == 17 :
            volume_ww[idx_lake, day] = tank_data['catch_pop'][idx_lake]*wwfracl + tank_data['catch_pop'][idx_lake-1]*wwfracl #Jakkur Lake STP receives sewage water from upstream catchment (Yelahanka)
        else :
            volume_ww[idx_lake, day] = tank_data['catch_pop'][idx_lake]*wwfracl
        
        #calculation of treated and untreated volumes
        stp_data_lake = stp_data.loc[stp_data['lake_ID'] == idx_lake + 1] #table of STPs discharging in the same lake
        total_stp_lake_capacity = (stp_data_lake['capacity_volume']*stp_data_lake['percentage_utilisation']).sum() #total volume that could be treated by the STPs discharging in a same lake
        sewerage_network_coverage = tank_data['treated'][idx_lake]
        untreated_volume_ww[idx_lake, day] = (1-sewerage_network_coverage) * volume_ww[idx_lake, day]
        if (total_stp_lake_capacity >  sewerage_network_coverage * volume_ww[idx_lake, day]):
            treated_volume_ww[idx_lake, day] =  sewerage_network_coverage * volume_ww[idx_lake, day]
        else:
            treated_volume_ww[idx_lake, day] = sewerage_network_coverage * total_stp_lake_capacity
            untreated_volume_ww[idx_lake, day] += volume_ww[idx_lake, day] - treated_volume_ww[idx_lake, day]
        
        #SCS runoff volume
        tank_crunvol[idx_lake, day] = tank_data_2[idx_lake]['tank_crunvol'][day]*10**3 #in liters
        
        #upstream spill volume 
        tank_uspill[idx_lake, day] = tank_data_2[idx_lake]['tank_uspill'][day]*10**3   #in liters
    



######################################################################

#Concentrations in the untreated water entering the Rajakaluve

''' Concentrations in the upstream spills are very complicated to estimate if we want to take into account
the specific concentration of each lake spilling into the lake under consideration. The easiest way to do this 
would be to have the concentrations of the water in the rajakaluve. I would try to have an estimation of this, 
if it is not possible, then I would consider the concentrations in the main lake discharging'''

# Declare blank arrays required for first set of calculations
untreated_water_tss = np.zeros((NB_LAKES , NB_DAYS,))
untreated_water_cod = np.zeros((NB_LAKES , NB_DAYS,))
untreated_water_bod = np.zeros((NB_LAKES , NB_DAYS,))
untreated_water_nitrate = np.zeros((NB_LAKES , NB_DAYS,))
untreated_water_TN = np.zeros((NB_LAKES , NB_DAYS,))
untreated_water_ammonia = np.zeros((NB_LAKES , NB_DAYS,))
untreated_water_phosphate = np.zeros((NB_LAKES , NB_DAYS,))
untreated_water_TP = np.zeros((NB_LAKES , NB_DAYS,))

untreated_water_volume = np.zeros((NB_LAKES , NB_DAYS,))

#calculation of pollutant concentrations of the water entering the Rajakaluve
for idx_lake in range(0, NB_LAKES):
    for day in range(0, NB_DAYS):
        untreated_water_volume[idx_lake,day] = tank_crunvol[idx_lake, day] + tank_uspill[idx_lake, day] + untreated_volume_ww[idx_lake, day]
        if (tank_crunvol[idx_lake, day] + tank_uspill[idx_lake, day] + untreated_volume_ww[idx_lake, day]) == 0:
         untreated_water_tss[idx_lake,day] = 0 
         untreated_water_cod[idx_lake,day] = 0
         untreated_water_nitrate[idx_lake,day] = 0
         untreated_water_TN[idx_lake,day] = 0 
         untreated_water_ammonia[idx_lake,day] = 0
         untreated_water_phosphate[idx_lake,day] = 0
         untreated_water_TP[idx_lake,day] = 0
            
            
        else:
         untreated_water_tss[idx_lake,day] = (tank_crunvol[idx_lake, day] * stormwater_quality_data['TSS'][0] + tank_uspill[idx_lake, day] * jakkur_lake_quality_data['TSS'][day]  + untreated_volume_ww[idx_lake, day] * jakkur_wastewater_quality_data['TSS'][day])/(untreated_water_volume[idx_lake,day]) 
        
         untreated_water_cod[idx_lake,day] = (tank_crunvol[idx_lake, day] * stormwater_quality_data['COD'][0] 
                                              + tank_uspill[idx_lake, day] * jakkur_lake_quality_data['COD'][day] 
                                              + untreated_volume_ww[idx_lake, day] * jakkur_wastewater_quality_data['COD'][day])/(untreated_water_volume[idx_lake,day])

        
         untreated_water_bod[idx_lake,day] = (tank_crunvol[idx_lake, day] * stormwater_quality_data['BOD'][0] + tank_uspill[idx_lake, day] * jakkur_lake_quality_data['BOD'][day] + untreated_volume_ww[idx_lake, day] * jakkur_wastewater_quality_data['BOD'][day])/(untreated_water_volume[idx_lake,day])
          
         untreated_water_nitrate[idx_lake,day] = (tank_crunvol[idx_lake, day] * stormwater_quality_data['Nitrate'][0] 
                                                + tank_uspill[idx_lake, day] * jakkur_lake_quality_data['Nitrate'][day] 
                                                + untreated_volume_ww[idx_lake, day] * jakkur_wastewater_quality_data['Nitrate'][day])/(untreated_water_volume[idx_lake,day])

         untreated_water_TN[idx_lake,day] = (tank_crunvol[idx_lake, day] * stormwater_quality_data['TN'][0] 
                                               + tank_uspill[idx_lake, day] * jakkur_lake_quality_data['TN'][day] 
                                               + untreated_volume_ww[idx_lake, day] * jakkur_wastewater_quality_data['TN'][day])/(untreated_water_volume[idx_lake,day])

         untreated_water_ammonia[idx_lake,day] = (tank_crunvol[idx_lake, day] * stormwater_quality_data['NH3-N'][0] 
                                                  + tank_uspill[idx_lake, day] * jakkur_lake_quality_data['NH4-N'][day] 
                                                  + untreated_volume_ww[idx_lake, day] * jakkur_wastewater_quality_data['NH4-N'][day])/(untreated_water_volume[idx_lake,day])

         untreated_water_phosphate[idx_lake,day] = (tank_crunvol[idx_lake, day] * stormwater_quality_data['PO4-P'][0] 
                                                     + tank_uspill[idx_lake, day] * jakkur_lake_quality_data['PO4-P'][day] 
                                                     + untreated_volume_ww[idx_lake, day] * jakkur_wastewater_quality_data['PO4-P'][day])/(untreated_water_volume[idx_lake,day])

         untreated_water_TP[idx_lake,day] = (tank_crunvol[idx_lake, day] * stormwater_quality_data['TP'][0] 
                                               + tank_uspill[idx_lake, day] * jakkur_lake_quality_data['TP'][day] 
                                               + untreated_volume_ww[idx_lake, day] * jakkur_wastewater_quality_data['TP'][day])/(untreated_water_volume[idx_lake,day])



#####################################################################

#Concentrations in the effluent of all the STP discharging in each lake & all the total combined effluent when there is several STPs

# Declare blank arrays required for first set of calculations
total_effluent_tss = np.zeros((NB_LAKES , NB_DAYS)) #tss concentration in the global effluent of all the STP discharging in each lake
total_effluent_cod = np.zeros((NB_LAKES , NB_DAYS)) #cod concentration in the global effluent of all the STP discharging in each lake
total_effluent_bod = np.zeros((NB_LAKES , NB_DAYS)) #bod concentration in the global effluent of all the STP discharging in each lake
total_effluent_nitrate = np.zeros((NB_LAKES , NB_DAYS)) 
total_effluent_TN = np.zeros((NB_LAKES , NB_DAYS)) 
total_effluent_ammonia = np.zeros((NB_LAKES , NB_DAYS)) 
total_effluent_phosphate = np.zeros((NB_LAKES , NB_DAYS)) 
total_effluent_TP = np.zeros((NB_LAKES , NB_DAYS)) 
        

#calculate pollutant concentrations of the effluent of each STP for each day of the year for each lake

for idx_lake in range(0, NB_LAKES):
    nstps = np.shape(stp_data.loc[stp_data['lake_ID'] == idx_lake + 1])[0]
    stp_capacity_table = (stp_data.loc[stp_data['lake_ID'] == idx_lake + 1])['capacity_volume'] #matrix of capacity for lake underconsideration
    stp_utilisation_table = (stp_data.loc[stp_data['lake_ID'] == idx_lake + 1])['percentage_utilisation']
    total_stp_capacity = (stp_capacity_table * stp_utilisation_table).sum()
    volume_treated_stp = np.zeros((1,nstps))
    effluent_tss = np.zeros((1,nstps)) #tss concentration in the  effluent of each STP discharging in one lake
    effluent_cod = np.zeros((1,nstps)) #cod concentration in the  effluent of each STP discharging in one lake
    effluent_bod = np.zeros((1,nstps)) #bod concentration in the  effluent of each STP discharging in one lake
    effluent_nitrate = np.zeros((1,nstps))
    effluent_TN = np.zeros((1,nstps))
    effluent_ammonia = np.zeros((1,nstps))
    effluent_phosphate = np.zeros((1,nstps))
    effluent_TP = np.zeros((1,nstps))
    
    for day in range(0, NB_DAYS): 
        # for each day of the simulation period, the diffrerent effluent concentrations, for each stp discharging in idx_lake, are estimated 
        for istp in range(0, nstps): 
            istp_capacity = stp_capacity_table[istp]
            istp_utilisation = stp_utilisation_table[istp]
            volume_treated_stp[istp] = treated_volume_ww[idx_lake, day] * istp_capacity * istp_utilisation / total_stp_capacity
            stp_type = str(stp_data['technologies_type'][istp])
            i_tss = jakkur_wastewater_quality_data['TSS'][day]
            i_cod = jakkur_wastewater_quality_data['COD'][day]
            i_bod = jakkur_wastewater_quality_data['BOD'][day]
            i_nitrate = jakkur_wastewater_quality_data['NO3-N'][day]
            i_TN = jakkur_wastewater_quality_data['NH4-N'][day]
            i_ammonia = jakkur_wastewater_quality_data['TN'][day]
            i_phosphate = jakkur_wastewater_quality_data['PO4-P'][day]
            i_TP = jakkur_wastewater_quality_data['TP'][day]
            f_tss, f_cod, f_bod, f_nitrate, f_TN, f_ammonia, f_phosphate, f_TP = process_efficiency(stp_type, i_tss, i_cod, i_bod, i_nitrate, i_TN, i_ammonia, i_phosphate, i_TP)
            effluent_tss[istp] = f_tss
            effluent_cod[istp] = f_cod
            effluent_bod[istp] = f_bod
            effluent_nitrate[istp] = f_nitrate
            effluent_TN[istp] = f_TN
            effluent_ammonia[istp] = f_ammonia
            effluent_phosphate[istp] = f_phosphate
            effluent_TP[istp] = f_TP
            
        total_effluent_tss[idx_lake,day] = ((effluent_tss * volume_treated_stp).sum())/treated_volume_ww[idx_lake, day]
        total_effluent_cod[idx_lake,day] = ((effluent_cod * volume_treated_stp).sum())/treated_volume_ww[idx_lake, day]
        total_effluent_bod[idx_lake,day] = ((effluent_bod * volume_treated_stp).sum())/treated_volume_ww[idx_lake, day]
        total_effluent_nitrate[idx_lake,day] = ((effluent_nitrate * volume_treated_stp).sum())/treated_volume_ww[idx_lake, day]
        total_effluent_TN[idx_lake,day] = ((effluent_TN * volume_treated_stp).sum())/treated_volume_ww[idx_lake, day]
        total_effluent_ammonia[idx_lake,day] = ((effluent_ammonia * volume_treated_stp).sum())/treated_volume_ww[idx_lake, day]
        total_effluent_phosphate[idx_lake,day] = ((effluent_phosphate * volume_treated_stp).sum())/treated_volume_ww[idx_lake, day]
        total_effluent_TP[idx_lake,day] = ((effluent_TP * volume_treated_stp).sum())/treated_volume_ww[idx_lake, day]
        
        
#When a result concentration is equal to 0, it means either that the initial concentration was not available or that the removal efficiency was unknown

############################################################################################################
# If the lake itself has a wetland which is integrated in the treatment process, the global STPS effluent passes through the wetland and the user has the flexibility to give a proportion
#of raw wastewater (indistinguishly untreated wastewater + runoff volume + upstream spill) passing through the wetland --> This configuration is very specific to Jakkur Lake but could be used as a model

volume_rw_wetland = np.zeros((NB_LAKES , NB_DAYS,)) #volume of raw wastewater passing through the wetland
total_volume_wetland = np.zeros((NB_LAKES , NB_DAYS,)) #total volume of water passing through the wetland (treated effluent of the STP and proportion of wastewater)

wetland_inlet_tss = np.zeros((NB_LAKES , NB_DAYS,)) #tss concentration at the inlet of the wetland
wetland_inlet_cod = np.zeros((NB_LAKES , NB_DAYS,)) #cod concentration at the inlet of the wetland
wetland_inlet_bod = np.zeros((NB_LAKES , NB_DAYS,)) #bod concentration at the inlet of the wetland
wetland_inlet_nitrate = np.zeros((NB_LAKES , NB_DAYS,)) 
wetland_inlet_TN = np.zeros((NB_LAKES , NB_DAYS,)) 
wetland_inlet_ammonia = np.zeros((NB_LAKES , NB_DAYS,)) 
wetland_inlet_phosphate = np.zeros((NB_LAKES , NB_DAYS,)) 
wetland_inlet_TP = np.zeros((NB_LAKES , NB_DAYS,)) 

 
wetland_outlet_tss = np.zeros((NB_LAKES , NB_DAYS,)) #tss concentration at the outlet of the wetland
wetland_outlet_cod = np.zeros((NB_LAKES , NB_DAYS,)) #cod concentration at the outlet of the wetland
wetland_outlet_bod = np.zeros((NB_LAKES , NB_DAYS,)) #bod concentration at the outlet of the wetland
wetland_outlet_nitrate = np.zeros((NB_LAKES , NB_DAYS,)) 
wetland_outlet_TN = np.zeros((NB_LAKES , NB_DAYS,)) 
wetland_outlet_ammonia = np.zeros((NB_LAKES , NB_DAYS,)) 
wetland_outlet_phosphate = np.zeros((NB_LAKES , NB_DAYS,)) 
wetland_outlet_TP = np.zeros((NB_LAKES , NB_DAYS,)) 

p = np.zeros(NB_LAKES) 


for idx_lake in range(0, NB_LAKES):
    #if the lake has a wetland 
   if tank_data['wetland'][idx_lake]== 'y':
       print("which average percentage of raw wastewater is passing through the wetland of tank " + str(idx_lake+1) + " ?")
       percentage = int(input('The percentage : '))
       p[idx_lake] = percentage
       
       
       for day in range(0, NB_DAYS):
           volume_rw_wetland[idx_lake,day] = p[idx_lake]/100 * untreated_water_volume[idx_lake,day] #volume of untreated water/raw water (spill,runoff, untreated wastewater) entering the wetland
           total_volume_wetland[idx_lake,day] = volume_rw_wetland[idx_lake,day] + treated_volume_ww[idx_lake, day]
           
           wetland_inlet_tss[idx_lake,day] = (total_effluent_tss[idx_lake,day] * treated_volume_ww[idx_lake, day] + untreated_water_tss[idx_lake,day]* volume_rw_wetland[idx_lake,day])/ total_volume_wetland[idx_lake,day]
           wetland_inlet_cod[idx_lake,day] = (total_effluent_cod[idx_lake,day] * treated_volume_ww[idx_lake, day] + untreated_water_cod[idx_lake,day]* volume_rw_wetland[idx_lake,day])/ total_volume_wetland[idx_lake,day]
           wetland_inlet_bod[idx_lake,day] = (total_effluent_bod[idx_lake,day] * treated_volume_ww[idx_lake, day] + untreated_water_bod[idx_lake,day]* volume_rw_wetland[idx_lake,day])/ total_volume_wetland[idx_lake,day]
           wetland_inlet_nitrate[idx_lake,day] = (total_effluent_nitrate[idx_lake,day] * treated_volume_ww[idx_lake, day] + untreated_water_nitrate[idx_lake,day]* volume_rw_wetland[idx_lake,day])/ total_volume_wetland[idx_lake,day]
           wetland_inlet_TN[idx_lake,day] = (total_effluent_TN[idx_lake,day] * treated_volume_ww[idx_lake, day] + untreated_water_TN[idx_lake,day]* volume_rw_wetland[idx_lake,day])/ total_volume_wetland[idx_lake,day]
           wetland_inlet_ammonia[idx_lake,day] = (total_effluent_ammonia[idx_lake,day] * treated_volume_ww[idx_lake, day] + untreated_water_ammonia[idx_lake,day]* volume_rw_wetland[idx_lake,day])/ total_volume_wetland[idx_lake,day]
           wetland_inlet_phosphate[idx_lake,day] = (total_effluent_phosphate[idx_lake,day] * treated_volume_ww[idx_lake, day] + untreated_water_phosphate[idx_lake,day]* volume_rw_wetland[idx_lake,day])/ total_volume_wetland[idx_lake,day] 
           wetland_inlet_TP[idx_lake,day] = (total_effluent_TP[idx_lake,day] * treated_volume_ww[idx_lake, day] + untreated_water_TP[idx_lake,day]* volume_rw_wetland[idx_lake,day])/ total_volume_wetland[idx_lake,day]
           
           tss = wetland_inlet_tss[idx_lake,day] 
           cod = wetland_inlet_cod[idx_lake,day] 
           bod = wetland_inlet_bod[idx_lake,day]
           nitrate = wetland_inlet_nitrate[idx_lake,day] 
           TN = wetland_inlet_TN[idx_lake,day]
           ammonia = wetland_inlet_ammonia[idx_lake,day] 
           phosphate = wetland_inlet_phosphate[idx_lake,day]
           TP = wetland_inlet_TP[idx_lake,day]
           
           wetland_outlet_tss[idx_lake,day], wetland_outlet_cod[idx_lake,day], wetland_outlet_bod[idx_lake,day], wetland_outlet_nitrate[idx_lake,day],wetland_outlet_TN[idx_lake,day], wetland_outlet_ammonia[idx_lake,day], wetland_outlet_phosphate[idx_lake,day], wetland_outlet_TP[idx_lake,day] = wetland_efficiency(tss, cod, bod, nitrate, TN, ammonia, phosphate, TP)
           
   else :
       percentage = 0
       p[idx_lake] = percentage
       
       for day in range(0, NB_DAYS):
           wetland_outlet_tss[idx_lake,day], wetland_outlet_cod[idx_lake,day], wetland_outlet_bod[idx_lake,day], wetland_outlet_nitrate[idx_lake,day],wetland_outlet_TN[idx_lake,day], wetland_outlet_ammonia[idx_lake,day], wetland_outlet_phosphate[idx_lake,day], wetland_outlet_TP[idx_lake,day] =  wetland_inlet_tss[idx_lake,day], wetland_inlet_cod[idx_lake,day], wetland_inlet_bod[idx_lake,day],wetland_inlet_nitrate[idx_lake,day], wetland_inlet_TN[idx_lake,day],wetland_inlet_ammonia[idx_lake,day], wetland_inlet_phosphate[idx_lake,day], wetland_inlet_TP[idx_lake,day] 
        
   
       
      

#TO DO : ajouter une question sur le wetland et mettre un warning si la capacit?? d??passe 


############################################################################################################

#Volume & Concentrations in the inflow of the lake

#Declare blank arrays required for calculations of volume inflow
diverted_volume = np.zeros((NB_LAKES , NB_DAYS)) #for lakes having diversion channels, volume of water in rajakalve is preferably diverted
tank_inflow =  np.zeros((NB_LAKES , NB_DAYS)) #volume of water from the rajakalve entering the lake
total_tank_inflow = np.zeros((NB_LAKES , NB_DAYS)) #volume of water from the rajakalve and the STP entering the lake 
volume_rajakaluve = np.zeros((NB_LAKES , NB_DAYS)) #volume of untreated water in the Rajakaluve
tank_divthresh =np.zeros((NB_LAKES,1)) #volume that can be diverted

for idx_lake in range(0, NB_LAKES):
    tank_divthresh[idx_lake] = tank_data['dchanw'][idx_lake]*tank_data['dchanh'][idx_lake]*0.04*3600*24 #taken from ATREE's Cascade model
    for day in range(0, NB_DAYS):
        volume_rajakaluve[idx_lake, day] = tank_crunvol[idx_lake, day] + tank_uspill[idx_lake, day] + (1-p[idx_lake])/100 * untreated_volume_ww[idx_lake, day]
        if tank_data['divert'][idx_lake] == "y": 
            if volume_rajakaluve[idx_lake, day] > tank_divthresh[idx_lake]:
               tank_inflow[idx_lake, day] = volume_rajakaluve[idx_lake, day] - tank_divthresh[idx_lake]  
            else:
               tank_inflow[idx_lake, day] = 0
        else:            
            tank_inflow[idx_lake, day] = volume_rajakaluve[idx_lake, day]
            
        total_tank_inflow[idx_lake, day] = tank_inflow[idx_lake, day] + treated_volume_ww[idx_lake, day] + p[idx_lake]/100 * untreated_volume_ww[idx_lake, day]

#Declare blank arrays required for calculations of inflow concentrations

total_inflow_tss = np.zeros((NB_LAKES , NB_DAYS,)) #tss concentration in the inflow of each lake
total_inflow_cod = np.zeros((NB_LAKES , NB_DAYS,)) #cod concentration in the inflow of each lake
total_inflow_bod = np.zeros((NB_LAKES , NB_DAYS,)) #bod concentration in the inflow of each lake
total_inflow_nitrate = np.zeros((NB_LAKES , NB_DAYS,))
total_inflow_TN = np.zeros((NB_LAKES , NB_DAYS,))
total_inflow_ammonia = np.zeros((NB_LAKES , NB_DAYS,))
total_inflow_phosphate = np.zeros((NB_LAKES , NB_DAYS,))
total_inflow_TP = np.zeros((NB_LAKES , NB_DAYS,))


for idx_lake in range(0, NB_LAKES):
    for day in range(0, NB_DAYS): 
        total_inflow_tss[idx_lake, day] = (wetland_outlet_tss[idx_lake,day] * total_volume_wetland[idx_lake, day] 
                                          + untreated_water_tss[idx_lake,day] * tank_inflow[idx_lake, day])/ total_tank_inflow[idx_lake, day]
        
        total_inflow_cod[idx_lake, day] = (wetland_outlet_cod[idx_lake,day]  *total_volume_wetland[idx_lake, day] 
                                          + untreated_water_cod[idx_lake,day] * tank_inflow[idx_lake, day])/ total_tank_inflow[idx_lake, day]
        
        total_inflow_bod[idx_lake, day] = (wetland_outlet_bod[idx_lake,day] * total_volume_wetland[idx_lake, day]
                                          + untreated_water_bod[idx_lake,day] * tank_inflow[idx_lake, day])/ total_tank_inflow[idx_lake, day]
        
        total_inflow_nitrate[idx_lake, day] = (wetland_outlet_nitrate[idx_lake,day] * total_volume_wetland[idx_lake, day]
                                               + untreated_water_nitrate[idx_lake,day] * tank_inflow[idx_lake, day])/ total_tank_inflow[idx_lake, day]
 
        total_inflow_TN[idx_lake, day] = (wetland_outlet_TN[idx_lake,day] * total_volume_wetland[idx_lake, day]
                                          + untreated_water_TN[idx_lake,day] * tank_inflow[idx_lake, day])/ total_tank_inflow[idx_lake, day]
    
        total_inflow_ammonia[idx_lake, day] = (wetland_outlet_ammonia[idx_lake,day] * total_volume_wetland[idx_lake, day]
                                              + untreated_water_ammonia[idx_lake,day] * tank_inflow[idx_lake, day])/ total_tank_inflow[idx_lake, day]
    
    
        total_inflow_phosphate[idx_lake, day] = (wetland_outlet_phosphate[idx_lake,day] * total_volume_wetland[idx_lake, day]
                                                + untreated_water_phosphate[idx_lake,day] * tank_inflow[idx_lake, day])/ total_tank_inflow[idx_lake, day]
    
    
        total_inflow_TP[idx_lake, day] = (wetland_outlet_TP[idx_lake,day] * total_volume_wetland[idx_lake, day]
                                          + untreated_water_TP[idx_lake,day] * tank_inflow[idx_lake, day])/ total_tank_inflow[idx_lake, day]
    
    
    
# fig = plt.figure()
# ax1 = fig.add_subplot(111)
# days = np.arange(365)
# ax1.scatter(days, total_inflow_tss[17], c='r', s=2, label ='inflow tss' )
# ax1.scatter(days, total_effluent_tss[17], c='g', s=2, label ='stp effluent tss')
# ax1.scatter(days, untreated_water_tss[17], c='b', s=2, label = 'rajakaluve tss')
# plt.xlabel('days')
# plt.ylabel('tss concentrations')
# plt.legend()
# plt.show()

########################################################################################################################

#Cost module

average_influent_BOD = (jakkur_wastewater_quality_data['BOD'].mean())/1000 #average influent BOD in kg/m3
capital_costs = np.zeros((NB_STP ,1 ))
O_M_costs = np.zeros((NB_STP ,1 ))


for istp in range (0,NB_STP):
    # design_BOD = stp_data['capacity_volume'][istp] * average_BOD
    # treated_BOD = stp_data['capacity_volume'][istp] * stp_data['percentage_utilisation'][istp] * average_BOD
    stp_type = str(stp_data['technologies_type'][istp])
    idx_lake = stp_data['lake_ID'][istp]
    nb_inhabitant = tank_data['catch_pop'][idx_lake - 1]
    # stp_capacity = stp_data['capacity_volume'][istp]
    # treated_volume = stp_data['capacity_volume'][istp] * stp_data['percentage_utilisation'][istp]
    capital_costs[istp],O_M_costs[istp] = total_cost(stp_type,nb_inhabitant)
    
    print(capital_costs, O_M_costs)

#%%    
#########################################################################################################################
#results MSc Thesis
# technologie_table = pd.DataFrame([total_effluent_tss[17,:],total_effluent_cod[17,:],total_effluent_bod[17,:], total_effluent_nitrate[17,:], total_effluent_TN[17,:], total_effluent_ammonia[17,:], total_effluent_phosphate[17,:]])
# print(technologie_table)
#create output as csv files
import itertools


outcalc = [total_effluent_tss[17,:],total_effluent_cod[17,:],total_effluent_bod[17,:],total_effluent_nitrate[17,:], total_effluent_TN[17,:], total_effluent_ammonia[17,:], total_effluent_phosphate[17,:],total_effluent_TP[17,:]]  

    
flat = np.array(outcalc)
transp = flat.T
outtech = "UASB+EA.csv"
outfile = os.path.join(output, outtech)
    
with open(outfile, 'w') as f:
        writerh = csv.DictWriter(f, fieldnames = ["TSS", "COD", "BOD", "nitrate", "TN", 
                                                  "ammonia", "phosphate","TP"], delimiter = ',')
        writerh.writeheader()
        writer = csv.writer(f)
        writer.writerows(transp)
        
#%%
########################################################################################################################
#create output as csv files
import itertools

for idx_lake in range (NB_LAKES):
    outcalc = [[untreated_volume_ww[idx_lake,:],untreated_water_tss[idx_lake,:],untreated_water_cod[idx_lake,:],untreated_water_bod[idx_lake,:],
            total_effluent_tss[idx_lake,:],total_effluent_cod[idx_lake,:],total_effluent_bod[idx_lake,:], wetland_outlet_tss[idx_lake,:], wetland_outlet_cod[idx_lake,:],wetland_outlet_bod[idx_lake,:],
            total_inflow_tss[idx_lake,:],total_inflow_cod[idx_lake,:],total_inflow_bod[idx_lake,:]]]  

    
    flat = list(itertools.chain(*outcalc))
    transp = list(zip(*flat))
    outlake = "tank" + str(idx_lake) + ".csv"
    outfile = os.path.join(output, outlake)
    
    with open(outfile, 'w') as f:
        writerh = csv.DictWriter(f, fieldnames = ["untreated volume", "TSS in rajakaluve", "COD in rajakaluve", "BOD in rajakaluve", "TSS in STPs effluent", 
                                                  "COD in STPs effluent", "BOD in STPs effluent","TSS in wetland outlet","COD in wetland outlet", "BOD in wetland outlet",
                                                  "TSS in lake inflow", "COD in lake inflow", "BOD in lake inflow"], delimiter = ',')
        writerh.writeheader()
        writer = csv.writer(f)
        writer.writerows(transp)
        


#%%
################################################################################################################################
#Table Visualization of results for Jakkur lake & Jakkur STP
times = pd.Series(pd.date_range('2021', periods=365, freq='D'))
np.array(times)
                  

year_table_BOD = pd.DataFrame([jakkur_wastewater_quality_data['BOD'],total_effluent_bod[17,:], stp_effluent_exp_data['BOD'], wetland_outlet_bod[17,:],wetland_effluent_exp_data['BOD']]).T
year_table_BOD.columns = ['BOD in wastewater (mg/L)','Modelled BOD in STP effluent (mg/L)','Measured BOD in STP effluent (mg/L)', 'Modelled BOD in wetland effluent (mg/L)', 'Measured BOD in wetland effluent (mg/L)']
year_table_BOD.index = pd.Index(times,name = 'Date')

year_table_BOD.style.set_caption("Results with " + str(p[17]) + "% of untreated water entering the wetland")

year_table_ammonia = pd.DataFrame([jakkur_wastewater_quality_data['NH4-N'],total_effluent_ammonia[17,:], stp_effluent_exp_data['NH4-N'], wetland_outlet_ammonia[17,:],wetland_effluent_exp_data['NH4-N']]).T
year_table_ammonia.columns = ['ammonia in wastewater (mg/L)','Modelled ammonia in STP effluent (mg/L)','Measured ammonia in STP effluent (mg/L)', 'Modelled ammonia in wetland effluent (mg/L)', 'Measured ammonia in wetland effluent (mg/L)']
year_table_ammonia.index = pd.Index(times,name = 'Date')

year_table_ammonia.style.set_caption("Results with " + str(p[17]) + "% of untreated water entering the wetland")

# Create a Pandas Excel writer using XlsxWriter as the engine
year_BOD_values = pd.ExcelWriter('BOD-Values.xlsx', engine='xlsxwriter')
year_ammonia_values = pd.ExcelWriter('ammonia-Values.xlsx', engine='xlsxwriter')

# Convert the dataframe to an XlsxWriter Excel object.
year_table_BOD.to_excel(year_BOD_values,sheet_name = 'BOD')
year_table_ammonia.to_excel(year_ammonia_values, sheet_name = 'ammonia')


# Get the xlsxwriter workbook and worksheet objects.
workbook  = year_BOD_values.book
worksheet = year_BOD_values.sheets['BOD']
workbook_2 = year_ammonia_values.book
worksheet_2 = year_ammonia_values.sheets['ammonia']

# Set the conditional format range.
start_row = 4
start_col = 1
end_row = len(year_table_BOD)+3
end_cold = 4

# Add a format. Light red fill with dark red text.
format1 = workbook.add_format({'bg_color': '#FFC7CE',
                               'font_color': '#9C0006'})

# Add a format. Orange fill with dark green text.
format2 = workbook.add_format({'bg_color': '#FF97306',
                               'font_color': '#9C2700'})

# Apply a conditional format to the cell range.
worksheet.conditional_format(start_row, start_col, end_row, end_cold, {'type':'cell','criteria':'between','minimum':10,'maximum':30, 'format':format2})
worksheet.conditional_format(start_row, start_col, end_row, end_cold, {'type':'cell','criteria':'>','value':'30', 'format':format1})

# Close the Pandas Excel writer and output the Excel file.
year_BOD_values.save()
year_ammonia_values.save()




#Plot visualisation of results for jakkur lake & Jakkur STP
days = np.arange(1,366,1)
year_table_BOD.insert(0, "Days", days)
year_table_BOD.insert(1, "General BOD discharge standard (mg/L)", 30)
year_table_BOD.insert(1, "Target BOD discharge standard (mg/L)", 10)
tech = str(stp_data['technologies_type'][0])

year_table_ammonia.insert(0, "Days", days)
year_table_ammonia.insert(1, "General ammonia discharge standard (mg/L)", 30)
year_table_ammonia.insert(1, "Target ammonia discharge standard (mg/L)", 10)


# year_table_BOD.plot(x='Days' , y=["BOD in wastewater (mg/L)", 'Measured BOD in STP effluent (mg/L)'],title = 'Results with '+ str(tech) +' technology',grid = "on")
# plt.show()

# year_table_BOD.plot(x='Days' , y=["BOD in wastewater (mg/L)", 'Modelled BOD in STP effluent (mg/L)'],title = 'Results with '+ str(tech) +' technology',grid = "on")
# plt.show()
# 'Results with '+ str(tech) +' technology'

year_table_BOD.plot(x='Days' , y=['Modelled BOD in STP effluent (mg/L)', 'Measured BOD in STP effluent (mg/L)',],title = 'Modelled Vs Measured BOD in Jakkur STP effluent' ,grid = "on")
plt.legend(loc='upper right', fontsize=9)
plt.xlim(0,365)
plt.ylim(0,50)
plt.ylabel('concentration in mg/lL')
plt.show()

year_table_BOD.plot(x='Days' , y=['Modelled BOD in wetland effluent (mg/L)', 'Measured BOD in wetland effluent (mg/L)'], title = 'Modelled Vs Measured BOD in Jakkur wetland effluent \n with '+ str(p[17]) +'% of untreated water passing through the wetland', grid = "on")
plt.legend(loc='upper left', fontsize=9)
plt.xlim(0,365)
plt.ylim(0,50)
plt.ylabel('concentration in mg/lL')
plt.show()

year_table_BOD.plot(x='Days' , y=['Measured BOD in STP effluent (mg/L)', 'Measured BOD in wetland effluent (mg/L)'], title = 'Comparison betwen measured BOD \n in Jakkur STP and Jakkur wetland effluents', grid = "on", color =('g','r'))
plt.legend(loc='upper left', fontsize=9)
plt.xlim(0,365)
plt.ylim(0,50)
plt.ylabel('concentration in mg/lL')
plt.show()

# year_table_BOD.plot(x='Days' , y=['Measured BOD in wetland effluent (mg/L)', 'Measured BOD in STP effluent (mg/L)'], title = 'Results with '+ str(p[17]) +'% of untreated water passing through the wetland', grid = "on")
# plt.show()


# year_table_BOD.plot(x='Days' , y=['Modelled BOD in wetland effluent (mg/L)', 'Modelled BOD in STP effluent (mg/L)'], title = 'Results with '+ str(p[17]) +'% of untreated water passing through the wetland', grid = "on")
# plt.show()

year_table_ammonia.plot(x='Days' , y=['Modelled ammonia in STP effluent (mg/L)', 'Measured ammonia in STP effluent (mg/L)'],title = 'Modelled Vs Measured ammonia in Jakkur STP effluent ',grid = "on")
plt.legend(loc='upper right', fontsize=9)
plt.xlim(0,365)
plt.ylim(0,70)
plt.ylabel('concentration in mg/lL')
plt.show()

year_table_ammonia.plot(x='Days' , y=['Modelled ammonia in wetland effluent (mg/L)', 'Measured ammonia in wetland effluent (mg/L)'], title = 'Modelled Vs Measured ammonia in Jakkur wetland effluent \n with '+ str(p[17]) +'% of untreated water passing through the wetland', grid = "on")
plt.legend(loc='upper left', fontsize=9)
plt.xlim(0,365)
plt.ylim(0,70)
plt.ylabel('concentration in mg/lL')
plt.show()

year_table_ammonia.plot(x='Days' , y=['Measured ammonia in STP effluent (mg/L)', 'Measured ammonia in wetland effluent (mg/L)'], title = 'Comparison betwen measured ammonia \n in Jakkur STP and Jakkur wetland effluents ', grid = "on", color =('g','r'))
plt.legend(loc='upper left', fontsize=9)
plt.xlim(0,365)
plt.ylim(0,60)
plt.ylabel('concentration in mg/lL')
plt.show()




relative_BOD_STP_error = ((year_table_BOD['Measured BOD in STP effluent (mg/L)'].mean()-year_table_BOD['Modelled BOD in STP effluent (mg/L)'].mean())/year_table_BOD['Measured BOD in STP effluent (mg/L)'].mean())
print(relative_BOD_STP_error)

relative_BOD_wetland_error = ((year_table_BOD['Measured BOD in wetland effluent (mg/L)'].mean()-year_table_BOD['Modelled BOD in wetland effluent (mg/L)'].mean())/year_table_BOD['Measured BOD in wetland effluent (mg/L)'].mean())
print(relative_BOD_wetland_error)

relative_ammonia_STP_error = ((year_table_ammonia['Measured ammonia in STP effluent (mg/L)'].mean()-year_table_ammonia['Modelled ammonia in STP effluent (mg/L)'].mean())/year_table_ammonia['Measured ammonia in STP effluent (mg/L)'].mean())
print(relative_ammonia_STP_error)

relative_ammonia_wetland_error = ((year_table_ammonia['Measured ammonia in wetland effluent (mg/L)'].mean()-year_table_ammonia['Modelled ammonia in wetland effluent (mg/L)'].mean())/year_table_ammonia['Measured ammonia in wetland effluent (mg/L)'].mean())
print(relative_ammonia_wetland_error)
############################################################################
#%%
#Multi-Criteria Analysis with the Weighted_Sum_model
technology_table = ['CAS','EA','SBR','MBR','MBBR','ABR','UASB','UASB+EA','UASB+SBR','UASB+MBR','UASB+MBBR','SFCW']
nb_tech = len(technology_table) 


f_MCA_tss = np.zeros((NB_DAYS))
f_MCA_cod = np.zeros((NB_DAYS))
f_MCA_bod = np.zeros((NB_DAYS))
f_MCA_nitrate = np.zeros((NB_DAYS))
f_MCA_TN = np.zeros((NB_DAYS))
f_MCA_ammonia = np.zeros((NB_DAYS))
f_MCA_phosphate = np.zeros((NB_DAYS))
f_MCA_TP = np.zeros((NB_DAYS))

MCA_tss = np.zeros((nb_tech))
MCA_cod = np.zeros((nb_tech))
MCA_bod = np.zeros((nb_tech))
MCA_nitrate = np.zeros((nb_tech))
MCA_TN = np.zeros((nb_tech))
MCA_ammonia = np.zeros((nb_tech))
MCA_phosphate = np.zeros((nb_tech))
MCA_TP = np.zeros((nb_tech))

MCA_tss_score = np.zeros((nb_tech))
MCA_cod_score = np.zeros((nb_tech))
MCA_bod_score = np.zeros((nb_tech))
MCA_nitrate_score = np.zeros((nb_tech))
MCA_TN_score = np.zeros((nb_tech))
MCA_ammonia_score = np.zeros((nb_tech))
MCA_phosphate_score = np.zeros((nb_tech))
MCA_TP_score = np.zeros((nb_tech))


MCA_capital_costs = np.zeros((nb_tech))
MCA_O_M_costs = np.zeros((nb_tech))

MCA_capital_costs_score = np.zeros((nb_tech))
MCA_O_M_costs_score = np.zeros((nb_tech))

MCA_total_score = np.zeros((nb_tech))
MCA_rank = np.zeros((nb_tech))


print("For which inhabitant number would you like to design the STP")
MCA_stp_inhabitants = int(input('number of ihabitants : '))
MCA_stp_capacity = MCA_stp_inhabitants * wwfracl #minimum capacity to cover the whole intended population en m3/d
MCA_stp_capacity_2 = MCA_stp_capacity * 10**(-6) #in MLD

print ("The minimum design capacity should be: "+ str(MCA_stp_capacity_2)+ ' MLD')
# MCA_average_influent_BOD = (jakkur_wastewater_quality_data['BOD'].mean())/1000


# print("At which percentage do you plan the STP will be used (between 0 and 1)?")
# MCA_stp_utilisation = float(input('utilisation between 0 and 1 : '))
# MCA_treated_volume = MCA_stp_capacity * MCA_stp_utilisation

tss_standard = int(input('tss standard: ')) #enter the target tss concentration (mg/L)
cod_standard = int(input('cod standard: '))
bod_standard = int(input('bod standard: '))
nitrate_standard = int(input('nitrate standard: '))
TN_standard = int(input('TN standard: '))
ammonia_standard = int(input('ammonia standard: '))
phosphate_standard = int(input('phosphate standard: '))
TP_standard = int(input('TP standard: '))

for idex_tech in range(0,nb_tech):
    technology = technology_table[idex_tech]
    for day in range(0, NB_DAYS):
        
        i_MCA_tss = jakkur_wastewater_quality_data['TSS'][day]
        i_MCA_cod = jakkur_wastewater_quality_data['COD'][day]
        i_MCA_bod = jakkur_wastewater_quality_data['BOD'][day]
        i_MCA_nitrate = jakkur_wastewater_quality_data['Nitrate'][day]
        i_MCA_TN = jakkur_wastewater_quality_data['TN'][day]
        i_MCA_ammonia = jakkur_wastewater_quality_data['NH4-N'][day]
        i_MCA_phosphate = jakkur_wastewater_quality_data['PO4-P'][day]
        i_MCA_TP = jakkur_wastewater_quality_data['TP'][day]
        
        f_MCA_tss[day], f_MCA_cod[day], f_MCA_bod[day], f_MCA_nitrate[day], f_MCA_TN[day], f_MCA_ammonia[day], f_MCA_phosphate[day], f_MCA_TP[day] = process_efficiency(technology, i_MCA_tss, i_MCA_cod, i_MCA_bod, i_MCA_nitrate, i_MCA_TN, i_MCA_ammonia, i_MCA_phosphate, i_MCA_TP)
        
    MCA_tss[idex_tech] = f_MCA_tss.mean()
    MCA_cod[idex_tech] = f_MCA_cod.mean()
    MCA_bod[idex_tech] = f_MCA_bod.mean()
    MCA_nitrate[idex_tech] = f_MCA_nitrate.mean()
    MCA_TN[idex_tech] = f_MCA_TN.mean()
    MCA_ammonia[idex_tech] = f_MCA_ammonia.mean()
    MCA_phosphate[idex_tech] = f_MCA_phosphate.mean()
    MCA_TP[idex_tech] = f_MCA_TP.mean()
    
    #standardization  
    MCA_tss_score[idex_tech] = abs(MCA_tss[idex_tech]-tss_standard)
    MCA_cod_score[idex_tech] = abs(MCA_cod[idex_tech]-cod_standard)
    MCA_bod_score[idex_tech] = abs(MCA_bod[idex_tech]-bod_standard)
    MCA_nitrate_score[idex_tech] = abs(MCA_nitrate[idex_tech]-nitrate_standard)
    MCA_TN_score[idex_tech] = abs(MCA_TN[idex_tech]-TN_standard)
    MCA_ammonia_score[idex_tech] = abs(MCA_ammonia[idex_tech]-ammonia_standard)
    MCA_phosphate_score[idex_tech] = abs(MCA_phosphate[idex_tech]-phosphate_standard)
    MCA_TP_score[idex_tech] = abs(MCA_TP[idex_tech]-TP_standard)
    
    MCA_tss_score[idex_tech] = (MCA_tss_score[idex_tech]- MCA_tss_score.mean())/MCA_tss_score.std()
    MCA_cod_score[idex_tech] = (MCA_cod_score[idex_tech]- MCA_cod_score.mean())/MCA_cod_score.std()
    MCA_bod_score[idex_tech] = (MCA_bod_score[idex_tech]- MCA_bod_score.mean())/MCA_bod_score.std()
    MCA_nitrate_score[idex_tech] = (MCA_nitrate_score[idex_tech]- MCA_nitrate_score.mean())/MCA_nitrate_score.std()
    MCA_TN_score[idex_tech] = (MCA_TN_score[idex_tech]- MCA_TN_score.mean())/MCA_TN_score.std()
    MCA_ammonia_score[idex_tech] = (MCA_ammonia_score[idex_tech]- MCA_ammonia_score.mean())/MCA_ammonia_score.std()
    MCA_phosphate_score[idex_tech] = (MCA_phosphate_score[idex_tech]- MCA_phosphate_score.mean())/MCA_phosphate_score.std()
    MCA_TP_score[idex_tech] =  (MCA_TP_score[idex_tech]-  MCA_TP_score.mean())/ MCA_TP_score.std()
        
    MCA_capital_costs[idex_tech],MCA_O_M_costs[idex_tech] = total_cost(technology, MCA_stp_inhabitants )
    
    MCA_capital_costs_score[idex_tech] = ((MCA_capital_costs[idex_tech]- MCA_capital_costs.mean())/MCA_capital_costs.std())
    MCA_O_M_costs_score[idex_tech] = ((MCA_O_M_costs[idex_tech] - MCA_O_M_costs.mean())/MCA_O_M_costs.std())
    
    MCA_total_score[idex_tech] =(MCA_tss_score[idex_tech]+ MCA_bod_score[idex_tech]+MCA_TN_score[idex_tech]+ MCA_nitrate_score[idex_tech]+ 4*MCA_capital_costs_score[idex_tech] + 4*MCA_O_M_costs_score[idex_tech]) #the two criteria are weighted equally
 
    MCA_matrix = pd.DataFrame([technology_table, MCA_tss_score, MCA_bod_score, MCA_TN_score,MCA_nitrate_score, MCA_capital_costs_score, MCA_O_M_costs_score, MCA_total_score])
    MCA_matrix = MCA_matrix.T
    MCA_matrix.columns = ['technology_table', 'MCA_tss_score', 'MCA_bod_score','MCA_TN_score','MCA_nitrate_score', 'MCA_capital_costs_score', 'MCA_O_M_costs_score', 'MCA_total_score']
    MCA_matrix['rank'] = MCA_matrix['MCA_total_score'].rank(method ='max')
    pd.DataFrame(MCA_matrix).to_csv("C:/Users/mkona/OneDrive/Bureau/Imperial_Msc EEBM_2021/Summer Project/project/WWT_module_repo/outputs_WW/test.csv")
    
#%%
    
    MCA_matrix = pd.DataFrame([technology_table, MCA_tss_score, MCA_cod_score, MCA_bod_score,MCA_nitrate_score, MCA_TN_score, MCA_ammonia_score, MCA_capital_costs_score, MCA_O_M_costs_score, MCA_total_score])
    MCA_matrix = MCA_matrix.T
    MCA_matrix.columns = ['technology_table', 'MCA_tss_score', 'MCA_cod_score', 'MCA_bod_score', 'MCA_TN_score', 'MCA_ammonia_score', 'MCA_capital_costs_score', 'MCA_O_M_costs_score', 'MCA_total_score']
    MCA_matrix['rank'] = MCA_matrix['MCA_total_score'].rank(method ='max')
    
    pd.DataFrame(MCA_matrix).to_csv("C:/Users/mkona/OneDrive/Bureau/Imperial_Msc EEBM_2021/Summer Project/project/WWT_module_repo/outputs_WW/test.csv")

        
    




#        capital_costs , O_M_costs = capital_costs + process_cost(technology,stp_capacity,treated_volume,design_BOD, treated_BOD )[0] , O_M_costs + process_cost(technology,stp_capacity,treated_volume,design_BOD, treated_BOD )[1]
# return capital_costs, O_M_costs

# print("Do you want to integrate a Horizontal Flow Constructed Wetland in the wetland ?")
# answer = str(input('Yes or No : '))
