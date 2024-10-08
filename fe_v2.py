# -*- coding: utf-8 -*-
"""FE-v2.ipynb

Author: Anand Cheruvu
version: 2
"""

# install the latest OANDA API
!pip install git+https://github.com/hootnot/oanda-api-v20.git

#@title FARDe FrontEnd { run: "auto", vertical-output: true, form-width: "50%" }
Master_Algorithm = "On" #@param ["On", "Off"]
Auto_Update = "On" #@param ["On", "Off"]
Manual_Update = "Off" #@param ["Off", "On"]
Algorithm_Name_1 = "Test1" #@param {type:"string"}
Account_Name_1 = "Demo" #@param {type:"string"}
Account_Number_1 = "101-001-16163394-002" #@param {type:"string"}
Access_Key_1 = "cf85f57a5f83fd5e05ad6cbf2f7b69f3-bb7c6626e971c36e9f45f43ae90d22ac" #@param {type:"string"}
Currency_1 = "EUR/USD" #@param ["EUR/USD", "GBP/JPY", "USD/CAD", "NZD/USD", "AUD/USD"]
Trade_Direction_1 = "Short" #@param ["Long", "Short", "Long & Short"]
Risk_On_Off_1 = "Off" #@param ["On", "Off"]
Risk_Value_1 = "5" #@param {type:"string"}
Stop_Loss_Manager_1 = "On" #@param ["On", "Off"]
SLM_Take_Profit_Initial_On_Off_1 = "On" #@param ["On", "Off"]
SLM_Take_Profit_Initial_Value_1 = "25" #@param {type:"string"}
SLM_Stop_Loss_On_Off_1 = "Off" #@param ["On", "Off"]
SLM_Stop_Loss_Value_1 = "" #@param {type:"string"}
SLM_Trailing_Stop_Loss_On_Off_1 = "Off" #@param ["On", "Off"]
SLM_Trailing_Stop_Loss_Value_1 = "" #@param {type:"string"}
SLM_Move_Stop_Loss_To_On_Off = "Off" #@param ["On", "Off"]
SLM_Move_Stop_Loss_To_Value_1 = "15" #@param {type:"string"}
SLM_Move_Stop_Loss_To_Value_2 = "20" #@param {type:"string"}
SLM_Initiate_Trailing_Stop_Loss_To_On_Off = "On" #@param ["On", "Off"]
SLM_Initiate_Trailing_Stop_Loss_To_Value_1 = "15" #@param {type:"string"}
SLM_Initiate_Trailing_Stop_Loss_To_Value_2 = "20" #@param {type:"string"}


# ---------- Main Code --------------------
import json
import oandapyV20
import oandapyV20.endpoints.trades as trades
import oandapyV20.endpoints.pricing as pricing
import oandapyV20.endpoints.orders as orders
from oandapyV20.contrib.requests import TakeProfitOrderRequest
from oandapyV20.contrib.requests import StopLossOrderRequest
from oandapyV20.contrib.requests import TrailingStopLossOrderRequest

if Master_Algorithm == "On":
  # get authorization
  account_id = Account_Number_1
  access_key = Access_Key_1
  take_profit=0
  stop_loss=0

  if Stop_Loss_Manager_1 == "On":
    if SLM_Take_Profit_Initial_On_Off_1 == "On":
      initial_take_profit = int(SLM_Take_Profit_Initial_Value_1)/10000
    else:
      initial_take_profit = 0
    if SLM_Stop_Loss_On_Off_1 == "On":
      initial_stop_loss = int(SLM_Stop_Loss_Value_1)/10000
    else:
      initial_stop_loss = 0
    if SLM_Move_Stop_Loss_To_On_Off == "On":
      move_stop_loss_to_price = int(SLM_Move_Stop_Loss_To_Value_1)/10000
      move_stop_loss_when_price = int(SLM_Move_Stop_Loss_To_Value_2)/10000
    else:
      move_stop_loss_to_price = 0
      move_stop_loss_when_price = 0
    if SLM_Initiate_Trailing_Stop_Loss_To_On_Off == "On":
      initiate_trailing_stop_loss_price = int(SLM_Initiate_Trailing_Stop_Loss_To_Value_1)/10000
      initiate_trailing_stop_when_price = int(SLM_Initiate_Trailing_Stop_Loss_To_Value_2)/10000
    else:
      print("SLM_Take_Profit_Initial_On_Off_1 is OFF")
      initiate_trailing_stop_loss_price = 0
      initiate_trailing_stop_when_price = 0

    # get open trades
    client = oandapyV20.API(access_token=access_key)
    r = trades.OpenTrades(accountID=account_id)
    rv = client.request(r)
    response = (json.dumps(rv, indent=2))
    try:
     price = float ([acc.get('price') for acc in r.response.get('trades')][0])
     tradeNum = int ([acc.get('id') for acc in r.response.get('trades')][0])
     sign = [acc.get('currentUnits') for acc in r.response.get('trades')][0][0]
    except:
     tradeNum = "N/A"
     sign = "N/A"
     price = "N/A"

    if sign == "-":
      tradeType = "sell"
    else:
      tradeType = "buy"

    if tradeNum != "N/A":
      print("****Open Trades Info: ", "\n","Sign:",sign, "Trade #:", tradeNum, "Trade Type:",tradeType, "Price:",price)

      # initiate take profit
      if tradeType == "sell":
        take_profit = price - initial_take_profit
      else:
        take_profit = price + initial_take_profit

      ordr = TakeProfitOrderRequest(tradeID=tradeNum, price=take_profit)
      print("\n","****Take Profit Order Details ***** \n",json.dumps(ordr.data, indent=4))
      #print(ordr.data['order']['type'])

      if ordr.data['order']['type'] != "TAKE_PROFIT":
        r = orders.OrderCreate(accountID=account_id, data=ordr.data)
        rv = client.request(r)
      else:
        print("\n Take Profit Order already exists")

      # instantiate stop loss
      if tradeType == "sell":
        stop_loss = price + initial_stop_loss
      else:
        stop_loss = price - initial_stop_loss

      ordr = StopLossOrderRequest(tradeID=tradeNum, price=stop_loss)
      print("\n",json.dumps(ordr.data, indent=4))

      r = orders.OrderCreate(accountID=account_id, data=ordr.data)
      rv = client.request(r)

      # move stop loss according to price
      new_stop_loss = price + move_stop_loss_to_price
      data = {
        "stopLoss": {
        "timeInForce": "GTC",
        "price": str (new_stop_loss)
        }
      }

      a = pricing.PricingStream(accountID=account_id, params={"instruments": Currency_1})

      for tick in client.request(a):
        if tradeType == "sell":
          print(tick)
          if tick["type"] == "PRICE":
            currentPrice = float(((tick["bids"])[0])["price"])
            if currentPrice < price - move_stop_loss_when_price:
                r = trades.TradeCRCDO(accountID=account_id, tradeID=tradeID, data=data)
                rv = client.request(r)
                print(json.dumps(rv, indent=4))
                break
          else:
            print(tick)
            if tick["type"] == "PRICE":
              currentPrice = float(((tick["asks"])[0])["price"])
            if currentPrice > price + move_stop_loss_when_price:
                r = trades.TradeCRCDO(accountID=account_id, tradeID=tradeNum, data=data)
                rv = client.request(r)
                print(json.dumps(rv, indent=4))
                break

      # instantiate trailing stop loss based on price
      ordr = TrailingStopLossOrderRequest(tradeID=tradeNum,distance=initiate_trailing_stop_loss_price)
      a = pricing.PricingStream(accountID=accountID, params={"instruments": [Currency_1]})
      print(tradeType)

      for tick in client.request(a):
        if tradeType == "sell":
          print(tick)
          if tick["type"] == "PRICE":
            currentPrice = float(((tick["bids"])[0])["price"])
            if currentPrice < price - initiate_trailing_stop_when_price:
              r = orders.OrderCreate(accountID=account_id, data=ordr.data)
              rv = client.request(r)
              print(json.dumps(rv, indent=4))
              break
          else:
            print(tick)
            if tick["type"] == "PRICE":
              currentPrice = float(((tick["asks"])[0])["price"])
              if currentPrice > price + initiate_trailing_stop_when_price:
                r = orders.OrderCreate(accountID=account_id, data=ordr.data)
                rv = client.request(r)
                print(json.dumps(rv, indent=4))
                break
    else:
      print("***** THERE ARE NO OPEN ORDERS. PLACE AN OPEN ORDER FIRST. ******")

  else:
    print("Stop Loss Manager is Off")

else:
  print("MA IS OFF")
