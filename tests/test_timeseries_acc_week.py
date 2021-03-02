import datetime
import math
import itertools
import pytest

from homeplotter.timeseries import TimeSeries

sample_data = [[datetime.date(2020, 12, 23), 200.0],[datetime.date(2020, 12, 24), 50.0],[datetime.date(2020, 12, 30), 200.0], [datetime.date(2020, 12, 30), 400.0], [datetime.date(2020, 12, 31), -300], [datetime.date(2021, 1, 2), 100],[datetime.date(2021,1,11),60]]

sample_data = {
    "both-broken":[[datetime.date(2020, 12, 23), 200.0],[datetime.date(2020, 12, 24), 50.0],[datetime.date(2020, 12, 30), 200.0], [datetime.date(2020, 12, 30), 400.0], [datetime.date(2020, 12, 31), -300], [datetime.date(2021, 1, 2), 100],[datetime.date(2021,1,11),60]],
    "last-broken":[[datetime.date(2020, 12, 21), 200.0],[datetime.date(2020, 12, 24), 50.0],[datetime.date(2020, 12, 30), 200.0], [datetime.date(2020, 12, 30), 400.0], [datetime.date(2020, 12, 31), -300], [datetime.date(2021, 1, 2), 100],[datetime.date(2021,1,11),60]],
    "first-broken":[[datetime.date(2020, 12, 22), 200.0],[datetime.date(2020, 12, 24), 50.0],[datetime.date(2020, 12, 30), 200.0], [datetime.date(2020, 12, 30), 400.0], [datetime.date(2020, 12, 31), -300], [datetime.date(2021, 1, 2), 100],[datetime.date(2021,1,10),60]],
    "both-even":[[datetime.date(2020, 12, 21), 200.0],[datetime.date(2020, 12, 24), 50.0],[datetime.date(2020, 12, 30), 200.0], [datetime.date(2020, 12, 30), 400.0], [datetime.date(2020, 12, 31), -300], [datetime.date(2021, 1, 2), 100],[datetime.date(2021,1,10),60]],
    "one-week":[[datetime.date(2020, 12, 21), 200.0],[datetime.date(2020, 12, 24), 50.0],[datetime.date(2020, 12, 27), 200.0]],
}

def expected_start_date(date, padding): 
    if padding:
        return date-datetime.timedelta(date.weekday())
    else:
        return date+datetime.timedelta(7-date.weekday() if date.weekday() != 0 else 0)

def expected_end_date(date, padding): 
    if padding:
        return date-datetime.timedelta(date.weekday() if date.weekday() != 6 else 6)
    else:
        return date-datetime.timedelta(date.weekday() + 7 if date.weekday() != 6 else 6)

@pytest.mark.parametrize("padding,sample_key", itertools.product([False,True],sample_data.keys()))
def test_accumulate__len(padding,sample_key):
    ts = TimeSeries(sample_data[sample_key])
    original_len = len(ts.data)
    start_date = expected_start_date(ts.data[0][0],padding)
    end_date = expected_end_date(ts.data[-1][0], padding)
    expected_len = ((end_date-start_date).days+7)/7
    ts.accumulate(1,"Week",padding=padding)
    assert(len(ts.data) == expected_len)

@pytest.mark.parametrize("padding,sample_key", itertools.product([False,True],sample_data.keys()))
def test_accumulate__start_date(padding,sample_key):
    sd = sample_data[sample_key]
    ts = TimeSeries(sd)
    ts.accumulate(1,"Week",padding=padding)
    assert(ts.get_x()[0]==expected_start_date(sd[0][0],padding))
    assert(ts.get_x()[0].weekday()==0)

@pytest.mark.parametrize("padding,sample_key", itertools.product([False,True],sample_data.keys()))
def test_accumulate__steps(padding,sample_key):
    ts = TimeSeries(sample_data[sample_key])
    ts.accumulate(1,"Week",padding=padding)
    for i in range(1,len(ts.data)):
        assert((ts.data[i][0]-ts.data[i-1][0]).days == 7)

@pytest.mark.parametrize("padding,sample_key", itertools.product([False,True],sample_data.keys()))
def test_accumulate__end_date(padding,sample_key):
    sd = sample_data[sample_key]
    ts = TimeSeries(sd)
    ts.accumulate(1,"Week",padding=padding)
    assert(ts.get_x()[-1]==expected_end_date(sd[-1][0],padding))
    assert(ts.get_x()[-1].weekday()==0)

@pytest.mark.parametrize("padding,sample_key", itertools.product([False,True],sample_data.keys()))
def test_accumulate__sum(padding,sample_key):
    #If padding false, the first day should be skipped (in this case)
    #If padding is true, only the first day should be summed (together with two empty days)
    sd = sample_data[sample_key]
    ts = TimeSeries(sd)
    ts.accumulate(1,"Week",padding=padding)
    for i in range(len(ts.data)):
        cum_sum = 0
        for data in sd:
            if ts.data[i][0]<=data[0]<ts.data[i][0]+datetime.timedelta(7):
                cum_sum+=data[1]
        assert(ts.data[i][1]==cum_sum)