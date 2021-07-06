import os

from homeplotter.categorizer import Categorizer

resource_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'example_data'))
cat_path = os.path.join(resource_path,"categories.json")
tag_path = os.path.join(resource_path,"tags.json")
tag_nested_path = os.path.join(resource_path,"tags_nested.json")

def test_match_category():
    categorizer = Categorizer(cat_path)
    assert(categorizer.match("A1")=="cat1")
    assert(categorizer.match("Kortköp 20210101 A2")=="cat1")
    assert(categorizer.match("B1")=="cat2")
    assert(categorizer.match("A*2")=="cat1")
    assert(categorizer.match("Some random words")=="Uncategorized")

def test_match_tag():
    tagger = Categorizer(tag_path,mode="tag")
    assert(tagger.match("A1")==["tag1"])
    assert(tagger.match("Kortköp 20210101 A2")==["tag2"])
    assert(tagger.match("Överföring E3") == ["tag3", "överföring"])
    assert(tagger.match("Some random words")==[])

def test_match_tag_nested():
    tagger = Categorizer(tag_nested_path,mode="tag")
    assert(tagger.match("A1")==["A", "tagABC"])
    assert(tagger.match("B2")==["B23","B","tagABC","tag2"])
    assert(tagger.match("C3")==["tagABC"])
    assert(tagger.match("E2")==["tag2"])

def test_tag_get_levels():
    tagger = Categorizer(tag_nested_path,mode="tag")
    assert(list(tagger.get_levels().keys())==[1,2,0])
    assert(tagger.get_levels()[0]==["tagABC","tag2"])
    assert(tagger.get_levels()[1]==["A","B"])
    assert(tagger.get_levels()[2]==["B1","B23"])

def test_tag_get_level():
    tagger = Categorizer(tag_nested_path,mode="tag")
    assert(tagger.get_level("tagABC")==0)
    assert(tagger.get_level("B23")==2)

def test_category_append():
    categorizer = Categorizer(cat_path)
    categorizer.append("cat1","Lorem")
    assert(categorizer.match("Lorem ipsum")=="cat1")
    categorizer.append("new cat","sit")
    assert(categorizer.match("dolor sit amet")=="new cat")

def test_tag_append_flat():
    tagger = Categorizer(tag_path,mode="tag")
    tagger.append("tag1","Lorem")
    assert(tagger.match("Lorem ipsum")==["tag1"])
    tagger.append("new tag","A1")
    assert(tagger.match("dolor sit amet A1")==["tag1","new tag"])

def test_tag_append_nested():
    tagger = Categorizer(tag_nested_path,mode="tag")
    tagger.append("tagABC","Lorem")
    assert(tagger.match("Lorem ipsum")==["tagABC"])
    tagger.append("A","sit")
    assert(tagger.match("dolor sit amet")==["A","tagABC"])
    tagger.append("new tag","elit","B23")
    assert(tagger.match("consectetur adipiscing elit")==["B23","B","tagABC","new tag"])
    tagger.append("new top tag","sed")
    assert(tagger.match("sed do")==["new top tag"])

def test_tag_append_nested_levels():
    tagger = Categorizer(tag_nested_path,mode="tag")
    tagger.append("new tag","elit","B23")
    assert(tagger.get_levels()[3]==["new tag"])
    tagger.append("new top tag","sed")
    assert(tagger.get_levels()[0]==["tagABC","tag2","new top tag"])

if __name__=="__main__":
    test_match_category()