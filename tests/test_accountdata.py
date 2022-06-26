import os
import datetime
import pytest

from homeplotter.accountdata import AccountData

resource_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'example_data'))
tag_path = os.path.join(resource_path,"tags.json")
tag_nested_path = os.path.join(resource_path,"tags_nested.json")
data_path1 = os.path.join(resource_path,"data1.csv")
data_path2 = os.path.join(resource_path,"data2.csv")

def test_init():
    acc_data1 = AccountData(data_path1)
    acc_data2 = AccountData(data_path2,tag_nested_path)

def test_get_data():
    acc_data1 = AccountData(data_path1)
    #Check that data corresponds to the first entry
    assert(acc_data1.get_data()[0][acc_data1.columns['amount']] == 100)
    #And that lenght is correct
    assert(len(acc_data1.get_data()) == 20)

def test_get_data__is_sorted():
    #Everything should sorted ascending by the first column (date) after initialization
    acc_data1 = AccountData(data_path1)
    
    all_data = acc_data1.get_data()
    last_date = all_data[0][0]
    for data in all_data[1:]:
        assert(data[0]>=last_date)
        last_date=data[0]

def test_add():
    acc_data1 = AccountData(data_path1,tag_nested_path)
    acc_data2 = AccountData(data_path2,tag_nested_path)
    sum_data = acc_data1 + acc_data2

    #Categories should not change since both acc_data use the same tag file, though order may change (so sorting it)
    assert(sorted(list(acc_data1.get_tags()))==sorted(list(sum_data.get_tags())))
    #Length of get_data should be the sum of both
    assert(len(sum_data.get_data())==len(acc_data1.get_data())+len(acc_data2.get_data()))

def test_div():
    acc_data = AccountData(data_path1)
    acc_data_div = acc_data/2

    assert(sum(acc_data.get_column("amount"))/2==sum(acc_data_div.get_column("amount")))
    assert(len(acc_data.get_data())==len(acc_data_div.get_data()))

def test_div__property():
    acc_data1 = AccountData(data_path1,tag_nested_path)
    acc_data2 = AccountData(data_path2,tag_nested_path,account_name="other_data")

    summed_account = acc_data1 + acc_data2/2

    #Use the account name to get the scale of the account, either using the file name, or account name if given
    assert(summed_account.get_scale("data1")==1)
    assert(summed_account.get_scale("other_data")==1/2)

    amount_col = summed_account.columns["amount"]
    amount_unscaled = summed_account.columns["amount_unscaled"]
    account_col = summed_account.columns["account"]

    assert(
        summed_account.get_data()[0][amount_col] == 
        summed_account.get_data()[0][amount_unscaled]
        *summed_account.get_scale(summed_account.get_data()[0][account_col])
        )

def test_add__is_sorted():
    #Everything should still be sorted ascending by the first column (date) after adding two account data
    acc_data1 = AccountData(data_path1)
    acc_data2 = AccountData(data_path2)
    sum_data = acc_data1 + acc_data2
    
    all_data = sum_data.get_data()
    last_date = all_data[0][0]
    for data in all_data[1:]:
        assert(data[0]>=last_date)
        last_date=data[0]

def test_get_timeseries():
    acc_data2 = AccountData(data_path2)
    ts = acc_data2.get_timeseries().data

    #The lenght of the timeseries should be the number of number of days between first and last day of data 1
    assert(len(ts)==26)

    #All dates should be present between the first and the last, an only occur once
    last_date = ts[0][0]
    for data in ts[1:]:
        assert(last_date+datetime.timedelta(1)==data[0])
        last_date = data[0]

def test_get_timeseries__correct_sum():
    #The total expenses should not change
    acc_data1 = AccountData(data_path2)
    sum1 = 0
    for data in acc_data1.get_data():
        sum1+=data[1]
    sum2 = 0
    for data in acc_data1.get_timeseries().data:
        sum2+=data[1]
    
    assert(sum1==sum2)

def test_get_average():
    acc_data = AccountData(data_path1)
    total_expenses = sum([data[1] for data in acc_data.get_data()])
    days = (acc_data.get_data()[-1][0]-acc_data.get_data()[0][0]).days +1

    assert(acc_data.get_average("Day") == total_expenses/days)
    assert(acc_data.get_average("Week") == sum([data[1] for data in acc_data.get_data()[1:-1]])/3)

def test_get_average__empty():
    #Should return 0 if there is no data
    acc_data = AccountData(data_path1,tag_nested_path)
    acc_data.filter_data("tags","==","Non-existing")
    assert(acc_data.get_average("Day")==0)

def test_get_average__filtered():
    acc_data = AccountData(data_path1,tag_path)
    #If we filter by something by other than date, we should still accumulate to the full extent of the data
    acc_data.filter_data("tags","==","tag2")
    assert(acc_data.get_average("Day")==sum(acc_data.get_column("amount"))/26)
    #If filter by date, accumulate should only be within the filtered dates
    acc_data.reset_filter()
    acc_data.filter_data("date",">",datetime.date(2020,12,13))
    acc_data.filter_data("date","<=",datetime.date(2020,12,20))
    assert(acc_data.get_average("Week")==(1000+100-25000)/1)
    #The filter function should detect if the date filter is greater than the data and it should affect the average
    acc_data.reset_filter()
    acc_data.filter_data("date",">=",datetime.date(2020,12,7))
    acc_data.filter_data("date","<",datetime.date(2020,12,23))
    assert(acc_data.get_average("Week")==(1000+100-25000)/1)

def test_get_total():
    acc_data = AccountData(data_path1,tag_path)
    assert(acc_data.get_total()==-44559.5)
    acc_data.filter_data("tags","==","tag2")
    assert(acc_data.get_total()==-24560.0)
    acc_data.filter_data("date",">",datetime.date(2020,12,25))
    assert(acc_data.get_total()==200.0)

def test_get_tags():
    acc_data = AccountData(data_path1,tag_file=tag_path)
    assert(sorted(acc_data.get_tags())==["tag1","tag2","tag3","överföring"])

def test_get_tags_level():
    acc_data = AccountData(data_path1,tag_file=tag_nested_path)
    assert(acc_data.get_tags("==",0) == ["tag2","tagABC"])
    assert(acc_data.get_tags(">=",1) == ["B23","B","A","B1"])
    #Since there are only 2 levels, getting all levels that are less than 3 should give back all tags
    assert(acc_data.get_tags("<",3) == acc_data.get_tags())

def test_save_load(tmp_path):
    acc_data = AccountData(data_path1,tag_file=tag_nested_path)
    acc_data.save(tmp_path/"test_save_load_data.csv")
    acc_data_loaded = AccountData(tmp_path/"test_save_load_data.csv")

    #Saving and loading should not affect data
    acc_data._expenses == acc_data_loaded._expenses
    acc_data._daterange == acc_data_loaded._daterange

def test_get_tags_by_average():
    acc_data = AccountData(data_path1,tag_file=tag_nested_path)
    assert(acc_data.get_tags_by_average(10000)=={'tag2': ['tag2'], 'tagABC, Other': ['*tagABC', 'A', 'B']})
    assert(acc_data.get_tags_by_average(100000,other_suffix="Övrig")=={'Övrig': ['tag2', 'tagABC']})
    assert(acc_data.get_tags_by_average(0)=={'tag2': ['tag2'], 'A': ['A'], 'B1': ['B1'], 'B23': ['B23'], 'tagABC, Other': ['*tagABC', '*B']})

def test_get_tags_by_average__keep_filter():
    acc_data = AccountData(data_path1,tag_file=tag_nested_path)
    acc_data.filter_data("tags","!=","tag2")
    #Calling get_tags_by_average should not mess upp the filter
    original_data = acc_data.get_data()
    original_daterange = acc_data._f_daterange
    acc_data.get_tags_by_average(10000)
    new_data = acc_data.get_data()
    new_daterange = acc_data._f_daterange
    assert(original_data==new_data)
    assert(original_daterange==new_daterange)

if __name__=="__main__":
    test_init()
    test_get_data()
    test_get_data__is_sorted()
    test_add()
    test_add__is_sorted()
