from pathlib import Path
import os
import pandas as pd
from datetime import datetime
import lxml
import html5lib
from bs4 import BeautifulSoup
 
#from tabula import read_pdf
#from tabula import convert_into
#from tika import parser
 
pd.option_context('display.max_rows', None, 'display.max_columns', None)  # more options can be specified also
pd.options.display.max_colwidth = 199
pd.options.display.max_columns = 1000
pd.options.display.width = 1000
pd.options.display.precision = 2  # set as needed
 
lawson_path = 'K:/ClinicalAdvisoryTeam/test_folder/4 South/feb_march_2020.htm'
 
lawson_df = pd.read_html(lawson_path)
 
 
lawson_path2 = os.path.join('C:\\', 'Users', 'Ethan', 'OneDrive', 'Desktop', 'lawson_test.pdf')
tmpTxtPath = os.path.join('C:\\', 'Users', 'Ethan', 'OneDrive', 'Desktop', 'tmpTxt.txt')
tmpCSVPath = os.path.join('C:\\', 'Users', 'Ethan', 'OneDrive', 'Desktop', 'pdfToCSV.csv')
 
lawson_out_file = 'K:/ClinicalAdvisoryTeam/test_folder/4 South/lawson_out.csv'
 
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
 
 
####*************** seems good up to here *****************##########
 
 
## remove rows for floor shifts (A1 is day, P1 is nights) this can happen with releifs and sups working floor shifts
#lawson_stacked = lawson_stacked[lawson_stacked.shift_code != 'P1']
#lawson_stacked = lawson_stacked[lawson_stacked.shift_code != 'A1']
 
## get rid of the '/r' that appears in the conversion from pdf with long naes
#lawson_stacked['name'] = lawson_stacked['name'].str.replace('\r', ' ')
 
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
######################################################################
''' Need to write some logic to address schedules at the end of the year, something like if current month 
is Nov or Dec,then current year = year +1 '''
######################################################################
 
#lawson_stacked = lawson_stacked[lawson_stacked.date != 'Staff ID']
 
 
#split the month/day into separate columns
lawson_stacked[['month_sched','day_sched']] = lawson_stacked['date'].str.split('/', expand=True)
# this is a rediculous solution to make single digit months into 2 digit strings
lawson_stacked['zero_col'] = '0'
 
lawson_stacked = lawson_stacked.dropna()
 
 
lawson_stacked['cal_day'] = lawson_stacked['year_sched'].astype(str) +'-' + lawson_stacked['month_sched'].astype(str) + '-' + lawson_stacked['day_sched'].astype(str)
lawson_stacked['cal_day'] = pd.to_datetime(lawson_stacked['cal_day']).datetime64
 
lawson_stacked['day_plus'] = pd.Timestamp(lawson_stacked['cal_day']) + pd.DateOffset(days=1).strftime('%Y-%m-%d')
 
x = '2017-05-15'
# choose some combination of below methods
res = (pd.Timestamp(x) + pd.DateOffset(days=1)).strftime('%Y-%m-%d')
 
 
 
# use a mask to identify months that are one character
mask = lawson_stacked['month_sched'].str.len() == 1
# use the mask to change single character months to 2 character months
lawson_stacked.month_sched = lawson_stacked.month_sched.mask(mask, lawson_stacked['zero_col'] + lawson_stacked['month_sched'])
 
mask = lawson_stacked['day_sched'].str.len() == 1
lawson_stacked.day_sched = lawson_stacked.day_sched.mask(mask, lawson_stacked['zero_col'] + lawson_stacked['day_sched'])
 
 
# combine columns to get the stime and etime as specified in tiger connect sample file
lawson_stacked['stime'] = lawson_stacked['year_sched'].astype(str) + '-' + lawson_stacked['month_sched'].astype(str) + '-' + lawson_stacked['day_sched'].astype(str) + 'T' + lawson_stacked['start_time'].astype(str) + 'Z'
lawson_stacked['etime'] = lawson_stacked['year_sched'].astype(str) + '-' + lawson_stacked['month_sched'].astype(str) + '-' + lawson_stacked['day_sched'].astype(str) + 'T' + lawson_stacked['end_time'].astype(str) + 'Z'
 
 
lawson_stacked = lawson_stacked.dropna()
 
 
# write the dataframe to a csv
lawson_stacked.to_csv(lawson_out_file)
 
lawson_stacked
 
