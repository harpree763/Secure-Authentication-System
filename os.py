import tkinter as tk
import bcrypt
import pyotp
import time
import os

# ── FILES ───────────────────────────────────────────
PASSWORD_FILE = "password.hash"
SECRET_FILE   = "totp.secret"

# ── TOTP SECRET ─────────────────────────────────────
if os.path.exists(SECRET_FILE):
    with open(SECRET_FILE, "r") as f:
        secret = f.read().strip()
else:
    secret = pyotp.random_base32()
    with open(SECRET_FILE, "w") as f:
        f.write(secret)

totp = pyotp.TOTP(secret)

# ── LOCKOUT STATE ────────────────────────────────────
attempts     = 0
locked_until = 0

# ── COLORS ──────────────────────────────────────────
BG      = "#0a0e1a"
PANEL   = "#0d1220"
BORDER  = "#0a84ff"
GLOW    = "#00d4ff"
ACCENT  = "#00ffcc"
DIM     = "#111827"
SUBTEXT = "#3a6080"
TEXT    = "#cce8ff"
RED     = "#ff3355"
GREEN   = "#00ffaa"
YELLOW  = "#ffcc00"
MONO    = "Courier New"

# ── PASSWORD HELPERS ────────────────────────────────
def save_password(pw):
    with open(PASSWORD_FILE, "wb") as f:
        f.write(bcrypt.hashpw(pw.encode(), bcrypt.gensalt()))

def load_password():
    if os.path.exists(PASSWORD_FILE):
        with open(PASSWORD_FILE, "rb") as f:
            return f.read()
    return None

# ── ROOT WINDOW ─────────────────────────────────────
root = tk.Tk()
root.title("KALI // SECURE AUTH")
root.attributes('-fullscreen', True)
root.attributes('-topmost', True)
root.configure(bg=BG)
root.protocol("WM_DELETE_WINDOW", lambda: None)
root.bind("<Escape>",  lambda e: "break")
root.bind("<Alt-F4>",  lambda e: "break")

# ── TOP HUD BAR ─────────────────────────────────────
top_bar = tk.Frame(root, bg="#05090f", height=28)
top_bar.pack(fill="x", side="top")
tk.Label(top_bar, text="◉  KALI LINUX x64 — SECURE AUTHENTICATION SYSTEM",
         font=(MONO, 9, "bold"), bg="#05090f", fg=GLOW).pack(side="left", padx=10)
clock_lbl = tk.Label(top_bar, text="", font=(MONO, 9), bg="#05090f", fg=SUBTEXT)
clock_lbl.pack(side="right", padx=10)

def tick_clock():
    clock_lbl.config(text=time.strftime("%H:%M:%S  %Y-%m-%d"))
    root.after(1000, tick_clock)
tick_clock()

# ── BOTTOM HUD BAR ───────────────────────────────────
bot_bar = tk.Frame(root, bg="#05090f", height=24)
bot_bar.pack(fill="x", side="bottom")
tk.Label(bot_bar, text="ENCRYPTION: BCRYPT + TOTP RFC-6238  |  UNAUTHORIZED ACCESS PROHIBITED",
         font=(MONO, 8), bg="#05090f", fg=SUBTEXT).pack(side="left", padx=10)

# ── CENTER CARD ──────────────────────────────────────
center = tk.Frame(root, bg=BG)
center.pack(expand=True, fill="both")

card_border = tk.Frame(center, bg=BORDER, padx=2, pady=2)
card_border.place(relx=0.5, rely=0.5, anchor="center")

card = tk.Frame(card_border, bg=PANEL, padx=44, pady=32)
card.pack()

# Top accent line
tk.Frame(card, bg=GLOW, height=3).pack(fill="x", pady=(0, 16))

# Dragon ASCII
DRAGON = (
"  ⠀⠀⢀⣠⣴⣶⣿⣿⣷⣶⣦⣄⡀⠀⠀\n"
"  ⠀⣠⣾⣿⣿⡿⠛⠉⠛⢿⣿⣿⣷⣄⠀\n"
"  ⢀⣼⣿⣿⠟⠀⣀⣀⠀⠀⠻⣿⣿⣧⡀\n"
"  ⣿⣿⣿⠃⠀⣴⣿⣿⣷⡄⠀⢸⣿⣿⣿\n"
"  ⣿⣿⣿⣧⠀⠘⣿⣿⣿⠃⠀⣼⣿⣿⣿\n"
"  ⠸⣿⣿⣿⣦⠀⠙⠿⠋⢀⣴⣿⣿⣿⠇\n"
"  ⠀⠙⢿⣿⣿⣿⣦⣀⣴⣿⣿⣿⡿⠋⠀"
)
tk.Label(card, text=DRAGON, font=(MONO, 8),
         bg=PANEL, fg=BORDER, justify="center").pack(pady=(0, 4))

tk.Label(card, text="KALI LINUX",
         font=(MONO, 24, "bold"), bg=PANEL, fg=GLOW).pack()
tk.Label(card, text="S E C U R E   A U T H E N T I C A T I O N",
         font=(MONO, 8), bg=PANEL, fg=SUBTEXT).pack(pady=(2, 12))

# Divider
div = tk.Frame(card, bg=PANEL)
div.pack(fill="x", pady=(0, 16))
tk.Frame(div, bg=BORDER, height=1, width=110).pack(side="left", padx=4, pady=8)
tk.Label(div, text="◈", font=(MONO, 12), bg=PANEL, fg=GLOW).pack(side="left")
tk.Frame(div, bg=BORDER, height=1, width=110).pack(side="left", padx=4, pady=8)

# Content frame
frame = tk.Frame(card, bg=PANEL)
frame.pack()

# ── WIDGET HELPERS ───────────────────────────────────
def mk_entry(parent, show=""):
    wrap = tk.Frame(parent, bg=GLOW, padx=1, pady=1)
    wrap.pack(pady=3, fill="x")
    inner = tk.Frame(wrap, bg=DIM, padx=4, pady=3)
    inner.pack(fill="x")
    e = tk.Entry(inner, show=show, font=(MONO, 13),
                 bg=DIM, fg=ACCENT, insertbackground=GLOW,
                 relief="flat", bd=0, width=26,
                 selectbackground=BORDER, selectforeground=BG)
    e.pack(fill="x", ipady=4)
    return e

def mk_toggle(parent, entry):
    state = {"on": False}
    def toggle():
        state["on"] = not state["on"]
        entry.config(show="" if state["on"] else "*")
        btn.config(text="⬛ HIDE" if state["on"] else "⬜ SHOW",
                   fg=RED if state["on"] else ACCENT)
    btn = tk.Button(parent, text="⬜ SHOW", command=toggle,
                    font=(MONO, 9, "bold"), bg=PANEL, fg=ACCENT,
                    activebackground=PANEL, relief="flat",
                    bd=0, cursor="hand2")
    btn.pack(pady=1)

def mk_button(parent, text, cmd, color=BORDER):
    f = tk.Frame(parent, bg=color, padx=1, pady=1)
    f.pack(pady=8)
    b = tk.Button(f, text=text, command=cmd,
                  font=(MONO, 11, "bold"), bg=DIM, fg=color,
                  activebackground=color, activeforeground=BG,
                  relief="flat", bd=0, padx=24, pady=8, cursor="hand2")
    b.pack()
    b.bind("<Enter>", lambda e: b.config(bg=color, fg=BG))
    b.bind("<Leave>", lambda e: b.config(bg=DIM, fg=color))

def mk_msg(parent):
    l = tk.Label(parent, text="", font=(MONO, 10), bg=PANEL, fg=RED)
    l.pack(pady=3)
    return l

def mk_flabel(parent, text):
    tk.Label(parent, text="▸ " + text,
             font=(MONO, 9, "bold"), bg=PANEL, fg=BORDER).pack(anchor="w", pady=(8,1))

def clear():
    for w in frame.winfo_children():
        w.destroy()

# ── SCREENS ──────────────────────────────────────────
def setup_screen():
    clear()
    tk.Label(frame, text="[ SET MASTER PASSWORD ]",
             font=(MONO, 13, "bold"), bg=PANEL, fg=GLOW).pack(pady=(0, 4))
    tk.Label(frame, text="First run detected. Create your password.",
             font=(MONO, 9), bg=PANEL, fg=SUBTEXT).pack(pady=(0, 10))

    mk_flabel(frame, "NEW PASSWORD  (min 8 chars)")
    entry = mk_entry(frame, show="*")
    entry.focus()
    mk_toggle(frame, entry)
    msg = mk_msg(frame)

    def save():
        pw = entry.get()
        if len(pw) < 8:
            msg.config(text="⚠  Too short! Min 8 characters.", fg=YELLOW)
            return
        save_password(pw)
        msg.config(text="✔  Password saved!", fg=GREEN)
        root.after(800, lambda: login_screen(load_password()))

    mk_button(frame, "  ► SAVE PASSWORD  ", save)
    entry.bind("<Return>", lambda e: save())


def login_screen(stored):
    clear()
    global attempts, locked_until
    tk.Label(frame, text="[ AUTHENTICATION REQUIRED ]",
             font=(MONO, 13, "bold"), bg=PANEL, fg=GLOW).pack(pady=(0, 4))
    tk.Label(frame, text="Enter master password to continue.",
             font=(MONO, 9), bg=PANEL, fg=SUBTEXT).pack(pady=(0, 10))

    mk_flabel(frame, "MASTER PASSWORD")
    pw_entry = mk_entry(frame, show="*")
    pw_entry.focus()
    mk_toggle(frame, pw_entry)
    msg = mk_msg(frame)

    # Attempt indicator dots
    dot_row = tk.Frame(frame, bg=PANEL)
    dot_row.pack(pady=3)
    dots = [tk.Label(dot_row, text="○", font=(MONO, 13),
                     bg=PANEL, fg=SUBTEXT) for _ in range(3)]
    [d.pack(side="left", padx=5) for d in dots]

    def refresh_dots():
        for i, d in enumerate(dots):
            d.config(text="●" if i < attempts else "○",
                     fg=RED if i < attempts else SUBTEXT)

    def authenticate():
        global attempts, locked_until
        if time.time() < locked_until:
            rem = int(locked_until - time.time())
            msg.config(text=f"⛔  Locked! {rem}s remaining", fg=RED)
            return
        else:
            attempts = 0
            refresh_dots()

        if bcrypt.checkpw(pw_entry.get().encode(), stored):
            attempts = 0
            msg.config(text="✔  Correct! Loading 2FA...", fg=GREEN)
            root.after(600, otp_screen)
        else:
            attempts += 1
            refresh_dots()
            if attempts >= 3:
                locked_until = time.time() + 30
                msg.config(text="⛔  Too many attempts! Locked 30s", fg=RED)
            else:
                msg.config(text=f"✘  Wrong Password [{attempts}/3]", fg=RED)

    mk_button(frame, "  ► LOGIN  ", authenticate)
    pw_entry.bind("<Return>", lambda e: authenticate())


def otp_screen():
    clear()
    tk.Label(frame, text="[ TWO-FACTOR VERIFICATION ]",
             font=(MONO, 13, "bold"), bg=PANEL, fg=GLOW).pack(pady=(0, 4))
    tk.Label(frame, text="Enter the 6-digit OTP from your authenticator.",
             font=(MONO, 9), bg=PANEL, fg=SUBTEXT).pack(pady=(0, 8))

    # Secret box
    s = tk.Frame(frame, bg=DIM, padx=10, pady=6)
    s.pack(fill="x", pady=6)
    tk.Label(s, text="TOTP SECRET:", font=(MONO, 8), bg=DIM, fg=SUBTEXT).pack()
    tk.Label(s, text=secret, font=(MONO, 9, "bold"), bg=DIM,
             fg=BORDER, wraplength=300, justify="center").pack()

    mk_flabel(frame, "ONE-TIME PASSWORD")
    otp_entry = mk_entry(frame, show="*")
    otp_entry.focus()
    mk_toggle(frame, otp_entry)
    msg = mk_msg(frame)

    # Live OTP countdown
    timer = tk.Label(frame, text="", font=(MONO, 9), bg=PANEL, fg=YELLOW)
    timer.pack(pady=2)
    def tick():
        rem = 30 - (int(time.time()) % 30)
        timer.config(text=f"OTP expires in: {rem:02d}s  [{'█'*rem}{'░'*(30-rem)}]")
        root.after(1000, tick)
    tick()

    def verify():
        if totp.verify(otp_entry.get()):
            msg.config(text="✔  Access Granted! Welcome.", fg=GREEN)
            root.after(700, root.destroy)
        else:
            msg.config(text="✘  Invalid OTP. Try again.", fg=RED)

    mk_button(frame, "  ► VERIFY OTP  ", verify, GREEN)
    otp_entry.bind("<Return>", lambda e: verify())


# ── LAUNCH ───────────────────────────────────────────
stored = load_password()
if stored is None:
    setup_screen()
else:
    login_screen(stored)

root.mainloop()
