import json
import re
import collections

class Categorizer():
    def __init__(self, cfile):
        with open(cfile) as json_file:
            data = json.load(json_file)
            #Using ordered dict since I need to makes sure it's the last key that matches everything.
            #Seems like we can use an ordinary dict from python 3.7 and on. 
            self._rec_cat = collections.OrderedDict(data)
            self._rec_cat["Uncategorized"] = [""]
        
    def match_category(self,reciever):
        for category in self._rec_cat:
            reg_exp = "\\b("+"|".join(self._rec_cat[category])+")"
            if not re.search(reg_exp,reciever) is None:
                return category

        #Throw exception?
        return None

    def categories(self):
        return dict.keys(self._rec_cat)

if __name__=="__main__":
    categorizer = Categorizer("/root/projects/homeplotter/example_data/categories.json")
    print(categorizer.match_category("Kortköp 201227 A*2"))