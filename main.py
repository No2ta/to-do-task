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


task_points = 0

def update_points_display():
    points_label.config(text=f"Task Points: {task_points}")

def auto_save():
    tasks = listbox_task.get(0, listbox_task.size())
    data = {'tasks': tasks, 'points': task_points}
    pickle.dump(data, open("tasks.dat", "wb"))

def auto_load():
    global task_points
    try:
        data = pickle.load(open("tasks.dat", 'rb'))
        if isinstance(data, dict):
            tasks = data.get('tasks', [])
            task_points = data.get('points', 0)
        else:
            tasks = data
            task_points = 0
        
        listbox_task.delete(0, tkinter.END)
        for task in tasks:
            listbox_task.insert(tkinter.END, task)
        update_points_display()
    except:
        pass





def addtask():
    task = entry_task.get()
    if task != "":
        listbox_task.insert(tkinter.END, task)
        entry_task.delete(0, tkinter.END)
        auto_save()
    else:
        messagebox.showerror(title="fr?", message="you cant leave a task empty dude")

def deletetask():
    try:
        task_index = listbox_task.curselection()[0]
        listbox_task.delete(task_index)
        auto_save()
    except:
        messagebox.showerror(title="bro", message="are you really that dumb deleting none?")

def finishtask():
    global task_points
    try:
        task_index = listbox_task.curselection()[0]
        listbox_task.delete(task_index)
        task_points += 2
        update_points_display()
        auto_save()
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

listbox_task = tkinter.Listbox(root, bg="#d0a465", height=25, width=100)
listbox_task.pack()

entry_task = tkinter.Entry(root, bg="#d0a465", width=90)
entry_task.pack()

buttonframe = Frame(root, bg="#c58d40")
buttonframe.place(relx=0.5, rely=0.75, anchor="center", relwidth=1, relheight=0.35)

buttonadd = tkinter.Button(buttonframe, text="Add task", width=20, height=5, command=addtask, 
                          relief="raised", bd=3, font=("Arial", 12, "bold"), 
                          bg="#765424", cursor="hand2")
buttonadd.place(relx=0.05, rely=0.25, anchor="center")

buttondelete = tkinter.Button(buttonframe, text="Delete task", width=20, height=5, command=deletetask, 
                             relief="raised", bd=3, font=("Arial", 12, "bold"), 
                             bg="#765424", cursor="hand2")
buttondelete.place(relx=0.05, rely=0.85, anchor="center")


buttonfinish = tkinter.Button(buttonframe, text="Finish task", width=20, height=5, command=finishtask, 
                             relief="raised", bd=3, font=("Arial", 12, "bold"), 
                             bg="#765424", cursor="hand2")
buttonfinish.place(relx=0.5, rely=0.5, anchor="center")

buttonsave = tkinter.Button(buttonframe, text="Save tasks", width=20, height=5, command=savetask, 
                           relief="raised", bd=3, font=("Arial", 12, "bold"), 
                           bg="#765424", cursor="hand2")
buttonsave.place(relx=0.95, rely=0.25, anchor="center")

buttonload = tkinter.Button(buttonframe, text="Load tasks", width=20, height=5, command=loadtask, 
                           relief="raised", bd=3, font=("Arial", 12, "bold"), 
                           bg="#765424", cursor="hand2")
buttonload.place(relx=0.95, rely=0.85, anchor="center")


points_label = tkinter.Label(root, text=f"Task Points: {task_points}", 
                            font=("Arial", 16, "bold"), bg="#c58d40", fg="white")
points_label.place(relx=0.98, rely=0.02, anchor="ne")

auto_load()
root.mainloop()