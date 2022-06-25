import os

from homeplotter.categorizer import Categorizer


resource_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'example_data'))
tag_nested_path = os.path.join(resource_path,"tags_nested.json")

def test_get_tag_children():
        tagger = Categorizer(tag_nested_path)
        assert(all([x in tagger.get_tag_children("tagABC") for x in ["A","B"]])) 
        assert(all([x in tagger.get_tag_children("B") for x in ["B1","B23"]]))
        assert(len(tagger.get_tag_children("A"))==0)

if __name__ == "__main__":
        test_get_tag_children()