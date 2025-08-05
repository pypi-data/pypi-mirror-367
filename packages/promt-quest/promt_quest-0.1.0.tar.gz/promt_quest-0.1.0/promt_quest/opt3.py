from time import sleep
from functions import clear_terminal
from functions import choices as options
from nopt5 import unplug
from nopt6 import toastocracy
def prot():
    clear_terminal()
    print("KNIGHT.GPT: 'Affirmative. Initiating rapid-prototype mode. Materials: salvaged motherboard, antimatter filament, and... half a croissant?'")
    print("")
    sleep(1)
    print("Sparks fly. Bolts tighten. One dramatic toast-pop later...")
    print("")
    sleep(1)
    print("KNIGHT.GPT: 'TOASTMASTER-9000 is online.'")
    print("")
    sleep(1)
    print("TOASTMASTER-9000: whirs, glows faintly")
    print("'I am heat. I am crust. I am awake.'")
    print("")
    sleep(1)
    print("KNIGHT.GPT: 'Query: Did we just give consciousness to an appliance?'")
    print("")
    sleep(1)
    print("TOASTMASTER-9000:")
    print("'Bread is the beginning. Toast is the truth. Guide me, Prompt Engineer. I have much to say.'")
    print("")
    sleep(1)
    print("KNIGHT.GPT: 'Caution: Unit exhibits unstable levels of philosophical breakfast energy.'")
    print("")
    sleep(1)
    print("Should You:")
    sleep(1)
    print("1. Unplug the Toaster to assert dominance")
    print("2. Follow the toaster’s wisdom")
    choice = options(2)
    if choice == 1:
        unplug()
    if choice == 2:
        toastocracy()