from tkinter import *
from PIL import ImageTk,Image
from tkinter import messagebox


root = Tk()
root.title('to do list???')
root.iconbitmap('icon.ico')

##loop for the 1st warnings
def popup():
    response = messagebox.askyesno( " ", "you will suffer do you want to continue?")
    if response == 1:
        response2 = messagebox.askyesno(" " , "you really wanna continue?")
        if response2 == 1:
            response3 = messagebox.askyesno( " ",  "bro stop it there is no going back")
            if response3 == 1:
                response4 = messagebox.showerror(  " " ,"fine what a di**head i warned you enough, jus click the start again")     
            else:
                None    
    else:
        None
    





Button(root, text="start", command=popup).pack()

root.mainloop()