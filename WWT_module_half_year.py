# -*- coding: utf-8 -*-
"""
Created on Wed Jul 28 23:27:41 2021

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
NB_DAYS = 184
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

#data on wastewater quality generated from Jakkur catchment 
wastewater_quality_path = os.path.join(input_dir, "raw_sewage_half_year.csv")

jakkur_wastewater_quality_data = pd.read_csv(wastewater_quality_path, sep=";",
                        dtype={'Date':'str','TSS':'float64','BOD':'float64','COD':'float64',
                       'Nitrate':'float64', 'NH4-N':'float64', 
                       'PO4-P':'float64'})



#data on stormwater quality, calculated from litterature and Event Mean Concentration (EMC)
stormwater_quality_path = os.path.join(input_dir, "stormwater_quality.csv")

stormwater_quality_data = pd.read_csv(stormwater_quality_path, sep=";",
                        dtype={'BOD':'float64', 
                       'COD':'float64', 'TSS':'float64','TKN':'float64', 
                       'nitrate':'float64', 'TP':'float64','PO4-P':'float64',
                       'NH3-N':'float64'})


#data on lake water quality (only available for Jakkur lake so these data are 
#taken as a reference for a lake)
lake_quality_path = os.path.join(input_dir, "jakkur_lake_quality_half_year.csv")

jakkur_lake_quality_data = pd.read_csv(lake_quality_path, sep=";",
                        dtype={'Date':'str', 'TSS':'float64', 'BOD':'float64','COD':'float64','NO3-N':'float64',
                       'Nitrates':'float64', 'NH4-N':'float64', 
                       'TN':'float64','PO4-P':'float64','TP':'float64'})


#data of experimental concentrations in STP effluent 

stp_effluent_path = os.path.join(input_dir, "STP_effluent_exp_2016.csv")

stp_effluent_exp_data = pd.read_csv(stp_effluent_path, sep=";",
                        dtype={'Date':'str', 'TSS':'float64', 'BOD':'float64','COD':'float64',
                       'Nitrates':'float64', 'NH4-N':'float64', 
                       'PO4-P':'float64'})



#data of experimental concentrations in wetland effleunt

wetland_effluent_path = os.path.join(input_dir, "wetland_effluent_exp_half_year.csv")

wetland_effluent_exp_data = pd.read_csv(wetland_effluent_path, sep=";",
                        dtype={'Date':'str', 'TSS':'float64', 'BOD':'float64','COD':'float64','NO3-N':'float64',
                       'Nitrates':'float64', 'NH4-N':'float64', 
                       'TN':'float64','PO4-P':'float64','TP':'float64'})

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
        if idx_lake == 17 :
            volume_ww[idx_lake, day] = tank_data['catch_pop'][idx_lake]*wwfracl + tank_data['catch_pop'][idx_lake-1]*wwfracl
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
        tank_crunvol[idx_lake, day] = tank_data_2[idx_lake]['tank_crunvol'][120+day]
        
        #upstream spill volume 
        tank_uspill[idx_lake, day] = tank_data_2[idx_lake]['tank_uspill'][120+day]
    



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
        if (tank_crunvol[idx_lake, day] + tank_uspill[idx_lake, day] + untreated_volume_ww[idx_lake, day])== 0:
         untreated_water_tss[idx_lake,day] = 0 
         untreated_water_cod[idx_lake,day] = 0
         untreated_water_nitrate[idx_lake,day] = 0
         untreated_water_TN[idx_lake,day] = 0 
         untreated_water_ammonia[idx_lake,day] = 0
         untreated_water_phosphate[idx_lake,day] = 0
         untreated_water_TP[idx_lake,day] = 0
            
            
        else:
         untreated_water_tss[idx_lake,day] = (tank_crunvol[idx_lake, day] * stormwater_quality_data['TSS'][0] 
                                             + tank_uspill[idx_lake, day] * jakkur_lake_quality_data['TSS'][day] 
                                             + untreated_volume_ww[idx_lake, day] * jakkur_wastewater_quality_data['TSS'][day])/(untreated_water_volume[idx_lake,day]) 
        
         untreated_water_cod[idx_lake,day] = (tank_crunvol[idx_lake, day] * stormwater_quality_data['COD'][0] 
                                             + tank_uspill[idx_lake, day] * jakkur_lake_quality_data['COD'][day] 
                                             + untreated_volume_ww[idx_lake, day] * jakkur_wastewater_quality_data['COD'][day])/(untreated_water_volume[idx_lake,day])

        
         untreated_water_bod[idx_lake,day] = (tank_crunvol[idx_lake, day] * stormwater_quality_data['BOD'][0] 
                                              + tank_uspill[idx_lake, day] * jakkur_lake_quality_data['BOD'][day] 
                                              + untreated_volume_ww[idx_lake, day] * jakkur_wastewater_quality_data['BOD'][day])/(untreated_water_volume[idx_lake,day])
          
         untreated_water_nitrate[idx_lake,day] = (tank_crunvol[idx_lake, day] * stormwater_quality_data['Nitrate'][0] 
                                               + tank_uspill[idx_lake, day] * jakkur_lake_quality_data['Nitrate'][day] 
                                               + untreated_volume_ww[idx_lake, day] * jakkur_wastewater_quality_data['Nitrate'][day])/(untreated_water_volume[idx_lake,day])

         # untreated_water_TN[idx_lake,day] = (tank_crunvol[idx_lake, day] * stormwater_quality_data['TN'][0] 
         #                                       + tank_uspill[idx_lake, day] * jakkur_lake_quality_data['TN'][day] 
         #                                       + untreated_volume_ww[idx_lake, day] * jakkur_wastewater_quality_data['TN'][day])/(untreated_water_volume[idx_lake,day])

         untreated_water_ammonia[idx_lake,day] = (tank_crunvol[idx_lake, day] * stormwater_quality_data['NH3-N'][0] 
                                               + tank_uspill[idx_lake, day] * jakkur_lake_quality_data['NH4-N'][day] 
                                               + untreated_volume_ww[idx_lake, day] * jakkur_wastewater_quality_data['NH4-N'][day])/(untreated_water_volume[idx_lake,day])

         untreated_water_phosphate[idx_lake,day] = (tank_crunvol[idx_lake, day] * stormwater_quality_data['PO4-P'][0] 
                                               + tank_uspill[idx_lake, day] * jakkur_lake_quality_data['PO4-P'][day] 
                                               + untreated_volume_ww[idx_lake, day] * jakkur_wastewater_quality_data['PO4-P'][day])/(untreated_water_volume[idx_lake,day])

         # untreated_water_TP[idx_lake,day] = (tank_crunvol[idx_lake, day] * stormwater_quality_data['TP'][0] 
         #                                       + tank_uspill[idx_lake, day] * jakkur_lake_quality_data['TP'][day] 
         #                                       + untreated_volume_ww[idx_lake, day] * jakkur_wastewater_quality_data['TP'][day])/(untreated_water_volume[idx_lake,day])



#####################################################################

#Concentrations in the effluent of the STP 

# Declare blank arrays required for first set of calculations
total_effluent_tss = np.zeros((NB_LAKES , NB_DAYS,)) #tss concentration in the effluent of all the STP discharging in each lake
total_effluent_cod = np.zeros((NB_LAKES , NB_DAYS,)) #cod concentration in the effluent of all the STP discharging in each lake
total_effluent_bod = np.zeros((NB_LAKES , NB_DAYS,)) #bod concentration in the effluent of all the STP discharging in each lake
total_effluent_nitrate = np.zeros((NB_LAKES , NB_DAYS,)) 
# total_effluent_TN = np.zeros((NB_LAKES , NB_DAYS,)) 
total_effluent_ammonia = np.zeros((NB_LAKES , NB_DAYS,)) 
total_effluent_phosphate = np.zeros((NB_LAKES , NB_DAYS,)) 
# total_effluent_TP = np.zeros((NB_LAKES , NB_DAYS,)) 
        

#calculate pollutant concentrations of the effluent of each STP for each day of the year for each lake

for idx_lake in range(0, NB_LAKES):
    nstps = np.shape(stp_data.loc[stp_data['lake_ID'] == idx_lake + 1])[0]
    stp_capacity_table = (stp_data.loc[stp_data['lake_ID'] == idx_lake + 1])['capacity_volume'] #matrix of capacity for lake underconsideration
    stp_utilisation_table = (stp_data.loc[stp_data['lake_ID'] == idx_lake + 1])['percentage_utilisation']
    total_stp_capacity = (stp_capacity_table * stp_utilisation_table).sum()
    volume_treated_stp = np.zeros((1,nstps))
    effluent_tss = np.zeros((1,nstps))
    effluent_cod = np.zeros((1,nstps))
    effluent_bod = np.zeros((1,nstps))
    effluent_nitrate = np.zeros((1,nstps))
    # effluent_TN = np.zeros((1,nstps))
    effluent_ammonia = np.zeros((1,nstps))
    effluent_phosphate = np.zeros((1,nstps))
    # effluent_TP = np.zeros((1,nstps))
    
    for day in range(0, NB_DAYS): 
        for istp in range(0, nstps):
            istp_capacity = stp_capacity_table[istp]
            istp_utilisation = stp_utilisation_table[istp]
            volume_treated_stp[istp] = treated_volume_ww[idx_lake, day] * istp_capacity * istp_utilisation / total_stp_capacity
            stp_type = str(stp_data['technologies_type'][istp])
            i_tss = jakkur_wastewater_quality_data['TSS'][day]
            i_cod = jakkur_wastewater_quality_data['COD'][day]
            i_bod = jakkur_wastewater_quality_data['BOD'][day]
            i_nitrate = jakkur_wastewater_quality_data['Nitrate'][day]
            # i_TN = jakkur_wastewater_quality_data['TN'][day]
            i_ammonia = jakkur_wastewater_quality_data['NH4-N'][day]
            i_phosphate = jakkur_wastewater_quality_data['PO4-P'][day]
            # i_TP = jakkur_wastewater_quality_data['TP'][day]
            f_tss, f_cod, f_bod, f_nitrate, f_ammonia, f_phosphate = process_efficiency_2(stp_type, i_tss, i_cod, i_bod, i_nitrate, i_ammonia, i_phosphate)
            effluent_tss[istp] = f_tss
            effluent_cod[istp] = f_cod
            effluent_bod[istp] = f_bod
            effluent_nitrate[istp] = f_nitrate
            # effluent_TN[istp] = f_TN
            effluent_ammonia[istp] = f_ammonia
            effluent_phosphate[istp] = f_phosphate
            # effluent_TP[istp] = f_TP
            
        total_effluent_tss[idx_lake,day] = ((effluent_tss * volume_treated_stp).sum())/treated_volume_ww[idx_lake, day]
        total_effluent_cod[idx_lake,day] = ((effluent_cod * volume_treated_stp).sum())/treated_volume_ww[idx_lake, day]
        total_effluent_bod[idx_lake,day] = ((effluent_bod * volume_treated_stp).sum())/treated_volume_ww[idx_lake, day]
        total_effluent_nitrate[idx_lake,day] = ((effluent_nitrate * volume_treated_stp).sum())/treated_volume_ww[idx_lake, day]
        #total_effluent_TN[idx_lake,day] = ((effluent_TN * volume_treated_stp).sum())/treated_volume_ww[idx_lake, day]
        total_effluent_ammonia[idx_lake,day] = ((effluent_ammonia * volume_treated_stp).sum())/treated_volume_ww[idx_lake, day]
        total_effluent_phosphate[idx_lake,day] = ((effluent_phosphate * volume_treated_stp).sum())/treated_volume_ww[idx_lake, day]
        #total_effluent_TP[idx_lake,day] = ((effluent_TP * volume_treated_stp).sum())/treated_volume_ww[idx_lake, day]
        
        


############################################################################################################


volume_rw_wetland = np.zeros((NB_LAKES , NB_DAYS,)) 
total_volume_wetland = np.zeros((NB_LAKES , NB_DAYS,)) 

wetland_inlet_tss = np.zeros((NB_LAKES , NB_DAYS,)) 
wetland_inlet_cod = np.zeros((NB_LAKES , NB_DAYS,)) 
wetland_inlet_bod = np.zeros((NB_LAKES , NB_DAYS,)) 
wetland_inlet_nitrate = np.zeros((NB_LAKES , NB_DAYS,)) 
#wetland_inlet_TN = np.zeros((NB_LAKES , NB_DAYS,)) 
wetland_inlet_ammonia = np.zeros((NB_LAKES , NB_DAYS,)) 
wetland_inlet_phosphate = np.zeros((NB_LAKES , NB_DAYS,)) 
#wetland_inlet_TP = np.zeros((NB_LAKES , NB_DAYS,)) 

 
wetland_outlet_tss = np.zeros((NB_LAKES , NB_DAYS,)) 
wetland_outlet_cod = np.zeros((NB_LAKES , NB_DAYS,)) 
wetland_outlet_bod = np.zeros((NB_LAKES , NB_DAYS,)) 
wetland_outlet_nitrate = np.zeros((NB_LAKES , NB_DAYS,)) 
#wetland_outlet_TN = np.zeros((NB_LAKES , NB_DAYS,)) 
wetland_outlet_ammonia = np.zeros((NB_LAKES , NB_DAYS,)) 
wetland_outlet_phosphate = np.zeros((NB_LAKES , NB_DAYS,)) 
#wetland_outlet_TP = np.zeros((NB_LAKES , NB_DAYS,)) 

p = np.zeros(NB_LAKES) 


for idx_lake in range(0, NB_LAKES):
   if tank_data['wetland'][idx_lake]== 'y':
       print("which average percentage of raw wastewater is passing through the wetland of tank " + str(idx_lake+1) + " ?")
       percentage = input('The percentage : ')
       p[idx_lake] = percentage
       
   else :
       percentage = 0
       p[idx_lake] = percentage
        
   for day in range(0, NB_DAYS):
       volume_rw_wetland[idx_lake,day] = p[idx_lake]/100 * untreated_water_volume[idx_lake,day] #volume of untreated water/raw water (spill,runoff,wastewater) entering the wetland
       total_volume_wetland[idx_lake,day] = volume_rw_wetland[idx_lake,day] + treated_volume_ww[idx_lake, day]
       
       wetland_inlet_tss[idx_lake,day] = (total_effluent_tss[idx_lake,day] * treated_volume_ww[idx_lake, day] + untreated_water_tss[idx_lake,day]* volume_rw_wetland[idx_lake,day])/ total_volume_wetland[idx_lake,day]
       wetland_inlet_cod[idx_lake,day] = (total_effluent_cod[idx_lake,day] * treated_volume_ww[idx_lake, day] + untreated_water_cod[idx_lake,day]* volume_rw_wetland[idx_lake,day])/ total_volume_wetland[idx_lake,day]
       wetland_inlet_bod[idx_lake,day] = (total_effluent_bod[idx_lake,day] * treated_volume_ww[idx_lake, day] + untreated_water_bod[idx_lake,day]* volume_rw_wetland[idx_lake,day])/ total_volume_wetland[idx_lake,day]
       wetland_inlet_nitrate[idx_lake,day] = (total_effluent_nitrate[idx_lake,day] * treated_volume_ww[idx_lake, day] + untreated_water_nitrate[idx_lake,day]* volume_rw_wetland[idx_lake,day])/ total_volume_wetland[idx_lake,day]
       #wetland_inlet_TN[idx_lake,day] = (total_effluent_TN[idx_lake,day] * treated_volume_ww[idx_lake, day] + untreated_water_TN[idx_lake,day]* volume_rw_wetland[idx_lake,day])/ total_volume_wetland[idx_lake,day]
       wetland_inlet_ammonia[idx_lake,day] = (total_effluent_ammonia[idx_lake,day] * treated_volume_ww[idx_lake, day] + untreated_water_ammonia[idx_lake,day]* volume_rw_wetland[idx_lake,day])/ total_volume_wetland[idx_lake,day]
       wetland_inlet_phosphate[idx_lake,day] = (total_effluent_phosphate[idx_lake,day] * treated_volume_ww[idx_lake, day] + untreated_water_phosphate[idx_lake,day]* volume_rw_wetland[idx_lake,day])/ total_volume_wetland[idx_lake,day] 
       #wetland_inlet_TP[idx_lake,day] = (total_effluent_TP[idx_lake,day] * treated_volume_ww[idx_lake, day] + untreated_water_TP[idx_lake,day]* volume_rw_wetland[idx_lake,day])/ total_volume_wetland[idx_lake,day]
       
       tss = wetland_inlet_tss[idx_lake,day] 
       cod = wetland_inlet_cod[idx_lake,day] 
       bod = wetland_inlet_bod[idx_lake,day]
       nitrate = wetland_inlet_nitrate[idx_lake,day] 
       #TN = wetland_inlet_TN[idx_lake,day]
       ammonia = wetland_inlet_ammonia[idx_lake,day] 
       phosphate = wetland_inlet_phosphate[idx_lake,day]
       #TP = wetland_inlet_TP[idx_lake,day]
       
       wetland_outlet_tss[idx_lake,day], wetland_outlet_cod[idx_lake,day], wetland_outlet_bod[idx_lake,day], wetland_outlet_nitrate[idx_lake,day], wetland_outlet_ammonia[idx_lake,day], wetland_outlet_phosphate[idx_lake,day] = wetland_efficiency_2(tss, cod, bod, nitrate, ammonia, phosphate)
       
      

#TO DO : ajouter une question sur le wetland et mettre un warning si la capacité dépasse 


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
#total_inflow_TN = np.zeros((NB_LAKES , NB_DAYS,))
total_inflow_ammonia = np.zeros((NB_LAKES , NB_DAYS,))
total_inflow_phosphate = np.zeros((NB_LAKES , NB_DAYS,))
#total_inflow_TP = np.zeros((NB_LAKES , NB_DAYS,))


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
 
        #total_inflow_TN[idx_lake, day] = (wetland_outlet_TN[idx_lake,day] * total_volume_wetland[idx_lake, day]
                                          #+ untreated_water_TN[idx_lake,day] * tank_inflow[idx_lake, day])/ total_tank_inflow[idx_lake, day]
    
        total_inflow_ammonia[idx_lake, day] = (wetland_outlet_ammonia[idx_lake,day] * total_volume_wetland[idx_lake, day]
                                          + untreated_water_ammonia[idx_lake,day] * tank_inflow[idx_lake, day])/ total_tank_inflow[idx_lake, day]
    
    
        total_inflow_phosphate[idx_lake, day] = (wetland_outlet_phosphate[idx_lake,day] * total_volume_wetland[idx_lake, day]
                                          + untreated_water_phosphate[idx_lake,day] * tank_inflow[idx_lake, day])/ total_tank_inflow[idx_lake, day]
    
    
        #total_inflow_TP[idx_lake, day] = (wetland_outlet_TP[idx_lake,day] * total_volume_wetland[idx_lake, day]
                                         # + untreated_water_TP[idx_lake,day] * tank_inflow[idx_lake, day])/ total_tank_inflow[idx_lake, day]
    
    
    
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

#Cost functions 

average_BOD = (jakkur_wastewater_quality_data['BOD'].sum())/NB_DAYS
capital_costs = np.zeros((NB_STP ,1 ))
O_M_costs = np.zeros((NB_STP ,1 ))

for istp in range (0,NB_STP):
    design_BOD = stp_data['capacity_volume'][istp] * average_BOD
    treated_BOD = stp_data['capacity_volume'][istp] * stp_data['percentage_utilisation'][istp] * average_BOD
    stp_type = str(stp_data['technologies_type'][istp])
    stp_capacity = stp_data['capacity_volume'][istp]
    treated_volume = stp_data['capacity_volume'][istp] * stp_data['percentage_utilisation'][istp]
    capital_costs[istp],O_M_costs[istp] = total_cost(stp_type,stp_capacity,treated_volume,design_BOD, treated_BOD )
    
    print(capital_costs, O_M_costs)
    
    

########################################################################################################################
#create output as csv files

for idx_lake in range (NB_LAKES):
    outcalc = [[untreated_volume_ww[idx_lake,:],untreated_water_tss[idx_lake,:],untreated_water_cod[idx_lake,:],untreated_water_bod[idx_lake,:],
            total_effluent_tss[idx_lake,:],total_effluent_cod[idx_lake,:],total_effluent_bod[idx_lake,:], wetland_outlet_tss[idx_lake,:], wetland_outlet_cod[idx_lake,:],wetland_outlet_bod[idx_lake,:],
            total_inflow_tss[idx_lake,:],total_inflow_cod[idx_lake,:],total_inflow_bod[idx_lake,:]]]  

    import itertools
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
times = pd.Series(pd.date_range('2021', periods=184, freq='D'))
np.array(times)
                  
jakkur_wastewater_quality_data.plot(x="Date",y="BOD")
plt.show()

year_table = pd.DataFrame([jakkur_wastewater_quality_data['BOD'],total_effluent_bod[17,:], stp_effluent_exp_data['BOD'], wetland_outlet_bod[17,:],wetland_effluent_exp_data['BOD']]).T
year_table.columns = ['BOD in wastewater (mg/L)','Modelled BOD in STP effluent (mg/L)','Experimental BOD in STP effluent (mg/L)', 'Modelled BOD in wetland effluent (mg/L)', 'Experimental BOD in wetland effluent (mg/L)']
year_table.index = pd.Index(times,name = 'Date')

year_table.style.set_caption("Results with " + str(p[17]) + "% of untreated water entering the wetland")

# Create a Pandas Excel writer using XlsxWriter as the engine
year_BOD_values = pd.ExcelWriter('BOD-Values.xlsx', engine='xlsxwriter')

# Convert the dataframe to an XlsxWriter Excel object.
year_table.to_excel(year_BOD_values,sheet_name = 'BOD')

# Get the xlsxwriter workbook and worksheet objects.
workbook  = year_BOD_values.book
worksheet = year_BOD_values.sheets['BOD']

# Set the conditional format range.
start_row = 4
start_col = 1
end_row = len(year_table)+3
end_cold = 4

# Add a format. Light red fill with dark red text.
format1 = workbook.add_format({'bg_color': '#FFC7CE',
                               'font_color': '#9C0006'})

# Add a format. Orange fill with dark green text.
format2 = workbook.add_format({'bg_color': '#FF97306',
                               'font_color': '#9C2700'})

# Apply a conditional format to the cell range.
worksheet.conditional_format(start_row, start_col, end_row, end_cold, {'type':'cell','criteria':'>','value':'10', 'format':format2})
worksheet.conditional_format(start_row, start_col, end_row, end_cold, {'type':'cell','criteria':'>','value':'30', 'format':format1})

# Close the Pandas Excel writer and output the Excel file.
year_BOD_values.save()

#alternative way to present the table
# fig = plt.figure(figsize = (10, 2))
# ax = fig.add_subplot(111)

# ax.table(cellText = year_table.values,
#           rowLabels = year_table.index,
#           colLabels = year_table.columns,
#           loc = "center"
#          )
# ax.set_title("")

# ax.axis("off");


#Plot visualisation of results for jakkur lake & Jakkur STP
days = np.arange(1,185,1)
year_table.insert(0, "Days", days)
year_table.insert(1, "General BOD discharge standard (mg/L)", 30)
year_table.insert(1, "Target BOD discharge standard (mg/L)", 10)


year_table.plot(x='Days' , y=["BOD in wastewater (mg/L)", 'Experimental BOD in STP effluent (mg/L)'],title = 'Results with UASB+EA technology',grid = "on")
plt.show()

year_table.plot(x='Days' , y=["BOD in wastewater (mg/L)", 'Modelled BOD in STP effluent (mg/L)'],title = 'Results with UASB+EA technology',grid = "on")
plt.show()


year_table.plot(x='Days' , y=['Modelled BOD in STP effluent (mg/L)', 'Experimental BOD in STP effluent (mg/L)',"Target BOD discharge standard (mg/L)","General BOD discharge standard (mg/L)"],title = 'Results with UASB+EA technology',grid = "on")
plt.show()

year_table.plot(x='Days' , y=['Modelled BOD in wetland effluent (mg/L)', 'Experimental BOD in wetland effluent (mg/L)',"Target BOD discharge standard (mg/L)","General BOD discharge standard (mg/L)"], title = 'Results with '+ str(p[17]) +'% of untreated water passing through the wetland', grid = "on")
plt.show()

year_table.plot(x='Days' , y=['Experimental BOD in wetland effluent (mg/L)', 'Experimental BOD in STP effluent (mg/L)',"Target BOD discharge standard (mg/L)","General BOD discharge standard (mg/L)"], title = 'Results with '+ str(p[17]) +'% of untreated water passing through the wetland', grid = "on")
plt.show()


year_table.plot(x='Days' , y=['Modelled BOD in wetland effluent (mg/L)', 'Modelled BOD in STP effluent (mg/L)'], title = 'Results with '+ str(p[17]) +'% of untreated water passing through the wetland', grid = "on")
plt.show()