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

if __name__=="__main__":
    test_match_category()