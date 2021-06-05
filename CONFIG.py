import os, sys

main_path = os.path.dirname(sys.argv[0])
list_path = os.path.join(main_path, "lists/")
template_dir = os.path.join(main_path, "templates/")
img_dir = os.path.join(main_path, "help.png")

# Can be changed for program functionality
label_font = ('Arial', 12, 'bold')
desc_font = ('Arial', 12, 'italic')
title_font = ('Arial', 16, 'bold')
text_font = ('Arial', 9)
entry_width = 15
column_width = 300 # pixels
column_height = 500 # pixels

# These are hardcoded in other regions
field_params = {
                "text": ["name", "default"],
                "date": ["name", "type"], 
                "check": ["name","content"], 
                "radio": ["name","content"], 
                "drop": ["name","content"], 
                "drop2": ["name","content"], 
                "repeat": ["name","shift"]
               }

misc_tags = {
             "format": ["font", "size", "style"],
             "endformat": [],
             "split": ["name"]
            }



# These can be changed for template syntax
MAX_NUM_SPLITS = 5
START, CLOSE = "[", "]"
TITLE_END, PARAM_SEP, PARAM_SET = ".", ",", "="
NORM_FONT = ('Courier New', 9, 'normal')
BOLD_FONT = ('Calibri', 12, 'bold')
BOLD_SPLIT = "~"
DATE_FORMAT = "%m/%d"

manual = "\tThis program seeks to allow the quick creation of form-style documents. Specifically, " + \
    "this program is intended for situations where many similar but non-identical versions of " + \
    "a document are required. Here, documentation for program usage is provided.\n\n" + \
    "REQUIRED FILE ORGANIZATION.\n" + \
    "{Any folder}\n" + \
    "|-FormMaker.txt\n" + \
    "|-lists\n" + \
    "| '-{list text documents}\n" + \
    "'-templates\n" + \
    "  '-{template text documents}\n\n" + \
    "TEMPLATE CREATION.\n" + \
    "\tThis program utilizes user-generated text documents (i.e., files with .txt extension) " + \
    "to create generic 'templates' which are then utilized in-program to prompt the user to fill " + \
    "in required information. Templates use special characters and 'tags' to indicate what you desire " + \
    "to accomplish. Below are the list of things you can accomplish in your templates:\n" + \
    "\tTEXT FORMATTING. If you wish for a certain section of your document to contain text of a specified " + \
    "font, use the 'format' tag. Example: the line '[format. font=\"Arial\", size=16, style=italic]Formatted " + \
    "text here![end format]' will format the text 'Formatted text here!' to be of the font Arial, size 16 and " + \
    f"italicized. The default values of 'font', 'size' and 'style' are '{NORM_FONT[0]}', '{NORM_FONT[1]}' and " + \
    f"'{NORM_FONT[2]}' respectively, with these values being used when one is unspecified. These values are " + \
    "also used on all text that is not contained within a 'format' and 'end format' tag. Surrounding a " + \
    f"section of text with '{BOLD_SPLIT}' on either side is short-hand for the 'format' and 'end format' " + \
    f"tag specifying the {BOLD_FONT[0]} font, size {BOLD_FONT[1]}, with {BOLD_FONT[2]} styling. Note " + \
    "that this is the only tag that has a start and an end tag instead of a single tag, is the " + \
    "only tag besides 'split' that doesn't require a name, and is the only tag that can encompass " + \
    "other tags.\n" + \
    "\tTEXT ENTRY. To prompt the input of text in a given area of the document, use the 'text' tag. " + \
    "For example: [text. name=\"Customer name\"] will create an entry field in the program for " + \
    "you to type the customer name. If desired, you may also include a default text value that is " + \
    "put into the entry field by including default=\"\" in the tag. If the value is \"^\" or greater" + \
    f"than {entry_width} characters, a bigger text entry box will appear.\n" + \
    "\tDATE ENTRY. To prompt the input of a date in a given area of the document, use the 'date' tag. " + \
    "For example: [date. name=\"Appointment date\"] will create an entry field in the program for " + \
    "you to type the appointment date. Setting type=\"\" allows users to format dates using info " + \
    "described at strftime.org.\n" + \
    "\tCHECKBOX SELECTION. To prompt the selection of one or more options from a list to include in " + \
    "the final document, use the 'check' tag. For example: [check. name=\"Materials\"," + \
    "content=materialslist.txt] will read the contents of materialslist.txt from the 'lists' folder " + \
    "line by line and create checkboxes from them.\n" + \
    "\tRADIOBUTTON SELECTION. The 'radio' tag is identical to the 'check' tag except that only one " + \
    "option can be selected.\n" + \
    "\tDROPDOWN SELECTION. The 'drop' tag is identical to the 'radio' tag except that it uses a " + \
    "searchable dropdown box. This list can be navigated by arrow keys/enter or mouse. This is " + \
    "prefereable over 'radio' when the list of options is greater than 10 long.\n" + \
    "\tTWO-DROPDOWN SELECTION. The 'drop2' tag is similar to the 'drop' tag except instead of using " + \
    "a basic linebreak-separated text document, it utilizes a list of lists. The 'content' file will " + \
    "be organized not only by line breaks but also tabs. For example, the file may appear like this:\n" + \
    "\nKitchen\n\t1:Pot\n\t2:Pan\n\t3:Bowl\nBathroom\n\t1:Toilet\n\t2:Sink\n\t3:Bathtub\n" + \
    "\n\tThis file is read into the program and used for searchable text entry boxes." + \
    "\n\tREPEAT PREVIOUS ENTRY. This will repeat the text generated from a previous tag as specified " + \
    "by name. Note that this means that you will copy exactly the name assigned to the tag desired " + \
    "to be copied.\n" + \
    "\tSPLIT FORM. The 'split' tag takes no parameters and allows for separate copying of sections " + \
    "within the document as a whole."
