import os
import datetime
import pytest

from homeplotter.accountdata import AccountData
from homeplotter.timeseries import TimeSeries

resource_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'example_data'))
cat_path = os.path.join(resource_path,"categories.json")
tag_path = os.path.join(resource_path,"tags.json")
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

def test_filter__type_ok():
    acc_data1 = AccountData(data_path1,cat_path)
    acc_data1.filter_data("amount",">",100)
    acc_data1.filter_data("amount",">",200.5)
    acc_data1.filter_data("text","!=","test")
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
    
def test_filter__tags():
    acc_data = AccountData(data_path1,tag_file=tag_path)
    acc_data.filter_data("tags","!=","tag1")
    assert("tag1" not in acc_data.get_tags())
    acc_data.filter_data("tags","==","tag3")
    assert(acc_data.get_tags()==["tag3"])

def test_filter__multi_tags():
    #If a data point has multiple tags, those tags should be preserved
    acc_data = AccountData(data_path1,tag_file=tag_path)
    acc_data.filter_data("tags","==","överföring")
    assert(len(acc_data.get_tags())>1)

def test_filter__tag_list():
    acc_data = AccountData(data_path1,tag_file=tag_path)
    acc_data.filter_data("tags","==",["tag1","överföring"])
    #Should only contain the once that contains all the tags.
    assert(sorted(acc_data.get_tags())==sorted(["tag1","överföring"]))

def test_filter__tag_list_order():
    acc_data = AccountData(data_path1,tag_file=tag_path)
    #If the order of the tags is different, then it should still yield the same result
    acc_data.filter_data("tags","==",["överföring","tag1"])
    #Should only contain the once that contains all the tags.
    assert(sorted(acc_data.get_tags())==sorted(["tag1","överföring"]))

def test_filter__multi_tags_list():
    #When filtering with a list, only the tags with that litteral list should kept
    acc_data = AccountData(data_path1,tag_file=tag_path)
    acc_data.filter_data("tags","==",["överföring"])
    assert(acc_data.get_tags()==["överföring"])

def test_filter__tag_empty():
    acc_data = AccountData(data_path1,tag_file=tag_path)
    #Should only return those that lack any tags.
    acc_data.filter_data("tags","==",[])
    assert(acc_data.get_tags()==[])
    assert(len(acc_data.get_data())>0)

def test_filter__not_tag_list():
    acc_data = AccountData(data_path1,tag_file=tag_path)
    acc_data.filter_data("tags","!=",["tag1","överföring"])
    #Should still contain överföring, just not any that also tag1
    assert("överföring" in acc_data.get_tags())

def test_filter__not_tag_empty():
    acc_data = AccountData(data_path1,tag_file=tag_path)
    #Should only return those that has tags
    acc_data.filter_data("tags","!=",[])
    assert(all(len(tags)>0 for tags in acc_data.get_column("tags")))

def test_filter__empty():
    #If filtering twice with an inverted filter the result should be empty
    acc_data = AccountData(data_path1,cat_path)
    acc_data.filter_data("amount",">=",300)
    acc_data.filter_data("amount","<",300)
    assert(len(acc_data.get_data())==0)
    #Tags should also be empty
    assert(len(acc_data.get_tags())==0)
    #It should be possible to still call get_timeseries()
    assert(type(acc_data.get_timeseries())==TimeSeries)

