import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
import math

from homeplotter.accountdata import AccountData 

cat_file="./data/personal_categories.json"
tag_file="./data/personal_tags.json"
account_data1 = AccountData("./data/konto_gemensamt.csv",cat_file,tag_file)
account_data2 = AccountData("./data/konto_personligt.csv",cat_file,tag_file)
summed_account = account_data1/2 + account_data2

categories = summed_account.get_categories()
categories.remove("Uncategorized")
categories.remove("Transfer")
categories.append("All")

tags = summed_account.get_tags()
tags.remove("Reservation")

print("\n------Tag Summary (Month)------\n")
for tag in tags:
    summed_account.reset_filter()
    summed_account.filter_data("tags","==",tag)
    summed_account.filter_data("date",">=",datetime.date(2020,12,15))
    print("{tag}: {amount}\n".format(tag=tag,amount=math.ceil(summed_account.get_average("Month"))))
    # for acc_delta in ["Week", "Month"]:
    #     plt.cla()
    #     tsdata = summed_account.get_timeseries()
    #     tsdata.accumulate(1,acc_delta)
    #     plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
    #     if acc_delta == "Week":
    #         plt.gca().xaxis.set_major_locator(mdates.WeekdayLocator())
    #     else:
    #         plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    #     plt.plot(tsdata.get_x(),tsdata.get_y())
    #     plt.gcf().autofmt_xdate()
    #     plt.savefig('./output/{acc_delta}ly/{tag}.png'.format(tag=tag,acc_delta=acc_delta.lower()))


print("\n------Category Summary (Month)------\n")
for category in categories:
    summed_account.reset_filter()

    summed_account.filter_data("date",">=",datetime.date(2020,12,15))
    if category != "All":
        summed_account.filter_data("category","==",category)
    else:
        #Try to remove transfers from all to get a bit more consistency
        summed_account.filter_data("category","!=","Transfer")
    print("{category}: {amount}\n".format(category=category,amount=math.ceil(summed_account.get_average("Month"))))
    summed_account.filter_data("tags","!=","Reservation")
    for acc_delta in ["Week", "Month"]:
        plt.cla()
        tsdata = summed_account.get_timeseries()
        tsdata.accumulate(1,acc_delta)
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
        if acc_delta == "Week":
            plt.gca().xaxis.set_major_locator(mdates.WeekdayLocator())
        else:
            plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
        plt.plot(tsdata.get_x(),tsdata.get_y())
        plt.gcf().autofmt_xdate()
        plt.savefig('./output/{acc_delta}ly/{category}.png'.format(category=category,acc_delta=acc_delta.lower()))

with open("./output/categories.csv", "w") as f:
    summed_account.reset_filter()
    for data in summed_account.get_data():
        f.write(", ".join([data[3],data[2],str(data[4])]))
        f.write("\n")