from tkinter import Frame, Entry, Checkbutton, Radiobutton, Label, StringVar, IntVar
from tkinter.ttk import Combobox
from datetime import datetime, timedelta
import os
import sys

main_path = os.path.dirname(sys.argv[0])
list_path = os.path.join(main_path, "lists/")
label_font = ('Arial', 12, 'bold')
desc_font = ('Arial', 12, 'italic')


class Field:
    def __init__(self, id, code_string, type, params_dict, root, updateMethod, repeatMethod):
        self.id = id
        self.code_string = code_string
        self.type = type
        self.params_dict = params_dict
        self.updateMethod = lambda: updateMethod(params_dict["name"])
        self.repeatMethod = repeatMethod
        self.values = []
        self.text_values = []
        self.misc = []
        self.frame = Frame(root)
    
    def set(self):
        if self.type == "repeat":
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

        elif self.type in ["text", "date"]:
            Label(self.frame, text=self.getName().title() + ":", font=label_font).grid(row=0, column=0, padx=3)
            self.values.append(StringVar())
            self.values[0].set(self.params_dict["default"] if "default" in self.params_dict else "")
            self.values[0].trace_add("write", lambda a, b, c: self.updateMethod())
            Entry(self.frame, width=5, textvariable=self.values[0]).grid(row=0, column=1, padx=3)
            if self.type == "date":
                Label(self.frame, text="MM/DD/YY", font=desc_font).grid(row=0, column=2, padx=3)

        elif self.type == "check":
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

        elif self.type == "radio":
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

        elif self.type == "drop":
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
            Combobox(self.frame, values=self.text_values, 
                     textvariable=self.values[0]).grid(row=0, column=1, padx=3)

        elif self.type == "drop2":
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
            self.misc.append(Combobox(self.frame, values=self.text_values, textvariable=self.values[0]))
            self.misc.append(Combobox(self.frame, values=self.text_values[list(self.text_values)[0]], 
                                      textvariable=self.values[1]))
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
    
    def getText(self, shift=0):
        if self.type == "repeat":
            return string if (string := self.repeatMethod(self.getName(), self.getShift())) else self.code_string

        elif self.type == "text":
            return string if (string := self.values[0].get()) else self.code_string
        
        elif self.type == "date":
            if len(string := self.values[0].get()) == 8:
                date_list = string.split("/")
                date = datetime(int("20" + date_list[2]), int(date_list[0]), int(date_list[1])) + timedelta(days=shift)
                return date.strftime("%a, %b %d")
            else:
                return self.code_string

        elif self.type == "check":
            if any(item.get() for item in self.values):
                return "\n".join([item for num, item in enumerate(self.text_values) if self.values[num].get()])
            else:
                return self.code_string

        elif self.type == "radio":
            if (value := self.values[0].get()) > -1:
                return self.text_values[value]
            else:
                return self.code_string

        elif self.type == "drop":
            return string if (string := self.values[0].get()) else self.code_string

        elif self.type == "drop2":
            return [item.get for item in self.value]
    
    def setText(self, text):
        if len(text) == 8:
            date_list = text.split("-")
            date = datetime(int("20" + date_list[2]), int(date_list[0]), int(date_list[1])) + timedelta(days=self.getShift())
            self.values[0](date.strftime("%m-%I-%y"))
