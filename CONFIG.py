import os, sys

main_path = os.path.dirname(sys.argv[0])
list_path = os.path.join(main_path, "lists/")
template_dir = os.path.join(main_path, "templates/")

label_font = ('Arial', 12, 'bold')
desc_font = ('Arial', 12, 'italic')
text_font = ('Arial', 9)

field_params = {
                "text": ["name", "default"],
                "date": ["name"], 
                "check": ["name","content"], 
                "radio": ["name","content"], 
                "drop": ["name","content"], 
                "drop2": ["name","content"], 
                "repeat": ["name","shift"]
               }

MAX_NUM_SPLITS = 5

START, CLOSE = "[", "]"
TITLE_END, PARAM_SEP, PARAM_SET = ".", ",", "="
SPLIT = "[split]"

BOLD_SPLIT = "~"

NORM_FONT = 'style="font-family:Courier New;font-size:9"'
BOLD_FONT = 'style="font-family:Calibri;font-size:12;font-weight:bold"'
TITLE_FONT = 'style="font-family:Calibri;font-size:16;font-weight:bold"'


