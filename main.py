from src.parser import Parse
from src.functions import Tape
import os
import json
from lib.colorama import Fore, init

CACHE_PATH = 'cache'

init(autoreset=True)

try:
    with open("cache\\cache.json", "r", encoding="utf-8") as file:
        cache = json.load(file)
except:
    cache = {'choosen_machine' : 'None'}

def run(tape):
    if cache['choosen_machine'] == 'None':
        print(Fore.YELLOW + "No machine selected. Use 'choose' command first.")
        return
    try:
        r = Parse(cache['choosen_machine'])
        if r != None:
            print(r)
        else:
            Tape.tape = 'x' + tape + 'x'
            Tape.run()
    except Exception as e:
            print(Fore.RED + f"{e}")
        

def save():
    global cache
    if not os.path.exists(CACHE_PATH):
        os.makedirs(CACHE_PATH, exist_ok=True)
    with open('cache\\cache.json', 'w+') as f:
        json.dump(cache, f, indent=4)

def start():
    global cache
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