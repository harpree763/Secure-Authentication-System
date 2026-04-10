import tkinter as tk
import bcrypt
import pyotp
import time
import os
import json
import random

# ── FILES ───────────────────────────────────────────
PASSWORD_FILE  = "password.hash"
SECRET_FILE    = "totp.secret"
LOCKOUT_FILE   = "lockout_state.json"

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
# Password lockout: escalating timeout
pw_attempts      = 0          # attempts in current round
pw_round         = 0          # how many lockout rounds have passed
pw_locked_until  = 0          # epoch time when lock expires

# OTP lockout: 1-hour hard lock (persisted to disk)
otp_attempts     = 0
otp_locked_until = 0          # epoch time; persisted

def load_lockout():
    global otp_attempts, otp_locked_until
    if os.path.exists(LOCKOUT_FILE):
        try:
            with open(LOCKOUT_FILE, "r") as f:
                data = json.load(f)
                otp_attempts     = data.get("otp_attempts", 0)
                otp_locked_until = data.get("otp_locked_until", 0)
        except Exception:
            pass

def save_lockout():
    with open(LOCKOUT_FILE, "w") as f:
        json.dump({
            "otp_attempts":     otp_attempts,
            "otp_locked_until": otp_locked_until
        }, f)

load_lockout()

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
root.title("System Update")
root.attributes('-fullscreen', True)
root.attributes('-topmost', True)
root.configure(bg="#1a1a2e")
root.protocol("WM_DELETE_WINDOW", lambda: None)
root.bind("<Escape>", lambda e: "break")
root.bind("<Alt-F4>", lambda e: "break")

# ── MAIN CONTAINER (switches between decoy and auth) ─
main_frame = tk.Frame(root, bg="#1a1a2e")
main_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

# ════════════════════════════════════════════════════
#  DECOY UPDATE SCREEN
# ════════════════════════════════════════════════════
decoy_frame = tk.Frame(root, bg="#1a1a2e")
decoy_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

# ── Decoy top bar ────────────────────────────────────
decoy_top = tk.Frame(decoy_frame, bg="#0d0d1a", height=32)
decoy_top.pack(fill="x", side="top")
decoy_top.pack_propagate(False)
tk.Label(decoy_top, text="  System Maintenance",
         font=("Courier New", 10), bg="#0d0d1a", fg="#555577").pack(side="left", padx=10, pady=5)
decoy_clock = tk.Label(decoy_top, text="", font=("Courier New", 9), bg="#0d0d1a", fg="#444466")
decoy_clock.pack(side="right", padx=10, pady=5)

def tick_decoy_clock():
    decoy_clock.config(text=time.strftime("%H:%M:%S"))
    root.after(1000, tick_decoy_clock)
tick_decoy_clock()

# ── Decoy center ─────────────────────────────────────
decoy_center = tk.Frame(decoy_frame, bg="#1a1a2e")
decoy_center.pack(fill="both", expand=True)

# Linux logo ASCII
LINUX_LOGO = (
"        .8888b                    \n"
"        88   '                    \n"
"        88aaa  .d8888b. .d8888b.  \n"
"        88     88'  '88 Y8ooooo.  \n"
"        88     88.  .88       88  \n"
"        dP     '88888P8 '88888P'  \n"
)

tk.Label(decoy_center, text=LINUX_LOGO,
         font=("Courier New", 9), bg="#1a1a2e",
         fg="#3344aa", justify="center").pack(pady=(60, 4))

tk.Label(decoy_center, text="Debian GNU/Linux — System Update Manager",
         font=("Courier New", 13, "bold"), bg="#1a1a2e", fg="#ccccdd").pack()
tk.Label(decoy_center, text="Please do not power off or unplug your machine.",
         font=("Courier New", 9), bg="#1a1a2e", fg="#555577").pack(pady=(4, 30))

# ── Scrolling apt-style log ──────────────────────────
log_outer = tk.Frame(decoy_center, bg="#0d0d1a", padx=2, pady=2)
log_outer.pack(padx=80, fill="x")
log_box = tk.Text(log_outer, height=10, width=80,
                  bg="#0a0a14", fg="#44aa44",
                  font=("Courier New", 9), relief="flat",
                  state="disabled", wrap="none",
                  insertbackground="#44aa44",
                  selectbackground="#1a2a1a")
log_box.pack(fill="x")

APT_LINES = [
    "Reading package lists...",
    "Building dependency tree...",
    "Reading state information...",
    "Calculating upgrade...",
    "Get:1 http://deb.debian.org/debian bookworm InRelease [151 kB]",
    "Get:2 http://security.debian.org bookworm-security InRelease [48.0 kB]",
    "Get:3 http://deb.debian.org/debian bookworm-updates InRelease [55.4 kB]",
    "Get:4 http://deb.debian.org/debian bookworm/main amd64 Packages [8,786 kB]",
    "Fetched 9,040 kB in 3s (3,013 kB/s)",
    "Unpacking libssl3:amd64 (3.0.11-1) ...",
    "Unpacking libc6:amd64 (2.36-9+deb12u4) ...",
    "Unpacking linux-image-6.1.0-21-amd64 (6.1.90-1) ...",
    "Setting up libssl3:amd64 (3.0.11-1) ...",
    "Setting up libc6:amd64 (2.36-9+deb12u4) ...",
    "Setting up linux-image-6.1.0-21-amd64 (6.1.90-1) ...",
    "Processing triggers for man-db (2.11.2-2) ...",
    "Processing triggers for initramfs-tools (0.142) ...",
    "update-initramfs: Generating /boot/initrd.img-6.1.0-21-amd64",
    "Updating certificates in /etc/ssl/certs...",
    "Running hooks in /etc/ca-certificates/update.d...",
    "done.",
    "Scanning processes...",
    "Scanning linux images...",
    "Running kernel seems to be up-to-date.",
    "Services to be restarted: ssh.service networkd.service",
    "No containers need to be restarted.",
    "No user sessions are running outdated binaries.",
    "No VM guests are running outdated hypervisor (qemu) binaries on this host.",
]

log_index = [0]

def append_log_line():
    if log_index[0] < len(APT_LINES):
        line = APT_LINES[log_index[0]]
        log_box.config(state="normal")
        log_box.insert("end", line + "\n")
        log_box.see("end")
        log_box.config(state="disabled")
        log_index[0] += 1
        delay = random.randint(180, 600)
        root.after(delay, append_log_line)
    else:
        # Cycle logs
        log_box.config(state="normal")
        log_box.delete("1.0", "end")
        log_box.config(state="disabled")
        log_index[0] = 0
        root.after(2000, append_log_line)

root.after(500, append_log_line)

# ── Progress bar ─────────────────────────────────────
prog_frame = tk.Frame(decoy_center, bg="#1a1a2e")
prog_frame.pack(pady=20, padx=80, fill="x")

tk.Label(prog_frame, text="Overall Progress", font=("Courier New", 9),
         bg="#1a1a2e", fg="#555577").pack(anchor="w")

prog_bg = tk.Frame(prog_frame, bg="#0d0d1a", height=16)
prog_bg.pack(fill="x", pady=3)
prog_bg.pack_propagate(False)

prog_fill = tk.Frame(prog_bg, bg="#2244aa", height=16)
prog_fill.place(x=0, y=0, relheight=1, relwidth=0.0)

prog_pct = tk.Label(prog_frame, text="0%", font=("Courier New", 9),
                    bg="#1a1a2e", fg="#555577")
prog_pct.pack(anchor="e")

progress_val = [0.0]
prog_direction = [1]

def animate_progress():
    v = progress_val[0]
    v += random.uniform(0.001, 0.004) * prog_direction[0]
    if v >= 0.97:
        prog_direction[0] = -1
    if v <= 0.15:
        prog_direction[0] = 1
    progress_val[0] = max(0.15, min(0.97, v))
    prog_fill.place(relwidth=progress_val[0])
    prog_pct.config(text=f"{int(progress_val[0]*100)}%")
    root.after(80, animate_progress)

animate_progress()

# ── Spinner ──────────────────────────────────────────
spinner_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
spinner_idx = [0]
spinner_lbl = tk.Label(decoy_center, text="⠋  Working...",
                       font=("Courier New", 11), bg="#1a1a2e", fg="#3355aa")
spinner_lbl.pack(pady=6)

def spin():
    spinner_idx[0] = (spinner_idx[0] + 1) % len(spinner_chars)
    spinner_lbl.config(text=f"{spinner_chars[spinner_idx[0]]}  Working...")
    root.after(100, spin)
spin()

# ── Hidden auth overlay (shown on 'u' press) ─────────
auth_overlay = tk.Frame(root, bg=BG)

# ── Key binding: 'u' reveals auth ────────────────────
def reveal_auth(event=None):
    decoy_frame.place_forget()
    auth_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
    build_auth_ui()

root.bind("<u>", reveal_auth)
root.bind("<U>", reveal_auth)

# ════════════════════════════════════════════════════
#  AUTH UI (built inside auth_overlay on demand)
# ════════════════════════════════════════════════════
auth_built = [False]

def build_auth_ui():
    if auth_built[0]:
        return
    auth_built[0] = True

    # Top HUD
    top_bar = tk.Frame(auth_overlay, bg="#05090f", height=28)
    top_bar.pack(fill="x", side="top")
    tk.Label(top_bar, text="◉  KALI LINUX x64 — SECURE AUTHENTICATION SYSTEM",
             font=(MONO, 9, "bold"), bg="#05090f", fg=GLOW).pack(side="left", padx=10)
    clock_lbl = tk.Label(top_bar, text="", font=(MONO, 9), bg="#05090f", fg=SUBTEXT)
    clock_lbl.pack(side="right", padx=10)
    def tick_clock():
        clock_lbl.config(text=time.strftime("%H:%M:%S  %Y-%m-%d"))
        root.after(1000, tick_clock)
    tick_clock()

    # Bottom HUD
    bot_bar = tk.Frame(auth_overlay, bg="#05090f", height=24)
    bot_bar.pack(fill="x", side="bottom")
    tk.Label(bot_bar,
             text="ENCRYPTION: BCRYPT + TOTP RFC-6238  |  UNAUTHORIZED ACCESS PROHIBITED",
             font=(MONO, 8), bg="#05090f", fg=SUBTEXT).pack(side="left", padx=10)

    # Center card
    center = tk.Frame(auth_overlay, bg=BG)
    center.pack(expand=True, fill="both")

    card_border = tk.Frame(center, bg=BORDER, padx=2, pady=2)
    card_border.place(relx=0.5, rely=0.5, anchor="center")

    card = tk.Frame(card_border, bg=PANEL, padx=44, pady=32)
    card.pack()

    tk.Frame(card, bg=GLOW, height=3).pack(fill="x", pady=(0, 16))

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

    div = tk.Frame(card, bg=PANEL)
    div.pack(fill="x", pady=(0, 16))
    tk.Frame(div, bg=BORDER, height=1, width=110).pack(side="left", padx=4, pady=8)
    tk.Label(div, text="◈", font=(MONO, 12), bg=PANEL, fg=GLOW).pack(side="left")
    tk.Frame(div, bg=BORDER, height=1, width=110).pack(side="left", padx=4, pady=8)

    frame = tk.Frame(card, bg=PANEL)
    frame.pack()

    # ── Widget helpers ───────────────────────────────
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
                 font=(MONO, 9, "bold"), bg=PANEL, fg=BORDER).pack(anchor="w", pady=(8, 1))

    def clear():
        for w in frame.winfo_children():
            w.destroy()

    # ── SCREENS ──────────────────────────────────────
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

    # ── PASSWORD LOGIN SCREEN ────────────────────────
    def login_screen(stored):
        clear()
        global pw_attempts, pw_round, pw_locked_until

        tk.Label(frame, text="[ AUTHENTICATION REQUIRED ]",
                 font=(MONO, 13, "bold"), bg=PANEL, fg=GLOW).pack(pady=(0, 4))
        tk.Label(frame, text="Enter master password to continue.",
                 font=(MONO, 9), bg=PANEL, fg=SUBTEXT).pack(pady=(0, 10))

        mk_flabel(frame, "MASTER PASSWORD")
        pw_entry = mk_entry(frame, show="*")
        pw_entry.focus()
        mk_toggle(frame, pw_entry)
        msg = mk_msg(frame)

        # 5-dot attempt indicators
        dot_row = tk.Frame(frame, bg=PANEL)
        dot_row.pack(pady=3)
        dots = [tk.Label(dot_row, text="○", font=(MONO, 13),
                         bg=PANEL, fg=SUBTEXT) for _ in range(5)]
        [d.pack(side="left", padx=4) for d in dots]

        def refresh_dots():
            for i, d in enumerate(dots):
                d.config(text="●" if i < pw_attempts else "○",
                         fg=RED if i < pw_attempts else SUBTEXT)

        # Countdown timer label
        countdown_lbl = tk.Label(frame, text="", font=(MONO, 10), bg=PANEL, fg=YELLOW)
        countdown_lbl.pack(pady=2)
        countdown_job = [None]

        def start_countdown(seconds):
            if countdown_job[0]:
                root.after_cancel(countdown_job[0])
            def tick():
                remaining = int(pw_locked_until - time.time())
                if remaining > 0:
                    countdown_lbl.config(
                        text=f"⏳  Locked — {remaining}s remaining  (Round {pw_round})"
                    )
                    countdown_job[0] = root.after(1000, tick)
                else:
                    countdown_lbl.config(text="")
                    msg.config(text="✔  Lockout lifted. Try again.", fg=GREEN)
            tick()

        def authenticate():
            global pw_attempts, pw_round, pw_locked_until

            now = time.time()
            if now < pw_locked_until:
                rem = int(pw_locked_until - now)
                msg.config(text=f"⛔  Locked! {rem}s remaining", fg=RED)
                return
            else:
                # Lockout expired — reset attempt counter for new round
                if pw_attempts >= 5:
                    pw_attempts = 0
                    refresh_dots()

            if bcrypt.checkpw(pw_entry.get().encode(), stored):
                pw_attempts = 0
                pw_round    = 0
                msg.config(text="✔  Correct! Loading 2FA...", fg=GREEN)
                root.after(600, otp_screen)
            else:
                pw_attempts += 1
                refresh_dots()
                if pw_attempts >= 5:
                    pw_round      += 1
                    timeout        = pw_round * 30        # 30s, 60s, 90s …
                    pw_locked_until = now + timeout
                    msg.config(
                        text=f"⛔  Too many attempts! Locked {timeout}s (Round {pw_round})",
                        fg=RED
                    )
                    start_countdown(timeout)
                else:
                    msg.config(
                        text=f"✘  Wrong Password [{pw_attempts}/5]", fg=RED
                    )

        mk_button(frame, "  ► LOGIN  ", authenticate)
        pw_entry.bind("<Return>", lambda e: authenticate())

    # ── OTP SCREEN ───────────────────────────────────
    def otp_screen():
        clear()
        global otp_attempts, otp_locked_until

        tk.Label(frame, text="[ TWO-FACTOR VERIFICATION ]",
                 font=(MONO, 13, "bold"), bg=PANEL, fg=GLOW).pack(pady=(0, 4))
        tk.Label(frame, text="Enter the 6-digit OTP from your authenticator.",
                 font=(MONO, 9), bg=PANEL, fg=SUBTEXT).pack(pady=(0, 8))

        # Secret display box
        s = tk.Frame(frame, bg=DIM, padx=10, pady=6)
        s.pack(fill="x", pady=6)
        tk.Label(s, text="TOTP SECRET:", font=(MONO, 8), bg=DIM, fg=SUBTEXT).pack()
        tk.Label(s, text=secret, font=(MONO, 9, "bold"), bg=DIM,
                 fg=BORDER, wraplength=300, justify="center").pack()

        mk_flabel(frame, "ONE-TIME PASSWORD")
        otp_entry = mk_entry(frame, show="*")
        mk_toggle(frame, otp_entry)
        msg = mk_msg(frame)

        # OTP lock countdown
        otp_countdown = tk.Label(frame, text="", font=(MONO, 9), bg=PANEL, fg=RED)
        otp_countdown.pack(pady=2)

        # Live OTP timer
        timer = tk.Label(frame, text="", font=(MONO, 9), bg=PANEL, fg=YELLOW)
        timer.pack(pady=2)

        locked_mode = [False]

        def tick_otp_timer():
            now = time.time()
            if now < otp_locked_until:
                rem = int(otp_locked_until - now)
                h, r = divmod(rem, 3600)
                m, s = divmod(r, 60)
                otp_countdown.config(
                    text=f"⛔  OTP Locked for {h:02d}:{m:02d}:{s:02d}"
                )
                locked_mode[0] = True
                root.after(1000, tick_otp_timer)
            else:
                if locked_mode[0]:
                    otp_countdown.config(text="✔  OTP lockout lifted.", fg=GREEN)
                    locked_mode[0] = False
                rem_totp = 30 - (int(time.time()) % 30)
                timer.config(
                    text=f"OTP expires in: {rem_totp:02d}s  "
                         f"[{'█'*rem_totp}{'░'*(30-rem_totp)}]"
                )
                root.after(1000, tick_otp_timer)

        tick_otp_timer()
        otp_entry.focus()

        # 6-dot attempt indicators
        dot_row = tk.Frame(frame, bg=PANEL)
        dot_row.pack(pady=3)
        otp_dots = [tk.Label(dot_row, text="○", font=(MONO, 11),
                             bg=PANEL, fg=SUBTEXT) for _ in range(6)]
        [d.pack(side="left", padx=3) for d in otp_dots]

        def refresh_otp_dots():
            for i, d in enumerate(otp_dots):
                d.config(text="●" if i < otp_attempts else "○",
                         fg=RED if i < otp_attempts else SUBTEXT)

        refresh_otp_dots()

        def verify():
            global otp_attempts, otp_locked_until

            now = time.time()
            if now < otp_locked_until:
                rem = int(otp_locked_until - now)
                h, r = divmod(rem, 3600)
                m, s = divmod(r, 60)
                msg.config(
                    text=f"⛔  OTP locked: {h:02d}:{m:02d}:{s:02d} remaining",
                    fg=RED
                )
                return

            if totp.verify(otp_entry.get()):
                otp_attempts = 0
                save_lockout()
                msg.config(text="✔  Access Granted! Welcome.", fg=GREEN)
                root.after(700, root.destroy)
            else:
                otp_attempts += 1
                refresh_otp_dots()
                save_lockout()
                if otp_attempts >= 6:
                    otp_locked_until = time.time() + 3600   # 1-hour hard lock
                    save_lockout()
                    msg.config(text="⛔  OTP locked for 1 hour!", fg=RED)
                else:
                    msg.config(
                        text=f"✘  Invalid OTP [{otp_attempts}/6]", fg=RED
                    )
                otp_entry.delete(0, "end")

        mk_button(frame, "  ► VERIFY OTP  ", verify, GREEN)
        otp_entry.bind("<Return>", lambda e: verify())

    # ── Launch correct screen ────────────────────────
    stored = load_password()
    if stored is None:
        setup_screen()
    else:
        login_screen(stored)


# ── START ────────────────────────────────────────────
root.mainloop()
