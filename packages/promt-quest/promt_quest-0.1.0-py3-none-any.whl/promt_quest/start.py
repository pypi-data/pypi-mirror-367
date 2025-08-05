from time import sleep
from opt1 import scan
from opt2 import introduce
from opt3 import prot
from functions import choices as options
print("SYSTEM STATUS: BOOT COMPLETE.")
print("Welcome, Prompt Engineer #404.")
sleep(1)
print("")
print("Your AI assistant, Codename: KNIGHT.GPT, is waking up after 1000 years of standby.")
sleep(1)
print("")
print("ERROR: All mission parameters corrupted.")
print("Your task: Guide it through a broken world using only prompts.")
sleep(1)
print("")
print("⚠️ WARNING: The AI interprets prompts... creatively.")
sleep(1)
print("")
print("You have 3 choices")
sleep(1)
print("")
print("1. wake up and scan for threats")
sleep(1)
print("2. introduce yourself to the nearest lifeform")
sleep(1)
print("3. build sentient toaster first, THEN assess situation")
choice = options(3)
if choice == 1:
    scan()
if choice == 2:
    introduce()
if choice == 3:
    prot()