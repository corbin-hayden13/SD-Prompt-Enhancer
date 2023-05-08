import os
from random import shuffle

import modules.scripts as scripts
from modules.scripts import script_callbacks
import gradio as gr

from modules.processing import process_images
from pandas import read_csv, isna, concat, DataFrame
import numpy as np


# TODO Ability to add and remove tags from within UI
# TODO Ability to share tag file

priorities = ["Prompt", "Random", "None"]
# tags_dict = read_csv("scripts/prompt_enhancer_tags/prompt_enhancer_tags.csv", na_values=["null"]).replace("", np.nan)
tags_dict = DataFrame()
pos_prompt_comp = None
all_sections = []
database_file_path = "extensions/sd-prompt-enhancer/prompt_enhancer_tags"
num_extras = 3


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


def read_all_databases():
    global database_file_path, tags_dict

    databases = []
    for file in os.listdir(database_file_path):
        if file.endswith(".csv"):
            databases.append(read_csv(os.path.join(database_file_path, file), na_values=["null"]).replace("", np.nan))

    tags_dict = concat(databases, axis=0, ignore_index=True)


def format_tag_database():
    global tags_dict, priorities

    read_all_databases()

    section_name_list = []
    for a in range(len(tags_dict["Section"])):
        if tags_dict["Section"][a] not in section_name_list:
            section_name_list.append(tags_dict["Section"][a])

    sections_list = []
    for a in range(len(section_name_list)):
        sections_list.append(TagSection(section_name_list[a]))
        if section_name_list[a] not in priorities:
            priorities.insert(a + 1, section_name_list[a])

    for section in sections_list:
        category_list = []
        for a in range(len(tags_dict["Category"])):
            if tags_dict["Category"][a] not in category_list and tags_dict["Section"][a] == section.name:
                category_list.append(tags_dict["Category"][a])

        for category in category_list:
            new_dict = TagDict(category)
            for b in range(len(tags_dict["Label"])):
                if tags_dict["Category"][b] == category and tags_dict["Section"][b] == section.name:
                    if not isna(tags_dict["Label"][b]):
                        label = tags_dict["Label"][b]
                    else: label = ""
                    if not isna(tags_dict["Tag"][b]):
                        tag = tags_dict["Tag"][b]
                    else: tag = ""
                    new_dict[label] = tag
                    new_dict.multiselect = tags_dict["Multiselect"][b]

            section.append(new_dict)

    return sections_list


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


def on_click(*args):
    global num_extras
    pos_prompt_component = args[2]
    prompt = pos_prompt_component
    print(f"prompt = {prompt}")
    arg_list = []
    for arg in args:
        arg_list.append(arg)
    value = Script.handle_priority(prompt, arg_list, num_extras)
    return gr.Textbox().update(value=value)


class Script(scripts.Script):
    def title(self):
        return "SD Prompt Enhancer"  # Inspired by https://sd-prompt-builder.vercel.app

    def after_component(self, component, **kwargs):
        global pos_prompt_comp
        try:
            if kwargs["elem_id"] == "txt2img_prompt":
                pos_prompt_comp = component
        except KeyError:
            pass

    def run(self, p, *args):
        global all_sections, num_extras

        priority = args[0]
        button_output = args[1]

        p.prompt = str(Script.handle_priority(p.prompt, args, num_extras))

        return process_images(p)

    # def process(self, p, *args):
    #     return self.run(p, args)

    @staticmethod
    def handle_priority(prompt, args, num_extras):
        global priorities
        priority = args[0]

        if priority == priorities[0]:
            return Script.prompt_priority(prompt, args, num_extras)
        elif priority == priorities[len(priorities) - 2]:
            return Script.randomize_prompt(prompt, args, num_extras)
        else:  # This satisfies both None and Arbitrary priorities
            return Script.arbitrary_priority(prompt, args, num_extras, priority=priority)

    @staticmethod
    def prompt_priority(prompt, args, num_extras):
        global all_sections
        return "((" + prompt + ")), " + Script.parse_arbitrary_args(args, all_sections, num_extras)

    @staticmethod
    def arbitrary_priority(prompt, args, num_extras, priority=None):
        global all_sections
        return prompt + ", " + Script.parse_arbitrary_args(args, all_sections, num_extras, priority_section=priority)

    @staticmethod
    def parse_arbitrary_args(args, section_list, num_extras, is_random=False, priority_section=None) -> str:
        final_list = []
        print(f"attributes = {section_list}, args = {args}")
        for a in range(len(section_list)):
            starting_ind = num_extras if a == 0 else len(section_list[a - 1]) + starting_ind
            temp_str = ""
            for b in range(starting_ind, starting_ind + len(section_list[a])):  # For every valid category...
                if isinstance(args[b], list) and len(args[b]) > 0:
                    temp_str += keys_to_str(args[b], section_list[a][b - starting_ind]) + ", "

                elif len(args[b]) > 0:
                    temp_str += section_list[a][b - starting_ind][args[b]] + ", "
                    
            temp_str = temp_str[:len(temp_str) - 2]    
            if section_list[a].name == priority_section: final_list.insert(0, "((" + temp_str + "))")
            else: final_list.append(temp_str)

        if is_random:
            shuffle(final_list)
            print(f"Shuffled to {final_list}")

        return list_to_str(final_list).replace(" ,", "")

    @staticmethod
    def randomize_prompt(prompt, args, num_extras) -> str:
        global all_sections
        prompt_list = prompt if isinstance(prompt, list) else [a.strip() for a in prompt.split(",")]
        args_list = list(args)
        args_list.append(prompt_list)

        return Script.parse_arbitrary_args(args_list, all_sections, num_extras, True)


def broken_on_ui_tabs():
    global all_sections, pos_prompt_comp
    with gr.Blocks(analytics_enabled=False) as sd_prompt_enhancer:
        gr.HTML("<br />")
        with gr.Row():
            with gr.Column():
                priority_radio = gr.Radio(label="Prioritize...", choices=priorities, elem_id="priorities",
                                          type="value", value="None")

            with gr.Column():
                test_button = gr.Button(value="Add Tags to Prompt", elem_id="testing button")

        all_sections = format_tag_database()
        ret_list = [priority_radio, test_button, pos_prompt_comp]

        for section in all_sections:
            gr.HTML("<br />")
            gr.HTML(f"<span><b>{section.name}</b></span>")
            with gr.Row():
                for a in range(len(section)):  # Categories
                    with gr.Row():
                        temp_dropdown = gr.Dropdown(label=section[a].name, choices=section[a].keys(),
                                                    elem_id=section[a].name, type="value",
                                                    multiselect=section[a].multiselect)
                    ret_list.append(temp_dropdown)

        test_button.click(fn=on_click, inputs=ret_list, outputs=pos_prompt_comp)

        """with gr.Row():
            gr.HTML("<br />")
            gr.HTML(f"<span><b>Add a new Tag</b></span>")"""

    # return ret_list
    print("Returning on callback...")
    return [(sd_prompt_enhancer, "SD Prompt Enhancer", "sd_prompt_enhancer")]


script_callbacks.on_ui_tabs(broken_on_ui_tabs)

