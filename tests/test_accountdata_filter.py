import os
import datetime
import pytest

from homeplotter.accountdata import AccountData

resource_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'example_data'))
cat_path = os.path.join(resource_path,"categories.json")
data_path1 = os.path.join(resource_path,"data1.csv")
data_path2 = os.path.join(resource_path,"data2.csv")

def test_filter__date():
    acc_data1 = AccountData(data_path1,cat_path)
    first_date = acc_data1.get_column("date")[0]
    next_date = acc_data1.get_column("date")[1]
    acc_data1.filter_data("date",">",first_date)

    assert(acc_data1.get_column("date")[0] == next_date)

@pytest.mark.parametrize("fun",[">",">=","==","!=","<=","<"] )
def test_filter__amount(fun):
    acc_data1 = AccountData(data_path1,cat_path)
    acc_data1.filter_data("amount",fun,200)
    for amount in acc_data1.get_column("amount"):
        if fun == ">":
            assert(amount>200)
        elif fun == ">=":
            assert(amount>=200)
        elif fun == "==":
            assert(amount==200)
        elif fun == "!=":
            assert(amount!=200)
        elif fun == "<=":
            assert(amount<=200)
        elif fun == "<":
            assert(amount<200)

def test_filter__category():
    acc_data1 = AccountData(data_path1,cat_path)
    acc_data1.filter_data("category","==","cat2")
    assert(acc_data1.get_column("category")[0]=="cat2")

def test_filter__type_ok():
    acc_data1 = AccountData(data_path1,cat_path)
    acc_data1.filter_data("amount",">",100)
    acc_data1.filter_data("amount",">",200.5)
    acc_data1.filter_data("text","!=","test")
    acc_data1.filter_data("category","==","cat1")
    acc_data1.filter_data("date",">",datetime.date(2021,1,4))

def test_filter__type_wrong():
    acc_data1 = AccountData(data_path1,cat_path)
    with pytest.raises(ValueError):
        acc_data1.filter_data("amount","==","text")
    with pytest.raises(ValueError):
        acc_data1.filter_data("date",">",2)
    with pytest.raises(ValueError):
        acc_data1.filter_data("text",">","text")
    with pytest.raises(ValueError):
        acc_data1.filter_data("category","==",datetime.date(2021,1,1))

def test_reset_filter():
    acc_data1 = AccountData(data_path1,cat_path)
    original_data = acc_data1.get_data()
    acc_data1.filter_data("amount","==",1000)
    filtered_data = acc_data1.get_data()
    acc_data1.reset_filter()
    reset_data = acc_data1.get_data()
    assert(original_data==reset_data)
    assert(reset_data!=filtered_data)

def test_filter__categories():
    acc_data = AccountData(data_path1,cat_path)
    acc_data.filter_data("category","!=","cat1")
    assert("cat1" not in acc_data.get_categories())
    acc_data.filter_data("category","==","cat3")
    assert(acc_data.get_categories()==["cat3"])

