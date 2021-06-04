from tkinter.ttk import Scrollbar
from tkinter import Frame, Entry, Label, StringVar, IntVar, Checkbutton, Radiobutton, Text, Toplevel, Canvas
from tkinter import WORD, END, NORMAL, DISABLED, VERTICAL, LEFT
from datetime import datetime, timedelta
from tkinter.constants import NO
from CONFIG import list_path, label_font, desc_font, title_font, entry_width, \
    NORM_FONT, DATE_FORMAT, START, CLOSE
import os

# Field classes

def dateValid(date):
    return len(date) >= 6 and date.count("/") == 2 and len(date.split("/")[2]) == 2


class Field:
    def __init__(self, id, code_string, type, params_dict, root, updateMethod):
        self.id = id
        self.code_string = code_string
        self.type = type
        self.params_dict = params_dict
        if type == "repeat":
            self.updateMethod = lambda: updateMethod(params_dict["name"], repeat=True)
        else:
            self.updateMethod = lambda: updateMethod(params_dict["name"])
        self.values = []
        self.text_values = []
        self.frame = Frame(root)
    
    def getShift(self):
        if "shift" in self.params_dict:
            return int(self.params_dict["shift"])
        else:
            return 0
    
    def getName(self):
        return self.params_dict["name"]
    
    def getID(self):
        return self.id
    
    def getType(self):
        return self.type
    
    def getText(self, blank=False, shift=0):
        raise NotImplementedError("Extend .getText()")
    
    def set(self):
        raise NotImplementedError("Extend .set()")
    
    def getContent(self):
        if "content" in self.params_dict:
            if os.path.isfile(os.path.join(list_path, self.params_dict["content"])):
                f = open(os.path.join(list_path, self.params_dict["content"]))
                lst_options = f.read()
                f.close()
            else:
                lst_options = self.params_dict["content"]
            return lst_options
    
    def pack(self):
        self.frame.pack(pady=5, fill="both", expand=True)
    
    def makeLabel(self, text=None, row=0, column=0, font=None, **kwargs):
        if not font:
            font = label_font
        if not text:
            text = self.getName().title() + ":"
        Label(self.frame, text=text, font=font).grid(row=row, column=column, **kwargs)
    
    def __getattr__(self, name): 
        return lambda *args, **kwargs: getattr(Frame, name)(self.frame, *args, **kwargs)

class Textfield(Field):
    def set(self):
        self.makeLabel(sticky="w")
        self.default_text = self.params_dict["default"] if "default" in self.params_dict else ""
        if len(self.default_text) < entry_width and self.default_text != "^":
            self.values = StringVar()
            self.values.set(self.default_text)
            self.values.trace_add("write", lambda *args: self.updateMethod())
            Entry(self.frame, width=entry_width, textvariable=self.values).grid(row=1, column=0, sticky="w")
        else:
            if self.default_text == "^":
                self.default_text = ""
            self.values = Text(self.frame, wrap=WORD, width=entry_width*2, 
                               height=min(4,len(self.default_text)//entry_width))
            self.values.insert(1.0, self.default_text)
            self.values.bind("<Any-KeyPress>", lambda *args: self.updateMethod())
            self.values.grid(row=1, column=0, sticky="w")
        self.pack()
    
    def getText(self, blank=False):
        if isinstance(self.values, StringVar):
            response = self.values.get()
        else:
            response = self.values.get("1.0", END)[:-1]
        if blank or response:
            return response
        else:
            return START + self.getName() + CLOSE

class Datefield(Field):
    def set(self):
        self.makeLabel(padx=3)
        self.values = StringVar()
        self.values.set(self.params_dict["default"] if "default" in self.params_dict else "")
        self.values.trace_add("write", self.update)
        Entry(self.frame, width=5, textvariable=self.values).grid(row=0, column=1, padx=3)
        self.makeLabel(text="MM/DD/YY", font=desc_font, column=2, padx=3)
        self.pack()
    
    def update(self, *args):
        if dateValid(self.values.get()):
            self.updateMethod()
    
    def getText(self, blank=False):
        if dateValid(string := self.values.get()):
            date_list = string.split("/")
            try:
                return datetime(int("20" + date_list[2]), int(date_list[0]), int(date_list[1])).strftime(DATE_FORMAT)
            except ValueError:
                pass
        if blank:
            return ""
        else:
            return START + self.getName() + CLOSE

class Checkfield(Field):
    def set(self):
        self.makeLabel(sticky="w")
        lst_options = self.getContent()
        self.text_values = lst_options.split("\n")
        for num, option in enumerate(self.text_values):
            self.values.append(IntVar())
            Checkbutton(self.frame, text=option, variable=self.values[num],
                        command=self.updateMethod).grid(row=num+1, column=0)
        self.pack()

    def getText(self, blank=False):
        if any(item.get() for item in self.values):
            return "\n".join([item for num, item in enumerate(self.text_values) if self.values[num].get()])
        elif blank:
            return ""
        else:
            return START + self.getName() + CLOSE

class Radiofield(Field):
    def set(self):
        self.makeLabel(sticky="w")
        lst_options = self.getContent()
        self.text_values = lst_options.split("\n")
        self.values = IntVar()
        self.values.set(-1)
        for num, option in enumerate(self.text_values):
            Radiobutton(self.frame, text=option, variable=self.values, value=num, 
                        command=self.updateMethod).grid(row=num+1, column=0)
        self.pack()

    def getText(self, blank=False):
        if (value := self.values.get()) > -1:
            return self.text_values[value]
        elif blank:
            return ""
        else:
            return START + self.getName() + CLOSE

class Dropfield(Field):
    def set(self):
        self.makeLabel(sticky="w")
        lst_options = self.getContent()
        self.text_values = lst_options.split("\n")
        self.values = StringVar()
        self.values.trace_add("write", lambda a, b, c: self.updateMethod())
        Search(self.frame, lst=self.text_values).grid(row=1, column=0)
        self.pack()

    def getText(self, blank=False):
        return string if (string := self.values.get()) else ("" if blank else START + self.getName() + CLOSE)

class Drop2field(Field):
    def set(self):
        self.makeLabel(padx=3, sticky="w")
        self.text_values = self.processText()
        self.values.append(Search(self.frame, list(self.text_values)))
        self.values[0].stringvar.trace_add("write", self.updateSearchList)
        self.values.append(Search(self.frame, ["Select list on the right"]))
        self.values[1].stringvar.trace_add("write", self.updateAll)
        self.values.append(Label(self.frame, text="", font=desc_font))
        for num, widget in enumerate(self.values):
            widget.grid(row=1+num, column=0, padx=3)
        self.pack()
    
    def updateSearchList(self):
        entry1 = self.values[0].get()
        if entry1 in self.text_values:
            self.values[1].set("")
            self.values[1].lst = list(self.text_values[entry1])
            self.values[1].updateList()
    
    def updateAll(self):
        entry1, entry2 = self.values[0].get(), self.values[1].get()
        if entry1 in self.text_values and entry2 in self.text_values[entry1]:
            self.values[2].config(text=self.text_values[entry1][entry2])
            self.updateMethod()

    def getText(self, blank=False):
        entry = "".join([item.get() for item in self.values[:2]])
        if entry:
            return entry
        elif blank:
            return ""
        else:
            return START + self.getName() + CLOSE
    
    def processText(self):
        content_dict = {}
        for lst in self.getContent().replace("\n\t","\t").split("\n"):
            content_lst = lst.split("\t")
            content_dict[content_lst[0]] = dict(entry.split(":") for entry in content_lst[1:])
        return content_dict

class Repeatfield(Field):
    def __init__(self, id, code_string, type, params_dict, root, updateMethod, repeatMethod):
        super().__init__(id, code_string, type, params_dict, root, updateMethod)
        self.repeatMethod = repeatMethod
        self.disabled_color = "#aaaaaa"
    
    def set(self):
        if "shift" in self.params_dict:
            self.values.append(IntVar())
            self.values.append(StringVar())
            self.values[1].trace_add("write", lambda a, b, c: self.updateMethod())
            Checkbutton(self.frame, text="Enable", variable=self.values[0], 
                        command=self.toggleActivity).grid(row=0, column=0, columnspan=3, sticky="w")
            self.text_values.append(Label(self.frame, text=self.getName().title() + ", shifted by " + \
                self.params_dict["shift"] + ":", font=label_font, fg=self.disabled_color))
            self.text_values[0].grid(row=1, column=0, padx=3)
            self.text_values.append(Entry(self.frame, width=5, textvariable=self.values[1], state=DISABLED))
            self.text_values[1].grid(row=1, column=1, padx=3)
            self.text_values.append(Label(self.frame, text="MM/DD/YY", font=desc_font, fg=self.disabled_color))
            self.text_values[2].grid(row=1, column=2, padx=3)
            self.pack()
        else:
            return
    
    def toggleActivity(self):
        if self.values[0].get():
            self.text_values[0].config(fg="#000")
            self.text_values[1].config(state=NORMAL)
            self.text_values[2].config(fg="#000")
        else:
            self.text_values[0].config(fg=self.disabled_color)
            self.text_values[1].config(state=DISABLED)
            self.text_values[2].config(fg=self.disabled_color)
    
    def getText(self):
        if "shift" in self.params_dict:
            if dateValid(string := self.values[1].get()):
                date_list = string.split("/")
                try:
                    return datetime(int("20" + date_list[2]), int(date_list[0]), int(date_list[1])).strftime(DATE_FORMAT)
                except ValueError:
                    pass
            return START + self.getName() + ", shifted " + str(self.getShift()) + CLOSE
        else:
            return string if (string := self.repeatMethod(self.getName())) else START + self.getName() + CLOSE
    
    def setText(self, text):
        if "shift" in self.params_dict:
            month, day = text.split("/")
            now = datetime.now()
            date = datetime(now.year, int(month), int(day))
            if date < now:
                date = datetime(now.year + 1, int(month), int(day))
            date = date + timedelta(days=self.getShift())
            self.values[1].set(date.strftime("%m/%d/%y"))
            self.values[0].set(0)
            self.toggleActivity()

# Non-Field Classes

class HelpBox:
    def __init__(self, widget, title, message):
        self.root = widget.master
        self.widget = widget
        self.title = title
        self.message = message
        self.widget.bind('<Button-1>', self.popup)

    def popup(self, event):
        window = Toplevel(self.root)
        l0 = Label(window, text=self.title, font=title_font, justify=LEFT)
        f0 = Frame(window)
        t0 = Text(f0, height=30, width=75, wrap=WORD)
        s0 = Scrollbar(f0)
        t0.config(yscrollcommand=s0.set)
        s0.config(command=t0.yview)

        t0.insert(END, self.message)

        t0.config(state=DISABLED)
        t0.pack(side=LEFT)
        l0.pack()
        f0.pack()

class TkExceptionHandler:
    def __init__(self, func, subst, widget):
        self.func = func
        self.subst = subst
        self.widget = widget

    def __call__(self, *args):
        if self.subst:
            args = self.subst(*args)
        return self.func(*args)

class ScrollableFrame(Frame):
    def __init__(self, root, *args, **kwargs):
        self.root = root
        self.mainframe = Frame(root, *args, **kwargs)
        self.canvas = Canvas(self.mainframe, height=kwargs["height"])
        self.scrollbar = Scrollbar(self.mainframe, orient=VERTICAL, command=self.canvas.yview)
        super().__init__(self.canvas)
        self.bind("<Configure>", self.reconfigure)
        self.bind("<MouseWheel>", self.on_mousewheel)
        self.canvas.create_window((0, 0), window=self, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
    
    def reconfigure(self, *args):
        self.root.update()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def on_mousewheel(self, event):
        self.canvas.yview_scroll(-1*(event.delta/120), "units")
    
    def grid(self, **kwargs):
        self.mainframe.grid(**kwargs)

class TextHTML(Text):
    def __init__(self, root, **kwargs):
        super().__init__(root, **kwargs)
        self.font_lst = []
    
    def setHTML(self, html):
        self.delete(1.0, END)
        for frag in html.split("<span style=\""):
            if frag:
                style, content = frag.split("\">", 1)
                font = tuple([pair.split(":")[1] for pair in style.split(";")])
                if font not in self.font_lst:
                    self.tag_configure(len(self.font_lst), font=font)
                    self.font_lst.append(font)
                self.insert(END, content.replace("</span>","").replace("&nbsp", " ").replace("<br />", "\n") \
                    .replace("&lt;", "<").replace("&gt;", ">"), self.font_lst.index(font))

class Font:
    def __init__(self, font=NORM_FONT[0], size=NORM_FONT[1], style=NORM_FONT[2]):
        self.font = (font, size, style)
    
    def getFont(self):
        return self.font
    
    def getHTML(self, content):
        content_lst = [entry2 for entry1 in content.split(START) for entry2 in entry1.split(CLOSE)]
        for num, entry in enumerate(content_lst):
            if not num % 2:
                content_lst[num] = entry.replace(" ", "&nbsp").replace("<", "&lt;") \
                                        .replace(">", "&gt;").replace("\n", "<br />")
            else:
                content_lst[num] = START + entry + CLOSE
        return f'<span style="font-family:{self.font[0]};font-size:{self.font[1]};font-weight:{self.font[2]}">' + \
            ''.join(content_lst) + "</span>"

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
        self.toplevel.wm_overrideredirect()
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
        else: 
            return "" 
    
    def set(self, user_input): 
        self.stringvar.set(user_input)
    
    def __getattr__(self, name): 
        return lambda *args, **kwargs: getattr(Entry, name)(self.entry, *args, **kwargs)
