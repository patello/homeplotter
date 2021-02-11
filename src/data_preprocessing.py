import csv
import re

import reciever_categories

def process_date(date_string):
    return date_string

def process_amount(amount_string):
    #Replace the decimal comma with a dot
    processed_string = amount_string.replace(",",".")
    #Turn the string into a number and define expenses as positive
    amount = -float(processed_string)
    return amount

def match_category(reciever, categories):
    for category in categories:
        reg_exp = "\\b("+"|".join(categories[category])+")"
        if not re.search(reg_exp,reciever) is None:
            return category
    return None

class EmptyAccountData():
    def __init__(self):
        self.purchases = {}
        self.categories = []
        self.unsorted_recievers = []
        
    def get_category(self,category):
        return self.purchases[category]

    def sum_dates(self):
        #Sum all purchases on a given date into one post
        for category in self.categories:
            i = 0
            purchase_len = len(self.purchases[category])
            while i < purchase_len:
                # Find all matches which has the same date as the one at index i. 
                # From https://stackoverflow.com/questions/946860/using-pythons-list-index-method-on-a-list-of-tuples-or-objects
                matches=[index for index, purchase  in enumerate(self.purchases[category]) if purchase[0] == self.purchases[category][i][0]]
                #Ignore the first (last after reversing) one since it matches itself. Also reverse it since we want to delete the index without affecting the order 
                #Last tip from https://stackoverflow.com/questions/11303225/how-to-remove-multiple-indexes-from-a-list-at-the-same-time
                for j in sorted(matches[1:],reverse=True):
                    #Add the amount on the current date together with the amount the matched date
                    self.purchases[category][i][1] += self.purchases[category][j][1]
                    del self.purchases[category][j]
                #Since the length might have change, we need to recalculate it:
                purchase_len = len(self.purchases[category])
                i += 1

    def __add__(self, other):
        summed_account = EmptyAccountData()
        #Get the unqiue categories from the lists of categories
        unique_categories = list(set(self.categories) | set(other.categories))
        #Loop through each category, default to an empty list if key doesn't exist in either account data
        for category in unique_categories:
            summed_account.purchases[category]=self.purchases.get(category,[])+other.purchases.get(category,[])
        summed_account.categories=unique_categories
        summed_account.unsorted_recievers=self.unsorted_recievers+other.unsorted_recievers
        return summed_account

class AccountData(EmptyAccountData):
    def __init__(self, account_file):
        super().__init__()
        #Consider moving to EmptyAccountData, since most/all use-cases will use the same reciever categories
        self.reciever_category = reciever_categories.categories
        self.categories = self.reciever_category.keys()

        #Add all categories to the purchase dict
        for category in self.categories:
            self.purchases[category] = []

        with open(account_file, newline='') as csvfile:
            accountreader = csv.reader(csvfile, delimiter=';')
            #Skip the header line by first calling next
            next(accountreader,None)
            for row in accountreader:
                category = match_category(row[5],self.reciever_category)
                if not category is None:
                    self.purchases[category].append([process_date(row[0]),process_amount(row[1])])
                else:
                    self.unsorted_recievers.append(row[5])

#if __name__ == "main":
account_data1 = AccountData("./data/konto_gemensamt.csv")
account_data2 = AccountData("./data/konto_personligt.csv")
summed_account = account_data1 + account_data2
print(summed_account.get_category("Services"))
summed_account.sum_dates()
print(summed_account.get_category("Services"))