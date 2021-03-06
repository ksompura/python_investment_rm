import datetime as dt
import pandas as pd
from pandas_datareader import data as pdr
import yfinance as yf
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import os
from pandas import ExcelWriter
from price_relativity import price_relativity as pr

yf.pdr_override() 
start =dt.datetime(2017,1,1)
now = dt.datetime.now()

root = Tk()
ftypes = [(".xlsm","*.xlsx",".xls")]
ttl  = "Title"
dir1 = 'C:\\'
# filePath = askopenfilename(filetypes = ftypes, initialdir = dir1, title = ttl)
filePath=r"C:\Users\Keshav Sompura\Documents\Python Projects\RichardStocks.xlsx"

stocklist = pd.read_excel(filePath)
stocklist=stocklist[:50] # WARNING remove if want to screen all stocks in list, want to check if you are allowed to scrape thousands of stock 
# print(stocklist)

export_list = pd.DataFrame(columns =["Stock", "50 Day MA", "150 Day MA", "200 Day MA", "52 Week Low", "52 Week High","Pct change 5 Day MA"]) #"52 Week Vol High"

for i in stocklist.index:
    stock = str(stocklist["Symbol"][i])



    try:
        df = pdr.get_data_yahoo(stock, start, now)
        

        sma_used = [50,150,200]
        for x in sma_used:
            sma = x
            #Find simple moving average for volume and 
            # df[f"Vol_SMA_{sma}"] = df.iloc[:,6].rolling(window=sma).mean()
            df[f"SMA_{sma}"] = round(df.iloc[:,4].rolling(window=sma).mean(),2)
            
        


        # append price relativity compared with SPY
        df["PR"] = pr(stock)
        # create new column for change in PR in percentage terms
        df["Delta_PR (%)"] = df.pct_change()["PR"] * 100
    
        # create moving average for delta price relativity
        ma = 5 # day period
        df[f"del_pr_ma_{ma}"] = round(df.iloc[:,-1].rolling(window=ma).mean(),2)

        # print(df)
        # break

        
        current_close = df["Adj Close"][-1]
        ma_50 = df["SMA_50"][-1]
        ma_150 = df["SMA_150"][-1]
        ma_200 = df["SMA_200"][-1]
        low_52_wk=min(df["Adj Close"][-260:])
        high_52_wk=max(df["Adj Close"][-260:])
        high_vol_52_wk=max(df["Volume"][-260:])
        del_pr_ma_5 = df["del_pr_ma_5"][-1]
        # current_vol = df["Volume"][-1]
        # vol_ma_50 = df["Vol_SMA_50"][-1]
        
        try:
            ma_200_20past = df["SMA_200"][-20]
            ma_200_80past = df["SMA_200"][-80]



        except Exception:
            ma_200_20past = 0
            ma_200_80past = 0

        #Condition 1: Current Price > 150 SMA and 200 SMA
        if (current_close > ma_150 and current_close > ma_200):
            cond_1 = True
        else:
            cond_1 = False
        #Condition 2: 150 SMA > 200 SMA
        if (ma_150 > ma_200):
            cond_2 = True
        else:
            cond_2 = False
        #Condtion 3: 200 SMA trending up for > 1 month (preferably 4-5 months min in most cases)
        if (ma_200 > ma_200_20past):
        # if (ma_200 > ma_200_80past):
            cond_3 = True
        else:
            cond_3 = False
        #Condtion 4: 50 SMA > 150 SMA and 50 SMA > 200 SMA
        if (ma_50 > ma_150 and ma_50 > ma_200):
            cond_4 = True
        else:
            cond_4 = False
        #Condtion 5: Current Price > 50 SMA
        if (current_close > ma_50):
            cond_5 = True
        else:
            cond_5 = False
        #Condition 6: Current Price is at least 30% above its 52 week low
        if (current_close >= 1.3*low_52_wk):
            cond_6 = True
        else:
            cond_6 = False
        #Condtion 7: Current Price within at least 25% of its 52 week high
        if (current_close >= high_52_wk*0.75):
            cond_7 = True
        else:
            cond_7 = False
        #Condition 8: Relative Strength ranking (RS ranking), as repored in Investor's Business Daily, is no less than 70 (try to figure out and program it in)
        #My version of Relative Strength compared to S&P 500 
        if (del_pr_ma_5) >= 1.5: #greater than 1.5%
            cond_8 = True
        else:
            cond_8 = False

        #Condition 9: Current volume within 10% of max volume
        # if (current_vol >= high_vol_52_wk*0.10):
        #     cond_9 = True
        # else:
        #     cond_9 = False

        if (cond_1 and cond_2 and cond_3 and cond_4 and cond_5 and cond_6 and cond_7 and cond_8): #and cond_9
            export_list = export_list.append({"Stock": stock, "50 Day MA": ma_50, "150 Day MA":ma_150, "200 Day MA":ma_200, "52 Week Low":low_52_wk, "52 Week High":high_52_wk, "Pct change 5 Day MA":del_pr_ma_5},ignore_index=True) #,"52 Week Vol High":high_vol_52_wk
        else:
            print(f"{stock} doesn't meet the criteria")
        
    except Exception:
        print(f"No data on {stock}")
        

        
print(export_list)

new_file = os.path.dirname(filePath)+ "/Screen_Output.xlsx"

writer = ExcelWriter(new_file)
export_list.to_excel(writer,"Sheet1")
writer.save()