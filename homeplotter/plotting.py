import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime

from homeplotter.accountdata import AccountData 

cat_file="./data/personal_categories.json"
account_data1 = AccountData("./data/konto_gemensamt.csv",cat_file)
account_data2 = AccountData("./data/konto_personligt.csv",cat_file)
summed_account = account_data1 + account_data2

summed_account.filter_data("date",">=",datetime.date(2020,12,15))
summed_account.filter_data("category","!=","Uncategorized")
summed_account.filter_data("category","!=","Reservation")

for category in summed_account.get_categories():
    plt.cla()
    tsdata = summed_account.get_timeseries(category)
    tsdata.accumulate(1,"Week")
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
    plt.gca().xaxis.set_major_locator(mdates.WeekdayLocator())
    plt.plot(tsdata.get_x(),tsdata.get_y())
    plt.gcf().autofmt_xdate()
    plt.savefig('./output/{category}.png'.format(category=category))