import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
import math

from homeplotter.accountdata import AccountData 

tag_file="./data/personal_tags.json"
account_data1 = AccountData("./data/konto_gemensamt.csv",tag_file=tag_file)
account_data2 = AccountData("./data/konto_personligt.csv",tag_file=tag_file)
account_data3 = AccountData("./data/konto_ica.csv",tag_file=tag_file)
summed_account = (account_data1/2) + account_data2 + (account_data3/2)

start_date = datetime.date(2021,2,1)

def create_plot(tag,output_path,acc_delta="Month"):
    summed_account.reset_filter()
    if tag != "All":
        summed_account.filter_data("tags","==",tag)
    else:
        summed_account.filter_data("tags","!=","Reservation")
        summed_account.filter_data("tags","!=","Överföring")
        summed_account.filter_data("tags","!=","Lön")
    summed_account.filter_data("date",">=",start_date)
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
    plt.grid(axis="y")
    plt.savefig(output_path)
    summed_account.reset_filter()

def create_average(tags,output_path,acc_delta="Month"):
    tag_averages = []
    for tag in tags:
        summed_account.reset_filter()
        summed_account.filter_data("tags","==",tag)
        summed_account.filter_data("date",">=",start_date)
        tag_averages.append([tag,math.ceil(summed_account.get_average(acc_delta))])
    with open(output_path, "w") as f:
        for (tag,average) in sorted(tag_averages, key=lambda x: -x[1]):
            f.write("{tag}: {average}\n".format(tag=tag,average=average))

def create_month_totals(tags,output_path,month,year):
    tag_totals = []
    for tag in tags:
        summed_account.reset_filter()
        summed_account.filter_data("tags","==",tag)
        summed_account.filter_data("date",">=",datetime.date(year,month,1))
        summed_account.filter_data("date","<",datetime.date(year if month != 12 else year +1,month + 1 if month != 12 else 1,1))
        tag_totals.append([tag,math.ceil(summed_account.get_total())])
    with open(output_path, "w") as f:
        for (tag,total) in sorted(tag_totals, key=lambda x: -x[1]):
            f.write("{tag}: {total}\n".format(tag=tag,total=total))

def create_unsorted(output_path):
    summed_account.reset_filter()
    summed_account.filter_data("tags","==",[])
    summed_account.filter_data("date",">=",start_date)
    with open(output_path, "w") as f:
        for (date,amount,text,category,tags) in summed_account.get_data():
            f.write("{date}, {amount}, {text}\n".format(date=date.strftime("%d/%m"),amount=amount,text=text))

top_tags = summed_account.get_tags("==",0)
top_tags.remove("Reservation")
top_tags.remove("Överföring")
create_average(top_tags,"./output/summaries/average_top_tags.txt")
top_tags.append("All")
for tag in top_tags:
    create_plot(tag,'./output/{tag}.png'.format(tag=tag))

other_tags = summed_account.get_tags(">=",1)
for tag in other_tags:
    create_plot(tag,'./output/other/{tag}.png'.format(tag=tag))

all_tags = summed_account.get_tags()
create_average(all_tags,"./output/summaries/averages_all_tags.txt")
month=datetime.date.today().month
year=datetime.date.today().year
create_month_totals(all_tags,"./output/summaries/current_month_total.txt",month,year)
create_month_totals(all_tags,"./output/summaries/last_month_total.txt",month-1 if month != 1 else 12,year if month != 1 else year-1)

create_unsorted("./output/summaries/untagged.txt")