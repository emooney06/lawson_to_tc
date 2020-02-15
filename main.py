from pathlib import Path
import os
import pandas as pd
from datetime import datetime
from datetime import timedelta
import lxml
import html5lib
from bs4 import BeautifulSoup
import numpy as np
 
pd.option_context('display.max_rows', None, 'display.max_columns', None)  # more options can be specified also
pd.options.display.max_colwidth = 199
pd.options.display.max_columns = 1000
pd.options.display.width = 1000
pd.options.display.precision = 2  # set as needed
 
on_laptop = False

if on_laptop == True:
    lawson_path = 'C:/Users/Ethan/OneDrive/TigerConnect_MPaCC/test_folder/4_south/feb_march_2020.htm'
    lawson_out_file = 'C:/Users/Ethan/OneDrive/TigerConnect_MPaCC/test_folder/4_south/lawson_out.csv'
    lawson_out_file2 = 'C:/Users/Ethan/OneDrive/TigerConnect_MPaCC/test_folder/4_south/lawson_out2.csv'
else:
    lawson_path = 'K:/ClinicalAdvisoryTeam/test_folder/4 South/feb_mar_2020.htm'
    lawson_out_file = 'K:/ClinicalAdvisoryTeam/test_folder/4 South/lawson_out.csv'

# read the raw lawson scheduler HTML file to a list
lawson_df = pd.read_html(lawson_path)
# Convert the pandas list to a dataframe
lawson_df = lawson_df[0]
# write the dataframe to csv simply to re-load and drop the "unnamed columns" row
lawson_df.to_csv(lawson_out_file, index=False)
lawson_df = pd.read_csv(lawson_out_file, skiprows=1)
# limit the dataset to only nurses to avoid those scheduled for 'person at the desk' position
lawson_df = lawson_df.loc[(lawson_df['Staff Type *'] == "2. Professional")]
# A4 is day charge, A0 is night charge
searchfor = ['A4', 'A0']
#use the pipe | character to match each of the substrings in the words in the dataframe
lawson_df = lawson_df[lawson_df.apply(lambda r: r.str.contains('|'.join(searchfor), case=False).any(), axis=1)]
# Drop the unnamed columns
lawson_df = lawson_df[lawson_df.columns.drop(list(lawson_df.filter(regex='Unnamed')))]
# drop the team and staff type columns because they don't matter
limit_set = lawson_df.drop(columns=['Team *', 'Staff Type *'])
#set the 'name column as the index
limit_set = limit_set.set_index('Staff ID')
#transpose the data set to make each row a date
lawson_transposed = limit_set.transpose()
# Stack the dataframe to reshape it closer to target
lawson_stacked = lawson_transposed.stack()
# Write the dataframe to CSV to reset it into a flat dataframe without unstacking
lawson_stacked.to_csv(lawson_out_file, header=True)
# read the file into a dataframe
lawson_stacked = pd.read_csv(lawson_out_file, names=['date', 'Staff ID', 'shift_code'])
# Stack the columns to orient the dataframe with dates as rows instead of columns 
lawson_stacked = lawson_stacked[lawson_stacked.date != 'Staff ID']
# Truncate the first 3 characters of values in the 'Date' column because they are days of the week (mon, tues, wed, etc)
lawson_stacked['date'] = lawson_stacked['date'].str[3:]
#add a column for the start times
lawson_stacked.loc[lawson_stacked['shift_code'] == 'A0', 'start_time'] = '19:00:00'
lawson_stacked.loc[lawson_stacked['shift_code'] == 'A4', 'start_time'] = '07:00:00'
#add a column for end times
lawson_stacked.loc[lawson_stacked['shift_code'] == 'A0', 'end_time'] = '07:00:00'
lawson_stacked.loc[lawson_stacked['shift_code'] == 'A4', 'end_time'] = '19:00:00'
#establish the year
this_year = datetime.now().year
#add a column for the year
lawson_stacked['year_sched'] = this_year
#split the month/day into separate columns
lawson_stacked[['month_sched','day_sched']] = lawson_stacked['date'].str.split('/', expand=True)
# drop 'NaN' rows
lawson_stacked = lawson_stacked.dropna()  
# use a mask to identify months that are single character
mask = lawson_stacked['month_sched'].str.len() == 1
# replace single character months with the 2-char version (ie. 1:01, 2:02, etc)
lawson_stacked.month_sched = lawson_stacked.month_sched.mask(mask, '0' + lawson_stacked['month_sched'])
# use mask to identify days that are single characters 
mask = lawson_stacked['day_sched'].str.len() == 1
# replace single character days with the 2-char version (ie. 1:01, 2:02, etc)
lawson_stacked.day_sched = lawson_stacked.day_sched.mask(mask, '0' + lawson_stacked['day_sched'])
# create a 'calendar day" (cal_day) from multiple columns that can be converted to a datetime
lawson_stacked['cal_day'] = lawson_stacked['year_sched'].astype(str) +'-' + lawson_stacked['month_sched'].astype(str) + '-' + lawson_stacked['day_sched'].astype(str)
# convert the calnedar day (cal_day) column to a datetime object in the dataframe so a calendar day can be added
lawson_stacked['cal_day'] = pd.to_datetime(lawson_stacked['cal_day'], yearfirst=True)
# make lawson_stacked "lawson"... just because it's easier for me to type (and maybe it's not really stacked any more...)
lawson = lawson_stacked

# Create a list of 1s and 0s as integers to add to the cal_day column to get the shift end date
next_days = []
# loop through the shift code column to create the list of 0s for day shifts and 1s for night shifts 
for row in lawson['shift_code']:
    #if the shift code is A0, it's night shift and the shift will end on start date + 1 day
    if row == 'A0':
        next_days.append(1)
    else:
        # Else the shift is a day shift and will end on the same day it starts
        next_days.append(0)

# Add the list as a dataframe column so it can be added to the cal_day column 
lawson['next_day'] = next_days
# ceil the values in 'next_day' column as timedelta objects representing change of 1 day
temp = lawson['next_day'].apply(np.ceil).apply(lambda x: pd.Timedelta(x, unit='D'))
# add the timedelta objects to the cal_day column to get the shift end dates
lawson['shift_end'] = lawson['cal_day'] + temp
# combine columns to get the stime and etime as specified in tiger connect sample file
lawson['stime'] = lawson['cal_day'].astype(str) + 'T' + lawson['start_time'].astype(str) + 'Z'
lawson['etime'] = lawson['shift_end'].astype(str) + 'T' + lawson['end_time'].astype(str) + 'Z'
# change the staff ID column to username to meet the tiger connect specs
lawson = lawson.rename(columns={'Staff ID':'username'})
# reduce the dataframe to elements needed for the TigerConnect file
lawson_for_schedule = lawson[['username','stime', 'etime']] 
# write the file
lawson_for_schedule.to_csv(lawson_out_file, index=False)


