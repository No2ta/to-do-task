import tkinter
from tkinter import *
from PIL import ImageTk, Image
from tkinter import messagebox
import json
import os
import pickle

root = Tk()
root.title('to do list???')
root.iconbitmap('icon.ico')
root.attributes('-fullscreen', True)
root.bind("<Escape>", lambda e: root.attributes("-fullscreen", False))
root.bind("<Tab>", lambda e: root.attributes("-fullscreen", True))
root.configure(bg="#c58d40")

def addtask():
    task = entry_task.get()
    if task != "":
        listbox_task.insert(tkinter.END, task)
        entry_task.delete(0, tkinter.END)
    else:
        messagebox.showerror(title="fr?", message="you cant leave a task empty dude")

def deletetask():
    try:
        task_index = listbox_task.curselection()[0]
        listbox_task.delete(task_index)
    except:
        messagebox.showerror(title="bro", message="are you really that dumb deleting none?")
def finishtask():
    try:
        task_index = listbox_task.curselection()[0]
        listbox_task.delete(task_index)
    except:
        messagebox.showerror("man", "youre a reta*d tryna finish none fr?")
def savetask():
    tasks = listbox_task.get(0, listbox_task.size())
    pickle.dump(tasks, open("tasks.dat", "wb"))

def loadtask():
    try:
        tasks = pickle.load(open("tasks.dat", 'rb'))
        listbox_task.delete(0, tkinter.END)
        for task in tasks:
            listbox_task.insert(tkinter.END, task)
    except:
        messagebox.showerror("BRO???", "YOU REALLY TRYNA LOAD NOTHING????")

listbox_task = tkinter.Listbox(root, bg="#d0a465" ,height=25, width=100)
listbox_task.pack()

entry_task = tkinter.Entry(root, bg="#d0a465", width=90)
entry_task.pack()


buttonframe = Frame(root, bg="#c58d40")
buttonframe.place(relx=0.5, rely=0.75, anchor="center", relwidth=1)


buttonadd= tkinter.Button(buttonframe, text="Add task", width= 20,height=20, command=addtask)
buttonadd.place(relx=0.98, rely=0.5, anchor="e")

buttonfinish= tkinter.Button(buttonframe, text="Finish task", width= 20,height=20, command=finishtask)
buttonfinish.place(relx=0.5, rely=0.5, anchor="center")

buttondelete= tkinter.Button(buttonframe, text="Delete task", width= 20,height=20, command=deletetask)
buttondelete.place(relx=0.85, rely=10, anchor="e")

buttonsave= tkinter.Button(buttonframe, text="Save task", width= 20,height=20, command=savetask)
buttonsave.place(relx=0.02, rely=0.5, anchor="w")

buttonload= tkinter.Button(buttonframe, text="Load tasks", width= 20,height=20, command=loadtask)
buttonload.place(relx=0.15, rely=0.5, anchor="w")


root.mainloop()