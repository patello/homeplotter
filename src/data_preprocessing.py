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
        
    def get_category(self,category):
        return self.purchases[category]

    def __add__(self, other):
        summedAccount = EmptyAccountData()
        #Get the unqiue categories from the lists of categories
        unique_categories = list(set(self.categories) | set(other.categories))
        #Loop through each category, default to an empty list if key doesn't exist in either account data
        for category in unique_categories:
            summedAccount.purchases[category]=self.purchases.get(category,[])+self.purchases.get(category,[])
        return summedAccount

class AccountData(EmptyAccountData):
    def __init__(self, account_file):
        super().__init__()
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
                    self.purchases[category].append((process_date(row[0]),process_amount(row[1])))

#if __name__ == "main":
account_data1 = AccountData("./data/konto_gemensamt.csv")
account_data2 = AccountData("./data/konto_personligt.csv")
summed_account = account_data1 + account_data2
print(summed_account.get_category("Food"))
