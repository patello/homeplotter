import datetime
import math

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

def test_accumulate__start_date():
    #First day should be the same
    ts = TimeSeries(sample_data)
    ts.accumulate(3)
    assert(ts.get_x()[0]==sample_data[0][0])


def test_accumulate__len():
    #Number of points should be ceil(original length/delta) 
    ts = TimeSeries(sample_data)
    original_len = len(ts.data)
    ts.accumulate(3)
    assert(len(ts.data)==math.ceil(original_len/3))

def test_accumulate__sum():
    #The first y value should be the same as the sum of the first three days (if accumulate(3))
    ts = TimeSeries(sample_data)
    ts.accumulate(3)
    assert(ts.get_y()[0]==200+50)

def test_accumulate__all():
    #Accumulating the whole interval should yeild just one data point, the first date, with the total sum of sample data
    ts = TimeSeries(sample_data)
    ts.accumulate(len(ts.data))

    assert(len(ts.data)==1)
    assert(ts.get_x()==[sample_data[0][0]])
    assert(ts.get_y()==[200+50+200+400-300+100])

