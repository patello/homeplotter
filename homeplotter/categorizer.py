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
                    #Unnesting works by iterating over all sub tags and flattening out all elements.
                    #Tags also return a dict so that sub tags can be broken out on level 0
                    unnested_list = []
                    unnested_dict = {}
                    for tag in tag_list:
                        #If tag is an empty string treat it as if the parent was a list (i.e, don't break anything)
                        if tag=="":
                            unnested_list+=tag_list[tag] 
                        #If the tag is a list, add it to the parents list (via unnested_list) and break ut the tag on it's own
                        elif type(tag_list[tag]) is list:
                            unnested_list+=tag_list[tag]
                            unnested_dict.update({tag:tag_list[tag]})
                        #If the tag is a dict, recursively call tag_unnesteing which will return a flat list of all the sub elements, and all the broken out dicts
                        elif type(tag_list[tag]) is dict:
                            ret_list, ret_dicts = tag_unnesting(tag_list[tag])
                            unnested_list+=ret_list
                            unnested_dict.update(ret_dicts)
                            #Also add this tag to the dict
                            unnested_dict.update({tag:ret_list})
                    #Return a flat list that contains all sub elements, as well as all sub dicts flattened.
                    return((unnested_list,unnested_dict))
                def levels_unnesting(tag_list,level):
                    levels = {level:[]}
                    for tag in tag_list:
                        #Ignore tags with empty strings, they act as if parent was a list
                        if tag != "":
                            levels[level].append(tag)
                            if type(tag_list[tag]) is dict:
                                ret_levels = levels_unnesting(tag_list[tag],level+1)
                                for ret_level in ret_levels:
                                    if ret_level in levels:
                                        levels[ret_level]+=ret_levels[ret_level]
                                    else:
                                        levels[ret_level]=ret_levels[ret_level]
                    return levels
                #Tag levels need to be extracted from _rec_cat before tag_unnesting as it flattens the levels
                self._tag_levels=levels_unnesting(self._rec_cat,0)
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
    
    def get_levels(self):
        if self._mode=="tag":
            return self._tag_levels
        else:
            raise(NotImplemented)

if __name__=="__main__":
    categorizer = Categorizer("/root/projects/homeplotter/example_data/categories.json")
    print(categorizer.match("Kortköp 201227 A*2"))
