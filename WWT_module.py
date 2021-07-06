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

#ignore all warnings
import warnings
warnings.filterwarnings('ignore')

#import functions
from utility_functions import *

#constants
NB_LAKES = 37
NB_DAYS = 365

#set WWT module input & output path directories 
input = os.path.join(workdir, "inputs_WW")
output = os.path.join(workdir, "outputs_WW")

# load STP csv file into Pandas dataframe
stp_path = os.path.join(input, "STP_data.csv")

stp_data = pd.read_csv(stp_path, 
                       dtype={'STP_ID':'int64', 'name':'str', 'lake':'str','lake_ID':'int64', 
                       'capacity_volume':'float64', 'percentage_utilisation':'float64',
                       'technologies_type':'str'})


#load tanks/lakes csv file into Pandas dataframe
#raw data on lakes and their catchment
tank_path = os.path.join(input, "tank_master.csv")

tank_data = pd.read_csv(tank_path,
                        dtype={'ID':'int64', 'name':'str', 'area_max':'float32', 
                       'vol_max':'float64', 'vol_open':'float64', 
                       'vol_close':'float64', 'catch_size':'float64', 
                       'catch_pop':'int64', 'paved':'float64', 'DS_tank':'int64',
                       'divert':'str', 'treated':'float64', 'dchanw':'float64', 'dchanh':'float64'})

#calculated data on the catchment and the lakes dynamics
#not to be loaded when module is inserted in the whole cascade model

tank_data_2 = []

for i in range(NB_LAKES):
    tank_path_2 = os.path.join(input, "tank_{}.csv".format(i))
    
    tank_data_2.append(pd.read_csv(tank_path_2,
                              dtype={'ID':'int64', 'name':'str',	'tank_wsarea':'float64',
                                     'tank_sewvol':'float64',	'tank_vopen':'float64',	'tank_evvol':'float64', 
                                     'tank_revol':'float64',	'spill':'float64',	'tank_uspill':'float64', 
                                     'tank_crunvol':'float64',	'tank_rajkalve':'float64',	
                                     'tank_inflow':'float64',	'tank_usdivert':'float64',	
                                     'tank_vclose':'float64', 'tank_stp':'float64',	'DS_tank':'int64',
                                     'divert':'str','treated':'float64'}))




#load all water sources quality csv file into Pandas dataframe

#data on wastewater quality generated from Jakkur catchment 
#TO DO FOR EACH CATCHMENT
wastewater_quality_path = os.path.join(input, "raw_sewage.csv")

wastewater_quality_data = pd.read_csv(wastewater_quality_path,
                        dtype={'pH':'float64', 
                       'TSS':'float64', 'COD':'float64', 
                       'BOD':'float64', 'TKN':'float64', 
                       'nitrite + nitrate':'float64', 'ammonium':'float64',
                       'phosphate':'float64',
                       'TP':'float64'})

#data on stormwater quality, calculated from litterature and Event Mean Concentration (EMC)
stormwater_quality_path = os.path.join(input, "stormwater_quality.csv")

stormwater_quality_data = pd.read_csv(wastewater_quality_path,
                        dtype={'BOD':'float64', 
                       'COD':'float64', 'TSS':'float64','TKN':'float64', 
                       'nitrate + nitrite':'float64', 'TP':'float64',
                       'ammonium':'float64'})

#data on lake water quality (only available for Jakkur lake so these data are 
#taken as a reference for a lake)
#TO DO : add these data to tank master or HCM daily output for each lake
lake_quality_path = os.path.join(input, "jakkur_lake_quality.csv")

lake_quality_data = pd.read_csv(lake_quality_path,
                        dtype={'pH':'float64', 
                       'Nitrates':'float64', 'TSS':'float64', 
                       'BOD':'float64','COD':'float64','phosphate':'float64', 
                       'ammonium':'float64'})


###################################################################

# Volumes of wastewater generated/Total untreated volume

volume_ww = np.zeros((NB_LAKES , NB_DAYS)) # volume of daily wastewater generated for each catchment
untreated_volume_ww = np.zeros((NB_LAKES , NB_DAYS)) # untreated volume of wastewater when the STP's capacity are not sufficient
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
        volume_ww[idx_lake, day] = tank_data['catch_pop'][idx_lake]*wwfracl
        
        #calculation of treated and untreated volumes
        stp_data_lake = stp_data.loc[stp_data['lake_ID'] == idx_lake] #table of STPs discharging in the same lake
        total_stp_lake_capacity = (stp_data_lake['capacity_volume']*stp_data_lake['percentage_utilisation']).sum() #total volume that could be treated by the STPs discharging in a same lake
        if (total_stp_lake_capacity > volume_ww[idx_lake, day]):
            treated_volume_ww[idx_lake, day] = volume_ww[idx_lake, day]
        else:
            treated_volume_ww[idx_lake, day] =  total_stp_lake_capacity
            untreated_volume_ww[idx_lake, day] = volume_ww[idx_lake, day] - treated_volume_ww[idx_lake, day]
        
        #SCS runoff volume
        tank_crunvol[idx_lake, day] = tank_data_2[idx_lake]['tank_crunvol'][day]
        
        #upstream spill volume 
        tank_uspill[idx_lake, day] = tank_data_2[idx_lake]['tank_uspill'][day]
    



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
untreated_water_phosphate = np.zeros((NB_LAKES , NB_DAYS,))
untreated_water_ammonium = np.zeros((NB_LAKES , NB_DAYS,))


#calculation of pollutant concentrations of the water entering the Rajakaluve
for idx_lake in range(0, NB_LAKES):
    for day in range(0, NB_DAYS):
         untreated_water_tss[idx_lake,day] = (tank_crunvol[idx_lake, day] * stormwater_quality_data['TSS'][0] 
                                             + tank_uspill[idx_lake, day] * lake_quality_data['TSS'][day] 
                                             + untreated_volume_ww[idx_lake, day] * wastewater_quality_data['TSS'][day])/(tank_crunvol[idx_lake, day] + tank_uspill[idx_lake, day] + untreated_volume_ww[idx_lake, day]) 
         untreated_water_cod[idx_lake,day] = (tank_crunvol[idx_lake, day] * stormwater_quality_data['COD'][0] 
                                             + tank_uspill[idx_lake, day] * lake_quality_data['COD'][day] 
                                             + untreated_volume_ww[idx_lake, day] * wastewater_quality_data['COD'][day])/(tank_crunvol[idx_lake, day] + tank_uspill[idx_lake, day] + untreated_volume_ww[idx_lake, day])
         untreated_water_bod[idx_lake,day] = (tank_crunvol[idx_lake, day] * stormwater_quality_data['BOD'][0] 
                                             + tank_uspill[idx_lake, day] * lake_quality_data['BOD'][day] 
                                             + untreated_volume_ww[idx_lake, day] * wastewater_quality_data['BOD'][day])/(tank_crunvol[idx_lake, day] + tank_uspill[idx_lake, day] + untreated_volume_ww[idx_lake, day])

#TO DO : other pollutants

plt.plot(untreated_water_tss[18])

#####################################################################

#Concentrations in the effluent of the STP 

# Declare blank arrays required for first set of calculations
total_effluent_tss = np.zeros((NB_LAKES , NB_DAYS,)) #tss concentration in the effluent of all the STP discharging in each lake
total_effluent_cod = np.zeros((NB_LAKES , NB_DAYS,)) #cod concentration in the effluent of all the STP discharging in each lake
total_effluent_bod = np.zeros((NB_LAKES , NB_DAYS,)) #bod concentration in the effluent of all the STP discharging in each lake


#calculate pollutant concentrations of the effluent of each STP for each day of the year for each lake

for idx_lake in range(0, NB_LAKES):
    nstps = np.shape(stp_data.loc[stp_data['lake_ID'] == idx_lake])[0]
    stp_capacity_table = (stp_data.loc[stp_data['lake_ID'] == idx_lake])['capacity_volume'] #matrix of capacity for lake underconsideration
    stp_utilisation_table = (stp_data.loc[stp_data['lake_ID'] == idx_lake])['percentage_utilisation']
    total_stp_capacity = (stp_capacity_table * stp_utilisation_table).sum()
    volume_treated_stp = np.zeros((1,nstps))
    effluent_tss = np.zeros((1,nstps))
    effluent_cod = np.zeros((1,nstps))
    effluent_bod = np.zeros((1,nstps))
    for day in range(0, NB_DAYS): 
        for istp in range(0, nstps):
            istp_capacity = stp_capacity_table[istp]
            istp_utilisation = stp_utilisation_table[istp]
            volume_treated_stp[istp] = treated_volume_ww[idx_lake, day] * istp_capacity * istp_utilisation / total_stp_capacity
            stp_type = str(stp_data['technologies_type'][istp])
            i_tss = wastewater_quality_data['TSS'][istp]
            i_cod = wastewater_quality_data['COD'][istp]
            i_bod = wastewater_quality_data['BOD'][istp]
            f_tss, f_cod, f_bod = total_efficiency(stp_type, i_tss, i_cod, i_bod)
            effluent_tss[istp] = f_tss
            effluent_cod[istp] = f_cod
            effluent_bod[istp] = f_bod
            
        total_effluent_tss[idx_lake,day] = ((effluent_tss * volume_treated_stp).sum())/treated_volume_ww[idx_lake, day]
        total_effluent_cod[idx_lake,day] = ((effluent_cod * volume_treated_stp).sum())/treated_volume_ww[idx_lake, day]
        total_effluent_bod[idx_lake,day] = ((effluent_bod * volume_treated_stp).sum())/treated_volume_ww[idx_lake, day]
            

#TO DO : other pollutants 

############################################################################################################
#TO DO : Give flexibility to the user by enabling a part of untreated water in the Rjakaluve to enter the wetland 

# for idx_lake in range(0, NB_LAKES):
#         for day in range(0, NB_DAYS): 
#             for istp in range(0, nstps):
#                 technology_combination = read_technology_type(stp_type)



############################################################################################################

#Volume & Concentrations in the inflow of the lake

#Declare blank arrays required for calculations of volume inflow
diverted_volume = np.zeros((NB_LAKES , NB_DAYS)) #for lakes having diversion channels, volume of water in rajakalve is preferably diverted
tank_inflow =  np.zeros((NB_LAKES , NB_DAYS)) #volume of water from the rajakalve entering the lake
total_tank_inflow = np.zeros((NB_LAKES , NB_DAYS)) #volume of water from the rajakalve and the STP entering the lake 
volume_rajakaluve = np.zeros((NB_LAKES , NB_DAYS)) #volume of untreated water in the Rajakaluve
tank_divthresh =np.zeros((NB_LAKES,1)) #volume that can be diverted

for idx_lake in range(0, NB_LAKES):
    tank_divthresh[idx_lake] = tank_data['dchanw'][idx_lake]*tank_data['dchanh'][idx_lake]*0.04*3600*24
    for day in range(0, NB_DAYS):
        volume_rajakaluve[idx_lake, day] = tank_crunvol[idx_lake, day] + tank_uspill[idx_lake, day] + untreated_volume_ww[idx_lake, day]
        if tank_data['divert'][idx_lake] == "y": 
            if volume_rajakaluve[idx_lake, day] > tank_divthresh[idx_lake]:
               tank_inflow[idx_lake, day] = volume_rajakaluve[idx_lake, day] - tank_divthresh[idx_lake]  
            else:
               tank_inflow[idx_lake, day] = 0
        else:            
            tank_inflow[idx_lake, day] = volume_rajakaluve[idx_lake, day]
            
        total_tank_inflow[idx_lake, day] = tank_inflow[idx_lake, day] + treated_volume_ww[idx_lake, day]

#Declare blank arrays required for calculations of inflow concentrations

total_inflow_tss = np.zeros((NB_LAKES , NB_DAYS,)) #tss concentration in the inflow of each lake
total_inflow_cod = np.zeros((NB_LAKES , NB_DAYS,)) #cod concentration in the inflow of each lake
total_inflow_bod = np.zeros((NB_LAKES , NB_DAYS,)) #bod concentration in the inflow of each lake

for idx_lake in range(0, NB_LAKES):
    for day in range(0, NB_DAYS): 
        total_inflow_tss[idx_lake, day] = (total_effluent_tss[idx_lake,day]*treated_volume_ww[idx_lake, day] 
                                          + untreated_water_tss[idx_lake,day] * tank_inflow[idx_lake, day])/ total_tank_inflow[idx_lake, day]
        total_inflow_cod[idx_lake, day] = (total_effluent_cod[idx_lake,day]*treated_volume_ww[idx_lake, day] 
                                          + untreated_water_cod[idx_lake,day] * tank_inflow[idx_lake, day])/ total_tank_inflow[idx_lake, day]
        total_inflow_bod[idx_lake, day] = (total_effluent_bod[idx_lake,day]*treated_volume_ww[idx_lake, day] 
                                          + untreated_water_bod[idx_lake,day] * tank_inflow[idx_lake, day])/ total_tank_inflow[idx_lake, day]
 
fig = plt.figure()
ax1 = fig.add_subplot(111)
days = np.arange(365)
ax1.scatter(days, total_inflow_tss[18], c='r', s=2, label ='inflow tss' )
ax1.scatter(days, total_effluent_tss[18], c='g', s=2, label ='stp effluent tss')
ax1.scatter(days, untreated_water_tss[18], c='b', s=2, label = 'rajakaluve tss')
plt.xlabel('days')
plt.ylabel('tss concentrations')
plt.legend()
plt.show()




