import datetime
import math
import itertools
import pytest
import calendar

from timeseries import TimeSeries

sample_data = {
    "broken":[[datetime.date(2020, 10, 12), 200.0],[datetime.date(2020, 11, 24), 50.0],[datetime.date(2020, 12, 5), 200.0], [datetime.date(2020, 12, 30), 400.0], [datetime.date(2020, 12, 31), -300], [datetime.date(2021, 2, 2), 100],[datetime.date(2021,3,11),60]],
    "even-3":[[datetime.date(2020, 10, 1), 200.0],[datetime.date(2020, 11, 24), 50.0],[datetime.date(2020, 12, 5), 200.0], [datetime.date(2020, 12, 30), 400.0], [datetime.date(2020, 12, 31), -300], [datetime.date(2021, 2, 2), 100],[datetime.date(2021,3,11),60]],
    "even-5":[[datetime.date(2020, 10, 6), 200.0],[datetime.date(2020, 11, 24), 50.0],[datetime.date(2020, 12, 5), 200.0], [datetime.date(2020, 12, 30), 400.0], [datetime.date(2020, 12, 31), -300], [datetime.date(2021, 2, 2), 100],[datetime.date(2021,3,11),60]],
    "short":[[datetime.date(2020, 12, 30), 400.0], [datetime.date(2020, 12, 31), -300], [datetime.date(2021, 1, 2), 100],[datetime.date(2021,1,3),60]],
}

deltas = [1,3,5]

def expected_start_date(date, delta, original_len, padding):
    if padding and original_len%delta != 0:
        return date - datetime.timedelta(delta - original_len%delta)
    else:
        return date + datetime.timedelta(original_len%delta)

def expected_end_date(date, delta, original_len, padding):
    return date-datetime.timedelta(delta-1)

@pytest.mark.parametrize("padding,sample_key,delta", itertools.product([False,True],sample_data.keys(),deltas))
def test_accumulate__len(padding,sample_key,delta):
    ts = TimeSeries(sample_data[sample_key])
    original_len = len(ts.data)
    start_date = expected_start_date(ts.data[0][0],delta,original_len,padding)
    end_date = expected_end_date(ts.data[-1][0],delta,original_len,padding)
    expected_len = (end_date-start_date).days/delta+1
    ts.accumulate(delta,"Day",padding=padding)
    assert(len(ts.data) == expected_len)

@pytest.mark.parametrize("padding,sample_key,delta", itertools.product([False,True],sample_data.keys(),deltas))
def test_accumulate__start_date(padding,sample_key,delta):
    sd = sample_data[sample_key]
    ts = TimeSeries(sd)
    original_len = len(ts.data)
    ts.accumulate(delta,"Day",padding=padding)
    assert(ts.get_x()[0]==expected_start_date(sd[0][0],delta,original_len,padding))

@pytest.mark.parametrize("padding,sample_key,delta", itertools.product([False,True],sample_data.keys(),deltas))
def test_accumulate__steps(padding,sample_key,delta):
    ts = TimeSeries(sample_data[sample_key])
    ts.accumulate(delta,"Day",padding=padding)
    for i in range(1,len(ts.data)):
        assert((ts.data[i][0]-ts.data[i-1][0]).days == delta)

@pytest.mark.parametrize("padding,sample_key,delta", itertools.product([False,True],sample_data.keys(),deltas))
def test_accumulate__end_date(padding,sample_key,delta):
    sd = sample_data[sample_key]
    ts = TimeSeries(sd)
    original_len = len(ts.data)
    ts.accumulate(delta,"Day",padding=padding)
    assert(ts.get_x()[-1]==expected_end_date(sd[-1][0],delta,original_len,padding))


@pytest.mark.parametrize("padding,sample_key,delta", itertools.product([False,True],sample_data.keys(),deltas))
def test_accumulate__sum(padding,sample_key,delta):
    sd = sample_data[sample_key]
    ts = TimeSeries(sd)
    ts.accumulate(delta,"Day",padding=padding)
    for i in range(len(ts.data)):
        cum_sum = 0
        for data in sd:
            if ts.data[i][0]<=data[0]<ts.data[i][0]+datetime.timedelta(delta):
                cum_sum+=data[1]
        assert(ts.data[i][1]==cum_sum)