#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corrected and Tiem Synced Backpack data
Created on Sun Aug 27 14:11:11 2023

This program takes PM2.5 colocation data (raw BackpAQ and hourly AirNow Jackson St), quality controls it for hourly and daily completeness, and evaluates
colocation metrics against recommended EPA Air Sensor Performance Standards

Output Figures: Hourly/Daily Correlation Plots, Hourly/Daily Timeseries
Output Files: Table of colocation performance metrics compared against EPA recommendations (csv), Merged Hourly/Daily BackpaAQ and Jackson St data (csv)


@author: TDEnviro
"""

# Required libraries
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import timedelta
import math


#%% User Settings (directories, filenames, time period, etc.)

# General data directory
inputDirectory = 'H:\My Drive\SSV'

# Folder where reference data files are stored (after recieving data from API)
ref_folder = inputDirectory + '\Jackson Reference Data' 
# Name of reference data file (created as output from AirNow API call in first program section)
ref_file = '\San Jose Jackson St 2024-01-21_to_2024-05-15_HourAverage_from_AirNowAPI.csv'

# Folder where sensor data is stored (after recieving data from API)
bp_folder = inputDirectory + '\BackpAQ_Data' 
bp_filename = '\All BackpAQ Data from_2024-01-21_to_2024-05-15from_API.csv'

# Folder where output dataframes, plots, metrics are stored
save_directory = inputDirectory + '\Colocation Assessment Outputs' 

# General sensor name (to use in file naming later on)
gen_sensor= 'BackpAQ'

# Time range for colocation evaluation (to use in file naming later on)
start_date = '2024-01-21 00:00:00'
end_date = '2024-05-15 00:00:00'

# Hourly offsets from UTC
# NOTE for YAQA Project: data from 'BackpAQ and AirNow API Data Call' python program is all in PST
ref_hr_offset = timedelta(hours=0)
#sensor_hr_offset = timedelta(hours=0)
sensor_hr_offset = timedelta(hours=0, minutes=45) #*** Add for time offset in AQ34

# Percent completeness for hourly/daily averages
custom_perct = 0.75



#%% Reference data - loading and formatting dataframe

#Load in hourly reference data to form dataframe
ref_df_hr = pd.read_csv(ref_folder + ref_file)

# Grab name of reference site to make Site column
ref_site = ref_df_hr.columns[1] 

# Add site name column
ref_df_hr['Site'] = ref_site

# Rename reference data columns to match sensor column names (to support merging dataframes later)
ref_df_hr = ref_df_hr.rename(columns = {ref_site:'PM2.5'}) #rename columns to be uniform with sensor data (helps merging later)

# Apply time format and offset
ref_df_hr['Datetime(PST)'] = pd.to_datetime(ref_df_hr['Datetime(PST)'])
ref_df_hr['Datetime(PST)'] = ref_df_hr['Datetime(PST)'] - ref_hr_offset


#%% Sensor data - loading and formatting dataframe

sensor_df_raw = pd.read_csv(bp_folder + bp_filename)

# Apply time format and offset
sensor_df_raw['Datetime(PST)'] = pd.to_datetime(sensor_df_raw['Datetime(PST)'])
sensor_df_raw['Datetime(PST)'] = sensor_df_raw['Datetime(PST)'] - sensor_hr_offset

# List of sensors to evaluate data for (taken from raw sensor files)
sensor_list = sensor_df_raw['Site'].unique().tolist()

# Compute sensor raw data frequency (used below to know how many data points per hour to expect)
sensor_freq = sensor_df_raw[sensor_df_raw['Site']==sensor_list[0]]['Datetime(PST)'].diff().mode()[0]

# Specify hourly and daily completeness
sensor_hour_comp = custom_perct * (timedelta(minutes=60)/sensor_freq)
day_comp = custom_perct * 24

#%% Sensor data - computing hourly and daily completeness

# Hourly averaging and completeness
sensor_df_raw = sensor_df_raw.set_index('Datetime(PST)')
sensor_hr_count = sensor_df_raw.groupby('Site').resample('1h')['PM2.5'].count().reset_index()
sensor_hr_mean = sensor_df_raw.groupby('Site').resample('1h')['PM2.5'].mean().reset_index()
sensor_hr_count = sensor_hr_count.rename(columns = {'PM2.5':'Hr_Count'})
sensor_df_hr = pd.concat([sensor_hr_mean,sensor_hr_count['Hr_Count']],axis=1)
sensor_df_hr['PM2.5'] = np.where(sensor_df_hr['Hr_Count']>=sensor_hour_comp,sensor_df_hr['PM2.5'],np.nan)

# Apply calibration y = 0.83x + 3.78 ### added AWS 1/4/2023
sensor_df_hr['PM2.5'] = 0.83*sensor_df_hr['PM2.5'] + 3.78

# Pivot table for joining with ref data later
sensor_tbl_hr = sensor_df_hr.pivot(index = 'Datetime(PST)',columns ='Site',values='PM2.5')

# Daily averaging and completeness
sensor_df_hr = sensor_df_hr.set_index('Datetime(PST)')
sensor_day_count = sensor_df_hr.groupby('Site').resample('1d')['PM2.5'].count().reset_index()
sensor_day_mean = sensor_df_hr.groupby('Site').resample('1d')['PM2.5'].mean().reset_index()
sensor_day_count = sensor_day_count.rename(columns = {'PM2.5':'Day_Count'})
sensor_df_day = pd.concat([sensor_day_mean,sensor_day_count['Day_Count']],axis=1)
sensor_df_day['PM2.5'] = np.where(sensor_df_day['Day_Count']>=day_comp,sensor_df_day['PM2.5'],np.nan)

# Pivot table for joining with ref data later 
sensor_tbl_day = sensor_df_day.pivot(index = 'Datetime(PST)',columns ='Site',values='PM2.5')


#%% Reference dataframe - computing daily completeness

# Pivot table for joining with sensor data later 
ref_tbl_hr = ref_df_hr.pivot(index = 'Datetime(PST)',columns ='Site',values='PM2.5')

# Daily averaging and completeness
ref_df_hr = ref_df_hr.set_index('Datetime(PST)')
ref_day_count = ref_df_hr.groupby('Site').resample('1d')['PM2.5'].count().reset_index()
ref_day_mean = ref_df_hr.groupby('Site').resample('1d')['PM2.5'].mean().reset_index()
ref_day_count = ref_day_count.rename(columns = {'PM2.5':'Day_Count'})
ref_df_day = pd.concat([ref_day_mean,ref_day_count['Day_Count']],axis=1)
ref_df_day['PM2.5'] = np.where(ref_df_day['Day_Count']>=day_comp,ref_df_day['PM2.5'],np.nan)

# Pivot table for joining with sensor data later 
ref_tbl_day = ref_df_day.pivot(index = 'Datetime(PST)',columns ='Site',values='PM2.5')

#%% Merging Sensor and Reference Hourly and Daily Dataframes and Saving to save_directory

merged_df_hr = pd.merge(sensor_tbl_hr,ref_tbl_hr,on='Datetime(PST)')

merged_df_day = pd.merge(sensor_tbl_day,ref_tbl_day,on='Datetime(PST)')

merged_df_hr.to_csv(save_directory + 'Merged Hourly ' + gen_sensor +' and ' + ref_site + ' PM2.5 from ' + str(start_date[0:10] + ' to ' + end_date[0:10]) + '.csv')

merged_df_day.to_csv(save_directory + 'Merged Daily ' + gen_sensor +' and ' + ref_site + ' PM2.5 from ' + str(start_date[0:10] + ' to ' + end_date[0:10]) + '.csv')


#%% Correlation Plots

# Specify which avgeraging interval you want to compute performance metrics for (can have both Daily and Hourly, separated by comma)
avg_freq = ['Hourly'] #'Daily' 'Hourly'

# Function to plot a line from a slope and intercept
def abline(slope, intercept):
    """Plot a line from slope and intercept"""
    axes = plt.gca()
    x_vals = np.array(axes.get_xlim())
    y_vals = intercept + slope * x_vals
    plt.plot(x_vals, y_vals, '--')

# Loop through averaging intervals for correlations     
for freq in avg_freq:

    if freq =='Hourly':
        
        colo_df_all = merged_df_hr
        colo_metrics_compute = 0
        
        # Specify the minimum and maximum concentrations for the correlation axes
        minp = -0.75
        maxp = 60
    
    elif freq == 'Daily':
        
        colo_df_all = merged_df_day
        
        # Initiate table of colocation metrics
        colo_metrics_compute = 1 # allows for colocation metric computation later on
        colo_metrics_tbl = pd.DataFrame()

        # Specify the minimum and maximum concentrations for the correlation axes
        minp = -0.75
        maxp = 15
        
    for sensor in sensor_list:
        
        # Work with only set of sensor's data at a time for correlation
        colo_df = colo_df_all[[sensor,ref_site]]
    
        colo_df = colo_df.dropna(how='any').reset_index()

        fig, ax = plt.subplots(figsize=(7, 7),dpi=200)
    
        #----Create the scatterplot----#
        
        x=colo_df[sensor]
        y=colo_df[ref_site]
        
        ax.set(xlim=(minp, maxp), ylim=(minp, maxp))
    
        if len(x)>0:
            corr = np.corrcoef(x, y)[0, 1]
        
            #sns.regplot(x=ref, y=sensor, data=df3,ci=None)
        
            sns.scatterplot(x=sensor, y=ref_site, data=colo_df)
        
            # Fit a regression line to the data
            slope, intercept = np.polyfit(x, y, 1)
        
            # Add the regression equation to the plot
            plt.text(0.5, 0.05, 'y = {:.2f}x + {:.2f}    R2 ={:.2f}  '.format(slope, intercept,corr*corr),
                 ha='center', va='center', transform=plt.gca().transAxes)
            
            # Add line of best to plot
            abline(slope, intercept)
        
            
            # Label and title plot
            plt.title(freq + r' PM$_{2.5}$ Comparison of ' + sensor + ' vs. ' + ref_site)
            plt.xlabel(sensor + r' (ug/m$^{3}$)')
            plt.ylabel(ref_site + r' (ug/m$^{3}$)')
            plt.show()
            
            # Save out correlation plots as images
            plt.savefig(save_directory + freq +  ' PM2.5 Comparison of ' + sensor + ' vs. ' + ref_site + '.png')
            
            #----Compute Performance Metrics----# 
            #(only for Daily avg freq)
            # Append important performance and dataset metrics to colo_metrics_tbl for each sensor (only if averaging freq = Daily)
            #(all values are rounded to two decimal places)
            if colo_metrics_compute == 1:
                rmse = round(math.sqrt(sum((x-y)**2) / len(x)),2) #root mean square error
                nrmse = round(((rmse/y.mean()) * 100),2) #normalized root mean square error, computed as %
                colo_metrics_tbl = pd.concat([colo_metrics_tbl,pd.DataFrame([{'Sensor':sensor,'Slope':slope,'Offset (μg/m3)':intercept,'R^2':round(corr*corr,2),'RMSE (μg/m3)':rmse,'NRMSE (%)':nrmse,'Min_Sensor_Conc':round(min(x),2),'Max_Sensor_Conc':round(max(x),2),'Min_Ref_Conc':round(min(y),2),'Max_Ref_Conc':round(max(y),2),'N':len(x)}])],ignore_index=True)

# If the colocation metrics table exists, save it
if 'colo_metrics_tbl' in locals():           
    # Add EPA Performance Metrics for comparison to colocation metric table
    colo_metrics_tbl = pd.concat([colo_metrics_tbl,pd.DataFrame([{'Sensor':'EPA Performance Targets','Slope':'1.0 +/- 0.35','Offset (μg/m3)':'-5 ≤ b ≤ 5','R^2':'≥ 0.70','RMSE (μg/m3)':'≤ 7','NRMSE (%)':'≤ 30','Min_Sensor_Conc':np.nan,'Max_Sensor_Conc':np.nan,'Min_Ref_Conc':np.nan,'Max_Ref_Conc':np.nan,'N':np.nan}])],ignore_index=True)

    # Save out colocation metrics to excel
    colo_metrics_tbl.to_excel(save_directory + 'Sensor Performance Metrics for ' + gen_sensor + ' ' + ref_site + ' Colocation.xlsx',index=False)
            
#%% Time Series Plots - both sensor and reference data

# Specify which avgeraging interval for time series visualizations (can have both Daily and Hourly, separated by comma)
avg_freq_plot = ['Hourly','Daily']

# Loop through averaging intervals     
for freq in avg_freq_plot:

    if freq =='Hourly':
        
        plot_df_all = merged_df_hr
        cols = plot_df_all.columns.tolist()
        cols.insert(0,cols.pop(cols.index('San Jose - Jackson St.')))
        plot_df_all = plot_df_all.reindex(columns = cols)
    
    elif freq == 'Daily':
        
        plot_df_all = merged_df_day
        cols = plot_df_all.columns.tolist()
        cols.insert(0,cols.pop(cols.index('San Jose - Jackson St.')))
        plot_df_all = plot_df_all.reindex(columns = cols)
    
    # Create timeseries plot
    fig, ax = plt.subplots(figsize=(10, 6),dpi=200)
     
    # Loop through columns of merged dataframe (sensor and reference data)
    for c in plot_df_all.columns:
        
        plt.plot(plot_df_all.index,plot_df_all[c],label=c)

    plt.title(freq + r' PM$_{2.5}$ Colocation')
    plt.xlabel('Datetime')
    plt.ylabel(r' PM$_{2.5}$ (ug/m$^{3}$)')
    plt.legend()
    plt.show()
    
    # Save out timeseries as image
    plt.savefig(save_directory + freq + ' PM2.5 Timeseries of ' + gen_sensor + ' and ' + ref_site + '.png')
    
    
    
    
