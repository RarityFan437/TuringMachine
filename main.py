"""
Главный скрипт.
"""
import json
import os
import importlib

from lib.colorama import Fore, init
import src.parser
import src.functions




CACHE_PATH = 'cache'
cache = {}

init(autoreset=True)

try:
    with open("cache\\cache.json", "r", encoding="utf-8") as file:
        cache = json.load(file)
except FileNotFoundError:
    cache = {'choosen_machine' : 'None'}


def run(tape):
    """
    Запускает Парсинг кода, а потом запускает машину.
    """
    importlib.reload(src.functions)
    importlib.reload(src.parser)
    if cache['choosen_machine'] == 'None':
        print(Fore.YELLOW + "No machine selected. Use 'choose' command first.")
        return
    try:
        src.parser.Parse(cache['choosen_machine'])
        src.functions.Tape.tape = 'x' + tape + 'x'
        src.functions.Tape.run()
    except Exception as e:
            print(Fore.RED + f"{e}")
        

def save():
    """
    Сохраняет кэш в файл.
    """
    
    if not os.path.exists(CACHE_PATH):
        os.makedirs(CACHE_PATH, exist_ok=True)
    with open('cache\\cache.json', 'w+', encoding="UTF-8") as f:
        json.dump(cache, f, indent=4)

def start():
    """
    Стартует кастомную консоль.
    """
    while True:
        command_raw = input(">> ")
        commands = command_raw.split(" ")
        match commands[0]:
            case "quit":
                break
            
            case "info":
                print(f"Choosen machine: {cache['choosen_machine']}")
            
            case "choose":
                if len(commands) == 2:
                    cache['choosen_machine'] = commands[1]
                    save()
                    print(Fore.GREEN + f'Succesful! You are choose your machine: {cache['choosen_machine']}')
                else:
                    print(Fore.RED + "Incorrect command usage")
            
            case "run":
                if len(commands) == 2:
                    run(commands[1])
                else:
                    print(Fore.RED + "Incorrect command usage")
            
            case "help":
                print("quit - exit the program\ninfo - shows choosen machine\nchoose [file name] - choosing your machine\nrun [tape] - running machine with entered tape\nclear - clear console")
            
            case "clear":
                os.system('cls' if os.name == 'nt' else 'clear')
            
            case _:
                print(Fore.RED + "Unknown Command. type 'help' for list of commands")

start()
