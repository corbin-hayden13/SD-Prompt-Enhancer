import os
from random import shuffle

import pandas as pd

import modules.scripts as scripts
from modules.scripts import script_callbacks
import gradio as gr

from modules.processing import process_images
from pandas import read_csv, isna, concat, DataFrame
import numpy as np


# TODO Ability to add and remove tags from within UI
# TODO Ability to share tag file

priorities = ["Prompt", "Random", "None"]
# tags_dict = read_csv("PromptEnhancerScripts/prompt_enhancer_tags/prompt_enhancer_tags.csv", na_values=["null"]).replace("", np.nan)
tags_dict = DataFrame()
database_dict = {}
pos_prompt_comp = None
all_sections = []
prompt_enhancer_dir = scripts.basedir()
database_file_path = os.path.join(prompt_enhancer_dir, "prompt_enhancer_tags")
num_extras = 5


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
    global database_file_path, database_dict, tags_dict

    databases = []
    for file in os.listdir(database_file_path):
        if file.endswith(".csv"):
            database_dict[file] = read_csv(os.path.join(database_file_path, file), na_values=["null"]).replace("", np.nan)
            databases.append(database_dict[file])

    return concat(databases, axis=0, ignore_index=True)


def format_tag_database():
    global tags_dict, priorities

    tags_dict = read_all_databases()

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


def update_textbox(new_prompt, *args):
    global num_extras
    args_list = list(args)
    value = PromptEnhancerScript.handle_priority(new_prompt, args_list, num_extras)
    return gr.Textbox().update(value=value)


def get_txt2img(prompt):
    return gr.Textbox().update(value=prompt)


def set_txt2img(*args):
    global num_extras
    new_prompt = args[5]
    new_prompt = new_prompt.replace(" ,", "")
    return gr.Textbox().update(value=new_prompt)


def update_new_prompt(*args):
    global num_extras
    new_prompt = args[3]
    return update_textbox(new_prompt, *args)


def add_update_tags(*args):
    global database_dict, prompt_enhancer_dir
    table_name = args[0]["label"]
    new_tag = {
        "Section": args[1],
        "Multiselect": args[3],
        "Category": args[2],
        "Label": args[4],
        "Tag": args[5]
    }
    temp_frame = pd.DataFrame(data=new_tag)
    database_dict[table_name] = concat([database_dict[table_name], temp_frame], axis=0, ignore_index=True)
    with open(os.path.join(prompt_enhancer_dir, "prompt_enhancer_tags", table_name), "w") as csv:
        database_dict[table_name].to_csv(path_or_buf=csv)

    return [new_arg.update(value="") for new_arg in args]


def on_ui_tabs():
    global all_sections, pos_prompt_comp, num_extras, database_file_path, prompt_enhancer_dir

    # custom_css = ".two-thirds{width:66.66% !important;}.one-third{width:33.33% !important;}"
    css = "<style>.equal-width{flex: 2 !important;} .button-width{flex: 1 !important;}</style>"
    with gr.Blocks(analytics_enabled=False, css=css) as sd_prompt_enhancer:
        with gr.Tab(label="Prompt Enhancer"):
            gr.HTML("<br />")
            with gr.Row():
                curr_prompt_box = gr.Textbox(label="Your Prompt", elem_id="curr_prompt", value="", type="text")
                get_curr_prompt_button = gr.Button(value="Get Txt2Img Prompt", elem_id="get_curr_prompt_button")
                get_curr_prompt_button.click(fn=get_txt2img, inputs=pos_prompt_comp, outputs=curr_prompt_box)

            with gr.Row():
                new_prompt_box = gr.Textbox(label="New Prompt", elem_id="new_prompt", value="", type="text")
                with gr.Row():
                    apply_tags_button = gr.Button(value="Update New Prompt", elem_id="apply_tags_buttons")
                    set_new_prompt_button = gr.Button(value="Set Txt2Img Prompt", elem_id="set_new_prompt_button")

            gr.HTML("<br />")
            with gr.Row():
                with gr.Column():
                    priority_radio = gr.Radio(label="Prioritize...", choices=priorities, elem_id="priorities",
                                              type="value", value="None")

                with gr.Column():
                    add_prompt_button = gr.Button(value="Add Tags to Prompt", elem_id="add_prompt_button")

            all_sections = format_tag_database()
            ret_list = [priority_radio, add_prompt_button, pos_prompt_comp, curr_prompt_box, get_curr_prompt_button,
                        new_prompt_box, set_new_prompt_button, apply_tags_button]
            num_extras = len(ret_list)

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

            set_new_prompt_button.click(fn=set_txt2img, inputs=ret_list, outputs=pos_prompt_comp)
            apply_tags_button.click(fn=update_new_prompt, inputs=ret_list, outputs=new_prompt_box)

        with gr.Tab(label="Tag Editor"):
            with gr.Column():
                databases = []
                for file in os.listdir(database_file_path):
                    if file.endswith(".csv"):
                        databases.append(
                            (file,
                             read_csv(os.path.join(database_file_path, file), na_values=["null"]).replace("", np.nan))
                        )

                for name, database in databases:
                    name_label = gr.Label(value=name, visible=False)
                    section_list = list(set(database["Section"]))
                    section_list.append("New Section")
                    category_list = list(set(database["Category"]))
                    category_list.append("New Category")
                    if len(section_list) > 1:
                        gr.Markdown(f"### Edit {name}")
                        with gr.Row():
                            with gr.Row(style={"flex": 2}):
                                section_dropdown = gr.Dropdown(label=f"Section Dropdown", choices=section_list,
                                                               elem_id="section_dropdown", type="value",
                                                               multiselect=False, elem_classes="equal-width")
                                category_dropdown = gr.Dropdown(label=f"Category Dropdown",
                                                                choices=category_list,
                                                                elem_id="category_dropdown", type="value",
                                                                multiselect=False, elem_classes="equal-width")
                                multiselect_dropdown = gr.Dropdown(label=f"Multiselect Dropdown",
                                                                   choices=["true", "false"],
                                                                   elem_id="multiselect_dropdown", type="value",
                                                                   multiselect=False,
                                                                   elem_classes="equal-width")
                            with gr.Row(style={"flex": 2}):
                                label_input = gr.Textbox(label="Create New Label", value="",
                                                         elem_id="label_input",
                                                         type="text", elem_classes="equal-width")
                                tag_input = gr.Textbox(label="Create New Tag", value="", elem_id="tag_input",
                                                       type="text", elem_classes="equal-width")
                            with gr.Row(style={"flex": 1}):
                                make_tag_button = gr.Button(value="Create New Tag", elem_id="make_tag_button",
                                                            elem_classes="button-width")

                    make_tag_button.click(fn=add_update_tags, inputs=[name_label, section_dropdown, category_dropdown,
                                                                      multiselect_dropdown, label_input, tag_input],
                                          outputs=[name_label, section_dropdown, category_dropdown, multiselect_dropdown,
                                                   label_input, tag_input])

    return [(sd_prompt_enhancer, "SD Prompt Enhancer", "sd_prompt_enhancer")]


class PromptEnhancerScript(scripts.Script):
    def title(self):
        return "SD Prompt Enhancer"  # Inspired by https://sd-prompt-builder.vercel.app

    """ This EXACT function and syntax is required for self.processing to be called """
    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def after_component(self, component, **kwargs):
        global pos_prompt_comp
        try:
            if kwargs["elem_id"] == "txt2img_prompt":
                pos_prompt_comp = component
        except KeyError:
            pass

    @staticmethod
    def handle_priority(prompt, args, num_extras):
        global priorities
        priority = args[0]

        if priority == priorities[0]:
            return PromptEnhancerScript.prompt_priority(prompt, args, num_extras)
        elif priority == priorities[len(priorities) - 2]:
            return PromptEnhancerScript.randomize_prompt(prompt, args, num_extras)
        else:  # This satisfies both None and Arbitrary priorities
            return PromptEnhancerScript.arbitrary_priority(prompt, args, num_extras, priority=priority)

    @staticmethod
    def prompt_priority(prompt, args, num_extras):
        global all_sections
        return "((" + prompt + ")), " + PromptEnhancerScript.parse_arbitrary_args(args, all_sections, num_extras)

    @staticmethod
    def arbitrary_priority(prompt, args, num_extras, priority=None):
        global all_sections
        return prompt + ", " + PromptEnhancerScript.parse_arbitrary_args(args, all_sections, num_extras, priority_section=priority)

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

        return PromptEnhancerScript.parse_arbitrary_args(args_list, all_sections, num_extras, True)


script_callbacks.on_ui_tabs(on_ui_tabs)

