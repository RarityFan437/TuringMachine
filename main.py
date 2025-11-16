from parser import Parse
from functions import Tape
import sys
import json
import argparse

try:
    with open("cache.json", "r", encoding="utf-8") as file:
        cache = json.load(file)
except:
    cache = {'choosen_machine' : '',
             'choosen_tape' : ''}

parser = argparse.ArgumentParser()
parser.add_argument("--tape")
parser.add_argument("command")

def run(tape):
    r = Parse(cache['choosen_machine'])
    if r != None:
        print(r)
    else:
        Tape.tape = 'x' + tape + 'x'
        Tape.run()

args = parser.parse_args()

match args.command:
    case 'choose':
        cache['choosen_machine'] = input('Enter file name: ')
        with open('cache.json', 'w+') as f:
            json.dump(cache, f, indent=4)
        print(f'Succesful! You are choose your machine: {cache['choosen_machine']}')
    case 'load':
        cache['choosen_tape'] = input('Enter file name: ')
        with open('cache.json', 'w+') as f:
            json.dump(cache, f, indent=4)
        print(f'Succesful! You are choose tape: {cache['choosen_tape']}')
    case 'run':
        if args.tape:
            run(args.tape)
        elif cache.get('choosen_tape'):
            with open(cache.get('choosen_tape'), 'r') as f:
                tape = f.read().rstrip()
            run(tape)
        else:
            'No tape!'
    case _:
        'Unknown command!'