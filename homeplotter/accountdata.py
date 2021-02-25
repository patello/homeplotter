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

class EmptyAccountData():
    def __init__(self):
        self.expenses = {}
        self.categories = []
        
    def get_category(self,category):
        return self.expenses[category]
    
    def get_category_column(self, category, i):
        return [row[i] for row in self.expenses[category]]

    def sum_dates(self):
        #Sum all expenses on a given date into one post
        for category in self.categories:
            i = 0
            purchase_len = len(self.expenses[category])
            while i < purchase_len:
                # Find all matches which has the same date as the one at index i. 
                # From https://stackoverflow.com/questions/946860/using-pythons-list-index-method-on-a-list-of-tuples-or-objects
                matches=[index for index, purchase  in enumerate(self.expenses[category]) if purchase[0] == self.expenses[category][i][0]]
                #Ignore the first (last after reversing) one since it matches itself. Also reverse it since we want to delete the index without affecting the order 
                #Last tip from https://stackoverflow.com/questions/11303225/how-to-remove-multiple-indexes-from-a-list-at-the-same-time
                for j in sorted(matches[1:],reverse=True):
                    #Add the amount on the current date together with the amount the matched date
                    self.expenses[category][i][1] += self.expenses[category][j][1]
                    del self.expenses[category][j]
                #Since the length might have change, we need to recalculate it:
                purchase_len = len(self.expenses[category])
                i += 1

    #Sort date set to private, data that is returned should always be sorted
    def _sort_dates(self):
        for category in self.categories:
            self.expenses[category]=sorted(self.expenses[category], key = lambda l:l[0])

    def add_missing_dates(self):
        #Adds dates that are missing from the series and set that expense to zero.
        #Assumes that the series has been sorted. Maybe call self._sort_dates first? Shouldn't be expensive if it is already sorted.
        for category in self.categories:
            for i in range(0,len(self.expenses[category])-1):
                days_between=(self.expenses[category][i+1][0]-self.expenses[category][i][0]).days
                for j in range(0,days_between-1):
                    self.expenses[category].append([self.expenses[category][i][0]+datetime.timedelta(j),0])
        #New dates are added to the end of the list so it needs to be sorted again
        self._sort_dates()

    def __add__(self, other):
        summed_account = EmptyAccountData()
        #Get the unqiue categories from the lists of categories
        unique_categories = list(set(self.categories) | set(other.categories))
        #Loop through each category, default to an empty list if key doesn't exist in either account data
        for category in unique_categories:
            summed_account.expenses[category]=self.expenses.get(category,[])+other.expenses.get(category,[])
        summed_account.categories=unique_categories
        summed_account._sort_dates()
        return summed_account

class AccountData(EmptyAccountData):
    def __init__(self, account_file,cat_file,**kwds):
        super().__init__(**kwds)
        #Consider moving to EmptyAccountData, since most/all use-cases will use the same reciever categories
        categorizer = Categorizer(cat_file)
        self.categories = categorizer.categories()

        #Add all categories to the expense dict
        for category in self.categories:
            self.expenses[category] = []

        with open(account_file, newline='') as csvfile:
            accountreader = csv.reader(csvfile, delimiter=';')
            #Skip the header line by first calling next
            next(accountreader,None)
            for row in accountreader:
                self.expenses[categorizer.match_category(row[5])].append([process_date(row[0]),process_amount(row[1])])
        self._sort_dates()

if __name__ == "__main__":
    cat_file="./example_data/categories.json"
    account_data1 = AccountData("./example_data/data1.csv",cat_file)
    account_data2 = AccountData("./example_data/data2.csv",cat_file)
    summed_account = account_data1 + account_data2
    print(summed_account.get_category_column("Uncategorized",0))

