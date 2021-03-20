import pandas as pd
import numpy as np 
from pandas_datareader import data as pdr
import yfinance as yf
import datetime as dt

# Says which portion of MACD we are in
# Richard Moglen calls it Red White Blue (RWB)
# Goal: Backtest Red white blue strategy (for leveraged ETFs)
# Red: short - term exponential moving average
# Blue: long - term exponential moving average
# Enter when Red crosses above blue line
# Exit when Red falls below blue line


yf.pdr_override()

stock=input("Enter a stock ticker symbol: ")

start_year = 2021
start_month = 1
start_day = 1

end_year = 2019
end_month = 5
end_day = 24

start = dt.datetime(start_year, start_month, start_day)
end = dt.datetime(end_year, end_month, end_day)
now = dt.datetime.now()

df = pdr.get_data_yahoo(stock, start, now)

# ma = 50 # 50 day moving average

# sma_string = f"Sma_ {ma}" #name of moving average column

# df[sma_string] = df.iloc[:,4].rolling(window=ma).mean() #create/ append the simple moving avg column

# create list of exponential moving day average periods
emas = [3,5,8,10,12,15,30,35,40,45,50,60] #short term: 3 to 15, long term: 30 to 60
for x in emas:
    ema=x
    df[f"Ema_{ema}"] = round(df.iloc[:,4].ewm(span=ema, adjust=False).mean(), 2) #.ewm() makes an exponential moving average

# print(df)

pos = 0 #We are entered if pos = 1, not entered if pos = 0
num = 0 # Keep track how number of trades
percent_change = [] # will help keep track of percentage change in results

for i in df.index: 
    # find the min of the short term exponential moving averages
    cmin = min(df["Ema_3"][i],df["Ema_5"][i],df["Ema_8"][i],df["Ema_10"][i],df["Ema_12"][i],df["Ema_15"][i])
    # find the max of the long term exponential moving averages
    cmax = max(df["Ema_30"][i],df["Ema_35"][i],df["Ema_40"][i],df["Ema_45"][i],df["Ema_50"][i],df["Ema_60"][i])

    close = df["Adj Close"][i] # grabs the close price at the date in the iteration

    if(cmin > cmax):
        print("Red White Blue")
        if(pos == 0):
            bp = close # bp means buy price
            pos = 1 # make a buy order
            print(f"Buying now at {bp}")

    elif(cmin < cmax):
        print("Blue White Red")
        if(pos == 1):
            sp = close
            pos = 0
            print(f"Selling now at {bp}")
            pc = (sp / bp - 1)* 100 # calculate percent gain or loss when exiting our position
            percent_change.append(pc)
    if (num ==df["Adj Close"].count()-1 and pos == 1): # checks if at the end of the dataframe we still are entered in a position. If we are we want to exit to calculate final gain or loss
        sp = close
        pos = 0
        print(f"Selling now at {bp}")
        pc = (sp / bp - 1)* 100 # calculate percent gain or loss when exiting our position
        percent_change.append(pc)

print(percent_change)

gains = 0
ng = 0 #number of gains
losses = 0
nl = 0 #number of losses
total_return = 1 # will be used to calculate total return
return_list =[]

#loop through each trade and see if it one or lost
for i in percent_change:
    if (i>0):
        gains += i 
        ng += 1
    else:
        losses += i
        nl += 1
    total_return=total_return*((i/100)+1)
    return_list.append(total_return)
    


total_return = round((total_return-1)*100, 2) # remove the inital portion of move invested to see total capital gains or losses only
returns = list(map(lambda x: f"{round((x-1)*100,2)}%", return_list))



# calculate average gain and average loss
if ng > 0:
    avg_gain = gains/ng
    max_return = str(max(percent_change))
else:
    avg_gain = 0
    max_return = "undefined"

if nl > 0:
    avg_loss = losses/nl
    max_loss = str(min(percent_change))
    ratio = str(-avg_gain/avg_loss) # risk to reward ratio
else:
    avg_loss = 0
    max_loss = "undefined"
    ratio = "infinite"

# calculate batting average (% of times it was a winning trade)
if ng > 0 or nl > 0:
    batting_avg = ng/(ng+nl)
else:
    batting_avg = 0


print(f"Results for {stock} going back to {df.index[0]}, Sample size: {ng+nl} trades")
print(f"EMAs used: {emas}")
print(f"Batting Avg: {batting_avg}")
print(f"Gain/loss ratio: {ratio}")
print(f"Average Gain: {avg_gain}")
print(f"Average Loss: {avg_loss}")
print(f"Max Return: {max_return}")
print(f"Max Loss: {max_loss}")
print(f"Total return over {ng+nl} trades: {total_return}%" )
print(f"Each trade return: {returns}")
