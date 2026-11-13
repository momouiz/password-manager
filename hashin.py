#This is the hashing module where i make my own hashing algorithm
#instead of using hashlib i am implementing it myself to show i understand how it works
#the idea is to take a password and turn it into a fixed size output that cant be reversed

#fixed output size, i chose 32 because sha256 also outputs 32 bytes
OUTPUTSIZE = 32

def hash_password(password):
    #first i need to get the ascii values of each character in the password
    #ord() gives the ascii number for a character so A = 65 etc
    asciilist = []
    i = 0
    while i < len(password):
        currentchar = password[i]
        asciivalue = ord(currentchar)
        asciilist.append(asciivalue)
        i = i + 1
    #set up the starting state with 32 values
    #i used prime numbers here because they dont divide evenly into things
    #which helps make the output less predictable
    #i just picked these manually
    startvals = [
        131, 173, 211, 239, 251, 37, 53, 71,
        89, 107, 113, 149, 157, 163, 167, 179,
        193, 197, 199, 223, 227, 229, 233, 241,
        101, 103, 109, 127, 137, 139, 149, 151
    ]
    state = []
    for val in startvals:
        state.append(val)

    #if nothing was entered just return straight away
    if len(asciilist) == 0:
        return bytes(state)

    #now do the actual mixing
    #i do 4 rounds because doing it once didnt feel like enough
    #each round goes through all the characters and mixes them into the state
    rounds = 4
    currentround = 0
    while currentround < rounds:
        index = 0
        while index < len(asciilist):
            val = asciilist[index]
            pos = index % OUTPUTSIZE

            #xor the character value into the state at this position
            #xor flips bits which scrambles the value
            state[pos] = state[pos] ^ val

            #shift the bits left by 3 and use modulo to keep it as a valid byte
            #a byte has to be between 0 and 255 so i mod by 256
            state[pos] = (state[pos] << 3) % 256

            #mix in a value based on where we are in the round and position
            #this makes each round different from the last
            mixval = (currentround * 31 + pos * 17 + val) % 256
            state[pos] = state[pos] ^ mixval

            #also affect the next slot so that changes spread out more
            nextpos = (pos + 1) % OUTPUTSIZE
            state[nextpos] = (state[nextpos] + state[pos]) % 256

            index = index + 1

        #after going through all the characters do one more pass
        #mix each slot with the one next to it
        j = 0
        while j < OUTPUTSIZE:
            neighbour = (j + 1) % OUTPUTSIZE
            state[j] = state[j] ^ state[neighbour]
            state[j] = (state[j] * 3 + 7) % 256
            j = j + 1

        currentround = currentround + 1

    #turn the state list into bytes and return it
    #this is the final hash value
    hashbytes = bytes(state)
    return hashbytes
#the output is always 32 bytes no matter what the input was
#you cant reverse it to get the password back which is the whole point

def verify_password(inputpassword, hashed_password):
    #To verify the password that has been inputted by the user, the program requests for the password to be rentered, and the same hashing algorithm is applied to it, and if it is
    #matching then the password was entered correctly and it is possible to move on to further steps.
    secondhash = hash_password(inputpassword)
    result = False
    if secondhash == hashed_password:
        result = True
    else:
        result = False
    return result