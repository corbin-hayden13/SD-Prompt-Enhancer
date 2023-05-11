import gradio as gr


add_tag_elements_dict = {
    "name label": ["label", False],
    "section dropdown": ["dropdown", True],
    "category dropdown": ["dropdown", True],
    "multiselect dropdown": ["dropdown", True],
    "label textbox": ["textbox", True],
    "tag textbox": ["textbox", True],
    "custom section": ["textbox", False, ""],
    "custom category": ["textbox", False],
    "custom multiselect": ["dropdown", False, None],
    "custom label": ["textbox", False],
    "custom tag": ["textbox", False],
    "make tag button": ["button", False]
}


def return_known_elements(attributes_dict):
    """
    Attributes are:
     - type: This defines the type of Gradio element from the used elements in this script
     - interactive: True or False, enable / disable gradio element
     - value: The value to update the Gradio element to
    """
    ret_gradio_list = []

    for attributes in list(attributes_dict.keys()):
        if attributes_dict[attributes][0] == "textbox":
            interactive = attributes_dict[attributes][1]
            try: value = attributes_dict[attributes][2]
            except IndexError: value = None
            ret_gradio_list.append(gr.Textbox().update(interactive=interactive, value=value))
        elif attributes_dict[attributes][0] == "dropdown":
            interactive = attributes_dict[attributes][1]
            ret_gradio_list.append(gr.Dropdown().update(interactive=interactive))
        elif attributes_dict[attributes][0] == "button":
            interactive = attributes_dict[attributes][1]
            ret_gradio_list.append(gr.Button().update(interactive=interactive))
        elif attributes_dict[attributes][0] == "label":
            visible = attributes_dict[attributes][1]
            ret_gradio_list.append(gr.Label().update(visible=visible))
        else: ret_gradio_list.append(None)

    return ret_gradio_list


def check_new_section(*args):
    global add_tag_elements_dict

    if args[1] == "New Section":
        print("New Section was found!")
        add_tag_elements_dict["category dropdown"][1] = False
        add_tag_elements_dict["multiselect dropdown"][1] = False
        add_tag_elements_dict["label textbox"][1] = False
        add_tag_elements_dict["tag textbox"][1] = False

        add_tag_elements_dict["custom section"][1] = True
        add_tag_elements_dict["custom category"][1] = True
        add_tag_elements_dict["custom multiselect"][1] = True
        add_tag_elements_dict["custom label"][1] = True
        add_tag_elements_dict["custom tag"][1] = True

    else:
        print("New Section was not found")
        add_tag_elements_dict["category dropdown"][1] = True
        add_tag_elements_dict["multiselect dropdown"][1] = True
        add_tag_elements_dict["label textbox"][1] = True
        add_tag_elements_dict["tag textbox"][1] = True

        add_tag_elements_dict["custom section"][1] = False
        add_tag_elements_dict["custom category"][1] = False
        add_tag_elements_dict["custom multiselect"][1] = False
        add_tag_elements_dict["custom label"][1] = False
        add_tag_elements_dict["custom tag"][1] = False

    tag_dropdown, custom_tag = check_tags_empty(args[5], args[10])
    if tag_dropdown or custom_tag: add_tag_elements_dict["make tag button"][1] = True
    else: add_tag_elements_dict["make tag button"][1] = False
    return return_known_elements(add_tag_elements_dict)


def check_new_category(*args):
    global add_tag_elements_dict

    if args[2] == "New Category":
        print("New Category was found!")
        add_tag_elements_dict["category dropdown"][1] = False
        add_tag_elements_dict["multiselect dropdown"][1] = False
        add_tag_elements_dict["label textbox"][1] = False
        add_tag_elements_dict["tag textbox"][1] = False

        add_tag_elements_dict["custom section"][2] = args[1]
        add_tag_elements_dict["custom section"][1] = True
        add_tag_elements_dict["custom category"][1] = True
        add_tag_elements_dict["custom multiselect"][1] = True
        add_tag_elements_dict["custom label"][1] = True
        add_tag_elements_dict["custom tag"][1] = True

    else:
        print("New Category was not found")
        add_tag_elements_dict["category dropdown"][1] = True
        add_tag_elements_dict["multiselect dropdown"][1] = True
        add_tag_elements_dict["label textbox"][1] = True
        add_tag_elements_dict["tag textbox"][1] = True

        add_tag_elements_dict["custom section"][2] = None
        add_tag_elements_dict["custom section"][1] = False
        add_tag_elements_dict["custom category"][1] = False
        add_tag_elements_dict["custom multiselect"][1] = False
        add_tag_elements_dict["custom label"][1] = False
        add_tag_elements_dict["custom tag"][1] = False

    tag_dropdown, custom_tag = check_tags_empty(args[5], args[10])
    if tag_dropdown or custom_tag: add_tag_elements_dict["make tag button"][1] = True
    else: add_tag_elements_dict["make tag button"][1] = False
    return return_known_elements(add_tag_elements_dict)


def check_tags_empty(tag_dropdown, custom_tag):
    return True if len(tag_dropdown) > 0 else False, True if len(custom_tag) > 0 else False


def verify_requirements(*args):  # Checks if an element has a value on change then checks tag inputs to enable button
    global add_tag_elements_dict

    print(f"args list in verify requirements = {args}")
    return gr.Button().update(interactive=False)
    """invalid = False
    for a in range(1, 6):
        if len(args[a]) <= 0:
            invalid = True
            break

    if not invalid:
        return gr.Button().update(interactive=True)

    invalid = False
    for b in range(6, 11):
        if len(args[b]) <= 0:
            invalid = True
            break

    if not invalid:
        return gr.Button().update(interactive=True)

    return gr.Button().update(interactive=False)"""

