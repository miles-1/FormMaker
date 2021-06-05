from Window import Window
from tkinter import Tk, messagebox
from CustomClasses import TkExceptionHandler
import tkinter, os

if __name__ == "__main__":
    tkinter.CallWrapper = TkExceptionHandler
    try:
        root = Tk()
        Window(root)
        root.mainloop()
    except SyntaxError as e:
        messagebox.showerror(message="Error in templates: " + e)
    except Exception as e:
        import traceback
        import sys
        messagebox.showerror(message=type(e).__name__ + ": " + str(e) + "\n"*3 + traceback.format_exc())
        sys.exit()
