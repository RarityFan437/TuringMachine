import time
import sys
import config
from enum import Enum
import os
import random

# Сдвиги
class Shift(Enum):
    LEFT = '<'
    RIGHT = '>'
    STAY = '~'

# Функция к которой перейти, функция которую пометить
class Jump:
    def __init__(self, function: 'Function', marking: 'Function'=None):
        self.function = function
        self.marking = marking

# Триплет, который выполняет машина
class Instruction:
    def __init__(self, value: str, jump: 'Jump', shift: 'Shift'):
        self.value = value
        self.jump = jump
        self.shift = shift
    
    def get_value(self):
        match self.value:
            case '?':
                return random.choice(["0", "1", "x"])
            case '!':
                return Tape.tape[Tape.current_function.mark]
            case _:
                return self.value
    
    def __call__(self):
        # Для начала присваиваем значение текущей ячейке
        Tape.set_char(self.get_value())

        # Переходим к другой функции и маркируем ячейку
        match self.jump.function:
            case '#':
                Tape.run_flag = False
            case '§':
                Tape.printer()
            case _:
                if Function.get_function_by_name(self.jump.function) is None:
                    raise NameError(f"Unknown function reference '{self.jump.function}' in function '{Tape.current_function}'")
                Tape.current_function = Function.get_function_by_name(self.jump.function)
                if not self.jump.marking is None:
                    Function.get_function_by_name(self.jump.marking).mark = Tape.cursor

        # Сдвигаемся по ленте
        Tape.shift(self.shift)

# Список инструкций функции
class InstructionSet:
    def __init__(self, zero: 'Instruction', one: 'Instruction', x: 'Instruction'):
        self.zero = zero
        self.one = one
        self.x = x

# Функция АКА правила по которым работает машина
class Function:
    functions = []
    bases = '#§'
    def __init__(self, index: str, default: 'InstructionSet', marked: 'InstructionSet'=None):
        self.index = index
        self.default = default
        if marked != None:
            self.marked = marked
        else:
            self.marked = default
        self.mark = 0

        Function.functions.append(self)
    
    # Возвращает функцию по имени, если такое нет возвращает
    def get_function_by_name(index):
        for func in Function.functions:
            if func.index == index:
                    return func
        return None

    # увеличить значение марок всех функций на 1
    def increment_marks():
        for func in Function.functions:
            func.mark += 1

    def __call__(self, char):
        match self.index:
            case '#':
                Tape.run_flag = False
            case '§':
                Tape.printer()
            case _:
                match char:
                    case '0':
                        if self.mark == Tape.cursor:
                            self.marked.zero()
                        else:
                            self.default.zero()
                    case '1':
                        if self.mark == Tape.cursor:
                            self.marked.one()
                        else:
                            self.default.one()
                    case 'x':
                        if self.mark == Tape.cursor:
                            self.marked.x()
                        else:
                            self.default.x()

class Tape:
    current_function = None
    cursor = 1
    tape = ''
    pause_time = config.pause_time
    run_flag = True
    char_table = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*=+-_?/;:.,<>~ '
    width = min(os.get_terminal_size().columns - 5, config.fov)

    start = 0
    end = width
    cursor_pos = 1

    def reset():
        Tape.current_function = None
        Tape.cursor = 1
        Tape.tape = ''
        Tape.pause_time = config.pause_time
        Tape.run_flag = True
        Tape.char_table = ' 0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*=+-_?/;:.,<>~'
        Tape.width = 60

        Tape.start = 0
        Tape.end = Tape.width
        Tape.cursor_pos = 1

    def get_char():
        return Tape.tape[Tape.cursor]

    def set_char(value):
        Tape.tape= Tape.tape[:(Tape.cursor)] + value + Tape.tape[(Tape.cursor+1):]
        return 
    
    def shift(value):
        match value:
            case Shift.STAY:
                return
            case Shift.LEFT:
                Tape.cursor -= 1
                if Tape.cursor == 0:
                    Tape.tape = 'x' + Tape.tape
                    Tape.cursor = 1
                    Tape.start = 0
                    Tape.end = Tape.width
                    Function.increment_marks()
                return
            case Shift.RIGHT:
                Tape.cursor += 1
                if Tape.cursor == len(Tape.tape)-1:
                    Tape.tape = Tape.tape + 'x'
                    Tape.start = len(Tape.tape) - Tape.width
                    Tape.end = len(Tape.tape)
                return
    
    def run():
        Tape.print_tape()
        try:
            while Tape.run_flag:
                time.sleep(Tape.pause_time/2)
                Tape.current_function(Tape.tape[Tape.cursor])
                Tape.print_tape()
                time.sleep(Tape.pause_time/2)
            print(Tape.tape.strip('x'))
            Tape.reset()
        except KeyboardInterrupt:  
            print(Tape.tape.strip('x'))
            Tape.reset()
    
    def print_tape():
        Tape.cursor_pos = Tape.cursor - Tape.start
        if Tape.cursor_pos == 1 and Tape.cursor != 1:
            Tape.start = max(0, Tape.start - 1)
            Tape.end = min(len(Tape.tape)-1, Tape.end - 1)
        if Tape.cursor_pos == Tape.width - 2 and Tape.cursor != len(Tape.tape) - 1:
            Tape.start = max(0, Tape.start + 1)
            Tape.end = min(len(Tape.tape)-1, Tape.end + 1)
        visible_tape = Tape.tape[Tape.start:Tape.end]
            
        
        sys.stdout.write('\033[F')
        sys.stdout.write('\033[K')  
        sys.stdout.write('\033[F')
        sys.stdout.write('\033[K')
        sys.stdout.write('\033[F')
        sys.stdout.write('\033[K')
        # print(Tape.tape + f'\n' + ' '*Tape.cursor + '^' + '\nPress Ctrl+C to stop.')
        print(visible_tape + f'\n' + ' '*Tape.cursor_pos + '^' + f'\nPress Ctrl+C to stop.')
    
    def printer():
        output = ''
        text = Tape.tape.strip('x').split('x')
        binaries = []
        for char in text:
            if all(c in '01' for c in char):
                binaries.append(char)
        for i in range(len(binaries)):
            binaries[i] = int(binaries[i], 2)
        for num in binaries:
            output += Tape.char_table[num]
        Tape.run_flag = False
        print(output)