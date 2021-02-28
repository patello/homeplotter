import datetime
import math
import pytest

from homeplotter.timeseries import TimeSeries

sample_data = [[datetime.date(2020, 12, 23), 200.0],[datetime.date(2020, 12, 24), 50.0],[datetime.date(2020, 12, 30), 200.0], [datetime.date(2020, 12, 30), 400.0], [datetime.date(2020, 12, 31), -300], [datetime.date(2021, 1, 2), 100]]

def test_init__length():
    ts = TimeSeries(sample_data).data

    #The lenght of the timeseries should be the number of number of days between first and last day of data 1
    assert(len(ts)==11)

def test_init__no_missing_dates():
    ts = TimeSeries(sample_data).data
    #All dates should be present between the first and the last, an only occur once
    last_date = ts[0][0]
    for data in ts[1:]:
        assert(last_date+datetime.timedelta(1)==data[0])
        last_date = data[0]

def test_init__correct_sum():
    ts = TimeSeries(sample_data).data
    #The total should be the sum of all the individual posts in sample_data
    sum1 = 0
    for data in ts:
        sum1 += data[1]
    assert(sum1==200+50+200+400-300+100)

def test_get_x():
    ts = TimeSeries(sample_data)
    x = ts.get_x()

    #Every value should be equal to the to the first column in ts.data
    for i in range(len(x)):
        assert(x[i]==ts.data[i][0])

def test_get_y():
    ts = TimeSeries(sample_data)
    y = ts.get_y()

    #Every value should be equal to the to the first column in ts.data
    for i in range(len(y)):
        assert(y[i]==ts.data[i][1])

@pytest.mark.parametrize("forward,padding", [(False,False), (False,True), (True,False), (True,True)])
def test_accumulate__len(forward,padding):
    #Number of points should be ceil(original length/delta) with padding, otherwise floor(original length/delta)
    ts = TimeSeries(sample_data)
    original_len = len(ts.data)
    ts.accumulate(3,forward=forward,padding=padding)
    assert(len(ts.data)==(math.ceil(original_len/3) if padding else math.floor(original_len/3)))

@pytest.mark.parametrize("forward,padding,expected_timedelta", [(False,False, (11%3)), (False,True,-(3-11%3)), (True,False,0), (True,True,0)])
def test_accumulate__start_date(forward,padding,expected_timedelta):
    #First day should be the same as sample data if forward is true
    #If forward is false and padding is true, then the first day should be minus the len mod delta:th day, if padding is false, it should be delta minus len mod delta
    ts = TimeSeries(sample_data)
    ts.accumulate(3,forward=forward,padding=padding)
    assert(ts.get_x()[0]==sample_data[0][0]+datetime.timedelta(expected_timedelta))

@pytest.mark.parametrize("forward,padding,expected_timedelta", [(False,False, -2), (False,True,-2), (True,False,-2-(11%3)), (True,True,-2+(3-11%3))])
def test_accumulate__end_date(forward,padding,expected_timedelta):
    #Last day should be the same as 1 minus delta if forward is false
    #If forward is true and padding is true, then the last day should be minus the len mod delta:th day, if padding is false, it should be delta minus len mod delta
    ts = TimeSeries(sample_data)
    ts.accumulate(3,forward=forward,padding=padding)
    assert(ts.get_x()[-1]==sample_data[-1][0]+datetime.timedelta(expected_timedelta))

@pytest.mark.parametrize("forward,padding,expected_first_sum,expected_last_sum", [(False,False,0+0+0,100+0-300), (False,True,0+200+50,100+0-300), (True,False,200+50+0,200+400-300), (True,True,200+50+0,100+0+0)])
def test_accumulate__sum(forward,padding,expected_first_sum,expected_last_sum):
    #The first y value should be the same as the sum of the first three days if direction is forward
    #If direction is not forward and padding false, the first day should be skipped (in this case)
    #If direction is not forward and padding is true, only the first day should be summed (together with two empty days)
    ts = TimeSeries(sample_data)
    ts.accumulate(3,forward=forward,padding=padding)
    assert(ts.get_y()[0]==expected_first_sum)
    assert(ts.get_y()[-1]==expected_last_sum)

@pytest.mark.parametrize("forward,padding", [(False,False), (False,True), (True,False), (True,True)])
def test_accumulate__all(forward,padding):
    #Accumulating the whole interval should yeild just one data point, the first date, with the total sum of sample data, regardless of padding or direction
    ts = TimeSeries(sample_data)
    ts.accumulate(len(ts.data),forward=forward,padding=padding)

    assert(len(ts.data)==1)
    assert(ts.get_x()==[sample_data[0][0]])
    assert(ts.get_y()==[200+50+200+400-300+100])

@pytest.mark.parametrize("forward,padding", [(False,False), (False,True), (True,False), (True,True)])
def test_accumulate__twice(forward,padding):
    #If you accumulate twice, it should be the same as delta1*delta2
    ts1 = TimeSeries(sample_data)
    ts2 = TimeSeries(sample_data)
    ts1.accumulate(10,forward=forward,padding=padding)
    ts2.accumulate(2,forward=forward,padding=padding)
    ts2.accumulate(5,forward=forward,padding=padding)

    assert(len(ts1.data)==len(ts2.data))
    assert(ts1.get_x()==ts2.get_x())
    assert(ts1.get_y()==ts2.get_y())

