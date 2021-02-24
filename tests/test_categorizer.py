import os

from homeplotter.categorizer import Categorizer

resource_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'example_data'))
cat_path = os.path.join(resource_path,"categories.json")

def test_match_category():
    categorizer = Categorizer(cat_path)
    assert(categorizer.match_category("A1")=="cat1")
    assert(categorizer.match_category("Kortköp 20210101 A2")=="cat1")
    assert(categorizer.match_category("B1")=="cat2")
    assert(categorizer.match_category("A*2")=="cat1")
    assert(categorizer.match_category("B*2")=="Uncategorized")
    assert(categorizer.match_category("Some random words")=="Uncategorized")

if __name__=="__main__":
    test_match_category()