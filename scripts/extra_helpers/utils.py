from random import shuffle


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


def parse_arbitrary_args(args, section_list, num_extras, is_random=False, priority_section=None) -> str:
    final_list = []
    for a in range(len(section_list)):
        starting_ind = num_extras if a == 0 else len(section_list[a - 1]) + starting_ind
        temp_str = ""
        for b in range(starting_ind, starting_ind + len(section_list[a])):  # For every valid category...
            if isinstance(args[b], list) and len(args[b]) > 0:
                temp_str += keys_to_str(args[b], section_list[a][b - starting_ind]) + ", "

            elif len(args[b]) > 0:
                temp_str += section_list[a][b - starting_ind][args[b]] + ", "

        temp_str = temp_str[:len(temp_str) - 2]
        if section_list[a].name == priority_section:
            final_list.insert(0, "((" + temp_str + "))")
        else:
            final_list.append(temp_str)

    if is_random:
        shuffle(final_list)
        print(f"Shuffled to {final_list}")

    return list_to_str(final_list).replace(" ,", "")


def randomize_prompt(prompt, args, section_list, num_extras) -> str:
    prompt_list = prompt if isinstance(prompt, list) else [a.strip() for a in prompt.split(",")]
    args_list = list(args)
    args_list.append(prompt_list)

    return parse_arbitrary_args(args_list, section_list, num_extras, True)