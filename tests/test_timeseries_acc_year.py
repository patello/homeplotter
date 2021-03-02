import datetime
import math
import itertools
import pytest
import calendar

from homeplotter.timeseries import TimeSeries

sample_data = {
    "both-broken":[[datetime.date(2017, 10, 12), 200.0],[datetime.date(2017, 11, 24), 50.0],[datetime.date(2018, 12, 5), 200.0], [datetime.date(2020, 12, 30), 400.0], [datetime.date(2020, 12, 31), -300], [datetime.date(2021, 2, 2), 100],[datetime.date(2021,3,11),60]],
    "last-broken":[[datetime.date(2017, 1, 1), 200.0],[datetime.date(2017, 11, 24), 50.0],[datetime.date(2018, 12, 5), 200.0], [datetime.date(2020, 12, 30), 400.0], [datetime.date(2020, 12, 31), -300], [datetime.date(2021, 2, 2), 100],[datetime.date(2021,3,11),60]],
    "first-broken":[[datetime.date(2017, 10, 12), 200.0],[datetime.date(2017, 11, 24), 50.0],[datetime.date(2018, 12, 5), 200.0], [datetime.date(2020, 12, 30), 400.0], [datetime.date(2020, 12, 31), -300], [datetime.date(2021, 2, 2), 100],[datetime.date(2021,12,31),60]],
    "both-even":[[datetime.date(2017, 1, 1), 200.0],[datetime.date(2017, 11, 24), 50.0],[datetime.date(2018, 12, 5), 200.0], [datetime.date(2020, 12, 30), 400.0], [datetime.date(2020, 12, 31), -300], [datetime.date(2021, 2, 2), 100],[datetime.date(2021,12,31),60]],
    "one-year":[[datetime.date(2020, 1, 1), 200.0],[datetime.date(2020, 12, 5), 50.0],[datetime.date(2020, 12, 31), 300.0]],
}

def expected_start_date(date, padding):    
    if padding or (date.month == 1 and date.day == 1):
        return datetime.date(date.year,1,1)
    else:
        return datetime.date(date.year+1,1,1)

def expected_end_date(date, padding):
    if padding or (date.month == 12 and date.day == 31):
        return datetime.date(date.year,1,1)
    else:
        return datetime.date(date.year-1,1,1)

@pytest.mark.parametrize("padding,sample_key", itertools.product([False,True],sample_data.keys()))
def test_accumulate__len(padding,sample_key):
    ts = TimeSeries(sample_data[sample_key])
    original_len = len(ts.data)
    start_date = expected_start_date(ts.data[0][0],padding)
    end_date = expected_end_date(ts.data[-1][0], padding)
    expected_len = end_date.year-start_date.year + 1
    ts.accumulate(1,"Year",padding=padding)
    assert(len(ts.data) == expected_len)

@pytest.mark.parametrize("padding,sample_key", itertools.product([False,True],sample_data.keys()))
def test_accumulate__start_date(padding,sample_key):
    sd = sample_data[sample_key]
    ts = TimeSeries(sd)
    ts.accumulate(1,"Year",padding=padding)
    assert(ts.get_x()[0]==expected_start_date(sd[0][0],padding))
    assert(ts.get_x()[0].day==1)
    assert(ts.get_x()[0].month==1)

@pytest.mark.parametrize("padding,sample_key", itertools.product([False,True],sample_data.keys()))
def test_accumulate__steps(padding,sample_key):
    ts = TimeSeries(sample_data[sample_key])
    ts.accumulate(1,"Year",padding=padding)
    for i in range(1,len(ts.data)):
        assert(ts.data[i-1][0].day==1)
        assert(ts.data[i-1][0].month==1)
        assert(ts.data[i][0].year-ts.data[i-1][0].year == 1)

@pytest.mark.parametrize("padding,sample_key", itertools.product([False,True],sample_data.keys()))
def test_accumulate__end_date(padding,sample_key):
    sd = sample_data[sample_key]
    ts = TimeSeries(sd)
    ts.accumulate(1,"Year",padding=padding)
    assert(ts.get_x()[-1]==expected_end_date(sd[-1][0],padding))
    assert(ts.get_x()[-1].day==1)
    assert(ts.get_x()[-1].month==1)

@pytest.mark.parametrize("padding,sample_key", itertools.product([False,True],sample_data.keys()))
def test_accumulate__sum(padding,sample_key):
    sd = sample_data[sample_key]
    ts = TimeSeries(sd)
    ts.accumulate(1,"Year",padding=padding)
    for i in range(len(ts.data)):
        cum_sum = 0
        for data in sd:
            year = data[0].year
            if ts.data[i][0]<=data[0]<ts.data[i][0]+datetime.timedelta(sum([calendar.monthrange(year,month)[1] for month in range(1,13)])):
                cum_sum+=data[1]
        assert(ts.data[i][1]==cum_sum)