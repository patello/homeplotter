import datetime
import math
import itertools
import pytest
import calendar

from homeplotter.timeseries import TimeSeries

sample_data = {
    "both-broken":[[datetime.date(2020, 10, 12), 200.0],[datetime.date(2020, 11, 24), 50.0],[datetime.date(2020, 12, 5), 200.0], [datetime.date(2020, 12, 30), 400.0], [datetime.date(2020, 12, 31), -300], [datetime.date(2021, 2, 2), 100],[datetime.date(2021,3,11),60]],
    "last-broken":[[datetime.date(2020, 10, 1), 200.0],[datetime.date(2020, 11, 24), 50.0],[datetime.date(2020, 12, 5), 200.0], [datetime.date(2020, 12, 30), 400.0], [datetime.date(2020, 12, 31), -300], [datetime.date(2021, 2, 2), 100],[datetime.date(2021,3,11),60]],
    "last-broken-year":[[datetime.date(2020, 10, 1), 200.0],[datetime.date(2020, 11, 24), 50.0],[datetime.date(2020, 12, 5), 200.0], [datetime.date(2020, 12, 30), 400.0], [datetime.date(2020, 12, 31), -300], [datetime.date(2021, 1, 2), 100]],
    "first-broken":[[datetime.date(2020, 10, 12), 200.0],[datetime.date(2020, 11, 24), 50.0],[datetime.date(2020, 12, 5), 200.0], [datetime.date(2020, 12, 30), 400.0], [datetime.date(2020, 12, 31), -300], [datetime.date(2021, 2, 2), 100],[datetime.date(2021,3,31),60]],
    "first-broken-year":[[datetime.date(2020, 12, 5), 200.0], [datetime.date(2020, 12, 30), 400.0], [datetime.date(2020, 12, 31), -300], [datetime.date(2021, 2, 2), 100],[datetime.date(2021,3,31),60]],
    "both-even":[[datetime.date(2020, 10, 1), 200.0],[datetime.date(2020, 11, 24), 50.0],[datetime.date(2020, 12, 5), 200.0], [datetime.date(2020, 12, 30), 400.0], [datetime.date(2020, 12, 31), -300], [datetime.date(2021, 2, 2), 100],[datetime.date(2021,3,31),60]],
    "one-month":[[datetime.date(2020, 12, 1), 200.0],[datetime.date(2020, 12, 5), 50.0],[datetime.date(2020, 12, 31), 300.0]],
}

def expected_start_date(date, padding):
    year = date.year
    month = date.month
    
    if padding or date.day == 1:
        return datetime.date(year,month,1)
    else:
        if month < 12:
            return datetime.date(year,month+1,1)
        else:
            return datetime.date(year+1,1,1)

def expected_end_date(date, padding):
    year = date.year
    month = date.month
    
    if padding or date.day==calendar.monthrange(year,month)[1]:
        return datetime.date(year,month,1)
    else:
        if month > 1:
            return datetime.date(year,month-1,1)
        else:
            return datetime.date(year-1,12,1)

@pytest.mark.parametrize("padding,sample_key", itertools.product([False,True],sample_data.keys()))
def test_accumulate__len(padding,sample_key):
    ts = TimeSeries(sample_data[sample_key])
    original_len = len(ts.data)
    start_date = expected_start_date(ts.data[0][0],padding)
    end_date = expected_end_date(ts.data[-1][0], padding)
    expected_len = (end_date.year-start_date.year)*12+(end_date.month-start_date.month)+1
    ts.accumulate(1,"Month",padding=padding)
    assert(len(ts.data) == expected_len)

@pytest.mark.parametrize("padding,sample_key", itertools.product([False,True],sample_data.keys()))
def test_accumulate__start_date(padding,sample_key):
    sd = sample_data[sample_key]
    ts = TimeSeries(sd)
    ts.accumulate(1,"Month",padding=padding)
    assert(ts.get_x()[0]==expected_start_date(sd[0][0],padding))
    assert(ts.get_x()[0].day==1)

@pytest.mark.parametrize("padding,sample_key", itertools.product([False,True],sample_data.keys()))
def test_accumulate__steps(padding,sample_key):
    ts = TimeSeries(sample_data[sample_key])
    ts.accumulate(1,"Month",padding=padding)
    for i in range(1,len(ts.data)):
        assert((ts.data[i][0]-ts.data[i-1][0]).days == calendar.monthrange(ts.data[i-1][0].year,ts.data[i-1][0].month)[1])

@pytest.mark.parametrize("padding,sample_key", itertools.product([False,True],sample_data.keys()))
def test_accumulate__end_date(padding,sample_key):
    sd = sample_data[sample_key]
    ts = TimeSeries(sd)
    ts.accumulate(1,"Month",padding=padding)
    assert(ts.get_x()[-1]==expected_end_date(sd[-1][0],padding))
    assert(ts.get_x()[-1].day==1)

@pytest.mark.parametrize("padding,sample_key", itertools.product([False,True],sample_data.keys()))
def test_accumulate__sum(padding,sample_key):
    sd = sample_data[sample_key]
    ts = TimeSeries(sd)
    ts.accumulate(1,"Month",padding=padding)
    for i in range(len(ts.data)):
        cum_sum = 0
        for data in sd:
            if ts.data[i][0]<=data[0]<ts.data[i][0]+datetime.timedelta(calendar.monthrange(ts.data[i][0].year,ts.data[i][0].month)[1]):
                cum_sum+=data[1]
        assert(ts.data[i][1]==cum_sum)