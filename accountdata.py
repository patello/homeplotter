import csv
import re
import datetime
import copy
import os
import ast

from functools import reduce

from categorizer import Categorizer
from timeseries import TimeSeries

def process_date(date_string):
    if(date_string == "Reserverat"):
        return datetime.date.today()
    elif("-" in date_string):
        return datetime.datetime.strptime(date_string,"%Y-%m-%d").date()
    elif("/" in date_string):
        return datetime.datetime.strptime(date_string,"%Y/%m/%d").date()
    else:
        return datetime.datetime.strptime(date_string,"%Y.%m.%d").date()

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
    def __init__(self, account_file=None, tag_file = None, expense_data = None, scales = None, **kwds):
        self.columns = {"date":0,"amount":1,"text":2,"tags":3,"amount_unscaled":4,"account":5}
        self.column_types = {0:datetime.date,1:float,2:str,3:list,4:float,5:str}
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

        if tag_file is not None:
            self.tagger = Categorizer(tag_file)
            
        if account_file is not None:
            account_name=kwds.get('account_name',os.path.basename(account_file).split('.')[0])   
            self._account_reader(account_file,account_name)
        
        self._sort_dates()
        #After sorting, we can get the first and last date
        self._daterange=[self._expenses[0][0],self._expenses[-1][0]]
        self.reset_filter()

    def get_data(self):
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
                filter_fun = lambda data: sorted(data[col_i])==sorted(value)
            else:
                filter_fun = lambda data: len(data[col_i])==0
        elif operator in ["all", "any"] and col_type == list and val_type == list:
            #Copy the value so that the modification done on the list doesn't affect the input
            val_cpy = list(value)
            exclude = []
            for i in range(len(val_cpy)):
                #Check if first letter is "*", then add children to exclusion list
                if val_cpy[i][0] == "*":
                    #Remove the asterix and add children to exclusion list
                    val_cpy[i] = val_cpy[i][1:]
                    exclude += self.tagger.get_tag_children(val_cpy[i])
            #Remove any children from exclusion list that are also in the inclusion list 
            exclude = list(filter(lambda elem: elem not in val_cpy,exclude))                 
            if operator == "any":
                filter_fun = lambda data: any(v in data[col_i] for v in val_cpy) and not any(v in data[col_i] for v in exclude)
            elif operator == "all":
                filter_fun = lambda data: all(v in data[col_i] for v in val_cpy) and not any(v in data[col_i] for v in exclude)
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
            raise ValueError("Unsuported operator \"{operator}\". Only ==, >=, >, <, <=, any and all are supported.".format(operator=operator))
        
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

    def get_column(self, column):
        return [row[self.columns[column]] for row in self.get_data()]

    def get_timeseries(self):
        return TimeSeries(self.get_data(),daterange=self._f_daterange)
    
    def get_average(self,unit):
        ts = self.get_timeseries()
        ts.accumulate(1,unit)
        expenses = [data[1] for data in ts.data]
        if len(expenses)>0:
            return sum(expenses)/len(expenses)
        else:
            return 0

    def get_total(self):
        expenses = [data[1] for data in self._f_expenses]
        return sum(expenses)

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
        tag_column = self.columns["tags"]
        for data in self._f_expenses:
            for tag in data[tag_column]:
                if tag not in tags and level_test_fun(tag):
                    tags.append(tag)
        return tags

    #Get tags where the monthly average is over a certain limit. Merge tags that are below the limit.
    #Returns a dictionary with tag name or merged name, and list of tags it contains.
    def get_tags_by_average(self,avg_lim,other_suffix = "Other"):
        daterange = self._f_daterange
        #Keep the filtered data since this function will call the filter function
        f_expenses_org = list(self._f_expenses)
        def _rec_get_tags_by_average(tags, parent, res_tag_dict):
            merge_tags = ["*"+parent] if parent != "" else []
            for tag in tags:
                self._f_expenses = list(f_expenses_org)
                self.filter_data("tags","any",[tag])
                #Take the tag total and divide it by the time period in days dividied
                #by the average number of days in a month (30.437 days)
                tag_avg = abs(self.get_total()/((daterange[1]-daterange[0]).days/30.437))
                if tag_avg >= avg_lim * 2:
                    child_tags = self.tagger.get_tag_children(tag)
                    if len(child_tags) >= 2:
                        (res_tag_dict,rest_tags) = _rec_get_tags_by_average(child_tags, tag, res_tag_dict)
                        merge_tags+=rest_tags
                    else:
                        res_tag_dict.update({tag:[tag]})
                elif tag_avg > avg_lim:
                    res_tag_dict.update({tag:[tag]})
                else:
                    merge_tags.append(tag)
            self._f_expenses = list(f_expenses_org)
            self.filter_data("tags","any",merge_tags)
            tag_avg = abs(self.get_total()/((daterange[1]-daterange[0]).days/30.437))
            if (tag_avg > avg_lim or parent == "") and len(merge_tags)>0:
                if parent == "":
                    name = other_suffix
                #Check if all child tags have been put in merge tag, then use parent name
                elif all(elem in merge_tags for elem in tags):
                    name = parent
                else:
                    name = parent+", "+other_suffix
                res_tag_dict.update({name:merge_tags})
                merge_tags = []
            return [res_tag_dict,merge_tags]
        (result, _) = _rec_get_tags_by_average(self.get_tags("==",0), "", {})
        self._f_expenses = list(f_expenses_org)
        return result

    def get_scale(self,account):
        return self._scales[account]

    def update(self,account_file,account_name):
        updated_account = AccountData(account_file,account_name=account_name)
        updated_account = updated_account / (1/self.get_scale(account_name))
        if hasattr(self,"tagger"):
            updated_account.tagger = self.tagger
        updated_account._retag()
        self._trim_date(updated_account._daterange[0],account_name)
        self._expenses = self._expenses + updated_account._expenses
        self._sort_dates()
        #After supdated_accountorting, we can get the first and last date
        self._daterange=[self._expenses[0][0],self._expenses[-1][0]]
        self.reset_filter()

    def save(self,file_path):
        with open(file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=';',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(list(self.columns.keys()))
            for row in self._expenses:
                writer.writerow(row)
        

    def _account_reader(self,account_file,account_name):
        #Encoding is a bit weird, but got /ufeff otherwise https://stackoverflow.com/questions/53187097/how-to-read-file-in-python-withou-ufef
        with open(account_file, newline='',encoding='utf-8-sig') as csvfile:
            accountreader = csv.reader(csvfile, delimiter=';')
            #Skip the header line by first calling next
            header_row = next(accountreader)
            #Check if header_row contains all information from used columns. Then it is a saved AccountData object
            if (list(self.columns.keys()) == header_row):
                #Copy the content:
                for row in accountreader:
                    #TODO: Optimze so that we don't do lookup for each row 
                    append_row=[]
                    for column_i in range(0,len(row)):
                        if(self.column_types[column_i]==datetime.date):
                            if(self.column_types[column_i]==datetime.date):
                                append_row.append(datetime.datetime.strptime(row[column_i],"%Y-%m-%d").date())
                            else:
                                append_row.append(datetime.datetime.strptime(row[column_i],"%Y.%m.%d").date())
                        elif(self.column_types[column_i]==list):
                            append_row.append(ast.literal_eval(row[column_i]))
                        else:
                        #TODO: Fix.. This seems dangerous...
                           append_row.append(self.column_types[column_i](row[column_i]))
                    self._expenses.append(append_row)
            #Otherwise it is a csv account file
            else:
                #Maybe clean this up and not have multiple try except
                try: 
                    file_columns = {"date":header_row.index("Bokföringsdag"),"amount":header_row.index("Belopp"),"text":header_row.index("Rubrik")}
                except ValueError:
                    try:
                        file_columns = {"date":header_row.index("Datum"),"amount":header_row.index("Belopp"),"text":header_row.index("Text")}
                    except ValueError:
                        raise ValueError("Unsupported csv file structure.")
                for row in accountreader:
                        tags=self.tagger.match(row[file_columns["text"]]) if hasattr(self,"tagger") else []
                        self._expenses.append([process_date(row[file_columns["date"]]),process_amount(row[file_columns["amount"]]),row[file_columns["text"]],tags,process_amount(row[file_columns["amount"]]),account_name])

    def _retag(self):
        for row in self._expenses:
            row[self.columns["tags"]]=self.tagger.match(row[self.columns["text"]]) if hasattr(self,"tagger") else []

    def _trim_date(self,cut_off_date,account_name):
        trim_rows = []
        for row in self._expenses:
            if ((row[self.columns["account"]] == account_name) and (row[self.columns["date"]] >= cut_off_date)):
                trim_rows.append(row)
        for row in trim_rows:
            self._expenses.remove(row)

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

