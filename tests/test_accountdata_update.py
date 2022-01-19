import os
import datetime
import pytest

from homeplotter.accountdata import AccountData

resource_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'example_data'))
tag_nested_path = os.path.join(resource_path,"tags_nested.json")
data_path1 = os.path.join(resource_path,"data1.csv")
data_path2 = os.path.join(resource_path,"data2.csv")
data_path_new = os.path.join(resource_path,"data_new.csv")

@pytest.mark.skip(reason="Update not implemented")
def test_update():
    account_data1 = AccountData("./example_data/data1.csv",tag_file="./example_data/tags_nested.json")
    account_data2 = AccountData("./example_data/data2.csv",account_name="other_data")

    summed_account = account_data1/2 + account_data2
    summed_account.update("./example_data/data_new.csv", "data1")
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
    assert(summed_account.get_column("amount")==[333.33/2])
    summed_account.reset_filter()

@pytest.mark.skip(reason="Save/load not implemented")
def test_update_save_load():
    account_data1 = AccountData("./example_data/data1.csv",tag_file="./example_data/tags_nested.json")
    account_data2 = AccountData("./example_data/data2.csv",account_name="other_data")

    summed_account = account_data1/2 + account_data2
    summed_account.update("./example_data/data_new.csv", "data1")

    #Save and load should not affect data
    summed_account.save("./temp/account_data.csv")

    summed_account = AccountData("./temp/account_data.csv")

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
    assert(summed_account.get_column("amount")==[333.33/2])
    summed_account.reset_filter() 