from tkinter import Frame, Radiobutton, Label, IntVar, Button
from tkinter.ttk import Separator
from tkinter import VERTICAL, END, WORD, HORIZONTAL
from Order import Order
from CustomClasses import TextHTML, ScrollableFrame
from CONFIG import template_dir
import os
# import klembord


class Window:
    def __init__(self, root):
        self.root = root
        self.root.title("FormMaker")
        self.template_names = sorted([name for name in os.listdir(template_dir) if name[-4:] == ".txt"])
        self.templates = []
        self.current_order = None
        
        for name in self.template_names:
            f = open(os.path.join(template_dir, name))
            self.templates.append(f.read())
            f.close()
        
        l0 = Label(self.root, text="Order Generator", font=('Arial', 18, 'bold'))
        f0 = Frame(self.root)
        s0 = Separator(self.root, orient=VERTICAL)
        self.f1 = ScrollableFrame(self.root, width=300, height=1500)
        f2 = Frame(self.root)

        Label(self.f1, text="Select a template above to enter fields here.").pack()

        self.radio_var = IntVar()
        self.radio_var.set(-1)
        for num, name in enumerate(self.template_names):
            Radiobutton(f0, text=name.replace(".txt","").title(), variable=self.radio_var, 
                        value=num, command=self.updateOrder).grid(row=0, column=num)

        self.textbox = TextHTML(f2, width=40, height=40, bg="#eee", bd=2, wrap=WORD)
        self.updateText()
        b0 = Button(f2, text="Copy Text", command=self.copyText)

        self.textbox.grid(row=0, column=0)
        b0.grid(row=1, column=0)

        l0.grid(row=0, column=0, columnspan=3)
        f0.grid(row=1, column=0, columnspan=3)
        self.f1.grid(row=2, column=0, padx=10)
        s0.grid(row=2, column=1, sticky="NS")
        f2.grid(row=2, column=2, padx=10)
    
    def updateOrder(self):
        self.f1.destroy()
        self.f1 = ScrollableFrame(self.root, width=300)
        self.current_order = Order(self.template_names[(current := self.radio_var.get())], 
                                   self.templates[current], self.f1, self.updateText)
        repeat_dict = self.current_order.getRepeatDict()
        for field in self.current_order.getFieldObjects():
            field.set()
            if (name := field.getName()) in repeat_dict:
                for repeat_obj in repeat_dict[name]:
                    if repeat_obj.getShift():
                        repeat_obj.set()
            Separator(self.f1, orient=HORIZONTAL).pack(fill="x")
        self.f1.grid(row=2, column=0, padx=10)
        self.updateText()
    
    def updateText(self):
        if self.radio_var.get() == -1:
            self.textbox.delete(1.0, END)
            self.textbox.insert(END, "Select a template above to see preview here.")
        else:
            self.textbox.setHTML(self.current_order.getHTML())
    
    def copyText(self, section):
        pass
        # klembord.set_with_rich_text(*self.current_order.getHTML(section, return_html=True))
        # TODO: verify it works w/o klembord.init()
