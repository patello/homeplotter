import os
import datetime

from homeplotter.accountdata import AccountData

resource_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'example_data'))
cat_path = os.path.join(resource_path,"categories.json")
data_path1 = os.path.join(resource_path,"data1.csv")
data_path2 = os.path.join(resource_path,"data2.csv")

def test_init():
    acc_data1 = AccountData(data_path1,cat_path)
    acc_data2 = AccountData(data_path2,cat_path)

def test_categories():
    acc_data1 = AccountData(data_path1,cat_path)
    #categories property returns the categories defined in categories.json plus "Uncategorized"
    assert(list(acc_data1.categories)==['cat1', 'cat2', 'cat3', 'Uncategorized'])

def test_get_category():
    acc_data1 = AccountData(data_path1,cat_path)
    #Length of get_category should be the same as the number of cat1 ("A") expenses in data1
    assert(len(acc_data1.get_category("cat1"))==8)
    #Length of get_category("Uncategorized") should be the same as the number of uncategorized expenses in data1
    assert(len(acc_data1.get_category("Uncategorized"))==3)

def test_get_category__category_is_correct():
    acc_data1 = AccountData(data_path1,cat_path)
    #When asking for data from a category, all categories should be correct
    for data in acc_data1.get_category("cat3"):
        assert(data[2]=="cat3")

def test_get_category__is_sorted():
    #Everything should sorted ascending by the first column (date) after initialization
    acc_data1 = AccountData(data_path1,cat_path)
    
    all_data = acc_data1.get_category("cat1")
    last_date = all_data[0][0]
    for data in all_data[1:]:
        assert(data[0]>=last_date)
        last_date=data[0]

def test_add():
    acc_data1 = AccountData(data_path1,cat_path)
    acc_data2 = AccountData(data_path2,cat_path)
    sum_data = acc_data1 + acc_data2

    #Categories should not change since both acc_data use the same category file, though order may change (so sorting it)
    assert(sorted(list(acc_data1.categories))==sorted(list(sum_data.categories)))
    #Length of get_category should be the sum of both
    assert(len(sum_data.get_category("cat1"))==len(acc_data1.get_category("cat1"))+len(acc_data2.get_category("cat1")))
    assert(len(sum_data.get_category("Uncategorized"))==len(acc_data1.get_category("Uncategorized"))+len(acc_data2.get_category("Uncategorized")))

def test_add__is_sorted():
    #Everything should still be sorted ascending by the first column (date) after adding two account data
    acc_data1 = AccountData(data_path1,cat_path)
    acc_data2 = AccountData(data_path2,cat_path)
    sum_data = acc_data1 + acc_data2
    
    all_data = sum_data.get_category("cat1")
    last_date = all_data[0][0]
    for data in all_data[1:]:
        assert(data[0]>=last_date)
        last_date=data[0]

def test_get_timeseries():
    acc_data2 = AccountData(data_path2,cat_path)
    ts = acc_data2.get_timeseries("cat1")

    #The lenght of the timeseries should be the number of number of days between first and last day of data 1
    assert(len(ts)==26)

    #All dates should be present between the first and the last, an only occur once
    last_date = ts[0][0]
    for data in ts[1:]:
        assert(last_date+datetime.timedelta(1)==data[0])
        last_date = data[0]


if __name__=="__main__":
    test_init()
    test_categories()
    test_get_category()
    test_get_category__is_sorted()
    test_add()
    test_add__is_sorted()
