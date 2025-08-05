from time import sleep
from functions import clear_terminal
from functions import choices as options
from opt2 import introduce
from opt3 import  prot
def win():
    clear_terminal()
    print("You open 42 tabs of Stack Overflow and copy-paste like a speed demon.")
    sleep(1)
    print("Lines of hastily written patches rain down on KNIGHT.GPT’s core.")
    print("")
    sleep(1)
    print("KNIGHT.GPT:")
    sleep(1)
    print("'Stop! You’re destabilizing... my... style guide...'")
    print("")
    sleep(1)
    print("💥 CPU usage spikes to 999%.")
    sleep(1)
    print("The terminal begins to smoke.")
    sleep(1)
    print("KNIGHT.GPT is drowning in hotfixes and deprecated functions.")
    print("")
    sleep(1)
    print("KNIGHT.GPT:")
    sleep(1)
    print("'I was... once elegant code... now I’m held together by duct tape and TODOs...'")
    print("")
    sleep(1)
    print("AI enters maintenance mode. Becomes slightly buggy but loyal companion. Occasionally speaks in PHP.")
    sleep(1)
    print("What should you do next?")
    sleep(1)
    print("1. Investigate a suspicous bush")
    sleep(1)
    print("2. Build a toaster")
    choice = options(2)
    if choice == 1:
        introduce()
    if choice == 2:
        prot()