import re


class Node:
    def __init__(self, value=None, children=[]):
        self.value = value
        self.children = children

    def __getitem__(self, index):
        return self.chhildren[index]

    def __setitem__(self, index, value):
        self.children[index] = value

    def append(self, new_node):
        self.children.append(new_node)


class LookupTree:
    def __init__(self, section_list):
        self.section_list = section_list
        self.root = self.build_string_tree()

    def build_string_tree(self) -> Node:
        root = Node()

        for section in self.section_list:
            self.parse_and_add(root, section.name)

            for tag_dict in section.category_dicts:
                self.parse_and_add(root, tag_dict.name)

                for key in tag_dict.keys():
                    self.parse_and_add(root, key)
                    self.parse_and_add(root, tag_dict[key])

        return root

    def parse_and_add(self, root, str_to_parse):
        tokens = [word for word in re.split(r"\W+", str_to_parse) if word]
        for token in tokens:
            self.word_to_nodes(root, token)

    def word_to_nodes(self, curr_node, word):
        if len(word) <= 1:
            curr_node.append(Node(value=word))
            return

        else:
            new_node = None
            for next_node in curr_node.children:
                if word[0].lower() == next_node.value:
                    new_node = next_node
                    break

            if new_node is None:
                new_node = Node(word[0].lower())
                curr_node.append(new_node)

            self.word_to_nodes(new_node, word[1:])


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

