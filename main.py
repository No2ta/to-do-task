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

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
bg_image = Image.open("bg.jpg")
bg_image = bg_image.resize((screen_width, screen_height), Image.Resampling.LANCZOS)
bg_photo = ImageTk.PhotoImage(bg_image)

canvas = Canvas(root, width=screen_width, height=screen_height)
canvas.pack(fill="both", expand=True)
canvas.create_image(0, 0, image=bg_photo, anchor="nw")

# Game data
game_data = {
    'tasks': []
}

def start_todo_window():
    root.destroy()

    todo_window = Tk()
    todo_window.title('TO DO LIST')
    todo_window.iconbitmap('icon.ico')
    todo_window.attributes('-fullscreen', True)
    todo_window.bind("<Escape>", lambda e: todo_window.attributes("-fullscreen", False))
    todo_window.configure(bg='black')

    Label(todo_window, text="TO DO LIST", font=("Arial", 32, "bold"),
          fg="white", bg="black").pack(pady=30)

    # Scrollable task list
    task_list_frame = Frame(todo_window, bg='black')
    task_list_frame.pack(fill='both', expand=True, pady=20, padx=50)

    task_canvas = Canvas(task_list_frame, bg='gray20', highlightthickness=0)
    task_scrollbar = Scrollbar(task_list_frame, orient="vertical", command=task_canvas.yview)
    scrollable_task_frame = Frame(task_canvas, bg='gray20')

    scrollable_task_frame.bind(
        "<Configure>",
        lambda e: task_canvas.configure(scrollregion=task_canvas.bbox("all"))
    )

    task_canvas.create_window((0, 0), window=scrollable_task_frame, anchor="nw")
    task_canvas.configure(yscrollcommand=task_scrollbar.set)

    task_canvas.pack(side="left", fill="both", expand=True)
    task_scrollbar.pack(side="right", fill="y")

    def refresh_tasks():
        for widget in scrollable_task_frame.winfo_children():
            widget.destroy()

        for task in game_data['tasks']:
            task_frame = Frame(scrollable_task_frame, bg='gray30', relief='raised', bd=3)
            task_frame.pack(fill='x', pady=8, padx=10)

            Label(task_frame, text=f"○ {task}", font=("Arial", 18, "bold"),
                  fg="white", bg='gray30', anchor='w', wraplength=600).pack(side='top', fill='x',
                  expand=True, padx=20, pady=20)

    # Control buttons
    button_frame = Frame(todo_window, bg='black')
    button_frame.pack(pady=30)

    create_btn = Button(button_frame, text="Create Task", bg='blue', fg='white',
                        font=("Arial", 16, "bold"), padx=30, pady=15)
    create_btn.pack(side='left', padx=20)

    def trigger_horror():
        messagebox.showinfo(" ", "LOL????? YOU actually thought... this is it. A F*CKING to do list??????")
        messagebox.showerror("", "how pathetic")
        create_btn.pack_forget()

        game_data['tasks'] = [
            "wake up",
            "wake up",
            "wake up",
            "wake up",
            "wake the f*ck up"
        ]
        refresh_tasks()

    create_btn.config(command=trigger_horror)

    Button(button_frame, text="Exit Game", command=todo_window.quit,
           bg='darkred', fg='white', font=("Arial", 16, "bold"), padx=30, pady=15).pack(side='left', padx=20)

    refresh_tasks()
    todo_window.mainloop()

def popup():
    if os.path.exists('data.json'):
        with open('data.json', 'r') as file:
            try:
                data = json.load(file)
                if data.get('intro_completed', False):
                    start_todo_window()
                    return
            except:
                pass

    response = messagebox.askyesno(" ", "you will suffer do you want to continue?")
    if response == 1:
        response2 = messagebox.askyesno(" ", "you really wanna continue?")
        if response2 == 1:
            response3 = messagebox.askyesno(" ", "bro stop it there is no going back")
            if response3 == 1:
                data = {'intro_completed': True}
                with open('data.json', 'w') as file:
                    json.dump(data, file)

                messagebox.showerror(" ", "fine what a di**head i warned you enough, jus click the start again")
                start_todo_window()

start_btn = Button(root, text="start", command=popup, font=("Arial", 20),
                   bg="white", fg="black", padx=20, pady=10)
canvas.create_window(screen_width//2, screen_height//2, anchor="center", window=start_btn)

root.mainloop()