import os
import pytest

from homeplotter.accountdata import AccountData

resource_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'example_data'))
tag_path = os.path.join(resource_path,"tags.json")
data_path1 = os.path.join(resource_path,"data1.csv")
data_path2 = os.path.join(resource_path,"data2.csv")

def test_filter__tags():
    acc_data = AccountData(data_path1,tag_file=tag_path)
    acc_data.filter_data("tags","!=","tag1")
    assert("tag1" not in acc_data.get_tags())
    acc_data.filter_data("tags","==","tag3")
    assert(acc_data.get_tags()==["tag3"])

def test_filter__multi_tags():
    #If a data point has multiple tags, those tags should be preserved
    acc_data = AccountData(data_path1,tag_file=tag_path)
    acc_data.filter_data("tags","==","överföring")
    assert(len(acc_data.get_tags())>1)

def test_filter__tag_list():
    acc_data = AccountData(data_path1,tag_file=tag_path)
    acc_data.filter_data("tags","==",["tag1","överföring"])
    #Should only contain the once that contains all the tags.
    assert(sorted(acc_data.get_tags())==sorted(["tag1","överföring"]))

def test_filter__tag_list_order():
    acc_data = AccountData(data_path1,tag_file=tag_path)
    #If the order of the tags is different, then it should still yield the same result
    acc_data.filter_data("tags","==",["överföring","tag1"])
    #Should only contain the once that contains all the tags.
    assert(sorted(acc_data.get_tags())==sorted(["tag1","överföring"]))

def test_filter__multi_tags_list():
    #When filtering with a list, only the tags with that litteral list should kept
    acc_data = AccountData(data_path1,tag_file=tag_path)
    acc_data.filter_data("tags","==",["överföring"])
    assert(acc_data.get_tags()==["överföring"])

def test_filter__multi_tags_all():
    #When filtering "all" with a list, other tags in list should be kept
    acc_data = AccountData(data_path1,tag_file=tag_path)
    acc_data.filter_data("tags","all",["överföring"])
    assert("överföring" in acc_data.get_tags())
    assert(len(acc_data.get_tags())>1)

def test_filter__multi_tags_any():
    #When filtering "all" with a list, other tags in list should be kept
    acc_data = AccountData(data_path1,tag_file=tag_path)
    acc_data.filter_data("tags","any",["tag1","tag3"])
    assert("tag1" in acc_data.get_tags())
    assert("tag3" in acc_data.get_tags())

def test_filter__tag_empty():
    acc_data = AccountData(data_path1,tag_file=tag_path)
    #Should only return those that lack any tags.
    acc_data.filter_data("tags","==",[])
    assert(acc_data.get_tags()==[])
    assert(len(acc_data.get_data())>0)

def test_filter__not_tag_list():
    acc_data = AccountData(data_path1,tag_file=tag_path)
    acc_data.filter_data("tags","!=",["tag1","överföring"])
    #Should still contain överföring, just not any that also tag1
    assert("överföring" in acc_data.get_tags())

def test_filter__not_tag_empty():
    acc_data = AccountData(data_path1,tag_file=tag_path)
    #Should only return those that has tags
    acc_data.filter_data("tags","!=",[])
    assert(all(len(tags)>0 for tags in acc_data.get_column("tags")))