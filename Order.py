from Field import Field, Font, Checkfield, Radiofield, Textfield, Datefield, \
    Checkbutton, Radiobutton, Dropfield, Drop2field, Repeatfield
from collections import defaultdict
from CONFIG import field_params, misc_tags, MAX_NUM_SPLITS, START, CLOSE, \
    TITLE_END, PARAM_SET, PARAM_SEP, SPLIT, BOLD_SPLIT, BOLD_FONT


def formatField(text):
    '''Remove whitespace and lower case unless within quotes'''
    text_lst = text.split("\"")
    final = ""
    for num, entry in enumerate(text_lst):
        if num % 2:
            final += entry
        else:
            final += entry.lower().replace(" ", "").replace("\n","")
    return final

def formatText(title, text):
    '''Replace 'format' tags with HTML and separate text by 'split' tags'''
    text_lst = []
    edited_text = ""
    # Remove spaces/newlines found between brackets & outside of quotes
    for num, entry in enumerate(text.split(START)):
        if num:
            if entry.count(CLOSE) != 1:
                raise SyntaxError("Incorrect bracket usage in template document: " + title)
            else:
                frag = entry.split(CLOSE)
                edited_text += formatField(START + frag[0] + CLOSE) + frag[1]
        else:
            edited_text += entry
    # Format no-param tags to remove TITLE_END
    edited_text = edited_text.replace(TITLE_END + CLOSE, CLOSE)
    # Split text on 'split' tags
    if edited_text.count(SPLIT) > MAX_NUM_SPLITS:
        raise SyntaxError("Too many split tags in template document: " + title)
    for section in edited_text.split(SPLIT):
        # Replace BOLD_SPLIT tags with 'format' tags
        format_tags = [f"{START}format{TITLE_END}font{PARAM_SET}\"{BOLD_FONT[0]}\"{PARAM_SEP}" + \
            f"size{PARAM_SET}{BOLD_FONT[1]}{PARAM_SEP}style{PARAM_SET}{BOLD_FONT[2]}{CLOSE}", 
            f"{START}endformat{CLOSE}"]
        section = ''.join([(format_tags[0] + entry + format_tags[1] if num % 2 else entry) \
            for num, entry in enumerate(section.split(BOLD_SPLIT))])
        # Split text to list before 'format' tag and after 'endformat' tag
        temp_lst = []
        for num, entry in enumerate([(f"{START}format{TITLE_END}" + entry if num else entry) 
            for num, entry in enumerate(section.split(f"{START}format{TITLE_END}"))]):
            if num:
                temp_sublist = entry.split(f"{START}endformat{CLOSE}")
                if len(temp_sublist) != 2:
                    raise SyntaxError("Incorrect usage of 'format' start/end tags " + \
                                    "in template document: " + title)
                else:
                    temp_lst.extend(temp_sublist)
            else:
                if entry:
                    temp_lst.append(entry)
        # Replace 'format' tags with HTML
        section = ""
        for entry in temp_lst:
            if f"{START}format." == entry[:8]:
                entry = entry[8:]
                params, entry = entry.split(CLOSE, 1)
                params_dict = {}
                for item in params.split(PARAM_SEP):
                    temp_sublist = item.split(PARAM_SET, 1)
                    if temp_sublist[0] not in misc_tags["format"]:
                        raise SyntaxError("Unrecognized 'format' parameter in " +
                                        title + ": " + temp_sublist[0])
                    params_dict[temp_sublist[0]] = temp_sublist[1]
                section += Font(**params_dict).getHTML(entry)
            elif entry:
                section += Font().getHTML(entry)
        text_lst.append(section)
    return text_lst

def processText(title, text, root, updateMethod, repeatMethod):
    '''Convert list of strings to list of lists for Order class'''
    text_lst = formatText(title, text)
    vars_dict = {}
    repeat_dict = defaultdict(list)
    for indx, section in enumerate(text_lst):
        section_lst = []
        for num, pseudo_frag in enumerate(section.split(START)):
            if not num:
                section_lst.append(pseudo_frag)
            else:
                # frags[0] is field + params, frags[1] is content following it
                frags = pseudo_frag.split(CLOSE, 1)
                # field_pair[0] is field name, field_pair[1] is parameter string
                field_pair = frags[0].split(TITLE_END, 1)
                # params_dict is dictionary of parameters
                params_dict = dict([pair.split(PARAM_SET,1) for pair in field_pair[1].split(PARAM_SEP)])
                # Catching errors
                if field_pair[0] not in field_params:
                    raise SyntaxError("Unrecognized field type in " + title + ": " + field_pair[0])
                if not all(param in field_params[field_pair[0]] for param in params_dict):
                    raise SyntaxError("Unrecognized parameter in " + title + " for " + field_pair[0] + ": " + \
                                        set(params_dict).difference(set(field_params[field_pair[0]])).pop())
                if "name" not in params_dict:
                    raise SyntaxError("'Name' parameter missing in " + title + " for " + field_pair[0])
                if "content" not in params_dict and "content" in field_params[field_pair[0]]:
                    raise SyntaxError("'Content' parameter missing in " + title + " for " + field_pair[0])
                # Make Field objects
                obj_params = (num, START + frags[0] + CLOSE, field_pair[0], params_dict, root, updateMethod)
                if field_pair[0] == "repeat": 
                    field_obj = Repeatfield(*obj_params, repeatMethod)
                    repeat_dict[field_obj.getName()].append(field_obj)
                else:
                    field_obj = globals()[field_pair[0].title() + "field"](*obj_params)
                    vars_dict[field_obj.getName()] = field_obj
                section_lst.extend([field_obj, frags[1]])
        text_lst[indx] = section_lst
    return text_lst, vars_dict, repeat_dict


class Order:
    def __init__(self, title, text, root, updateMethod):
        self.updateMethod = updateMethod
        self.text_lst, self.vars_dict, self.repeat_dict = \
            processText(title, text, root, self.updateMethod, self.returnRepeat)
        print(self.text_lst)
        sys

    def updateField(self, name):
        if name in self.repeat_dict:
            text = self.vars_dict[name].getText(blank=True)
            for field in self.repeat_dict[name]:
                field.setText(text)
        self.updateMethod()
    
    def returnRepeat(self, name, shift):
        return self.vars_dict[name].getText(shift)
    
    def getFieldObjects(self):
        return self.vars_dict.values()

    def getText(self, section, return_html=False):
        html = self.getHTML(section)
        text = html.replace("<br \>", "\n").replace("&nbsp", " ")
        text = ''.join([entry2 for entry1 in text.split("<") for entry2 in entry1.split(">")][::2])
        text = text.replace("&lt;", "<").replace("&gt;", ">")
        if return_html:
            return text, html
        else:
            return text
    
    def getHTML(self, section=-1):
        html = ""
        if section == -1:
            if (num_sections := len(self.text_lst)) > 1:
                for num in range(num_sections):
                    html += "\n="*10 + "SECTION " + str(num+1) + "="*10 + "\n" + self.getHTML(num)
            elif num_sections == 1:
                html += self.getHTML(0)
        else:
            for frag in self.text_lst[section]:
                if isinstance(frag, Field):
                    html += frag.getText()
                else:
                    html += frag
        return html

