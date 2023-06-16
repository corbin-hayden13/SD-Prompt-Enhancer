from random import shuffle
import re
import gradio as gr


blacklist = ["section", "multiselect", "category", "label", "tag", "", "none", "and"]


def make_token_list(section_list) -> list:
    ret_list = []
    for section in section_list:
        parse_and_add(ret_list, section.name)

        for tag_dict in section.category_dicts:
            parse_and_add(ret_list, tag_dict.name)

            for key in tag_dict.keys():
                parse_and_add(ret_list, key)
                parse_and_add(ret_list, tag_dict[key])

    return ret_list


def parse_and_add(curr_tokens, str_to_parse):
    global blacklist

    try:
        words = re.findall(r'\b\w*[a-zA-Z]\w*\b', str_to_parse)
    except TypeError:
        print(f"Type error in utils.py -> parse_and_add: caused by empty cells in between populated cells in csv file")
        return

    tokens = [word.strip().lower() for word in words if word.strip().lower() not in blacklist and word.strip().lower()
              not in curr_tokens]
    for token in tokens:
        curr_tokens.append(token)


def keys_to_str(key_list, value_dict):
    ret_str = ""
    for key in key_list:
        ret_str += value_dict[key] + ", "

    return ret_str[:len(ret_str) - 2] if ret_str != "" else ""


def list_to_str(str_list):
    ret_str = ""
    for string in str_list:
        ret_str += string + ", "

    return ret_str[:len(ret_str) - 2] if ret_str != "" else ""


def prompt_priority(prompt, args, section_list, num_extras) -> str:
    return "((" + prompt + ")), " + parse_arbitrary_args(args, section_list, num_extras)


def arbitrary_priority(prompt, args, section_list, num_extras, priority=None) -> str:
    return prompt + ", " + parse_arbitrary_args(args, section_list, num_extras, priority_section=priority)


def parse_arbitrary_args(args, section_list, num_extras, priority_section=None) -> str:

    final_list = []
    starting_ind = num_extras
    for a in range(len(section_list)):
        temp_str = ""
        try:
            for b in range(starting_ind, starting_ind + len(section_list[a])):  # For every valid category...
                if args[b] is None:
                    continue
                    
                elif isinstance(args[b], list) and len(args[b]) > 0:
                    temp_str += keys_to_str(args[b], section_list[a][b - starting_ind]) + ", "

                elif len(args[b]) > 0:
                    temp_str += section_list[a][b - starting_ind][args[b]] + ", "

        except IndexError:
            print(f"--- Caught Index Error in utils.py -> parse_arbitrary_args ---\nb = {b} for length of args = {len(args)}\n")
            temp_str = ", "

        temp_str = temp_str[:len(temp_str) - 2]
        if section_list[a].name == priority_section:
            final_list.insert(0, "((" + temp_str + "))")
        else:
            final_list.append(temp_str)

        starting_ind += len(section_list[a])

    final_str = list_to_str(final_list).replace(" ,", "")

    return final_str


def randomize_prompt(prompt, args, section_list, num_extras) -> str:
    prompt_list = prompt if isinstance(prompt, list) else [a.strip() for a in prompt.split(",")]

    parsed_str = parse_arbitrary_args(list(args), section_list, num_extras)
    parsed_list = [a.strip() for a in parsed_str.split(",")]

    prompt_list.extend(parsed_list)
    shuffle(prompt_list)

    return list_to_str(prompt_list).replace(" ,", "")


def clear_dropdowns(*args):
    ret_list = []

    for dropdown in args:
        if type(dropdown) == str:
            ret_list.append(gr.Dropdown().update(value=""))
        else:
            ret_list.append(gr.Dropdown().update(value=[]))

    return ret_list

