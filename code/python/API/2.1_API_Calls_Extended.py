# Reference: https://www.geeksforgeeks.org/python/python-gui-tkinter/
# Used for learning tkinter widgets, progressbar, and pack geometry manager
"""
I wanted to extend the password generator, so I added a gui, it's kinda clunky... But that's okay!
I also realized you can call multiple API's on a single program. The quote one you shared fit in.
Edit- I tried running it on my MacBook, with no luck, had to change some things, platform check, progress bar.
"""

from tkinter import messagebox
import requests
import json
import tkinter as tk
from tkinter import ttk
import os
import platform

generated_password = ""

def generate_password():
    global generated_password

    length = length_entry.get()
    api_key = api_key_entry.get()

    if not length.isdigit():
        messagebox.showerror("Error", "Please enter a valid number.")
        return

    if not api_key:
        messagebox.showerror("Error", "Please enter your API key.")
        return

    def cycle_quotes():
        api_url_quotes = 'https://api.api-ninjas.com/v1/quotes'
        response = requests.get(api_url_quotes, headers={'X-Api-Key': api_key_entry.get()})
        if response.status_code == requests.codes.ok:
            json_data = json.loads(response.text)
            quote = json_data[0]['quote']
            author = json_data[0]['author']
            quote_var.set(f'"{quote}"\n- {author}')

    def finish_generation():
        global generated_password
        quote_var.set("")
        api_url_1 = 'https://api.api-ninjas.com/v1/passwordgenerator?length={length}'.format(length=length)
        response = requests.get(api_url_1, headers={'X-Api-Key': api_key})

        if response.status_code == requests.codes.ok:
            json_data = json.loads(response.text)
            generated_password = json_data['random_password']
            save_button.pack(pady=10)
            reject_button.pack(pady=5)
        else:
            messagebox.showerror("Error:", f"{response.status_code}, {response.text}")

    def animate_progress(i=0):
        if i <= 100:
            progress['value'] = i
            if i == 0 or i % 60 == 0:
                cycle_quotes()
            root.after(50, animate_progress, i + 1)
        else:
            finish_generation()

    save_button.pack_forget()
    reject_button.pack_forget()
    progress['value'] = 0
    animate_progress()

def save_password():
    filepath = "generated_password.txt"
    with open(filepath, "w") as f:
        f.write("Your generated password:\n\n")
        f.write(generated_password)

    if platform.system() == "Windows":
        os.startfile(filepath)
    elif platform.system() == "Darwin":  # macOS
        os.system(f"open {filepath}")
    else:  # Linux
        os.system(f"xdg-open {filepath}")

def reject_password():
    global generated_password
    generated_password = ""
    save_button.pack_forget()
    reject_button.pack_forget()
    quote_var.set("")

# --- Window setup ---
root = tk.Tk()
root.title("Password Generator")
root.geometry("400x350")

tk.Label(root, text="API Key:").pack(pady=5)
api_key_entry = tk.Entry(root, width=40, show="*")  # show="*" hides input like a password field
api_key_entry.pack()

tk.Label(root, text="Password Length:").pack(pady=5)
length_entry = tk.Entry(root)
length_entry.pack()

tk.Button(root, text="Generate", command=generate_password).pack(pady=10)

progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
progress.pack(pady=5)

quote_var = tk.StringVar()  # StringVar lets labels update dynamically
tk.Label(root, textvariable=quote_var, wraplength=350, fg="gray", font=("italic", 9)).pack(pady=5)

save_button = tk.Button(root, text="Generation done! Open notepad?", command=save_password)
reject_button = tk.Button(root, text="Reject & Clear", command=reject_password)

root.mainloop()