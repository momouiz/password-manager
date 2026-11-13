# Password Manager

A desktop password manager I made in Python with Tkinter. It started as my A-level NEA project.

**This is a learning project. It is not production-grade crypto, so please don't use it to store your real passwords.** I wrote my own hash function and XOR encryption so I could understand how they work, not because they're safe. A real app should use tested libraries like `hashlib`/`argon2` and AES (for example `cryptography`'s Fernet).

## What it does

- Asks you to set a master password the first time you run it. Only a hash of it is saved, never the password itself.
- Uses my own hash function (`hashin.py`). It mixes the password into a 32-byte state over 4 rounds with XOR, bit shifts and modulo.
- Encrypts the vault with XOR using a random 64-byte key (`storage.py`).
- Checks password strength with entropy (`passwordstrength.py`): length × log2(size of the character set) gives Weak / Medium / Strong.
- Generates strong passwords with the `secrets` module (not `random`, because `random` is predictable).
- Locks you out for 30 seconds after 3 wrong master password attempts.
- Stores backup / recovery codes for your accounts inside the encrypted vault.

## Why I built it

I wanted to understand what actually happens when a website "hashes" your password, and why people say never to roll your own crypto. Building it myself and then finding the weaknesses taught me a lot more than just calling a library.

## How to run it

You need Python 3. No extra packages are needed because everything is in the standard library.

```
python main.py
```

The first run creates `master.hash`, `key.key` and `vault.dat` in the same folder. These are in `.gitignore` so they never get uploaded.

## Example

```
First run  -> "Create master password"  -> vault created
Add password -> service: example-site, password: (generated) -> Strength: Strong
Wrong master password x3 -> "Locked 30 seconds"
```

## What I learned / known weaknesses

- **Repeating-key XOR is weak.** If someone knows part of the plaintext (and the vault is JSON, so they do), they can work out the key.
- **The key is stored next to the vault.** Anyone who copies the folder can decrypt it. A real app would derive the key from the master password (PBKDF2 / scrypt / argon2).
- **My hash has no salt and is fast**, so it would be easy to brute force. Real password hashes are slow on purpose.
- The lockout only lasts while the app is open, so restarting it resets the counter.
- How entropy works, and why length matters more than adding one symbol.
- Splitting the code into modules (UI, storage, hashing, strength) made it much easier to test each part.

TODO: derive the key from the master password instead of saving it in a file.
