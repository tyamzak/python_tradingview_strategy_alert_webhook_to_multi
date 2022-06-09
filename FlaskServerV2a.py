#============================================================================
# TradingView + Binance等 仮想通貨
# TODO 各取引所ごとに関数を分けたほうがいい。
# 未定義　TV_MagicNo　ccxtKucoinf
#============================================================================
# -*- coding: utf-8 -*-
import time
import ast
from flask import Flask, request, abort
from pprint import pprint
import datetime
import requests
import os
from os.path import join, dirname
from dotenv import load_dotenv
from pathlib import Path
from matplotlib import pyplot as plt
import json
import hmac
import hashlib

########################################################
# load env
########################################################

load_dotenv(verbose=True)

dotenv_path = join(Path().resolve(), '.env')
load_dotenv(dotenv_path)

########################################################
# CCXT
########################################################

import ccxt

# BitFlyer
bitflyer = ccxt.bitflyer()
bitflyer.apiKey = ''
bitflyer.secret = ''

# bybit
bybit = ccxt.bybit({"apiKey":"", "secret":""})

# Binance 
Binance = ccxt.binance()
Binance = ccxt.binance({"apiKey":"", "secret":"","options": {"defaultType": "future"},"enableRateLimit": True,})



# BITGET
ccxtBitget = ccxt.bitget()
# APIキーの設定
ccxtBitget.apiKey = ''
ccxtBitget.secret = ''
ccxtBitget.password = ''



############################################
# configure lot
############################################

BTC_lot = 0.005
ETH_lot = 0.05
AVAX_lot = 0.7
LUNA_lot = 0.7
NEAR_lot = 0.7
AMPL_lot= 20
BNB_lot = 0.1
XRP_lot = 50



########################################################
# Line notification
########################################################
LINE_MSG = "OFF"    # ON or OFF

def LINE_BOT(msg2):
   line_notify_token = '*********************'
   line_notify_api = 'https://notify-api.line.me/api/notify'
   message = msg2
   payload = {'message': message}
   headers = {'Authorization': 'Bearer ' + line_notify_token} 
   line_notify = requests.post(line_notify_api, data=payload, headers=headers)

########################################################
# log configuration
########################################################
from logging import getLogger,Formatter,StreamHandler,FileHandler,INFO
logger2 = getLogger(__name__)
handlerSh = StreamHandler()
handlerFile = FileHandler("Bot.log") # ログファイルの出力先とファイル名を指定
handlerSh.setLevel(INFO)
handlerFile.setLevel(INFO)
logger2.setLevel(INFO)
logger2.addHandler(handlerSh)
logger2.addHandler(handlerFile)



############################################
# Flask
############################################
app = Flask(__name__)


@app.route('/')
def root() -> str:
    """_summary_
    return message when accessed from browser
    Returns:
        str: _description_message
    """
    return 'online'


@app.route('/webhook', methods=['POST'])
def webhook():
    """_summary_
    transaction after webhook received
    """
    #########################################
    # reading order lot
    #########################################
    global BTC_lot
    global ETH_lot
    global AMPL_lot
    global BNB_lot
    global XRP_lot
    global FTM_lot
    global BTC_lot
    global ETH_lot 
    global AVAX_lot 
    global LUNA_lot 
    global NEAR_lot 
    global BNB_lot 
    global XRP_lot 

    #########################################
    # received webhook
    #########################################
    if request.method == 'POST':
        #data = request.get_data()
        print("###")
        data = request.get_data(as_text=True)
        print(data)
        print('Webhook_received')

        ############################################
        # split messages with '@'
        # 
        # TradingView notification example
        # FTX@{{ticker}}@{{strategy.order.action}}@0.005@{{strategy.position_size}}
        ############################################
        moji = data.split('@')[0]
        print("market:",moji)
        moji = data.split('@')[1]
        print("ticker:",moji)
        moji = data.split('@')[2]
        print("order:",moji)
        moji = data.split('@')[3]
        print("size:",moji)
        moji = data.split('@')[4]
        print("pos:",moji)
        print("###")

        ##########################################
        # logging
        ##########################################
        LogTime = datetime.datetime.now()
        sLogTime =  LogTime.strftime("%Y-%m-%d %H:%M:%S")
        text = sLogTime, "Webhook: ", data
        logger2.info(text)

        # ===============================================================================================
        # post order
        # ===============================================================================================
        moji = data.split('@')[2]
        sOrder = ""
        if str(moji) == "buy":
            sOrder = "buy"
        elif str(moji) == "sell":
            sOrder = "sell"
        print("order:",sOrder)

        if data.split('@')[0] == "Bybit":
            print(" Bybit start transaction")
            ############################################
            # HTTP
            ############################################
            endpoint = 'https://api-bybit.com'
            path = '/private/linear/order/create';
            func = '/fapi/v1/ticker/bookTicker'
            ############################################
            # order BTCPERP Bybit
            ############################################
            if str(data.split('@')[1]) == "BTCUSDT":
                print(" order transaction  BTCUSDT (Bybit)")

                # order lot
                TV_lot = ""
                TV_lot = str(data.split('@')[3])
                BTC = bybit.create_order('BTCUSDT', type='market', side=sOrder, amount=str(TV_lot), price=0)
                pprint(BTC)
                # TradingView decide new order or not
                TV_sPosi = data.split('@')[4]
                TV_sPosi = float(TV_sPosi)

                ############################################
                # Symbol and lot
                ############################################
                SYMBOL = "BTCUSDT"
                quantity = TV_lot


############################################

        if data.split('@')[0] == "Binance":
            print(" BINANCE transaction started")
            ############################################
            # order transaction Binance（ USD(S)-M ）USD-M Futures
            ############################################
            ############################################
            # HTTP
            ############################################
            endpoint = 'https://fapi.binance.com'
            path = '/fapi/v1/order?';
            func = '/fapi/v1/ticker/bookTicker'

            ############################################
            # API configuration
            ############################################

            api_key = ""
            secret_key = ""

            ############################################
            # Order Transaction BTCPERP Binance
            ############################################
            if str(data.split('@')[1]) == "BTCPERP":
                print("Order Transaction BTCPERP (Binance)")

                # Order Lots
                TV_lot = ""
                TV_lot = str(data.split('@')[3])


                # Decide new order or not from Trading View
                TV_sPosi = data.split('@')[4]
                TV_sPosi = float(TV_sPosi)

                ############################################
                # Symbol, Lots configuration
                ############################################
                SYMBOL = "BTCUSDT"
                quantity = TV_lot



                ############################################
                # Order transaction
                ############################################
                # Get Current Price
                url_Ticker = endpoint + func + '?symbol=' + SYMBOL;
                res = requests.get(url_Ticker)
                data_Ticker = json.loads(res.text)
                # bid ask
                bid_price = data_Ticker['bidPrice']
                ask_price = data_Ticker['askPrice']
                print("bid: ",bid_price,"    ask: ",ask_price)
                # Define Timestamp
                timestamp = round(datetime.datetime.now().timestamp()) * 1000




                ############################################
                # New Order TV_sPosi>0 is long
                ############################################                
                if (sOrder == "buy") and (TV_sPosi > 0):
                    print(" Order Transaction(Long)  BTC-PERP")

                    # Configure Symbol and Price
                    side = "BUY"
                    price = float(ask_price)

                    # pls HTTP format
                    query = 'symbol=' + SYMBOL + '&side=' + side + '&price=' + str(price) +'&type=LIMIT&timeInForce=GTC'  +'&quantity=' + str(quantity) +'&timestamp=' + str(timestamp);


                ############################################
                # Long
                ############################################
                if (sOrder == "sell") and (TV_sPosi == 0):
                    print(" Transaction(buy)  BTC-PERP")
                    side = "SELL"
                    price = float(bid_price)

                    # pls HTTP format
                    query = 'symbol=' + SYMBOL + '&side=' + side + '&price=' + str(price) +'&type=LIMIT&timeInForce=GTC'  +'&quantity=' + str(quantity) +'&timestamp=' + str(timestamp);



                ############################################
                # New Order TV_sPosi<0 is Short
                ############################################                
                if (sOrder == "sell") and (TV_sPosi < 0):
                    print(" Order Transaction(Short)  BTC-PERP")

                    # Configure Symbol and Price
                    side = "SELL"
                    price = float(bid_price)

                    # pls HTTP format
                    query = 'symbol=' + SYMBOL + '&side=' + side + '&price=' + str(price) +'&type=LIMIT&timeInForce=GTC'  +'&quantity=' + str(quantity) +'&timestamp=' + str(timestamp);


                ############################################
                # Short Transaction
                ############################################
                if (sOrder == "buy") and (TV_sPosi == 0):
                    print(" Order Transaction(Short)  BTC-PERP")
                    side = "BUY"
                    price = float(ask_price)

                    # pls HTTP format
                    query = 'symbol=' + SYMBOL + '&side=' + side + '&price=' + str(price) +'&type=LIMIT&timeInForce=GTC'  +'&quantity=' + str(quantity) +'&timestamp=' + str(timestamp);

                ############################################
                # HTTP request
                ############################################
                # pls HTTP format
                query = 'symbol=' + SYMBOL + '&side=' + side + '&price=' + str(price) +'&type=LIMIT&timeInForce=GTC'  +'&quantity=' + str(quantity) +'&timestamp=' + str(timestamp);

                # hash Security
                signature = hmac.new(bytearray(secret_key.encode('utf-8')), query.encode('utf-8') , digestmod = hashlib.sha256 ).hexdigest()
                # HTTP + Hash
                url = endpoint + path + query + '&signature=' + signature
                # send with header
                headers = {
                    'X-MBX-APIKEY': api_key
                }
                res = requests.post(url, headers=headers)
                datas = json.loads(res.text)
                # Wait
                time.sleep(1)
                print("###")
                print("オーダーID:" , datas['orderId'])
                print("###")
                print(datas)


############################################
            ############################################
            # Order Transaction ETHPERP Binance
            ############################################
            if str(data.split('@')[1]) == "ETHPERP":
                print("Order Transaction ETHPERP (Binance)")

                # Order Lots
                TV_lot = ""
                TV_lot = str(data.split('@')[3])

                # Decide new order or not from Trading View
                TV_sPosi = data.split('@')[4]
                TV_sPosi = float(TV_sPosi)

                ############################################
                # Symbol, Lots configuration
                ############################################
                SYMBOL = "ETHUSDT"
                quantity = TV_lot



                ############################################
                # Order transaction
                ############################################
                # Get Current Price
                url_Ticker = endpoint + func + '?symbol=' + SYMBOL;
                res = requests.get(url_Ticker)
                data_Ticker = json.loads(res.text)
                # bid ask
                bid_price = data_Ticker['bidPrice']
                ask_price = data_Ticker['askPrice']
                print("bid: ",bid_price,"    ask: ",ask_price)
                # Define Timestamp
                timestamp = round(datetime.datetime.now().timestamp()) * 1000




                ############################################
                # New Order TV_sPosi>0 is long
                ############################################                
                if (sOrder == "buy") and (TV_sPosi > 0):
                    print(" Order Transaction(Long)  ETH-PERP")

                    # Configure Symbol and Price
                    side = "BUY"
                    price = float(ask_price)

                    # pls HTTP format
                    query = 'symbol=' + SYMBOL + '&side=' + side + '&price=' + str(price) +'&type=LIMIT&timeInForce=GTC'  +'&quantity=' + str(quantity) +'&timestamp=' + str(timestamp);


                ############################################
                # Long
                ############################################
                if (sOrder == "sell") and (TV_sPosi == 0):
                    print(" Transaction(buy)  BTC-PERP")
                    side = "SELL"
                    price = float(bid_price)

                    # pls HTTP format
                    query = 'symbol=' + SYMBOL + '&side=' + side + '&price=' + str(price) +'&type=LIMIT&timeInForce=GTC'  +'&quantity=' + str(quantity) +'&timestamp=' + str(timestamp);



                ############################################
                # New Order TV_sPosi<0 is Short
                ############################################                
                if (sOrder == "sell") and (TV_sPosi < 0):
                    print(" Order Transaction(Short)  BTC-PERP")

                    # Configure Symbol and Price
                    side = "SELL"
                    price = float(bid_price)

                    # pls HTTP format
                    query = 'symbol=' + SYMBOL + '&side=' + side + '&price=' + str(price) +'&type=LIMIT&timeInForce=GTC'  +'&quantity=' + str(quantity) +'&timestamp=' + str(timestamp);


                ############################################
                # Short Transaction
                ############################################
                if (sOrder == "buy") and (TV_sPosi == 0):
                    print(" Order Transaction(Short)  BTC-PERP")
                    side = "BUY"
                    price = float(ask_price)

                    # pls HTTP format
                    query = 'symbol=' + SYMBOL + '&side=' + side + '&price=' + str(price) +'&type=LIMIT&timeInForce=GTC'  +'&quantity=' + str(quantity) +'&timestamp=' + str(timestamp);




                ############################################
                # HTTP request
                ############################################
                # pls HTTP format
                query = 'symbol=' + SYMBOL + '&side=' + side + '&price=' + str(price) +'&type=LIMIT&timeInForce=GTC'  +'&quantity=' + str(quantity) +'&timestamp=' + str(timestamp);

                # hash Security
                signature = hmac.new(bytearray(secret_key.encode('utf-8')), query.encode('utf-8') , digestmod = hashlib.sha256 ).hexdigest()
                # HTTP + Hash
                url = endpoint + path + query + '&signature=' + signature
                # send with header
                headers = {
                    'X-MBX-APIKEY': api_key
                }
                res = requests.post(url, headers=headers)
                datas = json.loads(res.text)
                # Wait
                time.sleep(1)
                print("###")
                print("オーダーID:" , datas['orderId'])
                print("###")
                print(datas)

############################################
            ############################################
            # Order Transaction AVAXPERP Binance
            ############################################
            if str(data.split('@')[1]) == "AVAXPERP":
                print("Order Transaction AVAXPERP (Binance)")

                # Order Lots
                TV_lot = ""
                TV_lot = str(data.split('@')[3])


                # Decide new order or not from Trading View
                TV_sPosi = data.split('@')[4]
                TV_sPosi = float(TV_sPosi)

                ############################################
                # Symbol, Lots configuration
                ############################################
                SYMBOL = "AVAXUSDT"
                quantity = TV_lot



                ############################################
                # Order transaction
                ############################################
                # Get Current Price
                url_Ticker = endpoint + func + '?symbol=' + SYMBOL;
                res = requests.get(url_Ticker)
                data_Ticker = json.loads(res.text)
                # bid ask
                bid_price = data_Ticker['bidPrice']
                ask_price = data_Ticker['askPrice']
                print("bid: ",bid_price,"    ask: ",ask_price)
                # Define Timestamp
                timestamp = round(datetime.datetime.now().timestamp()) * 1000




                ############################################
                # New Order TV_sPosi>0 is long
                ############################################                
                if (sOrder == "buy") and (TV_sPosi > 0):
                    print(" Order Transaction(Long)  AVAX-PERP")

                    # Configure Symbol and Price
                    side = "BUY"
                    price = float(ask_price)

                    # pls HTTP format
                    query = 'symbol=' + SYMBOL + '&side=' + side + '&price=' + str(price) +'&type=LIMIT&timeInForce=GTC'  +'&quantity=' + str(quantity) +'&timestamp=' + str(timestamp);


                ############################################
                # Long
                ############################################
                if (sOrder == "sell") and (TV_sPosi == 0):
                    print(" Transaction(buy)  AVAX-PERP")
                    side = "SELL"
                    price = float(bid_price)

                    # pls HTTP format
                    query = 'symbol=' + SYMBOL + '&side=' + side + '&price=' + str(price) +'&type=LIMIT&timeInForce=GTC'  +'&quantity=' + str(quantity) +'&timestamp=' + str(timestamp);



                ############################################
                # New Order TV_sPosi<0 is Short
                ############################################                
                if (sOrder == "sell") and (TV_sPosi < 0):
                    print(" Order Transaction(Short)  AVAX-PERP")

                    # Configure Symbol and Price
                    side = "SELL"
                    price = float(bid_price)

                    # pls HTTP format
                    query = 'symbol=' + SYMBOL + '&side=' + side + '&price=' + str(price) +'&type=LIMIT&timeInForce=GTC'  +'&quantity=' + str(quantity) +'&timestamp=' + str(timestamp);


                ############################################
                # Short Transaction
                ############################################
                if (sOrder == "buy") and (TV_sPosi == 0):
                    print(" Order Transaction(Short)  AVAX-PERP")
                    side = "BUY"
                    price = float(ask_price)

                    # pls HTTP format
                    query = 'symbol=' + SYMBOL + '&side=' + side + '&price=' + str(price) +'&type=LIMIT&timeInForce=GTC'  +'&quantity=' + str(quantity) +'&timestamp=' + str(timestamp);

                ############################################
                # HTTP request
                ############################################
                # pls HTTP format
                query = 'symbol=' + SYMBOL + '&side=' + side + '&price=' + str(price) +'&type=LIMIT&timeInForce=GTC'  +'&quantity=' + str(quantity) +'&timestamp=' + str(timestamp);

                # hash Security
                signature = hmac.new(bytearray(secret_key.encode('utf-8')), query.encode('utf-8') , digestmod = hashlib.sha256 ).hexdigest()
                # HTTP + Hash
                url = endpoint + path + query + '&signature=' + signature
                # send with header
                headers = {
                    'X-MBX-APIKEY': api_key
                }
                res = requests.post(url, headers=headers)
                datas = json.loads(res.text)
                # Wait
                time.sleep(1)
                print("###")
                print("オーダーID:" , datas['orderId'])
                print("###")
                print(datas)



        
############################################
        
        ############################################
        # Transaction Bitget
        ############################################
        if data.split('@')[0] == "Bitget":
            print(" BITGET 処理スタート")
            ############################################
            # Order Transaction BTCPERP BITGET
            ############################################
            if str(data.split('@')[1]) == "BTCUSDTPERP":
                print("Order Transaction BTCPERP (BITGET)")

                # Order Lots
                TV_lot = ""
                TV_lot = str(data.split('@')[3])

                # Decide new order or not from Trading View
                TV_sPosi = data.split('@')[4]
                TV_sPosi = float(TV_sPosi)

                ############################################
                # Symbol, Lots configuration
                ############################################
                SYMBOL = "CMT_BTCUSDT"

                ############################################
                # New Order TV_sPosi>0 long params={'type': '1',} 
                ############################################                
                if (sOrder == "buy") and (TV_sPosi > 0):
                    print(" Order Transaction(Long)  BTCUSDTPERP")

                    # Configure Symbol and Price
                    side = "buy"
                    # price = float(ask_price)

                    # Order Transaction
                    BTC = ccxt.bitget.create_order(symbol=SYMBOL, type='market', side=sOrder, amount=str(TV_lot), params={'type': '1',})
                    pprint(BTC)


                ############################################
                # Long params={'type': '3',} needed
                ############################################
                if (sOrder == "sell") and (TV_sPosi == 0):
                    print(" Transaction(buy)  BTCUSDTPERP")
                    side = "sell"
                    # price = float(bid_price)

                    # Order Transaction
                    BTC = ccxt.bitget.create_order(symbol=SYMBOL, type='market', side=sOrder, amount=str(TV_lot), params={'type': '3',})
                    pprint(BTC)



                ############################################
                # New Order TV_sPosi<0 is Short
                ############################################                
                if (sOrder == "sell") and (TV_sPosi < 0):
                    print(" Order Transaction(Short)  BTC-PERP")

                    # Configure Symbol and Price
                    side = "SELL"
                    price = float(bid_price)

                    # pls HTTP format
                    query = 'symbol=' + SYMBOL + '&side=' + side + '&price=' + str(price) +'&type=LIMIT&timeInForce=GTC'  +'&quantity=' + str(quantity) +'&timestamp=' + str(timestamp);


                ############################################
                # Short Transaction
                ############################################
                if (sOrder == "buy") and (TV_sPosi == 0):
                    print(" Order Transaction(Short)  BTC-PERP")
                    side = "BUY"
                    price = float(ask_price)

                    # pls HTTP format
                    query = 'symbol=' + SYMBOL + '&side=' + side + '&price=' + str(price) +'&type=LIMIT&timeInForce=GTC'  +'&quantity=' + str(quantity) +'&timestamp=' + str(timestamp);



            ############################################
            # Order Transaction ETHPERP BITGET
            ############################################
            if str(data.split('@')[1]) == "ETHUSDTPERP":
                print("Order Transaction ETHPERP (BITGET)")

                # Order Lots
                TV_lot = ""
                TV_lot = str(data.split('@')[3])

                # Decide new order or not from Trading View
                TV_sPosi = data.split('@')[4]
                TV_sPosi = float(TV_sPosi)

                ############################################
                # Symbol, Lots configuration
                ############################################
                SYMBOL = "CMT_ETHUSDT"

                ############################################
                # New Order TV_sPosi>0 is long params={'type': '1',} 
                ############################################                
                if (sOrder == "buy") and (TV_sPosi > 0):
                    print(" Order Transaction(Long)  CMT_ETHUSDT")

                    # Configure Symbol and Price
                    side = "buy"
                    # price = float(ask_price)

                    # Order Transaction
                    ETH = ccxt.bitget.create_order(SYMBOL, type='market', side=sOrder, amount=str(TV_lot), params={'type': '1',})
                    pprint(ETH)


                ############################################
                # Long params={'type': '3',} is needed
                ############################################
                if (sOrder == "sell") and (TV_sPosi == 0):
                    print(" Transaction(buy)  CMT_ETHUSDT")
                    side = "sell"
                    # price = float(bid_price)

                    # Order Transaction
                    ETH = ccxt.bitget.create_order(SYMBOL, type='market', side=sOrder, amount=str(TV_lot), params={'type': '3',})
                    pprint(ETH)



            ############################################
            # Order Transaction AVAXPERP BITGET
            ############################################
            if str(data.split('@')[1]) == "AVAXUSDTPERP":
                print("Order Transaction AVAXPERP (BITGET)")

                # Order Lots
                TV_lot = ""
                TV_lot = str(data.split('@')[3])

                # Decide new order or not from Trading View
                TV_sPosi = data.split('@')[4]
                TV_sPosi = float(TV_sPosi)

                ############################################
                # Symbol, Lots configuration
                ############################################
                SYMBOL = "CMT_AVAXUSDT"

                ############################################
                # New Order TV_sPosi>0 is long params={'type': '1',} 
                ############################################                
                if (sOrder == "buy") and (TV_sPosi > 0):
                    print(" Order Transaction(Long)  AVAXUSDTPERP")

                    # Configure Symbol and Price
                    side = "buy"
                    # price = float(ask_price)

                    # Order Transaction
                    BTC = ccxt.Bitget.create_order(SYMBOL, type='market', side=sOrder, amount=str(TV_lot), params={'type': '1',})
                    pprint(BTC)

                    # Logging
                    LogTime = datetime.datetime.now()
                    sLogTime =  LogTime.strftime("%Y-%m-%d %H:%M:%S")
                    text = str(sLogTime)+"Store Order management: "+str(query)+":"+str(TV_MagicNo)
                    logger2.info(text)
                ############################################
                # Long params={'type': '3',} is needed
                ############################################
                if (sOrder == "sell") and (TV_sPosi == 0):
                    print(" Transaction(buy)  AVAXUSDTPERP")
                    side = "sell"
                    # price = float(bid_price)

                    # Order Transaction
                    BTC = ccxt.Bitget.create_order(SYMBOL, type='market', side=sOrder, amount=str(TV_lot), params={'type': '3',})
                    pprint(BTC)

                    # Logging
                    LogTime = datetime.datetime.now()
                    sLogTime =  LogTime.strftime("%Y-%m-%d %H:%M:%S")
                    text = str(sLogTime)+"Store Order management: "+str(query)+":"+str(TV_MagicNo)
                    logger2.info(text)

                ############################################
                # New Order TV_sPosi<0 is Short
                ############################################                
                if (sOrder == "sell") and (TV_sPosi < 0):
                    print(" Order Transaction(Short)  AVAXUSDTPERP")

                    # Configure Symbol and Price
                    side = "SELL"
                    price = float(bid_price)

                    # pls HTTP format
                    query = 'symbol=' + SYMBOL + '&side=' + side + '&price=' + str(price) +'&type=LIMIT&timeInForce=GTC'  +'&quantity=' + str(quantity) +'&timestamp=' + str(timestamp);

                    # Logging
                    LogTime = datetime.datetime.now()
                    sLogTime =  LogTime.strftime("%Y-%m-%d %H:%M:%S")
                    text = str(sLogTime)+"Store Order management: "+str(query)+":"+str(TV_MagicNo)
                    logger2.info(text)
                ############################################
                # Short Transaction
                ############################################
                if (sOrder == "buy") and (TV_sPosi == 0):
                    print(" Order Transaction(Short)  AVAXUSDTPERP")
                    side = "BUY"
                    price = float(ask_price)

                    # pls HTTP format
                    query = 'symbol=' + SYMBOL + '&side=' + side + '&price=' + str(price) +'&type=LIMIT&timeInForce=GTC'  +'&quantity=' + str(quantity) +'&timestamp=' + str(timestamp);

                    # Logging
                    LogTime = datetime.datetime.now()
                    sLogTime =  LogTime.strftime("%Y-%m-%d %H:%M:%S")
                    text = str(sLogTime)+"Store Order management: "+str(query)+":"+str(TV_MagicNo)
                    logger2.info(text)

            ############################################
            # Order Transaction NEARPERP BITGET
            ############################################
            if str(data.split('@')[1]) == "NEARUSDTPERP":
                print("Order Transaction NEARPERP (BITGET)")

                # Order Lots
                TV_lot = ""
                TV_lot = str(data.split('@')[3])

                # Decide new order or not from Trading View
                TV_sPosi = data.split('@')[4]
                TV_sPosi = float(TV_sPosi)

                ############################################
                # Symbol, Lots configuration
                ############################################
                SYMBOL = "CMT_NEARUSDT"
                quantity = TV_lot

            ############################################
            # Order Transaction ATOMPERP BITGET
            ############################################
            if str(data.split('@')[1]) == "ATOMUSDTPERP":
                print("Order Transaction ATOMPERP (BITGET)")

                # Order Lots
                TV_lot = ""
                TV_lot = str(data.split('@')[3])

                # Decide new order or not from Trading View
                TV_sPosi = data.split('@')[4]
                TV_sPosi = float(TV_sPosi)

                ############################################
                # Symbol, Lots configuration
                ############################################
                SYMBOL = "CMT_ATOMUSDT"
                quantity = TV_lot

            ############################################
            # Order Transaction BNBPERP BITGET
            ############################################
            if str(data.split('@')[1]) == "BNBUSDTPERP":
                print("Order Transaction BNBPERP (BITGET)")

                # Order Lots
                TV_lot = ""
                TV_lot = str(data.split('@')[3])

                # Decide new order or not from Trading View
                TV_sPosi = data.split('@')[4]
                TV_sPosi = float(TV_sPosi)

                ############################################
                # Symbol, Lots configuration
                ############################################
                SYMBOL = "CMT_BNBUSDT"
                quantity = TV_lot

        

        
        ############################################
        # Transaction KuCoin
        ############################################
        if data.split('@')[0] == "Kucoin":
            print(" KUCOIN 処理スタート")
            ############################################
            # Order Transaction
            ############################################
            if str(data.split('@')[1]) == "BTCUSDT":
                print("Order Transaction BTCPERP (Kucoin)")

                # Order Lots
                TV_lot = ""
                TV_lot = str(data.split('@')[3])

                # Decide new order or not from Trading View
                TV_sPosi = data.split('@')[4]
                TV_sPosi = float(TV_sPosi)

                ############################################
                # Symbol, Lots configuration
                ############################################
                SYMBOL = "BTC/USDT:USDT"

                ############################################
                # New Order TV_sPosi>0 is long 
                ############################################                
                if (sOrder == "buy") and (TV_sPosi > 0):
                    print(" Order Transaction(Long)  BTC/USDT:USDT")

                    # Configure Symbol and Price
                    side = "buy"
                    # price = float(ask_price)

                    # Order Transaction
                    order_Kucoin = ccxtKucoinf.create_order(SYMBOL, 'market', str(sOrder), int(TV_lot), {'leverage': 4})
                    pprint(order_Kucoin)
                    print("OrderID:" + str(order_Kucoin['id']))


                    # Logging
                    LogTime = datetime.datetime.now()
                    sLogTime =  LogTime.strftime("%Y-%m-%d %H:%M:%S")
                    text = str(sLogTime)+"Store Order management: "+str(query)+":"+str(TV_MagicNo)
                    logger2.info(text)
                ############################################
                # Long 
                ############################################
                if (sOrder == "sell") and (TV_sPosi == 0):
                    print(" Transaction(buy)  BTC/USDT:USDT")
                    side = "sell"
                    # price = float(bid_price)

                    # Order Transaction
                    order_Kucoin = ccxtKucoinf.create_order(SYMBOL, 'market', str(sOrder), int(TV_lot), {'leverage': 4})
                    pprint(order_Kucoin)
                    print("OrderID:" + str(order_Kucoin['id']))

                    # Logging
                    LogTime = datetime.datetime.now()
                    sLogTime =  LogTime.strftime("%Y-%m-%d %H:%M:%S")
                    text = str(sLogTime)+"Store Order management: "+str(query)+":"+str(TV_MagicNo)
                    logger2.info(text)
        

        print("###")

        return '', 200
    else:
        abort(400)

############################################
# inititial configuration
############################################
if __name__ == '__main__':

    app.run(debug=True, port=5000)