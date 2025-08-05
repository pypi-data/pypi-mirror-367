from time import sleep
from functions import clear_terminal
from functions import choices as options
from nopt1 import joke
from nopt2 import battle
def scan():
    clear_terminal()
    print("KNIGHT.GPT: ⚠️ ALERT! Threat detected: User identified as “Primary Source of System Instability.”")
    sleep(1)
    print("")
    print("Analyzing...")
    sleep(1)
    print("- High caffeine consumption ✔️  ")
    sleep(1)
    print("- Excessive keyboard mashing ✔️")  
    sleep(1)
    print("- Frequent use of vague commands like “do stuff” ❌ (yet suspicious)")
    sleep(1)
    print("")
    print("Recommendation: Proceed with extreme caution.  ")
    sleep(0.75)
    print("Initiating defensive protocol: Deploying virtual glitter bombs! ✨🎉")
    sleep(1)
    print("")
    print("User status: *Questionable*  ")
    sleep(1)
    print("")
    print("Shall You  ")
    sleep(1)
    print("1. Calm the AI down with a joke?  ")
    sleep(1)
    print("2. Attempt to reprogram the Ai.  ")
    choice = options(2)
    if choice == 1:
        joke()
    if choice == 2:
        battle()