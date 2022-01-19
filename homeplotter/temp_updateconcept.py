from homeplotter.accountdata import AccountData
import datetime

#Create a new all account
account_data1 = AccountData("./example_data/data1.csv",tag_file="./example_data/tags_nested.json")
#Default account name to the file name without the extension, use account_name parameter to override
#No need to use the tagger here, it can be applied later
account_data2 = AccountData("./example_data/data2.csv",account_name="other_data")

#The summed_account should default to use the same scaling operators when counting the summed values
summed_account = account_data1 + account_data2 / 2

#This should be some sort of property that you can query
assert(summed_account.get_scale("data1")==1) ##Returns 1
assert(summed_account.get_scale("other_data")==1/2)

#Data property 5 could be account and 6 could be unscaled amount
summed_account.get_data()[0][5]
summed_account.get_data()[0][6]

#The properties should be filterable
summed_account.filter_data("account","==","other_data")
summed_account.filter_data("original_amount","<=",100)
summed_account.reset_filter()

#??Any relevant parameters?
summed_account.save("./data/alla_konton.csv")

#Automatically detects if its an account data from the bank or from a previously summed account
summed_account = AccountData("./data/alla_konton.csv")

#Update function provided to add data to the account
#Need to specify which account the data should be added to
summed_account.update("./example_data/data_new.csv", "data1")

#Update shouldn't be used to add additional accounts. Use the __plus__ operator instead for that.
try:
    summed_account.update("./example_data/data_new.csv", "data3")
except:
    print("Data3 isn't available")

#Old and new data should be available
#Old data
summed_account.filter_data("date","==",datetime.date(2021, 1, 1))
assert(summed_account.get_column("text")==["Lorem Ipsum"])
summed_account.reset_filter()

#New data
summed_account.filter_data("date","==",datetime.date(2021, 1, 5))
assert(summed_account.get_column("text")==["New data","A2"])
summed_account.reset_filter()

#Overlapping data should be updated
summed_account.filter_data("date","==",datetime.date(2021, 1, 5))
assert(summed_account.get_column("text")==["Updated data"])
assert(summed_account.get_column("amount")==["333,33"])
summed_account.reset_filter()

summed_account.save("./data/alla_konton.csv")
