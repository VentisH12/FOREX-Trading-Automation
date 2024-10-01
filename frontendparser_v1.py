# -*- coding: utf-8 -*-
"""FrontendParser_v1.ipynb

Author: Anand Cheruvu
Version: 1.3
"""

!pip install --upgrade 'notebook>=5.7.6'

from google.colab import drive
drive.mount('/content/drive')

!pip install --upgrade gspread oauth2client df2gspread

# import the necessary packages
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Function to remove empty key in the dictionary.
# Input: Dictionary with empty keys
# Output: Cleaned dictionary

def remove_empty_keys_from_dict(d):
    if type(d) is dict:
        return dict((k, remove_empty_keys_from_dict(v)) for k, v in d.items() if v and remove_empty_keys_from_dict(v))
    elif type(d) is list:
        return [remove_empty_from_dict(v) for v in d if v and remove_empty_keys_from_dict(v)]
    else:
        return d
# Function to open connect to Google Sheets via OAUTH credentials and authentication.
# Input: Google Sheet URL Link
# Output: Workbook

def open_spread_sheet(sheet_url):
    from google.colab import auth
    auth.authenticate_user()
    import gspread
    from gspread_dataframe import get_as_dataframe, set_with_dataframe
    from oauth2client.client import GoogleCredentials
    gc = gspread.authorize(GoogleCredentials.get_application_default())

    scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
    #credentials = ServiceAccountCredentials.from_json_keyfile_name('/content/drive/My Drive/Forex2/gsheetparser-288520-3fd0612e50ed.json', scope)
    #gc = gspread.authorize(credentials)
    wb = gc.open_by_url(sheet_url)

    return wb

# Function to read the data from the opened google sheet.
# Input(s): Workbook and sheet name
# Output: data dictionary

def get_input_data_from_work_book(wb,sheet_name):
  currentSheet = wb.worksheet(sheet_name)
  #all_sheet_data = currentSheet.get_all_records() #use this to get all the data from the spreadsheet
  #print("ALL SHEET DATA - ",all_sheet_data)
  config_data = currentSheet.get('A1:C3') # get the config data only, returns list of lists
  config_dict = extract_config_section_data_from_sheet(config_data) # TODO: check for return data
  #print("config Data = ",config_data)

  account_info_dict = extract_account_input_section_data(currentSheet)
  #print("IN GET_INPUT_DATA_FROM...:acct_dict = ",account_info_dict)

  #stop_loss_manager_dict = extract_Stop_Loss_Manager_input_section_data(currentSheet,)
  #print("IN GET_INPUT_DATA_FROM...:SLM_dict = ",stop_loss_manager_dict)
  #print("SHEET DATA: ",sheet_data)
  #prepare_output_dictionary(output_range_data)

  master_frontend_input_dict.update(config_dict)
  master_frontend_input_dict.update(account_info_dict)
  return master_frontend_input_dict

# Function to extract the SLM information.
# Input: current sheet
# Output: multiple lists

def extract_Stop_Loss_Manager_input_section_data(currentSheet):
  #print("IN SLM method")

  # Stop Loss Manager details below
  new_slm_is_on_list=[]
  #is_SLM_On = False
  new_Take_Profit_is_on_list=[]
  new_Take_Profit_value_list=[]
  new_Stop_Loss_is_on_list=[]
  new_Stop_Loss_value_list=[]
  new_Trailing_Stop_Loss_is_on_list=[]
  new_Trailing_Stop_Loss_value_list=[]
  new_Move_Stop_Loss_is_on_list=[]
  new_Move_Stop_Loss_value_1_list=[]
  new_Move_Stop_Loss_value_2_list=[]
  new_Initiate_Trailing_Stop_at_is_on_list=[]
  new_Initiate_Trailing_Stop_at_value_1_list=[]
  new_Initiate_Trailing_Stop_at_value_2_list=[]

  slm_list = currentSheet.row_values(13)
  #print("SLM raw List = ",slm_list)

  if slm_list[0] == "Stop Loss Manager":
    slm_list = list(filter(None, slm_list)) #filter out empty strings
    #print(" SLM Cleaned LIST = ",slm_list)
  slm_list_length = len(slm_list)
  #print("SLM Length = ", slm_list_length,"SLM Range = ",range(slm_list_length))

  if slm_list[0] == "Stop Loss Manager":
    i = 1
    for i in range(slm_list_length):
      if slm_list[i] == "On":
        new_slm_is_on_list.insert(i,slm_list[i])
        #is_SLM_On = True
        #print("is_SLM_On=",is_SLM_On)
        #print("NEW SLM IS ON LIST = ",new_slm_is_on_list)

        # Take profit
        Take_Profit_list = currentSheet.row_values(14)
        Take_Profit_list_length = len(Take_Profit_list)

        if Take_Profit_list[0] == "Take Profit (Initial)":
          j = 1
          for j in range(Take_Profit_list_length):
            if Take_Profit_list[j] == "On":
              new_Take_Profit_is_on_list.insert(j,Take_Profit_list[j])
              new_Take_Profit_value_list.insert(j+1,Take_Profit_list[j+1])
            elif Take_Profit_list[j] == "Off":
              new_Take_Profit_is_on_list.insert(j,"Off")
              new_Take_Profit_value_list.insert(j+1,"0")
          #print("NEW Take Profit IS ON LIST = ",new_Take_Profit_is_on_list," NEW Take_Profit Value = ",new_Take_Profit_value_list)

        # Stop Loss
        Stop_Loss_list = currentSheet.row_values(15)
        Stop_Loss_list_length = len(Stop_Loss_list)

        if Stop_Loss_list[0] == "Stop Loss":
          k = 1
          for k in range(Stop_Loss_list_length):
           if Stop_Loss_list[k] == "On":
              new_Stop_Loss_is_on_list.insert(k,Stop_Loss_list[k])
              new_Stop_Loss_value_list.insert(k+1,Stop_Loss_list[k+1])
           elif Stop_Loss_list[k] == "Off":   #if the parameter is turned off, then capture it
              new_Stop_Loss_is_on_list.insert(k,"Off")
              new_Stop_Loss_value_list.insert(k+1,"0")
          #print("NEW Stop Loss IS ON LIST = ",new_Stop_Loss_is_on_list," NEW Stop Loss Value = ",new_Stop_Loss_value_list)

        # Trailing Stop Loss
        Trailing_Stop_Loss_list = currentSheet.row_values(16)
        Trailing_Stop_Loss_list_length = len(Trailing_Stop_Loss_list)

        if Trailing_Stop_Loss_list[0] == "Trailing Stop Loss":
          x = 1
          for x in range(Trailing_Stop_Loss_list_length):
            if Trailing_Stop_Loss_list[x] == "On":
              new_Trailing_Stop_Loss_is_on_list.insert(x,Trailing_Stop_Loss_list[x])
              new_Trailing_Stop_Loss_value_list.insert(x+1,Trailing_Stop_Loss_list[x+1])
            elif Trailing_Stop_Loss_list[x] == "Off":   #if the parameter is turned off, then capture it
              new_Trailing_Stop_Loss_is_on_list.insert(x,"Off")
              new_Trailing_Stop_Loss_value_list.insert(x+1,'0')
          #print("NEW Trailing Stop Loss IS ON LIST = ",new_Trailing_Stop_Loss_is_on_list," NEW Trailing Stop Loss Value = ",new_Trailing_Stop_Loss_value_list)

        # Move Stop Loss To
        Move_Stop_Loss_list = currentSheet.row_values(17)
        Move_Stop_Loss_list_length = len(Move_Stop_Loss_list)

        if Move_Stop_Loss_list[0] == "Move Stop Loss To":
         y = 1
         for y in range(Move_Stop_Loss_list_length):
          if Move_Stop_Loss_list[y] == "On":
            new_Move_Stop_Loss_is_on_list.insert(y,Move_Stop_Loss_list[y])
            new_Move_Stop_Loss_value_1_list.insert(y+1,Move_Stop_Loss_list[y+1])
            new_Move_Stop_Loss_value_2_list.insert(y+3,Move_Stop_Loss_list[y+3])
          elif Move_Stop_Loss_list[y] == "Off":
            new_Move_Stop_Loss_is_on_list.insert(y,"Off")
            new_Move_Stop_Loss_value_1_list.insert(y+1,"0")
            new_Move_Stop_Loss_value_2_list.insert(y+3,"0")
        #print("NEW Move Stop Loss IS ON LIST = ",new_Move_Stop_Loss_is_on_list," NEW Move Stop Loss Value 1 = ",new_Move_Stop_Loss_value_1_list," NEW Move Stop Loss Value 2 = ",new_Move_Stop_Loss_value_2_list)

        # Initate Trailing Stop at
        Initiate_Trailing_Stop_at_list = currentSheet.row_values(18)
        Initiate_Trailing_Stop_at_list_length = len(Initiate_Trailing_Stop_at_list)

        if Initiate_Trailing_Stop_at_list[0] == "Initiate Trailing Stop at":
          z = 1
          for z in range(Initiate_Trailing_Stop_at_list_length):
            if Initiate_Trailing_Stop_at_list[z] == "On":
              new_Initiate_Trailing_Stop_at_is_on_list.insert(z,Initiate_Trailing_Stop_at_list[z])
              new_Initiate_Trailing_Stop_at_value_1_list.insert(z+1,Initiate_Trailing_Stop_at_list[z+1])
              new_Initiate_Trailing_Stop_at_value_2_list.insert(z+3,Initiate_Trailing_Stop_at_list[z+3])
            elif Initiate_Trailing_Stop_at_list[z] == "Off":
              new_Initiate_Trailing_Stop_at_is_on_list.insert(z,"Off")
              new_Initiate_Trailing_Stop_at_value_1_list.insert(z+1,"0")
              new_Initiate_Trailing_Stop_at_value_2_list.insert(z+3,"0")
        #print("NEW Initiate Trailing Stop at IS ON LIST = ",new_Initiate_Trailing_Stop_at_is_on_list," NEW Initiate Trailing Stop at Value 1 = ",new_Initiate_Trailing_Stop_at_value_1_list," NEW Initiate Trailing Stop at Value 2 = ",new_Initiate_Trailing_Stop_at_value_2_list)
        """
        new_slm_name=['Stop Loss Manager']
        new_SLM_nested_dict = dict(map(lambda SLM,
                                 Is_SLM_On,
                                 Is_TP_initial_On,
                                 TP_initial_value,
                                 Is_Stop_Loss_On,
                                 Stop_Loss_Value,
                                 Is_Trailing_SL_On,
                                 Trailing_SL_Value,
                                 Is_Move_SL_to_On,
                                 Move_Stop_Loss_Value_1,
                                 Move_Stop_Loss_Value_2,
                                 Is_Initiate_TS_at_On,
                                 Initiate_TS_at_Value_1,
                                 Initiate_TS_at_Value_2 :
                                 (SLM,
                                    {'Is_SLM_On':str(Is_SLM_On),
                                     'Is_Initial_Take_Profit_On':str(Is_TP_initial_On),
                                     'Initial_Take_Profit_Value':str(TP_initial_value),
                                     'Is_Stop_Loss_On':str(Is_Stop_Loss_On),
                                     'Stop_Loss_Value':str(Stop_Loss_Value),
                                     'Is_Trailing_SL_On':str(Is_Trailing_SL_On),
                                     'Trailing_Stop_Loss_Value':str(Trailing_SL_Value),
                                     'Is_Move_Stop_Loss_To_On':str(Is_Move_SL_to_On),
                                     'Move_Stop_Loss_Value_1':str(Move_Stop_Loss_Value_1),
                                     'Move_Stop_Loss_Value_2':str(Move_Stop_Loss_Value_2),
                                     'Is_Initiate_TS_at_On':str(Is_Initiate_TS_at_On),
                                     'Initiate_TS_at_Value_1':str(Initiate_TS_at_Value_1),
                                     'Initiate_TS_at_Value_2':str(Initiate_TS_at_Value_2)
                                    }),
                                    new_slm_name,
                                    new_slm_is_on_list,
                                    new_Take_Profit_is_on_list,
                                    new_Take_Profit_value_list,
                                    new_Stop_Loss_is_on_list,
                                    new_Stop_Loss_value_list,
                                    new_Trailing_Stop_Loss_is_on_list,
                                    new_Trailing_Stop_Loss_value_list,
                                    new_Move_Stop_Loss_is_on_list,
                                    new_Move_Stop_Loss_value_1_list,
                                    new_Move_Stop_Loss_value_2_list,
                                    new_Initiate_Trailing_Stop_at_is_on_list,
                                    new_Initiate_Trailing_Stop_at_value_1_list,
                                    new_Initiate_Trailing_Stop_at_value_2_list))

        #print("IN SLM METHOD, nested DICT = ",new_SLM_nested_dict) """

      elif slm_list[i] == "Off":
        #print("i = ",i)
        new_slm_is_on_list.insert(i,"Off")
        new_Take_Profit_is_on_list.insert(i,"Off")
        new_Take_Profit_value_list.insert(i,"0")
        new_Stop_Loss_is_on_list.insert(i,"Off")
        new_Stop_Loss_value_list.insert(i,"0")
        new_Trailing_Stop_Loss_is_on_list.insert(i,"Off")
        new_Trailing_Stop_Loss_value_list.insert(i,"0")
        new_Move_Stop_Loss_is_on_list.insert(i,"Off")
        new_Move_Stop_Loss_value_1_list.insert(i,"0")
        new_Move_Stop_Loss_value_2_list.insert(i,"0")
        new_Initiate_Trailing_Stop_at_is_on_list.insert(i,"Off")
        new_Initiate_Trailing_Stop_at_value_1_list.insert(i,"0")
        new_Initiate_Trailing_Stop_at_value_2_list.insert(i,"0")
        #is_SLM_On = False
        #print("is_SLM_On=",is_SLM_On)
      #else:
      #  if slm_list[i] == " ":
      #    print("Found empty string")
      #    i = i+1

  return new_slm_is_on_list, new_Take_Profit_is_on_list, new_Take_Profit_value_list, new_Stop_Loss_is_on_list, new_Stop_Loss_value_list, new_Trailing_Stop_Loss_is_on_list, new_Trailing_Stop_Loss_value_list, new_Move_Stop_Loss_is_on_list, new_Move_Stop_Loss_value_1_list, new_Move_Stop_Loss_value_2_list, new_Initiate_Trailing_Stop_at_is_on_list, new_Initiate_Trailing_Stop_at_value_1_list, new_Initiate_Trailing_Stop_at_value_2_list

from  itertools import chain

# Function to extract account information from the current sheet.
# Input: current sheet
# Output: nested dictionaries 

def extract_account_input_section_data(currentSheet):
  account_input_section_dict_list=[]

  column_A_names = currentSheet.col_values(1)

  # get the list of algorithm names in this sheet.
  algo_list = currentSheet.row_values(column_A_names.index("Algorithm Name")+1)
  algo_list_length = len(algo_list)
  new_algo_list=[]

  # if the first value in the list is the field name "Algorithm Name", then get the subsequent names and insert into a new list
  if algo_list[0] == "Algorithm Name":
    for i in range(algo_list_length-1):
      if algo_list[i+1] != "":
        #print("ALG LIST 2:",algo_list[i+1])
        new_algo_list.insert(i,algo_list[i+1])
    #print("NEW ALGO LIST = ",new_algo_list)

  # get list of account names
  account_names_list = currentSheet.row_values(column_A_names.index("Account Name")+1)
  account_names_list_length = len(account_names_list)
  new_account_names_list=[]

  if account_names_list[0] == "Account Name":
    for i in range(account_names_list_length-1):
      if account_names_list[i+1] != "":
         new_account_names_list.insert(i,account_names_list[i+1])
    #print("NEW ACCT NAME LIST = ",new_account_names_list)

  # get list of account numbers
  account_number_list = currentSheet.row_values(column_A_names.index("Account Number")+1)
  account_number_list_length = len(account_number_list)
  new_account_number_list=[]

  if account_number_list[0] == "Account Number":
    for i in range(account_number_list_length-1):
      if account_number_list[i+1] != "":
         new_account_number_list.insert(i,account_number_list[i+1])
    #print("NEW ACCT NUMBER LIST = ",new_account_number_list)

  # get list of Access Key numbers
  access_key_list = currentSheet.row_values(column_A_names.index("Access Key (From Oanda)")+1)
  access_key_list_length = len(access_key_list)
  new_access_key_list=[]

  if access_key_list[0] == "Access Key (From Oanda)":
    for i in range(access_key_list_length-1):
      if access_key_list[i+1] != "":
         new_access_key_list.insert(i,access_key_list[i+1])
    #print("NEW access_key LIST = ",new_access_key_list)

  # get list of currencies
  currency_list = currentSheet.row_values(column_A_names.index("Currency")+1)
  currency_list_length = len(currency_list)
  new_currency_list=[]

  if currency_list[0] == "Currency":
    for i in range(currency_list_length-1):
      if currency_list[i+1] != "":
         new_currency_list.insert(i,currency_list[i+1])
    #print("NEW currency LIST = ",new_currency_list)

  # get Trade Direction
  trade_direction_list = currentSheet.row_values(column_A_names.index("Trade Direction")+1)
  trade_direction_list_length = len(trade_direction_list)
  new_trade_direction_list=[]

  if trade_direction_list[0] == "Trade Direction":
    for i in range(trade_direction_list_length-1):
      if trade_direction_list[i+1] != "":
         new_trade_direction_list.insert(i,trade_direction_list[i+1])
    #print("NEW trade direction LIST = ",new_trade_direction_list)

  # get Risk
  risk_list = currentSheet.row_values(column_A_names.index("Risk")+1)
  risk_list_length = len(risk_list)
  #print("risk length =", risk_list_length)
  new_risk_is_on_list=[]
  new_risk_value_list = []

  if risk_list[0] == "Risk":
    #print("RISK LIST = ",risk_list)
    i = 1
    for i in range(risk_list_length):
      if risk_list[i] == "On":
        new_risk_is_on_list.insert(i,risk_list[i])
        new_risk_value_list.insert(i,risk_list[i+1])
      elif risk_list[i] == "Off":
        new_risk_is_on_list.insert(i,risk_list[i])
        new_risk_value_list.insert(i,"0")
    #print("NEW Risk IS ON LIST = ",new_risk_is_on_list, "NEW RISK VALUE list = ",new_risk_value_list)

  #print("++++++++++++++++++++++++++++++++++++")
  # with all the account section inputs stored in lists, merge them into one dict with algo_name as the key and other variables as values
  #dictList={}
  #new_list = zip(new_account_names_list,new_account_number_list,new_access_key_list,new_currency_list,new_trade_direction_list,new_risk_is_on_list,new_risk_value_list)
  #dictList = dict(zip(new_algo_list,new_list))
  #print("NEW DICT in list form:::: ", dictList)
  #print("++++++++++++++++++++++++++++++++++++")

  print("=============================================")

  #Get SLM Info and add it to the master dictionary
  new_slm_is_on_list, new_Take_Profit_is_on_list, new_Take_Profit_value_list, new_Stop_Loss_is_on_list, new_Stop_Loss_value_list, new_Trailing_Stop_Loss_is_on_list, new_Trailing_Stop_Loss_value_list, new_Move_Stop_Loss_is_on_list, new_Move_Stop_Loss_value_1_list, new_Move_Stop_Loss_value_2_list, new_Initiate_Trailing_Stop_at_is_on_list, new_Initiate_Trailing_Stop_at_value_1_list, new_Initiate_Trailing_Stop_at_value_2_list = extract_Stop_Loss_Manager_input_section_data(currentSheet)

  #print("IN ACCT_INFO_METHOD...:SLM_dict = ",new_slm_is_on_list)
  new_algorithm_name=[]
  for rr in range(len(new_algo_list)):
      new_algorithm_name.insert(rr,"Algorithm_Info")

  if(len(new_slm_is_on_list) == len(new_Take_Profit_is_on_list) == len(new_Take_Profit_value_list) == len(new_Stop_Loss_is_on_list) == len(new_Stop_Loss_value_list) == len(new_Trailing_Stop_Loss_is_on_list) == len(new_Trailing_Stop_Loss_value_list) == len(new_Move_Stop_Loss_is_on_list) == len(new_Move_Stop_Loss_value_1_list) == len(new_Move_Stop_Loss_value_2_list) == len(new_Initiate_Trailing_Stop_at_is_on_list) == len(new_Initiate_Trailing_Stop_at_value_1_list) == len(new_Initiate_Trailing_Stop_at_value_2_list)):

    new_nested_dict = dict(map(lambda new_algorithm_name,alg_name,acc_name,acct_num,access_k,currency,trade_dir,Is_Risk_On,Risk_Value,Is_SLM_On,Is_Initial_Take_Profit_On,Initial_Take_Profit_Value, Is_Stop_Loss_On, Stop_Loss_Value, Is_Trailing_SL_On, Trailing_Stop_Loss_Value, Is_Move_Stop_Loss_To_On, Move_Stop_Loss_Value_1, Move_Stop_Loss_Value_2, Is_Initiate_TS_at_On, Initiate_TS_at_Value_1, Initiate_TS_at_Value_2: (alg_name,
                                                                                                      {'Algorithm_Name':str(alg_name),
                                                                                                       'Account_Name':str(acc_name),
                                                                                                       'Account_Number':str(acct_num),
                                                                                                       'Access_Key':str(access_k),
                                                                                                       'Currency':str(currency),
                                                                                                       'Trade_Direction':str(trade_dir),
                                                                                                       'Is_Risk_On':str(Is_Risk_On),
                                                                                                       'Risk_Value':str(Risk_Value),
                                                                                                       'Is_SLM_On':str(Is_SLM_On),
                                                                                                       'Is_Initial_Take_Profit_On':str(Is_Initial_Take_Profit_On),
                                                                                                       'Initial_Take_Profit_Value':str(Initial_Take_Profit_Value),
                                                                                                       'Is_Stop_Loss_On':str(Is_Stop_Loss_On),
                                                                                                       'Stop_Loss_Value':str(Stop_Loss_Value),
                                                                                                       'Is_Trailing_SL_On':str(Is_Trailing_SL_On),
                                                                                                       'Trailing_Stop_Loss_Value':str(Trailing_Stop_Loss_Value),
                                                                                                       'Is_Move_Stop_Loss_To_On':str(Is_Move_Stop_Loss_To_On),
                                                                                                       'Move_Stop_Loss_Value_1':str(Move_Stop_Loss_Value_1),
                                                                                                       'Move_Stop_Loss_Value_2':str(Move_Stop_Loss_Value_2),
                                                                                                       'Is_Initiate_TS_at_On':str(Is_Initiate_TS_at_On),
                                                                                                       'Initiate_TS_at_Value_1':str(Initiate_TS_at_Value_1),
                                                                                                       'Initiate_TS_at_Value_2':str(Initiate_TS_at_Value_2)}),new_algorithm_name, new_algo_list,new_account_names_list,new_account_number_list,new_access_key_list, new_currency_list,new_trade_direction_list,new_risk_is_on_list,new_risk_value_list,new_slm_is_on_list,new_Take_Profit_is_on_list,new_Take_Profit_value_list,new_Stop_Loss_is_on_list, new_Stop_Loss_value_list, new_Trailing_Stop_Loss_is_on_list, new_Trailing_Stop_Loss_value_list, new_Move_Stop_Loss_is_on_list, new_Move_Stop_Loss_value_1_list, new_Move_Stop_Loss_value_2_list, new_Initiate_Trailing_Stop_at_is_on_list, new_Initiate_Trailing_Stop_at_value_1_list, new_Initiate_Trailing_Stop_at_value_2_list))
  #print("NEW DICT in nested dict form === ",new_nested_dict)
  #print("=============================================")
  else:
    print("Missing input values, please check your input values")
    new_nested_dict = []
  """
  new_list1=zip(new_algo_list,
               new_slm_is_on_list,
               new_Take_Profit_is_on_list,
               new_Take_Profit_value_list,
               new_Stop_Loss_is_on_list,
               new_Stop_Loss_value_list,
               new_Trailing_Stop_Loss_is_on_list,
               new_Trailing_Stop_Loss_value_list,
               new_Move_Stop_Loss_is_on_list,
               new_Move_Stop_Loss_value_1_list,
               new_Move_Stop_Loss_value_2_list,
               new_Initiate_Trailing_Stop_at_is_on_list,
               new_Initiate_Trailing_Stop_at_value_1_list,
               new_Initiate_Trailing_Stop_at_value_2_list)
  #new_list.append(list(new_list1))
  ##print("NEW LIST = ",list(new_list))

  """
  return new_nested_dict

# Function to extact the configuration data from the opened google sheet.
# Input: Configuration data to be read
# Output: Dictionary of config data

def extract_config_section_data_from_sheet(config_data):

  master_alg_list = get_sub_list(config_data,"Master Algorithm")
  #print("MA = ",master_alg_list)
  is_master_algorithm_on = master_alg_list[0][1]
  if is_master_algorithm_on == 'On':
    config_dict.update({'Is_Master_Algorithm_On':is_master_algorithm_on})

  auto_update_list = get_sub_list(config_data,"Auto Update")
  is_auto_update_on = auto_update_list[0][1]
  if is_auto_update_on == 'On':
    config_dict.update({'Is_Auto_Update_On':is_auto_update_on})
  else:
    config_dict.update({'Is_Auto_Update_On':'Off'})

  manual_update_list = get_sub_list(config_data,"Manual Update")
  is_manual_update_on = manual_update_list[0][1]
  if is_manual_update_on == 'On':
    config_dict.update({'Is_Manual_Update_On':is_manual_update_on})
  else:
    config_dict.update({'Is_Manual_Update_On':'Off'})

  #print("CONFIG DICT = ",config_dict)
  return config_dict

# Function to get sub lists from list of lists.
# Input: list of the lists and pattern to search for
# Output: matches of the pattern

def get_sub_list(list_of_lists,pattern):
    matches = []
    for substring in list_of_lists:
       try:
          substring.index(pattern)
          matches.append(substring)
       except ValueError:
          continue

    return matches

def main():
  sheet_url = 'https://docs.google.com/spreadsheets/d/11DnkxvnOSQ5AnE9MVXhxcceSSkdfZFUE3Wt_V9D4Rds/edit?usp=sharing'

  #0. Read the Frontend file, parse and store the data into lists
  print("Opening the FARDe Front End Design Sheet")
  work_book = open_spread_sheet(sheet_url)
  print("Reading the Frontend-Input sheet")
  list_of_dicts1 = get_input_data_from_work_book(work_book,sheet_name)

  print("Done reading the input from Frontend-Input sheet. Please call the \"get_..() or Is_..()\" member functions to retrieve the data from the data dictionary.")
  #print("MASTER_INPUT_DICT::: ",list_of_dicts1)
  #print("MFID = ",master_frontend_input_dict)
  #print("IN MAIN NEW LIST = ",new_list)

sheet_name = "Frontend-Input"
config_dict={}
list_of_dicts = {}
master_frontend_input_dict={}
output_sheet_parameter_list_dict={}
new_list=[]

main()

#%cd "/content/drive/My Drive/Colab Notebooks"
#!pip install import-ipynb
#import import_ipynb

# Define set of functions to check if multipl configuration parameters are on or off.

def Is_Master_Algorithm_On():
  #print("MA get method:", master_frontend_input_dict.get('Is_Master_Algorithm_On'))
  return master_frontend_input_dict.get('Is_Master_Algorithm_On')

def Is_Auto_Update_On():
  return master_frontend_input_dict.get('Is_Auto_Update_On')

def Is_Manual_Update_On():
  return master_frontend_input_dict.get('Is_Manual_Update_On')

def get_algorithm_input_dicts():

  mfid = master_frontend_input_dict.copy()
  for d in master_frontend_input_dict.keys():
    #print("D = ",d)
    if d =='Is_Master_Algorithm_On':
      del mfid[d]
    if d =='Is_Auto_Update_On':
      del mfid[d]
    if d =='Is_Manual_Update_On':
      del mfid[d]

  #print("MFiD = ",mfid)

  return mfid

a_d = get_algorithm_input_dicts()
#print("Algo dict=",a_d)

# Function to write the data into the google sheet.
# Input: output dictionary
# Output: None

def set_Output_sheet(output_dict):
  #print("IN SET O/P SHEET")
  sheet_url = 'https://docs.google.com/spreadsheets/d/11DnkxvnOSQ5AnE9MVXhxcceSSkdfZFUE3Wt_V9D4Rds/edit?usp=sharing'
  work_book = open_spread_sheet(sheet_url)
  output_sheet = work_book.worksheet("Frontend-Output")
  print("Opened output sheet and started populating the fields.")

  #parse the output_dict and break it into lists from which the relevant data can be extracted
  balance_list = []
  equity_list = []
  Profit_Loss_USD_list = []
  Profit_Loss_Pips = []
  profit_loss_percentage_list = []
  profit_loss_pips_list = []
  current_price_list=[]
  executed_price_list = []
  slippage_pips_list = []
  take_profit_list = []
  take_profit_distance_list=[]
  stop_loss_list=[]
  stop_loss_distance_list = []
  trailing_stop_loss_list=[]
  trailing_stop_loss_distance_list = []
  time_executed_list = []
  duration_list = []

  for k,v in output_dict.items():
    #print("===================\n")
    #print("KV PAIR:",k,v)
    #L=[]
    for i,j in v.items():
        #L.append(i)
        if i == "Balance":
          balance_list.append(j)
        elif i == "Equity":
          equity_list.append(j)
          #print("i,j=",i,j)
          #print("L = ",L )
        elif i == "Profit_Loss_USD":
            Profit_Loss_USD_list.append(j)
        elif i == "Profit_Loss_Pips":
            profit_loss_pips_list.append(j)
        elif i == "Current_Price":
            current_price_list.append(j)
        elif i == "Executed_Price":
            executed_price_list.append(j)
        elif i == "Slippage_Pips":
            slippage_pips_list.append(j)
        elif i == "Take_Profit":
            take_profit_list.append(j)
        elif i == "Take_Profit_Distance":
            take_profit_distance_list.append(j)
        elif i == "Stop_Loss":
            stop_loss_list.append(j)
        elif i == "Stop_Loss_Distance":
            stop_loss_distance_list.append(j)
        elif i == "Trailing_Stop_Loss":
            trailing_stop_loss_list.append(j)
        elif i == "Trailing_Stop_Loss_Distance":
            trailing_stop_loss_distance_list.append(j)
        elif i == "Time_Executed":
            time_executed_list.append(j)

  # Updating of Balance row
  balance_cell = output_sheet.find("Balance")
  #print("balance cell col= ",balance_cell.col)
  bal_col = balance_cell.col+1
  #print("2 cols away = ",col)
  bal_row = balance_cell.row
  #print("Row = ",row)
  #bal = output_dict['Balance']
  #print("BAL = ",bal)
  for i in balance_list:
    output_sheet.update_cell(bal_row, bal_col, i)
    bal_col = bal_col + 5

  # Updating of Equity row
  eq_cell = output_sheet.find("Equity")
  eq_col = eq_cell.col+1
  #print("2 cols away = ",col)
  eq_row = eq_cell.row
  #eq = output_dict['Equity']
  for i in equity_list:
    output_sheet.update_cell(eq_row, eq_col, i)
    eq_col = eq_col + 5

  # Updating of Profit Loss row
  pl_cell = output_sheet.find("Profit / Loss (USD) | %")
  pl_col = pl_cell.col+1
  pl_row = pl_cell.row
  #pl = output_dict['Profit_Loss_USD']
  #pl = float(float(eq) - float(bal))
  #print("PL=",pl)
  for i in Profit_Loss_USD_list:
    output_sheet.update_cell(pl_row, pl_col, i)
    pl_col = pl_col + 5

  # Updating of Profit Loss Pips row
  pl_pips_cell = output_sheet.find("Profit / Loss (Pips)")
  pl_pips_col = pl_pips_cell.col+1
  pl_pips_row = pl_pips_cell.row
  #pl = output_dict['Profit_Loss_USD']
  #pl = float(float(eq) - float(bal))
  #print("PL=",pl)
  for i in profit_loss_pips_list:
    output_sheet.update_cell(pl_pips_row, pl_pips_col, i)
    pl_pips_col = pl_pips_col + 5

  # Updating of Current Price row
  current_price_cell = output_sheet.find("Current Price")
  current_price_col = current_price_cell.col+1
  current_price_row = current_price_cell.row
  #pl = output_dict['Profit_Loss_USD']
  #pl = float(float(eq) - float(bal))
  #print("PL=",pl)
  for i in current_price_list:
    output_sheet.update_cell(current_price_row, current_price_col, i)
    current_price_col = current_price_col + 5

  # Updating of Executed Price row
  executed_price_cell = output_sheet.find("Executed Price | Slippage pips")
  executed_price_col = executed_price_cell.col+1
  executed_price_row = executed_price_cell.row
  #pl = output_dict['Profit_Loss_USD']
  #pl = float(float(eq) - float(bal))
  #print("PL=",pl)
  for i in executed_price_list:
    output_sheet.update_cell(executed_price_row, executed_price_col, i)
    executed_price_col = executed_price_col + 5

  # Updating of Take Profit row
  take_profit_cell = output_sheet.find("Take Profit | Distance")
  take_profit_col = take_profit_cell.col+1
  take_profit_row = take_profit_cell.row
  #pl = output_dict['Profit_Loss_USD']
  #pl = float(float(eq) - float(bal))
  #print("PL=",pl)
  for i in take_profit_list:
    output_sheet.update_cell(take_profit_row, take_profit_col, i)
    take_profit_col = take_profit_col + 5

  # Updating of Stop Loss row
  stop_loss_cell = output_sheet.find("Stop Loss | Distance")
  stop_loss_col = stop_loss_cell.col+1
  stop_loss_row = stop_loss_cell.row
  #pl = output_dict['Profit_Loss_USD']
  #pl = float(float(eq) - float(bal))
  #print("PL=",pl)
  for i in stop_loss_list:
    output_sheet.update_cell(stop_loss_row, stop_loss_col, i)
    stop_loss_col = stop_loss_col + 5

  # Updating of Trailing Stop Loss row
  trailing_stop_loss_cell = output_sheet.find("Trailing Stop Loss | Distance")
  trailing_stop_loss_col = trailing_stop_loss_cell.col+1
  trailing_stop_loss_row = trailing_stop_loss_cell.row
  #pl = output_dict['Profit_Loss_USD']
  #pl = float(float(eq) - float(bal))
  #print("PL=",pl)
  for i in trailing_stop_loss_list:
    output_sheet.update_cell(trailing_stop_loss_row, trailing_stop_loss_col, i)
    trailing_stop_loss_col = trailing_stop_loss_col + 5

  # Updating of Time Executed row
  time_executed_cell = output_sheet.find("Time Executed | Duration")
  time_executed_col = time_executed_cell.col+1
  time_executed_row = time_executed_cell.row
  #pl = output_dict['Profit_Loss_USD']
  #pl = float(float(eq) - float(bal))
  #print("PL=",pl)
  for i in time_executed_list:
    output_sheet.update_cell(time_executed_row, time_executed_col, i)
    time_executed_col = time_executed_col + 5

  #print("Writing algo parameters")
  #update_output_sheet_with_algorithm_parameters(output_sheet)

  print("Completed updating the Frontend-Output spreadsheet tab. Please check the Frontend-Output tab.")

#out_dict={'Balance':'10070','Equity':'10030'}
# output_dict['Profit_Loss_USD'] = pl
#set_Output_sheet(out_dict)

def update_output_sheet_with_algorithm_parameters(output_sheet):
 """
  print("In update param list method")
  range1 = ["C17:C31","I17:I31"]
  for item in new_list:
    print("ITEM = ",item)
    for i,val in item:
      #output_sheet.batch_update([{'range':'B17:B90', 'values': [val] }])
      output_sheet.update(range1[i],item[val])
      print("Val = ",val)
 """

# build test output dict to test the writing into the sheet
import random
from datetime import datetime, timedelta
algo_name = []
bal_list = []
equity_list = []
profit_loss_USD_list = []
profit_loss_pips_list = []
current_price_list=[]
executed_price_list = []
slippage_pips_list = []
take_profit_list = []
take_profit_distance_list=[]
stop_loss_list=[]
stop_loss_distance_list = []
trailing_stop_loss_list=[]
trailing_stop_loss_distance_list = []
time_executed_list = []
duration_list = []
output_dict = {}
for key in a_d:
  algo_name.append(key)
#print("A NAME+=",algo_name)

for i in range(len(algo_name)):
  bal_list.append(random.random()*10000)
  equity_list.append(random.random()*10000)
  profit_loss_USD_list.insert(i,(bal_list[i]-equity_list[i]))
  profit_loss_pips_list.append(random.random()*100)
  current_price_list.append(random.random()*10)
  executed_price_list.append(random.random()*10)
  take_profit_list.append(random.random()*10)
  stop_loss_list.append(random.random()*10)
  trailing_stop_loss_list.append(random.random()*10)
  time_executed_list.append(datetime.now())

#print("PL list = ",profit_loss_USD_list)

# create the test output dict with few fields containing test data
output_dict = {algo_name:{'Balance':str(bal_list),'Equity':str(equity_list),'Profit_Loss_USD':str(profit_loss_USD_list), 'Profit_Loss_Pips':str(profit_loss_pips_list), 'Current_Price':str(current_price_list), 'Executed_Price':str(executed_price_list), 'Take_Profit':str(take_profit_list),'Stop_Loss':str(stop_loss_list), 'Trailing_Stop_Loss':str(trailing_stop_loss_list),'Time_Executed':str(time_executed_list)} for algo_name,bal_list,equity_list,profit_loss_USD_list,profit_loss_pips_list,current_price_list, executed_price_list, take_profit_list, stop_loss_list, trailing_stop_loss_list, time_executed_list in zip(algo_name,bal_list,equity_list,profit_loss_USD_list,profit_loss_pips_list,current_price_list, executed_price_list, take_profit_list, stop_loss_list, trailing_stop_loss_list, time_executed_list)}
print("Output DICT = ",output_dict)

set_Output_sheet(output_dict)
# process_dicts(output_dict)

def process_dicts(outs_dict):
  balc_list = []
  equity_list = []
  Profit_Loss_USD_list = []

  for k,v in outs_dict.items():
    print("===================\n")
    print("KV PAIR:",k,v)
    #L=[]
    for i,j in v.items():
        #L.append(i)
        if i == "Balance":
          balc_list.append(j)
        elif i == "Equity":
          equity_list.append(j)
          #print("i,j=",i,j)
          #print("L = ",L )
        elif i == "Profit_Loss_USD":
            Profit_Loss_USD_list.append(j)

  print("BALC LIST = ",balc_list)
  print("EQQ LIST = ",equity_list)
  print("PL USD LIST = ",profit_loss_USD_list)

a = ['A', 'B', 'C', 'D']
b = [1, 2, 3, 4]
c = [9, 8, 7, 6]

dct = dict(map(lambda x, y, z : (x, {str(y): str(z)}), a, b, c))

print("dct =",dct)

d = {k: {str(x): str(y)} for k, x, y in zip(a, b, c)}
print("D=",d)

#for item in dct.keys():
print("Keys = ", dct.keys(),"values = ",dct.values())
