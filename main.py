from pathlib import Path
import os
import pandas as pd
from datetime import datetime
from datetime import timedelta
import lxml
import html5lib
from bs4 import BeautifulSoup
import numpy as np
from functools import reduce
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import selenium
from selenium.webdriver.support.ui import WebDriverWait
import time
import pyautogui
from stdiomask import getpass
 
pd.option_context('display.max_rows', None, 'display.max_columns', None)  # more options can be specified also
pd.options.display.max_colwidth = 199
pd.options.display.max_columns = 1000
pd.options.display.width = 1000
pd.options.display.precision = 2  # as needed

password = getpass(mask='*')

on_laptop = True


if on_laptop == True:
    #paths for building the file
    provisioned_users_df = pd.read_csv('C:/Users/Ethan/OneDrive/TigerConnect_MPaCC/tc_support_files/provisioned_users.csv')
    linked_roles_df = pd.read_excel('C:/Users/Ethan/OneDrive/TigerConnect_MPaCC/tc_support_files/roles_tokens_by_unit.xlsx')
    units_directory = 'C:/Users/Ethan/OneDrive/TigerConnect_MPaCC/test_folder'
    lawson_out_file = 'C:/Users/Ethan/OneDrive/TigerConnect_MPaCC/tc_support_files/lawson_out.csv'
    lawson_out_file2 = 'C:/Users/Ethan/OneDrive/TigerConnect_MPaCC/tc_support_files/lawson_out2.csv'
    main_converted_path = 'C:/Users/Ethan/OneDrive/TigerConnect_MPaCC/tc_support_files/main_converted.csv'
    final_out_path= 'C:/Users/Ethan/OneDrive/TigerConnect_MPaCC/tc_support_files/final_compiled_schedule.csv'    
    #paths for the upload function
    upload_path = 'C:\\Users\Ethan\OneDrive\TigerConnect_MPaCC'
    upload_subdir = 'tc_support_files'
    upload_file = 'final_compiled_schedule.csv'

else:
    lawson_path = 'K:/ClinicalAdvisoryTeam/test_folder/4 South/feb_mar_2020.htm'
    lawson_out_file = 'K:/ClinicalAdvisoryTeam/test_folder/4 South/lawson_out.csv'


x = 0
i = 1

def convert_lawson_to_tc(file_path):   
    main_converted_df = pd.read_csv(main_converted_path)
    global x
    if x == 0:
        main_converted_df = main_converted_df.iloc[0:0]
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
    searchfor = ['A4', 'A0', 'P1', 'A5']
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
    #add a column for the start times (how PSC codes shifts)
    lawson_stacked.loc[lawson_stacked['shift_code'] == 'P2', 'start_time'] = '18:30:00'
    lawson_stacked.loc[lawson_stacked['shift_code'] == 'A5', 'start_time'] = '06:30:00'
    #add a column for end times (how PSC codes shifts)
    lawson_stacked.loc[lawson_stacked['shift_code'] == 'P2', 'end_time'] = '06:30:00'
    lawson_stacked.loc[lawson_stacked['shift_code'] == 'A5', 'end_time'] = '18:30:00'
    #add a column for the start times
    lawson_stacked.loc[lawson_stacked['shift_code'] == 'A0', 'start_time'] = '18:30:00'
    lawson_stacked.loc[lawson_stacked['shift_code'] == 'A4', 'start_time'] = '06:30:00'
    #add a column for end times
    lawson_stacked.loc[lawson_stacked['shift_code'] == 'A0', 'end_time'] = '06:30:00'
    lawson_stacked.loc[lawson_stacked['shift_code'] == 'A4', 'end_time'] = '18:30:00'
    #establish the year
    this_year = datetime.now().year
    #add a column for the year
    lawson_stacked['year_sched'] = this_year
    #split the month/day into separate columns
    lawson_stacked[['month_sched','day_sched']] = lawson_stacked['date'].str.split('/', expand=True)
    # drop 'NaN' rows
    lawson_stacked = lawson_stacked.dropna()  
    # add the unit to the dataframe
    lawson_stacked['unit'] = folder
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
        elif row == 'P2':
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
    lawson_for_schedule = lawson[['unit','username','stime', 'etime']] 

    # write the file
    lawson_for_schedule.to_csv(lawson_out_file, index=False)
    main_converted_df = lawson_for_schedule.append(main_converted_df, sort=True)
    main_converted_df = main_converted_df[['unit', 'username', 'etime', 'stime']]
    main_converted_df = main_converted_df.drop_duplicates()
    main_converted_df.to_csv(main_converted_path, index=False)
    x=x+1

def merge_sources():
        main_converted_df = pd.read_csv(main_converted_path)
        tokens_plus_schedule = reduce(lambda x,y: pd.merge(x,y, on='unit', how='left'), [main_converted_df, linked_roles_df])
        tokens_plus_schedule['Email'] = tokens_plus_schedule['username'] + '@salud.unm.edu' 
        tokens_plus_schedule = reduce(lambda x,y: pd.merge(x,y, on='Email', how='left'), [tokens_plus_schedule, provisioned_users_df])
        tokens_plus_schedule = tokens_plus_schedule.drop(columns=['username'])
        tokens_plus_schedule = tokens_plus_schedule.rename(columns={"Account Token": "user_token", "Username": "username", "Email": "user_email",                                                                "Phone(s)": "user_phone", "token": "role_token" })
        tokens_plus_schedule = tokens_plus_schedule[['user_token', 'username', 'user_email', 'user_phone', 'role_token', 'stime', 'etime']]
        tokens_plus_schedule.to_csv(final_out_path, index=False)

def drive_tc_upload():
        driver = webdriver.Chrome()
        driver.get("https://login.tigerconnect.com/app/messenger/index.html?_ga=2.103280259.2040127355.1581561402-2100901986.1581561402")
        driver.maximize_window()


        time.sleep(5)
        driver.find_element_by_xpath(".//*[@name='username']").send_keys('ejmooney@salud.unm.edu')

        continue_button = driver.find_element_by_xpath(".//*[@id='tc-SignInForm__UsernameForm']/form/div[3]")
        continue_button.click()
        time.sleep(7)

        driver.find_element_by_xpath(".//*[@id='tc-SignInForm__PasswordForm']/form/div[2]/div/input").send_keys(password)
        continue_button = driver.find_element_by_xpath(".//*[@id='tc-SignInForm__PasswordForm']/form/div[3]/button")
        continue_button.click()
        time.sleep(15)
            
        roles_button = driver.find_element_by_xpath(".//*[@id='app']/div/div[1]/div/div[2]/div/div[1]")
        roles_button.click()
        time.sleep(10)

        upload_cal_button = driver.find_element_by_xpath(".//*[@id='app']/div/div[2]/div[1]/div[1]/div/div/div[2]/div[2]")
        upload_cal_button.click()
        time.sleep(5)

        upload_tool = driver.find_element_by_xpath("./html/body/div[2]/div/div/ul/li[1]")
        upload_tool.click()
        time.sleep(3)
            
        pyautogui.moveTo(1300,850)
        pyautogui.click()
        time.sleep(2)
        pyautogui.typewrite(upload_path)
        pyautogui.press('enter')
        time.sleep(2)
        pyautogui.typewrite(upload_subdir)
        pyautogui.press('enter')
        time.sleep(2)
        pyautogui.typewrite(upload_file)
        pyautogui.press('enter')
        time.sleep(15)
        pyautogui.press('enter')
        pyautogui.moveTo(1300,950)   
        pyautogui.click()
       
        time.sleep(300)
        driver.close()

while True:
    for folder in os.listdir(units_directory):
        for file in os.listdir(units_directory +'/'+ folder):
            lawson_path = units_directory + '/' + folder + '/' + file
            unit_name = folder
            convert_lawson_to_tc(lawson_path)
            print('Completed: ' + unit_name) 
        
    merge_sources()
    y=str(i)
    drive_tc_upload()
    print('round: ' + y)
    i = i+1
    time.sleep(240)
