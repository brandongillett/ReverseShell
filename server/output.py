import colorama
from colorama import Fore

def banner():
    LOGO = """
 ______    _______  __   __  _______  ___      ___
|    _ |  |       ||  | |  ||       ||   |    |   |
|   | ||  |  _____||  |_|  ||    ___||   |    |   |
|   |_||_ | |_____ |       ||   |___ |   |    |   |
|    __  ||_____  ||       ||    ___||   |___ |   |___ 
|   |  | | _____| ||   _   ||   |___ |       ||       |
|___|  |_||_______||__| |__||_______||_______||_______|
    """
    echo(LOGO,'MAGENTA')

def echo(input,color,type="",newline=""):
    COLORS = {
        'RED': Fore.RED,
        'GREEN': Fore.GREEN,
        'BLUE': Fore.BLUE,
        'MAGENTA': Fore.MAGENTA,
        'WHITE': Fore.WHITE
    }

    TYPES = {
        'WARNING': Fore.RED +'[!]',
        'SUCCESS': Fore.GREEN +'[✓]',
        'ADDED': Fore.GREEN +'[+]',
        'EXIT': Fore.RED + '[X]'
    }
    text = COLORS.get(color, Fore.RESET) + input
    type_prefix = TYPES.get(type, '')

    text = f"{Fore.RESET}{type_prefix} {text}" if type_prefix else text

    if newline == "FIRST":
        text = '\n' + text
    elif newline == "LAST":
        text = text + '\n'
    else:
        text = '\n' + text + '\n'

    print(text)