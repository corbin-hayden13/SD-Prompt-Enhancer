# Stable Diffusion Prompt Enhancer v2.0
### Changelog
 * Added support for multiple tag csv files
 * Added template.csv to guide users in adding their own tags with the correct format
 * Added button to add tags to the prompt textbox
 * Added some more default tags

Credit for v1.0 goes to [etcroot](https://github.com/etcroot) and [Dreamlabs](https://civitai.com/user/Dreamlabs/models) for the original idea

## Welcome to the SD Prompt Enhancer script! Here to help you generate higher quality and more consistent images!

### Things to know when adding your own tags:
 * Tags have 5 attributes:
   - Section (string): This is the overall theme the tag belongs to, like "Camera Settings" or "Image Attributes"
   - Multiselect (binary/boolean): This is a TRUE/FALSE value that determines whether multiple tags from the same category can be applied to the
                                   prompt at once.  A camera setting for the different types of shots should be Multiselect: FALSE because it
                                   it doesn't make sense to ask for both a "Cowboy Shot" and "Long Shot"
   - Category (string): This is going to be the name of your dropdown, so it'slike a smaller group inside of Section.
                        Ex: Section - Image Attributes, Category - Lighting
   - Label (string): This is going to be the option that you see within the dropdown menu.  It's most often an abbreviation of the actual tag
   - Tag (string): This is the actual text that will be applied to the prompt.  As of the current version, is only visible on the front end
                   after generating an image using the script UI and selecting the corresponding Label

 * ALL TAGS MUST HAVE ALL ATTRIBUTES
   - Future releases will provide a client-side imterface to edit the database, but for now it can be edited manually
   - Do your best to keep tags of the same category next to each other within the csv.  I haven't tested a messy tag environment, but I will
     work on a more robust csv parser within the script to avoid potetial issues.
   - Do NOT edit any of the values in row one, as those are the column headers and required to read the csv in python

### Installing the script will now be slightly more involved, but not by much.
 * BOTH sd_prompt_enhancer.py AND prompt_enhancer_tags.csv must be in the same directory / folder to work properly.
 * BOTH files must be placed within your "scripts" folder.  They will not work if they are in a folder within the "scripts" folder
   - Correct: "scripts/sd_prompt_enhancer.py", "scripts/prompt_enhancer_tags.csv"
   - Incorrect: "scripts/subdirectory/prompt_enhancer_tags.csv", "automatic/sd_prompt_enhancer.py"

Thank you for using the Stable Diffusion Prompt Enhancer script!  As always please report any issues, concerns, and feature ideas on the model
[webpage](https://civitai.com/models/58869/sd-prompt-enhancer)
