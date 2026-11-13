import tkinter as tk
import json
import os
import time

from storage import generate_key, encrypt_data, decrypt_data, save_encrypted_data, load_encrypted_data
from hashin import hash_password, verify_password
from passwordstrength import calculate_entropy, password_strength
import secrets
import string
#Secrets is a module that generates cryptographically strong random numbers which are
#Which is quite suitable for storing stuff like passwords and security tokens

BG_COLOUR = "#121212"
FG_COLOUR = "#ffffff"
BTN_COLOUR = "#1f1f1f"
ENTRY_BG = "#1e1e1e"
ACCENT = "#4CAF50"
FONT = ("Segoe UI", 11)
TITLE_FONT = ("Segoe UI", 18, "bold")
#Above is the theme of the ui, where I set the background colour, foreground colour, and the font.

VAULT_FILE = "vault.dat"
MASTER_HASH_FILE = "master.hash"
KEY_FILE = "key.key"
#The files that need to be accessed include the vault filie which stores all of the hashed passwords, the master hash file has the master password stored in it, and the key file stores 
#the necessary keys for encryption and decryption
FAILED_ATTEMPTS = 0
LOCKED_UNTIL = None
#These are constants for how many attempts have been attempted and how long
#the program is locked for when the wrong password is attempted too many times

class PasswordManagerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Password Manager")
        self.geometry("500x420")
        self.configure(bg=BG_COLOUR)

        self.frames = {}
        for page in (LoginPage, HomePage, AddPasswordPage, ViewPasswordsPage, RecoveryHubPage, AddRecoveryPage, ViewRecoveryPage):
            frame = page(self)
            self.frames[page] = frame
            frame.place(relwidth=1, relheight=1)

        self.show_frame(LoginPage)

    def show_frame(self, page):
        frame = self.frames[page]
        if hasattr(frame, "on_show"):
            frame.on_show()
        frame.tkraise()
#The class PasswordManager app is the main app window, that initialises and stacks all the pages.
#it stacks the pages as frames, and it shows or hides them using show_frame

class ModernDialogue(tk.Toplevel):
    def __init__(self, parent, title, message, colour=ACCENT):
        super().__init__(parent)
        self.configure(bg=BG_COLOUR)
        self.geometry("350x180")
        self.resizable(False, False)
        self.title("")
        self.transient(parent)
        self.grab_set()
        tk.Label(self,
                 text=title,
                 font=("Segoe UI", 14, "bold"),
                 bg=BG_COLOUR,
                 fg=colour).pack(pady=(20, 5))
        tk.Label(self,
                 text=message,
                 font=FONT,
                 bg=BG_COLOUR,
                 fg=FG_COLOUR,
                 wraplength=300,
                 justify="center").pack(pady=10)
        tk.Button(self,
                  text="OK",
                  command=self.destroy,
                  bg=BTN_COLOUR,
                  fg=FG_COLOUR,
                  activebackground=ACCENT,
                  padx=20,
                  pady=6).pack(pady=10)
#ModernDialogue is a reusable popup i have made that can be used for alerts and confirmations
#it has a title, message and text colour with an ok buttom to remove it.

class LoginPage(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=BG_COLOUR)

        tk.Label(self, text="Master Password",
                 font=TITLE_FONT, bg=BG_COLOUR, fg=FG_COLOUR).pack(pady=30)

        self.password_entry = tk.Entry(
            self, show="*", font=FONT,
            bg=ENTRY_BG, fg=FG_COLOUR,
            insertbackground=FG_COLOUR
        )
        self.password_entry.pack(pady=10)

        tk.Button(self, text="Login",
                  font=FONT, bg=BTN_COLOUR, fg=FG_COLOUR,
                  command=self.login).pack(pady=15)

    def on_show(self):
        self.password_entry.delete(0, tk.END)

    def login(self):
        global FAILED_ATTEMPTS, LOCKED_UNTIL

        pwd = self.password_entry.get()
        if not pwd:
            ModernDialogue(self, "Error", "Password required", "red")
            return

        if LOCKED_UNTIL and time.time() < LOCKED_UNTIL:
            ModernDialogue(self, "Locked", "Try again later", "red")
            return

        if not os.path.exists(MASTER_HASH_FILE):
            #first time running the program so we need to set everything up
            hashvalue = hash_password(pwd)
            with open(MASTER_HASH_FILE, "wb") as f:
                f.write(hashvalue)

            key = generate_key()
            keyfile = open(KEY_FILE, "wb")
            keyfile.write(key)
            keyfile.close()

            emptyvault = json.dumps({})
            enc = encrypt_data(emptyvault, key)
            save_encrypted_data(enc, VAULT_FILE)

            ModernDialogue(self, "Created", "Master password set", "green")
            self.master.show_frame(HomePage)
            return

        stored = open(MASTER_HASH_FILE, "rb").read()

        if verify_password(pwd, stored):
            FAILED_ATTEMPTS = 0
            self.master.show_frame(HomePage)
        else:
            FAILED_ATTEMPTS = FAILED_ATTEMPTS + 1
            if FAILED_ATTEMPTS >= 3:
                LOCKED_UNTIL = time.time() + 30
                FAILED_ATTEMPTS = 0
                ModernDialogue(self, "Locked", "Locked 30 seconds", "red")
            else:
                ModernDialogue(self, "Error", "Access denied", "red")
#The class loginpage handles the login, and on the very first run of the program it creates
#the master password hash and it encrypts an empty vault, on other subsequent runs it 
#verifies the password with lockout after 3 failed attempts (of 30 seconds)


class HomePage(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=BG_COLOUR)

        tk.Label(self, text="Home",
                 font=TITLE_FONT, bg=BG_COLOUR, fg=FG_COLOUR).pack(pady=30)

        self.btn("Add Password", lambda: master.show_frame(AddPasswordPage))
        self.btn("View Passwords", lambda: master.show_frame(ViewPasswordsPage))
        self.btn("Recovery Codes", lambda: master.show_frame(RecoveryHubPage))
        self.btn("Logout", lambda: master.show_frame(LoginPage))

    def btn(self, text, cmd):
        tk.Button(self, text=text, command=cmd,
                  font=FONT, bg=BTN_COLOUR, fg=FG_COLOUR,
                  padx=20, pady=8).pack(pady=10)
#The home page has a simple navigation with buttons to add and view passwords, manage recovery
#codes or logout


class AddPasswordPage(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=BG_COLOUR)

        tk.Label(self, text="Add Password",
                 font=TITLE_FONT, bg=BG_COLOUR, fg=FG_COLOUR).pack(pady=20)

        self.service = self.entry("Service")
        self.password = self.entry("Password", hide=True)
        self.confirm_password = self.entry("Confirm Password", hide=True)

        self.match_label = tk.Label(self, text="", bg=BG_COLOUR, fg=FG_COLOUR)
        self.match_label.pack()

        self.btn("Generate Strong Password", self.generate_password)

        self.strength = tk.Label(self, text="Strength:",
                                 bg=BG_COLOUR, fg=FG_COLOUR)
        self.strength.pack()

        self.save_btn = tk.Button(self, text="Save", command=self.save,
                                  bg=BTN_COLOUR, fg=FG_COLOUR,
                                  padx=20, pady=8, state=tk.DISABLED)
        self.save_btn.pack(pady=8)

        self.btn("Back", lambda: master.show_frame(HomePage))

        self.password.bind("<KeyRelease>", self.on_password_change)
        self.confirm_password.bind("<KeyRelease>", self.on_confirm_change)

    def on_show(self):
        self.clear()

    def entry(self, label, hide=False):
        tk.Label(self, text=label, bg=BG_COLOUR, fg=FG_COLOUR).pack()
        e = tk.Entry(self, show="*" if hide else "",
                     bg=ENTRY_BG, fg=FG_COLOUR,
                     insertbackground=FG_COLOUR)
        e.pack(pady=5)
        return e

    def btn(self, t, c):
        tk.Button(self, text=t, command=c,
                  bg=BTN_COLOUR, fg=FG_COLOUR,
                  padx=20, pady=8).pack(pady=8)

    def update_strength(self, _=None):
        pwd = self.password.get()
        entropyvalue = calculate_entropy(pwd)
        s = password_strength(entropyvalue)
        if s == "Weak":
            colour = "red"
        elif s == "Medium":
            colour = "orange"
        elif s == "Strong":
            colour = ACCENT
        else:
            colour = FG_COLOUR
        self.strength.config(text="Strength: " + s, fg=colour)

    def update_match_label(self):
        """Update the match indicator and enable/disable Save accordingly."""
        pwd = self.password.get()
        confirm = self.confirm_password.get()

        if not pwd and not confirm:
            self.match_label.config(text="", fg=FG_COLOUR)
            self.save_btn.config(state=tk.DISABLED)
        elif verify_password(confirm, hash_password(pwd)):
            self.match_label.config(text="✔ Passwords match", fg=ACCENT)
            self.save_btn.config(state=tk.NORMAL)
        else:
            self.match_label.config(text="✘ Passwords do not match", fg="red")
            self.save_btn.config(state=tk.DISABLED)

    def on_password_change(self, _=None):
        self.update_strength()
        self.update_match_label()

    def on_confirm_change(self, _=None):
        self.update_match_label()

    def generate_password(self):
        length = 15
        upper = string.ascii_uppercase
        lower = string.ascii_lowercase
        digits = string.digits
        symbols = "!@#$%^&*()-_=+[]{};:,.<>?"
        #make sure we have at least one of each type
        password_chars = []
        password_chars.append(secrets.choice(upper))
        password_chars.append(secrets.choice(lower))
        password_chars.append(secrets.choice(digits))
        password_chars.append(secrets.choice(symbols))

        all_chars = upper + lower + digits + symbols
        remaining = length - 4
        for i in range(remaining):
            password_chars.append(secrets.choice(all_chars))

        secrets.SystemRandom().shuffle(password_chars)
        password = "".join(password_chars)

        self.password.delete(0, tk.END)
        self.password.insert(0, password)
        self.confirm_password.delete(0, tk.END)
        self.confirm_password.insert(0, password)

        self.update_strength()
        self.update_match_label()
        ModernDialogue(self, "Generated", "Strong password generated and filled", "green")

    def save(self):
        svc = self.service.get().strip().lower()
        pwd = self.password.get()
        confirm = self.confirm_password.get()

        if not svc or not pwd:
            ModernDialogue(self, "Error", "Fields required", "red")
            return

        if not verify_password(confirm, hash_password(pwd)):
            ModernDialogue(self, "Error", "Passwords do not match", "red")
            return

        strengthcheck = password_strength(calculate_entropy(pwd))
        if strengthcheck != "Strong":
            ModernDialogue(self, "Error", "Password must be strong", "red")
            return

        key = open(KEY_FILE, "rb").read()
        vault = json.loads(decrypt_data(load_encrypted_data(VAULT_FILE), key))

        if svc in vault:
            ModernDialogue(self,
                "Duplicate",
                "A password for this service already exists.\nUse edit or delete instead.",
                "red"
            )
            return

        vault[svc] = pwd

        save_encrypted_data(
            encrypt_data(json.dumps(vault), key),
            VAULT_FILE
        )

        ModernDialogue(self, "Saved", "Stored", "green")
        self.clear()

    def clear(self):
        self.service.delete(0, tk.END)
        self.password.delete(0, tk.END)
        self.confirm_password.delete(0, tk.END)
        self.strength.config(text="Strength:", fg=FG_COLOUR)
        self.match_label.config(text="", fg=FG_COLOUR)
        self.save_btn.config(state=tk.DISABLED)
#This is a form to add a new service or password, which includes live strength checking and
#it makes sure that passwords match when entered. 
#Additionally there is a strong password generator, it can also reject weak or duplicate
#password entries before saving to the encrypted vault


class ViewPasswordsPage(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=BG_COLOUR)

        tk.Label(self, text="Vault Access",
                 font=TITLE_FONT, bg=BG_COLOUR, fg=FG_COLOUR).pack(pady=30)

        tk.Button(self, text="Unlock Vault",
                  command=self.ask_master,
                  bg=BTN_COLOUR, fg=FG_COLOUR).pack(pady=10)

        tk.Button(self, text="Back",
                  command=lambda: master.show_frame(HomePage),
                  bg=BTN_COLOUR, fg=FG_COLOUR).pack()

    def ask_master(self):
        win = tk.Toplevel(self)
        win.configure(bg=BG_COLOUR)
        win.geometry("300x160")

        tk.Label(win, text="Master Password",
                 bg=BG_COLOUR, fg=FG_COLOUR).pack(pady=10)

        e = tk.Entry(win, show="*", bg=ENTRY_BG, fg=FG_COLOUR,
                     insertbackground=FG_COLOUR)
        e.pack()

        def check():
            stored = open(MASTER_HASH_FILE, "rb").read()
            enteredpassword = e.get()
            passwordcorrect = verify_password(enteredpassword, stored)
            if passwordcorrect == True:
                win.destroy()
                self.open_vault()
            else:
                ModernDialogue(self, "Locked", "Wrong password", "orange")

        tk.Button(win, text="Unlock", command=check,
                  bg=BTN_COLOUR, fg=FG_COLOUR).pack(pady=10)

    def open_vault(self):
        key = open(KEY_FILE, "rb").read()
        vault = json.loads(decrypt_data(load_encrypted_data(VAULT_FILE), key))

        win = tk.Toplevel(self)
        win.geometry("500x400")
        win.configure(bg=BG_COLOUR)

        search = tk.StringVar()

        tk.Entry(win, textvariable=search,
                 bg=ENTRY_BG, fg=FG_COLOUR,
                 insertbackground=FG_COLOUR).pack()

        box = tk.Listbox(win, bg=ENTRY_BG, fg=FG_COLOUR)
        box.pack(fill="both", expand=True)

        def refresh(*_):
            box.delete(0, tk.END)
            term = search.get().lower()
            for s in vault:
                if s == "recovery_codes":
                    continue
                if term in s.lower():
                    box.insert(tk.END, s)

        search.trace_add("write", refresh)
        refresh()

        def reveal():
            sel = box.curselection()
            if not sel:
                return
            svc = box.get(sel[0])
            pwd = vault[svc]
            strength = password_strength(calculate_entropy(pwd))
            self.clipboard_clear()
            self.clipboard_append(pwd)
            ModernDialogue(
                self,
                svc,
                f"{pwd}\n\nStrength: {strength}\n\nCopied to clipboard", "green"
            )

        tk.Button(win, text="Reveal + Copy",
                  command=reveal,
                  bg=BTN_COLOUR, fg=FG_COLOUR).pack(pady=10)
#The viewpasswordspage has a simple job which is firstly to reauthenticate the master password
#before even opening the vault.
#It then shows a list of searchable services, and selecting one reveals it and copies the password
#to your clipboard automatically.

class AddRecoveryPage(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=BG_COLOUR)

        tk.Label(self,
                 text="Recovery Codes",
                 font=TITLE_FONT,
                 bg=BG_COLOUR,
                 fg=FG_COLOUR).pack(pady=20)

        container = tk.Frame(self, bg=BG_COLOUR)
        container.pack(expand=True)
        tk.Label(container, text="Service",
                 bg=BG_COLOUR, fg=FG_COLOUR).pack()

        self.service_entry = tk.Entry(container,
                                      bg=ENTRY_BG,
                                      fg=FG_COLOUR,
                                      insertbackground=FG_COLOUR,
                                      relief="flat",
                                      bd=5)
        self.service_entry.pack(pady=5)

        self.codes_frame = tk.Frame(container, bg=BG_COLOUR)
        self.codes_frame.pack(pady=10)

        self.code_entries = []
        self.add_code_field()

        tk.Button(container,
                  text="+ Add Another Code",
                  command=self.add_code_field,
                  bg=BTN_COLOUR,
                  fg=FG_COLOUR,
                  relief="flat",
                  bd=0,
                  padx=20,
                  pady=8,
                  cursor="hand2").pack(pady=5)

        tk.Button(container,
                  text="Save Codes",
                  command=self.save_codes,
                  bg=BTN_COLOUR,
                  fg=FG_COLOUR,
                  relief="flat",
                  bd=0,
                  padx=25,
                  pady=10,
                  cursor="hand2").pack(pady=10)

        tk.Button(container,
                  text="Back",
                  command=lambda: master.show_frame(RecoveryHubPage),
                  bg=BTN_COLOUR,
                  fg=FG_COLOUR,
                  relief="flat",
                  bd=0,
                  padx=25,
                  pady=10,
                  cursor="hand2").pack(pady=5)

    def add_code_field(self):
        entry = tk.Entry(self.codes_frame,
                         bg=ENTRY_BG,
                         fg=FG_COLOUR,
                         insertbackground=FG_COLOUR,
                         relief="flat",
                         bd=5)
        entry.pack(pady=3)
        self.code_entries.append(entry)

    def save_codes(self):
        service = self.service_entry.get().strip().lower()
        codes = [e.get().strip() for e in self.code_entries if e.get().strip()]

        if not service or not codes:
            ModernDialogue(self, "Error", "Service and at least one code required", "red")
            return

        key = open(KEY_FILE, "rb").read()
        vault = json.loads(decrypt_data(load_encrypted_data(VAULT_FILE), key))

        if "recovery_codes" not in vault:
            vault["recovery_codes"] = {}

        if service in vault["recovery_codes"]:
            ModernDialogue(self, "Duplicate", "Recovery codes already exist for this service", "orange")
            return

        vault["recovery_codes"][service] = {
            "codes": codes,
            "used": []
        }

        save_encrypted_data(
            encrypt_data(json.dumps(vault), key),
            VAULT_FILE
        )

        ModernDialogue(self, "Saved", "Recovery codes stored securely")
        self.clear()

    def clear(self):
        self.service_entry.delete(0, tk.END)
        for entry in self.code_entries:
            entry.destroy()
        self.code_entries.clear()
        self.add_code_field()
#The add recovery page stores backup and recovery codes for a given service in the vault.
#It supports multiple codes per service and blocks duplicates


class RecoveryHubPage(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=BG_COLOUR)

        tk.Label(self, text="Recovery Codes",
                 font=TITLE_FONT,
                 bg=BG_COLOUR,
                 fg=FG_COLOUR).pack(pady=40)

        self.btn("Add Recovery Codes", lambda: master.show_frame(AddRecoveryPage))
        self.btn("View Recovery Codes", lambda: master.show_frame(ViewRecoveryPage))
        self.btn("Back", lambda: master.show_frame(HomePage))

    def btn(self, text, cmd):
        tk.Button(self,
                  text=text,
                  command=cmd,
                  font=FONT,
                  bg=BTN_COLOUR,
                  fg=FG_COLOUR,
                  relief="flat",
                  bd=0,
                  padx=25,
                  pady=10,
                  cursor="hand2").pack(pady=10)

#Recoveryhubpage is purely for navigation it has no logic, and it presents the three buttons
#to addrecoverypage, viewrecoverypage and back to the HomePagethe btn() helper method keeps
#the button styling consistent without repeating code

class ViewRecoveryPage(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=BG_COLOUR)

        tk.Label(self, text="View Recovery Codes",
                 font=TITLE_FONT,
                 bg=BG_COLOUR,
                 fg=FG_COLOUR).pack(pady=20)

        self.service_list = tk.Listbox(self,
                                       bg=ENTRY_BG,
                                       fg=FG_COLOUR)
        self.service_list.pack(fill="both", expand=True, padx=20, pady=10)

        tk.Button(self,
                  text="Open Service",
                  command=self.open_service,
                  bg=BTN_COLOUR,
                  fg=FG_COLOUR,
                  relief="flat",
                  bd=0,
                  padx=20,
                  pady=8).pack(pady=5)

        tk.Button(self,
                  text="Back",
                  command=lambda: master.show_frame(RecoveryHubPage),
                  bg=BTN_COLOUR,
                  fg=FG_COLOUR,
                  relief="flat",
                  bd=0,
                  padx=20,
                  pady=8).pack(pady=5)

    def on_show(self):
        self.refresh()

    def refresh(self):
        self.service_list.delete(0, tk.END)

        key = open(KEY_FILE, "rb").read()
        vault = json.loads(decrypt_data(load_encrypted_data(VAULT_FILE), key))

        if "recovery_codes" in vault:
            for service in vault["recovery_codes"]:
                self.service_list.insert(tk.END, service)

    def open_service(self):
        selection = self.service_list.curselection()
        if not selection:
            return

        service = self.service_list.get(selection[0])

        key = open(KEY_FILE, "rb").read()
        vault = json.loads(decrypt_data(load_encrypted_data(VAULT_FILE), key))
        data = vault["recovery_codes"][service]

        #check if old format (just a list) or new format (dictionary with codes and used)
        if isinstance(data, list):
            codes = data
            used = []
            vault["recovery_codes"][service] = {
                "codes": codes,
                "used": used
            }
            save_encrypted_data(
                encrypt_data(json.dumps(vault), key),
                VAULT_FILE
            )
        else:
            codes = data["codes"]
            used = data["used"]

        win = tk.Toplevel(self)
        win.geometry("400x400")
        win.configure(bg=BG_COLOUR)

        tk.Label(win, text=service,
                 font=("Segoe UI", 14, "bold"),
                 bg=BG_COLOUR,
                 fg=ACCENT).pack(pady=10)

        box = tk.Listbox(win,
                         bg=ENTRY_BG,
                         fg=FG_COLOUR)
        box.pack(fill="both", expand=True, padx=20, pady=10)

        for code in codes:
            if code in used:
                box.insert(tk.END, f"{code}  (USED)")
            else:
                box.insert(tk.END, code)

        def mark_used():
            sel = box.curselection()
            if not sel:
                return

            selected = box.get(sel[0]).replace("  (USED)", "")

            if selected not in used:
                used.append(selected)

                save_encrypted_data(
                    encrypt_data(json.dumps(vault), key),
                    VAULT_FILE
                )

                box.delete(sel[0])
                box.insert(sel[0], f"{selected}  (USED)")

        tk.Button(win,
                  text="Mark as Used",
                  command=mark_used,
                  bg=BTN_COLOUR,
                  fg=FG_COLOUR,
                  relief="flat",
                  bd=0,
                  padx=20,
                  pady=8).pack(pady=5)
#The viewrecoverypage lists the services with stored recovery codes, it opens a detail window
#which shows each codes used or unused status, with a mark as used button that
#persist the change to the vault.
