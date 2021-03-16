import json
import re
import collections

class Categorizer():
    def __init__(self, cfile, mode="categorize"):
        if mode in ["categorize","tag"]:
            self._mode = mode
        else:
            raise ValueError("Unknown mode: {mode}".format(mode=mode))
        with open(cfile) as json_file:
            data = json.load(json_file)
            #Using ordered dict since I need to makes sure it's the last key that matches everything.
            #Seems like we can use an ordinary dict from python 3.7 and on. 
            self._rec_cat = collections.OrderedDict(data)
            if self._mode=="categorize":
                self._rec_cat["Uncategorized"] = [""]
        
    def match(self,reciever):
        #Remove astrixes from reciever text since it they mess up matching and show up in random places
        r_text = reciever.replace("*","")
        if self._mode=="categorize":
            for category in self._rec_cat:
                reg_exp = "(?i)\\b("+"|".join(self._rec_cat[category])+")\\b"
                if not re.search(reg_exp,r_text) is None:
                    return category
        elif self._mode=="tag":
            matches = []
            for tag in self._rec_cat:
                reg_exp = "(?i)\\b("+"|".join(self._rec_cat[tag])+")\\b"
                if not re.search(reg_exp,r_text) is None:
                    matches.append(tag)
            return matches

        #Throw exception?
        return None

    def categories(self):
        return dict.keys(self._rec_cat)

if __name__=="__main__":
    categorizer = Categorizer("/root/projects/homeplotter/example_data/categories.json")
    print(categorizer.match("Kortköp 201227 A*2"))
