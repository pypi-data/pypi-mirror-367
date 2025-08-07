# === src/utils.py ===
from pyfiglet import figlet_format
from termcolor import colored

def stylish_heading(title="Lawyer-Bot"):
    banner = figlet_format(title, font="starwars", width=1000)
    print(colored(banner, "green"))
