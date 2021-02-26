import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from homeplotter.accountdata import AccountData 

cat_file="./data/personal_categories.json"
account_data1 = AccountData("./data/konto_gemensamt.csv",cat_file)
account_data2 = AccountData("./data/konto_personligt.csv",cat_file)
summed_account = account_data1 + account_data2

plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
plt.gca().xaxis.set_major_locator(mdates.DayLocator())

tsdata = summed_account.get_timeseries("Services")

plt.plot(tsdata.get_x(),tsdata.get_y())
plt.gcf().autofmt_xdate()
plt.savefig('./output/Services2.png')