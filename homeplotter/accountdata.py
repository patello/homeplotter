import csv
import re
import datetime
import copy
import os

from functools import reduce

from homeplotter.categorizer import Categorizer
from homeplotter.timeseries import TimeSeries

def process_date(date_string):
    return datetime.datetime.strptime(date_string,"%Y-%m-%d").date()

def process_amount(amount_string):
    #Replace the decimal comma with a dot
    processed_string = amount_string.replace(",",".")
    #Remove "kr" and " " if there are any, as in the case with ICA csv
    processed_string = processed_string.replace(" ","")
    processed_string = processed_string.replace("kr","")
    #Turn the string into a number and define expenses as positive
    amount = -float(processed_string)
    return amount        

class AccountData():
    def __init__(self, account_file=None, cat_file=None, tag_file = None, expense_data = None, scales = None, **kwds):
        self.columns = {"date":0,"amount":1,"text":2,"category":3,"tags":4,"amount_unscaled":5,"account":6}
        self.column_types = {0:datetime.date,1:float,2:str,3:str,4:list,5:float,6:str}
        self._daterange = []
        self._f_daterange = []
        
        if expense_data is None:
            self._expenses = []
            #Get account name from file path or account_name parameter.
            self._scales = {kwds.get('account_name',os.path.basename(account_file).split('.')[0]):1}
        else:
            self._expenses = expense_data
            #Need to set scales otherwise we don't know how different data is scaled.
            if scales is None:
                raise ValueError("Expense data is set but not scales")
            self._scales = scales


        if cat_file is not None:
            self.categorizer = Categorizer(cat_file)

        if tag_file is not None:
            self.tagger = Categorizer(tag_file,mode="tag")
            
        if account_file is not None:
            account_name=kwds.get('account_name',os.path.basename(account_file).split('.')[0])    
            #Encoding is a bit weird, but got /ufeff otherwise https://stackoverflow.com/questions/53187097/how-to-read-file-in-python-withou-ufef
            with open(account_file, newline='',encoding='utf-8-sig') as csvfile:
                accountreader = csv.reader(csvfile, delimiter=';')
                #Skip the header line by first calling next
                header_row = next(accountreader)
                #Maybe clean this up and not have multiple try except
                try: 
                    file_columns = {"date":header_row.index("Bokföringsdag"),"amount":header_row.index("Belopp"),"text":header_row.index("Rubrik")}
                except ValueError:
                    try:
                        file_columns = {"date":header_row.index("Datum"),"amount":header_row.index("Belopp"),"text":header_row.index("Text")}
                    except ValueError:
                        raise ValueError("Unsupported csv file structure.")
                for row in accountreader:
                    category=self.categorizer.match(row[file_columns["text"]]) if hasattr(self,"categorizer") else "Uncategorized"
                    tags=self.tagger.match(row[file_columns["text"]]) if hasattr(self,"tagger") else []
                    self._expenses.append([process_date(row[file_columns["date"]]),process_amount(row[file_columns["amount"]]),row[file_columns["text"]],category,tags,process_amount(row[file_columns["amount"]]),account_name])
        
        self._sort_dates()
        #After sorting, we can get the first and last date
        self._daterange=[self._expenses[0][0],self._expenses[-1][0]]
        self.reset_filter()

    def get_data(self,category=None):
        if category is not None:
            return list(filter(lambda x : x[3]==category,self._f_expenses))
        else:
            return list(self._f_expenses)

    def filter_data(self,column,operator,value):
        #Dict which defines which values are accepted for different column types
        acc_types = {
            datetime.date:[datetime.date],
            float:[float,int],
            str:[str],
            list:[list,str],
        }

        if column in self.columns:
            col_i = self.columns[column]
            col_type = self.column_types[col_i]
            val_type = type(value)
            if not any(val_type==supported_type for supported_type in acc_types[col_type]):
                raise ValueError("Unsupported type {type} for column \"{column}\". Supported types: {supported_types}".format(
                    type=val_type,column=column,supported_types=", ".join([str(typ) for typ in acc_types[col_type]])))
        else:
            raise ValueError("Unsuported column \"{column}\".".format(column=column))

        if operator == "==" and col_type != list:
            filter_fun = lambda data:data[col_i] == value
        elif operator == "==" and col_type == list and val_type == str:
            filter_fun = lambda data:value in data[col_i]
        elif operator == "==" and col_type == list and val_type == list:
            if len(value)>0:
                filter_fun = lambda data: all(v in data[col_i] for v in value)
            else:
                filter_fun = lambda data: len(data[col_i])==0
        elif operator == "!=" and col_type != list:
            filter_fun = lambda data:data[col_i] != value
        elif operator == "!=" and col_type == list and val_type == str:
            filter_fun = lambda data:value not in data[col_i]
        elif operator == "!=" and col_type == list and val_type == list:
            if len(value)>0:
                filter_fun = lambda data: all(d in value for d in data[col_i])
            else:
                filter_fun = lambda data: len(data[col_i])!=0
        elif val_type == str or val_type == list:
            raise ValueError("Unsuported operator \"{operator}\" for string. Only == and != is supported.".format(operator=operator)) 
        elif operator == ">=":
            filter_fun = lambda data:data[col_i] >= value
        elif operator == ">":   
            filter_fun = lambda data:data[col_i] > value
        elif operator == "<":
            filter_fun = lambda data:data[col_i] < value
        elif operator == "<=":
            filter_fun = lambda data:data[col_i] <= value
        else:
            raise ValueError("Unsuported operator \"{operator}\". Only ==, >=, >, < and <= are supported.".format(operator=operator))
        
        if column == "date" and (operator == ">" or operator == ">=" or operator == "=="):
            new_value = value if operator != ">" else value + datetime.timedelta(1)
            if new_value > self._daterange[0]:
                self._f_daterange[0] = new_value
        if column == "date" and (operator == "<" or operator == "<=" or operator == "=="):
            new_value = value if operator != "<" else value - datetime.timedelta(1)
            if new_value < self._daterange[1]:
                self._f_daterange[1] = new_value
        self._f_expenses=list(filter(filter_fun,self._f_expenses))
    
    def reset_filter(self):
        self._f_expenses = self._expenses.copy()
        self._f_daterange = self._daterange.copy()

    def get_column(self, column, category=None):
        return [row[self.columns[column]] for row in self.get_data(category)]

    def get_timeseries(self,category=None):
        return TimeSeries(self.get_data(category),daterange=self._f_daterange)
    
    def get_average(self,unit,category=None):
        ts = self.get_timeseries(category)
        ts.accumulate(1,unit)
        expenses = [data[1] for data in ts.data]
        if len(expenses)>0:
            return sum(expenses)/len(expenses)
        else:
            return 0

    def get_total(self):
        expenses = [data[1] for data in self._f_expenses]
        return sum(expenses)

    def get_categories(self):
        categories = []
        for data in self._f_expenses:
            if data[3] not in categories:
                categories.append(data[3])
        return categories

    def get_tags(self,operator=">=",level=0):
        tags = []
        if operator == ">=" and level == 0:
            #If default, no need to check the level
            level_test_fun = lambda tag:True
        elif type(level) != int or level < 0:
            raise ValueError("Unsuported level specification \"{level}\". Only ints  >= 0 are supported.".format(level=level))
        elif operator in [">=",">","==","<","<="]:
            #Get the largest key (level) to be used for operator >= and >
            max_level = max(self.tagger.get_levels().keys())
            if operator == ">=":
                it_range = (level,max_level+1)
            elif operator == ">":
                it_range = (level+1,max_level+1)
            elif operator == "==":
                it_range = (level,level+1)
            elif operator == "<":
                it_range = (0,level)
            elif operator == "<=":
                it_range = (0,level+1)
            tag_list = []
            tag_levels = self.tagger.get_levels()
            for it_level in range(*it_range):
                tag_list += tag_levels[it_level]
            #Defines a lambda function that will be used when iterating over tags, needs to be part of the tags of a certain level
            level_test_fun = lambda tag: tag in tag_list
        else:
            raise ValueError("Unsuported operator \"{operator}\". Only ==, >=, >, < and <= are supported.".format(operator=operator))

        for data in self._f_expenses:
            for tag in data[4]:
                if tag not in tags and level_test_fun(tag):
                    tags.append(tag)
        return tags

    def get_scale(self,account):
        return self._scales[account]

    def _retag(self):
        for row in self._expenses:
            row[self.columns["category"]]=self.categorizer.match(row[self.columns["text"]]) if hasattr(self,"categorizer") else "Uncategorized"
            row[self.columns["tags"]]=self.tagger.match(row[self.columns["text"]]) if hasattr(self,"tagger") else []
    #Sort date set to private, data that is returned should always be sorted
    def _sort_dates(self):
        self._expenses=sorted(self._expenses, key = lambda l:l[0])

    def __add__(self, other):
        expense_data=self._expenses+other._expenses
        #Merge scales dictionaries: https://stackoverflow.com/questions/38987/how-do-i-merge-two-dictionaries-in-a-single-expression-take-union-of-dictionari
        scales = {**self._scales,**other._scales}
        new_account = AccountData(expense_data=expense_data,scales=scales)
        #Tagger needs to be added to the new account data object so that we can get levels from it later
        if hasattr(self,"tagger"):
            new_account.tagger = self.tagger
        elif hasattr(other,"tagger"):
            new_account.tagger = other.tagger
        if hasattr(self,"categorizer"):
            new_account.categorizer = self.categorizer
        if hasattr(other,"categorizer"):
            new_account.categorizer = other.categorizer
        new_account._retag()
        return new_account

    def __truediv__(self, divisor):
        #Needs to deep copy, otherwise the elements in the list are the same id.
        expense_data=copy.deepcopy(self._expenses)
        scales = copy.deepcopy(self._scales)
        amount_col = self.columns["amount"]
        for i in range(len(expense_data)):
            expense_data[i][amount_col]=expense_data[i][amount_col]/divisor
        scales={k: v / divisor for k, v in scales.items()}
        new_account = AccountData(expense_data=expense_data,scales=scales)
        if hasattr(self,"tagger"):
            new_account.tagger = self.tagger
        if hasattr(self,"categorizer"):
            new_account.categorizer = self.categorizer
        return new_account


if __name__ == "__main__":
    cat_file="./example_data/categories.json"
    account_data1 = AccountData("./example_data/data1.csv",cat_file)
    account_data2 = AccountData("./example_data/data2.csv",cat_file)
    summed_account = account_data1 + account_data2
    print(summed_account.get_column("Uncategorized",0))

