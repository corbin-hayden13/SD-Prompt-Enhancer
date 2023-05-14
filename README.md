Credit for v1.0 goes to [etcroot](https://github.com/etcroot) and [Dreamlabs](https://civitai.com/user/Dreamlabs/models) for the original idea

## Welcome to the SD Prompt Enhancer script! Here to help you generate higher quality and more consistent images!

### You can now find user tag files [here](https://drive.google.com/drive/folders/1NAIa2riHAS9Cvjar_ah_Ebtj5m2fmsM6?usp=sharing) and I'm working on enabling requests to add community tag files to this list
 * Requests must be made to have you tags added (for content curation purposes), I will add a link to a form to fill out here soon
 * I'm trying to find a convenient solution to hosting community tag files, so if you have a solution let me know!

### Things to know when adding your own tags:

#### Adding via the webui

 * In this extension release I have implemented the feature of adding tags to your current csv files from within the webui
   - Limitations include:
     - No option to delete tags from within the webui
     - No option to create tables within the UI
   - I plan to add features to remedy these limitations in the future
 * When you press the add tag button, it will add the tag you created, it just will not visually indicate that you did.  I plan to make this more apparent in the future
 * You have to restart the client side UI to display any added tags.
 * You might get a permission error when creating new tags.  This is either due to your csv files being Read-Only, or you have a csv file you're trying to write to open in a different editor.

#### Manually adding tags

 * Tags have 5 attributes:
   - Section (string): This is the overall theme the tag belongs to, like "Camera Settings" or "Image Attributes"
   - Multiselect (binary/boolean): This is a TRUE/FALSE value that determines whether multiple tags from the same category can be applied to the prompt at once.  A camera setting for the different types of shots should be Multiselect: FALSE because it doesn't make sense to ask for both a "Cowboy Shot" and "Long Shot"
     - If you choose Multiselect: FALSE, you will have to add two tags to the category -> {"null":"null"} and {"none":"null"}.  This has to do with a dictionary issue in the script, but also allows you to "disable" your previous choice for that category, as Multiselect: FALSE dropdowns in Gradio have no default "None" option
   - Category (string): This is going to be the name of your dropdown, so it's like a smaller group inside of Section.
     - Ex: Section - Image Attributes, Category - Lighting
   - Label (string): This is going to be the option that you see within the dropdown menu.  It's most often an abbreviation of the actual tag
   - Tag (string): This is the actual text that will be applied to the prompt.  As of the current version, is only visible on the front end after generating an image using the script UI and selecting the corresponding Label

 * ALL TAGS MUST HAVE ALL ATTRIBUTES
   - Future releases will provide a client-side imterface to edit the database, but for now it can be edited manually
   - Tags don't need to be contiguous / clumped together if they're in the same category or section, you can just add new tags to the end of the file
   - Do NOT edit any of the values in row one, as those are the column headers and required to read the csv in python

### Installing the script will now be slightly more involved, but not by much.

#### Installing via Extensions tab in webui

 * You can now directly install this extension by copying and pasting the repo link into the option to install from link in your webui's extension tab
 * I recommend you use this method to install the extension

#### Manually adding files

 * You can download the zip file from my CivitAi page (linked below).  Unzip that file and put the "SD-Prompt-Enhancer" folder right into your extensions folder in your local installation.  that's it!
 * CivitAi vesions may be out of date at any given time, as I will only upload zipped version updates after large feature changes.  However, this repo will always be up-to-date

Thank you for using the Stable Diffusion Prompt Enhancer script!  As always please report any issues, concerns, and feature ideas on the model
[webpage](https://civitai.com/models/58869/sd-prompt-enhancer)
