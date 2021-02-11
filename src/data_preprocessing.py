import csv
import re

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

class AccountData():
    def __init__(self):
        self.reciever_category =  {"Food":["Delivery Hero Sweden","MAXI ICA STORMARKNAD"],"Drink":["SYSTEMBOLAGET"]}
        self.categories = self.reciever_category.keys()

        self.purchases = {}
        #Add all categories to the purchase dict
        for category in self.categories:
            self.purchases[category] = []

        with open('/root/projects/homeplotter/data/konto_personligt.csv', newline='') as csvfile:
            accountreader = csv.reader(csvfile, delimiter=';')
            #Skip the header line by first calling next
            next(accountreader,None)
            for row in accountreader:
                category = match_category(row[5],self.reciever_category)
                if not category is None:
                    self.purchases[category].append((process_date(row[0]),process_amount(row[1])))

    def get_category(self,category):
        return self.purchases[category]


#if __name__ == "main":
accountData = AccountData()
pass