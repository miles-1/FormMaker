from tkinter import Frame, Radiobutton, Text, Label, IntVar, Button
from tkinter.ttk import Separator
from tkinter import VERTICAL, END, WORD, HORIZONTAL
from Order import Order
from CONFIG import template_dir, BOLD_SPLIT
import os


class Window:
    def __init__(self, root):
        self.root = root
        self.root.title("Order Generator")
        self.template_names = [name for name in os.listdir(template_dir) if name[-4:] == ".txt"]
        self.templates = []
        self.field_obj = []
        self.current_order = None
        
        for name in self.template_names:
            f = open(os.path.join(template_dir, name))
            self.templates.append(f.read())
            f.close()
        
        l0 = Label(self.root, text="Order Generator", font=('Arial', 18, 'bold'))
        s0 = Separator(self.root, orient=VERTICAL)
        f0 = Frame(self.root)
        self.f1 = Frame(self.root, width=300)
        f2 = Frame(self.root)

        Label(self.f1, text="Select a template above to enter fields here.").pack()

        self.radio_var = IntVar()
        self.radio_var.set(-1)
        for num, name in enumerate(self.template_names):
            Radiobutton(f0, text=name.replace(".txt","").title(), variable=self.radio_var, 
                        value=num, command=self.updateOrder).grid(row=0, column=num)

        self.textbox = Text(f2, width=40, height=40, bg="#eee", bd=2, wrap=WORD)
        self.textbox.tag_configure("bold", font=('Arial', 14, 'bold'))
        self.textbox.tag_configure("norm", font=('Courier', 12))
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
        self.f1 = Frame(self.root, width=300)
        self.current_order = Order(self.template_names[(current := self.radio_var.get())], 
                                   self.templates[current], self.f1, self.updateText)
        self.field_obj = self.current_order.getFieldObjects()
        for field in self.field_obj:
            field.set()
            Separator(self.f1, orient=HORIZONTAL).pack(fill="x")
        self.f1.grid(row=2, column=0, padx=10)
        self.updateText()
    
    def updateText(self):
        self.textbox.delete(1.0, END)
        if self.radio_var.get() == -1:
            self.insertText("Select a template above to see preview here.")
        else:
            self.insertText(self.current_order.getText())
    
    def insertText(self, text):
        split_text = text.split(BOLD_SPLIT)
        for i, text_frag in enumerate(split_text):
            if not i % 2:
                self.textbox.insert(END, text_frag, "norm")
            else:
                self.textbox.insert(END, text_frag, "bold")
    
    def copyText(self):
        pass
