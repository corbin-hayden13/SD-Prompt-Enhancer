import os
from copy import deepcopy

import modules.scripts as scripts
from modules.scripts import script_callbacks
from scripts.extra_helpers.tag_classes import TagSection, TagDict
from scripts.extra_helpers.utils import randomize_prompt, arbitrary_priority, prompt_priority

from pandas import read_csv, isna, concat, DataFrame
import pandas as pd
import numpy as np
import gradio as gr


priorities = ["Prompt", "Random", "None"]
tags_dict = DataFrame()
database_dict = {}
pos_prompt_comp = None
all_sections = []
prompt_enhancer_dir = scripts.basedir()
database_file_path = os.path.join(prompt_enhancer_dir, "prompt_enhancer_tags")
num_extras = 4


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


def update_textbox(new_prompt, *args):
    global num_extras
    args_list = list(args)
    value = PromptEnhancerScript.handle_priority(new_prompt, args_list, num_extras)
    return gr.Textbox().update(value=value)


def get_txt2img(prompt):
    return gr.Textbox().update(value=prompt)


def set_txt2img(*args):
    global num_extras
    new_prompt = args[4]
    new_prompt = new_prompt.replace(" ,", "")
    return gr.Textbox().update(value=new_prompt)


def update_new_prompt(*args):
    global num_extras
    new_prompt = args[2]
    return update_textbox(new_prompt, *args)


def add_update_tags(*args):
    global database_dict, prompt_enhancer_dir, all_sections

    table_name = args[0]["label"]
    arg_offset = 5 if args[1] == "New Section" or args[2] == "New Category" else 0
    print(f"args[1] = \"{args[1]}\"\narg_offset = {arg_offset}\nSection is now = {str(args[1 + arg_offset])}")
    new_tag = {
        "Section":     [str(args[1 + arg_offset])],
        "Multiselect": [True if str(args[3 + arg_offset]) == "true" else False],
        "Category":    [str(args[2 + arg_offset])],
        "Label":       [str(args[4 + arg_offset])],
        "Tag":         [str(args[5 + arg_offset])]
    }
    temp_frame = pd.DataFrame(data=new_tag)
    database_dict[table_name] = concat([database_dict[table_name], temp_frame], axis=0, ignore_index=True)
    csv_path = os.path.join(prompt_enhancer_dir, "prompt_enhancer_tags", table_name)
    try:
        with open(csv_path, mode="w+") as file:
            database_dict[table_name].to_csv(path_or_buf=file, index=False)

    except PermissionError as err:
        print("Failed to add tag to csv, see console for more information")
        print(err)


def on_ui_tabs():
    global all_sections, pos_prompt_comp, num_extras, database_file_path, prompt_enhancer_dir

    # custom_css = ".two-thirds{width:66.66% !important;}.one-third{width:33.33% !important;}"
    css = ".equal-width{flex: 2 !important;} .button-width{flex: 1 !important;}"
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

            all_sections = format_tag_database()
            ret_list = [priority_radio, pos_prompt_comp, curr_prompt_box, get_curr_prompt_button,
                        new_prompt_box, set_new_prompt_button, apply_tags_button]
            num_extras = len(ret_list)

            with gr.Row():
                for section in all_sections:
                    with gr.Column():
                        gr.Markdown(f"### {section.name}")
                        for a in range(len(section)):  # Categories
                            temp_dropdown = gr.Dropdown(label=section[a].name, choices=section[a].keys(),
                                                        elem_id=section[a].name, type="value",
                                                        multiselect=section[a].multiselect)
                            ret_list.append(temp_dropdown)

            set_new_prompt_button.click(fn=set_txt2img, inputs=ret_list, outputs=pos_prompt_comp)
            apply_tags_button.click(fn=update_new_prompt, inputs=ret_list, outputs=new_prompt_box)

        with gr.Tab(label="Tag Editor"):
            global database_dict

            with gr.Row():
                for file in [csv_file for csv_file in list(database_dict.keys()) if csv_file != "template.csv"]:
                    file_name = file.split(".")[0].replace("_", " ")
                    with gr.Tab(label=f"{file_name}"):
                        with gr.Column():
                            with gr.Row():
                                with gr.Column(scale=7):
                                    search_dropdown = gr.Dropdown(label="Search By Keyword", choices=[], multiselect=True,
                                                                  type="value")
                                with gr.Column(scale=1):
                                    filter_dropdown = gr.Dropdown(choices=["All", "Section", "Multiselect", "Category", "Label", "Tag"],
                                                                  type="value", label="Filter By...", value="All",
                                                                  multiselect=False, interactive=True)

                            dataframe = gr.DataFrame(value=database_dict[file], interactive=True)

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
        global all_sections, priorities
        priority = args[0]

        if priority == priorities[0]:
            return prompt_priority(prompt, args, all_sections, num_extras)
        elif priority == priorities[len(priorities) - 2]:
            return randomize_prompt(prompt, args, all_sections, num_extras)
        else:  # This satisfies both None and Arbitrary priorities
            return arbitrary_priority(prompt, args, all_sections, num_extras, priority=priority)


script_callbacks.on_ui_tabs(on_ui_tabs)