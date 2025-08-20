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



root.mainloop()