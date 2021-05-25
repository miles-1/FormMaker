from Window import Window
from tkinter import Tk, messagebox

if __name__ == "__main__":
    try:
        root = Tk()
        Window(root)
        root.mainloop()
    except SyntaxError as e:
        messagebox.showerror("Error in templates: " + e)
    except Exception as e:
        messagebox.showerror(e)
