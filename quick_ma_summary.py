import pandas as pd
import numpy as np 
from pandas_datareader import data as pdr
import yfinance as yf
import datetime as dt

yf.pdr_override()

stock=input("Enter a stock ticker symbol: ")

start_year = 2019
start_month = 1
start_day = 1

start = dt.datetime(start_year, start_month, start_day)
now = dt.datetime.now()


# grab summary from yahoo finance
df = pdr.get_data_yahoo(stock, start, now)
# print(df)


# make a moving average
ma = 50 # 50 day moving average

sma_string = f"Sma_ {ma}" #name of moving average column

df[sma_string] = df.iloc[:,4].rolling(window=ma).mean() #create/ append the simple moving avg column

# print(df)

df = df.iloc[ma:] #removes first 50 values because the moving average is still being calculated
# print(df)

for i in df.index: #index is the particular date, so loop through each day
    print(df["Adj Close"][i]) #prints the adjusted close price of each day

for i in df.index:
    print(df[sma_string][i])

# Tally up how many days the close was higher and lower than the 50 day moving average
close_h = 0
close_l = 0
for i in df.index:
    if(df["Adj Close"][i] > df[sma_string][i]):
        print("The close is higher")
        close_h += 1
    else:
        print("The close is lower")
        close_l += 1

# Get a quick glance at the closing price vs moving average
print(f"Days adj close price was greater than moving avg: {close_h}")
print(f"Days adj close price was less than moving avg: {close_l}")