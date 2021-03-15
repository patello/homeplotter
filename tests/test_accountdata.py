import os
import datetime

from homeplotter.accountdata import AccountData

resource_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'example_data'))
cat_path = os.path.join(resource_path,"categories.json")
tag_path = os.path.join(resource_path,"tags.json")
data_path1 = os.path.join(resource_path,"data1.csv")
data_path2 = os.path.join(resource_path,"data2.csv")

def test_init():
    acc_data1 = AccountData(data_path1,cat_path)
    acc_data2 = AccountData(data_path2,cat_path)

def test_get_data():
    acc_data1 = AccountData(data_path1,cat_path)
    #Length of get_data should be the same as the number of cat1 ("A") expenses in data1
    assert(len(acc_data1.get_data("cat1"))==8)
    #Length of get_data("Uncategorized") should be the same as the number of uncategorized expenses in data1
    assert(len(acc_data1.get_data("Uncategorized"))==4)
    #It's ok to call get_data without any category. The lenght should be equal to the sum of length of all other categories.
    assert(len(acc_data1.get_data())==len(acc_data1.get_data("cat1"))+len(acc_data1.get_data("cat2"))+len(acc_data1.get_data("cat3"))+len(acc_data1.get_data("Uncategorized")))

def test_get_data__category_is_correct():
    acc_data1 = AccountData(data_path1,cat_path)
    #When asking for data from a category, all categories should be correct
    for data in acc_data1.get_data("cat3"):
        assert(data[2]=="cat3")

def test_get_data__is_sorted():
    #Everything should sorted ascending by the first column (date) after initialization
    acc_data1 = AccountData(data_path1,cat_path)
    
    all_data = acc_data1.get_data("cat1")
    last_date = all_data[0][0]
    for data in all_data[1:]:
        assert(data[0]>=last_date)
        last_date=data[0]

def test_add():
    acc_data1 = AccountData(data_path1,cat_path)
    acc_data2 = AccountData(data_path2,cat_path)
    sum_data = acc_data1 + acc_data2

    #Categories should not change since both acc_data use the same category file, though order may change (so sorting it)
    assert(sorted(list(acc_data1.get_categories()))==sorted(list(sum_data.get_categories())))
    #Length of get_data should be the sum of both
    assert(len(sum_data.get_data("cat1"))==len(acc_data1.get_data("cat1"))+len(acc_data2.get_data("cat1")))
    assert(len(sum_data.get_data("Uncategorized"))==len(acc_data1.get_data("Uncategorized"))+len(acc_data2.get_data("Uncategorized")))

def test_div():
    acc_data = AccountData(data_path1,cat_path)
    acc_data_div = acc_data/2

    assert(sum(acc_data.get_column("amount"))/2==sum(acc_data_div.get_column("amount")))
    assert(len(acc_data.get_data())==len(acc_data_div.get_data()))

def test_add__is_sorted():
    #Everything should still be sorted ascending by the first column (date) after adding two account data
    acc_data1 = AccountData(data_path1,cat_path)
    acc_data2 = AccountData(data_path2,cat_path)
    sum_data = acc_data1 + acc_data2
    
    all_data = sum_data.get_data("cat1")
    last_date = all_data[0][0]
    for data in all_data[1:]:
        assert(data[0]>=last_date)
        last_date=data[0]

def test_get_timeseries():
    acc_data2 = AccountData(data_path2,cat_path)
    ts = acc_data2.get_timeseries("cat1").data

    #The lenght of the timeseries should be the number of number of days between first and last day of data 1
    assert(len(ts)==26)

    #All dates should be present between the first and the last, an only occur once
    last_date = ts[0][0]
    for data in ts[1:]:
        assert(last_date+datetime.timedelta(1)==data[0])
        last_date = data[0]

def test_get_timeseries__all_categories():
    acc_data2 = AccountData(data_path2,cat_path)
    ts = acc_data2.get_timeseries("cat1").data

    #The lenght of the timeseries should be the number of number of days between first and last day of data 1
    assert(len(ts)==26)

    #All dates should be present between the first and the last, an only occur once
    last_date = ts[0][0]
    for data in ts[1:]:
        assert(last_date+datetime.timedelta(1)==data[0])
        last_date = data[0]

def test_get_timeseries__correct_sum():
    #The total expenses should not change
    acc_data1 = AccountData(data_path2,cat_path)
    sum1 = 0
    for data in acc_data1.get_data("cat1"):
        sum1+=data[1]
    sum2 = 0
    for data in acc_data1.get_timeseries("cat1").data:
        sum2+=data[1]
    
    assert(sum1==sum2)

def test_get_average():
    acc_data = AccountData(data_path1,cat_path)
    total_expenses = sum([data[1] for data in acc_data.get_data()])
    days = (acc_data.get_data()[-1][0]-acc_data.get_data()[0][0]).days +1

    assert(acc_data.get_average("Day") == total_expenses/days)
    assert(acc_data.get_average("Week") == sum([data[1] for data in acc_data.get_data()[1:-1]])/3)

def test_get_categories():
    acc_data = AccountData(data_path1,cat_path)
    assert(sorted(acc_data.get_categories())==["Uncategorized","cat1","cat2","cat3"])

def test_get_tags():
    acc_data = AccountData(data_path1,tag_file=tag_path)
    assert(sorted(acc_data.get_tags())==["tag1","tag2","tag3","överföring"])

if __name__=="__main__":
    test_init()
    test_categories()
    test_get_data()
    test_get_data__is_sorted()
    test_add()
    test_add__is_sorted()
