from src.functions import *
import re
from pathlib import Path

def Parse(file_name):
    chars_list = ['0', '1', 'x', '!', '?']
    shift_list = ['>', '<', '~']
    invalid_name_chars = '!~@#./?<>(){}[]'

    # Проверочка существует ли файл
    path = Path(file_name)
    if not path.exists():
        raise IOError(f"File not found: {file_name}")
    
    # Читаем, получаем сыроежку
    try:
        raw = path.read_text(encoding='utf-8')
    except:
        raise PermissionError("Permission denied. Maybe your machine's name has been lost from the cache.\nTry writing 'python main.py choose' and selecting your machine again.")

    # Удаляем коментарии
    raw = re.sub(r'".*?"|\'.*?\'', '', raw)
    
    # удаляем всякие пробельчики, табчики, переносы
    raw = re.sub(r'\s+', '', raw)

    # Разбиваем на части
    parts = [p for p in raw.split(';') if p != '']
    if not parts:
        raise ValueError("No functions found in file")
    
    functions = {}
    
    try:
        # Пройдемся по каждой части
        for part in parts:
            # если нету двоеточия поднимем скандал
            if ':' not in part:
                raise ValueError(f"Missing ':' in function definition: '{part}'")
            
            # Получим имя функции и её правила
            name, body = part.split(':', 1)
            if name == '':
                raise ValueError("Empty function name")

            # проверим нет ли в имени функции запрещёнки
            if any(ch in invalid_name_chars for ch in name):
                raise ValueError(f"Unexpected char in function name '{name}'")
            
            # обрабатываем тело функции: должно быть три триплета разделенных запятыми
            triplets = body.split(',')
            if len(triplets) != 3:
                raise ValueError(f"Function '{name}' must contain exactly 3 triplets separated by commas")
            
            for triplet in triplets:
                if triplet == '':
                    raise ValueError(f"Empty triplet in function '{name}'")
                if triplet[0] not in chars_list:
                    raise ValueError(f"Unknown cell value '{triplet[0]}' in function '{name}'")
                if triplet[-1] not in shift_list:
                    raise ValueError(f"Unknown shift '{triplet[-1]}' in function '{name}'")
            
            # заменяем собаку на имя функции (без ведущего '*', если есть)
            is_marked = name.startswith('*')
            func_name = name[1:] if is_marked else name

            triplets = [triplet.replace('@', func_name) for triplet in triplets]

            if is_marked:
                # найти уже существующую функцию по имени
                found = functions.get(func_name)

                # Если ненаход
                if not found:
                    raise ValueError(f"Function '{func_name}' not found to mark")
                
                # Записываем в словарь
                functions[func_name]['marked'] = [triplets[0], triplets[1], triplets[2]]
            else:
                # Записываем в словарь
                functions[func_name] = {}
                functions[func_name]['default'] = [triplets[0], triplets[1], triplets[2]]
        
        #Создаем функции
        for function_name in functions:
            default = functions[function_name]['default']
            marked = functions[function_name].get('marked')
            #  мда
            if not functions[function_name].get('marked') is None:
                Function(function_name,
                        InstructionSet(
                                        Instruction(default[0][0],
                                                    Jump(*tuple(default[0][1:-1].split('!', 1))),
                                                    Shift(default[0][-1])
                                                    ),
                                        Instruction(default[1][0],
                                                    Jump(*tuple(default[1][1:-1].split('!', 1))),
                                                    Shift(default[1][-1])
                                                    ),
                                        Instruction(default[2][0],
                                                    Jump(*tuple(default[2][1:-1].split('!', 1))),
                                                    Shift(default[2][-1])
                                                    ),
                                    ),
                        InstructionSet(
                                        Instruction(marked[0][0],
                                                    Jump(*tuple(marked[0][1:-1].split('!', 1))),
                                                    Shift(marked[0][-1])
                                                    ),
                                        Instruction(marked[1][0],
                                                    Jump(*tuple(marked[1][1:-1].split('!', 1))),
                                                    Shift(marked[1][-1])
                                                    ),
                                        Instruction(marked[2][0],
                                                    Jump(*tuple(marked[2][1:-1].split('!', 1))),
                                                    Shift(marked[2][-1])
                                                    ),
                                    )
                        )
            else:
                Function(function_name,
                        InstructionSet(
                                        Instruction(default[0][0],
                                                    Jump(*tuple(default[0][1:-1].split('!', 1))),
                                                    Shift(default[0][-1])
                                                    ),
                                        Instruction(default[1][0],
                                                    Jump(*tuple(default[1][1:-1].split('!', 1))),
                                                    Shift(default[1][-1])
                                                    ),
                                        Instruction(default[2][0],
                                                    Jump(*tuple(default[2][1:-1].split('!', 1))),
                                                    Shift(default[2][-1])
                                                    ),
                                    )
                        )
        
        # Закругляемся
        Tape.current_function = Function.functions[0]
    
    except Exception:
        raise