#module loaded
#analyses the password strength using entropy
#returning strength score and feedback
import math

def calculate_entropy(password):
    length = len(password)
    number = 0
    lowercase = False
    uppercase = False
    hasdigit = False
    symbol = False
    for character in password:
        if lowercase == False:
            isitlowercase = character.islower() 
            if isitlowercase == True:
                number = number + 26
                lowercase = True
        if uppercase == False:
            isituppercase = character.isupper()
            if isituppercase == True:
                number = number + 26
                uppercase = True
        if hasdigit == False:
            isitadigit = character.isdigit()
            if isitadigit == True:
                number = number + 10
                hasdigit = True
        if symbol == False:
            isitasymbol = character.isalnum()
            if isitasymbol == False:
                number = number + 32
                symbol = True
    #I also validate input because if the password entered is empty
    #then I prevent the code from breaking down
    if number == 0:
        return 0
    else:
        entropy = length * math.log2(number)
        return entropy

#This is an algorithm to check what characters are in the password
            
#N is the size of the character set used, where L is the length
# of the password    

#Password entropy is used by using standard logarithms based on the 
#length of the password and the character set size
#this allows for an estimation of password unpredictability while
#remaining computationally efficient
def password_strength(entropy):
    #this converts the numeric entropy value into a human 
    #readable strength rating so users can understand how 
    #secure their password is
    #entropy is very precise and mathematical meaning it snot
    #user friendly
    strength = ""
    if entropy < 40:
        strength = "Weak"
    elif entropy < 60 and entropy > 40:
        strength = "Medium"
    elif entropy > 60:
        strength = "Strong"
    return strength
