import random
import os
from pyfiglet import Figlet
from colorama import init, Fore, Style

init()

# Setup font dan warna
f = Figlet(font='standard')
colors = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA]

def clear():  # Opsional: bersihkan layar (kalau kamu mau pakai)
    os.system("cls" if os.name == "nt" else "clear")

def aku_tai(text="QJack"):
    """
    Menampilkan logo satu kali saja, warna acak, tidak mengganggu eksekusi program lain.
    """
    logo = f.renderText(text)
    color = random.choice(colors)
    print(color + Style.BRIGHT + logo + Style.RESET_ALL)
