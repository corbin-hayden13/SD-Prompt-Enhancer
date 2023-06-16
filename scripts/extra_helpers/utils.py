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
    print(f"Args = {args}\n")
    for a in range(len(section_list)):
        print(f"Starting_ind = {starting_ind}\n")
        temp_str = ""
        try:
            for b in range(starting_ind, starting_ind + len(section_list[a])):  # For every valid category...
                if isinstance(args[b], list) and len(args[b]) > 0:
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


def setup_ui(ui, gallery):
    def save_preview(index, images, filename):
        if len(images) == 0:
            print("There is no image in gallery to save as a preview.")
            return [page.create_html(ui.tabname) for page in ui.stored_extra_pages]
        index = int(index)
        index = 0 if index < 0 else index
        index = len(images) - 1 if index >= len(images) else index
        img_info = images[index if index >= 0 else 0]
        image = image_from_url_text(img_info)
        is_allowed = False
        for extra_page in ui.stored_extra_pages:
            if any(path_is_parent(x, filename) for x in extra_page.allowed_directories_for_previews()):
                is_allowed = True
                break
        assert is_allowed, f'writing to {filename} is not allowed'
        image.save(filename)
        shared.log.info(f'Extra network save preview: {filename}')
        return [page.create_html(ui.tabname) for page in ui.stored_extra_pages]

    ui.button_save_preview.click(
        fn=save_preview,
        _js="function(x, y, z){return [selected_gallery_index(), y, z]}",
        inputs=[ui.preview_target_filename, gallery, ui.preview_target_filename],
        outputs=[*ui.pages]
    )

    # write description to a file
    def save_description(filename,descrip):
        lastDotIndex = filename.rindex('.')
        filename = filename[0:lastDotIndex]+".description.txt"
        if descrip != "":
            try:
                with open(filename,'w', encoding='utf-8') as f:
                    f.write(descrip)
                shared.log.info(f'Extra network save description: {filename}')
            except Exception as e:
                shared.log.error(f'Extra network save preview: {filename} {e}')
        return [page.create_html(ui.tabname) for page in ui.stored_extra_pages]

    ui.button_save_description.click(
        fn=save_description,
        _js="function(x,y){return [x,y]}",
        inputs=[ui.description_target_filename, ui.description_input],
        outputs=[*ui.pages]
    )

