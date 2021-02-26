import datetime

from homeplotter.timeseries import TimeSeries

sample_data = [[datetime.date(2020, 12, 23), 200.0],[datetime.date(2020, 12, 30), 200.0], [datetime.date(2020, 12, 30), 400.0], [datetime.date(2020, 12, 31), -300], [datetime.date(2021, 1, 2), 100]]

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
    assert(sum1==200+200+400-300+100)

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

