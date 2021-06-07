import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
import math

from homeplotter.accountdata import AccountData 

cat_file="./data/personal_categories.json"
tag_file="./data/personal_tags.json"
account_data1 = AccountData("./data/konto_gemensamt.csv",cat_file,tag_file)
account_data2 = AccountData("./data/konto_personligt.csv",cat_file,tag_file)
account_data3 = AccountData("./data/konto_ica.csv",cat_file,tag_file)
summed_account = account_data1/2 + account_data2 + account_data3 / 3

categories = summed_account.get_categories()
categories.remove("Uncategorized")
categories.remove("Transfer")
categories.append("All")

tags = summed_account.get_tags()
tags.remove("Reservation")

summary_texts = []
summary_texts.append("------Tag Summary (Month)------")
tag_average = []
for tag in tags:
    summed_account.reset_filter()
    summed_account.filter_data("tags","==",tag)
    summed_account.filter_data("date",">=",datetime.date(2021,2,1))
    tag_average.append([tag,math.ceil(summed_account.get_average("Month"))])
    acc_delta = "Month"
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
    plt.savefig('./output/tags/{tag}.png'.format(tag=tag,acc_delta=acc_delta.lower()))
for tag in sorted(tag_average,key=lambda tag:-tag[1]):
    summary_texts.append("{tag}: {amount}".format(tag=tag[0],amount=tag[1]))

cat_average = []
summary_texts.append("\n------Category Summary (Month)------")
for category in categories:
    summed_account.reset_filter()

    summed_account.filter_data("date",">=",datetime.date(2020,12,1))
    if category != "All":
        summed_account.filter_data("category","==",category)
    else:
        #Remove transfers from all to get a bit more consistency
        summed_account.filter_data("category","!=","Transfer")
    cat_average.append([category,math.ceil(summed_account.get_average("Month"))])
    summed_account.filter_data("tags","!=","Reservation")
    acc_delta = "Month"
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
    plt.savefig('./output/{category}.png'.format(category=category,acc_delta=acc_delta.lower()))
for cat in sorted(cat_average,key=lambda cat:-cat[1]):
    summary_texts.append("{cat}: {amount}".format(cat=cat[0],amount=cat[1]))

with open("./output/categories.csv", "w") as f:
    summed_account.reset_filter()
    for data in reversed(summed_account.get_data()):
        f.write(", ".join([data[3],data[2],str(data[4])]))
        f.write("\n")

with open("./output/summary.txt", "w") as f:
    for row in summary_texts:
        f.write(row)
        f.write("\n")