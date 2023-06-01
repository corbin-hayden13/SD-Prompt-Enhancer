class Node:
    def __init__(self, value=None, children=[]):
        self.value = value
        self.children = children

    def __getitem__(self, index):
        return self.chhildren[index]

    def __setitem__(self, index, value):
        self.children[index] = value

    def delete(self, index):
        del self.children[index]

    def append(self, new_node):
        self.children.append(new_node)


def build_string_tree():
    pass


class TagDict:
    def __init__(self, name, multiselect=True):
        self.name = name
        self.multiselect = multiselect
        self.tag_dict = {}

    def __getitem__(self, item):
        return self.tag_dict[item]

    def __setitem__(self, key, value):
        self.tag_dict[key] = value

    def keys(self):
        return list(self.tag_dict.keys())


class TagSection:
    def __init__(self, name):
        self.name = name
        self.category_dicts = []

    def append(self, cat_dict):
        self.category_dicts.append(cat_dict)

    def __getitem__(self, index):
        try:
            return self.category_dicts[index]
        except TypeError:
            return None

    def __str__(self):
        ret_str = ""
        for cat_dict in self.category_dicts:
            ret_str += str(cat_dict) + "\n"

        return ret_str

    def __len__(self):
        return len(self.category_dicts)