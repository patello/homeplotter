import datetime
import math
import csv

from accountdata import AccountData 

tag_file="./data/personal_tags.json"
account_data1 = AccountData("./data/old/konto_gemensamt.csv",tag_file=tag_file)
account_data2 = AccountData("./data/old/konto_personligt.csv")
account_data3 = AccountData("./data/old/konto_ica.csv")
account_data4 = AccountData("./data/old/konto_reimbursments.csv")
summed_account = (account_data1/2) + account_data2 + (account_data3/2) + account_data4

start_date = datetime.date(2021,2,1)

summed_account.filter_data("tags","!=","Reservation")
summed_account.filter_data("tags","!=","Överföring")

tags = summed_account.get_tags_by_average(1000,"Övrigt")

month_data = {}

for tag in tags:
    summed_account.reset_filter()
    summed_account.filter_data("tags","any",tags[tag])
    summed_account.filter_data("date",">=",start_date)
    tsdata = summed_account.get_timeseries()
    tsdata.accumulate(1,"Month",padding=True)
    month_data.update({tag:tsdata.get_y()})

with open('./output/summaries/tag_summary.csv', 'w', newline='', encoding='utf-16') as csvfile:
    csvwriter = csv.writer(csvfile, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)

    csvwriter.writerow(["Tag"]+tsdata.get_x())
    for tag in tags:
        csvwriter.writerow([tag]+month_data[tag])