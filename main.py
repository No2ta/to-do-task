import tkinter as tk
from tkinter import messagebox, ttk
import pickle
import random
import time
from typing import Dict, Any

root = tk.Tk()
root.title('your average to do list')
try:
    root.iconbitmap('icon.ico')
except Exception:
    pass
root.attributes('-fullscreen', True)
root.bind("<Escape>", lambda e: root.attributes("-fullscreen", False))
root.bind("<Tab>", lambda e: root.attributes("-fullscreen", True))

BG_TODO = "#c58d40"
BG_CLICKER = "#c58d40"
FG_LIGHT = "#ffffff"
ACCENT = "#765424"

root.configure(bg=BG_TODO)

SAVE_FILE = "game_state.dat"

ACTIONS = ["add", "delete", "finish", "save", "load"]

state: Dict[str, Any] = {
    "tasks": [],
    "task_points": 0,

    "clicks": 0,
    "cpc": 1,
    "mult": 1,
    "autoclickers": 0,


    "unlocked": {a: False for a in ACTIONS},
    "costs": {},
    "cycle_baseline": 0,
    "relock_threshold": 0,
}

def init_first_cycle_costs():
    state["costs"] = {a: random.randint(100, 200) for a in ACTIONS}
    state["cycle_baseline"] = 0
    state["relock_threshold"] = 0

def save_all():
    if 'listbox_task' in globals() and listbox_task is not None:
        state["tasks"] = list(listbox_task.get(0, tk.END))
    try:
        with open(SAVE_FILE, "wb") as f:
            pickle.dump(state, f)
    except Exception as ex:
        messagebox.showerror("Save Error", f"Could not save:\n{ex}")

def load_all():
    try:
        with open(SAVE_FILE, "rb") as f:
            s = pickle.load(f)
        for k in list(state.keys()):
            if k in s:
                state[k] = s[k]
        if not isinstance(state.get("unlocked"), dict):
            state["unlocked"] = {a: False for a in ACTIONS}
        for a in ACTIONS:
            state["unlocked"].setdefault(a, False)
        if not state.get("costs"):
            init_first_cycle_costs()
    except Exception:
        init_first_cycle_costs()

def effective_mult() -> float:
    return max(1, state["mult"])

def clicks_per_tick() -> int:
    base = state["autoclickers"]
    return int(max(0, base) * effective_mult())

def clicks_per_press() -> int:
    return int(max(1, state["cpc"]) * effective_mult())

def format_big(n: float) -> str:
    try:
        n = float(n)
    except Exception:
        return str(n)
    if n >= 1_000_000_000:
        return f"{n/1_000_000_000:.2f}B"
    if n >= 1_000_000:
        return f"{n/1_000_000:.2f}M"
    if n >= 1_000:
        return f"{n/1_000:.2f}K"
    return str(int(n))

def all_actions_unlocked() -> bool:
    return all(state["unlocked"].get(a, False) for a in ACTIONS)

def maybe_relock_cycle():
    if state.get("relock_threshold") and state["clicks"] >= state["relock_threshold"]:
        for a in ACTIONS:
            state["unlocked"][a] = False
        new_costs = {}
        for a in ACTIONS:
            prev = state["costs"].get(a, 100)
            new_costs[a] = max(100, int(prev * 5 * random.uniform(0.9, 1.15)))
        state["costs"] = new_costs
        state["relock_threshold"] = 0
        refresh_all()

def check_after_full_unlock_set_threshold():
    if all_actions_unlocked() and state.get("relock_threshold", 0) == 0:
        state["cycle_baseline"] = max(state.get("clicks", 0), 1)
        state["relock_threshold"] = state["cycle_baseline"] * 6
        refresh_all()
    

def load_tasks_into_listbox():
    if 'listbox_task' in globals() and listbox_task is not None:
        listbox_task.delete(0, tk.END)
        for t in state.get("tasks", []):
            listbox_task.insert(tk.END, t)

def require_unlocked(action: str) -> bool:
    if not state["unlocked"].get(action, False):
        messagebox.showerror("Locked", "Feature is locked. Earn clicks to unlock.")
        return False
    return True

def add_task():
    if not require_unlocked("add"):
        return
    text = entry_task.get().strip()
    if not text:
        messagebox.showerror("Empty", "Task cannot be empty.")
        return
    listbox_task.insert(tk.END, text)
    entry_task.delete(0, tk.END)
    state["tasks"] = list(listbox_task.get(0, tk.END))
    save_all()
    refresh_all()

def delete_task():
    if not require_unlocked("delete"):
        return
    try:
        idx = listbox_task.curselection()[0]
        listbox_task.delete(idx)
        state["tasks"] = list(listbox_task.get(0, tk.END))
        save_all()
        refresh_all()
    except Exception:
        messagebox.showerror("Select one", "No task selected.")

def finish_task():
    if not require_unlocked("finish"):
        return
    try:
        idx = listbox_task.curselection()[0]
        listbox_task.delete(idx)
        reward = 2
        state["task_points"] = state.get("task_points", 0) + reward
        state["tasks"] = list(listbox_task.get(0, tk.END))
        save_all()
        refresh_all()
    except Exception:
        messagebox.showerror("Select one", "No task selected.")

def save_tasks_only():
    if not require_unlocked("save"):
        return
    state["tasks"] = list(listbox_task.get(0, tk.END))
    save_all()
    messagebox.showinfo("Saved", "Tasks saved.")

def load_tasks_only():
    if not require_unlocked("load"):
        return
    load_all()
    load_tasks_into_listbox()
    refresh_all()
    messagebox.showinfo("Loaded", "Tasks loaded.")

def do_click():
    state["clicks"] = state.get("clicks", 0) + clicks_per_press()
    after_click_common()

def after_click_common():
    refresh_clicker_stats()
    maybe_relock_cycle()
    save_all()

def try_buy_action(action: str):
    cost = state["costs"].get(action, 999999999)
    if state["unlocked"].get(action, False):
        messagebox.showinfo("Unlocked", f"{action.title()} already unlocked.")
        return
    if state["clicks"] < cost:
        messagebox.showerror("Need more clicks", f"Cost: {format_big(cost)} clicks.")
        return
    state["clicks"] -= cost
    state["unlocked"][action] = True
    refresh_all()
    save_all()
    check_after_full_unlock_set_threshold()


menu_frame = tk.Frame(root, bg=BG_TODO)
lbl_title = tk.Label(menu_frame, text="TO-DO LIST", font=("Arial", 40, "bold"), bg=BG_TODO, fg=FG_LIGHT)
lbl_title.pack(pady=50)
btn_start = tk.Button(menu_frame, text="Start", font=("Arial", 20, "bold"), bg=ACCENT, fg="white",
                      width=20, height=2, command=lambda: switch_frame(todo_frame))
btn_start.pack(pady=10)
btn_exit = tk.Button(menu_frame, text="Exit", font=("Arial", 20, "bold"), bg=ACCENT, fg="white",
                     width=20, height=2, command=root.destroy)
btn_exit.pack(pady=10)

todo_frame = tk.Frame(root, bg=BG_TODO)
btn_back_menu = tk.Button(todo_frame, text="Back", font=("Arial", 12, "bold"), bg=ACCENT, fg="white",
                          command=lambda: switch_frame(menu_frame))
btn_back_menu.place(relx=0.02, rely=0.02, anchor="nw")
btn_clicker = tk.Button(todo_frame, text="Click", font=("Arial", 14, "bold"), bg="#2ecc71", fg="white",
                        command=lambda: switch_frame(clicker_frame))
btn_clicker.place(relx=0.98, rely=0.02, anchor="ne")
points_label = tk.Label(todo_frame, text="Task Points: 0", font=("Arial", 16, "bold"), bg=BG_TODO, fg="white")
points_label.place(relx=0.80, rely=0.02, anchor="ne")
listbox_task = tk.Listbox(todo_frame, bg="#d0a465", height=14, width=80)
listbox_task.pack(pady=(60, 5))
entry_task = tk.Entry(todo_frame, bg="#d0a465", width=70)
entry_task.pack()
btns = tk.Frame(todo_frame, bg=BG_TODO)
btns.pack(pady=10)
btn_add = tk.Button(btns, text="Add task", width=14, height=2, command=add_task,
                    font=("Arial", 12, "bold"), bg=ACCENT, fg="white")
btn_add.grid(row=0, column=0, padx=6, pady=6)
btn_del = tk.Button(btns, text="Delete task", width=14, height=2, command=delete_task,
                    font=("Arial", 12, "bold"), bg=ACCENT, fg="white")
btn_del.grid(row=1, column=0, padx=6, pady=6)
btn_finish = tk.Button(btns, text="Finish task", width=14, height=2, command=finish_task,
                       font=("Arial", 12, "bold"), bg=ACCENT, fg="white")
btn_finish.grid(row=0, column=1, padx=6, pady=6)
btn_save = tk.Button(btns, text="Save tasks", width=14, height=2, command=save_tasks_only,
                     font=("Arial", 12, "bold"), bg=ACCENT, fg="white")
btn_save.grid(row=0, column=2, padx=6, pady=6)
btn_load = tk.Button(btns, text="Load tasks", width=14, height=2, command=load_tasks_only,
                     font=("Arial", 12, "bold"), bg=ACCENT, fg="white")
btn_load.grid(row=1, column=2, padx=6, pady=6)

clicker_frame = tk.Frame(root, bg=BG_CLICKER)
def switch_frame(frame: tk.Frame):
    for f in (menu_frame, todo_frame, clicker_frame):
        f.pack_forget()
    frame.pack(fill="both", expand=True)

main_grid_frame = tk.Frame(clicker_frame, bg=BG_CLICKER)
main_grid_frame.pack(fill="both", expand=True, padx=20, pady=20)
main_grid_frame.columnconfigure(0, weight=1)
main_grid_frame.columnconfigure(1, weight=1)
main_grid_frame.columnconfigure(2, weight=1)

stats = tk.LabelFrame(main_grid_frame, text="Your Stats", font=("Arial", 14, "bold"),
                       bg=BG_CLICKER, fg=FG_LIGHT, bd=2)
stats.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="ew")
stats.columnconfigure(0, weight=1)
stats.columnconfigure(1, weight=1)
stats.columnconfigure(2, weight=1)
lbl_clicks = tk.Label(stats, text="Clicks: 0", font=("Consolas", 18, "bold"), bg=BG_CLICKER, fg=FG_LIGHT)
lbl_clicks.grid(row=0, column=0, padx=8, pady=5)
lbl_cpc = tk.Label(stats, text="CPC: 1", font=("Consolas", 14, "bold"), bg=BG_CLICKER, fg=FG_LIGHT)
lbl_cpc.grid(row=0, column=1, padx=8, pady=5)

def refresh_clicker_stats():
    lbl_clicks.config(text=f"Clicks: {format_big(state.get('clicks', 0))}")
    lbl_cpc.config(text=f"CPC: {state.get('cpc', 1)}")

def refresh_todo_buttons_state():
    points_label.config(text=f"Task Points: {state['task_points']}")
    btn_add.config(state='normal' if state["unlocked"].get('add', False) else 'disabled')
    btn_del.config(state='normal' if state["unlocked"].get('delete', False) else 'disabled')
    btn_finish.config(state='normal' if state["unlocked"].get('finish', False) else 'disabled')
    btn_save.config(state='normal' if state["unlocked"].get('save', False) else 'disabled')
    btn_load.config(state='normal' if state["unlocked"].get('load', False) else 'disabled')

def refresh_all():
    refresh_clicker_stats()
    refresh_todo_buttons_state()

def game_loop():
    refresh_all()
    root.after(1000, game_loop) 

def on_close():
    save_all()
    root.destroy()

if __name__ == "__main__":
    load_all()
    load_tasks_into_listbox()
    refresh_all()

    root.protocol("WM_DELETE_WINDOW", on_close)

    switch_frame(menu_frame)
    game_loop()
    root.mainloop()