import tkinter as tk
from tkinter import scrolledtext

def read_log_file(log_file):
    with open(log_file, 'r') as f:
        return f.read()

def update_log_display():
    log_content = read_log_file(log_file)
    log_display.delete(1.0, tk.END)
    log_display.insert(tk.INSERT, log_content)
    root.after(60000, update_log_display)  # Update every minute

log_file = '/home/peter-kiarie/System_Testing/Data_logfile'

root = tk.Tk()
root.title("Network Data Usage")

log_display = scrolledtext.ScrolledText(root, width=100, height=30)
log_display.pack()

update_log_display()

root.mainloop()