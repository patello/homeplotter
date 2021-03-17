import csv
import re
import datetime
import copy

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
    def __init__(self, account_file=None, cat_file=None, tag_file = None, expense_data = None, **kwds):
        self.columns = {"date":0,"amount":1,"text":2,"category":3,"tags":4}
        self.column_types = {0:datetime.date,1:float,2:str,3:str,4:list}
        self._daterange = []
        self._f_daterange = []
        
        if expense_data is None:
            self._expenses = []
        else:
            self._expenses = expense_data


        if cat_file is not None:
            categorizer = Categorizer(cat_file)

        if tag_file is not None:
            tagger = Categorizer(tag_file,mode="tag")
            
        if account_file is not None:    
            with open(account_file, newline='') as csvfile:
                accountreader = csv.reader(csvfile, delimiter=';')
                #Skip the header line by first calling next
                next(accountreader,None)
                for row in accountreader:
                    category=categorizer.match(row[5]) if 'categorizer' in locals() else "Uncategorized"
                    tags=tagger.match(row[5]) if 'tagger' in locals() else []
                    self._expenses.append([process_date(row[0]),process_amount(row[1]),row[5],category,tags])
        
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

    def get_categories(self):
        categories = []
        for data in self._f_expenses:
            if data[3] not in categories:
                categories.append(data[3])
        return categories

    def get_tags(self):
        tags = []
        for data in self._f_expenses:
            for tag in data[4]:
                if tag not in tags:
                    tags.append(tag)
        return tags


    #Sort date set to private, data that is returned should always be sorted
    def _sort_dates(self):
        self._expenses=sorted(self._expenses, key = lambda l:l[0])

    def __add__(self, other):
        expense_data=self._expenses+other._expenses
        return AccountData(expense_data=expense_data)

    def __truediv__(self, divisor):
        #Needs to deep copy, otherwise the elements in the list are the same id.
        expense_data=copy.deepcopy(self._expenses)
        amount_col = self.columns["amount"]
        for i in range(len(expense_data)):
            expense_data[i][amount_col]=expense_data[i][amount_col]/divisor
        return AccountData(expense_data=expense_data)


if __name__ == "__main__":
    cat_file="./example_data/categories.json"
    account_data1 = AccountData("./example_data/data1.csv",cat_file)
    account_data2 = AccountData("./example_data/data2.csv",cat_file)
    summed_account = account_data1 + account_data2
    print(summed_account.get_column("Uncategorized",0))

