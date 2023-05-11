import os

import modules.scripts as scripts
from modules.scripts import script_callbacks
from scripts.extra_helpers.tag_classes import TagSection, TagDict
from scripts.extra_helpers.utils import randomize_prompt, arbitrary_priority, prompt_priority
from scripts.extra_helpers.element_organizer import check_new_section, check_new_category, verify_requirements

from pandas import read_csv, isna, concat, DataFrame
import pandas as pd
import numpy as np
import gradio as gr


# TODO Ability to add and remove tags from within UI

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
    new_tag = {
        "Section":     [str(args[1])],
        "Multiselect": [str(args[3])],
        "Category":    [str(args[2])],
        "Label":       [str(args[4])],
        "Tag":         [str(args[5])]
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


def set_relevant_categories(curr_section):
    global all_sections

    relevant_categories = []
    for tag_section in all_sections:
        if tag_section.name == curr_section:
            for a in range(len(tag_section)):
                relevant_categories.append(tag_section[a].name)

    return gr.Dropdown().update(choices=relevant_categories)


def set_category_multiselect(curr_category):
    global tags_dict
    for a in range(len(tags_dict["Category"])):
        if tags_dict["Category"][a] == curr_category:
            return gr.Dropdown().update(value=str(tags_dict["Multiselect"][a]).lower())

    return gr.Dropdown().update(value="")


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
            description = gr.Markdown("""### Please Note:
                                          * Custom sections and categories are disabled unless you first select \"New Section\" or \"New Category\" from the corresponding dropdowns
                                          * Add Tag button is disabled until you have filled in all required fields
                                      """)
            with gr.Column():
                databases = []
                for file in os.listdir(database_file_path):
                    if file.endswith(".csv"):
                        databases.append(
                            (file, read_csv(os.path.join(database_file_path, file),
                                            na_values=["null"]).replace("", np.nan))
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
                            with gr.Column():
                                with gr.Row():
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
                                                                       multiselect=False, interactive=True)

                                with gr.Row():
                                    custom_section = gr.Textbox(label="Add Your New Section Here", value="",
                                                                elem_id="custom_section",
                                                                type="text", interactive=False)

                                    custom_category = gr.Textbox(label="Add Your New Category Here",
                                                                 value="",
                                                                 elem_id="custom_category",
                                                                 type="text", interactive=False)
                                    custom_multiselect = gr.Dropdown(label=f"Custom Multiselect",
                                                                     choices=["true", "false"],
                                                                     elem_id="custom_multiselect", type="value",
                                                                     multiselect=False, interactive=False)

                            with gr.Column():
                                with gr.Row():
                                    label_input = gr.Textbox(label="Create New Label", value="",
                                                             elem_id="label_input",
                                                             type="text", elem_classes="equal-width")
                                    tag_input = gr.Textbox(label="Create New Tag", value="", elem_id="tag_input",
                                                           type="text", elem_classes="equal-width")

                                with gr.Row():
                                    custom_label = gr.Textbox(label="Add Custom Label", value="", elem_id="custom_label",
                                                              type="text", interactive=False)
                                    custom_tag = gr.Textbox(label="Add Custom Tag", value="", elem_id="custom_label",
                                                            type="text", interactive=False)

                            with gr.Column():
                                with gr.Row():
                                    make_tag_button = gr.Button(value="Create New Tag", elem_id="make_tag_button",
                                                                elem_classes="button-width", interactive=False)

                    all_inputs = [name_label, section_dropdown, category_dropdown, multiselect_dropdown, label_input,
                                  tag_input, custom_section, custom_category, custom_multiselect, custom_label,
                                  custom_tag, make_tag_button]

                    section_dropdown.change(fn=check_new_section, inputs=all_inputs, outputs=all_inputs)
                    category_dropdown.change(fn=check_new_category, inputs=all_inputs, outputs=all_inputs)
                    # On change for all elements to enable and disable add tag button
                    """multiselect_dropdown.change(fn=verify_requirements, inputs=all_inputs, outputs=make_tag_button)
                    label_input.change(fn=verify_requirements, inputs=all_inputs, outputs=make_tag_button)
                    tag_input.change(fn=verify_requirements, inputs=all_inputs, outputs=make_tag_button)
                    custom_section.change(fn=verify_requirements, inputs=all_inputs, outputs=make_tag_button)
                    custom_category.change(fn=verify_requirements, inputs=all_inputs, outputs=make_tag_button)
                    custom_multiselect.change(fn=verify_requirements, inputs=all_inputs, outputs=make_tag_button)
                    custom_label.change(fn=verify_requirements, inputs=all_inputs, outputs=make_tag_button)
                    custom_tag.change(fn=verify_requirements, inputs=all_inputs, outputs=make_tag_button)"""

                    make_tag_button.click(fn=add_update_tags, inputs=all_inputs)
                    section_dropdown.change(fn=set_relevant_categories, inputs=section_dropdown,
                                            outputs=category_dropdown)
                    category_dropdown.change(fn=set_category_multiselect, inputs=category_dropdown,
                                             outputs=multiselect_dropdown)

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