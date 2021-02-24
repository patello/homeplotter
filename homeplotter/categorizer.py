import json
import re

class Categorizer():
    def __init__(self, cfile):
        with open(cfile) as json_file:
            self.rec_cat = json.load(json_file)

    def match_category(self,reciever):
        for category in self.rec_cat:
            reg_exp = "\\b("+"|".join(self.rec_cat[category])+")"
            if not re.search(reg_exp,reciever) is None:
                return category
        return None

if __name__=="__main__":
    categorizer = Categorizer("/root/projects/homeplotter/data/personal_categories.json")
    print(categorizer.match_category("Kortköp 201227 COOP NÄRA REIMERSHOL"))