import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
import math

from homeplotter.accountdata import AccountData 

tag_file="./data/personal_tags.json"
account_data1 = AccountData("./data/old/konto_gemensamt.csv",tag_file=tag_file)
account_data2 = AccountData("./data/old/konto_personligt.csv")
account_data3 = AccountData("./data/old/konto_ica.csv")
account_data4 = AccountData("./data/old/konto_reimbursments.csv")
summed_account = (account_data1/2) + account_data2 + (account_data3/2) + account_data4

start_date = datetime.date(2021,2,1)

def create_plot(tag,output_path,acc_delta="Month"):
    summed_account.reset_filter()
    if tag != "Alla" and tag != "Överskott eller Underskottt":
        summed_account.filter_data("tags","==",tag)
    else:
        summed_account.filter_data("tags","!=","Reservation")
        summed_account.filter_data("tags","!=","Överföring")
        if tag == "Alla":
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
        if tag != "Alla" and tag != "Överskott eller Underskottt":
            summed_account.filter_data("tags","==",tag)
        else:
            summed_account.filter_data("tags","!=","Reservation")
            summed_account.filter_data("tags","!=","Överföring")
            if tag == "Alla":
                summed_account.filter_data("tags","!=","Lön")
        summed_account.filter_data("date",">=",start_date)
        tag_averages.append([tag,math.ceil(summed_account.get_average(acc_delta))])
    with open(output_path, "w") as f:
        for special in ["Alla","Lön","Överskott eller Underskottt"]:
            try:
                index = [row[0] for row in tag_averages].index(special)
                f.write("{tag}: {total}\n".format(tag=special,total=tag_averages[index][1]))
                del tag_averages[index]
            except ValueError:
                break
        for (tag,average) in sorted(tag_averages, key=lambda x: -x[1]):
            f.write("{tag}: {average}\n".format(tag=tag,average=average))

def create_month_totals(tags,output_path,month,year):
    tag_totals = []
    for tag in tags:
        summed_account.reset_filter()
        if tag != "Alla" and tag != "Överskott eller Underskottt":
            summed_account.filter_data("tags","==",tag)
        else:
            summed_account.filter_data("tags","!=","Reservation")
            summed_account.filter_data("tags","!=","Överföring")
            if tag == "Alla":
                summed_account.filter_data("tags","!=","Lön")
        summed_account.filter_data("date",">=",datetime.date(year,month,1))
        summed_account.filter_data("date","<",datetime.date(year if month != 12 else year +1,month + 1 if month != 12 else 1,1))
        tag_totals.append([tag,math.ceil(summed_account.get_total())])
    with open(output_path, "w") as f:
        for special in ["Alla","Lön","Överskott eller Underskottt"]:
            try:
                index = [row[0] for row in tag_totals].index(special)
                f.write("{tag}: {total}\n".format(tag=special,total=tag_totals[index][1]))
                del tag_totals[index]
            except ValueError:
                break
        for (tag,total) in sorted(tag_totals, key=lambda x: -x[1]):
            f.write("{tag}: {total}\n".format(tag=tag,total=total))

def create_unsorted(output_path):
    summed_account.reset_filter()
    summed_account.filter_data("tags","==",[])
    summed_account.filter_data("date",">=",start_date)
    with open(output_path, "w") as f:
        for data in summed_account.get_data():
            date = data[summed_account.columns["date"]]
            amount = data[summed_account.columns["amount"]]
            text = data[summed_account.columns["text"]]
            f.write("{date}, {amount}, {text}\n".format(date=date.strftime("%d/%m"),amount=amount,text=text))
    summed_account.reset_filter()
    summed_account.filter_data("tags","==",["Reservation"])
    summed_account.filter_data("date",">=",start_date)
    with open(output_path, "a") as f:
        for data in summed_account.get_data():
            date = data[summed_account.columns["date"]]
            amount = data[summed_account.columns["amount"]]
            text = data[summed_account.columns["text"]]
            f.write("{date}, {amount}, {text}\n".format(date=date.strftime("%d/%m"),amount=amount,text=text))

def create_month_sums(output_path):
    month=datetime.date.today().month
    year=datetime.date.today().year
    while(month != start_date.month and year != start_date.year):
        summed_account.reset_filter()
        summed_account.filter_data("date",">=",datetime.date(1,month,year))
        summed_account.filter_data("date","<",datetime.date(1, month+1 if month != 12 else 1,year if month != 12 else year+1))
        
    

top_tags = summed_account.get_tags("==",0)
if "Reservation" in top_tags:
    top_tags.remove("Reservation")
if "Överföring" in top_tags:
    top_tags.remove("Överföring")
top_tags.append("Alla")
top_tags.append("Överskott eller Underskottt")
create_average(top_tags,"./output/summaries/average_top_tags.txt")
for tag in top_tags:
    create_plot(tag,'./output/{tag}.png'.format(tag=tag))

other_tags = summed_account.get_tags(">=",1)
for tag in other_tags:
    create_plot(tag,'./output/other/{tag}.png'.format(tag=tag))

all_tags = summed_account.get_tags()
all_tags.append("Alla")
all_tags.append("Överskott eller Underskottt")
create_average(all_tags,"./output/summaries/averages_all_tags.txt")
month=datetime.date.today().month
year=datetime.date.today().year
create_month_totals(all_tags,"./output/summaries/current_month_total.txt",month,year)
create_month_totals(all_tags,"./output/summaries/last_month_total.txt",month-1 if month != 1 else 12,year if month != 1 else year-1)

create_unsorted("./output/summaries/untagged.txt")