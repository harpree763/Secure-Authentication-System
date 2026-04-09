import tkinter as tk
import bcrypt
import pyotp
import time
import os

PASSWORD_FILE = "password.hash"
SECRET_FILE = "totp.secret"

if os.path.exists(SECRET_FILE):
    with open(SECRET_FILE, "r") as f:
        secret = f.read().strip()
else:
    secret = pyotp.random_base32()
    with open(SECRET_FILE, "w") as f:
        f.write(secret)

totp = pyotp.TOTP(secret)
attempts = 0
locked_until = 0

root = tk.Tk()
root.title("Secure Authentication System")
root.attributes('-fullscreen', True)
root.attributes('-topmost', True)

def disable_event():
    pass

root.protocol("WM_DELETE_WINDOW", disable_event)
root.bind("<Escape>", lambda e: "break")
root.bind("<Alt-F4>", lambda e: "break")

frame = tk.Frame(root)
frame.pack(expand=True)

def save_password(password):
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    with open(PASSWORD_FILE, "wb") as f:
        f.write(hashed)

def load_password():
    if os.path.exists(PASSWORD_FILE):
        with open(PASSWORD_FILE, "rb") as f:
            return f.read()
    return None

def make_show_toggle(entry):
    """Creates a Show/Hide button linked to the given entry widget."""
    def toggle():
        if entry.cget("show") == "*":
            entry.config(show="")
            btn.config(text="Hide")
        else:
            entry.config(show="*")
            btn.config(text="Show")
    btn = tk.Button(frame, text="Show", command=toggle, font=("Arial", 11))
    btn.pack(pady=2)
    return btn

def setup_password_screen():
    for widget in frame.winfo_children():
        widget.destroy()

    tk.Label(frame, text="Set Your Password", font=("Arial", 20)).pack(pady=20)

    entry = tk.Entry(frame, show="*", font=("Arial", 16))
    entry.pack(pady=10)
    make_show_toggle(entry)

    msg = tk.Label(frame, text="", fg="red")
    msg.pack()

    def save():
        password = entry.get()
        if len(password) < 8:
            msg.config(text="Password too short! (min 8 chars)")
            return
        save_password(password)
        login_screen(load_password())

    tk.Button(frame, text="Save Password", command=save, font=("Arial", 13)).pack(pady=10)

def login_screen(stored_password):
    for widget in frame.winfo_children():
        widget.destroy()

    tk.Label(frame, text="Enter Password", font=("Arial", 20)).pack(pady=20)

    password_entry = tk.Entry(frame, show="*", font=("Arial", 16))
    password_entry.pack(pady=10)
    make_show_toggle(password_entry)

    message = tk.Label(frame, text="", fg="red")
    message.pack()

    def check_password():
        global attempts, locked_until

        if time.time() < locked_until:
            remaining = int(locked_until - time.time())
            message.config(text=f"Locked! Try again in {remaining}s")
            return
        else:
            attempts = 0

        entered = password_entry.get()

        if bcrypt.checkpw(entered.encode(), stored_password):
            attempts = 0
            show_otp_screen()
        else:
            attempts += 1
            message.config(text=f"Wrong Password ({attempts}/3)")
            if attempts >= 3:
                locked_until = time.time() + 30
                message.config(text="Too many attempts! Locked 30s")

    tk.Button(frame, text="Login", command=check_password, font=("Arial", 13)).pack(pady=10)

def show_otp_screen():
    for widget in frame.winfo_children():
        widget.destroy()

    tk.Label(frame, text="Enter OTP", font=("Arial", 20)).pack(pady=20)
    tk.Label(frame, text=f"Your secret (share with authenticator app):\n{secret}",
             font=("Arial", 10), fg="gray").pack(pady=5)

    otp_entry = tk.Entry(frame, show="*", font=("Arial", 16))
    otp_entry.pack(pady=10)
    make_show_toggle(otp_entry)

    msg = tk.Label(frame, text="", fg="red")
    msg.pack()

    def verify():
        if totp.verify(otp_entry.get()):
            root.destroy()
        else:
            msg.config(text="Invalid OTP")

    tk.Button(frame, text="Verify", command=verify, font=("Arial", 13)).pack(pady=10)

stored_password = load_password()
if stored_password is None:
    setup_password_screen()
else:
    login_screen(stored_password)

root.mainloop()
