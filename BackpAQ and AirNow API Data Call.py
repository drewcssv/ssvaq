#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 12 13:20:20 2023

This program calls both the BackpAQ and AirNow API's, retrieves raw BackpAQ data and hourly AirNow data, and saves
the dataframes into their respective csvs and folders

Output Files: Raw BackpAQ PM2.5 colocation data from thingspeak API (csv), Hourly Jackson St PM2.5 colocation data from AirNow API (csv)

@author: TDEnviro
"""     
# Required libraries
import pandas as pd
import datetime as dt
from time import sleep
import urllib
import json
import requests
import io
import numpy as np


# Specify output directory to save BackpAQ and AirNow data

bp_outputDirectory = 'H:\My Drive\SSV\BackpAQ_Data'
#'/Users/helenapliszka/Library/CloudStorage/GoogleDrive-helena.pliszka@tdenviro.com/.shortcut-targets-by-id/14GzzYFbnfKLJyNmJ9Kr8Ln3TagvuUsp_/Company Files/TDE-PROJECTS/SSV - YAQA/Work/BackpAQ Colocation Assessment/BackpAQ_data/'
airnow_outputDirectory = 'H:\My Drive\SSV\Jackson Reference Data'
#'/Users/helenapliszka/Library/CloudStorage/GoogleDrive-helena.pliszka@tdenviro.com/.shortcut-targets-by-id/14GzzYFbnfKLJyNmJ9Kr8Ln3TagvuUsp_/Company Files/TDE-PROJECTS/SSV - YAQA/Work/BackpAQ Colocation Assessment/Jackson_ref_data/'

#%% User Settings : BackpAQ API Data call 

# Specify the start and end date for the data period of interest
startDate = "2024-01-21 23:59:59"
endDate = "2024-05-15 23:59:59"

# Specify the differecnce (in minutes) between LST and UTC (e.g. For PST, 8 hours behind, which is 480 minutes)
tzoneOffset = dt.timedelta(minutes=480) #PST (8 hours behind UTC)


# Define device channel number and API key associated with each BackpAQ from Thingspeak
channel_dict = {'BackpAQ29':1863185, 'BackpAQ34':2015884}
api_key_dict = {'BackpAQ29':'491LPCUC72TG1RAK','BackpAQ34':'3PBAGTC41HU0JO8N'}



#%% BackpAQ API Data Call runs


# Device channel number and API key information is merged to one dataframe for access later
channel_df = pd.DataFrame(list(channel_dict.items()), columns=['Name', 'Channel'])
api_key_df = pd.DataFrame(list(api_key_dict.items()), columns=['Name', 'API Key'])
sensor_access_df = pd.merge(channel_df, api_key_df, on='Name')

# Column names for desired BackpAQ data (without 'entry_id')
columnNames =  ['Datetime(UTC)','PM1.0','PM2.5','PM10','Temp (F)','RelHum (%)','Lat','Lon','CO2']

# Create date objects in UTC for looping through days and to determine the number of weeks
# Data from API is in UTC so need to adjust start and end date by time difference
sdate_obj = dt.datetime.strptime(startDate[0:10] + ' ' + startDate[11:19], '%Y-%m-%d %H:%M:%S') + tzoneOffset
edate_obj = dt.datetime.strptime(endDate[0:10] + ' ' + endDate[11:19], '%Y-%m-%d %H:%M:%S') + tzoneOffset

# Create date objects for looping through days and to determine the number of weeks
delta = edate_obj - sdate_obj 
weeks = int(delta.days/7) + 1 #adding additional day for looping through weeks later
days = delta.days + 1
 
# Create a blank dataframe to merge BackpAQ data from each week into
bpStorage = pd.DataFrame(columns=columnNames)
    
# Loop through all the devices in sensor_access_df(rows)
for index, p in sensor_access_df.iterrows():

    # Get Thingspeak information (name, channel ID, API key)
    siteName = p['Name']
    thingspeakID = p['Channel']
    thingspeakKey = p['API Key']
    
    print (' Site: ' + siteName)
    
    # Looping through day periods (to not overload API)
    for dy in range (0,days):   

        sDateDay = sdate_obj + dt.timedelta(days=dy)
        eDateDay = sdate_obj + dt.timedelta(days=dy) + dt.timedelta(hours=23, minutes=59, seconds=59)
      
        
        # Create date objects for the API call (Note: format "yyyy-mm-dd%20hh:mm:ss" is needed for accessing the Thingspeak API)
        sdate = str(sDateDay)[0:10] + '%20' + str(sDateDay)[11:22]
        edate = str(eDateDay)[0:10] + '%20' + str(eDateDay)[11:22]
        
        print('Start Date ' + sdate)
        print('End Date ' + edate)
        
        # Create API url call
        urlCall = "http://api.thingspeak.com/channels/" + str(thingspeakID) + "/feeds.json?" + "api_key=" + thingspeakKey + "&start=" + sdate + "&end=" + edate 
        print(urlCall)
        
        # Request data from API through url call
        with urllib.request.urlopen(urlCall) as url:
            
            # Load in json data and decode
            bpData = json.loads(url.read().decode())
            
            # BackpAQ data from API is outputed as a dictionary that contains both 'channels' information and associated results in 'feeds'
            # Load the results ('feeds') of the API call into a dataframe
            bp_df = pd.DataFrame(data = bpData['feeds'])
             
            # If there is data present, proceed
            if not bp_df.empty:
                
                # Drop any columns that are not needed
                bp_df.drop(['entry_id'], axis=1, inplace=True)
                
                # Rename columns to pollutant names
                bp_df.columns = columnNames
                
                # Add site name to dataframe to differentiate between BackpAQs
                bp_df['Site'] = siteName

                # Append current dataframe (bp_df) to bpStorage
                bpStorage = pd.concat([bpStorage, bp_df], ignore_index=True)

                #Sleep for 2 seconds so as not to over tax the API
                sleep(2) # Time in seconds
    
# Convert the full BackpAQ dataset LST, drop the UTC column and reorder columns
bpStorage['Datetime(PST)'] = pd.to_datetime(bpStorage['Datetime(UTC)']) - tzoneOffset   
bpStorage['Datetime(PST)'] = bpStorage['Datetime(PST)'].dt.tz_localize(None) #remove timezone identifier in format
cols = bpStorage.columns.tolist()
cols.insert(0,cols.pop(cols.index('Datetime(PST)')))
bpStorage = bpStorage.reindex(columns = cols)
bpStorage = bpStorage.drop('Datetime(UTC)',axis=1)   

# Save out the full BackpAQ dataset
bpStorage.to_csv(bp_outputDirectory + '\All BackpAQ Data from_' + startDate[0:10] + '_to_' + endDate[0:10] + 'from_API.csv',index=False)


# Supporting Information for BackpAQ API call:

# Channels: This is the format sensor information will come in from the API:
# {'id': 2015884,
#  'name': 'BackpAQ Data 1',
#  'latitude': '0.0',
#  'longitude': '0.0',
#  'field1': 'PM1.0 µg/m³',
#  'field2': 'PM2.5 µg/m³',
#  'field3': 'PM10 µg/m³',
#  'field4': 'Temperature (Deg F)',
#  'field5': 'Humidity (Relative %)',
#  'field6': 'Latitude (deg)',
#  'field7': 'Longitude (deg)',
#  'field8': 'CO2 ppm',
#  'created_at': '2023-01-24T19:55:03Z',
#  'updated_at': '2023-01-26T05:57:38Z',
#  'last_entry_id': 224658}

# Feeds: This is the format that data will come in from the API:
# 'created_at': '2023-10-16T02:21:07Z',
#  'entry_id': 114012,
#  'field1': '1',
#  'field2': '1',
#  'field3': '1',
#  'field4': '60.96598',
#  'field5': '79.45557',
#  'field6': '37.87536',
#  'field7': '-122.54143',
#  'field8': '465'


#%% USER SETTINGS: AirNow API call for Hourly San Jose Jackson St Reference

# Monitoring Site Name (used for file saving)
a_site_name = '\San Jose Jackson St'

# Specify Geographic Bounds for API call (to get data from one monitor, restrict bounds to around that monitor only)
LatN = 37.349
LatS = 37.347
LonW = -121.896
LonE = -121.893

# Specify Dates  (Note: format "yyyy-mm-dd hh:mm:ss" and time is in Pacific Standard Time (PST or LST))
#startDate = "2023-10-21 23:59:59"
#endDate = "2024-03-31 23:59:59"

# Specify timezone offset from UTC to LST (e.g. For PST, 8 hours behind, which is 480 minutes)
tzoneOffset = dt.timedelta(minutes=480)   

# Specify parameter of interest (in AirNow API format)
parameters = "PM25"

# Specify AirNow API key
apiKey = 'FE17E81D-0969-49C9-941A-3258BBB97052'

#%% AirNow API call for Hourly San Jose Jackson St Reference runs..

# Create date objects that are in UTC for the API call
sdateObj = dt.datetime.strptime(startDate[0:10] + ' '+ startDate[11:19], '%Y-%m-%d %H:%M:%S') + tzoneOffset
edateObj = dt.datetime.strptime(endDate[0:10] + ' '+ endDate[11:19], '%Y-%m-%d %H:%M:%S') + tzoneOffset

# Create date objects for looping through days and to determine the number of weeks
delta = edateObj - sdateObj
weeks = int(delta.days/7) + 1 #adding additional week to catch all available data

# Column names for parameters of interest (order matters)
columnNames = ["lat","lon","datetime(UTC)","param","units","conc","poc","site","aqsCode"]

# Create a blank dataframe to merge data from each week into
anStorage = pd.DataFrame(columns=columnNames)

# Loop through week periods (to not overload API)
for wk in range (0,weeks):
    sDateWeek = sdateObj + dt.timedelta(weeks=wk)
    eDateWeek = sdateObj + dt.timedelta(weeks=wk) + dt.timedelta(days=6, hours=23, minutes=59, seconds=59)
        
    # Create date objects for the API call (Note: format "yyyy-mm-ddThh:mm:ss" is needed for accessing the Thingspeak API)
    sdate = str(sDateWeek)[0:10] + 'T' + str(sDateWeek)[11:13]
    edate = str(eDateWeek)[0:10] + 'T' + str(eDateWeek)[11:13]
    
    print(sdate)
    print(edate)

    # Generate a API call, make request, replacing missing values with NaN
    urlCall = "http://www.airnowapi.org/aq/data/?startDate=" + sdate + "&endDate=" + edate + "&parameters=" + parameters + "&BBOX=" + str(LonW) + ',' + str(LatS) + ',' + str(LonE) + ',' + str(LatN) + "&dataType=B&format=text/csv&verbose=1&nowcastonly=0&includerawconcentrations=1&API_KEY=" + apiKey
    print(urlCall)
    
    # Specify column names for incoming data
    csvColumns = ['lat','lon','datetime(UTC)','param','midpoint','units','conc','AQI','poc','site','agency','aqsCode','airnowCode']
    
    r = requests.post(urlCall)
    if r.ok:
        
        print("getting data for " + sdate)
        data = r.content.decode('utf8')
        an = pd.read_csv(io.StringIO(data),header=None, names=csvColumns)
      
        # Drop unnecessary data
        an.drop(['midpoint', 'AQI', 'agency', 'airnowCode'], axis=1, inplace=True)
        
        # Replace instances of -999 with NaN
        an['conc'].replace(-999,np.nan,inplace=True)
        
        # Append current dataframe (an) into anStorage
        anStorage = pd.concat([anStorage,an],ignore_index=True)

        
# Pivot ouput to be datetime rows with sites as columns
an1Hr = pd.pivot_table(anStorage, values='conc', index=['datetime(UTC)'], columns=['site']).reset_index()

# Convert datetime and create a LST time and re-order the columns
an1Hr['Datetime(PST)'] = pd.to_datetime(an1Hr['datetime(UTC)']) - tzoneOffset
cols = an1Hr.columns.tolist()
cols.insert(0,cols.pop(cols.index('Datetime(PST)')))
an1Hr = an1Hr.reindex(columns = cols)
an1Hr.drop(['datetime(UTC)'], axis=1, inplace=True)


# Write all data to CSV file
filename = airnow_outputDirectory + a_site_name + ' ' + str(startDate[0:10] + '_to_' + endDate[0:10]) + "_HourAverage_from_AirNowAPI" +".csv"
an1Hr.to_csv(filename, float_format='%.2f',index=False)  
    
  






