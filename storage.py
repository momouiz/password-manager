#This is the storage module, where the generation, encryption, decryption and saving/retrieval of saved passwords is done.
#i am writing my own encryption instead of using the fernet library
#the way it works is using XOR which is a bitwise operation
#if you XOR something with a key, you can XOR it again with the same key to get the original back
#so the same code works for both encrypting and decrypting which is convenient

import os
import secrets

KEY_FILE = "key.key"
KEYLENGTH = 64

def generate_key():
    #The generated keys must be random and unpredictable
    #in this function, it is checked if key already exists, and if it does not then a key is created and stored
    if not os.path.exists(KEY_FILE):
        #secrets.token_bytes gives properly random bytes using the os random generator
        #i used this instead of random because random isnt actually that unpredictable
        newkey = secrets.token_bytes(KEYLENGTH)
        keyfile = open(KEY_FILE, "wb")
        keyfile.write(newkey)
        keyfile.close()
        key = newkey
    else:
        keyfile = open(KEY_FILE, "rb")
        key = keyfile.read()
        keyfile.close()
    return key
#This is more secure than hardcoding a key myself in the program.

def encrypt_data(data, key):
    #convert the string to bytes first because you cant XOR a string directly
    databytes = data.encode()

    #the key needs to be the same length as the data
    #if the data is longer than the key i just repeat the key
    #i do this by going through each position and picking the key byte at position mod keylength
    keyrepeated = []
    pos = 0
    while pos < len(databytes):
        whichkeybyte = pos % len(key)
        keyrepeated.append(key[whichkeybyte])
        pos = pos + 1

    #now XOR each byte of the data with the corresponding byte from the key
    #this scrambles the data
    output = []
    pos = 0
    while pos < len(databytes):
        newbyte = databytes[pos] ^ keyrepeated[pos]
        output.append(newbyte)
        pos = pos + 1

    encrypteddata = bytes(output)
    return encrypteddata
#Here I handle the encryption, the encrption key is the master key and without this the file is useless.
#This uses XOR which is a bitwise operation, XORing with the same key twice always gives back the original value

def decrypt_data(encrypted_data, key):
    #decryption is literally the same thing as encryption with XOR
    #XOR is its own inverse so you just do the same steps again with the same key

    #rebuild the repeated key the same way
    keyrepeated = []
    pos = 0
    while pos < len(encrypted_data):
        whichkeybyte = pos % len(key)
        keyrepeated.append(key[whichkeybyte])
        pos = pos + 1

    #XOR each byte with the key to get back the original
    output = []
    pos = 0
    while pos < len(encrypted_data):
        originalbyte = encrypted_data[pos] ^ keyrepeated[pos]
        output.append(originalbyte)
        pos = pos + 1

    #convert back to string
    decryptedstring = bytes(output).decode()
    return decryptedstring
#Encryption and decryption work by encoding the data into bits and bytes first
#This 

def save_encrypted_data(encrypted_data, filename):
    with open(filename, "wb") as f:
        f.write(encrypted_data)
#Here there is the file where passwords are written to, and read from to retrieve them and display them to the user

def load_encrypted_data(filename):
    with open(filename, "rb") as f:
        return f.read()