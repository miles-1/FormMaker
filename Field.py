from tkinter import Frame, Entry, Label, StringVar, IntVar, Checkbutton, Radiobutton, Text, Toplevel
from tkinter import WORD, END
from datetime import datetime, timedelta
from CONFIG import list_path, label_font, desc_font, NORM_FONT, BOLD_FONT
import os


class TextHTML(Text):
    def __init__(self, root, **kwargs):
        super().__init__(root, **kwargs)
        self.font_lst = []
    
    def setHTML(self, html):
        self.delete(1.0, END)
        for frag in html.split("<pre style=\""):
            if frag:
                for style, content in frag.split("\">", 1):
                    font = tuple([pair.split(":")[1] for pair in style.split(";")])
                    if font not in self.font_lst:
                        self.tag_configure(len(self.font_lst), font=font)
                        self.font_lst.append(font)
                    self.insert(END, content.replace("</pre>","").replace("&nbsp", " ").replace("<br />", "\n") \
                        .replace("&lt;", "<").replace("&gt;", ">"), self.font_lst.index(font))

class Font:
    def __init__(self, font=NORM_FONT[0], size=NORM_FONT[1], style=NORM_FONT[2]):
        self.font = (font, size, style)
    
    def getFont(self):
        return self.font
    
    def getHTML(self, content):
        return f'<span style="font-family:{self.font[0]};font-size:{self.font[1]};font-weight:{self.font[2]}">' + \
            content.replace(" ", "&nbsp").replace("\n", "<br />").replace("<", "&lt;").replace(">", "&gt;") + "</span>"

class Search: 
    '''A widget with features of Entry and Combobox that allows for a dropdown list 
    that 1) dynamically reduces listed options to those that match user input and
    2) allows for arrow key/enter and mouseover/click functionality.'''
    def __init__(self, root, lst, width=15, allow_unlisted=True):
        self.root = root 
        self.lst = lst 
        self.current_lst = lst 
        self.width = width 
        self.allow_unlisted = allow_unlisted 
        self.indices = [0.0] * 2

        self.stringvar = StringVar() 
        self.stringvar.trace_add("write", self.updateList) 
        self.entry = Entry(root, width=self.width, font=("Arial", 9), textvariable=self.stringvar) 
        self.entry.bind("<FocusIn>", self.showList) 
        self.entry.bind("<FocusOut>", self.hideList) 
        self.entry.bind("<Up>", self.keyList) 
        self.entry.bind("<Down>", self.keyList) 
        self.entry.bind("<Return>", self.hideList)

        self.toplevel = None 
        self.text = None
        self.updateList()
    
    def showList(self, *args): 
        self.toplevel = Toplevel(self.root) 
        self.toplevel.attributes("-type", "splash")
        x = self.entry.winfo_rootx() 
        y = self.entry.winfo_rooty() + self.entry.winfo_height()
        self.toplevel.wm_geometry(f"+{x}+{y}")

        self.text = Text(self.toplevel, wrap=WORD, foreground="#333333")
        self.text.config(font=("Arial", 9), width=self.width)
        self.text.tag_configure("highlight", background="dodger blue", foreground="white") 
        self.text.bind("<Motion>", self.motionList) 
        self.text.bind("<Up>", self.keyList) 
        self.text.bind("<Down>", self.keyList) 
        self.text.bind("<Button-1>", self.hideList) 
        self.text.bind("<Return>", self.hideList)
        self.text.pack()
        self.updateList()
    
    def hideList(self, *args): 
        if self.text and self.text.winfo_ismapped():
            self.select()
        if self.toplevel:
            self.toplevel.destroy()
            self.toplevel = self.text = None
        self.root.focus_set()
    
    def updateList(self, *args): 
        var = self.stringvar.get() 
        self.indices = [0.0] * 2 
        self.current_lst = [item for item in self.lst if var.lower() in item.lower()] 
        if self.text: 
            self.text.tag_remove("highlight", 1.0, END)
            self.text.config(height=min(10, len(self.current_lst)))
            self.text.delete(1.0, END)
            self.text.insert(END, "\n".join(self.current_lst))
    
    def motionList(self, event): 
        index1 = float(self.text.index(f"@{event.x},{event.y} linestart"))
        self.highlight(index1) 
    
    def keyList(self, event):
        if event.keysym == "Up" and self.indices[0] > 0: 
            self.indices[0] -= 1 
        elif event.keysym == "Down" and self.indices[0] < len(self.current_lst): 
            self.indices[0] += 1
        if self.indices[0]: 
            self.highlight(self.indices[0]) 
        else: 
            self.indices = [0.0] * 2 
            self.text.tag_remove("highlight", 1.0, END) 
    
    def highlight(self, index1): 
        self.indices = [index1, float(self.text.index(f"{index1} lineend"))] 
        self.text.tag_remove("highlight", 1.0, END) 
        self.text.tag_add("highlight", *self.indices) 
    
    def select(self, *args):
        if self.indices[0]: 
            self.stringvar.set(self.text.get(*self.indices))
    
    def get(self): 
        user_input = self.stringvar.get() 
        if user_input in self.lst or self.allow_unlisted: 
            return user_input 
        else: return "" 
    
    def set(self, user_input): 
        self.stringvar.set(user_input) 
    
    def __getattr__(self, name): 
        return lambda *args, **kwargs: getattr(Entry, name)(self.entry, *args, **kwargs)

class Field:
    def __init__(self, id, code_string, type, params_dict, root, updateMethod):
        self.id = id
        self.code_string = code_string
        self.type = type
        self.params_dict = params_dict
        self.updateMethod = lambda: updateMethod(params_dict["name"])
        self.values = []
        self.text_values = []
        self.misc = []
        self.frame = Frame(root)
    
    def getShift(self):
        if "shift" in self.params_dict:
            return self.params_dict["shift"]
        else:
            return 0
    
    def getName(self):
        return self.params_dict["name"]
    
    def getID(self):
        return self.id
    
    def getType(self):
        return self.type
    
    def getText(self):
        raise NotImplementedError("Extend getText")

class Textfield(Field):
    def set(self):
        Label(self.frame, text=self.getName().title() + ":", font=label_font).grid(row=0, column=0, padx=3)
        self.values.append(StringVar())
        self.values[0].set(self.params_dict["default"] if "default" in self.params_dict else "")
        self.values[0].trace_add("write", lambda a, b, c: self.updateMethod())
        Entry(self.frame, width=5, textvariable=self.values[0]).grid(row=0, column=1, padx=3)
        self.frame.pack(pady=5)
    
    def drop2(self, type=1):
        if type:
            self.misc[1].config(values=self.text_values[self.values[0]])
        self.misc[2].config(text=self.text_values[self.values[0]][self.values[1]])
        self.updateMethod()
    
    def getText(self, shift=0):
        return string if (string := self.values[0].get()) else self.code_string

class Datefield(Field):
    def set(self):
        Label(self.frame, text=self.getName().title() + ":", font=label_font).grid(row=0, column=0, padx=3)
        self.values.append(StringVar())
        self.values[0].set(self.params_dict["default"] if "default" in self.params_dict else "")
        self.values[0].trace_add("write", lambda a, b, c: self.updateMethod())
        Entry(self.frame, width=5, textvariable=self.values[0]).grid(row=0, column=1, padx=3)
        Label(self.frame, text="MM/DD/YY", font=desc_font).grid(row=0, column=2, padx=3)
        self.frame.pack(pady=5)
    
    def getText(self, shift=0):
        if len(string := self.values[0].get()) == 8:
            date_list = string.split("/")
            date = datetime(int("20" + date_list[2]), int(date_list[0]), int(date_list[1])) + timedelta(days=shift)
            return date.strftime("%a, %b %d")
        else:
            return self.code_string

    def setText(self, text):
        if len(text) == 8:
            date_list = text.split("-")
            date = datetime(int("20" + date_list[2]), int(date_list[0]), int(date_list[1])) + timedelta(days=self.getShift())
            self.values[0](date.strftime("%m-%I-%y"))

class Checkfield(Field):
    def set(self):
        Label(self.frame, text=self.getName().title() + ":", font=label_font).grid(row=0, column=0)
        if os.path.isfile(os.path.join(list_path, self.params_dict["content"])):
            f = open(os.path.join(list_path, self.params_dict["content"]))
            lst_options = f.read()
            f.close()
        else:
            lst_options = self.params_dict["content"]
        self.text_values = lst_options.split("\n")
        for num, option in enumerate(self.text_values):
            self.values.append(IntVar())
            Checkbutton(self.frame, text=option, variable=self.values[num],
                        command=self.updateMethod).grid(row=num+1, column=0)

        self.frame.pack(pady=5)

    def getText(self, shift=0):
        if any(item.get() for item in self.values):
            return "\n".join([item for num, item in enumerate(self.text_values) if self.values[num].get()])
        else:
            return self.code_string

class Radiofield(Field):
    def set(self):
        Label(self.frame, text=self.getName().title() + ":", font=label_font).grid(row=0, column=0)
        if os.path.isfile(os.path.join(list_path, self.params_dict["content"])):
            f = open(os.path.join(list_path, self.params_dict["content"]))
            lst_options = f.read()
            f.close()
        else:
            lst_options = self.params_dict["content"]
        self.text_values = lst_options.split("\n")
        self.values.append(IntVar())
        self.values[0].set(-1)
        for num, option in enumerate(self.text_values):
            Radiobutton(self.frame, text=option, variable=self.values[0], value=num, 
                        command=self.updateMethod).grid(row=num+1, column=0)

        self.frame.pack(pady=5)

    def getText(self, shift=0):
        if (value := self.values[0].get()) > -1:
            return self.text_values[value]
        else:
            return self.code_string

class Dropfield(Field):
    def set(self):
        Label(self.frame, text=self.getName().title() + ":", font=label_font).grid(row=0, column=0, padx=3)
        if os.path.isfile(os.path.join(list_path, self.params_dict["content"])):
            f = open(os.path.join(list_path, self.params_dict["content"]))
            lst_options = f.read()
            f.close()
        else:
            lst_options = self.params_dict["content"]
        self.text_values = lst_options.split("\n")
        self.values.append(StringVar())
        self.values[0].trace_add("write", lambda a, b, c: self.updateMethod())
        Search(self.frame, values=self.text_values, 
                    textvariable=self.values[0]).grid(row=0, column=1, padx=3)

        self.frame.pack(pady=5)

    def getText(self, shift=0):
        return string if (string := self.values[0].get()) else self.code_string

class Drop2field(Field):
    def set(self):
        Label(self.frame, text=self.getName().title() + ":", font=label_font).grid(row=0, column=0, padx=3)
        if os.path.isfile(os.path.join(list_path, self.params_dict["content"])):
            f = open(os.path.join(list_path, self.params_dict["content"]))
            lst_options = f.read()
            f.close()
        else:
            lst_options = self.params_dict["content"]
        text_values = lst_options.split("\n")
        current_drop = ""
        self.text_values = {}
        for line in text_values:
            if line[0] != "\t":
                current_drop = line
                self.text_values[line] = {}
            else:
                temp_pair = line.replace("\t", "").split(":", 1)
                self.text_values[current_drop][temp_pair[0]] = temp_pair[1] if len(temp_pair) == 2 else ""
        self.values.extend([StringVar(), StringVar()])
        self.values[0].trace_add("write", lambda a, b, c: self.drop2())
        self.values[1].trace_add("write", lambda a, b, c: self.drop2(0))
        self.misc.append(Search(self.frame, self.text_values))
        self.misc.append(Search(self.frame, self.text_values[list(self.text_values)[0]]))
        self.misc.append(Label(self.frame, text=self.text_values[self.values[0].get()][self.values[1].get()], 
                                font=desc_font))
        for num, widget in enumerate(self.misc):
            widget.grid(row=0, column=1+num, padx=3)
            
        self.frame.pack(pady=5)
    
    def drop2(self, type=1):
        if type:
            self.misc[1].config(values=self.text_values[self.values[0]])
        self.misc[2].config(text=self.text_values[self.values[0]][self.values[1]])
        self.updateMethod()

    def getText(self, shift=0):
        return [item.get for item in self.value]

class Repeatfield(Field):
    def __init__(self, id, code_string, type, params_dict, root, updateMethod, repeatMethod):
        super().__init__(id, code_string, type, params_dict, root, updateMethod)
        self.repeatMethod = repeatMethod
    
    def set(self):
        if "shift" in self.params_dict:
            Label(self.frame, text=self.getName().title() + ", shifted by " + self.params_dict["shift"] + ":", 
                    font=label_font).grid(row=0, column=0, padx=3)
            self.values.append(StringVar())
            self.values[0].trace_add("write", lambda a, b, c: self.updateMethod())
            Entry(self.frame, width=5, 
                    textvariable=self.values[0]).grid(row=0, column=1, padx=3)
            Label(self.frame, text="MM/DD/YY", font=desc_font).grid(row=0, column=2, padx=3)
        else:
            return
        
        self.frame.pack(pady=5)
    
    def getText(self, shift=0):
        return string if (string := self.repeatMethod(self.getName(), self.getShift())) else self.code_string
        # TODO: fix up

