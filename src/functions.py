import time
import sys
import config
from enum import Enum

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
    char_table = ' 0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*=+-_?/;:.,<>~'

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
                    Function.increment_marks()
                return
            case Shift.RIGHT:
                Tape.cursor += 1
                if Tape.cursor == len(Tape.tape)-1:
                    Tape.tape = Tape.tape + 'x'
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
        except KeyboardInterrupt:  
            print(Tape.tape.strip('x'))
    
    def print_tape():
        print(Tape.tape + f'\n' + ' '*Tape.cursor + '^' + '\nPress Ctrl+C to stop.')
        sys.stdout.write('\033[F')
        sys.stdout.write('\033[K')  
        sys.stdout.write('\033[F')
        sys.stdout.write('\033[K')
        sys.stdout.write('\033[F')
        sys.stdout.write('\033[K')
    
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