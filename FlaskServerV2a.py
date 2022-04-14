#============================================================================
# TradingView + Binance等 仮想通貨
# 各取引所ごとに関数を分けたほうがいい。orderデータとかが散らばり過ぎてわからない。
# 未定義　TV_MagicNo　ccxtKucoinf
#============================================================================
# -*- coding: utf-8 -*-
import time
import ast
from flask import Flask, request, abort
from pprint import pprint
import datetime
import requests
# Binance用に追加が必要 start ---------
import json
import hmac
import hashlib
# Binance用に追加が必要  end ---------

#-------------------------------------------------------
# CCXTapi設定
#-------------------------------------------------------

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



# -----------------------------------------------------------------------
# ロット設定 
# TradingViewでロット設定しない場合は、こちらでロットを固定で持つことも可能
# ※通貨の種類増やしたら「def webhook():」のglobalも増やす
# -----------------------------------------------------------------------
# 例)ロット設定
BTC_lot = 0.005
ETH_lot = 0.05
AVAX_lot = 0.7
LUNA_lot = 0.7
NEAR_lot = 0.7
AMPL_lot= 20
BNB_lot = 0.1
XRP_lot = 50

# BITGET


# kucoinfutures用


#-------------------------------------------------------
# Line通知設定
#-------------------------------------------------------
LINE_MSG = "OFF"    # ON or OFF

def LINE_BOT(msg2):
   line_notify_token = '*********************'
   line_notify_api = 'https://notify-api.line.me/api/notify'
   message = msg2
   payload = {'message': message}
   headers = {'Authorization': 'Bearer ' + line_notify_token} 
   line_notify = requests.post(line_notify_api, data=payload, headers=headers)

#-------------------------------------------------------
# ログ設定
#-------------------------------------------------------
from logging import getLogger,Formatter,StreamHandler,FileHandler,INFO
logger2 = getLogger(__name__)
handlerSh = StreamHandler()
handlerFile = FileHandler("Bot.log") # ログファイルの出力先とファイル名を指定
handlerSh.setLevel(INFO)
handlerFile.setLevel(INFO)
logger2.setLevel(INFO)
logger2.addHandler(handlerSh)
logger2.addHandler(handlerFile)



# ----------------------------------------------
# Flaskを起動する
# ----------------------------------------------
app = Flask(__name__)


@app.route('/')
def root() -> str:
    """_summary_
    return message when accessed from browser
    Returns:
        str: _description_message
    """
    return 'online ＞V(＾＾)'


@app.route('/webhook', methods=['POST'])
def webhook():
    """_summary_
    Trading viewのWebhookを受け取った後の処理
    """
    # --------------------------------------
    # 発注ロットの読み込み（固定で行う場合）
    # --------------------------------------
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

    # --------------------------------------
    # Webhookを受け取った
    # --------------------------------------
    if request.method == 'POST':
        # FlaskでPOSTされたデータをそのまま受け取るときはrequest.dataではなくrequest.get_data()を使う
        #data = request.get_data()
        print("----------------------")
        data = request.get_data(as_text=True)
        print(data)
        print('Webhook受信')

        # ----------------------------------------------------
        # メッセージ内容を振り分ける ※アラートを「@」で分ける
        # 
        # TradingViewの通知設定は以下
        # FTX@{{ticker}}@{{strategy.order.action}}@0.005@{{strategy.position_size}}
        # ----------------------------------------------------
        moji = data.split('@')[0]
        print("取引所:",moji)
        moji = data.split('@')[1]
        print("ticker:",moji)
        moji = data.split('@')[2]
        print("order:",moji)
        moji = data.split('@')[3]
        print("size:",moji)
        moji = data.split('@')[4]
        print("pos:",moji)
        print("----------------------")

        # ----------------------------------------------
        # ログ出力
        # ----------------------------------------------
        LogTime = datetime.datetime.now()
        sLogTime =  LogTime.strftime("%Y-%m-%d %H:%M:%S")
        text = sLogTime, "Webhook: ", data
        logger2.info(text)

        # ===============================================================================================
        # ★ オーダー実行処理 ★★★
        # ===============================================================================================
        moji = data.split('@')[2]
        # オーダー用格納
        sOrder = ""
        if str(moji) == "buy":
            sOrder = "buy"
        elif str(moji) == "sell":
            sOrder = "sell"
        print("order:",sOrder)
        

        # ====================================  ここから追加分 start  ==================================


        if data.split('@')[0] == "Bybit":
            print(" Bybit 処理スタート")
            # ---------------------------------------------------------
            # HTTP形式の設定
            # ---------------------------------------------------------
            endpoint = 'https://api-bybit.com'
            path = '/private/linear/order/create';
            func = '/fapi/v1/ticker/bookTicker'
            # ----------------------------------------------------------------------------------------
            # 発注処理 BTCPERP Bybit
            # --------------------------------------------------------
            if str(data.split('@')[1]) == "BTCUSDT":
                print("● 注文処理 ● BTCUSDT (Bybit)")

                # 発注ロット
                TV_lot = ""
                TV_lot = str(data.split('@')[3])
                BTC = bybit.create_order('BTCUSDT', type='market', side=sOrder, amount=str(TV_lot), price=0)
                pprint(BTC)
                # TradingViewから新規注文か、決済処理か判断する
                TV_sPosi = data.split('@')[4]
                TV_sPosi = float(TV_sPosi)

                # ---------------------------------------------------------
                # シンボルとLotの設定
                # ---------------------------------------------------------
                SYMBOL = "BTCUSDT"
                quantity = TV_lot


# ------------------------------------------------------------
        # ====================================  ここから追加分 start  ==================================
        if data.split('@')[0] == "Binance":
            print(" BINANCE 処理スタート")
            # -----------------------------------------------------------------------
            # 取引処理 Binance先物（ USD(S)-M ）USD-M Futures
            # -----------------------------------------------------------------------
            # ---------------------------------------------------------
            # HTTP形式の設定
            # ---------------------------------------------------------
            endpoint = 'https://fapi.binance.com'
            path = '/fapi/v1/order?';
            func = '/fapi/v1/ticker/bookTicker'

            # ---------------------------------------------------------
            # API設定
            # ---------------------------------------------------------

            api_key = ""
            secret_key = ""

            # --------------------------------------------------------
            # 発注処理 BTCPERP Binance
            # --------------------------------------------------------
            if str(data.split('@')[1]) == "BTCPERP":
                print("● 注文処理 ● BTCPERP (Binance)")

                # 発注ロット
                TV_lot = ""
                TV_lot = str(data.split('@')[3])


                # TradingViewから新規注文か、決済処理か判断する
                TV_sPosi = data.split('@')[4]
                TV_sPosi = float(TV_sPosi)

                # ---------------------------------------------------------
                # シンボルとLotの設定
                # ---------------------------------------------------------
                SYMBOL = "BTCUSDT"
                quantity = TV_lot



                # ---------------------------------------------------------
                # オーダー処理
                # ---------------------------------------------------------
                # 現在価格を取得する
                url_Ticker = endpoint + func + '?symbol=' + SYMBOL;
                res = requests.get(url_Ticker)
                data_Ticker = json.loads(res.text)
                # bid ask
                bid_price = data_Ticker['bidPrice']
                ask_price = data_Ticker['askPrice']
                print("bid: ",bid_price,"    ask: ",ask_price)
                # タイムスタンプを宣言
                timestamp = round(datetime.datetime.now().timestamp()) * 1000




                # ------------------------------------------------------------
                # 新規注文の場合 TV_sPosi>0はlong
                # ------------------------------------------------------------                
                if (sOrder == "buy") and (TV_sPosi > 0):
                    print("● 注文処理(Long) ● BTC-PERP")

                    # シンボルと価格の設定
                    side = "BUY"
                    price = float(ask_price)

                    # HTTP形式に引っ付ける
                    query = 'symbol=' + SYMBOL + '&side=' + side + '&price=' + str(price) +'&type=LIMIT&timeInForce=GTC'  +'&quantity=' + str(quantity) +'&timestamp=' + str(timestamp);


                # ------------------------------------------------------------
                # Longの決済
                # ------------------------------------------------------------
                if (sOrder == "sell") and (TV_sPosi == 0):
                    print("● 決済処理(buy) ● BTC-PERP")
                    side = "SELL"
                    price = float(bid_price)

                    # HTTP形式に引っ付ける
                    query = 'symbol=' + SYMBOL + '&side=' + side + '&price=' + str(price) +'&type=LIMIT&timeInForce=GTC'  +'&quantity=' + str(quantity) +'&timestamp=' + str(timestamp);



                # ------------------------------------------------------------
                # 新規注文の場合 TV_sPosi<0はShort
                # ------------------------------------------------------------                
                if (sOrder == "sell") and (TV_sPosi < 0):
                    print("● 注文処理(Short) ● BTC-PERP")

                    # シンボルと価格の設定
                    side = "SELL"
                    price = float(bid_price)

                    # HTTP形式に引っ付ける
                    query = 'symbol=' + SYMBOL + '&side=' + side + '&price=' + str(price) +'&type=LIMIT&timeInForce=GTC'  +'&quantity=' + str(quantity) +'&timestamp=' + str(timestamp);


                # ------------------------------------------------------------
                # Shortの決済
                # ------------------------------------------------------------
                if (sOrder == "buy") and (TV_sPosi == 0):
                    print("● 注文処理(Short) ● BTC-PERP")
                    side = "BUY"
                    price = float(ask_price)

                    # HTTP形式に引っ付ける
                    query = 'symbol=' + SYMBOL + '&side=' + side + '&price=' + str(price) +'&type=LIMIT&timeInForce=GTC'  +'&quantity=' + str(quantity) +'&timestamp=' + str(timestamp);

                # ------------------------------------------------------------
                # HTTP形式で送信
                # ------------------------------------------------------------
                # HTTP形式に引っ付ける
                query = 'symbol=' + SYMBOL + '&side=' + side + '&price=' + str(price) +'&type=LIMIT&timeInForce=GTC'  +'&quantity=' + str(quantity) +'&timestamp=' + str(timestamp);

                # hashセキュリティ
                signature = hmac.new(bytearray(secret_key.encode('utf-8')), query.encode('utf-8') , digestmod = hashlib.sha256 ).hexdigest()
                # HTTPとHashを引っ付ける
                url = endpoint + path + query + '&signature=' + signature
                # ヘッダーを付けて飛ばす
                headers = {
                    'X-MBX-APIKEY': api_key
                }
                res = requests.post(url, headers=headers)
                datas = json.loads(res.text)
                # オーダー通るまで少し待ち
                time.sleep(1)
                print("-----------------------------------")
                print("オーダーID:" , datas['orderId'])
                print("-----------------------------------")
                print(datas)


# ------------------------------------------------------------
            # ----------------------------------------------------------------------------------------
            # 発注処理 ETHPERP Binance
            # --------------------------------------------------------
            if str(data.split('@')[1]) == "ETHPERP":
                print("● 注文処理 ● ETHPERP (Binance)")

                # 発注ロット
                TV_lot = ""
                TV_lot = str(data.split('@')[3])

                # TradingViewから新規注文か、決済処理か判断する
                TV_sPosi = data.split('@')[4]
                TV_sPosi = float(TV_sPosi)

                # ---------------------------------------------------------
                # シンボルとLotの設定
                # ---------------------------------------------------------
                SYMBOL = "ETHUSDT"
                quantity = TV_lot



                # ---------------------------------------------------------
                # オーダー処理
                # ---------------------------------------------------------
                # 現在価格を取得する
                url_Ticker = endpoint + func + '?symbol=' + SYMBOL;
                res = requests.get(url_Ticker)
                data_Ticker = json.loads(res.text)
                # bid ask
                bid_price = data_Ticker['bidPrice']
                ask_price = data_Ticker['askPrice']
                print("bid: ",bid_price,"    ask: ",ask_price)
                # タイムスタンプを宣言
                timestamp = round(datetime.datetime.now().timestamp()) * 1000




                # ------------------------------------------------------------
                # 新規注文の場合 TV_sPosi>0はlong
                # ------------------------------------------------------------                
                if (sOrder == "buy") and (TV_sPosi > 0):
                    print("● 注文処理(Long) ● ETH-PERP")

                    # シンボルと価格の設定
                    side = "BUY"
                    price = float(ask_price)

                    # HTTP形式に引っ付ける
                    query = 'symbol=' + SYMBOL + '&side=' + side + '&price=' + str(price) +'&type=LIMIT&timeInForce=GTC'  +'&quantity=' + str(quantity) +'&timestamp=' + str(timestamp);


                # ------------------------------------------------------------
                # Longの決済
                # ------------------------------------------------------------
                if (sOrder == "sell") and (TV_sPosi == 0):
                    print("● 決済処理(buy) ● BTC-PERP")
                    side = "SELL"
                    price = float(bid_price)

                    # HTTP形式に引っ付ける
                    query = 'symbol=' + SYMBOL + '&side=' + side + '&price=' + str(price) +'&type=LIMIT&timeInForce=GTC'  +'&quantity=' + str(quantity) +'&timestamp=' + str(timestamp);



                # ------------------------------------------------------------
                # 新規注文の場合 TV_sPosi<0はShort
                # ------------------------------------------------------------                
                if (sOrder == "sell") and (TV_sPosi < 0):
                    print("● 注文処理(Short) ● BTC-PERP")

                    # シンボルと価格の設定
                    side = "SELL"
                    price = float(bid_price)

                    # HTTP形式に引っ付ける
                    query = 'symbol=' + SYMBOL + '&side=' + side + '&price=' + str(price) +'&type=LIMIT&timeInForce=GTC'  +'&quantity=' + str(quantity) +'&timestamp=' + str(timestamp);


                # ------------------------------------------------------------
                # Shortの決済
                # ------------------------------------------------------------
                if (sOrder == "buy") and (TV_sPosi == 0):
                    print("● 注文処理(Short) ● BTC-PERP")
                    side = "BUY"
                    price = float(ask_price)

                    # HTTP形式に引っ付ける
                    query = 'symbol=' + SYMBOL + '&side=' + side + '&price=' + str(price) +'&type=LIMIT&timeInForce=GTC'  +'&quantity=' + str(quantity) +'&timestamp=' + str(timestamp);




                # ------------------------------------------------------------
                # HTTP形式で送信
                # ------------------------------------------------------------
                # HTTP形式に引っ付ける
                query = 'symbol=' + SYMBOL + '&side=' + side + '&price=' + str(price) +'&type=LIMIT&timeInForce=GTC'  +'&quantity=' + str(quantity) +'&timestamp=' + str(timestamp);

                # hashセキュリティ
                signature = hmac.new(bytearray(secret_key.encode('utf-8')), query.encode('utf-8') , digestmod = hashlib.sha256 ).hexdigest()
                # HTTPとHashを引っ付ける
                url = endpoint + path + query + '&signature=' + signature
                # ヘッダーを付けて飛ばす
                headers = {
                    'X-MBX-APIKEY': api_key
                }
                res = requests.post(url, headers=headers)
                datas = json.loads(res.text)
                # オーダー通るまで少し待ち
                time.sleep(1)
                print("-----------------------------------")
                print("オーダーID:" , datas['orderId'])
                print("-----------------------------------")
                print(datas)

# ------------------------------------------------------------
            # ----------------------------------------------------------------------------------------
            # 発注処理 AVAXPERP Binance
            # --------------------------------------------------------
            if str(data.split('@')[1]) == "AVAXPERP":
                print("● 注文処理 ● AVAXPERP (Binance)")

                # 発注ロット
                TV_lot = ""
                TV_lot = str(data.split('@')[3])


                # TradingViewから新規注文か、決済処理か判断する
                TV_sPosi = data.split('@')[4]
                TV_sPosi = float(TV_sPosi)

                # ---------------------------------------------------------
                # シンボルとLotの設定
                # ---------------------------------------------------------
                SYMBOL = "AVAXUSDT"
                quantity = TV_lot



                # ---------------------------------------------------------
                # オーダー処理
                # ---------------------------------------------------------
                # 現在価格を取得する
                url_Ticker = endpoint + func + '?symbol=' + SYMBOL;
                res = requests.get(url_Ticker)
                data_Ticker = json.loads(res.text)
                # bid ask
                bid_price = data_Ticker['bidPrice']
                ask_price = data_Ticker['askPrice']
                print("bid: ",bid_price,"    ask: ",ask_price)
                # タイムスタンプを宣言
                timestamp = round(datetime.datetime.now().timestamp()) * 1000




                # ------------------------------------------------------------
                # 新規注文の場合 TV_sPosi>0はlong
                # ------------------------------------------------------------                
                if (sOrder == "buy") and (TV_sPosi > 0):
                    print("● 注文処理(Long) ● AVAX-PERP")

                    # シンボルと価格の設定
                    side = "BUY"
                    price = float(ask_price)

                    # HTTP形式に引っ付ける
                    query = 'symbol=' + SYMBOL + '&side=' + side + '&price=' + str(price) +'&type=LIMIT&timeInForce=GTC'  +'&quantity=' + str(quantity) +'&timestamp=' + str(timestamp);


                # ------------------------------------------------------------
                # Longの決済
                # ------------------------------------------------------------
                if (sOrder == "sell") and (TV_sPosi == 0):
                    print("● 決済処理(buy) ● AVAX-PERP")
                    side = "SELL"
                    price = float(bid_price)

                    # HTTP形式に引っ付ける
                    query = 'symbol=' + SYMBOL + '&side=' + side + '&price=' + str(price) +'&type=LIMIT&timeInForce=GTC'  +'&quantity=' + str(quantity) +'&timestamp=' + str(timestamp);



                # ------------------------------------------------------------
                # 新規注文の場合 TV_sPosi<0はShort
                # ------------------------------------------------------------                
                if (sOrder == "sell") and (TV_sPosi < 0):
                    print("● 注文処理(Short) ● AVAX-PERP")

                    # シンボルと価格の設定
                    side = "SELL"
                    price = float(bid_price)

                    # HTTP形式に引っ付ける
                    query = 'symbol=' + SYMBOL + '&side=' + side + '&price=' + str(price) +'&type=LIMIT&timeInForce=GTC'  +'&quantity=' + str(quantity) +'&timestamp=' + str(timestamp);


                # ------------------------------------------------------------
                # Shortの決済
                # ------------------------------------------------------------
                if (sOrder == "buy") and (TV_sPosi == 0):
                    print("● 注文処理(Short) ● AVAX-PERP")
                    side = "BUY"
                    price = float(ask_price)

                    # HTTP形式に引っ付ける
                    query = 'symbol=' + SYMBOL + '&side=' + side + '&price=' + str(price) +'&type=LIMIT&timeInForce=GTC'  +'&quantity=' + str(quantity) +'&timestamp=' + str(timestamp);

                # ------------------------------------------------------------
                # HTTP形式で送信
                # ------------------------------------------------------------
                # HTTP形式に引っ付ける
                query = 'symbol=' + SYMBOL + '&side=' + side + '&price=' + str(price) +'&type=LIMIT&timeInForce=GTC'  +'&quantity=' + str(quantity) +'&timestamp=' + str(timestamp);

                # hashセキュリティ
                signature = hmac.new(bytearray(secret_key.encode('utf-8')), query.encode('utf-8') , digestmod = hashlib.sha256 ).hexdigest()
                # HTTPとHashを引っ付ける
                url = endpoint + path + query + '&signature=' + signature
                # ヘッダーを付けて飛ばす
                headers = {
                    'X-MBX-APIKEY': api_key
                }
                res = requests.post(url, headers=headers)
                datas = json.loads(res.text)
                # オーダー通るまで少し待ち
                time.sleep(1)
                print("-----------------------------------")
                print("オーダーID:" , datas['orderId'])
                print("-----------------------------------")
                print(datas)



        # ====================================  ここから追加分  end  ==================================
# ------------------------------------------------------------
        # ====================================  ここから追加分 start  ==================================
        # -----------------------------------------------------------------------
        # 取引処理 Bitget
        # -----------------------------------------------------------------------
        if data.split('@')[0] == "Bitget":
            print(" BITGET 処理スタート")
            # ----------------------------------------------------------------------------------------
            # 発注処理 BTCPERP BITGET
            # --------------------------------------------------------
            if str(data.split('@')[1]) == "BTCUSDTPERP":
                print("● 注文処理 ● BTCPERP (BITGET)")

                # 発注ロット
                TV_lot = ""
                TV_lot = str(data.split('@')[3])

                # TradingViewから新規注文か、決済処理か判断する
                TV_sPosi = data.split('@')[4]
                TV_sPosi = float(TV_sPosi)

                # ---------------------------------------------------------
                # シンボルとLotの設定
                # ---------------------------------------------------------
                SYMBOL = "CMT_BTCUSDT"

                # ------------------------------------------------------------
                # 新規注文の場合 TV_sPosi>0はlong params={'type': '1',} 
                # ------------------------------------------------------------                
                if (sOrder == "buy") and (TV_sPosi > 0):
                    print("● 注文処理(Long) ● BTCUSDTPERP")

                    # シンボルと価格の設定
                    side = "buy"
                    # price = float(ask_price)

                    # 発注処理
                    BTC = ccxt.bitget.create_order(symbol=SYMBOL, type='market', side=sOrder, amount=str(TV_lot), params={'type': '1',})
                    pprint(BTC)


                # ------------------------------------------------------------
                # Longの決済 決済には「params={'type': '3',}」が必要
                # ------------------------------------------------------------
                if (sOrder == "sell") and (TV_sPosi == 0):
                    print("● 決済処理(buy) ● BTCUSDTPERP")
                    side = "sell"
                    # price = float(bid_price)

                    # 発注処理
                    BTC = ccxt.bitget.create_order(symbol=SYMBOL, type='market', side=sOrder, amount=str(TV_lot), params={'type': '3',})
                    pprint(BTC)



                # ------------------------------------------------------------
                # 新規注文の場合 TV_sPosi<0はShort
                # ------------------------------------------------------------                
                if (sOrder == "sell") and (TV_sPosi < 0):
                    print("● 注文処理(Short) ● BTC-PERP")

                    # シンボルと価格の設定
                    side = "SELL"
                    price = float(bid_price)

                    # HTTP形式に引っ付ける
                    query = 'symbol=' + SYMBOL + '&side=' + side + '&price=' + str(price) +'&type=LIMIT&timeInForce=GTC'  +'&quantity=' + str(quantity) +'&timestamp=' + str(timestamp);


                # ------------------------------------------------------------
                # Shortの決済
                # ------------------------------------------------------------
                if (sOrder == "buy") and (TV_sPosi == 0):
                    print("● 注文処理(Short) ● BTC-PERP")
                    side = "BUY"
                    price = float(ask_price)

                    # HTTP形式に引っ付ける
                    query = 'symbol=' + SYMBOL + '&side=' + side + '&price=' + str(price) +'&type=LIMIT&timeInForce=GTC'  +'&quantity=' + str(quantity) +'&timestamp=' + str(timestamp);



            # ----------------------------------------------------------------------------------------
            # 発注処理 ETHPERP BITGET
            # --------------------------------------------------------
            if str(data.split('@')[1]) == "ETHUSDTPERP":
                print("● 注文処理 ● ETHPERP (BITGET)")

                # 発注ロット
                TV_lot = ""
                TV_lot = str(data.split('@')[3])

                # TradingViewから新規注文か、決済処理か判断する
                TV_sPosi = data.split('@')[4]
                TV_sPosi = float(TV_sPosi)

                # ---------------------------------------------------------
                # シンボルとLotの設定
                # ---------------------------------------------------------
                SYMBOL = "CMT_ETHUSDT"

                # ------------------------------------------------------------
                # 新規注文の場合 TV_sPosi>0はlong params={'type': '1',} 
                # ------------------------------------------------------------                
                if (sOrder == "buy") and (TV_sPosi > 0):
                    print("● 注文処理(Long) ● CMT_ETHUSDT")

                    # シンボルと価格の設定
                    side = "buy"
                    # price = float(ask_price)

                    # 発注処理
                    ETH = ccxt.bitget.create_order(SYMBOL, type='market', side=sOrder, amount=str(TV_lot), params={'type': '1',})
                    pprint(ETH)


                # ------------------------------------------------------------
                # Longの決済 決済には「params={'type': '3',}」が必要
                # ------------------------------------------------------------
                if (sOrder == "sell") and (TV_sPosi == 0):
                    print("● 決済処理(buy) ● CMT_ETHUSDT")
                    side = "sell"
                    # price = float(bid_price)

                    # 発注処理
                    ETH = ccxt.bitget.create_order(SYMBOL, type='market', side=sOrder, amount=str(TV_lot), params={'type': '3',})
                    pprint(ETH)



            # ----------------------------------------------------------------------------------------
            # 発注処理 AVAXPERP BITGET
            # --------------------------------------------------------
            if str(data.split('@')[1]) == "AVAXUSDTPERP":
                print("● 注文処理 ● AVAXPERP (BITGET)")

                # 発注ロット
                TV_lot = ""
                TV_lot = str(data.split('@')[3])

                # TradingViewから新規注文か、決済処理か判断する
                TV_sPosi = data.split('@')[4]
                TV_sPosi = float(TV_sPosi)

                # ---------------------------------------------------------
                # シンボルとLotの設定
                # ---------------------------------------------------------
                SYMBOL = "CMT_AVAXUSDT"

                # ------------------------------------------------------------
                # 新規注文の場合 TV_sPosi>0はlong params={'type': '1',} 
                # ------------------------------------------------------------                
                if (sOrder == "buy") and (TV_sPosi > 0):
                    print("● 注文処理(Long) ● AVAXUSDTPERP")

                    # シンボルと価格の設定
                    side = "buy"
                    # price = float(ask_price)

                    # 発注処理
                    BTC = ccxt.Bitget.create_order(SYMBOL, type='market', side=sOrder, amount=str(TV_lot), params={'type': '1',})
                    pprint(BTC)

                    # ログ出力
                    LogTime = datetime.datetime.now()
                    sLogTime =  LogTime.strftime("%Y-%m-%d %H:%M:%S")
                    text = str(sLogTime)+"オーダー管理へ格納: "+str(query)+":"+str(TV_MagicNo)
                    logger2.info(text)
                # ------------------------------------------------------------
                # Longの決済 決済には「params={'type': '3',}」が必要
                # ------------------------------------------------------------
                if (sOrder == "sell") and (TV_sPosi == 0):
                    print("● 決済処理(buy) ● AVAXUSDTPERP")
                    side = "sell"
                    # price = float(bid_price)

                    # 発注処理
                    BTC = ccxt.Bitget.create_order(SYMBOL, type='market', side=sOrder, amount=str(TV_lot), params={'type': '3',})
                    pprint(BTC)

                    # ログ出力
                    LogTime = datetime.datetime.now()
                    sLogTime =  LogTime.strftime("%Y-%m-%d %H:%M:%S")
                    text = str(sLogTime)+"オーダー管理へ格納: "+str(query)+":"+str(TV_MagicNo)
                    logger2.info(text)

                # ------------------------------------------------------------
                # 新規注文の場合 TV_sPosi<0はShort
                # ------------------------------------------------------------                
                if (sOrder == "sell") and (TV_sPosi < 0):
                    print("● 注文処理(Short) ● AVAXUSDTPERP")

                    # シンボルと価格の設定
                    side = "SELL"
                    price = float(bid_price)

                    # HTTP形式に引っ付ける
                    query = 'symbol=' + SYMBOL + '&side=' + side + '&price=' + str(price) +'&type=LIMIT&timeInForce=GTC'  +'&quantity=' + str(quantity) +'&timestamp=' + str(timestamp);

                    # ログ出力
                    LogTime = datetime.datetime.now()
                    sLogTime =  LogTime.strftime("%Y-%m-%d %H:%M:%S")
                    text = str(sLogTime)+"オーダー管理へ格納: "+str(query)+":"+str(TV_MagicNo)
                    logger2.info(text)
                # ------------------------------------------------------------
                # Shortの決済
                # ------------------------------------------------------------
                if (sOrder == "buy") and (TV_sPosi == 0):
                    print("● 注文処理(Short) ● AVAXUSDTPERP")
                    side = "BUY"
                    price = float(ask_price)

                    # HTTP形式に引っ付ける
                    query = 'symbol=' + SYMBOL + '&side=' + side + '&price=' + str(price) +'&type=LIMIT&timeInForce=GTC'  +'&quantity=' + str(quantity) +'&timestamp=' + str(timestamp);

                    # ログ出力
                    LogTime = datetime.datetime.now()
                    sLogTime =  LogTime.strftime("%Y-%m-%d %H:%M:%S")
                    text = str(sLogTime)+"オーダー管理へ格納: "+str(query)+":"+str(TV_MagicNo)
                    logger2.info(text)

            # --------------------------------------------------------
            # 発注処理 NEARPERP BITGET
            # --------------------------------------------------------
            if str(data.split('@')[1]) == "NEARUSDTPERP":
                print("● 注文処理 ● NEARPERP (BITGET)")

                # 発注ロット
                TV_lot = ""
                TV_lot = str(data.split('@')[3])

                # TradingViewから新規注文か、決済処理か判断する
                TV_sPosi = data.split('@')[4]
                TV_sPosi = float(TV_sPosi)

                # ---------------------------------------------------------
                # シンボルとLotの設定
                # ---------------------------------------------------------
                SYMBOL = "CMT_NEARUSDT"
                quantity = TV_lot

            # --------------------------------------------------------
            # 発注処理 ATOMPERP BITGET
            # --------------------------------------------------------
            if str(data.split('@')[1]) == "ATOMUSDTPERP":
                print("● 注文処理 ● ATOMPERP (BITGET)")

                # 発注ロット
                TV_lot = ""
                TV_lot = str(data.split('@')[3])

                # TradingViewから新規注文か、決済処理か判断する
                TV_sPosi = data.split('@')[4]
                TV_sPosi = float(TV_sPosi)

                # ---------------------------------------------------------
                # シンボルとLotの設定
                # ---------------------------------------------------------
                SYMBOL = "CMT_ATOMUSDT"
                quantity = TV_lot

            # --------------------------------------------------------
            # 発注処理 BNBPERP BITGET
            # --------------------------------------------------------
            if str(data.split('@')[1]) == "BNBUSDTPERP":
                print("● 注文処理 ● BNBPERP (BITGET)")

                # 発注ロット
                TV_lot = ""
                TV_lot = str(data.split('@')[3])

                # TradingViewから新規注文か、決済処理か判断する
                TV_sPosi = data.split('@')[4]
                TV_sPosi = float(TV_sPosi)

                # ---------------------------------------------------------
                # シンボルとLotの設定
                # ---------------------------------------------------------
                SYMBOL = "CMT_BNBUSDT"
                quantity = TV_lot

        # ====================================  ここから追加分  end  ==================================

        # ====================================  ここから追加分 start  ==================================
        # -----------------------------------------------------------------------
        # 取引処理 KuCoin
        # -----------------------------------------------------------------------
        if data.split('@')[0] == "Kucoin":
            print(" KUCOIN 処理スタート")
            # --------------------------------------------------------
            # 発注処理
            # --------------------------------------------------------
            if str(data.split('@')[1]) == "BTCUSDT":
                print("● 注文処理 ● BTCPERP (Kucoin)")

                # 発注ロット
                TV_lot = ""
                TV_lot = str(data.split('@')[3])

                # TradingViewから新規注文か、決済処理か判断する
                TV_sPosi = data.split('@')[4]
                TV_sPosi = float(TV_sPosi)

                # ---------------------------------------------------------
                # シンボルとLotの設定
                # ---------------------------------------------------------
                SYMBOL = "BTC/USDT:USDT"

                # ------------------------------------------------------------
                # 新規注文の場合 TV_sPosi>0はlong 
                # ------------------------------------------------------------                
                if (sOrder == "buy") and (TV_sPosi > 0):
                    print("● 注文処理(Long) ● BTC/USDT:USDT")

                    # シンボルと価格の設定
                    side = "buy"
                    # price = float(ask_price)

                    # 発注処理
                    order_Kucoin = ccxtKucoinf.create_order(SYMBOL, 'market', str(sOrder), int(TV_lot), {'leverage': 4})
                    pprint(order_Kucoin)
                    print("発注ID:" + str(order_Kucoin['id']))


                    # ログ出力
                    LogTime = datetime.datetime.now()
                    sLogTime =  LogTime.strftime("%Y-%m-%d %H:%M:%S")
                    text = str(sLogTime)+"オーダー管理へ格納: "+str(query)+":"+str(TV_MagicNo)
                    logger2.info(text)
                # ------------------------------------------------------------
                # Longの決済 
                # ------------------------------------------------------------
                if (sOrder == "sell") and (TV_sPosi == 0):
                    print("● 決済処理(buy) ● BTC/USDT:USDT")
                    side = "sell"
                    # price = float(bid_price)

                    # 発注処理
                    order_Kucoin = ccxtKucoinf.create_order(SYMBOL, 'market', str(sOrder), int(TV_lot), {'leverage': 4})
                    pprint(order_Kucoin)
                    print("発注ID:" + str(order_Kucoin['id']))

                    # ログ出力
                    LogTime = datetime.datetime.now()
                    sLogTime =  LogTime.strftime("%Y-%m-%d %H:%M:%S")
                    text = str(sLogTime)+"オーダー管理へ格納: "+str(query)+":"+str(TV_MagicNo)
                    logger2.info(text)
        # ====================================  ここから追加分  end  ==================================

        print("----------------------")
        # ---------------------------------------------------------------------------
        # ★メッセージが取得できたらngrokに200を返す:（200okとなる）重要これないとエラー
        # ---------------------------------------------------------------------------
        # 削除しないでください
        return '', 200
    else:
        abort(400)

# ----------------------------------------------
# 初期設定
# ----------------------------------------------
if __name__ == '__main__':
    # 重要！ ngrokとポート番号をあわせる
    app.run(debug=True, port=5000)