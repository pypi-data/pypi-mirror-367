import os
import time
import threading
from pyfiglet import Figlet
from colorama import init, Fore, Style

init()

f = Figlet(font='standard')
colors = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA]

arabic_text = "Lā ḥawla wa lā quwwata illā billāh✨"

def print_logo(text, color):
    logo = f.renderText(text)
    print(f"\033[1;0H", end="")
    print(color + Style.BRIGHT + logo + Style.RESET_ALL, end="")
    print("\n" * 2)  # Tambah baris agar area bawah ikut dibersihkan


def arabic_typing_effect(text, start_row):
    while True:
        typed = ""
        for char in text:
            typed += char
            # Pindah cursor ke baris start_row, kolom 0
            print(f"\033[{start_row};0H" + Fore.CYAN + Style.BRIGHT + typed + " " * 10 + Style.RESET_ALL, end="", flush=True)
            time.sleep(0.25)
        time.sleep(1)
        # Bersihkan baris tulisan arab setelah selesai mengetik
        print(f"\033[{start_row};0H" + " " * (len(text) + 10), end="", flush=True)

def rainbow_logo_loop(text):
    i = 0
    while True:
        color = colors[i % len(colors)]
        print_logo(text, color)
        i += 1
        time.sleep(0.25)

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def start_animations():
    clear()

    # Sembunyikan kursor
    print("\033[?25l", end="")

    try:
        logo_text = "QJack"
        logo_lines = f.renderText(logo_text).splitlines()
        logo_height = len(logo_lines)

        print_logo(logo_text, colors[0])

        arabic_row = logo_height + 1

        t_logo = threading.Thread(target=rainbow_logo_loop, args=(logo_text,), daemon=True)
        t_logo.start()

        arabic_typing_effect(arabic_text, arabic_row)

    except KeyboardInterrupt:
        pass
    finally:
        # Tampilkan kembali kursor setelah keluar
        print("\033[?25h", end="")
        # Pindahkan kursor ke bawah agar tidak ganggu tampilan
        print(f"\033[{arabic_row + 2};0H", end="", flush=True)

if __name__ == "__main__":
    start_animations()
