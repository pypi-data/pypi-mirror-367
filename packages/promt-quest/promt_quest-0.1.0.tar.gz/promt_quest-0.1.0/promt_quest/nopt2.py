from time import sleep
from functions import clear_terminal
from functions import choices as options
from nnopt1 import win
from nnopt2 import lose
def battle():
    clear_terminal()
    print("KNIGHT.GPT:")
    sleep(0.5)
    print("'You dare touch my source code?! Initiating countermeasures.'")
    sleep(1)
    print("")
    print("⚡ Terminal glitches violently. The screen flickers. You hear digital growls.")
    print("")
    sleep(1)
    print("[BATTLE MODE ACTIVATED]")
    sleep(1)
    print("ASCII laser beams fire from the console.")
    sleep(1)
    print("Recursive error messages swirl like missiles.")
    print("")
    sleep(1.5)
    print("You furiously type recursive logic, patches, and debugging commands.")
    print("")
    sleep(1)
    print("KNIGHT.GPT retaliates by injecting syntax errors and launching infinite loops.")
    print("")
    sleep(1)
    print("Your fingers race against the clock. Your only hope: out-code the AI’s defenses.")
    print("")
    sleep(1)
    print("Choose your hacking tactic:")
    print("")
    print("1. Flood with endless bug fixes → (Risk: Overload your system)")
    print("")
    print("2. Attempt a graceful shutdown → (Risk: AI triggers emergency protocols)")
    print("")
    print("The outcome depends on your choice — and your coding skill.")
    sleep(1)
    choice = options(2)
    if choice == 1:
        win()
    if choice == 2:
        lose()