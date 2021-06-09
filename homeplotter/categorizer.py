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
            if self._mode=="tag":
                def tag_unnesting(tag_list):
                    unnested_list = []
                    unnested_dict = {}
                    for tag in tag_list:
                        if tag=="":
                            unnested_list+=tag_list[tag] 
                        elif type(tag_list[tag]) is list:
                            unnested_list+=tag_list[tag]
                            unnested_dict.update({tag:tag_list[tag]})
                        elif type(tag_list[tag]) is dict:
                            ret_list, ret_dicts = tag_unnesting(tag_list[tag])
                            unnested_list+=ret_list
                            unnested_dict.update(ret_dicts)
                            unnested_dict.update({tag:ret_list})
                    return((unnested_list,unnested_dict))

                (_,self._rec_cat)=tag_unnesting(self._rec_cat)
        
    def match(self,reciever):
        #Remove common astrixes from reciever text since it they mess up matching and show up in random places
        r_text = reciever
        r_text = r_text.replace("K*","")
        r_text = r_text.replace("C*","")
        r_text = r_text.replace("*","")
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
