from Field import Field, Textfield, Datefield, Checkbutton, Radiobutton, Dropfield, Drop2field, Repeatfield
from collections import defaultdict
from CONFIG import field_params, MAX_NUM_SPLITS, START, CLOSE, TITLE_END, PARAM_SET, \
    PARAM_SEP, SPLIT, BOLD_SPLIT, NORM_FONT, BOLD_FONT, TITLE_FONT
import klembord


def formatField(text):
    text_lst = text.split("\"")
    final = ""
    for num, entry in enumerate(text_lst):
        if num % 2:
            final += entry
        else:
            final += entry.lower().replace(" ", "").replace("\n","")
    return final

def processText(title, text, root, updateMethod, returnRepeat):
    text_lst = []
    vars_dict = {}
    repeat_dict = defaultdict(list)
    if text.count("[split]") > MAX_NUM_SPLITS:
        raise SyntaxError("Too many split tags in template document: " + title)
    for num, pseudo_frag in enumerate(text.split(START)):
        if not num:
            text_lst.append(pseudo_frag)
        elif pseudo_frag.count(CLOSE) != 1 and num:
            raise SyntaxError("Incorrect bracket usage in template document: " + title)
        else:
            frags = pseudo_frag.split(CLOSE, 1)
            field_pair = formatField(frags[0]).split(TITLE_END, 1)
            if field_pair[0] not in field_params:
                raise SyntaxError("Unrecognized field type in " + title + ": " + field_pair[0])
            params = dict([pair.split(PARAM_SET,1) for pair in field_pair[1].split(PARAM_SEP)])
            if not all(param in field_params[field_pair[0]] for param in params):
                raise SyntaxError("Unrecognized parameter in " + title + " for " + field_pair[0] + ": " + \
                                    set(params).difference(set(field_params[field_pair[0]])).pop())
            if "name" not in params:
                raise SyntaxError("'Name' parameter missing in " + title + " for " + field_pair[0])
            if "content" not in params and "content" in field_params[field_pair[0]]:
                raise SyntaxError("'Content' parameter missing in " + title + " for " + field_pair[0])
            field_obj = Field(num, START + frags[0] + CLOSE, field_pair[0], params, root, updateMethod, returnRepeat)
            text_lst.extend([field_obj, frags[1]])
            if field_obj.getType() != "repeat":
                vars_dict[field_obj.getName()] = field_obj
            else:
                repeat_dict[field_obj.getName()].append(field_obj)
    return text_lst, vars_dict, repeat_dict


class Order:
    def __init__(self, title, text, root, updateMethod):
        self.text = text
        self.updateMethod = updateMethod
        self.text_lst, self.vars_dict, self.repeat_dict = \
            processText(title, text, root, self.updateMethod, self.returnRepeat)

    def updateField(self, name):
        if name in self.repeat_dict:
            text = self.vars_dict[name].getText()
            for field in self.repeat_dict[name]:
                field.setText(text)
        self.updateMethod()
    
    def returnRepeat(self, name, shift):
        return self.vars_dict[name].getText(shift)
    
    def getFieldObjects(self):
        return self.vars_dict.values()

    def getText(self):
        full_text = ""
        for frag in self.text_lst:
            if isinstance(frag, Field):
                full_text += frag.getText()
            else:
                full_text += frag
        return full_text
    
    def getCopy(self, section):
        text = self.getText().split(SPLIT)[section]
        text_list = text.split(BOLD_SPLIT)
        start_tag = "<pre "
        end_tag = "</pre>"
        formatted_text = ""
        for num, entry in enumerate(text_list):
            if not num % 2 and entry:
                    formatted_text += start_tag + NORM_FONT + ">" + entry + end_tag
            elif entry:
                if num == 1:
                     formatted_text += start_tag + TITLE_FONT + ">" + entry + end_tag
                else:
                    formatted_text += start_tag + BOLD_FONT + ">" + entry + end_tag

        klembord.set_with_rich_text(text.replace(BOLD_SPLIT, ""), formatted_text)
        # TODO: verify it works w/o klembord.init()

