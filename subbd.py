import logging
from binance_f import SubscriptionClient, RequestClient
from binance_f.constant.test import *
from binance_f.model import *
from binance_f.exception.binanceapiexception import BinanceApiException
import pandas as pd
import numpy as np
from pandas_datareader import data
import matplotlib.pyplot as plt
import requests, json, time, threading, ccxt, datetime
from binance_f.base.printobject import *

logger = logging.getLogger("binance-futures")
logger.setLevel(level=logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

request_client = RequestClient(api_key=g_api_key, secret_key=g_secret_key)
sub_client = SubscriptionClient(api_key=g_api_key, secret_key=g_secret_key)
sch = 0
tima = []
def callback(data_type: 'SubscribeMessageType', event: 'any'):
    time1 = datetime.datetime.fromtimestamp(request_client.get_servertime()['serverTime']/1000)
    if data_type == SubscribeMessageType.RESPONSE:
        print("Event ID: ", event)
    elif  data_type == SubscribeMessageType.PAYLOAD:
        print("Event type: ", event.eventType)
        print("Event time: ", event.eventTime)
        print("transaction time: ", event.transactionTime)
        print("Symbol: ", event.symbol)
        print("first update Id from last stream: ", event.firstUpdateId)
        print("last update Id from last stream: ", event.lastUpdateId)
        print("last update Id in last stream: ", event.lastUpdateIdInlastStream)
        print("=== Bids ===")
        PrintMix.print_data(event.bids)
        print("===================")
        print("=== Asks ===")
        PrintMix.print_data(event.asks)
        print("===================")
        cpr = round(float(request_client.get_mark_price(symbol="BTCUSDT")['markPrice']),2)
        bidsarrayp = []
        bidsarrayq = []
        pricearray = []
        asksarrayp = []
        asksarrayq = []
        for idx, row in enumerate(event.bids):
            members = [attr for attr in dir(row) if not callable(attr) and not attr.startswith("__")]
            for member_def in members:
                val_str = str(getattr(row, member_def))
                if member_def == "price":
                    bidsarrayp.append(val_str)
                else:
                    bidsarrayq.append(val_str)
            pricearray.append(str(cpr))
        for idx, row in enumerate(event.asks):
            members = [attr for attr in dir(row) if not callable(attr) and not attr.startswith("__")]
            for member_def in members:
                val_str = str(getattr(row, member_def))
                if member_def == "price":
                    asksarrayp.append(val_str)
                else:
                    asksarrayq.append(val_str)
        d = 0
        d = {"Bid_Price":pd.Series(bidsarrayp), "Bid_Quantity":pd.Series(bidsarrayq), "Ask_Price":pd.Series(asksarrayp), "Ask_Quantity":pd.Series(asksarrayq), "Current_Price":pd.Series(pricearray)}
        df = pd.DataFrame(d)
        ordertxt = open("orders.txt", "a")
        i = 0
        while i < 20:
            ordertxt.write(str(df['Bid_Price'][i]))
            ordertxt.write(" ")
            ordertxt.write(str(df['Bid_Quantity'][i]))
            ordertxt.write(" ")
            ordertxt.write(str(df['Ask_Price'][i]))
            ordertxt.write(" ")
            ordertxt.write(str(df['Ask_Quantity'][i]))
            ordertxt.write(" ")
            ordertxt.write(str(df['Current_Price'][i]))
            ordertxt.write("\n")
            i += 1
        ordertxt.close()
        #Push to GitHub
        user = "Stuffman"
        password = "Boryan1999"
        g = Github(user,password)
        repo = g.get_user().get_repo('test')
        file_list = ['orders.txt']
        file_names = ['orders.txt']
        commit_message = 'Fuck you'
        master_ref = repo.get_git_ref('heads/master')
        master_sha = master_ref.object.sha
        base_tree = repo.get_git_tree(master_sha)
        element_list = list()
        for i, entry in enumerate(file_list):
            with open(entry) as input_file:
                data = input_file.read()
                element = InputGitTreeElement(file_names[i], '100644', 'blob', data)
                element_list.append(element)
        tree = repo.create_git_tree(element_list, base_tree)
        parent = repo.get_git_commit(master_sha)
        commit = repo.create_git_commit(commit_message, tree, [parent])
        master_ref.edit(commit.sha)
        sch += 1
        time2 = datetime.datetime.fromtimestamp(request_client.get_servertime()['serverTime']/1000)
        tima.append(time1)
        tima.append(time2)
        if sch == 4:
            sub_client.unsubscribe_all()
            print(tima)
    else:
        print("Unknown Data:")
    print()


def error(e: 'BinanceApiException'):
    print(e.error_code + e.error_message)

# Valid limit values are 5, 10, or 20 
sub_client.subscribe_book_depth_event("btcusdt", 20, callback, error, update_time=UpdateTime.FAST)
#sub_client.subscribe_book_depth_event("btcusdt", 20, callback, error, update_time=UpdateTime.NORMAL)
#sub_client.subscribe_book_depth_event("btcusdt", 10, callback, error)
