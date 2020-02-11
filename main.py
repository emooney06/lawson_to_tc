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
 
on_laptop = True

if on_laptop == True:
    lawson_path = 'C:/Users/Ethan/OneDrive/TigerConnect_MPaCC/test_folder/4_south/feb_march_2020.htm'
    lawson_out_file = 'C:/Users/Ethan/OneDrive/TigerConnect_MPaCC/test_folder/4_south/lawson_out.csv'
    lawson_out_file2 = 'C:/Users/Ethan/OneDrive/TigerConnect_MPaCC/test_folder/4_south/lawson_out2.csv'
else:
    lawson_path = 'K:/ClinicalAdvisoryTeam/test_folder/4 South/feb_march_2020.htm'
    lawson_out_file = 'K:/ClinicalAdvisoryTeam/test_folder/4 South/lawson_out.csv'

lawson_df = pd.read_html(lawson_path)
 
lawson_df = lawson_df[0]
 
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
limit_set = limit_set.set_index('Staff Name')
#transpose the data set to make each row a date
lawson_transposed = limit_set.transpose()
# Stack the dataframe to reshape it closer to target
lawson_stacked = lawson_transposed.stack()
# Write the dataframe to CSV to reset it into a flat dataframe without unstacking
lawson_stacked.to_csv(lawson_out_file, header=True)
# read the file into a dataframe
lawson_stacked = pd.read_csv(lawson_out_file, names=['date', 'name', 'shift_code'])
 
lawson_stacked = lawson_stacked[lawson_stacked.date != 'Staff ID']
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
 
lawson_stacked = lawson_stacked.dropna()
  
# use a mask to identify months that are one character
mask = lawson_stacked['month_sched'].str.len() == 1
lawson_stacked.month_sched = lawson_stacked.month_sched.mask(mask, '0' + lawson_stacked['month_sched'])
 
mask = lawson_stacked['day_sched'].str.len() == 1
lawson_stacked.day_sched = lawson_stacked.day_sched.mask(mask, '0' + lawson_stacked['day_sched'])



lawson_stacked['cal_day'] = lawson_stacked['year_sched'].astype(str) +'-' + lawson_stacked['month_sched'].astype(str) + '-' + lawson_stacked['day_sched'].astype(str)
lawson_stacked['cal_day'] = pd.to_datetime(lawson_stacked['cal_day'], yearfirst=True)

lawson_stacked.to_csv(lawson_out_file)
lawson = pd.read_csv(lawson_out_file)


# Create a list to store the data
next_days = []

# For each row in the column,
for row in lawson['shift_code']:
    # if more than a value,
    if row == 'A0':
        next_days.append(1)
    else:
        # Append a failing grade
        next_days.append(0)

# Create a column from the list
lawson['next_day'] = next_days
lawson['cal_day'] = pd.to_datetime(lawson['cal_day'])

temp = lawson['next_day'].apply(np.ceil).apply(lambda x: pd.Timedelta(x, unit='D'))

lawson['shift_end'] = lawson['cal_day'] + temp

lawson.to_csv(lawson_out_file)
 
# combine columns to get the stime and etime as specified in tiger connect sample file
lawson['stime'] = lawson['cal_day'].astype(str) + 'T' + lawson['start_time'].astype(str) + 'Z'
lawson['etime'] = lawson['shift_end'].astype(str) + 'T' + lawson['end_time'].astype(str) + 'Z'

lawson_for_schedule = lawson[['name','stime', 'etime']] 
lawson.to_csv(lawson_out_file)
 