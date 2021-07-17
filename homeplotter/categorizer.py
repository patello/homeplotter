import json
import re
import collections
from typing import List

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
            self._tag_parents = {}
            if self._mode=="categorize":
                self._rec_cat["Uncategorized"] = [""]
            def tag_flattening(tag_list,tag=None):
                if type(tag_list) is list:
                    flattened_tags = {tag:tag_list}
                else:
                    flattened_tags = {}
                    for sub_tag in tag_list:
                        if sub_tag != "":
                            flattened_tags.update(tag_flattening(tag_list[sub_tag],sub_tag))
                        else:
                            flattened_tags.update({tag:tag_list[sub_tag]})
                #If the top tag doesn't have any matches of it's own, add an empty list s that we still keep track of it
                if tag is not None and tag not in flattened_tags:
                    flattened_tags[tag]=[]
                return flattened_tags


            def parent_unnesting(tag_list,parent=None):
                parents = {}
                for tag in tag_list:
                    if tag != "":
                        if parent is not None:
                            parents[tag]=parent
                        if type(tag_list[tag]) is dict:
                            ret_parents = parent_unnesting(tag_list[tag],tag)
                            for ret_parent in ret_parents:
                                parents[ret_parent] = ret_parents[ret_parent]
                return parents

                #Tag parents need to be extracted from _rec_cat before tag_unnesting as it flattens the levels
            self._tag_parents=parent_unnesting(self._rec_cat)
            self._rec_cat = collections.OrderedDict(tag_flattening(self._rec_cat))
        
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
                if self._rec_cat[tag] != [] and not re.search(reg_exp,r_text) is None:
                    matches.append(tag)
                    #Check if it has a parent, and add those recursively as well.
                    parent_tag = self._tag_parents.get(tag,None)
                    while parent_tag is not None:
                        matches.append(parent_tag)
                        parent_tag = self._tag_parents.get(parent_tag,None)
            return matches

        #Throw exception?
        return None

    def categories(self):
        return dict.keys(self._rec_cat)
    
    def get_levels(self):
        tag_levels = {}
        for tag in self._rec_cat:
            level = self.get_level(tag)
            if level in tag_levels:
                tag_levels[level].append(tag)
            else:
                tag_levels[level]=[tag]
        return tag_levels

    def get_level(self,tag):
        level = 0
        next_tag = tag
        while next_tag in self._tag_parents:
            next_tag = self._tag_parents[next_tag]
            level+=1
        return level

    def append(self,tag,text,parent_tag=None):
        #For the purposes of this function, a tag can also be a category if mode ="Category"
        #Check if tag already exists.
        if tag in self._rec_cat:
            #If it exists, append the text to the list or dict
            if type(self._rec_cat[tag])==list:
                self._rec_cat[tag].append(text)
            else:
                #If it is a dictionary, it belongs to a tag that has children, but isn't part of the children.
                #They are denoted with an empty string.
                self._rec_cat[tag][""].append(text)
        else:
            #Else, create a new tag with the text.
            self._rec_cat[tag]=[text]
            if parent_tag is not None:
                self._tag_parents[tag]=parent_tag
            if self._mode=="categorize":
                #If mode is categorize, the "Uncategorized function need to be moved to the end of the dict
                self._rec_cat.move_to_end("Uncategorized")

    def save(self, cfile):
        def tag_nesting(tag):
            #Find all child tags (keys to tag parents are children)
            child_tags = []
            for child_tag in self._tag_parents:
                if self._tag_parents[child_tag] == tag:
                    child_tags.append(child_tag)
            if child_tags != []:
                nested_tags = {}
                #check if it has own tags, add them as the "''" key then
                if self._rec_cat[tag] != []:
                    nested_tags['']=self._rec_cat[tag]
                for child_tag in child_tags:
                    nested_tags.update(tag_nesting(child_tag))
                return {tag:nested_tags}
            else:
                return {tag:self._rec_cat[tag]}

        nested_tag = {}
        for root_tag in self.get_levels()[0]:
            nested_tag.update(tag_nesting(root_tag))
        data = json.dumps(nested_tag)
        catFile = open(cfile,"w")
        catFile.write(data)
        catFile.close()

if __name__=="__main__":
    categorizer = Categorizer("/root/projects/homeplotter/example_data/categories.json")
    print(categorizer.match("Kortköp 201227 A*2"))
