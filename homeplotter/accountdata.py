import csv
import re
import datetime

from homeplotter.categorizer import Categorizer

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

    def get_data(self,category):
        return list(filter(lambda x : x[2]==category,self._expenses))
    
    def get_column(self, category, i):
        return [row[i] for row in self.get_data(category)]

    def get_timeseries(self,category):
        ts_acc_data = AccountData()
        ts_acc_data.categories = self.categories
        ts_acc_data._expenses = self._expenses
        ts_acc_data._sum_dates()
        ts_acc_data._add_missing_dates()
        return ts_acc_data.get_data(category)

    def _

    def _sum_dates(self):
        #Sum all expenses on a given date into one post, do it separately for each category
        for category in self.categories:
            i = 0
            purchase_len = len(self.get_data(category))
            while i < purchase_len:
                # Find all matches which has the same date as the one at index i. 
                # From https://stackoverflow.com/questions/946860/using-pythons-list-index-method-on-a-list-of-tuples-or-objects
                matches=[index for index, purchase  in enumerate(self._expenses[category]) if purchase[0] == self._expenses[category][i][0]]
                #Ignore the first (last after reversing) one since it matches itself. Also reverse it since we want to delete the index without affecting the order 
                #Last tip from https://stackoverflow.com/questions/11303225/how-to-remove-multiple-indexes-from-a-list-at-the-same-time
                for j in sorted(matches[1:],reverse=True):
                    #Add the amount on the current date together with the amount the matched date
                    self._expenses[category][i][1] += self._expenses[category][j][1]
                    del self._expenses[category][j]
                #Since the length might have change, we need to recalculate it:
                purchase_len = len(self._expenses[category])
                i += 1

    #Sort date set to private, data that is returned should always be sorted
    def _sort_dates(self):
        self._expenses=sorted(self._expenses, key = lambda l:l[0])

    def _add_missing_dates(self):
        #Adds dates that are missing from the series and set that expense to zero.
        #Assumes that the series has been sorted. Maybe call self._sort_dates first? Shouldn't be expensive if it is already sorted.
        for category in self.categories:
            for i in range(0,len(self._expenses[category])-1):
                days_between=(self._expenses[category][i+1][0]-self._expenses[category][i][0]).days
                for j in range(1,days_between):
                    self._expenses[category].append([self._expenses[category][i][0]+datetime.timedelta(j),0])
        #New dates are added to the end of the list so it needs to be sorted again
        self._sort_dates()

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

