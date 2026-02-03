"""Сам интерпретатор."""
import time
import sys
import os
import random
from enum import Enum
import config


# Сдвиги
class Shift(Enum):
    """
    Таблица возможных шифтов.
    """
    LEFT = '<'
    RIGHT = '>'
    STAY = '~'

# Функция к которой перейти, функция которую пометить
class Jump:
    """Класс прыжка содержит информацию о второй команде триплета."""
    def __init__(self, function: 'Function', marking: 'Function'=None):
        self.function = function
        self.marking = marking

# Триплет, который выполняет машина
class Instruction:
    """
    Триплет.
    """
    def __init__(self, value: str, jump: 'Jump', shift: 'Shift'):
        self.value = value
        self.jump = jump
        self.shift = shift
    
    def get_value(self):
        """
        возвращает значение которое должна поставить функция в ячейку.
        """
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
    """
    три триплета.
    """
    def __init__(self, zero: 'Instruction', one: 'Instruction', x: 'Instruction'):
        self.zero = zero
        self.one = one
        self.x = x

# Функция АКА правила по которым работает машина
class Function:
    """
    Класс функции, содержит: индекс, триплеты и флаг маркировки.
    """
    functions = []
    bases = '#§'
    def __init__(self, index: str, default: 'InstructionSet', marked: 'InstructionSet'=None):
        self.index = index
        self.default = default
        if marked is not None:
            self.marked = marked
        else:
            self.marked = default
        self.mark = 0

        Function.functions.append(self)
    
    @staticmethod
    def get_function_by_name(index):
        """
        возвращает функцию по индексу.
        """
        for func in Function.functions:
            if func.index == index:
                return func
        return None

    @staticmethod
    def increment_marks():
        """
        увеличивает значение марок всех функций на 1
        """
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
    """
    Класс ленты
    """
    current_function: Function
    cursor = 1
    tape = ''
    pause_time = config.pause_time
    run_flag = True
    char_table = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*=+-_?/;:.,<>~ '
    width = min(os.get_terminal_size().columns - 5, config.fov)
    printer_string = ''

    start = 0
    end = width
    cursor_pos = 1

    @staticmethod
    def get_char():
        """
        Возвращает значение текущей ячейки.
        """
        return Tape.tape[Tape.cursor]

    @staticmethod
    def set_char(value):
        """
        Устанавливает значение текущей ячейке.
        """
        Tape.tape= Tape.tape[:(Tape.cursor)] + value + Tape.tape[(Tape.cursor+1):]
        return 
    
    @staticmethod
    def shift(value):
        """
        Двигает курсор.
        """
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
    
    @staticmethod
    def run():
        """
        Запускает програмный цикл.
        """
        print()
        print()
        print()
        Tape.print_tape()
        try:
            while Tape.run_flag:
                time.sleep(Tape.pause_time/2)
                Tape.current_function(Tape.tape[Tape.cursor])
                Tape.print_tape()
                time.sleep(Tape.pause_time/2)
            Tape.cls()
            if Tape.printer_string != "":
                print(Tape.printer_string)
            else:
                print(Tape.tape.strip('x'))
        except KeyboardInterrupt:  
            print(Tape.tape.strip('x'))

    @staticmethod
    def cls():
        """
        Очищает пространство работы.
        """
        sys.stdout.write('\033[F')
        sys.stdout.write('\033[K')
        sys.stdout.write('\033[F')
        sys.stdout.write('\033[K')
        sys.stdout.write('\033[F')
        sys.stdout.write('\033[K')
    
    @staticmethod
    def print_tape():
        """
        Выводит ленту.
        """
        Tape.cursor_pos = Tape.cursor - Tape.start
        if Tape.cursor_pos == 1 and Tape.cursor != 1:
            Tape.start = max(0, Tape.start - 1)
            Tape.end = min(len(Tape.tape)-1, Tape.end - 1)
        if Tape.cursor_pos == Tape.width - 2 and Tape.cursor != len(Tape.tape) - 1:
            Tape.start = max(0, Tape.start + 1)
            Tape.end = min(len(Tape.tape)-1, Tape.end + 1)
        visible_tape = Tape.tape[Tape.start:Tape.end]

        Tape.cls()
        print(visible_tape + '\n' + ' '*Tape.cursor_pos + '^' + f'\nPress Ctrl+C to stop. Pos: {Tape.cursor} Function: {Tape.current_function.index}')

    @staticmethod
    def printer():
        """
        Преобразует ленту, заканчивает программу и выводит результат.
        """
        output = ''
        text = Tape.tape.strip('x').split('x')
        binaries = []
        for char in text:
            if all(c in '01' for c in char):
                binaries.append(char)
        for i, char in enumerate(binaries):
            binaries[i] = int(char, 2)
        for num in binaries:
            output += Tape.char_table[num]
        Tape.run_flag = False
        Tape.printer_string = output