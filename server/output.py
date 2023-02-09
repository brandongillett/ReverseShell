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
    echo('\n','WHITE')

def echo(input,color):
    if color == 'RED':
        print(Fore.RED + input, end = '')
    if color == 'GREEN':
        print(Fore.GREEN + input, end = '')
    if color == 'BLUE':
        print(Fore.BLUE + input, end = '')
    if color == 'MAGENTA':
        print(Fore.MAGENTA + input, end = '')
    if color == 'WHITE':
        print(Fore.WHITE + input, end = '')
