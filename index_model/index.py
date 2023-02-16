import datetime as dt
import pandas as pd

class IndexModel:
    def __init__(self) -> None:
        self.df_prices = pd.read_csv("data_sources/stock_prices.csv") #Importing the csv
        self.index_level = 100.0    #Initial index level or the first price for the index
        self.df_prices["Date"] = pd.to_datetime(self.df_prices["Date"],infer_datetime_format=True)
        self.df_index = self.df_prices["Date"]  #initializing a variable to later updated as dataframe
        self.weights = [0.5,0.25,0.25]  #Our weights to be assigned to first, second and third stock
        self.shares_outstanding = 1 #Initializing the variable for shares outstanding. since same value, we can insert 1 here.
        pass

    def calc_index_level(self, start_date: dt.date, end_date: dt.date) -> None:
        #Adjusting the stock price dataframe to the start and end date
        stock_prix_new =  self.df_prices[(self.df_prices['Date'] <= pd.to_datetime(end_date)) & (self.df_prices["Date"] >= pd.to_datetime(start_date))].reset_index()
        stock_prix_new.set_index("Date",inplace=True)
        #Initialising a variable for a switch. Initially we use the index level for the first month. Later once i rises with the month, we have a function to update the indexlevel variable.
        i = 0
        index_val_list = [] #empty list for storing the index values.
        
        for month,data in stock_prix_new.groupby(pd.Grouper(freq='M')): #grouping by Month
            #checking the last business day of last month and obtaining the stocks with top 3 market capitalizations. 
            #Since the shares outstanding 
            last_business_dict = self.df_prices.iloc[data["index"][0]-1].to_dict() 
            del last_business_dict["Date"]
            stocks_new = [x for x,y in sorted(last_business_dict.items(), key=lambda item: -1*item[1]*self.shares_outstanding)[:3]]
            data_modified = data[stocks_new]
            #Updating the index value by taking the past choice of 3 shares, computing the change in shares between the first business day of current and last month for return.
            if i!=0:
                stocks = list(data_triplet.keys())
                self.index_level = (self.weights[0]*data[stocks[0]][0]/data_triplet[stocks[0]] + self.weights[1]*data[stocks[1]][0]/data_triplet[stocks[1]] + self.weights[2]*data[stocks[2]][0]/data_triplet[stocks[2]])*self.index_level
            data_triplet = {} #making a dict for storing the current choice of shares.
            for stock in stocks_new:
                data_triplet[stock] = data_modified[stock][0]
                data_modified[stock] = data_modified[stock]/data_triplet[stock] #updating the values in stock prices by their ratios from first day.
            index_val_list += list((self.weights[0]*data_modified[stocks_new[0]] + self.weights[1]*data_modified[stocks_new[1]] + self.weights[2]*data_modified[stocks_new[2]])*self.index_level)
            i += 1
        #updating the index values and rounding them to 2 significant decimals.
        stock_prix_new["index_level"] = [round(x,2) for x in index_val_list]
        self.df_index = stock_prix_new["index_level"].reset_index()
        self.df_index["Date"] = self.df_index["Date"].apply(lambda x: x.strftime('%Y-%m-%d'))
        pass

    def export_values(self, file_name: str) -> None:
        # Simply use the tocsv function of pandas
        self.df_index.to_csv(file_name, index=False)
