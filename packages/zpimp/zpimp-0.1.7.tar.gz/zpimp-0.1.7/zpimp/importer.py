import json
import os
import sys
import traceback
import inspect
from contextlib import contextmanager

# --- Конфигурация ---
ZEPPELIN_BASE_DIR = "/notebook"

# --- Вспомогательные функции ---

@contextmanager
def suppress_stdout_stderr():
    """
    Контекстный менеджер для временного подавления вывода в stdout и stderr.
    Используется для "тихого" выполнения кода из импортируемых ноутбуков.
    """
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    devnull = open(os.devnull, 'w', encoding='utf-8')
    try:
        sys.stdout = devnull
        sys.stderr = devnull
        yield
    finally:
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        devnull.close()

# --- Основные функции ---

def find_notebook_path(notebook_path_prefix, base_dir, verbose):
    """
    Находит полный путь к файлу ноутбука Zeppelin (.zpln) по его префиксу.

    :param notebook_path_prefix: Префикс пути к ноутбуку, например 'utils/my_helpers'.
    :param base_dir: Корневая директория для поиска ноутбуков.
    :param verbose: Флаг для включения отладочного вывода.
    :return: Полный путь к найденному файлу ноутбука.
    :raises FileNotFoundError: Если директория или ноутбук не найдены.
    :raises ValueError: Если найдено несколько ноутбуков по одному префиксу.
    """
    normalized_prefix = notebook_path_prefix.strip('/')
    if '/' in normalized_prefix:
        parts = normalized_prefix.rsplit('/', 1)
        notebook_dir_relative, notebook_base_name = parts
    else:
        notebook_dir_relative, notebook_base_name = "", normalized_prefix

    target_dir = os.path.join(base_dir, notebook_dir_relative)
    if verbose:
        print(f"[DEBUG] Поиск ноутбука с именем '{notebook_base_name}' в '{target_dir}'")

    if not os.path.isdir(target_dir):
        raise FileNotFoundError(f"Директория для импорта не найдена: {target_dir}")

    matches = []
    try:
        for filename in os.listdir(target_dir):
            if filename.endswith(".zpln"):
                name_without_ext = filename[:-5]
                last_underscore_index = name_without_ext.rfind('_')
                if last_underscore_index != -1 and name_without_ext[:last_underscore_index] == notebook_base_name:
                    if last_underscore_index < len(name_without_ext) - 1:
                        matches.append(os.path.join(target_dir, filename))
    except OSError as e:
        raise FileNotFoundError(f"Ошибка доступа к директории {target_dir}: {e}")

    if not matches:
        raise FileNotFoundError(f"Ноутбук с префиксом '{notebook_path_prefix}' не найден в '{target_dir}'.")
    elif len(matches) > 1:
        error_message = (
            f"Найдено несколько ноутбуков для префикса '{notebook_path_prefix}' в '{target_dir}':\n"
            f"{chr(10).join(matches)}\n"
            "Пожалуйста, укажите более точный путь."
        )
        raise ValueError(error_message)
    
    if verbose:
        print(f"[DEBUG] Найден один совпадающий ноутбук: {matches[0]}")
    return matches[0]


def import_zeppelin_notebook_from_path(full_notebook_path, verbose, show_link):
    """
    Внутренняя функция для выполнения кода из файла ноутбука.

    :param full_notebook_path: Полный путь к .zpln файлу.
    :param verbose: Если True, выводит подробную информацию о процессе.
    :param show_link: Если True, выводит кликабельную ссылку на ноутбук.
    :return: True в случае успеха, False в случае ошибки.
    """
    html_to_print_last = None
    success = False

    try:
        if verbose:
            print(f"[DEBUG] Читаю файл: {full_notebook_path}")

        if not os.path.exists(full_notebook_path):
            print(f"ОШИБКА: Файл ноутбука не найден: {full_notebook_path}")
            return False

        # Подготовка HTML-ссылки для отложенного вывода
        if show_link:
            try:
                filename = os.path.basename(full_notebook_path)
                name_without_ext = filename[:-5]
                last_underscore_index = name_without_ext.rfind('_')
                if last_underscore_index != -1:
                    notebook_id = name_without_ext[last_underscore_index + 1:]
                    relative_url = f"/#/notebook/{notebook_id}"
                    clean_notebook_name = name_without_ext[:last_underscore_index]
                    html_to_print_last = (
                        f'%html <div style="font-family: Arial, sans-serif; font-size: 14px;"><strong>Импортирован ноутбук:</strong> <a href="{relative_url}" '
                        f'target="_blank" rel="noopener noreferrer">{clean_notebook_name}</a></div>'
                    )
            except Exception:
                pass  # Не прерываем выполнение, если не удалось создать ссылку

        with open(full_notebook_path, 'r', encoding='utf-8') as f:
            notebook_data = json.load(f)

        python_code_to_execute = ""
        for paragraph in notebook_data.get("paragraphs", []):
            code = paragraph.get("text", "")
            if not code or not code.strip():
                continue

            stripped_code = code.lstrip()
            if stripped_code.startswith(("%python", "%spark.pyspark", "%flink.pyflink", "%jdbc(python)")):
                lines = code.splitlines()
                if len(lines) > 1:
                    python_code_to_execute += "\n".join(lines[1:]) + "\n\n"

        if python_code_to_execute:
            caller_globals = inspect.stack()[2].frame.f_globals
            
            # Выполнение кода с подавлением вывода или без, в зависимости от флага verbose
            if not verbose:
                with suppress_stdout_stderr():
                    exec(python_code_to_execute, caller_globals)
            else:
                print("-" * 20 + "\n[DEBUG] Код для выполнения:\n" + python_code_to_execute.strip() + "\n" + "-" * 20)
                exec(python_code_to_execute, caller_globals)
            
            if verbose:
                print(f"[DEBUG] Выполнение кода из {os.path.basename(full_notebook_path)} завершено.")
        elif verbose:
            print(f"[DEBUG] В ноутбуке {os.path.basename(full_notebook_path)} не найдено исполняемого Python кода.")
        
        success = True

    except Exception:
        # В случае любой ошибки, выводим полный traceback для диагностики
        traceback.print_exc()
        success = False
        
    finally:
        # Гарантированный вывод HTML-ссылки в самом конце, если все прошло успешно
        if success and html_to_print_last:
            print(html_to_print_last)
    
    return success

# --- Публичная API-функция ---

def import_note(notebook_path_prefix, base_dir=ZEPPELIN_BASE_DIR, verbose=False, show_link=True):
    """
    Находит и выполняет Python-код из другого ноутбука Zeppelin, делая его
    определения (функции, переменные) доступными в текущей сессии.
    Ничего не возвращает, чтобы избежать авто-печати 'True' в Zeppelin.
    
    :param notebook_path_prefix: Путь-префикс к ноутбуку для импорта (например, 'libraries/utils').
    :param base_dir: (опционально) Базовая директория ноутбуков.
    :param verbose: (опционально) Если True, выводит подробный лог выполнения. По умолчанию False.
    :param show_link: (опционально) Если True, выводит кликабельную ссылку на импортированный ноутбук. По умолчанию True.
    """
    try:
        full_path = find_notebook_path(notebook_path_prefix, base_dir, verbose)
        # Вызываем внутреннюю функцию, но не возвращаем ее результат пользователю
        import_zeppelin_notebook_from_path(full_path, verbose, show_link)
    except (FileNotFoundError, ValueError) as e:
        # Выводим только критические ошибки, которые мешают импорту
        print(f"ОШИБКА ИМПОРТА: {e}")
    except Exception:
        # Для всех остальных непредвиденных ошибок выводим полный traceback
        print(f"НЕПРЕДВИДЕННАЯ ОШИБКА при импорте '{notebook_path_prefix}':")
        traceback.print_exc()