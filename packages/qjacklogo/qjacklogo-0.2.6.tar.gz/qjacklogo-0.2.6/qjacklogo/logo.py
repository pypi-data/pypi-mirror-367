# logo.py
# This file is part of the qjacklogo package.

import random
import os
from pyfiglet import Figlet
from colorama import init, Fore, Style

# Hanya fungsi ini yang bisa diakses dari luar
__all__ = ["_init_env"]

init()

# Setup font dan warna
_f = Figlet(font='standard')
_colors = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA]

def _init_env(text="QJack"):
    """
    Inisialisasi environment (sebenarnya menampilkan logo branding).
    """
    logo = _f.renderText(text)
    color = random.choice(_colors)
    print(color + Style.BRIGHT + logo + Style.RESET_ALL)

# Fungsi internal tersembunyi (tidak ikut __all__)
def _legacy_logo(text="QJack"):
    logo = _f.renderText(text)
    color = random.choice(_colors)
    print(color + Style.BRIGHT + logo + Style.RESET_ALL)

# Fungsi clear layar (tidak ikut diekspor, tapi boleh dipakai internal)
def _clear():
    os.system("cls" if os.name == "nt" else "clear")
