# -*- coding: utf-8 -*-
"""
Created on Wed Jun  2 17:35:00 2021

@author: mkona
"""

#import relevant system/os commands
from os import chdir, listdir, getcwd

'''set the working directory (change this path to the location where all model 
input files are)'''

workdir = 'C:/Users/mkona/OneDrive/Bureau/Imperial_Msc EEBM_2021/Summer Project/project/Literature review/ATREE documents/Cascade_Model/'
chdir(workdir)

#import relevant modules
import os #operating system
import csv #read csv files
import numpy as np
import pandas as pd

#import functions
from utility_functions import process_efficiency

#set WWT module input & output path directories 
input = os.path.join(workdir, "inputs_WW")
output = os.path.join(workdir, "outputs_WW")

# load STP csv file into Pandas dataframe
stp_path = os.path.join(input, "STP_data.csv")

stp_data = pd.read_csv(stp_path, 
                       dtype={'STP_ID':'int64', 'name':'str', 'lake':'str','lake_ID':'int64', 
                       'treated_volume':'float64', 'technologies_type':'str', 
                       'DO':'float64', 'pH':'float64', 'temperature':'float64',
                       'nitrates':'int64', 'phosphates':'float64'})

# load drain csv file into Pandas dataframe
drain_path = os.path.join(input, "drain_data.csv")

drain_data = pd.read_csv(drain_path, 
                       dtype={'drain_ID':'int64', 'lake':'str', 'lake_ID':'int64', 
                       'volume_discharged':'float64','DO':'float64',
                       'nitrates':'int64', 'phosphates':'float64'})



###################################################################


#number of STPs
nstps = 1

# Declare blank arrays required for first set of calculations
effluent_do = []
effluent_nitrate = []
effluent_phosphate = []
effluent_volume = []
lake_id = []

#calculate pollutant concentrations of the effluent of each STP 
for istp in range(0,nstps):
    stp_type = stp_data['technologies_type'][istp]
    ph = stp_data['pH'][istp]
    temperature = stp_data['temperature'][istp]
    i_nitrate = stp_data['nitrates(mg/l)'][istp]
    i_do = stp_data['DO(mg/l)'][istp]
    i_phosphate = stp_data['phosphates(mg/l)'][istp]
    f_nitrate, f_do, f_phosphate = process_efficiency(stp_type, ph, temperature, i_nitrate, i_do, i_phosphate)
    effluent_do.append(f_do)
    effluent_nitrate.append(f_nitrate)
    effluent_phosphate.append(f_phosphate)
    effluent_volume.append(stp_data['treated_volume'][istp])
    lake_id.append(stp_data['lake_ID'][istp])



#####################################################################

#number of lake
nlake = 1

#Declare blank arrays required for first set of calculations
total_drain_volume_discharged = []
total_drain_do_concentration = []
total_drain_nitrate_concentration = []
total_drain_phosphate_concentration = []


for ilake in range(1, nlake + 1):
    drain_data_lake = drain_data.loc[drain_data['lake_ID'] == ilake]
    total_discharged = drain_data_lake['volume_discharged'].sum()
    total_drain_volume_discharged.append(drain_data_lake['volume_discharged'].sum())
    total_drain_do_concentration.append((drain_data_lake['DO(mg/l)']*drain_data_lake['volume_discharged']).sum()/total_discharged)
    total_drain_nitrate_concentration.append((drain_data_lake['nitrates(mg/l)']*drain_data_lake['volume_discharged']).sum()/total_discharged)
    total_drain_phosphate_concentration.append((drain_data_lake['phosphates(mg/l)']*drain_data_lake['volume_discharged']).sum()/total_discharged)


total_volume_discharged = []
total_do_concentration = []
total_nitrates_concentration = []
total_phosphates_concentration = []

for ilake in range(1, nlake + 1):
    total_volume_discharged_by_stp = 0
    total_do_mass_of_stp = 0
    total_nitrates_mass_of_stp = 0
    total_phosphates_mass_of_stp = 0
    for k in range(len(lake_id)):
        if lake_id[k] == ilake:
            total_volume_discharged_by_stp += effluent_volume[k]
            total_do_mass_of_stp += effluent_do[k]*effluent_volume[k]
            total_nitrates_mass_of_stp += effluent_nitrate[k]*effluent_volume[k]
            total_phosphates_mass_of_stp += effluent_phosphate[k]*effluent_volume[k]
    total_volume_discharged.append(total_drain_volume_discharged[ilake - 1] + total_volume_discharged_by_stp)
    total_do_concentration.append((total_do_mass_of_stp + total_drain_do_concentration[ilake - 1] * total_drain_volume_discharged[ilake - 1])/total_volume_discharged[ilake - 1])
    total_nitrates_concentration.append((total_nitrates_mass_of_stp + total_drain_nitrate_concentration[ilake - 1] * total_drain_volume_discharged[ilake - 1])/total_volume_discharged[ilake - 1])
    total_phosphates_concentration.append((total_phosphates_mass_of_stp + total_drain_phosphate_concentration[ilake - 1] * total_drain_volume_discharged[ilake - 1])/total_volume_discharged[ilake - 1])
