"""File Handler.
Реализует стратегию работы с файлом в консоли.
"""

import os
import subprocess
import time

from datetime import datetime
from pathlib import Path
from types import NoneType
from typing import Generator

from backend.config import Config
from backend.strategy import HandlerStrategy
from iterfzf import iterfzf

import __init__


class TerminalNote(Config, HandlerStrategy):
    """Класс TerminalNote.
    Содержит реализацию работы с файлом в консоли.
    """

    def __init__(self):
        super().__init__()
        self.ERRORS: dict[str, dict[int, str]]

    def get_path(self, file_name: str) -> str:
        """Создаёт переменную путь к файлу.
        Args:
            file_name (str): Имя файла
        Returns:
            str: Путь к файлу, пример: /home/belousov/terminal_note/file_name.md
        """
        file_path = f"{self.PATH_TO_STORAGE}/{file_name}"
        return file_path

    def file_list(self) -> Generator:
        """Список файлов в директории
        Сканирование директории и сбор всех файлов в список.

        Returns:
            Функция возвращает генератор с задержкой 0.01 сек.
        """
        path = Path(self.PATH_TO_STORAGE)
        file_list = [str(file) for file in path.glob("**/*") if file.is_file()]
        if len(file_list) < 1:
            yield "Директория пуста"
        for file in file_list:
            yield file
            time.sleep(0.01)

    def prompt_fzf(self) -> tuple[str, str] | tuple[str, NoneType]:
        """Реализация fzf

        Вызывает объект iterfzf.
        открывается список файлов, можно выбрать курсором или набрать текст, fzf отфильтрует.

        Returns:
            tuple (str, str): Если выбрать файл из текущего списка
            tuple (str, str): Если впиcать в промпт имя файла, при условии, что файл существует
            tuple (str, NoneType): Если вписать в промпт имя файла, а файла нет
        """
        return iterfzf(self.file_list(),
                       preview="cat {}", sort=True, print_query=True,
                       prompt="Введи имя файла: ")
        

    def create(self, file_name: str) -> dict[int, str] | None:
        """Создание файла.

        Args:
            file_name (str): Имя создаваемого файла
        Returns:
            dict: {0: "Файл создан"}, {1: "Файл существует"}

        """
        file_path = f"{self.get_path(file_name)}.{self.EXTENSION}"
        if not os.path.exists(file_path):
            with open(file_path, "w"):
                return self.ERRORS.get("file_created")
        return self.ERRORS.get("file_exists")

    def create_on_template(self, file_name: str) -> dict[int, str] | None:
        """Создать файл по шаблону.
        Создаёт файл на основании шаблона пользователя.
        Args:
            file_name (str): имя файла, который создаём

        Returns:
            dict[int, str]:
                {0: "Файл создан"},
                {1: "Файл существует"},
                {2: "Шаблон не существует"},

        """
        file_path = f"{self.get_path(file_name)}.{self.EXTENSION}"
        if not os.path.exists(self.PATH_TO_TEMPLATE_FILE):
            return self.ERRORS.get("template_is_not_exists")
        if not os.path.exists(file_path):
            with open(self.PATH_TO_TEMPLATE_FILE, "r") as t:
                template = t.read()
            with open(file_path, "w") as f:
                f.write(template)
            return self.ERRORS.get("file_created")
        return self.ERRORS.get("file_exists")

    def update(self) -> None | dict[int, str] | Exception | KeyboardInterrupt:
        """Изменить файл.
        Функция открывает файл для его изменения в редакторе, который указан в
        в конфиге
        Returns:
            dict[int, str]: {3: "Редактор не найден"},
            subprocess.CalledProcessError: Ошибка при открытии файла.
            KeyboardInterrupt: если не выбрали файл и нажали esc
            None: Если всё хорошо, то открывается редактор.
        """
        try:
            prompt, fzf = self.prompt_fzf()
            if "Директория пуста" in (prompt, fzf):
                print("Директория пуста")
                return
            if fzf is None:
                create_template = self.create_on_template(str(prompt))
                if create_template == self.ERRORS.get("template_is_not_exists"):
                    self.create(str(prompt))
                subprocess.run(
                    [self.EDITOR, f"{self.PATH_TO_STORAGE}/{prompt}.{self.EXTENSION}"],
                    check=True,
                )
            else:
                subprocess.run([self.EDITOR, str(fzf)], check=True)
        except NotADirectoryError:
            return self.ERRORS.get("editor_error")
        except KeyboardInterrupt as e:
            return e
        except subprocess.CalledProcessError as e:
            return e

    def delete(self) -> dict[int, str] | None | KeyboardInterrupt | FileNotFoundError:
        """Удалить файл.

        Ищем файл с помощью fzf, если файл есть удаяем нажав enter
        Если файла нет, то вывод в консоль "Файл не найден"
        Если отмена, то прекращение работы скрипта

        Returns:
            dict: {5: "Файл удалён", 4: "Файл не существет"}
        """
        try:
            prompt, deleted_file = self.prompt_fzf()
            if "Директория пуста" in (prompt, deleted_file):
                print("Директория пуста")
                return
            os.remove(str(deleted_file))
            print(f"Файл \033[32m{deleted_file.split('/')[-1]}\033[0m удалён")
            return self.ERRORS.get("file_deleted")
        except KeyboardInterrupt as e:
            return e
        except FileNotFoundError as e:
            print(f"Файл \033[31m{prompt}\033[0m не найден")
            return e

    def inline_note(self, text: str) -> dict[int, str] | None:
        """Записать однострочную заметку.

        При запсиси одностройчной заметки создаётся файл в хранилище
        С указанным расширением, имя файла генерируется автоматически в формате
        даты и времени "2025-05-06 13:26:15"

        Args:
            text (str): строка, текст быстрой заметки
        Returns:
            dict[int,str]: {6: "Заметка сохранена"}, {7: "Ошибка при сохранении}
            None: Если ошибки нет в списке
        """
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file_path = f"{self.get_path(date)}.{self.EXTENSION}"
        try:
            with open(file_path, "w") as f:
                f.writelines(f"{text}\n")
            return self.ERRORS.get("text_saved")
        except OSError:
            return self.ERRORS.get("text_saved_error")

    def read(self) -> None | KeyboardInterrupt | FileNotFoundError:
        """Прочитать файл.

        Функция читает файл и возвращавет его содержимое.
        Если файл .md открывается приложение frogmouth,
        если у файла другое расширение, то выводится в коснсоль той программой,
        которая указана в конфиге.

        Returns:
            None: при расширении md открывается приложение,
                в остальныхз случаях выводится тем приложением,
                уоторое указали в конфиге
            KeyboardInterrupt: если нажали esc, программа завершается
        """
       
        try:
            prompt, file = self.prompt_fzf()
            if "Директория пуста" in (prompt, file):
                print("Директория пуста")
                return

            if file is None:
                print(f"Файл \033[32m{prompt.split('/')[-1]}\033[0m не найден")
                return
            if ".md" in str(file):
                subprocess.run(["frogmouth", str(file)], check=True)
            else:
                if self.FILE_READER:
                    subprocess.run([self.FILE_READER, str(file)], check=True)
                else:
                    subprocess.run(["cat", str(file)], check=True)
        except KeyboardInterrupt as e:
            return e
