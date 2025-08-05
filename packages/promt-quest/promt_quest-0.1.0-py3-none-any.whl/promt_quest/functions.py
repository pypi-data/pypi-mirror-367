import os
from time import sleep
def clear_terminal():
    # Check the operating system and execute the appropriate clear command
    if os.name == 'nt':  # For Windows
        _ = os.system('cls')
    else:  # For Mac and Linux (POSIX systems)
        _ = os.system('clear')

def choices(num):
    choice = None
    if num == 3:
        while choice not in [1, 2, 3]:
            sleep(1)
            try:
                print("enter a number between 1-3")
                choice = int(input("What's your choice, brave adventurer? (1–3): "))
            except ValueError:
                print("Please do not enter a number with a decimal point")
    elif num == 2:
        while choice not in [1, 2]:
            sleep(1)
            try:
                print("enter a number between 1-2")
                choice = int(input("What's your choice, brave adventurer? (1–2): "))
            except ValueError:
                print("Please do not enter a number with a decimal point")
    return choice

def theEnd():
    sleep(3)
    print("")
    print("")
    print("")
    print(r"_________          _______    _______  _        ______  ")
    print(r"\__   __/|\     /|(  ____ \  (  ____ \( (    /|(  __  \ ")
    print(r"   ) (   | )   ( || (    \/  | (    \/|  \  ( || (  \  )")
    print(r"   | |   | (___) || (__      | (__    |   \ | || |   ) |")
    print(r"   | |   |  ___  ||  __)     |  __)   | (\ \) || |   | |")
    print(r"   | |   | (   ) || (        | (      | | \   || |   ) |")
    print(r"   | |   | )   ( || (____/\  | (____/\| )  \  || (__/  )")
    print(r"   )_(   |/     \|(_______/  (_______/|/    )_)(______/ ")