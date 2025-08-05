from time import sleep
from functions import clear_terminal
from functions import choices as options
from nopt3 import friend
from nopt4 import haluctination
def introduce():
    clear_terminal()
    print("Scanning for nearest lifeform...")
    sleep(1)
    print("")
    print("✅ Target acquired: 3 meters away.  ")
    sleep(1)
    print("**Species:** Unknown.  ")
    sleep(0.5)
    print("**Shape:** Shrublike.  ")
    sleep(0.5)
    print("**Hostile?** Unknown, but... leafy.")
    sleep(1)
    print("")
    print("Approaching...")
    sleep(1)
    print("")
    print("🌿 'HALT, FLESHLING!'  ")
    sleep(0.5)
    print("The shrub suddenly sprouts a tiny speaker and a glowing red berry. It seems... **sentient**.")
    print("")
    sleep(0.5)
    print("KNIGHT.GPT: Uh... this bush is talking. I think it may be intelligent. Or haunted. Or both.")
    print("")
    sleep(0.5)
    print("🌿 SHRUBBERY.EXE: 'You dare sneak up on me, the Elder Root of Sector 9?! Speak now, or be composted.'")
    print("")
    sleep(1)
    print("What will you do?")
    print("")
    sleep(1)
    print("1. Apologize for startling it  ")
    print("2. Eat one of its berries")
    choice = options(2)
    if choice == 1:
        friend()
    if choice == 2:
        haluctination()