# Create price relativity condition based on S&P 500
# moving average of price relativity close price 5 or 10 day period, create in stock_screener
import datetime as dt
import pandas as pd
from pandas_datareader import data as pdr
import yfinance as yf


def price_relativity(stock,year=2017,month=1,day=1):
    
    #set date range
    yf.pdr_override() 
    start =dt.datetime(year,month,day)
    now = dt.datetime.now()

    # Grab stock data for calculation
    df_stock = pdr.get_data_yahoo(stock, start, now)
    df_index = pdr.get_data_yahoo("SPY", start, now)
   
    # Create Price relativity column
    price_relativity = df_stock["Adj Close"] / df_index["Adj Close"]
    return price_relativity

    # make a moving average
# ma = 20 # 20 day moving average

# sma_string = f"PR_Sma_{ma}" #name of moving average column

# df[sma_string] = df.iloc[:,4].rolling(window=ma).mean() #create/ append the simple moving avg column
price_relativity("MVIS")
