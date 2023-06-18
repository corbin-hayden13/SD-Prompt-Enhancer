import os

import modules.scripts as scripts
from modules.scripts import script_callbacks
from modules.ui import extra_networks_symbol
from modules.ui_components import FormRow, ToolButton
from modules.shared import opts
from scripts.extra_helpers.tag_classes import TagSection, TagDict
from scripts.extra_helpers.utils import randomize_prompt, arbitrary_priority, prompt_priority, make_token_list, clear_dropdowns

from pandas import read_csv, isna, concat, DataFrame
import pandas as pd
import numpy as np
import gradio as gr


priorities = ["Prompt", "Random", "None"]
tags_dict = DataFrame()
database_dict = {}
pos_prompt_comp = None
all_sections = []
token_list = []
prompt_enhancer_dir = scripts.basedir()
database_file_path = os.path.join(prompt_enhancer_dir, "prompt_enhancer_tags")
num_extras = 4
dropdowns_displayed = False
extra_networks_visible = False


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
        if tags_dict["Section"][a] not in section_name_list and type(tags_dict["Section"][a]) != float:
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
    new_prompt = args[3]
    new_prompt = new_prompt.replace(" ,", "")
    return gr.Textbox().update(value=new_prompt)


def update_new_prompt(*args):
    new_prompt = args[2]
    return update_textbox(new_prompt, *args)


def update_choices(*args):
    global database_dict

    if len(args[0]) <= 0:
        return gr.Dataframe().update(value=database_dict[args[2]["label"]])

    if args[1] == "All":
        keys = ["Section", "Category", "Label", "Tag"]
    else: keys = list(args[1])

    ref_dataframe = database_dict[args[2]["label"]]
    new_dataframe = {
        "Section": [],
        "Multiselect": [],
        "Category": [],
        "Label": [],
        "Tag": []
    }
    for a in range(len(ref_dataframe["Section"])):
        found = False
        for key in keys:
            for tag in args[0]:
                if tag.lower() in str(ref_dataframe[key][a]).lower():
                    found = True
                    break

            if found: break

        if found:
            for key in keys:
                new_dataframe[key].append(ref_dataframe[key][a])
            new_dataframe["Multiselect"].append(ref_dataframe["Multiselect"][a])

    return gr.DataFrame().update(value=pd.DataFrame(new_dataframe))


def add_update_tags(*args):
    global database_dict, prompt_enhancer_dir, all_sections

    table_name = args[0]["label"]
    arg_offset = 5 if args[1] == "New Section" or args[2] == "New Category" else 0
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
    global all_sections, token_list, pos_prompt_comp, num_extras, database_file_path, prompt_enhancer_dir

    css = "# columnAccordion .label {font-weight: bold !important; font-size: 10vw !important}"

    with gr.Blocks(analytics_enabled=False, css=css) as sd_prompt_enhancer:
        with gr.Tab(label="Prompt Enhancer"):
            gr.HTML("<br />")
            with gr.Row():
                with gr.Column(scale=7):
                    curr_prompt_box = gr.Textbox(label="Your Prompt", elem_id="sd_enhancer_prompt", value="", type="text")
                with gr.Column(scale=1):
                    with gr.Row():
                        with gr.Column(scale=7):
                            get_curr_prompt_button = gr.Button(value="Get Txt2Img Prompt", elem_id="get_curr_prompt_button")
                            get_curr_prompt_button.click(fn=get_txt2img, inputs=pos_prompt_comp, outputs=curr_prompt_box)

                    with gr.Column(scale=1):
                        extra_networks_button = ToolButton(value=extra_networks_symbol, elem_id="extra_networks_toggle")

            with gr.Row():
                with gr.Column(scale=7):
                    new_prompt_box = gr.Textbox(label="New Prompt", elem_id="new_prompt", value="", type="text")
                with gr.Column(scale=1):
                    with gr.Row():
                        apply_tags_button = gr.Button(value="Update New Prompt", elem_id="apply_tags_buttons")
                        set_new_prompt_button = gr.Button(value="Set Txt2Img Prompt", elem_id="set_new_prompt_button")

            with FormRow(variant='compact', elem_id="sd_enhancer_extra_networks", visible=False) as extra_networks_formrow:
                from modules import ui_extra_networks
                extra_networks_ui = ui_extra_networks.create_ui(extra_networks_formrow, extra_networks_button,
                                                                'sd_enhancer')

            def toggle_extra_networks():
                global extra_networks_visible

                extra_networks_visible = not extra_networks_visible
                print(extra_networks_visible)
                return gr.update(visible=extra_networks_visible)

            extra_networks_button.click(fn=toggle_extra_networks, outputs=extra_networks_formrow)

            gr.HTML("<br />")
            with gr.Row():
                with gr.Column(scale=7):
                    priority_radio = gr.Radio(label="Prioritize...", choices=priorities, elem_id="priorities",
                                              type="value", value="None")
                with gr.Column(scale=2):
                    clear_dropdowns_button = gr.Button(value="Clear All Dropdown Fields", elem_id="dropdown_clear")

            all_sections = format_tag_database()
            token_list = sorted(make_token_list(all_sections))
            ret_list = [priority_radio, pos_prompt_comp, curr_prompt_box, new_prompt_box]
            num_extras = len(ret_list)

            with gr.Row():
                with gr.Column(scale=7):
                    pass  # List all shown sections
                with gr.Column(scale=2):
                    pass  # Search all known tags

            for a in range(0, len(all_sections), 5):
                with gr.Row():
                    for b in range(5):
                        try:
                            test = all_sections[a + b].name
                        except IndexError:
                            break

                        with gr.Accordion(label=f"{all_sections[a + b].name}", open=False):
                            with gr.Column():
                                for c in range(len(all_sections[a + b])):  # Categories
                                    temp_dropdown = gr.Dropdown(label=all_sections[a + b][c].name,
                                                                choices=all_sections[a + b][c].keys(),
                                                                elem_id=all_sections[a + b][c].name, type="value",
                                                                multiselect=all_sections[a + b][c].multiselect)
                                    ret_list.append(temp_dropdown)

            set_new_prompt_button.click(fn=set_txt2img, inputs=ret_list, outputs=pos_prompt_comp)
            apply_tags_button.click(fn=update_new_prompt, inputs=ret_list, outputs=new_prompt_box)
            clear_dropdowns_button.click(fn=clear_dropdowns, inputs=ret_list, outputs=ret_list)

        with gr.Tab(label="Tag Editor"):
            global database_dict

            with gr.Row():
                for file in [csv_file for csv_file in list(database_dict.keys()) if csv_file != "template.csv"]:
                    file_name = file.split(".")[0].replace("_", " ")
                    with gr.Tab(label=f"{file_name}"):
                        with gr.Column():
                            with gr.Row():
                                with gr.Column(scale=7):
                                    search_dropdown = gr.Dropdown(label="Search By Keyword", type="value", interactive=True,
                                                                  choices=token_list, multiselect=True)

                                with gr.Column(scale=1):
                                    filter_dropdown = gr.Dropdown(choices=["All", "Section", "Multiselect", "Category", "Label", "Tag"],
                                                                  type="value", label="Filter By...", value="All",
                                                                  multiselect=False, interactive=True)

                            dataframe = gr.DataFrame(value=database_dict[file], interactive=True)
                            file_name = gr.Label(value=file, visible=False)
                            search_dropdown.change(fn=update_choices, inputs=[search_dropdown, filter_dropdown, file_name],
                                                   outputs=dataframe)

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

