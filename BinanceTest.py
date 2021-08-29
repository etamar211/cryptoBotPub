import os
import sys
import time
import apprise
from binance.client import Client
from binance.enums import *
from binance.exceptions import BinanceAPIException, BinanceOrderException

f = open("log.txt", "a")
f1 = open("SaleAndBuylog.txt", "a")

apobj = apprise.Apprise()
isokay = apobj.add('discord link here')

apobjLog = apprise.Apprise()
isokay = apobjLog.add('discord link here')

#api key and secret key.
api_key = "api_key here"
api_sk = "api sk here"

#Initiate Client
client = Client(api_key, api_sk)

btt_balance = float(client.get_asset_balance(asset='BTT')['free']) - 82896
#btt_balance = 0

usdt_balance = float(client.get_asset_balance(asset='USDT')['free'])
#usdt_balance = 0

#Constants
SYMBOL = "BTTUSDT"
HIGHEST_PRICE_DEFAULT = -1
LOWEST_PRICE_DEFAULT = 999999


crtPrice = float(client.get_symbol_ticker(symbol=SYMBOL)['price'])
prvPrice = crtPrice

lastOrderPrice = 0.0033773
highestPrice = HIGHEST_PRICE_DEFAULT
lowestPrice = LOWEST_PRICE_DEFAULT

state = 0 #0 is buy, 1 is sell

counter = 0
idleForInMinutes = 0
day = 0

while 1:
    try:
        usdt_balance = float(client.get_asset_balance(asset='USDT')['free'])
        btt_balance = float(client.get_asset_balance(asset='BTT')['free']) - 82896
        crtPrice = float(client.get_symbol_ticker(symbol=SYMBOL)['price'])
        
    except BinanceAPIException as e:
        # error handling goes here
        print(e)
        apobj.notify(body="Exception")
        time.sleep(1)
        client = Client(api_key, api_sk)
        continue
        
    except Exception as e:
        # error handling goes here
        print("Get Price and Currency:\n")
        print(e)
        apobjLog.notify(body= "Get Price and Currency Exception")
        time.sleep(1)
        client = Client(api_key, api_sk)
        continue
        
    
    print(str(crtPrice) + " h: " + str(highestPrice) + " l:" + str(lowestPrice))
    f.write(str(crtPrice) + " h: " + str(highestPrice) + " l:" + str(lowestPrice) + " lop:" + str(lastOrderPrice) + " c:" + str(idleForInMinutes) + "\n")
    
    if (crtPrice > lowestPrice + 0.00001) and state == 0 and crtPrice > prvPrice:
        #hold
        
        if crtPrice < (lastOrderPrice - 0.00004):
            #buy
            try:
            
                order = client.order_limit_buy(
                    symbol=SYMBOL,
                    quantity= int((usdt_balance / crtPrice)),
                    price= str(crtPrice))
                    
            except BinanceAPIException as e:
                # error handling goes here
                print(e)
                apobj.notify(body=e)
                exit(1)
                
            except BinanceOrderException as e:
                # error handling goes here
                print(e)
                apobj.notify(body=e)
                exit(1)
                
            except Exception as e:
                # error handling goes here
                print("BUY:\n")
                print(e)
                apobj.notify(body=e)
                exit(1)
            
            lastOrderPrice = crtPrice
            state = 1
            highestPrice = crtPrice
            print("b " + str(crtPrice) + " " + str(btt_balance) + " " + str(usdt_balance))
            f.write("b " + str(crtPrice) + " " + str(btt_balance) + " " + str(usdt_balance) + " " + str(day) + "\n")
            f1.write("b " + str(crtPrice) + " " + str(btt_balance) + " " + str(usdt_balance) + " " + str(day) + "\n")
            
            try:
            
                apobj.notify(body= ("b " + str(crtPrice) + " " + str(btt_balance) + " " + str(usdt_balance) + " " + str(day) + "\n"))
                
            except Exception as e:
                # error handling goes here
                print("BUY NOTIFY:\n")
                print(e)
                apobj.notify(body=e)
                exit(1)
            
            idleForInMinutes = 0
        
        else: 
            idleForInMinutes = idleForInMinutes + 1
            if crtPrice > highestPrice:
                highestPrice = crtPrice
                
    elif (crtPrice < highestPrice - 0.00001) and state == 1 and crtPrice < prvPrice:
        #hold
                
        if crtPrice > (lastOrderPrice + 0.00004):
            #sell
            try:
                order = client.order_limit_sell(
                    symbol=SYMBOL,
                    quantity= int(btt_balance),
                    price= str(crtPrice))
                    
            except BinanceAPIException as e:
                # error handling goes here
                print(e)
                apobj.notify(body=e)
                exit(1)
                
            except BinanceOrderException as e:
                # error handling goes here
                print(e)
                apobj.notify(body=e)
                exit(1)
            
            except Exception as e:
                # error handling goes here
                print("SELL:\n")
                print(e)
                apobj.notify(body=e)
                exit(1)
            
            lastOrderPrice = crtPrice
            state = 0
            lowestPrice = crtPrice
            print("s " + str(crtPrice) + " " + str(btt_balance) + " " + str(usdt_balance))
            f.write("s " + str(crtPrice) + " " + str(btt_balance) + " " + str(usdt_balance) + " " + str(day) + "\n")
            f1.write("s " + str(crtPrice) + " " + str(btt_balance) + " " + str(usdt_balance) + " " + str(day) + "\n")
            
            try:
            
                apobj.notify(body= ("s " + str(crtPrice) + " " + str(btt_balance) + " " + str(usdt_balance) + " " + str(day) + "\n"))
                
            except Exception as e:
                # error handling goes here
                print("SELL NOTIFY:\n")
                print(e)
                apobj.notify(body=e)
                exit(1)
            
            idleForInMinutes = 0
            haventBoughtFor = 0
            
        else:
            idleForInMinutes = idleForInMinutes + 1
            if crtPrice < lowestPrice:
                lowestPrice = crtPrice
    
    elif crtPrice > highestPrice:
        highestPrice = crtPrice
        idleForInMinutes = idleForInMinutes + 1

    elif crtPrice < lowestPrice:
        lowestPrice = crtPrice
        idleForInMinutes = idleForInMinutes + 1
    
    if idleForInMinutes == 600 and state == 1:
        lastOrderPrice = crtPrice - 0.001
        lowestPrice = LOWEST_PRICE_DEFAULT
        highestPrice = HIGHEST_PRICE_DEFAULT
    
    if idleForInMinutes > 40 and state == 0 and crtPrice > lastOrderPrice + 0.001:
        lastOrderPrice = crtPrice + 0.10
        lowestPrice = LOWEST_PRICE_DEFAULT
        highestPrice = HIGHEST_PRICE_DEFAULT

    try:
    
        apobjLog.notify(body= (str(crtPrice) + " h: " + str(highestPrice) + " l:" + str(lowestPrice)  + " lop:" + str(lastOrderPrice) + " c:" + str(idleForInMinutes)))
    
    except Exception as e:
        # error handling goes here
        print("LOG:\n")
        print(e)
        apobj.notify(body=e)
        exit(1)
        
    prvPrice = crtPrice
    counter = counter + 1
    if counter % 1440 == 0:
        day = day + 1
        time.sleep(57)
        
    elif counter == 0:
        
        time.sleep(50)
    
    else:
        time.sleep(57)

print(str(usdt_balance) + " " + str(btt_balance) + " " + str(idleForInMinutes) + "\n")
f.close()
f1.close()
