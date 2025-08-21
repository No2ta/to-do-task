import tkinter as tk
from tkinter import messagebox, ttk
import pickle
import random
import time
from typing import Dict, Any

root = tk.Tk()
root.title('To-Do + Clicker: Crazy Edition')
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
    "clicks_per_press": 1,
    "mult": 1,
    "autoclickers": 0,
    "rebirths": 0,
    "rebirth_points": 0,
    "transcendence": 0,
    "cosmic_mult": 1,

    "unlocked": {a: False for a in ACTIONS},
    "costs": {},
    "cycle_baseline": 0,
    "relock_threshold": 0,

    "price_clicks_per_press": 10,
    "price_mult": 100,
    "price_auto": 50,
    "price_task_to_clicks": 20,

    "interns": 0,
    "intern_price": 500,
    "factories": 0,
    "factory_price": 2000,
    
    "story_stage": 0,
    "cosmic_tier": 0,
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
    rebirth_mult = state.get("rebirth_points", 0) * 0.1 + 1
    cosmic_mult = state.get("cosmic_mult", 1)
    return max(1, state["mult"] * rebirth_mult * cosmic_mult)

def clicks_per_tick() -> int:
    base = state["autoclickers"] + state["interns"] * 2 + state["factories"] * 10
    return int(max(0, base) * effective_mult())

def clicks_per_press() -> int:
    return int(max(1, state["clicks_per_press"]) * effective_mult())

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
    
def check_story_progress():
    pass

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

def interns_tick():
    if state.get("interns", 0) and state.get("tasks"):
        finished = min(len(state["tasks"]), state["interns"])
        for _ in range(finished):
            state["tasks"].pop(0)
            state["task_points"] = state.get("task_points", 0) + 1
        load_tasks_into_listbox()
        refresh_all()
    cost = state.get("interns", 0) * 1
    state["clicks"] = max(0, state.get("clicks", 0) - cost)

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

def buy_clicks():
    price = state.get("price_clicks_per_press", 10)
    if state["clicks"] < price:
        messagebox.showerror("Need more clicks", f"Cost: {format_big(price)}")
        return
    state["clicks"] -= price
    state["clicks_per_press"] = state.get("clicks_per_press", 1) + 1
    state["price_clicks_per_press"] = int((state["clicks_per_press"] + 1) ** 2 * 10)
    refresh_all()
    save_all()

def buy_multiplier():
    price = state.get("price_mult", 100)
    if state["clicks"] < price:
        messagebox.showerror("Need more clicks", f"Cost: {format_big(price)}")
        return
    state["clicks"] -= price
    state["mult"] = state.get("mult", 1) * 2
    state["price_mult"] = int(state["price_mult"] * 2.5)
    refresh_all()
    save_all()

def buy_autoclicker():
    price = state.get("price_auto", 50)
    if state["clicks"] < price:
        messagebox.showerror("Need more clicks", f"Cost: {format_big(price)}")
        return
    state["clicks"] -= price
    state["autoclickers"] = state.get("autoclickers", 0) + 1
    state["price_auto"] = int(state["price_auto"] * 1.85 + 5)
    refresh_all()
    save_all()

def buy_task_to_clicks():
    price = state.get("price_task_to_clicks", 20)
    if state.get("task_points", 0) < price:
        messagebox.showerror("Need task points", f"Cost: {price} TP")
        return
    state["task_points"] -= price
    state["clicks_per_press"] = state.get("clicks_per_press", 1) + 2
    state["price_task_to_clicks"] = int(state["price_task_to_clicks"] * 1.75 + 5)
    refresh_all()
    save_all()

def buy_intern():
    if state["clicks"] < state.get("intern_price", 500):
        messagebox.showerror("Need more clicks", f"Cost: {format_big(state.get('intern_price', 500))}")
        return
    state["clicks"] -= state.get("intern_price", 500)
    state["interns"] = state.get("interns", 0) + 1
    state["intern_price"] = int(state.get("intern_price", 500) * 1.6)
    refresh_all()
    save_all()

def buy_factory():
    if state["clicks"] < state.get("factory_price", 2000):
        messagebox.showerror("Need more clicks", f"Cost: {format_big(state.get('factory_price', 2000))}")
        return
    state["clicks"] -= state.get("factory_price", 2000)
    state["factories"] = state.get("factories", 0) + 1
    state["factory_price"] = int(state.get("factory_price", 2000) * 2.0)
    refresh_all()
    save_all()

def do_rebirth():
    if state["clicks"] < 500_000:
        messagebox.showerror("Rebirth requires 500K clicks.", "You need at least 500,000 clicks to rebirth.")
        return
    points_gained = int(state["clicks"] / 500_000)
    state["rebirth_points"] += points_gained
    state["rebirths"] += 1

    state["clicks"] = 0
    state["clicks_per_press"] = 1
    state["mult"] = 1
    state["autoclickers"] = 0
    state["interns"] = 0
    state["factories"] = 0
    state["task_points"] = 0
    
    state["price_clicks_per_press"] = 10
    state["price_mult"] = 100
    state["price_auto"] = 50
    state["price_task_to_clicks"] = 20
    state["intern_price"] = 500
    state["factory_price"] = 2000
    
    state["unlocked"] = {a: False for a in ACTIONS}
    init_first_cycle_costs()
    messagebox.showinfo("Rebirth!", f"Rebirthed! Gained {points_gained} rebirth points.")
    refresh_all()
    save_all()

def do_transcendence():
    if state["rebirth_points"] < 20:
        messagebox.showerror("Transcendence requires 20 rebirth points.", "You need at least 20 rebirth points to transcend.")
        return
    
    points_spent = 20
    state["rebirth_points"] -= points_spent
    state["transcendence"] += 1
    state["cosmic_mult"] += 0.5
    
    state["clicks"] = 0
    state["clicks_per_press"] = 1
    state["mult"] = 1
    state["autoclickers"] = 0
    state["rebirths"] = 0
    state["interns"] = 0
    state["factories"] = 0
    state["task_points"] = 0
    
    state["price_clicks_per_press"] = 10
    state["price_mult"] = 100
    state["price_auto"] = 50
    state["price_task_to_clicks"] = 20
    state["intern_price"] = 500
    state["factory_price"] = 2000
    
    state["unlocked"] = {a: False for a in ACTIONS}
    init_first_cycle_costs()
    
    messagebox.showinfo("Transcendence!", f"Transcendence completed! Your cosmic multiplier is now ×{state['cosmic_mult']:.1f}.")
    refresh_all()
    save_all()

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

top_bar = tk.Frame(main_grid_frame, bg=BG_CLICKER)
top_bar.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 10))
btn_back_todo = tk.Button(top_bar, text="Back to To-Do", font=("Arial", 12, "bold"), bg=ACCENT, fg="white",
                          command=lambda: switch_frame(todo_frame))
btn_back_todo.pack(side="left")

stats = tk.LabelFrame(main_grid_frame, text="Your Stats", font=("Arial", 14, "bold"),
                       bg=BG_CLICKER, fg=FG_LIGHT, bd=2)
stats.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="ew")
stats.columnconfigure(0, weight=1)
stats.columnconfigure(1, weight=1)
stats.columnconfigure(2, weight=1)
lbl_clicks = tk.Label(stats, text="Clicks: 0", font=("Consolas", 18, "bold"), bg=BG_CLICKER, fg=FG_LIGHT)
lbl_clicks.grid(row=0, column=0, padx=8, pady=5)
lbl_clicks_per_press = tk.Label(stats, text="Clicks/Press: 1", font=("Consolas", 14, "bold"), bg=BG_CLICKER, fg=FG_LIGHT)
lbl_clicks_per_press.grid(row=0, column=1, padx=8, pady=5)
lbl_mult = tk.Label(stats, text="Mult: ×1", font=("Consolas", 14, "bold"), bg=BG_CLICKER, fg=FG_LIGHT)
lbl_mult.grid(row=0, column=2, padx=8, pady=5)
lbl_auto = tk.Label(stats, text="Autoclickers: 0", font=("Consolas", 14, "bold"), bg=BG_CLICKER, fg=FG_LIGHT)
lbl_auto.grid(row=1, column=0, padx=8, pady=5)
lbl_tp = tk.Label(stats, text="Task Points: 0", font=("Consolas", 14, "bold"), bg=BG_CLICKER, fg=FG_LIGHT)
lbl_tp.grid(row=1, column=1, padx=8, pady=5)

btn_big_click = tk.Button(main_grid_frame, text="CLICK", font=("Arial", 24, "bold"), width=14, height=3, bg="#e74c3c", fg="white",
                          command=do_click)
btn_big_click.grid(row=2, column=0, columnspan=3, pady=12)

shop = tk.LabelFrame(main_grid_frame, text="Upgrades & Automation", font=("Arial", 12, "bold"),
                     bg=BG_CLICKER, fg=FG_LIGHT, bd=2, labelanchor="n")
shop.grid(row=3, column=0, padx=10, pady=10, sticky="n")

lbl_clicks_per_press_price = tk.Label(shop, text="", font=("Arial", 11), bg=BG_CLICKER, fg=FG_LIGHT)
lbl_clicks_per_press_price.pack(pady=(8, 2))
btn_upgrade_clicks = tk.Button(shop, text="+1 Clicks/Press", font=("Arial", 12, "bold"), bg="#f39c12", fg="white",
                                command=buy_clicks, width=18)
btn_upgrade_clicks.pack(pady=(0, 6))

lbl_mult_price = tk.Label(shop, text="", font=("Arial", 11), bg=BG_CLICKER, fg=FG_LIGHT)
lbl_mult_price.pack(pady=(8, 2))
btn_upgrade_mult = tk.Button(shop, text="×2 Mult", font=("Arial", 12, "bold"), bg="#9b59b6", fg="white",
                             command=buy_multiplier, width=18)
btn_upgrade_mult.pack(pady=(0, 6))

lbl_auto_price = tk.Label(shop, text="", font=("Arial", 11), bg=BG_CLICKER, fg=FG_LIGHT)
lbl_auto_price.pack(pady=(8, 2))
btn_buy_auto = tk.Button(shop, text="+1 Autoclicker", font=("Arial", 12, "bold"), bg="#16a085", fg="white",
                         command=buy_autoclicker, width=18)
btn_buy_auto.pack(pady=(0, 6))

lbl_task_to_clicks_price = tk.Label(shop, text="", font=("Arial", 11), bg=BG_CLICKER, fg=FG_LIGHT)
lbl_task_to_clicks_price.pack(pady=(8, 2))
btn_task_to_clicks = tk.Button(shop, text="+2 Clicks (Task Pts)", font=("Arial", 12, "bold"), bg="#c0392b", fg="white",
                                command=buy_task_to_clicks, width=18)
btn_task_to_clicks.pack(pady=(0, 6))

lbl_intern = tk.Label(shop, text="", font=("Arial", 11), bg=BG_CLICKER, fg=FG_LIGHT)
lbl_intern.pack(pady=(6, 2))
btn_buy_intern = tk.Button(shop, text="Hire Intern", font=("Arial", 12, "bold"), bg="#2ecc71", fg="white",
                           command=buy_intern, width=18)
btn_buy_intern.pack(pady=(0, 6))

lbl_factory = tk.Label(shop, text="", font=("Arial", 11), bg=BG_CLICKER, fg=FG_LIGHT)
lbl_factory.pack(pady=(6, 2))
btn_buy_factory = tk.Button(shop, text="Build Factory", font=("Arial", 12, "bold"), bg="#34495e", fg="white",
                            command=buy_factory, width=18)
btn_buy_factory.pack(pady=(0, 6))

unlock = tk.LabelFrame(main_grid_frame, text="Unlock To-Do Actions", font=("Arial", 12, "bold"),
                       bg=BG_CLICKER, fg=FG_LIGHT, bd=2, labelanchor="n")
unlock.grid(row=3, column=1, padx=10, pady=10, sticky="n")

unlock_labels: Dict[str, tk.Label] = {}
unlock_buttons: Dict[str, tk.Button] = {}
for a in ACTIONS:
    frame = tk.Frame(unlock, bg=BG_CLICKER)
    frame.pack(pady=4, fill="x")
    lbl = tk.Label(frame, text=f"{a.title()}: cost ...", font=("Arial", 11), bg=BG_CLICKER, fg=FG_LIGHT)
    lbl.pack(side="left", padx=6)
    btn = tk.Button(frame, text=f"Unlock {a.title()}", font=("Arial", 10, "bold"), bg="#2ecc71", fg="white",
                    command=lambda x=a: try_buy_action(x))
    btn.pack(side="right", padx=6)
    unlock_labels[a] = lbl
    unlock_buttons[a] = btn

prestige_frame = tk.LabelFrame(main_grid_frame, text="Prestige", font=("Arial", 12, "bold"),
                       bg=BG_CLICKER, fg=FG_LIGHT, bd=2, labelanchor="n")
prestige_frame.grid(row=3, column=2, padx=10, pady=10, sticky="n")

lbl_rebirth_points = tk.Label(prestige_frame, text="Rebirth Points: 0", font=("Arial", 12), bg=BG_CLICKER, fg=FG_LIGHT)
lbl_rebirth_points.pack(pady=(8, 2))
lbl_rebirths = tk.Label(prestige_frame, text="Rebirths: 0", font=("Arial", 10), bg=BG_CLICKER, fg=FG_LIGHT)
lbl_rebirths.pack(pady=(0, 6))
btn_rebirth = tk.Button(prestige_frame, text="Rebirth\n(500K Clicks)", font=("Arial", 12, "bold"), bg="#e74c3c", fg="white",
                        command=do_rebirth, width=18)
btn_rebirth.pack(pady=(0, 10))

lbl_transcendence = tk.Label(prestige_frame, text="Transcendence: 0", font=("Arial", 12), bg=BG_CLICKER, fg=FG_LIGHT)
lbl_transcendence.pack(pady=(8, 2))
btn_transcend = tk.Button(prestige_frame, text="Transcend\n(20 Rebirth Pts)", font=("Arial", 12, "bold"), bg="#9b59b6", fg="white",
                         command=do_transcendence, width=18)
btn_transcend.pack(pady=(0, 6))


def refresh_clicker_stats():
    lbl_clicks.config(text=f"Clicks: {format_big(state.get('clicks', 0))}")
    lbl_clicks_per_press.config(text=f"Clicks/Press: {state.get('clicks_per_press', 1)} (+{clicks_per_press()})")
    lbl_mult.config(text=f"Mult: ×{state.get('mult', 1)} (Eff ×{effective_mult():.2f})")
    lbl_auto.config(text=f"Autoclickers: {state.get('autoclickers', 0)} (per tick: {clicks_per_tick()})")
    lbl_tp.config(text=f"Task Points: {state.get('task_points', 0)}")

    lbl_clicks_per_press_price.config(text=f"Price: {format_big(state.get('price_clicks_per_press', 10))} clicks")
    lbl_mult_price.config(text=f"Price: {format_big(state.get('price_mult', 100))} clicks")
    lbl_auto_price.config(text=f"Price: {format_big(state.get('price_auto', 50))} clicks")
    lbl_task_to_clicks_price.config(text=f"Price: {state.get('price_task_to_clicks', 20)} TP")

    lbl_intern.config(text=f"Interns: {state.get('interns', 0)} (Next {format_big(state.get('intern_price', 500))})")
    lbl_factory.config(text=f"Factories: {state.get('factories', 0)} (Next {format_big(state.get('factory_price', 2000))})")
    
    for a in ACTIONS:
        cost = state['costs'].get(a, 0)
        if state['unlocked'].get(a, False):
            unlock_labels[a].config(text=f"{a.title()}: UNLOCKED")
            unlock_buttons[a].config(state='disabled', bg="#1abc9c")
        else:
            unlock_labels[a].config(text=f"{a.title()}: cost {format_big(cost)}")
            unlock_buttons[a].config(state='normal', bg="#2ecc71")
            
    lbl_rebirth_points.config(text=f"Rebirth Points: {int(state.get('rebirth_points', 0))}")
    lbl_rebirths.config(text=f"Rebirths: {state.get('rebirths', 0)}")
    lbl_transcendence.config(text=f"Transcendence: {state.get('transcendence', 0)} (Mult ×{state.get('cosmic_mult', 1):.1f})")

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
    state["clicks"] += clicks_per_tick()
    interns_tick()

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