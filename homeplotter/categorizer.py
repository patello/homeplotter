import json
import re

class Categorizer():
    def __init__(self, cfile):
        with open(cfile) as json_file:
            self._rec_cat = json.load(json_file)

    def match_category(self,reciever):
        for category in self._rec_cat:
            reg_exp = "\\b("+"|".join(self._rec_cat[category])+")"
            if not re.search(reg_exp,reciever) is None:
                return category
        return None

    def categories(self):
        return dict.keys(self._rec_cat)

if __name__=="__main__":
    categorizer = Categorizer("/root/projects/homeplotter/example_data/example_categories.json")
    print(categorizer.match_category("Kortköp 201227 A1"))