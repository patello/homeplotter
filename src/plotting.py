import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from data_preprocessing import AccountData 

account_data1 = AccountData("./data/konto_gemensamt.csv")
account_data2 = AccountData("./data/konto_personligt.csv")
summed_account = account_data1 + account_data2

plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
plt.gca().xaxis.set_major_locator(mdates.DayLocator())
plt.plot(summed_account.get_category_column("Services",0),summed_account.get_category_column("Services",1))
plt.gcf().autofmt_xdate()
plt.savefig('./output/Services2.png')