import tkinter
from tkinter import *
from PIL import ImageTk, Image
from tkinter import messagebox
import json
import os

root = Tk()
root.title('to do list???')
root.iconbitmap('icon.ico')
root.attributes('-fullscreen', True)
root.bind("<Escape>", lambda e: root.attributes("-fullscreen", False))
root.bind("<Tab>", lambda e: root.attributes("-fullscreen", True))
root.configure(bg="#c58d40")
listbox_task = tkinter.Listbox(root, bg="#c8954c" ,height=25, width=100)
listbox_task.pack()



root.mainloop()