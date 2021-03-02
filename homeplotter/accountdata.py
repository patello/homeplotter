import csv
import re
import datetime

from homeplotter.categorizer import Categorizer
from homeplotter.timeseries import TimeSeries

def process_date(date_string):
    return datetime.datetime.strptime(date_string,"%Y-%m-%d").date()

def process_amount(amount_string):
    #Replace the decimal comma with a dot
    processed_string = amount_string.replace(",",".")
    #Turn the string into a number and define expenses as positive
    amount = -float(processed_string)
    return amount        

class AccountData():
    def __init__(self, account_file=None, cat_file=None, **kwds):
        self._expenses = []
        self.categories = []
        
        if cat_file is not None:
            categorizer = Categorizer(cat_file)
            self.categories = categorizer.categories()

            if account_file is not None:    
                with open(account_file, newline='') as csvfile:
                    accountreader = csv.reader(csvfile, delimiter=';')
                    #Skip the header line by first calling next
                    next(accountreader,None)
                    for row in accountreader:
                        category=categorizer.match_category(row[5])
                        self._expenses.append([process_date(row[0]),process_amount(row[1]),category,row[5]])
                self._sort_dates()

    def get_data(self,category=None):
        if category is not None:
            return list(filter(lambda x : x[2]==category,self._expenses))
        else:
            return list(self._expenses)
    
    def get_column(self, i, category=None):
        return [row[i] for row in self.get_data(category)]

    def get_timeseries(self,category=None):
        return TimeSeries(self.get_data(category))
    
    def get_average(self,unit,category=None):
        ts = TimeSeries(self.get_data(category))
        ts.accumulate(1,unit)
        expenses = [data[1] for data in ts.data]
        return sum(expenses)/len(expenses)

    #Sort date set to private, data that is returned should always be sorted
    def _sort_dates(self):
        self._expenses=sorted(self._expenses, key = lambda l:l[0])

    def __add__(self, other):
        summed_account = AccountData()
        #Add the two expense tables together
        summed_account._expenses=self._expenses+other._expenses
        #Get the unqiue categories from the lists of categories
        unique_categories = list(set(self.categories) | set(other.categories))
        summed_account.categories=unique_categories
        summed_account._sort_dates()
        return summed_account

if __name__ == "__main__":
    cat_file="./example_data/categories.json"
    account_data1 = AccountData("./example_data/data1.csv",cat_file)
    account_data2 = AccountData("./example_data/data2.csv",cat_file)
    summed_account = account_data1 + account_data2
    print(summed_account.get_column("Uncategorized",0))

