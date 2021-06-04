from tkinter import Frame, Radiobutton, Label, IntVar, Button, PhotoImage
from tkinter.ttk import Separator
from tkinter import VERTICAL, END, WORD, HORIZONTAL
from Order import Order
from CustomClasses import HelpBox, TextHTML, ScrollableFrame
from CONFIG import template_dir, img_dir, manual, column_width, column_height
import os
import klembord


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
        
        title_frame = Frame(self.root)
        l0 = Label(title_frame, text="FormMaker", font=('Arial', 18, 'bold'))
        self.img = PhotoImage(file=img_dir)
        l1 = Label(title_frame, image=self.img)
        HelpBox(l1, title="FormMaker User Manual", message=manual)
        l0.grid(row=0, column=0)
        l1.grid(row=0, column=1)

        f0 = Frame(self.root)
        self.radio_var = IntVar()
        self.radio_var.set(-1)
        for num, name in enumerate(self.template_names):
            Radiobutton(f0, text=name.replace(".txt","").title(), variable=self.radio_var, 
                        value=num, command=self.updateOrder).grid(row=0, column=num)
        
        self.f1 = ScrollableFrame(self.root, width=column_width, height=column_height)
        Label(self.f1, text="Select a template above to enter fields here.").pack()

        s0 = Separator(self.root, orient=VERTICAL)

        self.f2 = Frame(self.root)
        self.textbox = TextHTML(self.f2, width=int(column_width/6), 
                                height=int(column_height/12), bg="#eee", bd=2, wrap=WORD)
        self.updateText()
        self.button_frame = Frame(self.f2)
        self.textbox.grid(row=0, column=0)
        self.button_frame.grid(row=1, column=0)

        title_frame.grid(row=0, column=0, columnspan=3)
        f0.grid(row=1, column=0, columnspan=3)
        self.f1.grid(row=2, column=0, padx=10)
        s0.grid(row=2, column=1, sticky="NS")
        self.f2.grid(row=2, column=2, padx=10)
    
    def updateOrder(self):
        # Fields
        self.f1.destroy()
        self.f1 = ScrollableFrame(self.root, width=column_width, height=column_height)
        self.current_order = Order(self.template_names[(current := self.radio_var.get())], 
                                   self.templates[current], self.f1, self.updateText)
        repeat_dict = self.current_order.getRepeatDict()
        Label(self.f1, text="").pack(pady=10)
        for field in self.current_order.getFieldObjects():
            field.set()
            if (name := field.getName()) in repeat_dict:
                for repeat_obj in repeat_dict[name]:
                    if repeat_obj.getShift():
                        repeat_obj.set()
            Separator(self.f1, orient=HORIZONTAL).pack(fill="x")
        Label(self.f1, text="").pack(pady=10)
        self.f1.grid(row=2, column=0, padx=10)
        self.updateText()
        # Copy Buttons
        self.button_frame.destroy()
        self.button_frame = Frame(self.f2)
        for num, title in enumerate(self.current_order.getCopyButtonInfo()):
                Button(self.button_frame, text="Copy "+title, 
                       command=lambda:self.copyText(num)).grid(row=num, column=0)
        self.textbox.config(height=int(column_height/12)-num*2)
        self.button_frame.grid(row=1, column=0)
    
    def updateText(self):
        if self.radio_var.get() == -1:
            self.textbox.delete(1.0, END)
            self.textbox.insert(END, "Select a template above to see preview here.")
        else:
            self.textbox.setHTML(self.current_order.getHTML())
    
    def copyText(self, section):
        klembord.set_with_rich_text(*self.current_order.getText(section, return_html=True))
        # TODO: verify it works w/o klembord.init()
