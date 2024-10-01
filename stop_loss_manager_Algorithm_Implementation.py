# -*- coding: utf-8 -*-
"""STOP LOSS MANAGER.ipynb

Author: Anand Cheruvu
Version: 1.2
"""

from google.colab import drive
drive.mount('/content/drive')

# Commented out IPython magic to ensure Python compatibility.
#ensure all the ipynb files are in the same directory. If not, change the path before executing this
# %cd "/content/drive/My Drive/Colab Notebooks"
!pip install import-ipynb
import import_ipynb
import FrontendParser_v1_2  #import the parser library

# install the latest OANDA API
!pip install git+https://github.com/hootnot/oanda-api-v20.git

# Testing FrontendParser member function
if FrontendParser_v1_2.Is_Master_Algorithm_On() == "On":
 print("The Master Algorithm is On!")
elif FrontendParser_v1_2.Is_Master_Algorithm_On() == "Off":
  print("off")
inputVals = FrontendParser_v1_2.get_algorithm_input_dicts()
print("MASTER_INPUT_DICT::: ",inputVals)

#Get all values from dictionary

inputs = inputVals["1004"]

#Get values (pips)
if inputs["Is_Initial_Take_Profit_On"] == "On": initial_take_profit = int(inputs["Initial_Take_Profit_Value"])/10000
if inputs["Is_Stop_Loss_On"] == "On": initial_stop_loss = int(inputs["Stop_Loss_Value"])/10000
if inputs["Is_Move_Stop_Loss_To_On"] == "On":
  move_stop_loss_to_price = int(inputs["Move_Stop_Loss_Value_1"])/10000
  move_stop_loss_when_price = int(inputs["Move_Stop_Loss_Value_2"])/10000
if inputs["Is_Initiate_TS_at_On"] == "On":
  initiate_trailing_stop_loss_price = int(inputs["Initiate_TS_at_Value_1"])/10000
  initiate_trailing_stop_when_price = int(inputs["Initiate_TS_at_Value_2"])/10000

#Main method
def Main():
  openTrades()
  getPrice()
  if inputs["Is_Initial_Take_Profit_On"] == "On": takeProfit()
  if inputs["Is_Move_Stop_Loss_To_On"] == "On": moveStopLoss()
  if inputs["Is_Initiate_TS_at_On"] == "On": trailingStopLoss()

#Get open trades
import json
import oandapyV20
import oandapyV20.endpoints.trades as trades

access_token="insert the access token"
accountID="get the Account ID from the config file"

def openTrades():
  client = oandapyV20.API(access_token=access_token)

  r = trades.OpenTrades(accountID=accountID)
  rv = client.request(r)
  response = (json.dumps(rv, indent=2))
  try:
    tradeNum = (int(response[response.find("id")+6:response.find("id")+9]))
    sign = ((response[response.find("currentUnits")+16:response.find("currentUnits")+17]))
  except:
    tradeNum = "N/A"
    sign = "N/A"

  if sign == "-": tradeType = "sell"
  else: tradeType = "buy"

  print(sign, tradeNum, tradeType)

  return (tradeNum, tradeType)


openTrades()

#Get price at this time
import json
import oandapyV20
import oandapyV20.endpoints.pricing as pricing
from oandapyV20.exceptions import StreamTerminated


def getPrice(Tradetype):
  client = oandapyV20.API(access_token=access_token)

  instruments = ["EUR_USD"]
  a = pricing.PricingStream(accountID=accountID, params={"instruments": ",".join(instruments)})

  n = 0
  stopAfter = 1 #Recieve only first price
  try:
      for tick in client.request(a):
          if n >= stopAfter:
              a.terminate()
          else:
              print(tick)
              if Tradetype == "sell":
                  price = float(((tick["bids"])[0])["price"])
              else:
                  price = float(((tick["asks"])[0])["price"])
          n += 1

  except StreamTerminated as err:
      print("Stream processing ended because we made it stop after {} ticks".format(n))
  print(price)

getPrice(openTrades())

#Instantiate take profit
import json
import oandapyV20
import oandapyV20.endpoints.pricing as pricing
import oandapyV20.endpoints.orders as orders
from oandapyV20.contrib.requests import TakeProfitOrderRequest

def takeProfit():
  accountID, access_token = accountID, access_token
  client = oandapyV20.API(access_token=access_token)

  ordr = TakeProfitOrderRequest(tradeID=tradeNum, price=initial_take_profit)
  print(json.dumps(ordr.data, indent=4))

  r = orders.OrderCreate(accountID, data=ordr.data)
  rv = client.request(r)

# Move stop loss according to price
import json
import oandapyV20
import oandapyV20.endpoints.pricing as pricing
import oandapyV20.endpoints.orders as orders
from oandapyV20.contrib.requests import StopLossOrderRequest

def moveStopLoss():
  accountID, access_token = accountID, access_token
  client = oandapyV20.API(access_token=access_token)

  new_stop_loss = price + move_stop_loss_to_price
  ordr = StopLossOrderRequest(tradeID=tradeNum, price=new_stop_loss)

  a = pricing.PricingStream(accountID=accountID, params={"instruments": "EUR_USD"})

  try:
      for tick in client.request(a):
          if tradeType == "sell":
              currentPrice = float(((tick["bids"])[0])["price"])
              if currentPrice < price - move_stop_loss_when_price:
                  r = orders.OrderCreate(accountID, data=ordr.data)
                  rv = client.request(r)
                  print(json.dumps(rv, indent=4))
                  break
          else:
              currentPrice = float(((tick["asks"])[0])["price"])
              if currentPrice > price + move_stop_loss_when_price:
                  r = orders.OrderCreate(accountID, data=ordr.data)
                  rv = client.request(r)
                  print(json.dumps(rv, indent=4))
                  break
  except:
      print("Error")

#Instantiate trailing stop loss based on price
import json
import oandapyV20
import oandapyV20.endpoints.pricing as pricing
import oandapyV20.endpoints.orders as orders
from oandapyV20.contrib.requests import TrailingStopLossOrderRequest

def trailingStopLoss():
  accountID, access_token = accountID, access_token
  client = oandapyV20.API(access_token=access_token)

  trailing_stop_loss_distance = price + initiate_trailing_stop_loss_price
  ordr = TrailingStopLossOrderRequest(tradeID=tradeNum,distance=trailing_stop_loss_distance)

  a = pricing.PricingStream(accountID=accountID, params={"instruments": ["EUR_USD"]})

  try:
    for tick in client.request(a):
            if tradeType == "sell":
               currentPrice = float(((tick["bids"])[0])["price"])
                  if currentPrice < (price - initiate_trailing_stop_when_price):
                    r = orders.OrderCreate(accountID, data=ordr.data)
                    rv = client.request(r)
                    print(json.dumps(rv, indent=4))
                    break
            else:
              currentPrice = float(((tick["asks"])[0])["price"])
              if currentPrice > price + initiate_trailing_stop_when_price:
                  r = orders.OrderCreate(accountID, data=ordr.data)
                  rv = client.request(r)
                  print(json.dumps(rv, indent=4))
                  break
  except:
    print("Error")
