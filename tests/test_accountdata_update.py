import os
import datetime
import pytest

from homeplotter.accountdata import AccountData

resource_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'example_data'))
tag_nested_path = os.path.join(resource_path,"tags_nested.json")
data_path1 = os.path.join(resource_path,"data1.csv")
data_path2 = os.path.join(resource_path,"data2.csv")
data_path_new = os.path.join(resource_path,"data_new.csv")

def test_update():
    account_data1 = AccountData("./example_data/data1.csv",tag_file="./example_data/tags_nested.json")
    account_data2 = AccountData("./example_data/data2.csv",account_name="other_data")

    summed_account = account_data1/2 + account_data2
    summed_account.update("./example_data/data_new.csv", "data1")
    #Old and new data should be available

    #Old data
    summed_account.filter_data("date","==",datetime.date(2021, 1, 1))
    assert(summed_account.get_column("text")==["Lorem Ipsum","Lorem Ipsum"])
    summed_account.reset_filter()

    #New data
    summed_account.filter_data("date","==",datetime.date(2021, 1, 5))
    assert(summed_account.get_column("text")==["A1","SWISH FRÅN Namn"])
    summed_account.reset_filter()

    #Overlapping data should be updated
    summed_account.filter_data("date","==",datetime.date(2021, 1, 4))
    assert(summed_account.get_column("text")==['201229 A1', '201230 A3 ', '210101 B1', '210102 a4', 'Updated data'])
    #Last one is the new data (not reliable so change if it starts failing)
    #summed_account.filter_data("account" == "other_data")
    assert(summed_account.get_column("amount")[-1]==333.33/2)
    summed_account.reset_filter()

def test_update__daterange():
    account_data1 = AccountData("./example_data/data1.csv",tag_file="./example_data/tags_nested.json")
    account_data2 = AccountData("./example_data/data2.csv",account_name="other_data")

    summed_account = account_data1 + account_data2/2
    old_range = summed_account._daterange

    summed_account.update("./example_data/data_new.csv", "other_data")
    new_range = summed_account._daterange

    #Start date is same
    assert(old_range[0]==new_range[0])
    #New date range is longer however
    assert(old_range[1]<new_range[1])

def test_update__save_load(tmp_path):
    account_data1 = AccountData("./example_data/data1.csv",tag_file="./example_data/tags_nested.json")
    account_data2 = AccountData("./example_data/data2.csv",account_name="other_data")

    summed_account = account_data1/2 + account_data2
    summed_account.update("./example_data/data_new.csv", "data1")
    
    #Save and load should not affect data
    summed_account.save(tmp_path/"account_data.csv")

    summed_account = AccountData(tmp_path/"account_data.csv")

    #Old data
    summed_account.filter_data("date","==",datetime.date(2021, 1, 1))
    assert(summed_account.get_column("text")==['Lorem Ipsum', 'Lorem Ipsum'])
    summed_account.reset_filter()

    #New data
    summed_account.filter_data("date","==",datetime.date(2021, 1, 5))
    assert(summed_account.get_column("text")==['A1', 'SWISH FRÅN Namn'])
    summed_account.reset_filter()

    #Overlapping data should be updated
    summed_account.filter_data("date","==",datetime.date(2021, 1, 4))
    assert(summed_account.get_column("text")==['201229 A1', '201230 A3 ', '210101 B1', '210102 a4', 'Updated data'])
    summed_account.filter_data("account","==","data1")
    assert(summed_account.get_column("amount")==[333.33/2])
    summed_account.reset_filter() 